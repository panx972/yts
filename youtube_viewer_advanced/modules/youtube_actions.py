"""
YouTube Actions - Obsługa akcji na YouTube
"""

import time
import random
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from colorama import Fore, Style


class YouTubeActions:
    def __init__(self):
        self.wait_timeout = 30
    
    def watch_video(self, driver, video_url, min_duration=30, max_duration=180):
        """Ogląda film na YouTube"""
        try:
            print(f"{Fore.CYAN}🎬 Przechodzę do filmu...{Fore.RESET}")
            
            driver.get(video_url)
            time.sleep(3)
            
            # Zaakceptuj cookies
            self.accept_cookies(driver)
            
            # Czekaj na video
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "video"))
                )
            except:
                print(f"{Fore.YELLOW}⚠️  Nie znaleziono video{Fore.RESET}")
                return False
            
            # Czas oglądania
            watch_time = random.randint(min_duration, max_duration)
            print(f"{Fore.CYAN}⏱️  Oglądam {watch_time}s{Fore.RESET}")
            
            # Symuluj aktywność
            for _ in range(3):
                driver.execute_script("window.scrollBy(0, 300)")
                time.sleep(1)
            
            # Oglądaj
            elapsed = 0
            while elapsed < watch_time:
                if random.random() > 0.7:
                    self.perform_random_action(driver)
                time.sleep(random.uniform(5, 15))
                elapsed += random.uniform(5, 15)
            
            return True
            
        except Exception as e:
            print(f"{Fore.RED}❌ Błąd: {e}{Fore.RESET}")
            return False
    
    def search_and_verify_channel(self, driver, channel_url, channel_name, videos_to_watch=3):
        """Wyszukuje kanał i ogląda filmy"""
        result = {
            'channel_found': False,
            'videos_watched': 0,
            'success': False,
            'error': None
        }
        
        try:
            print(f"{Fore.CYAN}🔍 Szukam kanału: {channel_name}{Fore.RESET}")
            
            driver.get("https://www.youtube.com")
            time.sleep(3)
            self.accept_cookies(driver)
            
            # Wyszukaj
            search_box = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, "search_query"))
            )
            search_box.clear()
            search_box.send_keys(channel_name)
            search_box.send_keys(Keys.RETURN)
            time.sleep(3)
            
            # Szukaj kanału
            channel_found = self.find_channel_in_results(driver, channel_name)
            
            if not channel_found:
                try:
                    driver.get(channel_url)
                    time.sleep(3)
                    page_title = driver.title.lower()
                    if channel_name.lower() in page_title:
                        channel_found = True
                        print(f"{Fore.GREEN}✅ Znaleziono przez URL{Fore.RESET}")
                    else:
                        result['error'] = "Nieprawidłowy kanał"
                        return result
                except:
                    result['error'] = "Nie można załadować kanału"
                    return result
            
            if channel_found:
                result['channel_found'] = True
                print(f"{Fore.GREEN}✅ Kanał znaleziony!{Fore.RESET}")
                
                # Obejrzyj filmy
                videos_watched = 0
                for i in range(videos_to_watch):
                    try:
                        videos = driver.find_elements(By.XPATH, "//a[@id='video-title']")
                        if not videos:
                            videos = driver.find_elements(By.XPATH, "//ytd-grid-video-renderer//a[@id='video-title']")
                        
                        if i < len(videos):
                            video = videos[i]
                            video_url = video.get_attribute("href")
                            
                            if video_url:
                                print(f"{Fore.CYAN}📺 Film {i+1}/{videos_to_watch}{Fore.RESET}")
                                
                                driver.execute_script("window.open(arguments[0]);", video_url)
                                driver.switch_to.window(driver.window_handles[-1])
                                time.sleep(3)
                                
                                watch_success = self.watch_video(
                                    driver=driver,
                                    video_url=video_url,
                                    min_duration=30,
                                    max_duration=120
                                )
                                
                                if watch_success:
                                    videos_watched += 1
                                
                                driver.close()
                                driver.switch_to.window(driver.window_handles[0])
                                time.sleep(2)
                        
                    except Exception as e:
                        print(f"{Fore.RED}❌ Błąd film {i+1}: {e}{Fore.RESET}")
                
                result['videos_watched'] = videos_watched
                result['success'] = videos_watched > 0
                
            else:
                result['error'] = "Kanał nie znaleziony"
            
            return result
            
        except Exception as e:
            print(f"{Fore.RED}❌ Błąd: {e}{Fore.RESET}")
            result['error'] = str(e)
            return result
    
    def find_channel_in_results(self, driver, channel_name):
        """Szuka kanału w wynikach"""
        try:
            channel_elements = driver.find_elements(By.XPATH, "//ytd-channel-renderer")
            
            for element in channel_elements[:5]:
                try:
                    title_element = element.find_element(By.XPATH, ".//*[@id='channel-title']")
                    title = title_element.text.lower()
                    
                    search_terms = [term.lower().strip() for term in channel_name.split('|') if term.strip()]
                    
                    for term in search_terms:
                        if term in title or f"@{term}" in title:
                            try:
                                link = element.find_element(By.XPATH, ".//a[@id='channel-title']")
                                driver.execute_script("arguments[0].click();", link)
                                time.sleep(3)
                                return True
                            except:
                                pass
                except:
                    continue
            
            return False
            
        except Exception as e:
            print(f"{Fore.YELLOW}⚠️  Błąd: {e}{Fore.RESET}")
            return False
    
    def accept_cookies(self, driver):
        """Zaakceptuj cookies"""
        try:
            cookie_selectors = [
                "//button[contains(@aria-label, 'cookies')]",
                "//button[contains(text(), 'Accept')]",
                "//button[contains(text(), 'Zaakceptuj')]",
            ]
            
            for selector in cookie_selectors:
                try:
                    cookie_button = WebDriverWait(driver, 2).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    cookie_button.click()
                    time.sleep(1)
                    break
                except:
                    continue
                    
        except:
            pass
    
    def perform_random_action(self, driver):
        """Losowa akcja"""
        try:
            actions = ['like', 'pause', 'scroll']
            action = random.choice(actions)
            
            if action == 'like' and random.random() > 0.7:
                try:
                    like_button = driver.find_element(By.XPATH, "//button[@aria-label='Like this video']")
                    like_button.click()
                    time.sleep(1)
                except:
                    pass
                    
            elif action == 'pause' and random.random() > 0.8:
                try:
                    player = driver.find_element(By.TAG_NAME, "video")
                    driver.execute_script("arguments[0].pause();", player)
                    time.sleep(random.uniform(2, 5))
                    driver.execute_script("arguments[0].play();", player)
                except:
                    pass
            
            elif action == 'scroll':
                try:
                    driver.execute_script("window.scrollBy(0, 400);")
                    time.sleep(2)
                except:
                    pass
                    
        except:
            pass