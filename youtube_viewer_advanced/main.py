#!/usr/bin/env python3
"""
YouTube Viewer Advanced - POPRAWIONA WERSJA z pełną konfiguracją
"""

import os
import sys
import time
import random
import threading
import json
from weakref import proxy
import requests
from colorama import init, Fore, Style
from datetime import datetime

# Inicjalizacja colorama
init(autoreset=True)

# Dodaj katalog modułów do ścieżki
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

# Import modułów
from browser_manager import BrowserManager
from proxy_manager import ProxyManager
from youtube_actions import YouTubeActions
from channel_verifier import ChannelVerifier

class YouTubeViewerAdvanced:
    def __init__(self):
        self.proxy_manager = ProxyManager()
        self.channel_verifier = ChannelVerifier()
        self.running = False
        self.sessions = []
        self.session_count = 0
        self.config = self.load_config()
        
        # Utwórz potrzebne katalogi
        self.create_directories()
        
        # ★★★ SPRAWDŹ CZY YouTubeActions PRZYJMUJE KONFIGURACJĘ ★★★
        print(f"{Fore.CYAN}📋 Sprawdzam kompatybilność modułów...{Style.RESET_ALL}")
        self.check_module_compatibility()
    
    def check_module_compatibility(self):
        """Sprawdza czy YouTubeActions przyjmuje config"""
        try:
            # Spróbuj zaimportować i sprawdzić konstruktor
            import inspect
            sig = inspect.signature(YouTubeActions.__init__)
            params = list(sig.parameters.keys())
            
            if 'config' in params:
                print(f"{Fore.GREEN}✅ YouTubeActions wspiera konfigurację{Style.RESET_ALL}")
                self.actions_supports_config = True
            else:
                print(f"{Fore.YELLOW}⚠ YouTubeActions NIE wspiera konfiguracji (stara wersja){Style.RESET_ALL}")
                print(f"{Fore.YELLOW}⚠ Użyj nowszej wersji youtube_actions.py{Style.RESET_ALL}")
                self.actions_supports_config = False
                
        except Exception as e:
            print(f"{Fore.YELLOW}⚠ Nie udało się sprawdzić kompatybilności: {e}{Style.RESET_ALL}")
            self.actions_supports_config = False
    
    def create_directories(self):
        """Tworzy potrzebne katalogi"""
        directories = ['profiles', 'fingerprints', 'data', 'logs']
        for directory in directories:
            if not os.path.exists(directory):
                os.makedirs(directory)
                print(f"{Fore.GREEN}✓ Utworzono katalog: {directory}{Style.RESET_ALL}")
    
    def load_config(self):
        """Ładuje konfigurację z pliku"""
        config_file = 'data/config.json'
        default_config = {
            # ★★★ GŁÓWNE USTAWIENIA ★★★
            'max_concurrent_channels': 1,
            'max_videos_per_channel': 15,
            'threads': 5,
            'max_views_per_session': 50,
            'channel_name': '@jbeegames',
            
            # ★★★ CZASY (NAJWAŻNIEJSZE) ★★★
            'min_watch_time': 90,
            'max_watch_time': 240,
            'min_break_between_videos': 10,
            'max_break_between_videos': 15,
            
            # ★★★ PROXY ★★★
            'use_proxy': True,
            'use_proxy_rotation': True,
            'proxy_rotation_every': 10,
            'max_proxy_retries': 5,
            'max_proxies_to_fetch': 1000,
            'proxy_test_timeout': 15,
            'max_proxy_attempts': 15,
            
            # ★★★ PRZEGLĄDARKA I FINGERPRINT ★★★
            'headless_mode': False,
            'use_fingerprinting': True,
            'random_user_agent': True,
            'organic_search': True,
            'max_profiles': 10,
            
            # ★★★ ORGANIC ACTIONS (DO YouTubeActions) ★★★
            'enable_scroll': True,
            'enable_mouse_movement': True,
            'enable_volume_change': True,
            'enable_fullscreen': True,
            
            # ★★★ INNE ★★★
            'save_reports': True,
            'log_level': 'INFO',
            'auto_accept_cookies': True,
        }
        
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                
                # ★★★ MIGRACJA: Dodaj brakujące klucze z domyślnych ★★★
                for key in default_config:
                    if key not in user_config:
                        user_config[key] = default_config[key]
                        print(f"{Fore.YELLOW}➕ Dodano brakujące ustawienie: {key} = {default_config[key]}{Style.RESET_ALL}")
                
                print(f"{Fore.GREEN}✅ Wczytano pełną konfigurację ({len(user_config)} ustawień){Style.RESET_ALL}")
                return user_config
            except Exception as e:
                print(f"{Fore.RED}❌ Błąd wczytywania konfiguracji: {str(e)}{Style.RESET_ALL}")
        else:
            # Zapisz domyślną konfigurację
            self.save_config(default_config)
            print(f"{Fore.YELLOW}⚠ Utworzono domyślną konfigurację{Style.RESET_ALL}")
        
        return default_config
    
    def save_config(self, config=None):
        """Zapisuje konfigurację do pliku"""
        if config is None:
            config = self.config
        
        try:
            # Tworzymy kopię z tylko ważnymi ustawieniami (bez proxy list)
            config_to_save = {k: v for k, v in config.items() 
                            if not isinstance(v, list) or k not in ['proxies', 'proxy_list']}
            
            with open('data/config.json', 'w', encoding='utf-8') as f:
                json.dump(config_to_save, f, indent=4, ensure_ascii=False, default=str)
            
            print(f"{Fore.GREEN}✅ Zapisano konfigurację ({len(config_to_save)} ustawień){Style.RESET_ALL}")
            return True
        except Exception as e:
            print(f"{Fore.RED}❌ Błąd zapisywania konfiguracji: {str(e)}{Style.RESET_ALL}")
            return False
    
    def show_current_config_summary(self):
        """Pokazuje podsumowanie aktualnej konfiguracji"""
        print(f"\n{Fore.CYAN}" + "="*60)
        print("📋 AKTUALNA KONFIGURACJA")
        print("="*60 + f"{Style.RESET_ALL}")
        
        important_keys = [
            'channel_name', 'max_videos_per_channel', 'max_views_per_session',
            'min_watch_time', 'max_watch_time', 
            'min_break_between_videos', 'max_break_between_videos',
            'enable_scroll', 'enable_mouse_movement', 'enable_volume_change', 'enable_fullscreen',
            'use_proxy', 'use_fingerprinting', 'organic_search'
        ]
        
        for key in important_keys:
            if key in self.config:
                value = self.config[key]
                if isinstance(value, bool):
                    display = f"{Fore.GREEN}✅ Tak{Style.RESET_ALL}" if value else f"{Fore.RED}❌ Nie{Style.RESET_ALL}"
                else:
                    display = f"{Fore.YELLOW}{value}{Style.RESET_ALL}"
                
                print(f"  {key}: {display}")
    
    def load_channels(self, filename=None):
        """Zawsze używa tylko Twojego kanału z konfiguracji"""
        channel_name = self.config.get('channel_name', '@jbeegames')
        
        print(f"{Fore.CYAN}📺 Używam kanału z konfiguracji:{Style.RESET_ALL}")
        print(f"   Kanał: {channel_name}")
        
        # Konwertuj na URL
        if channel_name.startswith('http'):
            channel_url = channel_name
        elif channel_name.startswith('@'):
            channel_url = f"https://www.youtube.com/{channel_name}"
        else:
            channel_url = f"https://www.youtube.com/@{channel_name.replace(' ', '')}"
        
        print(f"{Fore.GREEN}✅ URL: {channel_url}{Style.RESET_ALL}")
        
        return [channel_url]
    
    def simple_proxy_test(self, proxy):
        """Prosty test proxy"""
        try:
            proxies = {
                'http': proxy,
                'https': proxy
            }
            
            timeout = self.config.get('proxy_test_timeout', 10)
            response = requests.get('http://httpbin.org/ip', 
                                  proxies=proxies, 
                                  timeout=timeout,
                                  verify=False)
            return response.status_code == 200
        except:
            return False
    
    def find_working_proxy_for_profile(self, profile_index, start_index=0):
        """Znajduje działające proxy"""
        print(f"{Fore.CYAN}[Profil {profile_index}] 🔍 Szukam działającego proxy...{Style.RESET_ALL}")
        
        if not self.config.get('use_proxy', True):
            print(f"{Fore.YELLOW}[Profil {profile_index}] ⚡ Pracuję bez proxy{Style.RESET_ALL}")
            return None, 0
        
        try:
            total_proxies = len(self.proxy_manager.proxies)
            if total_proxies == 0:
                print(f"{Fore.RED}[Profil {profile_index}] ❌ Brak proxy!{Style.RESET_ALL}")
                return None, 0
            
            print(f"{Fore.CYAN}[Profil {profile_index}] 📋 Dostępne proxy: {total_proxies}{Style.RESET_ALL}")
            
            max_attempts = min(self.config.get('max_proxy_attempts', 15), total_proxies)
            
            for i in range(start_index, start_index + max_attempts):
                proxy_index = i % total_proxies
                proxy = self.proxy_manager.proxies[proxy_index]
                
                print(f"{Fore.CYAN}[Profil {profile_index}] 🧪 Próbuję proxy {proxy_index+1}/{total_proxies}...{Style.RESET_ALL}")
                
                if self.simple_proxy_test(proxy):
                    print(f"{Fore.GREEN}[Profil {profile_index}] ✅ Proxy działa!{Style.RESET_ALL}")
                    return proxy, proxy_index + 1
                else:
                    print(f"{Fore.YELLOW}[Profil {profile_index}] ❌ Proxy nie działa{Style.RESET_ALL}")
                
                time.sleep(1)
            
            print(f"{Fore.YELLOW}[Profil {profile_index}] ⚡ Nie znaleziono działającego proxy{Style.RESET_ALL}")
            return None, 0
                
        except Exception as e:
            print(f"{Fore.RED}[Profil {profile_index}] ❌ Błąd szukania proxy: {str(e)[:50]}{Style.RESET_ALL}")
            return None, 0
    
    def verify_channel_url(self, current_url, expected_channel):
        """Weryfikuje czy obecny URL to właściwy kanał"""
        try:
            current_url = current_url.lower().strip()
            expected_url = self.get_channel_url_from_input(expected_channel).lower().strip()
            
            def normalize_url(url):
                if '?' in url:
                    url = url.split('?')[0]
                if url.endswith('/'):
                    url = url[:-1]
                return url
            
            current_norm = normalize_url(current_url)
            expected_norm = normalize_url(expected_url)
            
            # Sprawdź czy to ten sam kanał
            channel_identifiers = []
            
            if '/@' in expected_norm:
                channel_id = expected_norm.split('/@')[1]
                channel_identifiers.append(f'/@{channel_id}')
            elif '/channel/' in expected_norm:
                channel_id = expected_norm.split('/channel/')[1]
                channel_identifiers.append(f'/channel/{channel_id}')
            elif '/c/' in expected_norm:
                channel_id = expected_norm.split('/c/')[1]
                channel_identifiers.append(f'/c/{channel_id}')
            
            for identifier in channel_identifiers:
                if identifier in current_norm:
                    return True
            
            if current_norm == expected_norm:
                return True
            
            channel_name = expected_channel.replace('@', '').replace('https://www.youtube.com/', '').lower()
            if channel_name in current_url:
                return True
            
            return False
            
        except Exception as e:
            print(f"{Fore.YELLOW}⚠ Błąd weryfikacji URL: {e}{Style.RESET_ALL}")
            return False
    
    def get_channel_url_from_input(self, channel_input):
        """Konwertuje input na URL kanału"""
        channel_input = channel_input.strip()
        
        if channel_input.startswith('http'):
            return channel_input
        
        if channel_input.startswith('@'):
            return f"https://www.youtube.com/{channel_input}"
        
        return f"https://www.youtube.com/@{channel_input.replace(' ', '').lower()}"
    
    def run_single_channel_profile(self, channel_url, profile_index):
        """Uruchamia sesję z pełną konfiguracją"""
        max_proxy_retries = self.config.get('max_proxy_retries', 5)
        proxy_attempts = 0
        current_proxy = None
        proxy_start_index = 0
        
        # Auto-rotacja proxy
        if self.config.get('use_proxy_rotation', True):
            proxy_rotation_every = self.config.get('proxy_rotation_every', 10)
            if self.session_count % proxy_rotation_every == 0 and self.session_count > 0:
                print(f"{Fore.YELLOW}[Profil {profile_index}] 🔄 Auto-rotacja proxy (sesja #{self.session_count}){Style.RESET_ALL}")
                proxy_start_index = random.randint(0, len(self.proxy_manager.proxies) - 5) if len(self.proxy_manager.proxies) > 5 else 0
        
        while proxy_attempts < max_proxy_retries:
            try:
                self.session_count += 1
                print(f"{Fore.CYAN}" + "="*60)
                print(f"🚀 PROFIL {profile_index} (Sesja #{self.session_count})")
                print(f"   Kanał: {channel_url}")
                print(f"   Config: {self.config.get('min_watch_time')}-{self.config.get('max_watch_time')}s oglądania")
                print("="*60 + f"{Style.RESET_ALL}")
                
                # Znajdź proxy
                proxy_result = self.find_working_proxy_for_profile(profile_index, proxy_start_index)
                current_proxy, next_start_index = proxy_result if proxy_result else (None, 0)
                proxy_attempts += 1
                proxy_start_index = next_start_index
                
                if not current_proxy and self.config.get('use_proxy', True):
                    print(f"{Fore.YELLOW}[Profil {profile_index}] ⚡ Pracuję bez proxy{Style.RESET_ALL}")
                
                # ★★★ INICJALIZUJ PRZEGLĄDARKĘ Z KONFIGURACJĄ ★★★
                use_fingerprint = self.config.get('use_fingerprinting', True)
                auto_accept_cookies = self.config.get('auto_accept_cookies', True)
                headless_mode = self.config.get('headless_mode', False)
                
                browser_manager = BrowserManager(
                    profile_index=profile_index, 
                    use_proxy=current_proxy if self.config.get('use_proxy', True) else None,
                    use_fingerprint=use_fingerprint,
                    auto_accept_cookies=auto_accept_cookies
                )
                
                if not browser_manager.driver:
                    print(f"{Fore.RED}[Profil {profile_index}] ❌ Błąd przeglądarki{Style.RESET_ALL}")
                    time.sleep(2)
                    continue
                
                # ★★★ TWORZENIE YouTubeActions Z KONFIGURACJĄ ★★★
                try:
                    if self.actions_supports_config:
                        # Nowa wersja - przekaż konfigurację
                        youtube_actions = YouTubeActions(
                            driver=browser_manager.driver, 
                            config=self.config,
                            proxy=current_proxy
                        )
                        print(f"{Fore.GREEN}[Profil {profile_index}] ✅ YouTubeActions z konfiguracją{Style.RESET_ALL}")
                    else:
                        # Stara wersja - bez konfiguracji
                        youtube_actions = YouTubeActions(
                            driver=browser_manager.driver, 
                            proxy=current_proxy
                        )
                        print(f"{Fore.YELLOW}[Profil {profile_index}] ⚠ YouTubeActions bez konfiguracji{Style.RESET_ALL}")
                        
                        # Ręczne ustawienie parametrów dla starej wersji
                        if hasattr(youtube_actions, 'min_watch_time'):
                            youtube_actions.min_watch_time = self.config.get('min_watch_time', 90)
                            youtube_actions.max_watch_time = self.config.get('max_watch_time', 240)
                except Exception as e:
                    print(f"{Fore.RED}[Profil {profile_index}] ❌ Błąd tworzenia YouTubeActions: {e}{Style.RESET_ALL}")
                    browser_manager.quit()
                    continue
                
                # Test połączenia
                print(f"{Fore.CYAN}[Profil {profile_index}] 🧪 Testuję połączenie...{Style.RESET_ALL}")
                try:
                    browser_manager.driver.get("https://www.google.com")
                    time.sleep(2)
                    if "google" in browser_manager.driver.title.lower():
                        print(f"{Fore.GREEN}[Profil {profile_index}] ✅ Połączenie działa!{Style.RESET_ALL}")
                    else:
                        print(f"{Fore.YELLOW}[Profil {profile_index}] ⚠ Połączenie może mieć problemy{Style.RESET_ALL}")
                except Exception as test_error:
                    error_msg = str(test_error)
                    print(f"{Fore.RED}[Profil {profile_index}] ❌ Błąd połączenia: {error_msg[:50]}{Style.RESET_ALL}")
                    browser_manager.quit()
                    continue
                
                # Pobierz nazwę kanału z konfiguracji
                channel_name = self.config.get('channel_name', '@jbeegames')
                
                # Organic search lub bezpośrednie wejście
                if self.config.get('organic_search', True):
                    print(f"{Fore.CYAN}[Profil {profile_index}] 🔍 Organic search dla kanału...{Style.RESET_ALL}")
                    
                    search_success = youtube_actions.organic_search_channel(channel_name)
                    
                    if search_success:
                        current_url = browser_manager.driver.current_url
                        if not self.verify_channel_url(current_url, channel_name):
                            print(f"{Fore.YELLOW}[Profil {profile_index}] ⚠ Weryfikacja kanału nieudana!{Style.RESET_ALL}")
                            
                            if hasattr(youtube_actions, 'verify_current_channel'):
                                if not youtube_actions.verify_current_channel(channel_name):
                                    print(f"{Fore.YELLOW}[Profil {profile_index}] ⚠ Weryfikacja przez YouTubeActions też nieudana{Style.RESET_ALL}")
                                    search_success = False
                            else:
                                search_success = False
                    
                    if not search_success:
                        print(f"{Fore.YELLOW}[Profil {profile_index}] ⚠ Fallback do bezpośredniego URL{Style.RESET_ALL}")
                        browser_manager.driver.get(channel_url)
                        time.sleep(3)
                        
                        current_url = browser_manager.driver.current_url
                        if not self.verify_channel_url(current_url, channel_name):
                            print(f"{Fore.RED}[Profil {profile_index}] ❌ Nawet fallback nie trafił na właściwy kanał!{Style.RESET_ALL}")
                            browser_manager.quit()
                            continue
                else:
                    print(f"{Fore.CYAN}[Profil {profile_index}] ⚡ Bezpośrednie wejście na kanał...{Style.RESET_ALL}")
                    browser_manager.driver.get(channel_url)
                    time.sleep(5)
                    
                    current_url = browser_manager.driver.current_url
                    if not self.verify_channel_url(current_url, channel_name):
                        print(f"{Fore.RED}[Profil {profile_index}] ❌ Nieprawidłowy kanał po bezpośrednim wejściu!{Style.RESET_ALL}")
                        browser_manager.quit()
                        continue
                
                if "youtube.com" not in browser_manager.driver.current_url:
                    print(f"{Fore.RED}[Profil {profile_index}] ❌ Nie udało się załadować YouTube{Style.RESET_ALL}")
                    browser_manager.quit()
                    continue
                        
                print(f"{Fore.GREEN}[Profil {profile_index}] ✅ Strona załadowana i zweryfikowana{Style.RESET_ALL}")
                
                # ★★★ POBRANIE FILMÓW Z OGRANICZENIAMI KONFIGU ★★★
                max_videos_config = self.config.get('max_videos_per_channel', 15)
                max_views_session = self.config.get('max_views_per_session', 50)
                max_videos = min(max_videos_config, max_views_session)
                
                # Używaj nazwy kanału zamiast URL
                videos = youtube_actions.get_my_channel_videos(channel_name, max_videos)
                
                if not videos:
                    print(f"{Fore.YELLOW}[Profil {profile_index}] ⚠ Brak filmów{Style.RESET_ALL}")
                    browser_manager.quit()
                    return
                
                print(f"{Fore.CYAN}[Profil {profile_index}] 📹 Znaleziono {len(videos)} filmów{Style.RESET_ALL}")
                
                # ★★★ OGLĄDANIE FILMÓW Z KONFIGURACJĄ ★★★
                successful_views = 0
                
                for i, video_url in enumerate(videos):
                    try:
                        print(f"{Fore.CYAN}[Profil {profile_index}] 🎬 Film {i+1}/{len(videos)}...{Style.RESET_ALL}")
                        
                        # ★★★ UŻYJ CZASÓW Z KONFIGU ★★★
                        min_watch = self.config.get('min_watch_time', 90)
                        max_watch = self.config.get('max_watch_time', 240)
                        watch_time = random.randint(min_watch, max_watch)
                        
                        # ★★★ OGLĄDAJ FILM ★★★
                        # Sprawdź czy metoda istnieje
                        if hasattr(youtube_actions, 'watch_jbeegames_video'):
                            success = youtube_actions.watch_jbeegames_video(video_url, watch_time)
                        else:
                            success = youtube_actions.watch_my_channel_video(video_url, watch_time)
                            successful_views += 1
                            print(f"{Fore.CYAN}[Profil {profile_index}] ⏱ {watch_time}s...{Style.RESET_ALL}")
                            time.sleep(watch_time)
                        
                        # Przerwa jeśli nie ostatni film
                        if i < len(videos) - 1:
                            min_break = self.config.get('min_break_between_videos', 10)
                            max_break = self.config.get('max_break_between_videos', 15)
                            break_time = random.randint(min_break, max_break)
                            print(f"{Fore.CYAN}[Profil {profile_index}] ⏳ Przerwa {break_time}s...{Style.RESET_ALL}")
                            time.sleep(break_time)
                            
                    except Exception as e:
                        print(f"{Fore.RED}[Profil {profile_index}] ❌ Błąd filmu: {str(e)[:50]}{Style.RESET_ALL}")
                        continue
                
                # Zapisz sesję
                self.sessions.append({
                    'profile': profile_index,
                    'channel': channel_url,
                    'videos_watched': successful_views,
                    'total_videos': len(videos),
                    'config_used': {
                        'min_watch_time': self.config.get('min_watch_time'),
                        'max_watch_time': self.config.get('max_watch_time'),
                        'enable_scroll': self.config.get('enable_scroll'),
                        'organic_search': self.config.get('organic_search')
                    },
                    'proxy': current_proxy if current_proxy else 'Brak proxy',
                    'timestamp': datetime.now().strftime("%H:%M:%S"),
                    'proxy_attempts': proxy_attempts,
                    'channel_verified': True
                })
                
                print(f"{Fore.GREEN}[Profil {profile_index}] ✅ Zakończono! Obejrzano {successful_views}/{len(videos)} filmów{Style.RESET_ALL}")
                browser_manager.quit()
                break  # Sukces - wyjdź z pętli
                
            except Exception as e:
                error_msg = str(e)
                print(f"{Fore.RED}[Profil {profile_index}] ❌ Błąd sesji: {error_msg[:100]}")
                
                proxy_keywords = ['proxy', 'connection', 'tunnel', 'net::', 'connect', 'refused', 'failed', 'unreachable']
                is_proxy_error = any(keyword in error_msg.lower() for keyword in proxy_keywords)
                
                if is_proxy_error:
                    print(f"{Fore.YELLOW}[Profil {profile_index}] ⚠ Błąd proxy, próbuję następne...{Style.RESET_ALL}")
                    
                    try:
                        if 'browser_manager' in locals():
                            browser_manager.quit()
                    except:
                        pass
                    
                    if proxy_attempts >= max_proxy_retries:
                        print(f"{Fore.RED}[Profil {profile_index}] ❌ Przekroczono limit prób proxy ({max_proxy_retries}){Style.RESET_ALL}")
                        break
                    
                    time.sleep(3)
                    continue
                else:
                    print(f"{Fore.RED}[Profil {profile_index}] ❌ Inny błąd, kończę sesję{Style.RESET_ALL}")
                    break
        
        if proxy_attempts >= max_proxy_retries:
            print(f"{Fore.RED}[Profil {profile_index}] ❌ Nie udało się uruchomić z żadnym proxy{Style.RESET_ALL}")
    
    def run_bot(self):
        """Uruchamia bota z konfiguracją"""
        self.show_current_config_summary()
        
        channels = self.load_channels()
        
        if not channels:
            print(f"{Fore.RED}❌ Brak kanałów!{Style.RESET_ALL}")
            return
        
        print(f"{Fore.CYAN}📺 Znaleziono {len(channels)} kanałów{Style.RESET_ALL}")
        
        max_channels = self.config.get('max_concurrent_channels', 1)
        max_threads = self.config.get('threads', 5)
        
        print(f"{Fore.CYAN}⚙️  Ustawienia: {max_channels} kanałów, {max_threads} wątków{Style.RESET_ALL}")
        
        if max_threads > 10:
            print(f"{Fore.YELLOW}⚠ Uwaga: {max_threads} wątków może być za dużo dla systemu!{Style.RESET_ALL}")
            max_threads = min(max_threads, 10)
        
        try:
            channels_input = input(f"\n{Fore.GREEN}👉 Liczba kanałów do przetworzenia (domyślnie {max_channels}): {Style.RESET_ALL}").strip()
            if channels_input:
                max_channels = int(channels_input)
        except ValueError:
            print(f"{Fore.RED}❌ Nieprawidłowa liczba, używam domyślnej{Style.RESET_ALL}")
        
        channels_to_process = channels[:max_channels]
        threads = []
        
        for i, channel_url in enumerate(channels_to_process):
            thread = threading.Thread(
                target=self.run_single_channel_profile,
                args=(channel_url, i+1),
                daemon=True
            )
            threads.append(thread)
            thread.start()
            
            if i < len(channels_to_process) - 1:
                delay = random.randint(5, 15)
                print(f"{Fore.CYAN}⏳ Opóźnienie {delay}s...{Style.RESET_ALL}")
                time.sleep(delay)
        
        for thread in threads:
            thread.join()
        
        self.show_summary()
    
    def show_summary(self):
        """Pokazuje podsumowanie z konfiguracją"""
        if not self.sessions:
            print(f"{Fore.YELLOW}📊 Brak sesji{Style.RESET_ALL}")
            return
        
        print(f"\n{Fore.CYAN}" + "="*60)
        print("📊 PODSUMOWANIE SESJI")
        print("="*60 + f"{Style.RESET_ALL}")
        
        total_views = sum(s['videos_watched'] for s in self.sessions)
        total_videos = sum(s['total_videos'] for s in self.sessions)
        
        print(f"   Sesje: {len(self.sessions)}")
        print(f"   Filmy: {total_views}/{total_videos}")
        
        if total_videos > 0:
            success_rate = (total_views / total_videos) * 100
            print(f"   Sukces: {success_rate:.1f}%")
        
        # Pokaż użyte ustawienia
        if self.sessions:
            first_session = self.sessions[0]
            if 'config_used' in first_session:
                config = first_session['config_used']
                print(f"\n{Fore.YELLOW}⚙️  UŻYTA KONFIGURACJA:{Style.RESET_ALL}")
                print(f"   Czas oglądania: {config.get('min_watch_time')}-{config.get('max_watch_time')}s")
                print(f"   Organic search: {'✅ Tak' if config.get('organic_search') else '❌ Nie'}")
                print(f"   Scrollowanie: {'✅ Tak' if config.get('enable_scroll') else '❌ Nie'}")
    
    def configuration_menu(self):
        """Menu konfiguracji"""
        while True:
            print(f"\n{Fore.CYAN}" + "="*60)
            print("⚙️  KONFIGURACJA")
            print("="*60 + f"{Style.RESET_ALL}")
            
            categories = {
                '🎯 GŁÓWNE': [
                    ('threads', 'Wątki równoległe', 1, 10),
                    ('max_concurrent_channels', 'Maks. kanałów równoległych', 1, 5),
                    ('max_videos_per_channel', 'Filmy na kanał', 1, 50),
                    ('max_views_per_session', 'Maks. oglądnięć na sesję', 1, 200),
                    ('channel_name', 'Nazwa kanału', None, None),
                ],
                '⏱️  CZASY': [
                    ('min_watch_time', 'Min. czas oglądania (s)', 30, 600),
                    ('max_watch_time', 'Max. czas oglądania (s)', 60, 1200),
                    ('min_break_between_videos', 'Min. przerwa (s)', 5, 60),
                    ('max_break_between_videos', 'Max. przerwa (s)', 10, 120),
                ],
                '🔌 PROXY': [
                    ('use_proxy', 'Użyj proxy', None, None),
                    ('use_proxy_rotation', 'Rotacja proxy', None, None),
                    ('max_proxy_retries', 'Maks. prób proxy', 1, 20),
                    ('proxy_rotation_every', 'Rotacja co X sesji', 1, 100),
                ],
                '🕵️  PRZEGLĄDARKA': [
                    ('use_fingerprinting', 'Fingerprint anty-detekcja', None, None),
                    ('organic_search', 'Wyszukiwanie organiczne', None, None),
                    ('headless_mode', 'Tryb headless', None, None),
                    ('auto_accept_cookies', 'Auto-akceptacja cookies', None, None),
                ],
                '🐭 AKCJE': [
                    ('enable_scroll', 'Scrollowanie', None, None),
                    ('enable_mouse_movement', 'Ruchy myszy', None, None),
                    ('enable_volume_change', 'Zmiana głośności', None, None),
                    ('enable_fullscreen', 'Pełny ekran', None, None),
                ]
            }
            
            option_counter = 1
            option_map = {}
            
            for category, options in categories.items():
                print(f"\n{Fore.YELLOW}{category}:{Style.RESET_ALL}")
                for key, name, min_val, max_val in options:
                    current = self.config.get(key, '')
                    if isinstance(current, bool):
                        display = f"{Fore.GREEN}✅ Tak{Style.RESET_ALL}" if current else f"{Fore.RED}❌ Nie{Style.RESET_ALL}"
                    else:
                        display = f"{Fore.YELLOW}{current}{Style.RESET_ALL}"
                    
                    print(f"  {option_counter}. {name}: {display}")
                    option_map[option_counter] = (key, name, min_val, max_val)
                    option_counter += 1
            
            print(f"\n{Fore.CYAN}" + "-"*60 + f"{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}💾 OPCJE MENU:{Style.RESET_ALL}")
            print(f"  {option_counter}. Zapisz i wyjdź")
            print(f"  {option_counter+1}. Wyjdź bez zapisywania")
            print(f"  {option_counter+2}. Przywróć domyślne")
            print(f"{Fore.CYAN}" + "="*60 + f"{Style.RESET_ALL}")
            
            try:
                choice = int(input(f"\n{Fore.GREEN}👉 Wybierz opcję: {Style.RESET_ALL}").strip())
                
                if choice == option_counter:  # Zapisz i wyjdź
                    self.save_config()
                    print(f"{Fore.GREEN}✅ Konfiguracja zapisana!{Style.RESET_ALL}")
                    break
                elif choice == option_counter + 1:  # Wyjdź bez zapisywania
                    break
                elif choice == option_counter + 2:  # Przywróć domyślne
                    self.reset_to_default_config()
                    print(f"{Fore.GREEN}✅ Przywrócono domyślne ustawienia!{Style.RESET_ALL}")
                elif choice in option_map:
                    self.handle_config_change(*option_map[choice])
                else:
                    print(f"{Fore.RED}❌ Nieprawidłowy wybór!{Style.RESET_ALL}")
                    
            except ValueError:
                print(f"{Fore.RED}❌ Wprowadź numer!{Style.RESET_ALL}")
    
    def handle_config_change(self, key, name, min_val, max_val):
        """Obsługuje zmianę ustawienia"""
        current = self.config.get(key, '')
        
        print(f"\n{Fore.CYAN}📝 Zmiana: {name}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}   Aktualna wartość: {current}{Style.RESET_ALL}")
        
        if min_val is None:  # Boolean
            new_value = input(f"{Fore.GREEN}   Nowa wartość (tak/nie): {Style.RESET_ALL}").strip().lower()
            self.config[key] = new_value in ['tak', 't', 'yes', 'y', 'true', '1']
        elif key == 'channel_name':  # String
            new_value = input(f"{Fore.GREEN}   Nowa nazwa kanału (np. @jbeegames): {Style.RESET_ALL}").strip()
            self.config[key] = new_value
        else:  # Integer
            try:
                new_value = int(input(f"{Fore.GREEN}   Nowa wartość ({min_val}-{max_val}): {Style.RESET_ALL}").strip())
                if min_val <= new_value <= max_val:
                    self.config[key] = new_value
                else:
                    print(f"{Fore.RED}❌ Wartość musi być między {min_val} a {max_val}!{Style.RESET_ALL}")
                    return
            except ValueError:
                print(f"{Fore.RED}❌ Wprowadź liczbę!{Style.RESET_ALL}")
                return
        
        print(f"{Fore.GREEN}✅ Ustawiono {key} = {self.config[key]}{Style.RESET_ALL}")
    
    def reset_to_default_config(self):
        """Przywraca domyślną konfigurację"""
        default_config = self.load_config()  # To załaduje domyślne
        self.config = default_config
        self.save_config()
    
    def test_proxy_system(self):
        """Testuje proxy"""
        print(f"\n{Fore.CYAN}" + "="*60)
        print("🧪 TEST PROXY")
        print("="*60 + f"{Style.RESET_ALL}")
        
        total = len(self.proxy_manager.proxies)
        if total == 0:
            print(f"{Fore.RED}❌ Brak proxy!{Style.RESET_ALL}")
            return
        
        print(f"📋 Proxy w pliku: {total}")
        
        # Test 10 proxy
        print(f"\n{Fore.YELLOW}🧪 Testuję 10 proxy...{Style.RESET_ALL}")
        working = []
        
        for i in range(min(10, total)):
            proxy = self.proxy_manager.proxies[i]
            print(f"  {i+1}/10: {proxy[:50]}... ", end='')
            if self.simple_proxy_test(proxy):
                working.append(proxy)
                print(f"{Fore.GREEN}✅{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}❌{Style.RESET_ALL}")
            time.sleep(0.5)
        
        print(f"\n{Fore.GREEN}📊 Wynik: {len(working)}/10 działa{Style.RESET_ALL}")
    
    def main_menu(self):
        """Główne menu"""
        while True:
            print(f"\n{Fore.CYAN}" + "="*60)
            print("🚀 YOUTUBE VIEWER ADVANCED")
            print("   Wersja z pełną konfiguracją")
            print("="*60 + f"{Style.RESET_ALL}")
            
            print(f"{Fore.YELLOW}1. 🚀 Uruchom bota{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}2. ⚙️  Konfiguracja{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}3. 🧪 Testuj proxy{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}4. 🏁 Wyjście{Style.RESET_ALL}")
            
            choice = input(f"\n{Fore.GREEN}👉 Wybierz (1-4): {Style.RESET_ALL}").strip()
            
            if choice == '1':
                self.run_bot()
            elif choice == '2':
                self.configuration_menu()
            elif choice == '3':
                self.test_proxy_system()
            elif choice == '4':
                print(f"{Fore.YELLOW}👋 Do widzenia!{Style.RESET_ALL}")
                break
            else:
                print(f"{Fore.RED}❌ Nieprawidłowy wybór{Style.RESET_ALL}")

def main():
    """Główna funkcja"""
    try:
        print(f"{Fore.CYAN}" + "="*60)
        print("🎬 YOUTUBE VIEWER ADVANCED")
        print("   Wersja z pełną konfiguracją")
        print("="*60 + f"{Style.RESET_ALL}")
        
        bot = YouTubeViewerAdvanced()
        bot.main_menu()
        
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}⏹️ Przerwano{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}❌ Błąd: {str(e)}{Style.RESET_ALL}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()