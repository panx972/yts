#!/usr/bin/env python3
"""
YouTube Viewer Advanced - Główny plik programu
POPRAWIONE: Błędy składni i importy
"""

import os
import sys
import time
import threading
import random
from colorama import init, Fore, Style
from datetime import datetime

# Inicjalizacja colorama
init(autoreset=True)

# Dodaj katalog modułów do ścieżki - POPRAWIONE
current_dir = os.path.dirname(os.path.abspath(__file__))
modules_dir = os.path.join(current_dir, 'modules')
sys.path.insert(0, modules_dir)  # Dodaj na początek ścieżki

# Import modułów
try:
    from browser_manager import BrowserManager
    from proxy_manager import ProxyManager
    from youtube_actions import YouTubeActions
    from channel_verifier import ChannelVerifier
    print(f"{Fore.GREEN}✅ Załadowano wszystkie moduły{Style.RESET_ALL}")
except ImportError as e:
    print(f"{Fore.RED}❌ Błąd importu modułów: {str(e)}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}📁 Sprawdzam katalog modules/:{Style.RESET_ALL}")
    if os.path.exists(modules_dir):
        files = os.listdir(modules_dir)
        print(f"   Znaleziono: {files}")
    else:
        print(f"   ❌ Katalog modules/ nie istnieje!")
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
        """Tworzy potrzebne katalogi jeśli nie istnieją"""
        directories = ['data']
        for directory in directories:
            if not os.path.exists(directory):
                os.makedirs(directory)
                print(f"{Fore.GREEN}✓ Utworzono katalog: {directory}{Style.RESET_ALL}")
    
    def load_channels(self):
        """Ładuje listę kanałów z pliku"""
        channels_file = 'data/channels.txt'
        if not os.path.exists(channels_file):
            print(f"{Fore.YELLOW}⚠ Plik channels.txt nie istnieje. Tworzę przykładowy...{Style.RESET_ALL}")
            with open(channels_file, 'w', encoding='utf-8') as f:
                f.write("# Przykładowe kanały YouTube\n")
                f.write("https://www.youtube.com/@jbeegames\n")
            return []
        
        channels = []
        with open(channels_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    if '|' in line:
                        parts = line.split('|')
                        for part in parts:
                            part = part.strip()
                            if 'youtube.com' in part or 'youtu.be' in part:
                                channels.append(part)
                                break
                    else:
                        channels.append(line)
        
        return channels
    
    def load_videos(self):
        """Ładuje listę filmów z pliku"""
        videos_file = 'data/videos.txt'
        if not os.path.exists(videos_file):
            return None
        
        videos = []
        with open(videos_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    videos.append(line)
        
        return videos if videos else None
    
    def find_working_proxy_for_profile(self, profile_index, max_attempts=15):
        """Znajduje działające proxy dla profilu"""
        print(f"{Fore.CYAN}[Profil {profile_index}] 🔍 Szukam działającego proxy...{Style.RESET_ALL}")
        
        for attempt in range(max_attempts):
            try:
                proxy = self.proxy_manager.get_next_proxy()
                print(f"{Fore.CYAN}[Profil {profile_index}] 🧪 Test {attempt+1}/{max_attempts}: {proxy}...{Style.RESET_ALL}")
                
                if self.proxy_manager.test_proxy(proxy):
                    print(f"{Fore.GREEN}[Profil {profile_index}] ✅ Znaleziono działające proxy: {proxy}{Style.RESET_ALL}")
                    return proxy
                else:
                    print(f"{Fore.YELLOW}[Profil {profile_index}] ❌ Proxy nie działa: {proxy}{Style.RESET_ALL}")
                    
            except IndexError:
                print(f"{Fore.RED}[Profil {profile_index}] ❌ Brak dostępnych proxy!{Style.RESET_ALL}")
                time.sleep(2)
            except Exception as e:
                print(f"{Fore.RED}[Profil {profile_index}] ❌ Błąd testowania proxy: {str(e)[:100]}{Style.RESET_ALL}")
        
        print(f"{Fore.YELLOW}[Profil {profile_index}] ⚠ Używam bez proxy...{Style.RESET_ALL}")
        return None
    
    def run_single_channel_profile(self, channel_url, profile_index, videos_list=None):
        """Uruchamia sesję dla pojedynczego kanału"""
        try:
            print(f"{Fore.CYAN}============================================================{Style.RESET_ALL}")
            print(f"{Fore.GREEN}🚀 PROFIL {profile_index}: {channel_url}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}============================================================{Style.RESET_ALL}")
            
            proxy = self.find_working_proxy_for_profile(profile_index)
            
            # POPRAWIONE: Użyj use_proxy zamiast proxy
            browser_manager = BrowserManager(profile_index=profile_index, use_proxy=proxy)
            
            youtube_actions = YouTubeActions(browser_manager.driver, proxy)
            
            # POMIŃ WERYFIKACJĘ
            print(f"{Fore.YELLOW}[Profil {profile_index}] ⚡ Otwieram kanał...{Style.RESET_ALL}")
            
            try:
                print(f"{Fore.CYAN}[Profil {profile_index}] 🔗 Otwieram: {channel_url}{Style.RESET_ALL}")
                browser_manager.driver.get(channel_url)
                time.sleep(5)
                
                current_title = browser_manager.driver.title.lower()
                current_url = browser_manager.driver.current_url
                
                if "youtube" in current_title or "youtube.com" in current_url:
                    print(f"{Fore.GREEN}[Profil {profile_index}] ✅ Strona załadowana{Style.RESET_ALL}")
                else:
                    print(f"{Fore.YELLOW}[Profil {profile_index}] ⚠ URL: {current_url}{Style.RESET_ALL}")
            
            except Exception as e:
                print(f"{Fore.RED}[Profil {profile_index}] ❌ Błąd: {str(e)[:100]}{Style.RESET_ALL}")
                browser_manager.quit()
                return
            
            # Użyj listy filmów
            if videos_list:
                videos = videos_list
                print(f"{Fore.CYAN}[Profil {profile_index}] 📹 Używam {len(videos)} filmów z pliku{Style.RESET_ALL}")
            else:
                try:
                    videos = youtube_actions.get_channel_videos(channel_url)
                    if not videos:
                        print(f"{Fore.YELLOW}[Profil {profile_index}] ⚠ Szukam filmów alternatywnie...{Style.RESET_ALL}")
                        
                        videos_tab_url = f"{channel_url.rstrip('/')}/videos"
                        browser_manager.driver.get(videos_tab_url)
                        time.sleep(5)
                        
                        video_elements = browser_manager.driver.find_elements("css selector", "a#video-title-link")
                        videos = []
                        for elem in video_elements[:10]:
                            href = elem.get_attribute("href")
                            if href and "/watch?v=" in href:
                                videos.append(href)
                        
                        print(f"{Fore.CYAN}[Profil {profile_index}] 📹 Znaleziono {len(videos)} filmów{Style.RESET_ALL}")
                except Exception as e:
                    print(f"{Fore.RED}[Profil {profile_index}] ❌ Błąd: {str(e)[:100]}{Style.RESET_ALL}")
                    browser_manager.quit()
                    return
            
            if not videos:
                print(f"{Fore.RED}[Profil {profile_index}] ❌ Brak filmów{Style.RESET_ALL}")
                browser_manager.quit()
                return
            
            print(f"{Fore.CYAN}[Profil {profile_index}] 📹 Razem {len(videos)} filmów{Style.RESET_ALL}")
            
            # Maksymalnie 3 filmy
            videos = videos[:3]
            
            # Oglądaj filmy
            successful_views = 0
            for i, video_url in enumerate(videos):
                try:
                    print(f"{Fore.CYAN}[Profil {profile_index}] 🎬 Film {i+1}/{len(videos)}...{Style.RESET_ALL}")
                    
                    if youtube_actions.watch_video(video_url):
                        successful_views += 1
                        
                        watch_time = random.randint(30, 90)
                        print(f"{Fore.CYAN}[Profil {profile_index}] ⏱ {watch_time}s...{Style.RESET_ALL}")
                        time.sleep(watch_time)
                        
                        if random.random() > 0.7:
                            try:
                                youtube_actions.like_video()
                                print(f"{Fore.GREEN}[Profil {profile_index}] 👍 Polubiono{Style.RESET_ALL}")
                            except:
                                pass
                    
                    if i < len(videos) - 1:
                        delay = random.randint(10, 25)
                        print(f"{Fore.CYAN}[Profil {profile_index}] ⏳ Przerwa {delay}s...{Style.RESET_ALL}")
                        time.sleep(delay)
                        
                except Exception as e:
                    print(f"{Fore.RED}[Profil {profile_index}] ❌ Błąd: {str(e)[:80]}{Style.RESET_ALL}")
                    continue
            
            print(f"{Fore.GREEN}[Profil {profile_index}] ✅ Koniec. Wyświetlenia: {successful_views}/{len(videos)}{Style.RESET_ALL}")
            browser_manager.quit()
            
            # POPRAWIONE: Słownik bez błędów składni
            session_data = {
                'profile': profile_index,
                'channel': channel_url,
                'views': successful_views,
                'proxy': proxy or 'Brak proxy',
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            self.sessions.append(session_data)
            
        except Exception as e:
            print(f"{Fore.RED}[Profil {profile_index}] ❌ Błąd sesji: {str(e)}{Style.RESET_ALL}")
    
    def run_multiple_channels(self, max_concurrent=3):
        """Uruchamia wiele kanałów"""
        channels = self.load_channels()
        
        if not channels:
            print(f"{Fore.RED}❌ Brak kanałów!{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Dodaj do data/channels.txt{Style.RESET_ALL}")
            return
        
        print(f"{Fore.CYAN}📺 Znaleziono {len(channels)} kanałów{Style.RESET_ALL}")
        
        videos_list = self.load_videos()
        if videos_list:
            print(f"{Fore.CYAN}🎬 Filmy z pliku: {len(videos_list)}{Style.RESET_ALL}")
        
        threads = []
        self.running = True
        
        for i, channel_url in enumerate(channels[:max_concurrent]):
            try:
                thread = threading.Thread(
                    target=self.run_single_channel_profile,
                    args=(channel_url, i+1, videos_list),
                    name=f"Channel-{i+1}"
                )
                threads.append(thread)
                thread.start()
                
                if i < len(channels[:max_concurrent]) - 1:
                    delay = random.randint(5, 15)
                    print(f"{Fore.CYAN}⏳ Czekam {delay}s...{Style.RESET_ALL}")
                    time.sleep(delay)
                    
            except Exception as e:
                print(f"{Fore.RED}❌ Błąd: {str(e)}")
        
        for thread in threads:
            thread.join()
        
        self.running = False
        self.show_summary()
    
    def show_summary(self):
        """Pokazuje podsumowanie"""
        print(f"{Fore.CYAN}\n" + "="*60)
        print("📊 PODSUMOWANIE")
        print("="*60 + f"{Style.RESET_ALL}")
        
        if not self.sessions:
            print(f"{Fore.YELLOW}❌ Brak sesji{Style.RESET_ALL}")
            return
        
        total_views = sum(session['views'] for session in self.sessions)
        
        print(f"{Fore.GREEN}✅ Sesje: {len(self.sessions)}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}👁️  Wyświetlenia: {total_views}{Style.RESET_ALL}")
        
        for session in self.sessions:
            print(f"\n{Fore.YELLOW}Profil {session['profile']}:{Style.RESET_ALL}")
            print(f"  Kanał: {session['channel'][:50]}...")
            print(f"  Wyświetlenia: {session['views']}")
            print(f"  Proxy: {session['proxy']}")
            print(f"  Czas: {session['timestamp']}")
    
    def test_proxy_system(self):
        """Testuje proxy"""
        print(f"{Fore.CYAN}\n" + "="*60)
        print("🧪 TEST PROXY")
        print("="*60 + f"{Style.RESET_ALL}")
        
        working_proxies = self.proxy_manager.find_working_proxies(max_test=20)
        
        if working_proxies:
            print(f"{Fore.GREEN}✅ Działające: {len(working_proxies)}{Style.RESET_ALL}")
            for i, proxy in enumerate(working_proxies[:10], 1):
                print(f"  {i:2d}. {proxy}")
            
            if len(working_proxies) > 10:
                print(f"  ... i {len(working_proxies)-10} więcej")
        else:
            print(f"{Fore.RED}❌ Brak proxy!{Style.RESET_ALL}")
    
    def run(self):
        """Główna pętla"""
        print(f"{Fore.CYAN}" + "="*60)
        print("🚀 YOUTUBE VIEWER ADVANCED")
        print("="*60 + f"{Style.RESET_ALL}")
        
        while True:
            print(f"\n{Fore.YELLOW}🔧 MENU:{Style.RESET_ALL}")
            print(f"{Fore.CYAN}1. Uruchom bota{Style.RESET_ALL}")
            print(f"{Fore.CYAN}2. Testuj proxy{Style.RESET_ALL}")
            print(f"{Fore.CYAN}3. Wyjście{Style.RESET_ALL}")
            
            choice = input(f"\n{Fore.GREEN}👉 Wybierz (1-3): {Style.RESET_ALL}").strip()
            
            if choice == '1':
                try:
                    max_channels = int(input(f"{Fore.GREEN}👉 Liczba kanałów (domyślnie 1): {Style.RESET_ALL}") or "1")
                    self.run_multiple_channels(max_channels)
                except ValueError:
                    print(f"{Fore.RED}❌ Błąd! Używam 1{Style.RESET_ALL}")
                    self.run_multiple_channels(1)
                    
            elif choice == '2':
                self.test_proxy_system()
                
            elif choice == '3':
                print(f"{Fore.YELLOW}👋 Zamykam...{Style.RESET_ALL}")
                break
                
            else:
                print(f"{Fore.RED}❌ Zły wybór!{Style.RESET_ALL}")

if __name__ == "__main__":
    try:
        bot = YouTubeViewerAdvanced()
        bot.run()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}⏹️ Przerwano{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}❌ Błąd: {str(e)}{Style.RESET_ALL}")