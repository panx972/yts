from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random
import re

class YouTubeActions:
    """Akcje związane z interakcją z YouTube"""
    
    def __init__(self):
        print("✅ YouTubeActions zainicjalizowany")
    
    def search_channel(self, driver, keywords, channel_name, max_scroll=3):
        """
        Wyszukuje kanał na YouTube
        Returns: True jeśli znaleziono, False w przeciwnym razie
        """
        try:
            print(f"🔍 Szukam kanału: {channel_name}")
            
            # Znajdź pole wyszukiwania
            search_box = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, "search_query"))
            )
            
            # Wpisz frazę wyszukiwania
            search_box.clear()
            search_box.send_keys(keywords)
            search_box.send_keys(Keys.RETURN)
            
            time.sleep(random.uniform(2, 4))
            
            # Poczekaj na wyniki
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "contents"))
            )
            
            # Przewiń kilka razy aby załadować więcej wyników
            for i in range(max_scroll):
                driver.execute_script("window.scrollBy(0, 500)")
                time.sleep(random.uniform(1, 2))
            
            # Szukaj kanałów w wynikach
            channel_elements = driver.find_elements(By.XPATH, "//*[contains(@class, 'channel-link')]")
            
            if not channel_elements:
                # Alternatywny sposób wyszukiwania
                channel_elements = driver.find_elements(By.XPATH, "//a[contains(@href, '/@') or contains(@href, '/channel/')]")
            
            for element in channel_elements:
                try:
                    text = element.text.lower()
                    href = element.get_attribute("href") or ""
                    
                    # Sprawdź czy to pasujący kanał
                    if channel_name.lower() in text or any(keyword.lower() in text for keyword in keywords.split()):
                        print(f"✅ Znaleziono kanał: {channel_name}")
                        
                        # Kliknij w kanał
                        driver.execute_script("arguments[0].click();", element)
                        time.sleep(random.uniform(3, 5))
                        
                        # Potwierdź że jesteśmy na kanale
                        channel_title = driver.find_elements(By.XPATH, "//*[contains(@id, 'channel-name')]")
                        if channel_title:
                            print(f"📺 Jesteśmy na kanale: {channel_name}")
                            return True
                
                except:
                    continue
            
            print(f"❌ Nie znaleziono kanału: {channel_name}")
            return False
            
        except Exception as e:
            print(f"❌ Błąd wyszukiwania kanału: {e}")
            return False
    
    def watch_random_video_from_channel(self, driver, watch_time=60):
        """
        Ogląda losowy film z bieżącego kanału
        watch_time: czas oglądania w sekundach
        """
        try:
            print("🎬 Szukam filmów na kanale...")
            
            # Przewiń do sekcji filmów
            driver.execute_script("window.scrollBy(0, 800)")
            time.sleep(random.uniform(2, 4))
            
            # Znajdź wszystkie filmy na kanale
            video_elements = driver.find_elements(By.XPATH, "//a[@id='video-title' or contains(@href, '/watch?v=')]")
            
            if not video_elements:
                # Alternatywny sposób
                video_elements = driver.find_elements(By.XPATH, "//ytd-grid-video-renderer//a[@href]")
            
            if video_elements:
                # Wybierz losowy film
                video = random.choice(video_elements)
                video_url = video.get_attribute("href")
                
                if video_url and "youtube.com/watch" in video_url:
                    print(f"▶️  Oglądam film: {video.text[:50]}...")
                    
                    # Otwórz film
                    driver.get(video_url)
                    time.sleep(random.uniform(3, 5))
                    
                    # Odtwórz film
                    try:
                        play_button = driver.find_element(By.CLASS_NAME, "ytp-play-button")
                        if "Odtwórz" in play_button.get_attribute("title") or "Play" in play_button.get_attribute("title"):
                            play_button.click()
                            print("▶️  Film odtwarzany...")
                    except:
                        print("⏯️  Film już się odtwarza")
                    
                    # Oglądaj przez określony czas
                    print(f"⏱️  Oglądam przez {watch_time} sekund...")
                    
                    # Symuluj aktywność użytkownika
                    for i in range(watch_time // 10):
                        time.sleep(10)
                        
                        # Losowe akcje
                        if random.random() > 0.7:
                            # Przewiń trochę
                            scroll_amount = random.randint(100, 300)
                            driver.execute_script(f"window.scrollBy(0, {scroll_amount})")
                    
                    print("✅ Film obejrzany")
                    return True
            
            print("❌ Nie znaleziono filmów do obejrzenia")
            return False
            
        except Exception as e:
            print(f"❌ Błąd oglądania filmu: {e}")
            return False
    
    def like_video(self, driver):
        """Daje łapkę w górę filmowi"""
        try:
            like_button = driver.find_element(By.XPATH, "//button[contains(@aria-label, 'Lubi') or contains(@aria-label, 'like')]")
            like_button.click()
            print("👍 Polubiono film")
            return True
        except:
            return False
    
    def subscribe_channel(self, driver):
        """Subskrybuje kanał"""
        try:
            subscribe_button = driver.find_element(By.XPATH, "//*[contains(text(), 'Subskrybuj') or contains(text(), 'Subscribe')]")
            subscribe_button.click()
            print("🔔 Subskrybowano kanał")
            return True
        except:
            return False

# Testowanie modułu
if __name__ == "__main__":
    print("🧪 Testowanie YouTubeActions...")
    yt = YouTubeActions()
    print("✅ Moduł zainicjalizowany")