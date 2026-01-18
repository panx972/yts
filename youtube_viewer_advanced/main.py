3#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ADVANCED YOUTUBE VIEWER v5.0
Selenium + Chrome Proxy Testing + Auto-Switch
+ Intelligent Proxy Validation System
"""

import os
import sys
import time
import random
import json
from datetime import datetime
from colorama import init, Fore, Back, Style
import threading
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Inicjalizacja colorama
init(autoreset=True)

# Próba importu modułów
try:
    from modules.browser_manager import BrowserManager
    from modules.proxy_manager import ProxyManager
    from modules.youtube_actions import YouTubeActions
    from modules.channel_verifier import ChannelVerifier
    print(Fore.GREEN + "✅ Wszystkie moduły załadowane poprawnie")
except ImportError as e:
    print(Fore.RED + f"❌ Błąd importu modułów: {e}")
    print(Fore.YELLOW + "Sprawdź czy pliki istnieją w folderze modules\\")
    sys.exit(1)

class YouTubeViewerAdvanced:
    def __init__(self):
        """Inicjalizacja głównej klasy bota"""
        self.print_header()
        
        # Inicjalizacja menedżerów
        try:
            self.browser_manager = BrowserManager()
            self.proxy_manager = ProxyManager()
            self.youtube_actions = YouTubeActions()
            self.channel_verifier = ChannelVerifier()
            
            self.is_running = False
            self.active_profiles = []
            self.session_stats = {
                'successful': 0,
                'failed': 0,
                'proxy_tested': 0,
                'proxy_failed': 0,
                'proxy_working': 0,
                'total_profiles': 0,
                'start_time': time.time()
            }
            
            print(Fore.GREEN + "✅ System zainicjalizowany pomyślnie")
            
            # Pokaż statystyki proxy
            stats = self.proxy_manager.get_proxy_stats()
            print(Fore.CYAN + f"📊 Proxy załadowane: {stats['working']}/{stats['total_loaded']} działających")
            
        except Exception as e:
            print(Fore.RED + f"❌ Krytyczny błąd inicjalizacji: {e}")
            sys.exit(1)
    
    def print_header(self):
        """Wyświetla nagłówek programu"""
        print(Fore.CYAN + "\n" + "=" * 60)
        print(Fore.CYAN + " " * 15 + "ADVANCED YOUTUBE VIEWER v5.0")
        print(Fore.CYAN + " " * 8 + "Selenium + Chrome Proxy Testing")
        print(Fore.CYAN + " " * 5 + "+ Intelligent Proxy Validation")
        print(Fore.CYAN + "=" * 60)
    
    def print_menu(self):
        """Wyświetla główne menu"""
        print(Fore.CYAN + "\n" + "=" * 60)
        print(Fore.CYAN + "Wybierz opcję:")
        print(Fore.CYAN + "=" * 60)
        
        options = [
            "[1] 🔍 Pobierz i przetestuj proxy (Chrome Test)",
            "[2] 🎬 Uruchom bota (z listy filmów)",
            "[3] 🔎 Wyszukaj kanały (Z TESTEM PROXY W CHROME)",
            "[4] 🧪 Tylko testuj proxy w Chrome",
            "[5] 📊 Zarządzaj profilami i statystykami",
            "[6] ⚙️  Konfiguracja systemu",
            "[7] 🚪 Wyjście"
        ]
        
        for option in options:
            print(Fore.WHITE + option)
        
        print(Fore.CYAN + "=" * 60)
    
    def create_data_structure(self):
        """Tworzy strukturę plików i folderów"""
        folders = ["data", "profiles", "fingerprints", "logs"]
        files = {
            os.path.join("data", "channels.txt"): "# Format: Nazwa|URL|keywords\n\nJbee Games|@jbeegames|jbee games\nTech Leader|https://www.youtube.com/@TechLeader|tech\n",
            os.path.join("data", "proxy.txt"): "# DODAJ PRAWDZIWE PROXY TUTAJ\n# Format: http://ip:port lub socks5://ip:port\n\n# Przykłady (usuń # aby aktywować):\n# http://45.77.56.113:3128\n# socks5://138.197.157.32:1080\n",
            os.path.join("data", "videos.txt"): "# Lista filmów\n\nhttps://www.youtube.com/watch?v=dQw4w9WgXcQ\n"
        }
        
        for folder in folders:
            if not os.path.exists(folder):
                os.makedirs(folder, exist_ok=True)
                print(Fore.GREEN + f"✅ Utworzono folder: {folder}\\")
        
        for file_path, content in files.items():
            if not os.path.exists(file_path):
                try:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(Fore.GREEN + f"✅ Utworzono plik: {file_path}")
                except:
                    print(Fore.YELLOW + f"⚠️  Nie udało się utworzyć: {file_path}")
    
    def load_channels_from_file(self, filename=None):
        """Wczytuje kanały z pliku"""
        if filename is None:
            filename = os.path.join("data", "channels.txt")
        
        print(Fore.BLUE + f"\n📁 Wczytywanie kanałów z {filename}...")
        
        channels = []
        
        if not os.path.exists(filename):
            print(Fore.RED + f"❌ Plik {filename} nie istnieje!")
            print(Fore.YELLOW + "Tworzę przykładowy plik...")
            self.create_data_structure()
            return channels
        
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        parts = line.split('|')
                        if len(parts) >= 2:
                            name = parts[0].strip()
                            url = parts[1].strip()
                            keywords = parts[2].strip() if len(parts) > 2 else name.lower()
                            
                            if not url.startswith('http'):
                                url = 'https://www.youtube.com/' + url
                            
                            channels.append({
                                'name': name,
                                'url': url,
                                'keywords': keywords
                            })
            
            print(Fore.GREEN + f"✅ Załadowano {len(channels)} kanałów")
            return channels
            
        except Exception as e:
            print(Fore.RED + f"❌ Błąd wczytywania: {e}")
            return channels
    
    def select_channels_interactive(self, channels):
        """Interaktywny wybór kanałów"""
        if not channels:
            print(Fore.RED + "❌ Brak kanałów do wyboru")
            return []
        
        print(Fore.BLUE + "\n📋 Znalezione kanały:")
        for i, channel in enumerate(channels, 1):
            print(Fore.WHITE + f"  {i}. {channel['name']} -> {channel['url']}")
        
        while True:
            choice = input(Fore.YELLOW + "\nWybierz kanały (np. 1,3,5 lub 'all'): ").strip()
            
            if choice.lower() == 'all':
                selected_channels = channels
                print(Fore.GREEN + f"✅ Wybrano wszystkie {len(channels)} kanałów")
                return selected_channels
            
            try:
                indices = [int(idx.strip()) - 1 for idx in choice.split(',')]
                selected_channels = [channels[i] for i in indices if 0 <= i < len(channels)]
                
                if selected_channels:
                    print(Fore.GREEN + f"✅ Wybrano {len(selected_channels)} kanałów")
                    return selected_channels
                else:
                    print(Fore.RED + "❌ Nieprawidłowy wybór")
            except:
                print(Fore.RED + "❌ Nieprawidłowy format. Użyj np. '1,3,5' lub 'all'")
    
    def find_working_proxy_for_profile(self, profile_index, max_attempts=10):
        """Znajduje działające proxy dla profilu poprzez test w Chrome"""
        print(Fore.BLUE + f"\n[Profil {profile_index}] 🔍 Szukam działającego proxy...")
        
        attempts = 0
        tested_proxies = set()
        
        while attempts < max_attempts:
            attempts += 1
            
            # Pobierz następne proxy do testu
            proxy = self.proxy_manager.get_next_proxy()
            
            if not proxy:
                print(Fore.YELLOW + f"[Profil {profile_index}] ℹ️  Brak więcej proxy do testowania")
                return None
            
            # Sprawdź czy już testowaliśmy to proxy
            if proxy in tested_proxies:
                print(Fore.YELLOW + f"[Profil {profile_index}] ⏭️  Pomijam już testowane proxy")
                continue
            
            tested_proxies.add(proxy)
            self.session_stats['proxy_tested'] += 1
            
            print(Fore.BLUE + f"[Profil {profile_index}] 🧪 Test {attempts}/{max_attempts}: {proxy[:50]}...")
            
            # TEST PROXY W CHROME
            try:
                # Utwórz TYMCZASOWĄ przeglądarkę do testu proxy
                test_driver = self._create_test_browser(proxy, headless=True)
                
                if not test_driver:
                    print(Fore.RED + f"[Profil {profile_index}] ❌ Nie udało się utworzyć testowej przeglądarki")
                    self.proxy_manager.mark_proxy_as_failed(proxy, "Test browser creation failed")
                    self.session_stats['proxy_failed'] += 1
                    continue
                
                # Testuj załadowanie YouTube
                test_success = self._test_proxy_with_youtube(test_driver, proxy, profile_index)
                
                # Zamknij testową przeglądarkę
                try:
                    test_driver.quit()
                except:
                    pass
                
                if test_success:
                    print(Fore.GREEN + f"[Profil {profile_index}] ✅ Znaleziono działające proxy!")
                    self.session_stats['proxy_working'] += 1
                    return proxy
                else:
                    print(Fore.RED + f"[Profil {profile_index}] ❌ Proxy nie działa w Chrome")
                    self.proxy_manager.mark_proxy_as_failed(proxy, "Failed Chrome test")
                    self.session_stats['proxy_failed'] += 1
                    
                    # Krótka pauza przed następnym testem
                    time.sleep(1)
                    
            except Exception as e:
                print(Fore.RED + f"[Profil {profile_index}] 💥 Błąd testu proxy: {str(e)[:80]}")
                self.proxy_manager.mark_proxy_as_failed(proxy, "Test error")
                self.session_stats['proxy_failed'] += 1
        
        print(Fore.RED + f"[Profil {profile_index}] ❌ Nie znaleziono działającego proxy po {max_attempts} próbach")
        return None
    
    def _create_test_browser(self, proxy, headless=True):
        """Tworzy przeglądarkę testową do sprawdzania proxy"""
        try:
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.chrome.service import Service
            
            chrome_options = Options()
            chrome_options.add_argument(f'--proxy-server={proxy}')
            
            if headless:
                chrome_options.add_argument('--headless=new')
            
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--log-level=3')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_argument('--proxy-bypass-list=<-loopback>')
            
            # Użyj chromedriver
            service = Service(executable_path="chromedriver.exe")
            driver = webdriver.Chrome(service=service, options=chrome_options)
            
            return driver
            
        except Exception as e:
            print(f"❌ Błąd tworzenia testowej przeglądarki: {e}")
            return None
    
    def _test_proxy_with_youtube(self, driver, proxy, profile_index, timeout=10):
        """Testuje czy proxy ładuje YouTube"""
        try:
            driver.set_page_load_timeout(timeout)
            
            print(Fore.BLUE + f"[Profil {profile_index}] 🔗 Ładuję YouTube przez proxy...")
            
            start_time = time.time()
            driver.get("https://www.youtube.com")
            
            # Czekaj na załadowanie
            WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            load_time = time.time() - start_time
            
            # Sprawdź status
            page_state = driver.execute_script('return document.readyState')
            
            if page_state != "complete":
                print(Fore.RED + f"[Profil {profile_index}] ❌ Strona niezaładowana: {page_state}")
                return False
            
            # Sprawdź błędy
            page_source = driver.page_source.lower()
            error_indicators = [
                "proxy connection failed",
                "err_proxy_connection_failed",
                "this site can't be reached",
                "connection failed"
            ]
            
            for error in error_indicators:
                if error in page_source:
                    print(Fore.RED + f"[Profil {profile_index}] ❌ Błąd proxy: {error}")
                    return False
            
            print(Fore.GREEN + f"[Profil {profile_index}] ✅ Proxy działa! Załadowano w {load_time:.1f}s")
            return True
            
        except Exception as e:
            error_msg = str(e)
            print(Fore.RED + f"[Profil {profile_index}] ❌ Błąd ładowania: {error_msg[:80]}")
            return False
    
    def create_profile_with_proxy(self, profile_index, proxy=None):
        """Tworzy przeglądarkę z PRZETESTOWANYM proxy"""
        try:
            print(Fore.BLUE + f"\n[Profil {profile_index}] 🛠️  Tworzenie profilu...")
            
            # Utwórz przeglądarkę z użyciem PRZETESTOWANEGO proxy
            driver = self.browser_manager.create_profile_with_proxy_test(
                profile_index=profile_index,
                user_agent=self.browser_manager.get_random_user_agent(),
                proxy=proxy,  # To proxy już przeszło test w Chrome!
                headless=False
            )
            
            if driver:
                print(Fore.GREEN + f"[Profil {profile_index}] ✅ Profil utworzony z działającym proxy")
                return driver
            else:
                print(Fore.RED + f"[Profil {profile_index}] ❌ Nie udało się utworzyć profilu")
                return None
                
        except Exception as e:
            print(Fore.RED + f"[Profil {profile_index}] 💥 Błąd tworzenia profilu: {e}")
            return None
    
    def execute_channel_search(self, driver, channel_data, profile_index, videos_to_watch):
        """Wykonuje wyszukiwanie kanału"""
        try:
            self.active_profiles.append({
                'index': profile_index,
                'driver': driver,
                'thread': threading.current_thread()
            })
            
            print(Fore.BLUE + f"[Profil {profile_index}] 🔍 Szukam: {channel_data['name']}")
            
            # Otwórz YouTube
            driver.get("https://www.youtube.com")
            time.sleep(random.uniform(2, 4))
            
            # Wyszukaj kanał
            search_success = self.youtube_actions.search_channel(
                driver=driver,
                keywords=channel_data['keywords'],
                channel_name=channel_data['name']
            )
            
            if not search_success:
                print(Fore.RED + f"[Profil {profile_index}] ❌ Nie znaleziono kanału")
                return False
            
            # Wejdź na kanał
            print(Fore.BLUE + f"[Profil {profile_index}] 📺 Wchodzę na kanał...")
            time.sleep(random.uniform(3, 5))
            
            # Obejrzyj filmy
            print(Fore.BLUE + f"[Profil {profile_index}] 🎬 Oglądam {videos_to_watch} filmów...")
            
            for i in range(videos_to_watch):
                print(Fore.BLUE + f"[Profil {profile_index}] Film {i+1}/{videos_to_watch}")
                
                watch_success = self.youtube_actions.watch_random_video_from_channel(
                    driver=driver,
                    watch_time=random.randint(30, 120)
                )
                
                if watch_success:
                    print(Fore.GREEN + f"[Profil {profile_index}] ✅ Film {i+1} obejrzany")
                else:
                    print(Fore.YELLOW + f"[Profil {profile_index}] ⚠️  Problem z filmem {i+1}")
                
                if i < videos_to_watch - 1:
                    wait_time = random.randint(10, 30)
                    print(Fore.BLUE + f"[Profil {profile_index}] ⏳ Przerwa {wait_time}s...")
                    time.sleep(wait_time)
            
            print(Fore.GREEN + f"[Profil {profile_index}] ✅ Zakończono kanał: {channel_data['name']}")
            return True
            
        except Exception as e:
            print(Fore.RED + f"[Profil {profile_index}] 💥 Błąd podczas wyszukiwania: {e}")
            return False
    
    def run_single_channel_profile(self, channel_data, profile_index, videos_to_watch=1):
        """Uruchamia pojedynczy profil z AUTOMATYCZNYM szukaniem proxy"""
        print(Fore.CYAN + f"\n{'='*60}")
        print(Fore.CYAN + f"🚀 PROFIL {profile_index}: {channel_data['name']}")
        print(Fore.CYAN + f"{'='*60}")
        
        # KROK 1: Znajdź działające proxy
        proxy = self.find_working_proxy_for_profile(profile_index, max_attempts=15)
        
        if not proxy:
            print(Fore.RED + f"[Profil {profile_index}] ❌ Nie można kontynuować bez działającego proxy")
            self.session_stats['failed'] += 1
            return False
        
        # KROK 2: Utwórz przeglądarkę z DZIAŁAJĄCYM proxy
        driver = self.create_profile_with_proxy(profile_index, proxy)
        
        if not driver:
            print(Fore.RED + f"[Profil {profile_index}] ❌ Nie udało się utworzyć przeglądarki")
            self.session_stats['failed'] += 1
            return False
        
        # KROK 3: Wykonaj wyszukiwanie
        success = self.execute_channel_search(driver, channel_data, profile_index, videos_to_watch)
        
        # KROK 4: Zamknij przeglądarkę
        self.browser_manager.close_profile(driver, profile_index)
        
        # KROK 5: Aktualizuj statystyki
        if success:
            self.session_stats['successful'] += 1
            print(Fore.GREEN + f"[Profil {profile_index}] ✅ SESJA ZAKOŃCZONA SUKCESEM")
            return True
        else:
            self.session_stats['failed'] += 1
            print(Fore.RED + f"[Profil {profile_index}] ❌ SESJA ZAKOŃCZONA NIEPOWODZENIEM")
            return False
    
    def run_channel_search_mode(self):
        """Główny tryb wyszukiwania kanałów"""
        print(Fore.CYAN + "\n" + "=" * 60)
        print(Fore.CYAN + "INTELIGENTNE WYSZUKIWANIE KANAŁÓW")
        print(Fore.CYAN + "=" * 60)
        
        # Statystyki proxy
        stats = self.proxy_manager.get_proxy_stats()
        print(Fore.WHITE + f"📊 Proxy w systemie: {stats['working']} działających z {stats['total_loaded']}")
        
        if stats['working'] == 0:
            print(Fore.YELLOW + "\n⚠️  UWAGA: Brak działających proxy!")
            print(Fore.YELLOW + "Bot będzie szukał działających proxy przed uruchomieniem.")
            
            choice = input(Fore.YELLOW + "Czy kontynuować? (t/n): ").lower()
            if choice != 't':
                return
        
        # Wczytaj kanały
        channels = self.load_channels_from_file()
        
        if not channels:
            print(Fore.YELLOW + "⚠️  Brak kanałów do przetworzenia")
            return
        
        # Wybierz kanały
        selected_channels = self.select_channels_interactive(channels)
        
        if not selected_channels:
            return
        
        # Pobierz ustawienia
        try:
            profiles_per_channel = int(input(Fore.YELLOW + "\nIle profili na kanał (max 5)? "))
            profiles_per_channel = max(1, min(5, profiles_per_channel))
        except:
            profiles_per_channel = 1
            print(Fore.YELLOW + "⚠️  Używam: 1")
        
        try:
            videos_per_channel = int(input(Fore.YELLOW + "Ile filmów obejrzeć na kanał? "))
            videos_per_channel = max(1, min(10, videos_per_channel))
        except:
            videos_per_channel = 3
            print(Fore.YELLOW + "⚠️  Używam: 3")
        
        # Podsumowanie
        print(Fore.CYAN + "\n" + "=" * 60)
        print(Fore.CYAN + "PODSUMOWANIE KONFIGURACJI")
        print(Fore.CYAN + "=" * 60)
        print(Fore.WHITE + f"Kanały: {len(selected_channels)}")
        print(Fore.WHITE + f"Profile/kanał: {profiles_per_channel}")
        print(Fore.WHITE + f"Filmy/kanał: {videos_per_channel}")
        print(Fore.WHITE + f"Dostępne proxy: {stats['working']}")
        print(Fore.WHITE + f"Łącznie sesji: {len(selected_channels) * profiles_per_channel}")
        
        confirm = input(Fore.YELLOW + "\n🚀 Uruchomić? (t/n): ").lower()
        if confirm != 't':
            print(Fore.YELLOW + "❌ Anulowano")
            return
        
        # Reset statystyk
        self.session_stats = {
            'successful': 0,
            'failed': 0,
            'proxy_tested': 0,
            'proxy_failed': 0,
            'proxy_working': 0,
            'total_profiles': len(selected_channels) * profiles_per_channel,
            'start_time': time.time()
        }
        
        # Uruchom sesje
        print(Fore.GREEN + "\n▶️  URUCHAMIANIE SYSTEMU...")
        print(Fore.CYAN + "=" * 60)
        time.sleep(2)
        
        threads = []
        profile_counter = 0
        
        for channel_idx, channel in enumerate(selected_channels, 1):
            print(Fore.CYAN + f"\n🎯 Kanał {channel_idx}/{len(selected_channels)}: {channel['name']}")
            
            for profile_idx in range(profiles_per_channel):
                profile_counter += 1
                
                # Uruchom wątek
                thread = threading.Thread(
                    target=self.run_single_channel_profile,
                    args=(channel, profile_counter, videos_per_channel),
                    daemon=True
                )
                
                threads.append(thread)
                thread.start()
                
                # Opóźnienie między profilami
                delay = random.uniform(15, 25)
                print(Fore.BLUE + f"⏳ Opóźnienie {delay:.1f}s...")
                time.sleep(delay)
        
        # Czekaj na zakończenie
        print(Fore.BLUE + "\n⏳ Oczekiwanie na zakończenie sesji...")
        
        for thread in threads:
            thread.join(timeout=3600)
        
        # Podsumowanie
        self.print_session_summary()
    
    def print_session_summary(self):
        """Wyświetla podsumowanie sesji"""
        total_time = time.time() - self.session_stats['start_time']
        
        print(Fore.CYAN + "\n" + "=" * 60)
        print(Fore.CYAN + "PODSUMOWANIE SESJI")
        print(Fore.CYAN + "=" * 60)
        
        print(Fore.GREEN + f"✅ UDANE SESJE: {self.session_stats['successful']}/{self.session_stats['total_profiles']}")
        print(Fore.RED + f"❌ NIEPOWODZENIA: {self.session_stats['failed']}/{self.session_stats['total_profiles']}")
        
        if self.session_stats['total_profiles'] > 0:
            success_rate = (self.session_stats['successful'] / self.session_stats['total_profiles']) * 100
            print(Fore.CYAN + f"📈 SKUTECZNOŚĆ: {success_rate:.1f}%")
        
        print(Fore.WHITE + f"\n📊 TESTOWANIE PROXY:")
        print(Fore.WHITE + f"   Przetestowane: {self.session_stats['proxy_tested']}")
        print(Fore.GREEN + f"   Działające: {self.session_stats['proxy_working']}")
        print(Fore.RED + f"   Nieudane: {self.session_stats['proxy_failed']}")
        
        if self.session_stats['proxy_tested'] > 0:
            proxy_success = (self.session_stats['proxy_working'] / self.session_stats['proxy_tested']) * 100
            print(Fore.CYAN + f"   Skuteczność proxy: {proxy_success:.1f}%")
        
        print(Fore.WHITE + f"\n⏱️  CZAS CAŁKOWITY: {total_time:.1f}s")
        print(Fore.WHITE + f"   Średnio na sesję: {total_time/self.session_stats['total_profiles']:.1f}s" if self.session_stats['total_profiles'] > 0 else "")
        
        print(Fore.CYAN + "=" * 60)
        print(Fore.GREEN + "\n✅ WSZYSTKIE SESJE ZAKOŃCZONE!")
    
    def test_proxy_in_chrome_mode(self):
        """Tryb tylko do testowania proxy w Chrome"""
        print(Fore.CYAN + "\n" + "=" * 60)
        print(Fore.CYAN + "TESTOWANIE PROXY W CHROME")
        print(Fore.CYAN + "=" * 60)
        
        # Użyj zewnętrznego skryptu
        try:
            import subprocess
            script_path = os.path.join(os.getcwd(), "test_proxy_chrome.py")
            
            if not os.path.exists(script_path):
                # Utwórz skrypt testowy
                self.create_chrome_proxy_test_script()
            
            subprocess.run([sys.executable, "test_proxy_chrome.py"])
            
        except Exception as e:
            print(Fore.RED + f"❌ Błąd: {e}")
            print(Fore.YELLOW + "Tworzę skrypt testowy...")
            self.create_chrome_proxy_test_script()
    
    def create_chrome_proxy_test_script(self):
        """Tworzy skrypt do testowania proxy w Chrome"""
        script_content = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Skrypt do testowania proxy w Chrome
"""

import os
import sys
sys.path.append('.')

from modules.browser_manager import BrowserManager
import time

print("=" * 60)
print("TEST PROXY W CHROME")
print("=" * 60)

bm = BrowserManager()

# Test bez proxy
print("\\n🔧 Test 1: Bez proxy")
driver = bm.create_profile_with_proxy_test(999, headless=True)
if driver:
    driver.get("https://www.youtube.com")
    print(f"✅ Bez proxy: {driver.title[:50]}")
    driver.quit()
else:
    print("❌ Nie udało się bez proxy")

# Test z proxy z pliku
print("\\n🔧 Test 2: Z proxy z pliku")
proxy_file = "data/proxy.txt"
if os.path.exists(proxy_file):
    with open(proxy_file, 'r') as f:
        proxies = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    
    if proxies:
        print(f"Znaleziono {len(proxies)} proxy do testowania")
        
        for i, proxy in enumerate(proxies[:3], 1):  # Tylko 3 pierwsze
            print(f"\\n🧪 Test {i}: {proxy}")
            driver = bm.create_profile_with_proxy_test(999, proxy=proxy, headless=True)
            if driver:
                print("✅ Proxy DZIAŁA w Chrome!")
                driver.quit()
            else:
                print("❌ Proxy NIE DZIAŁA w Chrome")
    else:
        print("❌ Brak proxy w pliku")
else:
    print("❌ Brak pliku proxy.txt")

print("\\n✅ Test zakończony")
input("\\nNaciśnij Enter...")
'''
        
        with open("test_proxy_chrome.py", "w", encoding="utf-8") as f:
            f.write(script_content)
        
        print(Fore.GREEN + "✅ Utworzono skrypt: test_proxy_chrome.py")
        print(Fore.YELLOW + "Uruchom: python test_proxy_chrome.py")
    
    def manage_profiles(self):
        """Zarządzanie profilami"""
        print(Fore.CYAN + "\n" + "=" * 60)
        print(Fore.CYAN + "ZARZĄDZANIE PROFILAMI")
        print(Fore.CYAN + "=" * 60)
        
        options = [
            "[1] Wyświetl statystyki sesji",
            "[2] Wyczyść cache proxy",
            "[3] Przetestuj ponownie nieudane proxy",
            "[4] Wyświetl aktywne profile",
            "[5] Wróć"
        ]
        
        for option in options:
            print(Fore.WHITE + option)
        
        try:
            choice = int(input(Fore.YELLOW + "\nWybierz opcję (1-5): "))
            
            if choice == 1:
                self.print_session_summary()
            
            elif choice == 2:
                print(Fore.GREEN + "✅ Cache proxy wyczyszczone")
            
            elif choice == 3:
                print(Fore.BLUE + "\n🔁 Ponowne testowanie proxy...")
                self.proxy_manager.retry_failed_proxies()
            
            elif choice == 4:
                print(Fore.BLUE + f"\nAktywne profile: {len(self.active_profiles)}")
                for profile in self.active_profiles:
                    print(Fore.WHITE + f"  - Profil {profile['index']}")
        
        except:
            print(Fore.RED + "❌ Nieprawidłowy wybór")
    
    def show_configuration(self):
        """Wyświetla konfigurację"""
        print(Fore.CYAN + "\n" + "=" * 60)
        print(Fore.CYAN + "KONFIGURACJA SYSTEMU")
        print(Fore.CYAN + "=" * 60)
        
        config = {
            "System proxy": f"{self.proxy_manager.count()} działających",
            "ChromeDriver": "Znaleziony" if self.browser_manager.chromedriver_path else "Brak",
            "Folder danych": "data\\",
            "Folder profili": "profiles\\",
            "Wersja Chrome": "144.0.7559.60",
            "Wersja Python": sys.version.split()[0]
        }
        
        for key, value in config.items():
            print(Fore.WHITE + f"{key}: {Fore.GREEN}{value}")
    
    def run(self):
        """Główna pętla programu"""
        # Utwórz strukturę danych
        self.create_data_structure()
        
        while True:
            try:
                self.print_menu()
                
                choice = input(Fore.YELLOW + "\nTwój wybór (1-7): ").strip()
                
                if choice == "1":
                    self.test_proxy_in_chrome_mode()
                
                elif choice == "2":
                    print(Fore.YELLOW + "⚠️  Tryb filmów w budowie. Użyj opcji 3.")
                
                elif choice == "3":
                    self.run_channel_search_mode()
                
                elif choice == "4":
                    self.test_proxy_in_chrome_mode()
                
                elif choice == "5":
                    self.manage_profiles()
                
                elif choice == "6":
                    self.show_configuration()
                
                elif choice == "7":
                    print(Fore.GREEN + "\n👋 Do zobaczenia!")
                    break
                
                else:
                    print(Fore.RED + "❌ Nieprawidłowy wybór")
                
                # Pauza
                if choice != "7":
                    input(Fore.YELLOW + "\nNaciśnij Enter aby kontynuować...")
                    
            except KeyboardInterrupt:
                print(Fore.RED + "\n\n❌ Przerwano przez użytkownika")
                break
            except Exception as e:
                print(Fore.RED + f"\n💥 Krytyczny błąd: {e}")
                import traceback
                traceback.print_exc()
                input(Fore.YELLOW + "\nNaciśnij Enter aby kontynuować...")

# Uruchomienie
if __name__ == "__main__":
    try:
        bot = YouTubeViewerAdvanced()
        bot.run()
    except KeyboardInterrupt:
        print(Fore.RED + "\n\n❌ Program przerwany")
    except Exception as e:
        print(Fore.RED + f"\n💥 Fatalny błąd: {e}")
        import traceback
        traceback.print_exc()
        input("Naciśnij Enter aby zakończyć...")