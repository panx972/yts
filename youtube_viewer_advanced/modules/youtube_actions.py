"""
Akcje na YouTube - oglądanie, lajkowanie, interakcje
Z obsługą konfiguracji zewnętrznej
"""

import time
import random
import re
import sys
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from colorama import Fore, Style

# Dodaj ścieżkę do katalogu głównego dla importu config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import config
    CONFIG_LOADED = True
except ImportError:
    # Domyślna konfiguracja jeśli brak pliku config.py
    print(f"{Fore.YELLOW}⚠ Brak pliku config.py, używam domyślnych ustawień{Style.RESET_ALL}")
    CONFIG_LOADED = False
    
    class DefaultConfig:
        CONFIG = {
            'min_watch_time': 30,
            'max_watch_time': 120,
            'min_break_between_videos': 10,
            'max_break_between_videos': 30,
            'max_videos_per_channel': 5,
            'enable_likes': True,
            'enable_scroll': True,
            'volume_increase': True,
            'headless_mode': False,
            'log_level': 'INFO'
        }
    
    config = DefaultConfig()

class YouTubeActions:
    def __init__(self, driver, proxy=None):
        self.driver = driver
        self.proxy = proxy
        self.wait = WebDriverWait(driver, 20)
        self.videos_found = 0
        
        # Załaduj ustawienia z konfiguracji
        self.load_config_settings()
    
    def load_config_settings(self):
        """Ładuje ustawienia z konfiguracji"""
        if CONFIG_LOADED:
            self.min_watch_time = config.CONFIG.get('min_watch_time', 30)
            self.max_watch_time = config.CONFIG.get('max_watch_time', 120)
            self.min_break = config.CONFIG.get('min_break_between_videos', 10)
            self.max_break = config.CONFIG.get('max_break_between_videos', 30)
            self.max_videos = config.CONFIG.get('max_videos_per_channel', 5)
            self.enable_likes = config.CONFIG.get('enable_likes', True)
            self.enable_scroll = config.CONFIG.get('enable_scroll', True)
            self.volume_increase = config.CONFIG.get('volume_increase', True)
            self.headless_mode = config.CONFIG.get('headless_mode', False)
        else:
            self.min_watch_time = 30
            self.max_watch_time = 120
            self.min_break = 10
            self.max_break = 30
            self.max_videos = 5
            self.enable_likes = True
            self.enable_scroll = True
            self.volume_increase = True
            self.headless_mode = False
    
    def watch_video(self, video_url, watch_time=None):
        """Ogląda film przez określony czas"""
        try:
            print(f"{Fore.CYAN}   🎬 Otwieram film: {video_url}{Style.RESET_ALL}")
            
            # Otwórz film
            self.driver.get(video_url)
            time.sleep(5)
            
            # Akceptuj cookies jeśli potrzeba
            self.accept_cookies()
            
            # Odtwarzaj film
            if not self.play_video():
                print(f"{Fore.YELLOW}   ⚠ Nie udało się uruchomić odtwarzania{Style.RESET_ALL}")
                # Spróbuj alternatywnej metody
                self.play_video_alternative()
            
            # Ustaw czas oglądania
            if watch_time is None:
                watch_time = random.randint(self.min_watch_time, self.max_watch_time)
            
            print(f"{Fore.CYAN}   ⏱ Oglądam przez {watch_time}s...{Style.RESET_ALL}")
            
            # Zwiększ głośność stopniowo
            if self.volume_increase:
                self.increase_volume_gradually()
            
            # Symuluj aktywność użytkownika podczas oglądania
            self.simulate_viewing_activity(watch_time)
            
            # Losowe lajkowanie (jeśli włączone)
            if self.enable_likes and random.random() > 0.6:
                if self.like_video():
                    print(f"{Fore.GREEN}   👍 Polubiono film{Style.RESET_ALL}")
            
            print(f"{Fore.GREEN}   ✅ Film obejrzany: {video_url}{Style.RESET_ALL}")
            return True
            
        except Exception as e:
            print(f"{Fore.RED}   ❌ Błąd oglądania filmu: {str(e)[:80]}{Style.RESET_ALL}")
            return False
    
    def simulate_viewing_activity(self, total_time):
        """Symuluje aktywność użytkownika podczas oglądania"""
        segments = total_time // 15  # Dziel czas na 15-sekundowe segmenty
        
        for segment in range(segments):
            time.sleep(15)
            
            # Losowa akcja co segment
            if random.random() > 0.7:
                action = random.choice([
                    self.small_scroll,
                    self.move_mouse_randomly,
                    self.pause_resume_video,
                    self.adjust_volume_randomly
                ])
                
                try:
                    action()
                except:
                    pass
    
    def play_video(self):
        """Uruchamia odtwarzanie filmu"""
        try:
            # Spróbuj kliknąć przycisk play
            play_button = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button.ytp-play-button"))
            )
            
            # Sprawdź czy film jest wstrzymany
            if "Odtwórz" in play_button.get_attribute("title") or "Play" in play_button.get_attribute("title"):
                play_button.click()
                time.sleep(2)
            
            return True
            
        except TimeoutException:
            # Spróbuj alternatywnych metod
            return self.play_video_alternative()
        except Exception as e:
            print(f"{Fore.YELLOW}   ⚠ Błąd play button: {str(e)[:30]}{Style.RESET_ALL}")
            return self.play_video_alternative()
    
    def play_video_alternative(self):
        """Alternatywne metody uruchamiania filmu"""
        try:
            # Metoda 1: Kliknij w obszar wideo
            video_player = self.driver.find_element(By.CSS_SELECTOR, ".html5-video-container")
            video_player.click()
            time.sleep(2)
            return True
        except:
            try:
                # Metoda 2: Użyj JavaScript
                self.driver.execute_script("""
                    var video = document.querySelector('video');
                    if (video) video.play();
                """)
                time.sleep(2)
                return True
            except:
                return False
    
    def accept_cookies(self):
        """Akceptuje cookies jeśli pojawia się baner"""
        try:
            # Różne selektory dla przycisków cookies
            cookie_selectors = [
                "//button[contains(., 'Zaakceptuj')]",
                "//button[contains(., 'Accept')]",
                "//button[contains(., 'AGREE')]",
                "//button[contains(., 'Zgadzam')]",
                "//button[contains(@aria-label, 'Accept')]",
                "//button[@id='accept-button']",
                "//ytd-button-renderer[contains(., 'Accept')]//button"
            ]
            
            for selector in cookie_selectors:
                try:
                    cookie_button = self.driver.find_element(By.XPATH, selector)
                    if cookie_button.is_displayed():
                        cookie_button.click()
                        time.sleep(1)
                        print(f"{Fore.GREEN}   ✅ Zaakceptowano cookies{Style.RESET_ALL}")
                        return True
                except:
                    continue
                    
        except Exception as e:
            pass  # Ciche ignorowanie - cookies nie zawsze są obecne
    
    def like_video(self):
        """Lajkuje film"""
        try:
            like_button = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 
                    "button[aria-label*='like i'], "
                    "button[aria-label*='Lubię to'], "
                    "ytd-toggle-button-renderer.style-default-active, "
                    "#like-button"
                ))
            )
            
            # Sprawdź czy już polubione
            if "style-default-active" not in like_button.get_attribute("class"):
                like_button.click()
                time.sleep(1)
                return True
            else:
                return False
                
        except Exception as e:
            return False
    
    def get_channel_videos(self, channel_url, max_videos=None):
        """Pobiera listę filmów z kanału"""
        if max_videos is None:
            max_videos = self.max_videos
        
        try:
            print(f"{Fore.CYAN}   📹 Pobieram filmy z kanału...{Style.RESET_ALL}")
            
            # Otwórz kanał
            self.driver.get(channel_url)
            time.sleep(5)
            
            # Spróbuj różnych metod pobierania filmów
            videos = []
            
            # Metoda 1: Przejdź do /videos
            videos_url = self.get_videos_url(channel_url)
            if videos_url:
                self.driver.get(videos_url)
                time.sleep(5)
                videos = self.extract_videos_from_page(max_videos)
            
            # Metoda 2: Jeśli brak filmów, spróbuj z głównej strony kanału
            if not videos:
                self.driver.get(channel_url)
                time.sleep(5)
                videos = self.extract_videos_from_homepage(max_videos)
            
            self.videos_found = len(videos)
            
            if videos:
                print(f"{Fore.GREEN}   ✅ Znaleziono {len(videos)} filmów{Style.RESET_ALL}")
            else:
                print(f"{Fore.YELLOW}   ⚠ Nie znaleziono filmów{Style.RESET_ALL}")
            
            return videos
            
        except Exception as e:
            print(f"{Fore.RED}   ❌ Błąd pobierania filmów: {str(e)[:80]}{Style.RESET_ALL}")
            return []
    
    def get_videos_url(self, channel_url):
        """Tworzy URL do zakładki z filmami"""
        if '/@' in channel_url:
            return channel_url + '/videos'
        elif '/channel/' in channel_url:
            return channel_url + '/videos'
        elif '/c/' in channel_url:
            return channel_url + '/videos'
        elif '/user/' in channel_url:
            return channel_url + '/videos'
        else:
            return None
    
    def extract_videos_from_page(self, max_videos):
        """Wyciąga filmy ze strony /videos"""
        videos = []
        
        try:
            # Przewiń aby załadować więcej filmów
            for _ in range(3):
                if self.enable_scroll:
                    self.driver.execute_script("window.scrollBy(0, 800)")
                    time.sleep(2)
            
            # Znajdź linki do filmów
            video_selectors = [
                "a#video-title-link",
                "ytd-thumbnail a#thumbnail",
                "#contents ytd-rich-item-renderer a#thumbnail",
                "ytd-grid-video-renderer a#thumbnail"
            ]
            
            all_links = []
            for selector in video_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        href = element.get_attribute("href")
                        if href and "/watch?v=" in href:
                            all_links.append(href)
                except:
                    continue
            
            # Usuń duplikaty i limit
            unique_links = []
            for link in all_links:
                if link not in unique_links:
                    unique_links.append(link)
                if len(unique_links) >= max_videos * 2:  # Zbierz więcej niż potrzebujemy
                    break
            
            # Pobierz tylko unikalne filmy (bez playlist)
            for link in unique_links:
                if "/watch?v=" in link and "&list=" not in link and link not in videos:
                    videos.append(link)
                if len(videos) >= max_videos:
                    break
            
        except Exception as e:
            print(f"{Fore.YELLOW}   ⚠ Błąd ekstrakcji: {str(e)[:50]}{Style.RESET_ALL}")
        
        return videos[:max_videos]
    
    def extract_videos_from_homepage(self, max_videos):
        """Wyciąga filmy z głównej strony kanału"""
        videos = []
        
        try:
            # Przewiń stronę
            for _ in range(2):
                if self.enable_scroll:
                    self.driver.execute_script("window.scrollBy(0, 600)")
                    time.sleep(2)
            
            # Szukaj filmów w różnych sekcjach
            sections = [
                "ytd-rich-grid-renderer",
                "#contents",
                "ytd-item-section-renderer"
            ]
            
            all_links = []
            for section in sections:
                try:
                    elements = self.driver.find_elements(
                        By.CSS_SELECTOR, 
                        f"{section} a[href*='/watch?v=']"
                    )
                    for element in elements:
                        href = element.get_attribute("href")
                        if href:
                            all_links.append(href)
                except:
                    continue
            
            # Filtruj i limit
            for link in all_links:
                if "/watch?v=" in link and "&list=" not in link and link not in videos:
                    videos.append(link)
                if len(videos) >= max_videos:
                    break
            
        except Exception as e:
            print(f"{Fore.YELLOW}   ⚠ Błąd ekstrakcji z homepage: {str(e)[:50]}{Style.RESET_ALL}")
        
        return videos[:max_videos]
    
    def small_scroll(self):
        """Wykonuje mały scroll"""
        if not self.enable_scroll:
            return
            
        scroll_amount = random.randint(50, 200)
        direction = 1 if random.random() > 0.5 else -1
        self.driver.execute_script(f"window.scrollBy(0, {scroll_amount * direction})")
        time.sleep(0.5)
    
    def move_mouse_randomly(self):
        """Przesuwa kursor losowo"""
        try:
            script = """
            var event = new MouseEvent('mousemove', {
                view: window,
                bubbles: true,
                cancelable: true,
                clientX: %d,
                clientY: %d
            });
            document.dispatchEvent(event);
            """ % (random.randint(100, 800), random.randint(100, 600))
            
            self.driver.execute_script(script)
            time.sleep(0.3)
        except:
            pass
    
    def pause_resume_video(self):
        """Pauzuje i wznawia odtwarzanie"""
        try:
            play_button = self.driver.find_element(By.CSS_SELECTOR, "button.ytp-play-button")
            
            # Pauzuj
            play_button.click()
            pause_time = random.uniform(0.5, 2.0)
            time.sleep(pause_time)
            
            # Wznów
            play_button.click()
            
        except:
            pass
    
    def adjust_volume_randomly(self):
        """Dostosowuje głośność losowo"""
        if not self.volume_increase:
            return
            
        try:
            # Otwórz panel głośności
            volume_button = self.driver.find_element(By.CSS_SELECTOR, "button.ytp-mute-button")
            
            # Sprawdź czy wyciszone
            is_muted = "wyciszony" in volume_button.get_attribute("title").lower() or \
                      "muted" in volume_button.get_attribute("title").lower()
            
            if is_muted:
                volume_button.click()  # Odcisz
                time.sleep(0.5)
            
            # Losowa zmiana głośności
            if random.random() > 0.3:
                try:
                    # Kliknij przycisk głośności aby pokazać slider
                    volume_button.click()
                    time.sleep(0.3)
                    
                    # Ustaw losową głośność
                    volume = random.randint(30, 90)
                    script = """
                    var slider = document.querySelector('.ytp-volume-slider');
                    if (slider) {
                        var rect = slider.getBoundingClientRect();
                        var x = rect.width * (%d / 100);
                        var event = new MouseEvent('mousedown', {clientX: rect.left + x, clientY: rect.top});
                        slider.dispatchEvent(event);
                    }
                    """ % volume
                    
                    self.driver.execute_script(script)
                    time.sleep(0.5)
                    
                    # Zamknij panel
                    volume_button.click()
                    
                except:
                    pass
            
        except:
            pass
    
    def increase_volume_gradually(self):
        """Stopniowo zwiększa głośność"""
        if not self.volume_increase:
            return
            
        try:
            volume_button = self.driver.find_element(By.CSS_SELECTOR, "button.ytp-mute-button")
            
            # Sprawdź czy wyciszone
            if "wyciszony" in volume_button.get_attribute("title").lower() or \
               "muted" in volume_button.get_attribute("title").lower():
                
                volume_button.click()  # Odcisz
                time.sleep(1)
                
                # Stopniowo zwiększaj głośność
                for vol in range(10, 70, 15):
                    try:
                        self.adjust_volume_to(vol)
                        time.sleep(0.3)
                    except:
                        break
                        
        except:
            pass
    
    def adjust_volume_to(self, percentage):
        """Ustawia głośność na konkretny procent"""
        try:
            script = """
            var video = document.querySelector('video');
            if (video) {
                video.volume = %f;
            }
            """ % (percentage / 100.0)
            
            self.driver.execute_script(script)
            
        except:
            pass
    
    def subscribe_channel(self):
        """Subskrybuje kanał"""
        try:
            subscribe_button = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 
                    "button[aria-label*='Subscribe']",
                    "ytd-subscribe-button-renderer",
                    "#subscribe-button"
                ))
            )
            
            # Sprawdź czy już subskrybowany
            if "Subscribed" not in subscribe_button.text and "Subskrybujesz" not in subscribe_button.text:
                subscribe_button.click()
                time.sleep(2)
                return True
            else:
                return False
                
        except Exception as e:
            return False
    
    def get_video_info(self):
        """Pobiera informacje o filmie"""
        try:
            title = self.driver.title.replace(" - YouTube", "").strip()
            views = "Nieznane"
            
            try:
                # Różne selektory dla liczby wyświetleń
                view_selectors = [
                    "//span[contains(text(), 'wyświetleń')]",
                    "//span[contains(text(), 'views')]",
                    "//div[@id='count']//span[1]",
                    "ytd-video-view-count-renderer span"
                ]
                
                for selector in view_selectors:
                    try:
                        if selector.startswith("//"):
                            element = self.driver.find_element(By.XPATH, selector)
                        else:
                            element = self.driver.find_element(By.CSS_SELECTOR, selector)
                        
                        if element:
                            views = element.text
                            break
                    except:
                        continue
                        
            except:
                pass
            
            return {
                'title': title,
                'views': views,
                'url': self.driver.current_url,
                'timestamp': time.strftime("%H:%M:%S")
            }
            
        except Exception as e:
            return None
    
    def close_popups(self):
        """Zamyka różne popupy"""
        try:
            # Zamknij reklamy YouTube Premium
            close_selectors = [
                "button[aria-label='Close']",
                ".ytp-ad-overlay-close-button",
                "ytd-button-renderer.style-text",
                "#dismiss-button",
                "tp-yt-paper-dialog .close-button"
            ]
            
            for selector in close_selectors:
                try:
                    close_buttons = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for button in close_buttons:
                        if button.is_displayed():
                            button.click()
                            time.sleep(0.5)
                except:
                    continue
                    
        except:
            pass
    
    def get_watch_time_settings(self):
        """Zwraca ustawienia czasu oglądania"""
        return {
            'min': self.min_watch_time,
            'max': self.max_watch_time,
            'breaks_min': self.min_break,
            'breaks_max': self.max_break
        }
    
    def update_config(self, new_config):
        """Aktualizuje konfigurację"""
        if CONFIG_LOADED:
            for key, value in new_config.items():
                if key in config.CONFIG:
                    config.CONFIG[key] = value
            
            # Zaktualizuj lokalne ustawienia
            self.load_config_settings()
            return True
        return False


# Testowanie modułu
if __name__ == "__main__":
    print("🧪 Test modułu YouTubeActions")
    print("="*50)
    
    # Testowe wywołania
    yt = YouTubeActions(None)
    
    print(f"Ustawienia oglądania:")
    settings = yt.get_watch_time_settings()
    print(f"  • Czas: {settings['min']}-{settings['max']}s")
    print(f"  • Przerwy: {settings['breaks_min']}-{settings['breaks_max']}s")
    print(f"  • Max filmów: {yt.max_videos}")
    print(f"  • Lajkowanie: {'Tak' if yt.enable_likes else 'Nie'}")
    print(f"  • Scroll: {'Tak' if yt.enable_scroll else 'Nie'}")
    
    print(f"\n✅ Moduł YouTubeActions gotowy do użycia")