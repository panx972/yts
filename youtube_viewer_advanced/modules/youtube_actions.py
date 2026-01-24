#!/usr/bin/env python3
"""
YouTube Actions - SPECJALNA WERSJA DLA KANAŁU @jbeegames
"""

import time
import random
import logging
import json
import os
import re
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from selenium.webdriver.common.action_chains import ActionChains

class YouTubeActions:
    def __init__(self, driver, config=None, proxy=None):
        self.driver = driver
        self.proxy = proxy
        
        # Konfiguracja
        if config is None:
            config = self._load_config()
        self.config = config
        
        # Ustawienia z configu
        self.min_watch_time = config.get('min_watch_time', 90)
        self.max_watch_time = config.get('max_watch_time', 240)
        self.channel_name = config.get('channel_name', '@jbeegames')
        self.max_videos_per_channel = config.get('max_videos_per_channel', 15)
        
        # Ważne: Nazwa Twojego kanału do wyszukiwania
        self.MY_CHANNEL_NAME = "jbeegames"  # ★★★ ZAWSZE używaj tej nazwy ★★★
        
        self.wait = WebDriverWait(self.driver, 15)
        self.logger = self.setup_logger(config.get('log_level', 'INFO'))
        
        # Flagi
        self.cookies_accepted = False
        self.last_video_url = None
        
        self.logger.info(f"🎯 YouTubeActions dla kanału: @{self.MY_CHANNEL_NAME}")
    
    def _load_config(self):
        """Ładuje konfigurację"""
        try:
            with open('data/config.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    
    def setup_logger(self, log_level='INFO'):
        """Konfiguruje logger"""
        logger = logging.getLogger(__name__)
        level_map = {'DEBUG': logging.DEBUG, 'INFO': logging.INFO, 'WARNING': logging.WARNING, 'ERROR': logging.ERROR}
        logger.setLevel(level_map.get(log_level, logging.INFO))
        
        if not logger.handlers:
            file_handler = logging.FileHandler('logs/youtube_actions.log', encoding='utf-8')
            file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)
        
        return logger
    
    # ★★★ KRYTYCZNA METODA: ODTWARZANIE FILMU NA TWOIM KANALE ★★★
    def watch_jbeegames_video(self, video_url, watch_time=None):
        """
        SPECJALNA METODA TYLKO DLA FILMÓW @jbeegames
        Działa INACZEJ niż zwykłe oglądanie
        """
        if watch_time is None:
            watch_time = random.randint(self.min_watch_time, self.max_watch_time)
        
        self.logger.info(f"🎬 OGLĄDAM FILM @jbeegames ({watch_time}s)")
        self.logger.info(f"   URL: {video_url}")
        self.last_video_url = video_url
        
        try:
            # ★★★ KROK 1: Idź bezpośrednio do filmu ★★★
            self.logger.info("1. Przechodzę do filmu...")
            self.driver.get(video_url)
            time.sleep(5)  # Daj czas na załadowanie
            
            # ★★★ KROK 2: Sprawdź czy to właściwy film ★★★
            current_url = self.driver.current_url.lower()
            if 'watch' not in current_url or 'v=' not in current_url:
                self.logger.error("❌ To nie jest strona filmu!")
                return False
            
            # ★★★ KROK 3: Usuń przeszkody ★★★
            self._remove_all_obstacles_jbeegames()
            time.sleep(2)
            
            # ★★★ KROK 4: Znajdź PLAYER ★★★
            self.logger.info("2. Szukam playera...")
            player_found = self._find_youtube_player()
            
            if not player_found:
                self.logger.error("❌ Nie znaleziono playera YouTube!")
                return False
            
            # ★★★ KROK 5: SPRÓBUJ WSZYSTKICH METOD ODTWARZANIA ★★★
            self.logger.info("3. Próbuję uruchomić film...")
            
            methods = [
                self._method1_click_play_button,
                self._method2_click_video_area,
                self._method3_javascript_play,
                self._method4_spacebar_play,
                self._method5_click_thumbnail,
            ]
            
            video_started = False
            for i, method in enumerate(methods, 1):
                self.logger.info(f"   Próba {i}/5: {method.__name__}")
                if method():
                    self.logger.info(f"   ✅ Metoda {i} zadziałała!")
                    video_started = True
                    break
                time.sleep(1)
            
            if not video_started:
                self.logger.error("❌ Żadna metoda nie zadziałała!")
                return False
            
            # ★★★ KROK 6: POTWIERDŹ ODTWARZANIE ★★★
            self.logger.info("4. Sprawdzam czy film się odtwarza...")
            time.sleep(3)
            
            is_playing = self._confirm_video_playing()
            if not is_playing:
                self.logger.warning("⚠ Film nie odtwarza się, próbuję na nowo...")
                
                # Ostatnia szansa: refresh i spróbuj ponownie
                self.driver.refresh()
                time.sleep(3)
                self._remove_all_obstacles_jbeegames()
                
                # Spróbuj 2 metody
                if self._method1_click_play_button() or self._method2_click_video_area():
                    time.sleep(3)
                    is_playing = self._confirm_video_playing()
            
            if not is_playing:
                self.logger.error("❌ NIE UDAŁO SIĘ URUCHOMIĆ FILMU!")
                return False
            
            # ★★★ KROK 7: OGLĄDAJ FILM ★★★
            self.logger.info(f"5. ✅ FILM SIĘ ODTWARZA! Oglądam przez {watch_time}s")
            
            start_time = time.time()
            while time.time() - start_time < watch_time:
                # Co 10 sekund sprawdzaj czy film nadal się odtwarza
                elapsed = time.time() - start_time
                if elapsed > 10 and int(elapsed) % 10 == 0:
                    if not self._quick_video_check():
                        self.logger.warning("⚠ Film przestał się odtwarzać, próbuję wznowić...")
                        self._method1_click_play_button()
                        time.sleep(2)
                
                # Symuluj organiczne zachowanie
                if random.random() < 0.1:
                    self._simulate_viewer_activity()
                
                time.sleep(1)
            
            self.logger.info(f"✅ ZAKOŃCZONO OGLĄDANIE ({watch_time}s)")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ KRYTYCZNY BŁĄD: {e}")
            return False
    
    def _remove_all_obstacles_jbeegames(self):
        """Usuwa przeszkody SPECJALNIE dla @jbeegames"""
        try:
            # 1. Cookies - BEZ WYJĄTKU
            self._force_accept_cookies()
            time.sleep(1)
            
            # 2. Reklamy skip
            self._skip_ads_if_present()
            time.sleep(1)
            
            # 3. Zamknij wszelkie modale
            self._close_all_modals()
            time.sleep(1)
            
        except:
            pass
    
    def _force_accept_cookies(self):
        """AGRESYWNA akceptacja cookies"""
        cookie_texts = [
            "Accept all", "I accept", "Accept", "Agree", "OK",
            "Akceptuję", "Zaakceptuj", "Zgadzam się", "OK"
        ]
        
        for text in cookie_texts:
            try:
                # Szukaj button z tekstem
                xpath = f"//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{text.lower()}')]"
                buttons = self.driver.find_elements(By.XPATH, xpath)
                
                for btn in buttons:
                    if btn.is_displayed() and btn.is_enabled():
                        btn.click()
                        self.logger.info(f"🍪 Zaakceptowano cookies: {text}")
                        time.sleep(1)
                        return True
            except:
                continue
        
        # Specjalny selektor YouTube
        try:
            selectors = [
                'button[aria-label*="Accept" i]',
                'tp-yt-paper-button[aria-label*="accept" i]',
                'button.yt-spec-button-shape-next',
                'form[action*="consent"] button'
            ]
            
            for selector in selectors:
                try:
                    btns = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for btn in btns:
                        if btn.is_displayed():
                            btn.click()
                            self.logger.info("🍪 Zaakceptowano cookies (specjalny selector)")
                            time.sleep(1)
                            return True
                except:
                    continue
        except:
            pass
        
        return False
    
    def _skip_ads_if_present(self):
        """Pomija reklamy jeśli są"""
        try:
            # Czekaj na przycisk skip (może pojawić się później)
            for _ in range(10):
                skip_buttons = self.driver.find_elements(By.CSS_SELECTOR, 
                    'button.ytp-ad-skip-button, button[class*="skip"]')
                
                for btn in skip_buttons:
                    if btn.is_displayed():
                        # Czekaj aż będzie klikalny
                        for _ in range(5):
                            if btn.is_enabled():
                                btn.click()
                                self.logger.info("⏭️ Pominięto reklamę")
                                time.sleep(1)
                                return True
                            time.sleep(0.5)
                time.sleep(1)
        except:
            pass
        return False
    
    def _close_all_modals(self):
        """Zamyka wszystkie modale"""
        close_selectors = [
            'button[aria-label*="Close" i]',
            'button[aria-label*="Zamknij" i]',
            'button.ytp-ad-overlay-close-button',
            'button.ytp-close',
            'button[title*="Close" i]',
            'button[title*="Zamknij" i]',
            'button.ytp-popup-close'
        ]
        
        for selector in close_selectors:
            try:
                btns = self.driver.find_elements(By.CSS_SELECTOR, selector)
                for btn in btns:
                    if btn.is_displayed():
                        btn.click()
                        self.logger.info("❌ Zamknięto modal")
                        time.sleep(1)
                        return True
            except:
                continue
        return False
    
    def _find_youtube_player(self):
        """Znajduje YouTube player"""
        try:
            # Różne sposoby na znalezienie playera
            player_selectors = [
                '#movie_player',
                '.html5-video-player',
                'ytd-player',
                'video',
                'div.ytd-player'
            ]
            
            for selector in player_selectors:
                try:
                    element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if element:
                        self.logger.info(f"✅ Znaleziono player: {selector}")
                        return True
                except:
                    continue
            
            # Sprawdź czy jest tag video
            videos = self.driver.find_elements(By.TAG_NAME, "video")
            if videos:
                self.logger.info(f"✅ Znaleziono {len(videos)} elementów video")
                return True
            
            self.logger.warning("⚠ Nie znaleziono playera standardowo, sprawdzam strony...")
            
            # Zrób screenshot dla debugu
            try:
                self.driver.save_screenshot('player_debug.png')
                self.logger.info("📸 Zapisano screenshot: player_debug.png")
            except:
                pass
            
            return False
            
        except Exception as e:
            self.logger.error(f"❌ Błąd znajdowania playera: {e}")
            return False
    
    # ★★★ 5 METOD ODTWARZANIA ★★★
    def _method1_click_play_button(self):
        """Metoda 1: Kliknij przycisk Play"""
        try:
            # Wszystkie możliwe przyciski Play
            play_buttons = self.driver.find_elements(By.CSS_SELECTOR,
                'button.ytp-play-button, '  # Główny przycisk
                '.ytp-play-button, '        # Alternatywny
                'button[title*="Play" i], ' # Po tytule
                'button[title*="Odtwórz" i], '
                'button[aria-label*="Play" i], '
                'button[aria-label*="Odtwórz" i], '
                '.ytp-large-play-button, '  # DUŻY przycisk
                'button.ytp-large-play-button'
            )
            
            for btn in play_buttons:
                try:
                    if btn.is_displayed():
                        # Sprawdź czy to Play (nie Pause)
                        label = btn.get_attribute("aria-label") or ""
                        if "pause" not in label.lower() and "pauza" not in label.lower():
                            btn.click()
                            self.logger.info("▶ Kliknięto przycisk Play")
                            return True
                except:
                    continue
        except:
            pass
        return False
    
    def _method2_click_video_area(self):
        """Metoda 2: Kliknij w obszar video"""
        try:
            # Znajdź video element
            videos = self.driver.find_elements(By.TAG_NAME, "video")
            if videos:
                video = videos[0]
                
                # Sprawdź rozmiar
                size = video.size
                if size['width'] > 100 and size['height'] > 100:
                    # Kliknij w środek
                    actions = ActionChains(self.driver)
                    actions.move_to_element(video).click().perform()
                    self.logger.info("🖱️ Kliknięto w obszar video")
                    return True
                
                # Jeśli video ma 0x0, może być ukryte
                self.logger.warning("⚠ Video ma rozmiar 0x0 - może być ukryte")
        except:
            pass
        return False
    
    def _method3_javascript_play(self):
        """Metoda 3: JavaScript play"""
        try:
            script = """
            // Spróbuj znaleźć video
            var videos = document.getElementsByTagName('video');
            if (videos.length > 0) {
                var video = videos[0];
                video.play().then(function() {
                    return 'VIDEO_PLAY_SUCCESS';
                }).catch(function(e) {
                    console.log('Video play error:', e);
                    return 'VIDEO_PLAY_ERROR';
                });
            }
            
            // Spróbuj player API
            var player = document.getElementById('movie_player');
            if (player && player.playVideo) {
                player.playVideo();
                return 'PLAYER_API_SUCCESS';
            }
            
            // Kliknij przycisk przez JS
            var playBtn = document.querySelector('button.ytp-play-button, .ytp-large-play-button');
            if (playBtn) {
                playBtn.click();
                return 'CLICK_SUCCESS';
            }
            
            return 'NO_ELEMENT_FOUND';
            """
            
            result = self.driver.execute_script(script)
            time.sleep(1)
            
            if 'SUCCESS' in str(result) or 'CLICK' in str(result):
                self.logger.info(f"🔧 JavaScript: {result}")
                return True
                
        except Exception as e:
            self.logger.error(f"❌ JS error: {e}")
        
        return False
    
    def _method4_spacebar_play(self):
        """Metoda 4: Naciśnij spację"""
        try:
            from selenium.webdriver.common.keys import Keys
            body = self.driver.find_element(By.TAG_NAME, "body")
            body.send_keys(Keys.SPACE)
            self.logger.info("␣ Naciśnięto spację")
            return True
        except:
            return False
    
    def _method5_click_thumbnail(self):
        """Metoda 5: Kliknij w miniaturkę"""
        try:
            # Czasami trzeba kliknąć w miniaturkę
            thumbnails = self.driver.find_elements(By.CSS_SELECTOR,
                '.ytp-cued-thumbnail-overlay, '
                '.ytp-cued-thumbnail-overlay-image, '
                'div.ytp-cued-thumbnail-overlay'
            )
            
            for thumb in thumbnails:
                if thumb.is_displayed():
                    thumb.click()
                    self.logger.info("🖼️ Kliknięto w miniaturkę")
                    return True
        except:
            pass
        return False
    
    def _confirm_video_playing(self):
        """Potwierdza czy film się odtwarza"""
        try:
            script = """
            var video = document.querySelector('video');
            if (!video) return 'NO_VIDEO';
            
            // Sprawdź podstawowe właściwości
            if (!video.paused && video.readyState >= 2) {
                return 'PLAYING';
            }
            
            if (video.paused) {
                return 'PAUSED';
            }
            
            if (video.readyState < 2) {
                return 'NOT_LOADED';
            }
            
            return 'UNKNOWN';
            """
            
            for _ in range(3):  # Spróbuj 3 razy
                result = self.driver.execute_script(script)
                self.logger.info(f"📊 Status video: {result}")
                
                if result == 'PLAYING':
                    return True
                elif result == 'PAUSED':
                    # Spróbuj wznowić
                    self._method1_click_play_button()
                    time.sleep(2)
                
                time.sleep(1)
            
            return False
            
        except Exception as e:
            self.logger.error(f"❌ Błąd sprawdzania: {e}")
            return False
    
    def _quick_video_check(self):
        """Szybkie sprawdzenie czy video gra"""
        try:
            script = "return document.querySelector('video') && !document.querySelector('video').paused;"
            return self.driver.execute_script(script)
        except:
            return False
    
    def _simulate_viewer_activity(self):
        """Symuluje aktywność widza"""
        try:
            # Losowe ruchy scroll
            if random.random() < 0.5:
                scroll = random.randint(50, 200)
                self.driver.execute_script(f"window.scrollBy(0, {scroll});")
            
            # Losowe ruchy myszy
            if random.random() < 0.3:
                script = """
                var evt = new MouseEvent('mousemove', {
                    bubbles: true,
                    clientX: Math.random() * window.innerWidth,
                    clientY: Math.random() * window.innerHeight
                });
                document.dispatchEvent(evt);
                """
                self.driver.execute_script(script)
                
        except:
            pass
    
    # ★★★ METODY DLA MAIN.PY ★★★
    def organic_search_channel(self, channel_input):
        """Wyszukuje kanał @jbeegames"""
        self.logger.info(f"🔍 Szukam kanału: {self.MY_CHANNEL_NAME}")
        
        try:
            # Przejdź na YouTube
            self.driver.get("https://www.youtube.com")
            time.sleep(3)
            
            # Zaakceptuj cookies
            self._force_accept_cookies()
            time.sleep(2)
            
            # Wyszukaj kanał
            search_box = self.wait.until(
                EC.presence_of_element_located((By.NAME, "search_query"))
            )
            
            search_box.click()
            time.sleep(0.5)
            search_box.clear()
            
            # Wpisz nazwę kanału
            search_query = self.MY_CHANNEL_NAME
            for char in search_query:
                search_box.send_keys(char)
                time.sleep(random.uniform(0.05, 0.15))
            
            time.sleep(1)
            search_box.send_keys(Keys.RETURN)
            self.logger.info(f"✅ Wyszukano: {search_query}")
            time.sleep(4)
            
            # Przejdź do kanału
            channel_url = f"https://www.youtube.com/@{self.MY_CHANNEL_NAME}"
            self.driver.get(channel_url)
            time.sleep(4)
            
            self.logger.info(f"✅ Na kanale: @{self.MY_CHANNEL_NAME}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Błąd wyszukiwania: {e}")
            
            # Fallback: idź bezpośrednio
            self.driver.get(f"https://www.youtube.com/@{self.MY_CHANNEL_NAME}")
            time.sleep(4)
            return True
    
    def get_my_channel_videos(self, channel_name, max_videos=15):
        """Pobiera filmy z Twojego kanału"""
        self.logger.info(f"📹 Szukam filmów na @{self.MY_CHANNEL_NAME}")
        
        videos = []
        try:
            # Idź bezpośrednio na kanał
            self.driver.get(f"https://www.youtube.com/@{self.MY_CHANNEL_NAME}/videos")
            time.sleep(4)
            
            # Scrolluj aby załadować filmy
            for _ in range(3):
                self.driver.execute_script("window.scrollBy(0, 800);")
                time.sleep(2)
            
            # Znajdź wszystkie linki do filmów
            all_links = self.driver.find_elements(By.TAG_NAME, "a")
            
            for link in all_links:
                try:
                    href = link.get_attribute("href")
                    if href and "/watch?v=" in href:
                        # Upewnij się że to film z Twojego kanału
                        if self.MY_CHANNEL_NAME in href.lower():
                            if href not in videos:
                                videos.append(href)
                                if len(videos) >= max_videos:
                                    break
                except:
                    continue
            
            self.logger.info(f"✅ Znaleziono {len(videos)} filmów z @{self.MY_CHANNEL_NAME}")
            
            # Jeśli nie znaleziono, spróbuj inaczej
            if len(videos) == 0:
                self.logger.warning("⚠ Nie znaleziono filmów, próbuję alternatywnie...")
                
                # Spróbuj znaleźć po id="video-title-link"
                video_elements = self.driver.find_elements(By.ID, "video-title-link")
                for elem in video_elements[:max_videos]:
                    try:
                        href = elem.get_attribute("href")
                        if href and "/watch?v=" in href and href not in videos:
                            videos.append(href)
                    except:
                        continue
            
            return videos
            
        except Exception as e:
            self.logger.error(f"❌ Błąd pobierania filmów: {e}")
            return []
    
    def browse_my_channel_only(self, channel_name=None, max_videos=3):
        """Przegląda tylko Twój kanał"""
        try:
            self.logger.info(f"🚀 Przeglądam kanał @{self.MY_CHANNEL_NAME}")
            
            # 1. Znajdź kanał
            self.organic_search_channel(self.MY_CHANNEL_NAME)
            time.sleep(3)
            
            # 2. Pobierz filmy
            videos = self.get_my_channel_videos(self.MY_CHANNEL_NAME, max_videos)
            
            if not videos:
                self.logger.error("❌ Nie znaleziono filmów!")
                return False
            
            # 3. Obejrzyj losowy film
            random_video = random.choice(videos)
            watch_time = random.randint(self.min_watch_time, self.max_watch_time)
            
            self.logger.info(f"🎲 Losowy film: {random_video}")
            
            # ★★★ UŻYJ SPECJALNEJ METODY ★★★
            success = self.watch_jbeegames_video(random_video, watch_time)
            
            return success
            
        except Exception as e:
            self.logger.error(f"❌ Błąd przeglądania: {e}")
            return False
    
    # ★★★ KOMPATYBILNOŚĆ: stare metody ★★★
    def watch_my_channel_video(self, video_url, watch_time=None):
        """Kompatybilność: używa nowej metody"""
        return self.watch_jbeegames_video(video_url, watch_time)
    
    def verify_current_channel(self, expected_channel):
        """Weryfikuje kanał"""
        try:
            current_url = self.driver.current_url.lower()
            return self.MY_CHANNEL_NAME in current_url
        except:
            return False

# ★★★ DIAGNOSTYCZNY TEST ★★★
def test_jbeegames_video():
    """Testuje czy film się odtwarza na @jbeegames"""
    print("🧪 TEST FILMU @jbeegames")
    
    from browser_manager import BrowserManager
    
    # 1. Uruchom przeglądarkę
    browser = BrowserManager(
        profile_index=999,
        use_proxy=None,
        use_fingerprint=False,  # Wyłącz fingerprint dla testu
        auto_accept_cookies=True
    )
    
    if not browser.driver:
        print("❌ Nie udało się uruchomić przeglądarki")
        return
    
    actions = YouTubeActions(browser.driver)
    
    # 2. Znajdź film na kanale
    print("1. Szukam filmów na @jbeegames...")
    videos = actions.get_my_channel_videos("jbeegames", max_videos=3)
    
    if not videos:
        print("❌ Nie znaleziono filmów!")
        browser.quit()
        return
    
    print(f"✅ Znaleziono {len(videos)} filmów")
    
    # 3. Testuj pierwszy film
    test_video = videos[0]
    print(f"2. Testuję film: {test_video}")
    
    # 4. Oglądaj przez 30 sekund
    success = actions.watch_jbeegames_video(test_video, watch_time=30)
    
    if success:
        print("✅ TEST UDANY! Film się odtwarzał.")
    else:
        print("❌ TEST NIEUDANY! Film się nie odtwarzał.")
        
        # Zrób screenshot
        browser.driver.save_screenshot('test_failed.png')
        print("📸 Zapisano screenshot: test_failed.png")
    
    browser.quit()

if __name__ == "__main__":
    test_jbeegames_video()