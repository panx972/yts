#!/usr/bin/env python3
"""
YouTube Actions - Organiczne oglądanie BEZ interakcji
Skupia się tylko na wyświetleniach z organicznymi ruchami
"""

import time
import random
import logging
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException

class YouTubeActions:
    def __init__(self, driver, proxy=None):
        self.driver = driver
        self.proxy = proxy
        self.wait = WebDriverWait(self.driver, 15)
        
        # Konfiguracja organicznych ruchów (TYLKO do oglądania)
        self.action_config = {
            # Scrollowanie
            'min_scroll_time': 0.8,
            'max_scroll_time': 2.5,
            'min_scroll_amount': 80,
            'max_scroll_amount': 400,
            
            # Ruchy myszy
            'min_mouse_move': 40,
            'max_mouse_move': 250,
            
            # Zmiana zakładek (multitasking)
            'tab_switch_probability': 0.15,  # 15% szans
            
            # Oglądanie filmu
            'min_watch_percentage': 0.4,     # Minimum 40% filmu
            'max_watch_percentage': 0.85,    # Maximum 85% filmu
            'random_pauses_min': 0.3,
            'random_pauses_max': 2.5,
            
            # Losowe pauzy podczas scrollowania
            'scroll_pause_probability': 0.25,
            
            # Mute/unmute losowo
            'volume_change_probability': 0.2,
            
            # Pełny ekran losowo
            'fullscreen_probability': 0.1,
        }
        
        # Historia dla unikania powtarzania akcji
        self.last_actions = []
        self.max_history = 5
        
        # Logger
        self.logger = self.setup_logger()
        
        # Flaga dla Twojego kanału
        self.my_channel_patterns = [
            "@jbeegames",  # Twój kanał
            "Jbee Games",   # Nazwa kanału
            # Dodaj inne patterny swojego kanału
        ]
    
    def setup_logger(self):
        """Konfiguruje logger"""
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.FileHandler('data/youtube_actions.log', encoding='utf-8')
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def random_delay(self, min_seconds=0.3, max_seconds=2):
        """Losowe opóźnienie między akcjami"""
        delay = random.uniform(min_seconds, max_seconds)
        time.sleep(delay)
        return delay
    
    def organic_scroll_v1(self, scroll_count=2):
        """Organiczne scrollowanie - wersja 1 (gładkie)"""
        try:
            for i in range(scroll_count):
                # Losowa ilość pikseli do scrolla
                scroll_amount = random.randint(
                    self.action_config['min_scroll_amount'],
                    self.action_config['max_scroll_amount']
                )
                
                # 85% w dół, 15% w górę - jak prawdziwy użytkownik
                direction = -scroll_amount if random.random() < 0.85 else scroll_amount
                
                # Gładki scroll z animacją
                script = """
                window.scrollBy({
                    top: %d,
                    behavior: 'smooth'
                });
                """ % direction
                
                self.driver.execute_script(script)
                
                # Losowe opóźnienie między scrollami
                scroll_delay = random.uniform(
                    self.action_config['min_scroll_time'],
                    self.action_config['max_scroll_time']
                )
                time.sleep(scroll_delay)
                
                # Losowa pauza podczas scrollowania
                if random.random() < self.action_config['scroll_pause_probability']:
                    pause_time = random.uniform(0.5, 1.5)
                    time.sleep(pause_time)
            
            self.logger.info(f"Wykonano organiczne scrollowanie v1 ({scroll_count} razy)")
            return True
            
        except Exception as e:
            self.logger.error(f"Błąd podczas scrollowania v1: {e}")
            return False
    
    def organic_scroll_v2(self, scroll_count=3):
        """Organiczne scrollowanie - wersja 2 (przyrostowe)"""
        try:
            total_scroll = 0
            for i in range(scroll_count):
                # Mniejsze, częstsze scrollowanie
                small_scroll = random.randint(30, 150)
                direction = -small_scroll if random.random() < 0.9 else small_scroll
                
                self.driver.execute_script(f"window.scrollBy(0, {direction});")
                total_scroll += abs(direction)
                
                # Bardzo krótkie opóźnienia
                time.sleep(random.uniform(0.2, 0.8))
                
                # Czasami mikro-pauza
                if random.random() < 0.1:
                    time.sleep(0.3)
            
            self.logger.info(f"Wykonano organiczne scrollowanie v2 ({scroll_count} małych skoków, łącznie {total_scroll}px)")
            return True
            
        except Exception as e:
            self.logger.error(f"Błąd podczas scrollowania v2: {e}")
            return False
    
    def simulate_mouse_movement_v1(self):
        """Symuluje naturalne ruchy myszy - wersja 1 (okrężne)"""
        try:
            # Wykonaj 2-4 losowe ruchy myszy
            for _ in range(random.randint(2, 4)):
                # Losowe przesunięcia (okrężny ruch)
                x_offset = random.randint(-self.action_config['max_mouse_move'], 
                                        self.action_config['max_mouse_move'])
                y_offset = random.randint(-self.action_config['max_mouse_move'], 
                                        self.action_config['max_mouse_move'])
                
                script = """
                var evt = new MouseEvent('mousemove', {
                    view: window,
                    bubbles: true,
                    cancelable: true,
                    clientX: window.innerWidth / 2 + %d,
                    clientY: window.innerHeight / 2 + %d
                });
                document.dispatchEvent(evt);
                """ % (x_offset, y_offset)
                
                self.driver.execute_script(script)
                time.sleep(random.uniform(0.15, 0.45))
            
            return True
            
        except Exception as e:
            self.logger.error(f"Błąd symulacji myszy v1: {e}")
            return False
    
    def simulate_mouse_movement_v2(self):
        """Symuluje naturalne ruchy myszy - wersja 2 (liniowe)"""
        try:
            # Stwórz płynną trajektorię
            steps = random.randint(3, 6)
            start_x = random.randint(100, 500)
            start_y = random.randint(100, 400)
            
            for step in range(steps):
                # Płynne przesunięcie
                x_offset = start_x + (step * 50) + random.randint(-20, 20)
                y_offset = start_y + (step * 30) + random.randint(-15, 15)
                
                script = """
                var evt = new MouseEvent('mousemove', {
                    view: window,
                    bubbles: true,
                    cancelable: true,
                    clientX: %d,
                    clientY: %d
                });
                document.dispatchEvent(evt);
                """ % (x_offset, y_offset)
                
                self.driver.execute_script(script)
                time.sleep(random.uniform(0.08, 0.25))
            
            return True
            
        except Exception as e:
            self.logger.error(f"Błąd symulacji myszy v2: {e}")
            return False
    
    def random_tab_switch_v1(self):
        """Losowa zmiana zakładek - wersja 1 (krótka)"""
        if random.random() < self.action_config['tab_switch_probability']:
            try:
                self.logger.info("Rozpoczynam zmianę zakładki v1")
                
                # Otwórz nową zakładkę
                self.driver.execute_script("window.open('');")
                time.sleep(0.3)
                
                # Przełącz na nową zakładkę
                self.driver.switch_to.window(self.driver.window_handles[-1])
                
                # Otwórz szybką stronę
                quick_sites = [
                    "https://www.google.com/search?q=time",
                    "https://www.wikipedia.org",
                    "https://www.github.com",
                    "https://stackoverflow.com"
                ]
                
                self.driver.get(random.choice(quick_sites))
                time.sleep(random.uniform(1.5, 3.5))
                
                # Wróć do YouTube
                self.driver.close()
                self.driver.switch_to.window(self.driver.window_handles[0])
                
                self.logger.info("Zakończono zmianę zakładki v1")
                return True
                
            except Exception as e:
                self.logger.error(f"Błąd zmiany zakładki v1: {e}")
                # Spróbuj wrócić do głównej zakładki
                try:
                    if len(self.driver.window_handles) > 1:
                        self.driver.switch_to.window(self.driver.window_handles[0])
                except:
                    pass
                return False
        return False
    
    def random_tab_switch_v2(self):
        """Losowa zmiana zakładek - wersja 2 (tylko przełączenie)"""
        if random.random() < self.action_config['tab_switch_probability'] * 0.7:
            try:
                self.logger.info("Rozpoczynam zmianę zakładki v2 (szybka)")
                
                # Tylko przełączenie między już otwartymi zakładkami
                # (symulacja Alt+Tab)
                self.driver.execute_script("window.blur();")
                time.sleep(random.uniform(0.5, 1.2))
                self.driver.execute_script("window.focus();")
                
                self.logger.info("Zakończono zmianę zakładki v2")
                return True
                
            except Exception as e:
                self.logger.error(f"Błąd zmiany zakładki v2: {e}")
                return False
        return False
    
    def random_volume_change(self):
        """Losowa zmiana głośności"""
        if random.random() < self.action_config['volume_change_probability']:
            try:
                # Znajdź przycisk głośności
                volume_button = self.driver.find_elements(By.CSS_SELECTOR, 
                    "button.ytp-mute-button, button.ytp-volume-button")
                
                if volume_button:
                    # Losowo mute/unmute
                    volume_button[0].click()
                    time.sleep(random.uniform(0.5, 1.5))
                    
                    # Czasami wróć do poprzedniego stanu
                    if random.random() < 0.4:
                        time.sleep(random.uniform(2, 5))
                        volume_button[0].click()
                    
                    self.logger.info("Wykonano zmianę głośności")
                    return True
                    
            except Exception as e:
                self.logger.error(f"Błąd zmiany głośności: {e}")
        
        return False
    
    def random_fullscreen_toggle(self):
        """Losowe przełączenie pełnego ekranu"""
        if random.random() < self.action_config['fullscreen_probability']:
            try:
                # Znajdź przycisk pełnego ekranu
                fullscreen_button = self.driver.find_elements(By.CSS_SELECTOR,
                    "button.ytp-fullscreen-button")
                
                if fullscreen_button:
                    # Przełącz na pełny ekran
                    fullscreen_button[0].click()
                    time.sleep(random.uniform(3, 8))
                    
                    # Wróć do normalnego widoku (70% szans)
                    if random.random() < 0.7:
                        fullscreen_button[0].click()
                    
                    self.logger.info("Wykonano przełączenie pełnego ekranu")
                    return True
                    
            except Exception as e:
                self.logger.error(f"Błąd przełączania pełnego ekranu: {e}")
        
        return False
    
    def simulate_organic_watching_v1(self, watch_time):
        """Symuluje organiczne oglądanie filmu - wersja 1 (standardowa)"""
        try:
            # Losowy procent filmu do obejrzenia
            watch_percentage = random.uniform(
                self.action_config['min_watch_percentage'],
                self.action_config['max_watch_percentage']
            )
            
            actual_watch_time = watch_time * watch_percentage
            segments = random.randint(4, 7)
            segment_time = actual_watch_time / segments
            
            self.logger.info(f"Organic watching v1: {actual_watch_time:.1f}s ({watch_percentage*100:.0f}% filmu), {segments} segmentów")
            
            for segment in range(segments):
                # Obejrzyj segment
                segment_watch = segment_time * random.uniform(0.8, 1.2)
                time.sleep(segment_watch)
                
                # Losowe akcje DURING oglądania
                action_type = random.choice(['scroll', 'mouse', 'none', 'pause'])
                
                if action_type == 'scroll' and random.random() < 0.4:
                    # Krótkie scrollowanie
                    self.organic_scroll_v2(random.randint(1, 2))
                
                elif action_type == 'mouse' and random.random() < 0.3:
                    # Ruchy myszy
                    choice = random.choice([self.simulate_mouse_movement_v1, 
                                          self.simulate_mouse_movement_v2])
                    choice()
                
                elif action_type == 'pause' and random.random() < 0.2:
                    # Krótka pauza
                    pause_time = random.uniform(
                        self.action_config['random_pauses_min'],
                        self.action_config['random_pauses_max']
                    )
                    time.sleep(pause_time)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Błąd podczas organicznego oglądania v1: {e}")
            return False
    
    def simulate_organic_watching_v2(self, watch_time):
        """Symuluje organiczne oglądanie filmu - wersja 2 (z większą aktywnością)"""
        try:
            # Oglądaj większą część filmu
            watch_percentage = random.uniform(0.6, 0.95)
            actual_watch_time = watch_time * watch_percentage
            
            self.logger.info(f"Organic watching v2: {actual_watch_time:.1f}s ({watch_percentage*100:.0f}% filmu)")
            
            # Czas rozpoczęcia
            start_time = time.time()
            
            while time.time() - start_time < actual_watch_time:
                # Losowy czas segmentu (krótszy, częstsze akcje)
                segment_time = random.uniform(8, 20)
                if time.time() - start_time + segment_time > actual_watch_time:
                    segment_time = actual_watch_time - (time.time() - start_time)
                
                # Obejrzyj segment
                time.sleep(segment_time)
                
                # Więcej aktywności podczas oglądania
                if random.random() < 0.6:  # 60% szans na akcję
                    action = random.choice([
                        ('scroll', 0.3),
                        ('mouse', 0.4),
                        ('volume', 0.1),
                        ('fullscreen', 0.05),
                        ('tab', 0.15)
                    ])
                    
                    if action[0] == 'scroll':
                        self.organic_scroll_v1(random.randint(1, 2))
                    elif action[0] == 'mouse':
                        if random.random() < 0.5:
                            self.simulate_mouse_movement_v1()
                        else:
                            self.simulate_mouse_movement_v2()
                    elif action[0] == 'volume':
                        self.random_volume_change()
                    elif action[0] == 'fullscreen':
                        self.random_fullscreen_toggle()
                    elif action[0] == 'tab':
                        if random.random() < 0.7:
                            self.random_tab_switch_v2()
                        else:
                            self.random_tab_switch_v1()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Błąd podczas organicznego oglądania v2: {e}")
            return False
    
    def perform_pre_watch_actions(self):
        """Wykonuje akcje PRZED rozpoczęciem oglądania"""
        actions = []
        
        # Zawsze trochę scrollowania przed oglądaniem
        scroll_version = random.choice([self.organic_scroll_v1, self.organic_scroll_v2])
        if scroll_version(random.randint(1, 2)):
            actions.append('pre_scroll')
        
        # Czasami ruchy myszy
        if random.random() < 0.5:
            mouse_version = random.choice([self.simulate_mouse_movement_v1, 
                                         self.simulate_mouse_movement_v2])
            if mouse_version():
                actions.append('pre_mouse')
        
        return actions
    
    def perform_during_watch_actions(self):
        """Wykonuje akcje PODCZAS oglądania (wywoływane z zewnątrz)"""
        if random.random() < 0.35:  # 35% szans na akcję podczas oglądania
            action = random.choice(['scroll', 'mouse', 'tab', 'volume'])
            
            if action == 'scroll':
                return self.organic_scroll_v2(1)
            elif action == 'mouse':
                return random.choice([self.simulate_mouse_movement_v1, 
                                    self.simulate_mouse_movement_v2])()
            elif action == 'tab':
                return self.random_tab_switch_v2()
            elif action == 'volume':
                return self.random_volume_change()
        
        return False
    
    def perform_post_watch_actions(self):
        """Wykonuje akcje PO zakończeniu oglądania"""
        actions = []
        
        # Scrollowanie po filmie
        if random.random() < 0.7:
            scroll_version = random.choice([self.organic_scroll_v1, self.organic_scroll_v2])
            if scroll_version(random.randint(1, 3)):
                actions.append('post_scroll')
        
        # Czasami zmiana zakładki
        if random.random() < 0.25:
            if self.random_tab_switch_v1():
                actions.append('post_tab')
        
        return actions
    
    def get_my_channel_videos(self, channel_url, max_videos=3):
        """Pobiera filmy TYLKO z Twojego kanału"""
        videos = []
        try:
            # Przejdź do Twojego kanału
            self.driver.get(channel_url)
            time.sleep(4)
            
            # Sprawdź czy to właściwy kanał
            current_url = self.driver.current_url
            page_title = self.driver.title
            
            is_my_channel = False
            for pattern in self.my_channel_patterns:
                if pattern.lower() in current_url.lower() or pattern.lower() in page_title.lower():
                    is_my_channel = True
                    break
            
            if not is_my_channel:
                self.logger.warning(f"To nie jest Twój kanał! URL: {current_url}")
                # Przejdź do właściwego kanału
                self.driver.get("https://www.youtube.com/@jbeegames")
                time.sleep(4)
            
            # Organiczne scrollowanie aby załadować filmy
            self.organic_scroll_v1(2)
            time.sleep(1)
            self.organic_scroll_v2(3)
            time.sleep(1)
            
            # Znajdź linki do filmów
            video_elements = self.driver.find_elements(By.XPATH,
                '//a[@id="video-title-link"] | '
                '//a[contains(@href, "/watch?v=")]'
            )
            
            for element in video_elements[:max_videos * 3]:  # Szukaj więcej
                try:
                    href = element.get_attribute("href")
                    if href and "/watch?v=" in href and href not in videos:
                        videos.append(href)
                        if len(videos) >= max_videos:
                            break
                except:
                    continue
            
            self.logger.info(f"Znaleziono {len(videos)} filmów z Twojego kanału")
            
            # Jeśli nie znaleziono filmów, spróbuj jeszcze raz
            if len(videos) == 0:
                self.logger.warning("Nie znaleziono filmów, próbuję ponownie...")
                time.sleep(2)
                self.driver.refresh()
                time.sleep(4)
                
                video_elements = self.driver.find_elements(By.XPATH,
                    '//a[contains(@href, "/watch?v=")]'
                )
                
                for element in video_elements[:max_videos * 2]:
                    href = element.get_attribute("href")
                    if href and "/watch?v=" in href and href not in videos:
                        videos.append(href)
                        if len(videos) >= max_videos:
                            break
            
            return videos
            
        except Exception as e:
            self.logger.error(f"Błąd pobierania filmów z Twojego kanału: {e}")
            return []
    
    def watch_my_channel_video(self, video_url, watch_time):
        """Ogląda film Z TWOJEGO KANAŁU z organicznymi ruchami"""
        try:
            self.logger.info(f"Rozpoczynam oglądanie filmu z Twojego kanału: {video_url}")
            
            # Przejdź do filmu
            self.driver.get(video_url)
            time.sleep(5)
            
            # Sprawdź czy to film z Twojego kanału
            current_url = self.driver.current_url
            is_my_video = any(pattern.lower() in current_url.lower() 
                            for pattern in self.my_channel_patterns)
            
            if not is_my_video:
                self.logger.warning(f"To nie jest film z Twojego kanału! URL: {current_url}")
                # Wróć do swojego kanału
                self.driver.get("https://www.youtube.com/@jbeegames/videos")
                time.sleep(4)
                return False
            
            # Sprawdź czy film się załadował
            try:
                self.wait.until(
                    EC.presence_of_element_located((By.TAG_NAME, "video"))
                )
            except:
                self.logger.warning("Nie znaleziono elementu video, ale kontynuuję...")
            
            # Odtwórz film jeśli nie odtwarza się automatycznie
            try:
                play_button = self.driver.find_element(By.CSS_SELECTOR, "button.ytp-play-button")
                if play_button.get_attribute("data-title-no-tooltip") == "Odtwórz":
                    play_button.click()
                    time.sleep(2)
            except:
                pass
            
            # Akcje PRZED oglądaniem
            pre_actions = self.perform_pre_watch_actions()
            if pre_actions:
                self.logger.info(f"Akcje przed oglądaniem: {pre_actions}")
            
            # Losowo wybierz wersję oglądania
            watch_version = random.choice([self.simulate_organic_watching_v1,
                                         self.simulate_organic_watching_v2])
            
            # Oglądaj z organicznymi ruchami
            if watch_version == self.simulate_organic_watching_v1:
                self.logger.info("Używam organicznego oglądania v1")
                watch_version(watch_time)
            else:
                self.logger.info("Używam organicznego oglądania v2")
                watch_version(watch_time)
            
            # Akcje PO oglądaniu
            post_actions = self.perform_post_watch_actions()
            if post_actions:
                self.logger.info(f"Akcje po oglądaniu: {post_actions}")
            
            # Czasami losowa zmiana głośności/pełnego ekranu
            if random.random() < 0.3:
                if random.random() < 0.7:
                    self.random_volume_change()
                else:
                    self.random_fullscreen_toggle()
            
            self.logger.info(f"Zakończono organiczne oglądanie filmu z Twojego kanału (czas: {watch_time}s)")
            return True
            
        except Exception as e:
            self.logger.error(f"Błąd podczas oglądania filmu z Twojego kanału {video_url}: {e}")
            return False
    
    def browse_my_channel_only(self, channel_url, max_videos=3):
        """Przegląda TYLKO Twój kanał"""
        try:
            self.logger.info(f"Rozpoczynam przeglądanie TYLKO Twojego kanału: {channel_url}")
            
            # Idź na swój kanał
            self.driver.get(channel_url)
            time.sleep(4)
            
            # Organiczne scrollowanie po kanale
            self.organic_scroll_v1(random.randint(2, 4))
            time.sleep(1)
            self.organic_scroll_v2(random.randint(3, 5))
            time.sleep(1)
            
            # Pobierz filmy z Twojego kanału
            videos = self.get_my_channel_videos(channel_url, max_videos)
            
            if not videos:
                self.logger.warning("Nie znaleziono filmów na Twoim kanale!")
                return False
            
            # Obejrzyj losowy film z Twojego kanału
            random_video = random.choice(videos)
            
            # Losowy czas oglądania
            watch_time = random.randint(45, 120)
            
            # Oglądaj z organicznymi ruchami
            return self.watch_my_channel_video(random_video, watch_time)
            
        except Exception as e:
            self.logger.error(f"Błąd przeglądania Twojego kanału: {e}")
            return False

# Przykład użycia
if __name__ == "__main__":
    from selenium import webdriver
    from browser_manager import BrowserManager
    
    print("Testowanie YouTubeActions (TYLKO Twój kanał)...")
    
    browser = BrowserManager(profile_index=999, use_proxy=None)
    if browser.driver:
        actions = YouTubeActions(browser.driver)
        
        # Test organicznych akcji
        print("Testowanie scrollowania...")
        actions.organic_scroll_v1(2)
        
        print("Testowanie scrollowania v2...")
        actions.organic_scroll_v2(3)
        
        print("Testowanie ruchów myszy...")
        actions.simulate_mouse_movement_v1()
        actions.simulate_mouse_movement_v2()
        
        print("Test zakończony!")
        browser.quit()
    else:
        print("Nie udało się uruchomić przeglądarki")