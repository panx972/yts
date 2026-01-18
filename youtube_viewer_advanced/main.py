"""
ADVANCED YOUTUBE VIEWER v3.0
Ulepszona wersja z Selenium, fingerprintingiem i zarządzaniem profilami
Dodano: Wyszukiwanie kanałów z pliku + weryfikacja URL
POPRAWIONA WERSJA - naprawione błędy z kanałami
"""

import os
import sys
import time
import json
import random
import threading
from datetime import datetime
from colorama import init, Fore, Style

init(autoreset=True)

# Import modułów
try:
    from modules.proxy_manager import ProxyManager
    from modules.browser_manager import BrowserManager
    from modules.youtube_actions import YouTubeActions
    from modules.channel_verifier import ChannelVerifier
except ImportError as e:
    print(f"{Fore.RED}❌ Błąd importu modułów: {e}{Fore.RESET}")
    print(f"{Fore.YELLOW}Sprawdź czy pliki istnieją w folderze modules/{Fore.RESET}")
    
    # Próba bezpośredniego importu
    sys.path.append(os.path.dirname(__file__))
    try:
        from modules.proxy_manager import ProxyManager
        from modules.browser_manager import BrowserManager
        from modules.youtube_actions import YouTubeActions
        from modules.channel_verifier import ChannelVerifier
        print(f"{Fore.GREEN}✅ Moduły zaimportowane przez sys.path{Fore.RESET}")
    except ImportError as e2:
        print(f"{Fore.RED}❌ Krytyczny błąd importu: {e2}{Fore.RESET}")
        sys.exit(1)

class YouTubeViewerAdvanced:
    def __init__(self):
        self.config = self.load_config()
        self.proxy_manager = ProxyManager()
        self.browser_manager = BrowserManager()
        self.youtube_actions = YouTubeActions()
        self.channel_verifier = ChannelVerifier()
        
        # Statystyki
        self.stats = {
            'start_time': None,
            'total_views': 0,
            'successful_views': 0,
            'failed_views': 0,
            'active_profiles': 0,
            'channels_found': 0,
            'channels_failed': 0
        }
    
    def load_config(self):
        """Ładuje konfigurację z pliku"""
        config_path = os.path.join('data', 'config.json')
        default_config = {
            'max_profiles': 10,
            'view_duration_min': 30,
            'view_duration_max': 180,
            'use_fingerprinting': True,
            'use_proxy_rotation': True,
            'headless_mode': False,
            'threads': 5,
            'test_proxy_timeout': 15,
            'max_proxies_to_fetch': 1000
        }
        
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    user_config = json.load(f)
                    return {**default_config, **user_config}
            except Exception as e:
                print(f"{Fore.YELLOW}⚠️  Błąd wczytania config.json: {e}, używam domyślnych ustawień{Fore.RESET}")
                return default_config
        else:
            # Utwórz domyślną konfigurację
            os.makedirs('data', exist_ok=True)
            with open(config_path, 'w') as f:
                json.dump(default_config, f, indent=2)
            print(f"{Fore.GREEN}✅ Utworzono domyślną konfigurację{Fore.RESET}")
            return default_config
    
    def print_banner(self):
        """Wyświetla banner programu"""
        banner = f"""
{Fore.GREEN}
╔══════════════════════════════════════════════════════════╗
║         ADVANCED YOUTUBE VIEWER v3.0                     ║
║         Selenium + Fingerprinting + Proxy System         ║
║         + Channel Search with URL Verification           ║
╚══════════════════════════════════════════════════════════╝
{Fore.RESET}
        """
        print(banner)
    
    def print_menu(self):
        """Wyświetla menu programu"""
        menu = f"""
{Fore.CYAN}Wybierz opcję:{Fore.RESET}

{Fore.YELLOW}[1]{Fore.RESET} Pobierz i przetestuj proxy
{Fore.YELLOW}[2]{Fore.RESET} Uruchom bota (z listy filmów)
{Fore.YELLOW}[3]{Fore.RESET} Wyszukaj kanały z pliku (Z WERYFIKACJĄ)
{Fore.YELLOW}[4]{Fore.RESET} Tylko testuj proxy
{Fore.YELLOW}[5]{Fore.RESET} Zarządzaj profilami
{Fore.YELLOW}[6]{Fore.RESET} Konfiguracja
{Fore.YELLOW}[7]{Fore.RESET} Wyjście
        """
        print(menu)
    
    def option_1_fetch_proxies(self):
        """Opcja 1: Pobierz i przetestuj proxy"""
        print(f"\n{Fore.CYAN}🔄 Pobieranie i testowanie proxy...{Fore.RESET}")
        
        # Pobierz proxy
        proxies = self.proxy_manager.fetch_proxies(
            max_proxies=self.config.get('max_proxies_to_fetch', 1000)
        )
        
        if not proxies:
            print(f"{Fore.RED}❌ Nie pobrano żadnych proxy.{Fore.RESET}")
            return
        
        print(f"{Fore.GREEN}✅ Pobrano {len(proxies)} proxy{Fore.RESET}")
        
        # Zapytaj o testowanie
        test = input(f"{Fore.YELLOW}Przetestować proxy? (T/N): {Fore.RESET}").strip().lower()
        if test != 't':
            self.proxy_manager.save_proxies(proxies, 'data/proxy.txt')
            print(f"{Fore.GREEN}💾 Zapisano proxy do data/proxy.txt{Fore.RESET}")
            return
        
        # Testuj proxy
        print(f"{Fore.CYAN}🧪 Testuję proxy...{Fore.RESET}")
        good_proxies = self.proxy_manager.test_proxies_simple(
            proxies,
            max_workers=self.config.get('threads', 5),
            timeout=self.config.get('test_proxy_timeout', 15)
        )
        
        if good_proxies:
            self.proxy_manager.save_good_proxies(good_proxies, 'data/good_proxy.txt')
            print(f"{Fore.GREEN}✅ Znaleziono {len(good_proxies)} działających proxy{Fore.RESET}")
        else:
            print(f"{Fore.RED}❌ Nie znaleziono działających proxy{Fore.RESET}")
    
    def option_2_run_bot(self):
        """Opcja 2: Uruchom bota YouTube z listy filmów"""
        print(f"\n{Fore.CYAN}🎬 Uruchamianie bota (lista filmów)...{Fore.RESET}")
        
        # Sprawdź czy mamy dobre proxy
        good_proxies = self.proxy_manager.load_good_proxies('data/good_proxy.txt')
        if not good_proxies and self.config['use_proxy_rotation']:
            choice = input(f"{Fore.YELLOW}⚠️ Brak działających proxy. Kontynuować bez proxy? (T/N): {Fore.RESET}").strip().lower()
            if choice != 't':
                return
        
        # Pobierz listę filmów do obejrzenia
        video_list = self.get_video_list()
        if not video_list:
            print(f"{Fore.RED}❌ Brak filmów do obejrzenia.{Fore.RESET}")
            return
        
        print(f"{Fore.GREEN}✅ Znaleziono {len(video_list)} filmów{Fore.RESET}")
        
        # Ustawienia sesji
        num_profiles = self.get_int_input(
            f"Ile profili uruchomić (max {self.config['max_profiles']})? ",
            1, self.config['max_profiles']
        )
        
        views_per_profile = self.get_int_input(
            "Ile wyświetleń na profil? ",
            1, 50
        )
        
        print(f"\n{Fore.GREEN}▶️  Uruchamiam {num_profiles} profili...{Fore.RESET}")
        print(f"{Fore.CYAN}📊 Każdy profil obejrzy {views_per_profile} filmów{Fore.RESET}")
        
        # Uruchom profile
        self.stats['start_time'] = datetime.now()
        self.run_profiles_parallel(
            num_profiles, 
            video_list, 
            views_per_profile, 
            good_proxies
        )
        
        # Podsumowanie
        self.print_stats_summary()
    
    def get_video_list(self):
        """Pobiera listę filmów z pliku lub od użytkownika"""
        videos_file = 'data/videos.txt'
        videos = []
        
        if os.path.exists(videos_file):
            try:
                with open(videos_file, 'r', encoding='utf-8') as f:
                    videos = [line.strip() for line in f if line.strip()]
            except Exception as e:
                print(f"{Fore.YELLOW}⚠️  Błąd odczytu pliku videos.txt: {e}{Fore.RESET}")
        
        if not videos:
            print(f"{Fore.YELLOW}📝 Wpisz linki do filmów YouTube (jeden na linię, pusty wiersz aby zakończyć):{Fore.RESET}")
            while True:
                try:
                    url = input().strip()
                    if not url:
                        break
                    if 'youtube.com' in url or 'youtu.be' in url:
                        videos.append(url)
                        print(f"{Fore.GREEN}✅ Dodano: {url[:50]}...{Fore.RESET}")
                    else:
                        print(f"{Fore.YELLOW}⚠️  To nie wygląda na link YouTube. Spróbuj ponownie.{Fore.RESET}")
                except EOFError:
                    break
        
        return videos
    
    def get_int_input(self, prompt, min_val, max_val):
        """Pobiera liczbę całkowitą od użytkownika"""
        while True:
            try:
                value = input(f"{Fore.YELLOW}{prompt}{Fore.RESET}")
                if not value:
                    return min_val
                value = int(value)
                if min_val <= value <= max_val:
                    return value
                print(f"{Fore.RED}❌ Wartość musi być między {min_val} a {max_val}{Fore.RESET}")
            except ValueError:
                print(f"{Fore.RED}❌ To nie jest prawidłowa liczba.{Fore.RESET}")
    
    def run_profiles_parallel(self, num_profiles, video_list, views_per_profile, good_proxies):
        """Uruchamia profile równolegle"""
        threads = []
        
        for i in range(num_profiles):
            # Wybierz proxy dla tego profilu
            proxy = None
            if good_proxies and self.config['use_proxy_rotation']:
                proxy = random.choice(good_proxies)
            
            # Utwórz i uruchom wątek
            thread = threading.Thread(
                target=self.run_single_profile,
                args=(i, video_list, views_per_profile, proxy),
                daemon=True
            )
            threads.append(thread)
            thread.start()
            time.sleep(random.uniform(1, 3))  # Opóźnienie między uruchomieniami
        
        # Poczekaj na zakończenie wszystkich wątków
        for thread in threads:
            thread.join(timeout=1800)  # 30 minut timeout
    
    def run_single_profile(self, profile_id, video_list, views_per_profile, proxy=None):
        """Uruchamia pojedynczy profil"""
        profile_name = f"profile_{profile_id}"
        
        try:
            print(f"{Fore.CYAN}[Profil {profile_id}] 🟡 Uruchamianie...{Fore.RESET}")
            
            # Utwórz profil przeglądarki
            driver = self.browser_manager.create_profile(
                profile_name=profile_name,
                proxy=proxy,
                use_fingerprinting=self.config['use_fingerprinting'],
                headless=self.config['headless_mode']
            )
            
            if not driver:
                print(f"{Fore.RED}[Profil {profile_id}] ❌ Nie udało się utworzyć profilu{Fore.RESET}")
                self.stats['failed_views'] += views_per_profile
                return
            
            self.stats['active_profiles'] += 1
            
            # Wykonaj wyświetlenia
            for view_num in range(views_per_profile):
                if view_num >= len(video_list):
                    video_url = random.choice(video_list)
                else:
                    video_url = video_list[view_num]
                
                print(f"{Fore.CYAN}[Profil {profile_id}] 📺 Wyświetlenie {view_num+1}/{views_per_profile}{Fore.RESET}")
                
                success = self.youtube_actions.watch_video(
                    driver=driver,
                    video_url=video_url,
                    min_duration=self.config['view_duration_min'],
                    max_duration=self.config['view_duration_max']
                )
                
                if success:
                    self.stats['successful_views'] += 1
                    print(f"{Fore.GREEN}[Profil {profile_id}] ✅ Sukces{Fore.RESET}")
                else:
                    self.stats['failed_views'] += 1
                    print(f"{Fore.RED}[Profil {profile_id}] ❌ Niepowodzenie{Fore.RESET}")
                
                self.stats['total_views'] += 1
                
                # Losowa przerwa między filmami
                if view_num < views_per_profile - 1:
                    wait_time = random.uniform(10, 30)
                    print(f"{Fore.CYAN}[Profil {profile_id}] ⏸️  Przerwa {wait_time:.1f}s...{Fore.RESET}")
                    time.sleep(wait_time)
            
            # Zamknij przeglądarkę
            try:
                driver.quit()
            except:
                pass
            
            self.stats['active_profiles'] -= 1
            print(f"{Fore.GREEN}[Profil {profile_id}] 🏁 Zakończono{Fore.RESET}")
            
        except Exception as e:
            print(f"{Fore.RED}[Profil {profile_id}] 💥 Błąd: {e}{Fore.RESET}")
            self.stats['failed_views'] += views_per_profile
    
    def option_3_search_channels_from_file(self):
        """Opcja 3: Wyszukaj kanały z pliku yt_channels.txt - POPRAWIONA"""
        print(f"\n{Fore.CYAN}📁 Wczytywanie kanałów z pliku...{Fore.RESET}")
        
        # Użyj channel_verifier do załadowania kanałów
        channels = self.channel_verifier.load_channels_from_file('data/yt_channels.txt')
        
        if not channels:
            print(f"{Fore.RED}❌ Brak kanałów w pliku yt_channels.txt lub błąd formatu{Fore.RESET}")
            print(f"{Fore.YELLOW}💡 Sprawdź format pliku:{Fore.RESET}")
            print(f"{Fore.YELLOW}   Przykład: https://www.youtube.com/@jbeegames|Jbee Games|jbee{Fore.RESET}")
            
            # Sprawdź co jest w pliku
            try:
                with open('data/yt_channels.txt', 'r', encoding='utf-8') as f:
                    content = f.read()
                    print(f"\n{Fore.YELLOW}Aktualna zawartość pliku:{Fore.RESET}")
                    print(content)
            except:
                pass
            return
        
        print(f"{Fore.GREEN}✅ Załadowano {len(channels)} kanałów{Fore.RESET}")
        
        # Wyświetl listę kanałów
        print(f"\n{Fore.CYAN}📋 Znalezione kanały:{Fore.RESET}")
        for i, channel in enumerate(channels, 1):
            print(f"  {i}. {channel.get('name', 'BRAK NAZWY')} -> {channel.get('url', 'BRAK URL')}")
        
        # Wybór kanałów
        choice = input(f"\n{Fore.YELLOW}Wybierz kanały (np. 1,3,5 lub 'all'): {Fore.RESET}").strip().lower()
        
        if choice == 'all':
            selected_channels = channels
        else:
            selected_channels = []
            try:
                indices = [int(idx.strip()) - 1 for idx in choice.split(',') if idx.strip().isdigit()]
                for idx in indices:
                    if 0 <= idx < len(channels):
                        selected_channels.append(channels[idx])
            except Exception as e:
                print(f"{Fore.RED}❌ Nieprawidłowy wybór: {e}{Fore.RESET}")
                return
        
        if not selected_channels:
            print(f"{Fore.RED}❌ Nie wybrano żadnych kanałów{Fore.RESET}")
            return
        
        print(f"{Fore.GREEN}✅ Wybrano {len(selected_channels)} kanałów{Fore.RESET}")
        
        # Sprawdź proxy
        good_proxies = self.proxy_manager.load_good_proxies('data/good_proxy.txt')
        if not good_proxies and self.config['use_proxy_rotation']:
            choice = input(f"{Fore.YELLOW}⚠️ Brak działających proxy. Kontynuować bez proxy? (T/N): {Fore.RESET}").strip().lower()
            if choice != 't':
                return
        
        # Ustawienia
        num_profiles = self.get_int_input(
            f"Ile profili na kanał (max {self.config['max_profiles']})? ",
            1, self.config['max_profiles']
        )
        
        videos_per_channel = self.get_int_input(
            "Ile filmów obejrzeć na kanał? ",
            1, 10
        )
        
        # Reset statystyk
        self.stats = {
            'start_time': datetime.now(),
            'total_views': 0,
            'successful_views': 0,
            'failed_views': 0,
            'active_profiles': 0,
            'channels_found': 0,
            'channels_failed': 0
        }
        
        # Uruchom dla każdego kanału
        for channel_idx, channel_data in enumerate(selected_channels, 1):
            print(f"\n{Fore.GREEN}▶️  Kanał {channel_idx}/{len(selected_channels)}: {channel_data.get('name', 'Nieznany')}{Fore.RESET}")
            
            # DEBUG: Sprawdź dane kanału
            print(f"{Fore.CYAN}[DEBUG] Typ channel_data: {type(channel_data)}{Fore.RESET}")
            if isinstance(channel_data, dict):
                print(f"{Fore.CYAN}[DEBUG] Klucze: {list(channel_data.keys())}{Fore.RESET}")
            
            self.run_channel_profiles(
                channel_data=channel_data,
                num_profiles=num_profiles,
                videos_per_channel=videos_per_channel,
                good_proxies=good_proxies
            )
        
        # Podsumowanie
        self.print_stats_summary()
    
    def run_channel_profiles(self, channel_data, num_profiles, videos_per_channel, good_proxies):
        """Uruchamia profile dla konkretnego kanału"""
        threads = []
        
        for i in range(num_profiles):
            # Wybierz proxy
            proxy = None
            if good_proxies and self.config['use_proxy_rotation']:
                proxy = random.choice(good_proxies)
            
            # Uruchom wątek
            thread = threading.Thread(
                target=self.run_single_channel_profile,
                args=(i, channel_data, videos_per_channel, proxy),
                daemon=True
            )
            threads.append(thread)
            thread.start()
            time.sleep(random.uniform(5, 10))  # Dłuższe opóźnienie między profilami
        
        # Czekaj na zakończenie
        for thread in threads:
            thread.join(timeout=1800)  # 30 minut timeout
    
    def run_single_channel_profile(self, profile_id, channel_data, videos_to_watch, proxy=None):
        """Uruchamia pojedynczy profil dla kanału - POPRAWIONA"""
        try:
            # DEBUG: Sprawdź co dostajemy
            print(f"{Fore.MAGENTA}[DEBUG Profil {profile_id}] channel_data = {channel_data}{Fore.RESET}")
            print(f"{Fore.MAGENTA}[DEBUG Profil {profile_id}] type = {type(channel_data)}{Fore.RESET}")
            
            # Upewnij się że channel_data jest słownikiem
            if isinstance(channel_data, dict):
                # Pobierz dane ze słownika
                channel_name = channel_data.get('name', f'Channel_{profile_id}')
                channel_url = channel_data.get('url', '')
                search_keywords = channel_data.get('keywords', channel_name)
                
                print(f"{Fore.CYAN}[DEBUG] Pobrano z dict: name='{channel_name}', url='{channel_url}'{Fore.RESET}")
            elif isinstance(channel_data, str):
                # Jeśli to string, spróbuj podzielić
                print(f"{Fore.YELLOW}[DEBUG] channel_data to string: {channel_data}{Fore.RESET}")
                if '|' in channel_data:
                    parts = channel_data.split('|')
                    if len(parts) >= 2:
                        channel_url = parts[0].strip()
                        channel_name = parts[1].strip()
                        search_keywords = parts[2].strip() if len(parts) > 2 else channel_name
                        print(f"{Fore.CYAN}[DEBUG] Rozpoznano z stringa: name='{channel_name}'{Fore.RESET}")
                    else:
                        channel_name = channel_data
                        channel_url = ''
                        search_keywords = channel_name
                else:
                    channel_name = channel_data
                    channel_url = ''
                    search_keywords = channel_name
            else:
                # Domyślne wartości
                print(f"{Fore.RED}[DEBUG] Nieznany typ channel_data: {type(channel_data)}{Fore.RESET}")
                channel_name = f'Channel_{profile_id}'
                channel_url = ''
                search_keywords = channel_name
            
            # Utwórz nazwę profilu (bez znaków specjalnych)
            safe_name = channel_name.replace(' ', '_').replace('.', '_').replace('@', '').replace('/', '_')
            profile_name = f"channel_{safe_name}_{profile_id}"
            
            print(f"{Fore.CYAN}[Profil {profile_id}] 🟡 Szukam: {channel_name}{Fore.RESET}")
            
            # Utwórz profil przeglądarki
            driver = self.browser_manager.create_profile(
                profile_name=profile_name,
                proxy=proxy,
                use_fingerprinting=self.config['use_fingerprinting'],
                headless=self.config['headless_mode']
            )
            
            if not driver:
                print(f"{Fore.RED}[Profil {profile_id}] ❌ Nie udało się utworzyć profilu{Fore.RESET}")
                self.stats['failed_views'] += videos_to_watch
                return
            
            self.stats['active_profiles'] += 1
            
            # Wyszukaj i weryfikuj kanał
            result = self.youtube_actions.search_and_verify_channel(
                driver=driver,
                channel_url=channel_url,
                channel_name=search_keywords,
                videos_to_watch=videos_to_watch
            )
            
            if result.get('channel_found', False):
                self.stats['channels_found'] += 1
            else:
                self.stats['channels_failed'] += 1
            
            if result.get('success', False):
                self.stats['successful_views'] += result.get('videos_watched', 0)
                print(f"{Fore.GREEN}[Profil {profile_id}] ✅ Sukces - {result.get('videos_watched', 0)} filmów{Fore.RESET}")
            else:
                self.stats['failed_views'] += videos_to_watch
                error_msg = result.get('error', 'Nieznany błąd')[:100]
                print(f"{Fore.RED}[Profil {profile_id}] ❌ Niepowodzenie: {error_msg}{Fore.RESET}")
            
            self.stats['total_views'] += result.get('videos_watched', 0)
            
            # Zamknij przeglądarkę
            try:
                driver.quit()
            except:
                pass
            
            self.stats['active_profiles'] -= 1
            print(f"{Fore.GREEN}[Profil {profile_id}] 🏁 Zakończono{Fore.RESET}")
            
        except Exception as e:
            print(f"{Fore.RED}[Profil {profile_id}] 💥 Błąd: {str(e)[:200]}{Fore.RESET}")
            import traceback
            traceback.print_exc()
            self.stats['failed_views'] += videos_to_watch
    
    def option_4_test_proxies(self):
        """Opcja 4: Tylko testuj proxy"""
        print(f"\n{Fore.CYAN}🧪 Testowanie proxy...{Fore.RESET}")
        
        # Załaduj proxy z pliku
        proxies = self.proxy_manager.load_proxies('data/proxy.txt')
        if not proxies:
            print(f"{Fore.RED}❌ Brak proxy do przetestowania.{Fore.RESET}")
            return
        
        print(f"{Fore.GREEN}✅ Wczytano {len(proxies)} proxy{Fore.RESET}")
        
        # Testuj
        good_proxies = self.proxy_manager.test_proxies_simple(
            proxies,
            max_workers=self.config.get('threads', 5),
            timeout=self.config.get('test_proxy_timeout', 15)
        )
        
        if good_proxies:
            self.proxy_manager.save_good_proxies(good_proxies, 'data/good_proxy.txt')
            print(f"{Fore.GREEN}✅ Znaleziono {len(good_proxies)} działających proxy{Fore.RESET}")
        else:
            print(f"{Fore.RED}❌ Nie znaleziono działających proxy{Fore.RESET}")
    
    def option_5_manage_profiles(self):
        """Opcja 5: Zarządzaj profilami"""
        print(f"\n{Fore.CYAN}👤 Zarządzanie profilami...{Fore.RESET}")
        
        profiles_dir = 'profiles'
        if os.path.exists(profiles_dir):
            profiles = [d for d in os.listdir(profiles_dir) 
                       if os.path.isdir(os.path.join(profiles_dir, d))]
            
            if profiles:
                print(f"{Fore.YELLOW}Znalezione profile:{Fore.RESET}")
                for i, profile in enumerate(profiles, 1):
                    size = self.get_folder_size(os.path.join(profiles_dir, profile))
                    print(f"  {i}. {profile} ({size})")
                
                print(f"\n{Fore.YELLOW}Opcje:{Fore.RESET}")
                print(f"  1. Usuń wybrane profile")
                print(f"  2. Usuń wszystkie profile")
                print(f"  3. Wróć")
                
                choice = input(f"{Fore.YELLOW}Wybierz opcję: {Fore.RESET}").strip()
                
                if choice == '1':
                    to_delete = input(f"{Fore.YELLOW}Podaj numery profili do usunięcia (np. 1,3,5): {Fore.RESET}").strip()
                    self.delete_profiles(profiles, to_delete)
                elif choice == '2':
                    confirm = input(f"{Fore.RED}⚠️  Czy na pewno usunąć WSZYSTKIE profile? (T/N): {Fore.RESET}").strip().lower()
                    if confirm == 't':
                        self.delete_all_profiles(profiles_dir, profiles)
                else:
                    print(f"{Fore.YELLOW}↩️  Powrót do menu{Fore.RESET}")
            else:
                print(f"{Fore.YELLOW}📭 Brak zapisanych profili.{Fore.RESET}")
        else:
            print(f"{Fore.YELLOW}📭 Brak folderu profili.{Fore.RESET}")
    
    def get_folder_size(self, folder):
        """Oblicza rozmiar folderu"""
        total = 0
        try:
            for dirpath, dirnames, filenames in os.walk(folder):
                for f in filenames:
                    fp = os.path.join(dirpath, f)
                    if os.path.exists(fp):
                        total += os.path.getsize(fp)
        except Exception as e:
            return f"błąd: {str(e)[:20]}"
        
        if total < 1024:
            return f"{total} B"
        elif total < 1024 * 1024:
            return f"{total/1024:.1f} KB"
        else:
            return f"{total/(1024*1024):.1f} MB"
    
    def delete_profiles(self, profiles, to_delete):
        """Usuwa wybrane profile"""
        try:
            indices = [int(i.strip()) - 1 for i in to_delete.split(',') if i.strip().isdigit()]
            deleted_count = 0
            
            for idx in indices:
                if 0 <= idx < len(profiles):
                    profile_path = os.path.join('profiles', profiles[idx])
                    try:
                        import shutil
                        shutil.rmtree(profile_path, ignore_errors=True)
                        print(f"{Fore.GREEN}✅ Usunięto: {profiles[idx]}{Fore.RESET}")
                        deleted_count += 1
                    except Exception as e:
                        print(f"{Fore.RED}❌ Błąd przy usuwaniu {profiles[idx]}: {e}{Fore.RESET}")
            
            print(f"{Fore.GREEN}🗑️  Usunięto {deleted_count} profili{Fore.RESET}")
            
        except Exception as e:
            print(f"{Fore.RED}❌ Błąd: {e}{Fore.RESET}")
    
    def delete_all_profiles(self, profiles_dir, profiles):
        """Usuwa wszystkie profile"""
        import shutil
        try:
            shutil.rmtree(profiles_dir, ignore_errors=True)
            os.makedirs(profiles_dir, exist_ok=True)
            print(f"{Fore.GREEN}✅ Usunięto wszystkie profile ({len(profiles)}){Fore.RESET}")
        except Exception as e:
            print(f"{Fore.RED}❌ Błąd przy usuwaniu: {e}{Fore.RESET}")
    
    def option_6_configuration(self):
        """Opcja 6: Konfiguracja programu"""
        print(f"\n{Fore.CYAN}⚙️  Konfiguracja programu{Fore.RESET}")
        
        config_path = os.path.join('data', 'config.json')
        
        # Wyświetl bieżącą konfigurację
        print(f"{Fore.YELLOW}Bieżąca konfiguracja:{Fore.RESET}")
        for key, value in self.config.items():
            print(f"  {Fore.CYAN}{key}: {Fore.WHITE}{value}{Fore.RESET}")
        
        # Zapytaj o zmianę
        change = input(f"\n{Fore.YELLOW}Czy chcesz zmienić konfigurację? (T/N): {Fore.RESET}").strip().lower()
        if change != 't':
            return
        
        # Nowa konfiguracja
        new_config = self.config.copy()
        
        print(f"\n{Fore.YELLOW}Wprowadź nowe wartości (Enter aby zachować obecną):{Fore.RESET}")
        
        for key in new_config.keys():
            current = new_config[key]
            
            if isinstance(current, bool):
                response = input(f"{key} (T/N) [{'T' if current else 'N'}]: ").strip().lower()
                if response == 't':
                    new_config[key] = True
                elif response == 'n':
                    new_config[key] = False
            elif isinstance(current, int):
                try:
                    response = input(f"{key} [{current}]: ").strip()
                    if response:
                        new_config[key] = int(response)
                except:
                    pass
            elif isinstance(current, str):
                response = input(f"{key} [{current}]: ").strip()
                if response:
                    new_config[key] = response
        
        # Zapisz konfigurację
        with open(config_path, 'w') as f:
            json.dump(new_config, f, indent=2)
        
        print(f"{Fore.GREEN}✅ Konfiguracja zapisana{Fore.RESET}")
        self.config = new_config
    
    def print_stats_summary(self):
        """Wyświetla podsumowanie statystyk"""
        if not self.stats['start_time']:
            return
        
        elapsed = datetime.now() - self.stats['start_time']
        
        print(f"\n{Fore.GREEN}{'='*60}{Fore.RESET}")
        print(f"{Fore.CYAN}📊 PODSUMOWANIE:{Fore.RESET}")
        print(f"{Fore.YELLOW}   Czas trwania: {elapsed}{Fore.RESET}")
        print(f"{Fore.YELLOW}   Łączne wyświetlenia: {self.stats['total_views']}{Fore.RESET}")
        print(f"{Fore.GREEN}   Udane wyświetlenia: {self.stats['successful_views']}{Fore.RESET}")
        print(f"{Fore.RED}   Nieudane wyświetlenia: {self.stats['failed_views']}{Fore.RESET}")
        print(f"{Fore.CYAN}   Znalezione kanały: {self.stats['channels_found']}{Fore.RESET}")
        print(f"{Fore.RED}   Nieznalezione kanały: {self.stats['channels_failed']}{Fore.RESET}")
        
        if self.stats['total_views'] > 0:
            success_rate = (self.stats['successful_views'] / self.stats['total_views']) * 100
            print(f"{Fore.CYAN}   Skuteczność wyświetleń: {success_rate:.1f}%{Fore.RESET}")
        
        if self.stats['channels_found'] + self.stats['channels_failed'] > 0:
            channel_success = (self.stats['channels_found'] / (self.stats['channels_found'] + self.stats['channels_failed'])) * 100
            print(f"{Fore.CYAN}   Skuteczność kanałów: {channel_success:.1f}%{Fore.RESET}")
        
        print(f"{Fore.GREEN}{'='*60}{Fore.RESET}")
    
    def main(self):
        """Główna pętla programu"""
        self.print_banner()
        
        while True:
            try:
                self.print_menu()
                choice = input(f"\n{Fore.YELLOW}Twój wybór (1-7): {Fore.RESET}").strip()
                
                if choice == '1':
                    self.option_1_fetch_proxies()
                elif choice == '2':
                    self.option_2_run_bot()
                elif choice == '3':
                    self.option_3_search_channels_from_file()
                elif choice == '4':
                    self.option_4_test_proxies()
                elif choice == '5':
                    self.option_5_manage_profiles()
                elif choice == '6':
                    self.option_6_configuration()
                elif choice in ['7', 'q', 'exit', 'quit']:
                    print(f"\n{Fore.GREEN}👋 Do zobaczenia!{Fore.RESET}")
                    break
                else:
                    print(f"{Fore.RED}❌ Nieprawidłowy wybór.{Fore.RESET}")
                
                # Pauza przed kolejnym menu
                if choice not in ['7', 'q', 'exit', 'quit']:
                    input(f"\n{Fore.YELLOW}👆 Naciśnij Enter, aby kontynuować...{Fore.RESET}")
                    print("\n" * 2)
                
            except KeyboardInterrupt:
                print(f"\n{Fore.YELLOW}\n⚠️  Przerwano przez użytkownika.{Fore.RESET}")
                break
            except Exception as e:
                print(f"{Fore.RED}💥 Nieoczekiwany błąd: {e}{Fore.RESET}")
                import traceback
                traceback.print_exc()
                input(f"\n{Fore.YELLOW}👆 Naciśnij Enter, aby kontynuować...{Fore.RESET}")


if __name__ == "__main__":
    # Utwórz potrzebne katalogi
    os.makedirs('data', exist_ok=True)
    os.makedirs('profiles', exist_ok=True)
    os.makedirs('logs', exist_ok=True)
    os.makedirs('modules', exist_ok=True)
    
    # Sprawdź czy istnieją potrzebne pliki
    if not os.path.exists('data/config.json'):
        default_config = {
            'max_profiles': 10,
            'view_duration_min': 30,
            'view_duration_max': 180,
            'use_fingerprinting': True,
            'use_proxy_rotation': True,
            'headless_mode': False,
            'threads': 5,
            'test_proxy_timeout': 15,
            'max_proxies_to_fetch': 1000
        }
        with open('data/config.json', 'w') as f:
            json.dump(default_config, f, indent=2)
        print(f"{Fore.GREEN}✅ Utworzono domyślną konfigurację{Fore.RESET}")
    
    # Uruchom program
    try:
        app = YouTubeViewerAdvanced()
        app.main()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}👋 Program zakończony przez użytkownika{Fore.RESET}")
    except Exception as e:
        print(f"{Fore.RED}💥 Krytyczny błąd uruchamiania: {e}{Fore.RESET}")
        import traceback
        traceback.print_exc()
        input("Naciśnij Enter aby zakończyć...")