"""
Akcje na YouTube - oglądanie, lajkowanie, interakcje
"""

import time
import random
import re
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from colorama import Fore, Style

class YouTubeActions:
    def __init__(self, driver, proxy=None):
        self.driver = driver
        self.proxy = proxy
        self.wait = WebDriverWait(driver, 15)
    
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
                return False
            
            # Ustaw czas oglądania
            if watch_time is None:
                watch_time = random.randint(30, 120)
            
            print(f"{Fore.CYAN}   ⏱ Oglądam przez {watch_time}s...{Style.RESET_ALL}")
            
            # Symuluj aktywność użytkownika
            for i in range(watch_time // 10):
                time.sleep(10)
                
                # Losowe akcje podczas oglądania
                if random.random() > 0.8:
                    self.simulate_user_activity()
            
            # Zwiększ głośność stopniowo
            self.increase_volume_gradually()
            
            print(f"{Fore.GREEN}   ✅ Film obejrzany: {video_url}{Style.RESET_ALL}")
            return True
            
        except Exception as e:
            print(f"{Fore.RED}   ❌ Błąd oglądania filmu: {str(e)[:100]}{Style.RESET_ALL}")
            return False
    
    def play_video(self):
        """Uruchamia odtwarzanie filmu"""
        try:
            # Spróbuj kliknąć przycisk play
            play_button = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button.ytp-play-button"))
            )
            play_button.click()
            time.sleep(2)
            return True
        except:
            # Jeśli nie ma przycisku, być może film już się odtwarza
            try:
                # Sprawdź czy film się odtwarza
                video = self.driver.find_element(By.CSS_SELECTOR, "video")
                if video:
                    return True
            except:
                pass
            
            # Spróbuj kliknąć wideo
            try:
                video_player = self.driver.find_element(By.CSS_SELECTOR, ".html5-video-container")
                video_player.click()
                time.sleep(2)
                return True
            except:
                return False
    
    def accept_cookies(self):
        """Akceptuje cookies jeśli pojawia się baner"""
        try:
            cookie_button = self.driver.find_element(
                By.XPATH, 
                "//button[contains(., 'Zaakceptuj') or contains(., 'Accept') or contains(., 'AGREE')]"
            )
            cookie_button.click()
            time.sleep(1)
            print(f"{Fore.GREEN}   ✅ Zaakceptowano cookies{Style.RESET_ALL}")
        except:
            pass
    
    def like_video(self):
        """Lajkuje film"""
        try:
            like_button = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button[aria-label*='like']"))
            )
            like_button.click()
            time.sleep(1)
            return True
        except:
            return False
    
    def subscribe_channel(self):
        """Subskrybuje kanał"""
        try:
            subscribe_button = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button[aria-label*='Subscribe']"))
            )
            
            # Sprawdź czy już subskrybowany
            if "Subscribed" in subscribe_button.text:
                return False
            
            subscribe_button.click()
            time.sleep(2)
            return True
        except:
            return False
    
    def get_channel_videos(self, channel_url, max_videos=10):
        """Pobiera listę filmów z kanału"""
        try:
            print(f"{Fore.CYAN}   📹 Pobieram filmy z kanału...{Style.RESET_ALL}")
            
            # Otwórz kanał
            self.driver.get(channel_url)
            time.sleep(5)
            
            # Przejdź do zakładki z filmami
            try:
                videos_tab = self.driver.find_element(
                    By.XPATH, 
                    "//yt-tab-shape//div[contains(text(), 'Filmy') or contains(text(), 'Videos')]"
                )
                videos_tab.click()
                time.sleep(3)
            except:
                # Spróbuj alternatywnego selektora
                try:
                    videos_tab = self.driver.find_element(
                        By.CSS_SELECTOR, 
                        "a[href*='/videos']"
                    )
                    videos_tab.click()
                    time.sleep(3)
                except:
                    pass
            
            # Przewiń aby załadować więcej filmów
            for _ in range(3):
                self.driver.execute_script("window.scrollBy(0, 1000)")
                time.sleep(2)
            
            # Znajdź linki do filmów
            video_elements = self.driver.find_elements(
                By.CSS_SELECTOR, 
                "a#video-title-link, ytd-thumbnail a"
            )
            
            videos = []
            for element in video_elements:
                href = element.get_attribute("href")
                if href and "/watch?v=" in href and href not in videos:
                    videos.append(href)
                
                if len(videos) >= max_videos:
                    break
            
            print(f"{Fore.GREEN}   ✅ Znaleziono {len(videos)} filmów{Style.RESET_ALL}")
            return videos
            
        except Exception as e:
            print(f"{Fore.RED}   ❌ Błąd pobierania filmów: {str(e)[:100]}{Style.RESET_ALL}")
            return []
    
    def simulate_user_activity(self):
        """Symuluje aktywność użytkownika"""
        try:
            actions = [
                self.small_scroll,
                self.move_mouse_randomly,
                self.pause_resume_video,
                self.adjust_volume
            ]
            
            random.choice(actions)()
            return True
        except:
            return False
    
    def small_scroll(self):
        """Wykonuje mały scroll"""
        scroll_amount = random.randint(50, 200)
        self.driver.execute_script(f"window.scrollBy(0, {scroll_amount})")
        time.sleep(1)
    
    def move_mouse_randomly(self):
        """Przesuwa kursor losowo"""
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
        time.sleep(0.5)
    
    def pause_resume_video(self):
        """Pauzuje i wznawia odtwarzanie"""
        try:
            play_button = self.driver.find_element(By.CSS_SELECTOR, "button.ytp-play-button")
            play_button.click()
            time.sleep(random.uniform(0.5, 2))
            play_button.click()
        except:
            pass
    
    def adjust_volume(self):
        """Dostosowuje głośność"""
        try:
            # Otwórz panel głośności
            volume_button = self.driver.find_element(By.CSS_SELECTOR, "button.ytp-mute-button")
            volume_button.click()
            time.sleep(0.5)
            
            # Ustaw losową głośność
            volume_slider = self.driver.find_element(By.CSS_SELECTOR, ".ytp-volume-slider")
            if volume_slider:
                volume = random.randint(30, 100)
                script = """
                arguments[0].style.width = '%d%%';
                """ % volume
                self.driver.execute_script(script, volume_slider)
            
            time.sleep(0.5)
            volume_button.click()  # Zamknij panel
        except:
            pass
    
    def increase_volume_gradually(self):
        """Stopniowo zwiększa głośność"""
        try:
            volume_button = self.driver.find_element(By.CSS_SELECTOR, "button.ytp-mute-button")
            
            # Sprawdź czy wyciszone
            if "wyciszony" in volume_button.get_attribute("title").lower() or \
               "muted" in volume_button.get_attribute("title").lower():
                volume_button.click()  # Odcisz
                time.sleep(1)
                
                # Stopniowo zwiększaj głośność
                for vol in range(10, 80, 10):
                    try:
                        volume_slider = self.driver.find_element(By.CSS_SELECTOR, ".ytp-volume-slider")
                        if volume_slider:
                            script = """
                            arguments[0].style.width = '%d%%';
                            """ % vol
                            self.driver.execute_script(script, volume_slider)
                            time.sleep(0.5)
                    except:
                        break
        except:
            pass
    
    def get_video_info(self):
        """Pobiera informacje o filmie"""
        try:
            title = self.driver.title
            views = "Nieznane"
            
            try:
                view_element = self.driver.find_element(
                    By.XPATH, 
                    "//span[contains(text(), 'wyświetleń') or contains(text(), 'views')]"
                )
                views = view_element.text
            except:
                pass
            
            return {
                'title': title,
                'views': views,
                'url': self.driver.current_url
            }
        except:
            return None