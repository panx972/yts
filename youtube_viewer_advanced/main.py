#!/usr/bin/env python3
"""
YouTube Viewer Advanced - z konfiguracją
"""

import os
import sys
import time
import random
import threading
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

# Import konfiguracji
sys.path.append('.')  # Dodaj bieżący katalog do ścieżki
try:
    import config
    config.load_config()  # Wczytaj konfigurację
except ImportError:
    print(f"{Fore.RED}❌ Brak pliku config.py!{Style.RESET_ALL}")
    sys.exit(1)

class YouTubeViewerAdvanced:
    def __init__(self):
        self.proxy_manager = ProxyManager()
        self.channel_verifier = ChannelVerifier()
        self.running = False
        self.sessions = []
        
        # Utwórz potrzebne katalogi
        self.create_directories()
    
    def create_directories(self):
        """Tworzy potrzebne katalogi"""
        directories = ['profiles', 'fingerprints', 'data']
        for directory in directories:
            if not os.path.exists(directory):
                os.makedirs(directory)
                print(f"{Fore.GREEN}✓ Utworzono katalog: {directory}{Style.RESET_ALL}")
    
    def load_channels(self):
        """Ładuje listę kanałów"""
        channels_file = 'data/channels.txt'
        if not os.path.exists(channels_file):
            print(f"{Fore.YELLOW}⚠ Brak pliku channels.txt{Style.RESET_ALL}")
            return []
        
        channels = []
        with open(channels_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    if '|' in line:
                        # Format: Nazwa|URL|tagi
                        parts = line.split('|')
                        if len(parts) >= 2:
                            channels.append(parts[1].strip())
                    else:
                        channels.append(line)
        
        return channels
    
    def find_working_proxy_for_profile(self, profile_index):
        """Znajduje działające proxy"""
        print(f"{Fore.CYAN}[Profil {profile_index}] 🔍 Szukam proxy...{Style.RESET_ALL}")
        
        max_attempts = config.get_config('max_proxy_attempts', 15)
        use_proxy = config.get_config('use_proxy', True)
        
        if not use_proxy:
            print(f"{Fore.YELLOW}[Profil {profile_index}] ⚡ Pracuję bez proxy{Style.RESET_ALL}")
            return None
        
        for attempt in range(max_attempts):
            try:
                proxy = self.proxy_manager.get_next_proxy()
                print(f"{Fore.CYAN}[Profil {profile_index}] 🧪 Test {attempt+1}/{max_attempts}: {proxy}{Style.RESET_ALL}")
                
                if self.proxy_manager.test_proxy(proxy):
                    print(f"{Fore.GREEN}[Profil {profile_index}] ✅ Proxy działa: {proxy}{Style.RESET_ALL}")
                    return proxy
                else:
                    print(f"{Fore.YELLOW}[Profil {profile_index}] ❌ Proxy nie działa{Style.RESET_ALL}")
                    
            except Exception as e:
                print(f"{Fore.RED}[Profil {profile_index}] ❌ Błąd proxy: {str(e)[:50]}{Style.RESET_ALL}")
        
        print(f"{Fore.YELLOW}[Profil {profile_index}] ⚡ Używam bez proxy{Style.RESET_ALL}")
        return None
    
    def run_single_channel_profile(self, channel_url, profile_index):
        """Uruchamia sesję dla kanału"""
        try:
            print(f"{Fore.CYAN}" + "="*60)
            print(f"🚀 PROFIL {profile_index}: {channel_url}")
            print("="*60 + f"{Style.RESET_ALL}")
            
            # Znajdź proxy
            proxy = self.find_working_proxy_for_profile(profile_index)
            
            # Inicjalizuj przeglądarkę
            browser_manager = BrowserManager(
                profile_index=profile_index,
                use_proxy=proxy
            )
            
            if not browser_manager.driver:
                print(f"{Fore.RED}[Profil {profile_index}] ❌ Błąd przeglądarki{Style.RESET_ALL}")
                return
            
            youtube_actions = YouTubeActions(browser_manager.driver, proxy)
            
            # Otwórz kanał
            print(f"{Fore.CYAN}[Profil {profile_index}] ⚡ Otwieram kanał...{Style.RESET_ALL}")
            print(f"{Fore.CYAN}[Profil {profile_index}] 🔗 Otwieram: {channel_url}{Style.RESET_ALL}")
            
            browser_manager.driver.get(channel_url)
            time.sleep(5)
            
            print(f"{Fore.GREEN}[Profil {profile_index}] ✅ Strona załadowana{Style.RESET_ALL}")
            
            # Pobierz filmy z kanału
            videos = youtube_actions.get_channel_videos(channel_url)
            
            if not videos:
                print(f"{Fore.YELLOW}[Profil {profile_index}] ⚠ Szukam filmów alternatywnie...{Style.RESET_ALL}")
                # Alternatywna metoda pobierania filmów
                videos = self.get_videos_alternative(browser_manager.driver, channel_url)
            
            if not videos:
                print(f"{Fore.RED}[Profil {profile_index}] ❌ Brak filmów{Style.RESET_ALL}")
                browser_manager.quit()
                return
            
            max_videos = config.get_config('max_videos_per_channel', 3)
            videos = videos[:max_videos]
            
            print(f"{Fore.CYAN}[Profil {profile_index}] 📹 Razem {len(videos)} filmów{Style.RESET_ALL}")
            
            # Oglądaj filmy
            successful_views = 0
            
            for i, video_url in enumerate(videos):
                try:
                    print(f"{Fore.CYAN}[Profil {profile_index}] 🎬 Film {i+1}/{len(videos)}...{Style.RESET_ALL}")
                    
                    # Pobierz ustawienia czasu oglądania
                    min_watch = config.get_config('min_watch_time', 30)
                    max_watch = config.get_config('max_watch_time', 120)
                    
                    # Obejrzyj film
                    if youtube_actions.watch_video(video_url, watch_time=random.randint(min_watch, max_watch)):
                        successful_views += 1
                        
                        # Wyświetl czas oglądania
                        watch_display = random.randint(min_watch, max_watch)
                        print(f"{Fore.CYAN}[Profil {profile_index}] ⏱ {watch_display}s...{Style.RESET_ALL}")
                        time.sleep(watch_display)
                    
                    # Przerwa między filmami (jeśli nie ostatni film)
                    if i < len(videos) - 1:
                        min_break = config.get_config('min_break_between_videos', 10)
                        max_break = config.get_config('max_break_between_videos', 30)
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
                'timestamp': datetime.now().strftime("%H:%M:%S")
            })
            
            print(f"{Fore.GREEN}[Profil {profile_index}] ✅ Zakończono - obejrzano {successful_views}/{len(videos)} filmów{Style.RESET_ALL}")
            browser_manager.quit()
            
        except Exception as e:
            print(f"{Fore.RED}[Profil {profile_index}] ❌ Błąd sesji: {str(e)}{Style.RESET_ALL}")
    
    def get_videos_alternative(self, driver, channel_url):
        """Alternatywna metoda pobierania filmów"""
        try:
            # Przejdź do zakładki "Filmy"
            videos_url = channel_url
            if '/@' in channel_url:
                videos_url = channel_url + '/videos'
            elif '/channel/' in channel_url:
                videos_url = channel_url + '/videos'
            
            driver.get(videos_url)
            time.sleep(5)
            
            # Pobierz linki do filmów
            videos = []
            elements = driver.find_elements_by_css_selector('a#video-title-link, ytd-thumbnail a')
            
            for element in elements:
                href = element.get_attribute('href')
                if href and '/watch?v=' in href and href not in videos:
                    videos.append(href)
            
            return videos[:10]  # Maksymalnie 10 filmów
            
        except:
            return []
    
    def show_configuration_menu(self):
        """Menu konfiguracji"""
        while True:
            print(f"\n{Fore.CYAN}" + "="*60)
            print("⚙️  KONFIGURACJA BOTA")
            print("="*60 + f"{Style.RESET_ALL}")
            
            current_config = config.CONFIG
            
            print(f"{Fore.YELLOW}1. Ustawienia oglądania:{Style.RESET_ALL}")
            print(f"   • Filmy na kanał: {current_config['max_videos_per_channel']}")
            print(f"   • Czas oglądania: {current_config['min_watch_time']}-{current_config['max_watch_time']}s")
            print(f"   • Przerwa między filmami: {current_config['min_break_between_videos']}-{current_config['max_break_between_videos']}s")
            
            print(f"\n{Fore.YELLOW}2. Ustawienia proxy:{Style.RESET_ALL}")
            print(f"   • Użyj proxy: {'✅ Tak' if current_config['use_proxy'] else '❌ Nie'}")
            print(f"   • Próby proxy: {current_config['max_proxy_attempts']}")
            
            print(f"\n{Fore.YELLOW}3. Ustawienia ogólne:{Style.RESET_ALL}")
            print(f"   • Równoległe kanały: {current_config['max_concurrent_channels']}")
            print(f"   • Tryb headless: {'✅ Tak' if current_config['headless_mode'] else '❌ Nie'}")
            
            print(f"\n{Fore.YELLOW}4. Zapisz i wyjdź{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}5. Wyjdź bez zapisywania{Style.RESET_ALL}")
            
            choice = input(f"\n{Fore.GREEN}👉 Wybierz (1-5): {Style.RESET_ALL}").strip()
            
            if choice == '1':
                self.configure_watching()
            elif choice == '2':
                self.configure_proxy()
            elif choice == '3':
                self.configure_general()
            elif choice == '4':
                if config.save_config():
                    print(f"{Fore.GREEN}✅ Konfiguracja zapisana!{Style.RESET_ALL}")
                break
            elif choice == '5':
                break
            else:
                print(f"{Fore.RED}❌ Nieprawidłowy wybór{Style.RESET_ALL}")
    
    def configure_watching(self):
        """Konfiguracja oglądania"""
        print(f"\n{Fore.CYAN}🎬 KONFIGURACJA OGLĄDANIA{Style.RESET_ALL}")
        
        try:
            # Maksymalna liczba filmów
            max_videos = input(f"   Maks. filmów na kanał ({config.CONFIG['max_videos_per_channel']}): ").strip()
            if max_videos:
                config.set_config('max_videos_per_channel', int(max_videos))
            
            # Minimalny czas oglądania
            min_time = input(f"   Min. czas oglądania ({config.CONFIG['min_watch_time']}s): ").strip()
            if min_time:
                config.set_config('min_watch_time', int(min_time))
            
            # Maksymalny czas oglądania
            max_time = input(f"   Maks. czas oglądania ({config.CONFIG['max_watch_time']}s): ").strip()
            if max_time:
                config.set_config('max_watch_time', int(max_time))
            
            # Przerwa między filmami
            min_break = input(f"   Min. przerwa ({config.CONFIG['min_break_between_videos']}s): ").strip()
            if min_break:
                config.set_config('min_break_between_videos', int(min_break))
            
            max_break = input(f"   Maks. przerwa ({config.CONFIG['max_break_between_videos']}s): ").strip()
            if max_break:
                config.set_config('max_break_between_videos', int(max_break))
            
            print(f"{Fore.GREEN}✅ Ustawienia oglądania zaktualizowane{Style.RESET_ALL}")
            
        except ValueError:
            print(f"{Fore.RED}❌ Nieprawidłowa wartość!{Style.RESET_ALL}")
    
    def configure_proxy(self):
        """Konfiguracja proxy"""
        print(f"\n{Fore.CYAN}🔗 KONFIGURACJA PROXY{Style.RESET_ALL}")
        
        # Użyj proxy
        use_proxy = input(f"   Używać proxy? (t/n) [{'t' if config.CONFIG['use_proxy'] else 'n'}]: ").strip().lower()
        if use_proxy == 't':
            config.set_config('use_proxy', True)
        elif use_proxy == 'n':
            config.set_config('use_proxy', False)
        
        # Liczba prób proxy
        if config.CONFIG['use_proxy']:
            attempts = input(f"   Próby proxy ({config.CONFIG['max_proxy_attempts']}): ").strip()
            if attempts:
                try:
                    config.set_config('max_proxy_attempts', int(attempts))
                except ValueError:
                    print(f"{Fore.RED}❌ Nieprawidłowa liczba{Style.RESET_ALL}")
        
        print(f"{Fore.GREEN}✅ Ustawienia proxy zaktualizowane{Style.RESET_ALL}")
    
    def configure_general(self):
        """Konfiguracja ogólna"""
        print(f"\n{Fore.CYAN}⚙️  KONFIGURACJA OGÓLNA{Style.RESET_ALL}")
        
        try:
            # Równoległe kanały
            channels = input(f"   Równoległe kanały ({config.CONFIG['max_concurrent_channels']}): ").strip()
            if channels:
                config.set_config('max_concurrent_channels', int(channels))
            
            # Tryb headless
            headless = input(f"   Tryb headless? (t/n) [{'t' if config.CONFIG['headless_mode'] else 'n'}]: ").strip().lower()
            if headless == 't':
                config.set_config('headless_mode', True)
            elif headless == 'n':
                config.set_config('headless_mode', False)
            
            print(f"{Fore.GREEN}✅ Ustawienia ogólne zaktualizowane{Style.RESET_ALL}")
            
        except ValueError:
            print(f"{Fore.RED}❌ Nieprawidłowa wartość!{Style.RESET_ALL}")
    
    def run_bot(self):
        """Uruchamia bota"""
        channels = self.load_channels()
        
        if not channels:
            print(f"{Fore.RED}❌ Brak kanałów!{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Dodaj kanały do data/channels.txt{Style.RESET_ALL}")
            return
        
        print(f"{Fore.CYAN}📺 Znaleziono {len(channels)} kanałów{Style.RESET_ALL}")
        
        max_channels = config.get_config('max_concurrent_channels', 1)
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
            
            # Opóźnienie między uruchomieniami
            if i < len(channels_to_process) - 1:
                time.sleep(random.randint(5, 15))
        
        # Czekaj na zakończenie
        for thread in threads:
            thread.join()
        
        # Podsumowanie
        self.show_summary()
    
    def show_summary(self):
        """Pokazuje podsumowanie"""
        if not self.sessions:
            print(f"{Fore.YELLOW}📊 Brak sesji do podsumowania{Style.RESET_ALL}")
            return
        
        print(f"\n{Fore.CYAN}" + "="*60)
        print("📊 PODSUMOWANIE")
        print("="*60 + f"{Style.RESET_ALL}")
        
        total_views = sum(s['videos_watched'] for s in self.sessions)
        total_videos = sum(s['total_videos'] for s in self.sessions)
        
        print(f"   Sesje: {len(self.sessions)}")
        print(f"   Filmy: {total_views}/{total_videos}")
        print(f"   Sukces: {(total_views/total_videos*100 if total_videos > 0 else 0):.1f}%")
        
        for session in self.sessions:
            print(f"\n   Profil {session['profile']}:")
            print(f"      Kanał: {session['channel'][:50]}...")
            print(f"      Obejrzane: {session['videos_watched']}/{session['total_videos']}")
            print(f"      Czas: {session['timestamp']}")
    
    def main_menu(self):
        """Główne menu"""
        while True:
            print(f"\n{Fore.CYAN}" + "="*60)
            print("🚀 YOUTUBE VIEWER ADVANCED")
            print("="*60 + f"{Style.RESET_ALL}")
            
            print(f"{Fore.YELLOW}1. Uruchom bota{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}2. Konfiguracja{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}3. Testuj proxy{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}4. Wyjście{Style.RESET_ALL}")
            
            choice = input(f"\n{Fore.GREEN}👉 Wybierz (1-4): {Style.RESET_ALL}").strip()
            
            if choice == '1':
                try:
                    channels_input = input(f"{Fore.GREEN}👉 Liczba kanałów (domyślnie 1): {Style.RESET_ALL}").strip()
                    if channels_input:
                        config.set_config('max_concurrent_channels', int(channels_input))
                    
                    self.run_bot()
                except ValueError:
                    print(f"{Fore.RED}❌ Nieprawidłowa liczba!{Style.RESET_ALL}")
            
            elif choice == '2':
                self.show_configuration_menu()
            
            elif choice == '3':
                self.test_proxy_system()
            
            elif choice == '4':
                print(f"{Fore.YELLOW}👋 Do widzenia!{Style.RESET_ALL}")
                break
            
            else:
                print(f"{Fore.RED}❌ Nieprawidłowy wybór{Style.RESET_ALL}")
    
    def test_proxy_system(self):
        """Testuje system proxy"""
        print(f"{Fore.CYAN}\n🧪 TEST PROXY{Style.RESET_ALL}")
        working = self.proxy_manager.find_all_working_proxies()
        
        if working:
            print(f"{Fore.GREEN}✅ Znaleziono {len(working)} działających proxy{Style.RESET_ALL}")
            for i, proxy in enumerate(working[:10], 1):
                print(f"   {i}. {proxy}")
        else:
            print(f"{Fore.RED}❌ Brak działających proxy{Style.RESET_ALL}")

if __name__ == "__main__":
    try:
        bot = YouTubeViewerAdvanced()
        bot.main_menu()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}⏹️ Przerwano{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}❌ Błąd: {str(e)}{Style.RESET_ALL}")