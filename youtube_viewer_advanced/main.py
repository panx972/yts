#!/usr/bin/env python3
"""
YouTube Viewer Advanced - Główny plik programu
Automatyczna zmiana proxy przy błędach
"""

import os
import sys
import time
import random
import threading
import json
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
        self.config = self.load_config()
        
        # Utwórz potrzebne katalogi
        self.create_directories()
    
    def create_directories(self):
        """Tworzy potrzebne katalogi"""
        directories = ['profiles', 'fingerprints', 'data']
        for directory in directories:
            if not os.path.exists(directory):
                os.makedirs(directory)
                print(f"{Fore.GREEN}✓ Utworzono katalog: {directory}{Style.RESET_ALL}")
    
    def load_config(self):
        """Ładuje konfigurację z pliku"""
        config_file = 'data/config.json'
        default_config = {
            'max_concurrent_channels': 1,
            'max_videos_per_channel': 3,
            'min_watch_time': 45,
            'max_watch_time': 90,
            'min_break_between_videos': 10,
            'max_break_between_videos': 30,
            'use_proxy': True,
            'headless_mode': False,
            'enable_likes': True,
            'enable_scroll': True,
            'random_user_agent': True,
            'save_reports': True,
            'max_proxy_retries': 5
        }
        
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                # Aktualizuj domyślną konfigurację
                default_config.update(user_config)
                print(f"{Fore.GREEN}✅ Wczytano konfigurację{Style.RESET_ALL}")
            except Exception as e:
                print(f"{Fore.YELLOW}⚠ Błąd wczytywania konfiguracji: {str(e)}{Style.RESET_ALL}")
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
            with open('data/config.json', 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"{Fore.RED}❌ Błąd zapisywania konfiguracji: {str(e)}{Style.RESET_ALL}")
            return False
    
    def load_channels(self, filename=None):
        """Wczytuje kanały z pliku"""
        if filename is None:
            filename = r'C:\Users\Patry\Desktop\Bots\youtube_viewer_advanced\data\channels.txt'
        
        channels = []
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            print(f"{Fore.CYAN}📄 Analiza pliku channels.txt:{Style.RESET_ALL}")
            
            for i, line in enumerate(lines, 1):
                line = line.strip()
                if line and not line.startswith('#'):
                    print(f"   Linia {i}: '{line}'")
                    
                    # Prosta ekstrakcja URL
                    if 'youtube.com' in line:
                        # Jeśli format z pipem: Nazwa|URL|Tagi
                        if '|' in line:
                            parts = line.split('|')
                            for part in parts:
                                part = part.strip()
                                if 'youtube.com' in part:
                                    # Dodaj https:// jeśli brakuje
                                    if part.startswith('http'):
                                        channels.append(part)
                                    else:
                                        channels.append('https://' + part)
                                    break
                        else:
                            # Zwykły URL
                            if line.startswith('http'):
                                channels.append(line)
                            else:
                                channels.append('https://' + line)
                    elif line.startswith('@'):
                        # Handle: @username
                        channels.append(f'https://www.youtube.com/{line}')
            
            # Usuń duplikaty
            unique_channels = []
            for channel in channels:
                if channel not in unique_channels:
                    unique_channels.append(channel)
            
            print(f"\n{Fore.GREEN}✅ Załadowano {len(unique_channels)} kanałów:{Style.RESET_ALL}")
            for i, channel in enumerate(unique_channels, 1):
                print(f"   {i}. {channel}")
            
            return unique_channels
            
        except Exception as e:
            print(f"{Fore.RED}❌ Błąd ładowania kanałów: {str(e)}{Style.RESET_ALL}")
            return []
    
    def simple_proxy_test(self, proxy):
        """Prosty test proxy"""
        try:
            proxies = {
                'http': proxy,
                'https': proxy
            }
            
            # Krótki timeout
            response = requests.get('http://httpbin.org/ip', 
                                  proxies=proxies, 
                                  timeout=5,
                                  verify=False)
            return response.status_code == 200
        except:
            return False
    
    def find_working_proxy_for_profile(self, profile_index, start_index=0):
        """Znajduje działające proxy - próbuje kolejne z listy"""
        print(f"{Fore.CYAN}[Profil {profile_index}] 🔍 Szukam działającego proxy...{Style.RESET_ALL}")
        
        # Sprawdź czy proxy jest włączone w konfiguracji
        if not self.config.get('use_proxy', True):
            print(f"{Fore.YELLOW}[Profil {profile_index}] ⚡ Pracuję bez proxy{Style.RESET_ALL}")
            return None, 0
        
        try:
            total_proxies = len(self.proxy_manager.proxies)
            if total_proxies == 0:
                print(f"{Fore.RED}[Profil {profile_index}] ❌ Brak proxy!{Style.RESET_ALL}")
                return None, 0
            
            print(f"{Fore.CYAN}[Profil {profile_index}] 📋 Dostępne proxy: {total_proxies}{Style.RESET_ALL}")
            
            # Próbuj kolejne proxy z listy, zaczynając od start_index
            max_attempts = min(15, len(self.proxy_manager.proxies))
            
            for i in range(start_index, start_index + max_attempts):
                # Jeśli przekroczymy długość listy, zawijamy do początku
                proxy_index = i % len(self.proxy_manager.proxies)
                proxy = self.proxy_manager.proxies[proxy_index]
                
                print(f"{Fore.CYAN}[Profil {profile_index}] 🧪 Próbuję proxy {proxy_index+1}/{total_proxies}: {proxy[:50]}...{Style.RESET_ALL}")
                
                # Test proxy
                if self.simple_proxy_test(proxy):
                    print(f"{Fore.GREEN}[Profil {profile_index}] ✅ Proxy działa!{Style.RESET_ALL}")
                    return proxy, proxy_index + 1  # Zwróć proxy i następny indeks
                else:
                    print(f"{Fore.YELLOW}[Profil {profile_index}] ❌ Proxy nie działa, próbuję następne...{Style.RESET_ALL}")
                
                time.sleep(1)  # Krótka przerwa między testami
            
            print(f"{Fore.YELLOW}[Profil {profile_index}] ⚡ Nie znaleziono działającego proxy{Style.RESET_ALL}")
            return None, 0  # Nie znaleziono, zacznij od początku przy następnej próbie
                
        except Exception as e:
            print(f"{Fore.RED}[Profil {profile_index}] ❌ Błąd szukania proxy: {str(e)[:50]}{Style.RESET_ALL}")
            return None, 0
    
    def run_single_channel_profile(self, channel_url, profile_index):
        """Uruchamia sesję dla kanału z automatyczną zmianą proxy"""
        max_proxy_retries = self.config.get('max_proxy_retries', 5)
        proxy_attempts = 0
        current_proxy = None
        proxy_start_index = 0  # Od którego indeksu zaczynamy szukać proxy
        
        while proxy_attempts < max_proxy_retries:
            try:
                print(f"{Fore.CYAN}" + "="*60)
                print(f"🚀 PROFIL {profile_index} (Próba {proxy_attempts + 1}/{max_proxy_retries})")
                print(f"   Kanał: {channel_url}")
                print("="*60 + f"{Style.RESET_ALL}")
                
                # Znajdź nowe proxy dla każdej próby - zaczynając od proxy_start_index
                proxy_result = self.find_working_proxy_for_profile(profile_index, proxy_start_index)
                current_proxy, next_start_index = proxy_result if proxy_result else (None, 0)
                proxy_attempts += 1
                
                # Zaktualizuj indeks dla następnej próby
                proxy_start_index = next_start_index
                
                if not current_proxy and self.config.get('use_proxy', True):
                    print(f"{Fore.YELLOW}[Profil {profile_index}] ⚡ Pracuję bez proxy{Style.RESET_ALL}")
                
                # Inicjalizuj przeglądarkę
                browser_manager = BrowserManager(
                    profile_index=profile_index, 
                    use_proxy=current_proxy if self.config.get('use_proxy', True) else None
                )
                
                if not browser_manager.driver:
                    print(f"{Fore.RED}[Profil {profile_index}] ❌ Błąd przeglądarki{Style.RESET_ALL}")
                    time.sleep(2)
                    continue
                
                youtube_actions = YouTubeActions(browser_manager.driver, current_proxy)
                
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
                    
                    # Jeśli to błąd proxy, spróbuj następne
                    if "proxy" in error_msg.lower() or "tunnel" in error_msg.lower() or "connection" in error_msg.lower():
                        print(f"{Fore.YELLOW}[Profil {profile_index}] ⚠ To proxy nie działa w przeglądarce{Style.RESET_ALL}")
                    
                    browser_manager.quit()
                    continue
                
                # Otwórz kanał
                print(f"{Fore.CYAN}[Profil {profile_index}] ⚡ Otwieram kanał...{Style.RESET_ALL}")
                try:
                    browser_manager.driver.get(channel_url)
                    time.sleep(5)
                    
                    if "youtube.com" not in browser_manager.driver.current_url:
                        print(f"{Fore.RED}[Profil {profile_index}] ❌ Nie udało się załadować YouTube{Style.RESET_ALL}")
                        browser_manager.quit()
                        continue
                        
                    print(f"{Fore.GREEN}[Profil {profile_index}] ✅ Strona załadowana{Style.RESET_ALL}")
                except Exception as page_error:
                    error_msg = str(page_error)
                    print(f"{Fore.RED}[Profil {profile_index}] ❌ Błąd ładowania strony: {error_msg[:50]}{Style.RESET_ALL}")
                    
                    # Sprawdź czy to błąd proxy
                    if "proxy" in error_msg.lower() or "tunnel" in error_msg.lower():
                        print(f"{Fore.YELLOW}[Profil {profile_index}] ⚠ Błąd proxy przy ładowaniu strony{Style.RESET_ALL}")
                    
                    browser_manager.quit()
                    continue
                
                # Pobierz filmy
                max_videos = self.config.get('max_videos_per_channel', 3)
                videos = youtube_actions.get_my_channel_videos(channel_url, max_videos)
                
                if not videos:
                    print(f"{Fore.YELLOW}[Profil {profile_index}] ⚠ Brak filmów{Style.RESET_ALL}")
                    browser_manager.quit()
                    return
                
                print(f"{Fore.CYAN}[Profil {profile_index}] 📹 Znaleziono {len(videos)} filmów{Style.RESET_ALL}")
                
                # Oglądaj filmy
                successful_views = 0
                
                for i, video_url in enumerate(videos):
                    try:
                        print(f"{Fore.CYAN}[Profil {profile_index}] 🎬 Film {i+1}/{len(videos)}...{Style.RESET_ALL}")
                        
                        min_watch = self.config.get('min_watch_time', 30)
                        max_watch = self.config.get('max_watch_time', 120)
                        watch_time = random.randint(min_watch, max_watch)
                        
                        if youtube_actions.watch_my_channel_video(video_url, watch_time):
                            successful_views += 1
                            print(f"{Fore.CYAN}[Profil {profile_index}] ⏱ {watch_time}s...{Style.RESET_ALL}")
                            time.sleep(watch_time)
                        
                        # Przerwa jeśli nie ostatni film
                        if i < len(videos) - 1:
                            min_break = self.config.get('min_break_between_videos', 10)
                            max_break = self.config.get('max_break_between_videos', 30)
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
                    'proxy': current_proxy if current_proxy else 'Brak proxy',
                    'timestamp': datetime.now().strftime("%H:%M:%S"),
                    'proxy_attempts': proxy_attempts
                })
                
                print(f"{Fore.GREEN}[Profil {profile_index}] ✅ Zakończono! Obejrzano {successful_views}/{len(videos)} filmów{Style.RESET_ALL}")
                print(f"{Fore.CYAN}[Profil {profile_index}] 📊 Użyte proxy: {current_proxy if current_proxy else 'Brak'}{Style.RESET_ALL}")
                browser_manager.quit()
                break  # Sukces - wyjdź z pętli
                
            except Exception as e:
                error_msg = str(e)
                print(f"{Fore.RED}[Profil {profile_index}] ❌ Błąd sesji: {error_msg[:100]}")
                
                # Sprawdź czy to błąd proxy
                proxy_keywords = ['proxy', 'connection', 'tunnel', 'net::', 'connect', 'refused', 'failed', 'unreachable']
                is_proxy_error = any(keyword in error_msg.lower() for keyword in proxy_keywords)
                
                if is_proxy_error:
                    print(f"{Fore.YELLOW}[Profil {profile_index}] ⚠ Błąd proxy, próbuję następne...{Style.RESET_ALL}")
                    
                    # Zamknij przeglądarkę jeśli istnieje
                    try:
                        if 'browser_manager' in locals():
                            browser_manager.quit()
                    except:
                        pass
                    
                    if proxy_attempts >= max_proxy_retries:
                        print(f"{Fore.RED}[Profil {profile_index}] ❌ Przekroczono limit prób proxy ({max_proxy_retries}){Style.RESET_ALL}")
                        break
                    
                    time.sleep(3)  # Przerwa przed następną próbą
                    continue
                else:
                    print(f"{Fore.RED}[Profil {profile_index}] ❌ Inny błąd, kończę sesję{Style.RESET_ALL}")
                    break
        
        if proxy_attempts >= max_proxy_retries:
            print(f"{Fore.RED}[Profil {profile_index}] ❌ Nie udało się uruchomić z żadnym proxy{Style.RESET_ALL}")
    
    def run_bot(self):
        """Uruchamia bota"""
        channels = self.load_channels()
        
        if not channels:
            print(f"{Fore.RED}❌ Brak kanałów!{Style.RESET_ALL}")
            return
        
        print(f"{Fore.CYAN}📺 Znaleziono {len(channels)} kanałów{Style.RESET_ALL}")
        
        # Zapytaj o liczbę kanałów
        max_channels = self.config.get('max_concurrent_channels', 1)
        try:
            channels_input = input(f"{Fore.GREEN}👉 Liczba kanałów (domyślnie {max_channels}): {Style.RESET_ALL}").strip()
            if channels_input:
                max_channels = int(channels_input)
        except ValueError:
            print(f"{Fore.RED}❌ Nieprawidłowa liczba{Style.RESET_ALL}")
        
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
        
        # Czekaj na zakończenie
        for thread in threads:
            thread.join()
        
        # Podsumowanie
        self.show_summary()
    
    def show_summary(self):
        """Pokazuje podsumowanie"""
        if not self.sessions:
            print(f"{Fore.YELLOW}📊 Brak sesji{Style.RESET_ALL}")
            return
        
        print(f"\n{Fore.CYAN}" + "="*60)
        print("📊 PODSUMOWANIE")
        print("="*60 + f"{Style.RESET_ALL}")
        
        total_views = sum(s['videos_watched'] for s in self.sessions)
        total_videos = sum(s['total_videos'] for s in self.sessions)
        total_proxy_attempts = sum(s.get('proxy_attempts', 1) for s in self.sessions)
        
        print(f"   Sesje: {len(self.sessions)}")
        print(f"   Filmy: {total_views}/{total_videos}")
        print(f"   Próby proxy: {total_proxy_attempts}")
        
        if total_videos > 0:
            success_rate = (total_views / total_videos) * 100
            print(f"   Sukces: {success_rate:.1f}%")
        
        for session in self.sessions:
            print(f"\n   Profil {session['profile']}:")
            print(f"      Kanał: {session['channel'][:50]}...")
            print(f"      Obejrzane: {session['videos_watched']}/{session['total_videos']}")
            print(f"      Proxy: {session['proxy'][:50] if session['proxy'] != 'Brak proxy' else 'Brak'}")
            print(f"      Próby: {session.get('proxy_attempts', 1)}")
            print(f"      Czas: {session['timestamp']}")
    
    def configuration_menu(self):
        """Menu konfiguracji"""
        while True:
            print(f"\n{Fore.CYAN}" + "="*60)
            print("⚙️  KONFIGURACJA")
            print("="*60 + f"{Style.RESET_ALL}")
            
            print(f"{Fore.YELLOW}Aktualne ustawienia:{Style.RESET_ALL}")
            print(f"  1. Kanały równoległe: {self.config['max_concurrent_channels']}")
            print(f"  2. Filmy na kanał: {self.config['max_videos_per_channel']}")
            print(f"  3. Czas oglądania: {self.config['min_watch_time']}-{self.config['max_watch_time']}s")
            print(f"  4. Przerwa: {self.config['min_break_between_videos']}-{self.config['max_break_between_videos']}s")
            print(f"  5. Użyj proxy: {'✅ Tak' if self.config['use_proxy'] else '❌ Nie'}")
            print(f"  6. Maks. prób proxy: {self.config.get('max_proxy_retries', 5)}")
            
            print(f"\n{Fore.YELLOW}Opcje:{Style.RESET_ALL}")
            print(f"  7. Zapisz i wyjdź")
            print(f"  8. Wyjdź bez zapisywania")
            
            choice = input(f"\n{Fore.GREEN}👉 Wybierz (1-8): {Style.RESET_ALL}").strip()
            
            if choice == '8':
                break
            elif choice == '7':
                self.save_config()
                print(f"{Fore.GREEN}✅ Zapisano!{Style.RESET_ALL}")
                break
            elif choice == '1':
                try:
                    new_val = input(f"   Kanały równoległe ({self.config['max_concurrent_channels']}): ").strip()
                    if new_val:
                        self.config['max_concurrent_channels'] = int(new_val)
                except ValueError:
                    print(f"{Fore.RED}❌ Nieprawidłowa liczba!{Style.RESET_ALL}")
            elif choice == '2':
                try:
                    new_val = input(f"   Filmy na kanał ({self.config['max_videos_per_channel']}): ").strip()
                    if new_val:
                        self.config['max_videos_per_channel'] = int(new_val)
                except ValueError:
                    print(f"{Fore.RED}❌ Nieprawidłowa liczba!{Style.RESET_ALL}")
            elif choice == '3':
                try:
                    min_val = input(f"   Min. czas ({self.config['min_watch_time']}s): ").strip()
                    if min_val:
                        self.config['min_watch_time'] = int(min_val)
                    
                    max_val = input(f"   Max. czas ({self.config['max_watch_time']}s): ").strip()
                    if max_val:
                        self.config['max_watch_time'] = int(max_val)
                except ValueError:
                    print(f"{Fore.RED}❌ Nieprawidłowa liczba!{Style.RESET_ALL}")
            elif choice == '4':
                try:
                    min_val = input(f"   Min. przerwa ({self.config['min_break_between_videos']}s): ").strip()
                    if min_val:
                        self.config['min_break_between_videos'] = int(min_val)
                    
                    max_val = input(f"   Max. przerwa ({self.config['max_break_between_videos']}s): ").strip()
                    if max_val:
                        self.config['max_break_between_videos'] = int(max_val)
                except ValueError:
                    print(f"{Fore.RED}❌ Nieprawidłowa liczba!{Style.RESET_ALL}")
            elif choice == '5':
                current = self.config['use_proxy']
                new_val = input(f"   Używać proxy? (t/n) [{'t' if current else 'n'}]: ").strip().lower()
                if new_val == 't':
                    self.config['use_proxy'] = True
                elif new_val == 'n':
                    self.config['use_proxy'] = False
            elif choice == '6':
                try:
                    new_val = input(f"   Maks. prób proxy ({self.config.get('max_proxy_retries', 5)}): ").strip()
                    if new_val:
                        self.config['max_proxy_retries'] = int(new_val)
                except ValueError:
                    print(f"{Fore.RED}❌ Nieprawidłowa liczba!{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}❌ Nieprawidłowy wybór{Style.RESET_ALL}")
    
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
        
        print(f"\n{Fore.YELLOW}Opcje:{Style.RESET_ALL}")
        print(f"  1. Testuj WSZYSTKIE proxy")
        print(f"  2. Znajdź pierwsze działające")
        print(f"  3. Szybki test 10 proxy")
        
        choice = input(f"\n{Fore.GREEN}👉 Wybierz (1-3): {Style.RESET_ALL}").strip()
        
        if choice == '1':
            working = []
            for i, proxy in enumerate(self.proxy_manager.proxies):
                print(f"   Test {i+1}/{total}: {proxy[:50]}...")
                if self.simple_proxy_test(proxy):
                    working.append(proxy)
                    print(f"   {Fore.GREEN}✅ Działa{Style.RESET_ALL}")
                else:
                    print(f"   {Fore.RED}❌ Nie działa{Style.RESET_ALL}")
                time.sleep(0.5)
            
            if working:
                print(f"\n{Fore.GREEN}✅ Znaleziono {len(working)} działających proxy{Style.RESET_ALL}")
                for i, proxy in enumerate(working[:10], 1):
                    print(f"   {i}. {proxy}")
            else:
                print(f"\n{Fore.RED}❌ Brak działających proxy{Style.RESET_ALL}")
                
        elif choice == '2':
            print(f"{Fore.CYAN}🔍 Szukam pierwszego działającego proxy...{Style.RESET_ALL}")
            for i, proxy in enumerate(self.proxy_manager.proxies[:20]):
                print(f"   Próba {i+1}/20: {proxy[:50]}...")
                if self.simple_proxy_test(proxy):
                    print(f"\n{Fore.GREEN}✅ Znaleziono: {proxy}{Style.RESET_ALL}")
                    return
                time.sleep(0.5)
            
            print(f"\n{Fore.RED}❌ Nie znaleziono działającego proxy{Style.RESET_ALL}")
            
        elif choice == '3':
            print(f"{Fore.CYAN}🧪 Szybki test 10 proxy...{Style.RESET_ALL}")
            tested = 0
            working = []
            
            for proxy in self.proxy_manager.proxies[:10]:
                tested += 1
                print(f"   Test {tested}/10: {proxy[:50]}...")
                if self.simple_proxy_test(proxy):
                    working.append(proxy)
                    print(f"   {Fore.GREEN}✅ Działa{Style.RESET_ALL}")
                else:
                    print(f"   {Fore.RED}❌ Nie działa{Style.RESET_ALL}")
                time.sleep(0.5)
            
            print(f"\n{Fore.GREEN}📊 Wynik: {len(working)}/{tested} działa{Style.RESET_ALL}")
    
    def download_fresh_proxies(self):
        """Pobiera świeże proxy"""
        print(f"\n{Fore.CYAN}" + "="*60)
        print("🔄 POBIERANIE ŚWIEŻYCH PROXY")
        print("="*60 + f"{Style.RESET_ALL}")
        
        if os.path.exists('get_fresh_proxies.py'):
            try:
                # Uruchom skrypt
                os.system('python get_fresh_proxies.py')
                
                # Przeładuj proxy
                self.proxy_manager = ProxyManager()
                print(f"{Fore.GREEN}✅ Proxy zaktualizowane!{Style.RESET_ALL}")
                
            except Exception as e:
                print(f"{Fore.RED}❌ Błąd: {str(e)}{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}❌ Brak pliku get_fresh_proxies.py!{Style.RESET_ALL}")
    
    def main_menu(self):
        """Główne menu programu"""
        while True:
            print(f"\n{Fore.CYAN}" + "="*60)
            print("🚀 YOUTUBE VIEWER ADVANCED")
            print("   Automatyczna zmiana proxy przy błędach")
            print("="*60 + f"{Style.RESET_ALL}")
            
            print(f"{Fore.YELLOW}1. 🚀 Uruchom bota{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}2. ⚙️  Konfiguracja{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}3. 🧪 Testuj proxy{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}4. 🔄 Pobierz świeże proxy{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}5. 🏁 Wyjście{Style.RESET_ALL}")
            
            choice = input(f"\n{Fore.GREEN}👉 Wybierz (1-5): {Style.RESET_ALL}").strip()
            
            if choice == '1':
                self.run_bot()
            elif choice == '2':
                self.configuration_menu()
            elif choice == '3':
                self.test_proxy_system()
            elif choice == '4':
                self.download_fresh_proxies()
            elif choice == '5':
                print(f"{Fore.YELLOW}👋 Do widzenia!{Style.RESET_ALL}")
                break
            else:
                print(f"{Fore.RED}❌ Nieprawidłowy wybór{Style.RESET_ALL}")

def main():
    """Główna funkcja"""
    try:
        print(f"{Fore.CYAN}" + "="*60)
        print("🎬 YOUTUBE VIEWER ADVANCED")
        print("="*60 + f"{Style.RESET_ALL}")
        
        bot = YouTubeViewerAdvanced()
        bot.main_menu()
        
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}⏹️ Przerwano{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}❌ Błąd: {str(e)}{Style.RESET_ALL}")

if __name__ == "__main__":
    main()