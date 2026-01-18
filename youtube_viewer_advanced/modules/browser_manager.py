from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import os
import time
import random

class BrowserManager:
    """Uproszczony manager przeglądarek - najpierw ChromeDriver!"""
    
    def __init__(self):
        print("🔍 Sprawdzanie ChromeDriver...")
        self.chromedriver_path = self.verify_chromedriver()
        
        if self.chromedriver_path:
            print("✅ BrowserManager gotowy (ChromeDriver OK)")
        else:
            print("❌ BrowserManager: BRAK ChromeDriver!")
    
    def verify_chromedriver(self):
        """Sprawdza czy ChromeDriver jest dostępny"""
        # Sprawdź w bieżącym folderze
        if os.path.exists("chromedriver.exe"):
            return "chromedriver.exe"
        
        # Sprawdź w ścieżkach
        possible_paths = [
            "chromedriver.exe",
            os.path.join(os.getcwd(), "chromedriver.exe"),
            "chromedriver-win64\\chromedriver.exe",
            "C:\\chromedriver\\chromedriver.exe",
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                print(f"✅ Znaleziono ChromeDriver: {path}")
                return path
        
        # Jeśli nie znaleziono
        print("❌ NIE ZNALEZIONO ChromeDriver!")
        print("📥 Wykonaj te kroki:")
        print("   1. Pobierz z: https://chromedriver.chromium.org/")
        print("   2. Wybierz wersję dla Chrome 144")
        print("   3. Wypakuj chromedriver.exe")
        print("   4. Umieść w: ", os.getcwd())
        print("   5. Uruchom ponownie bota")
        
        return None
    
    def create_profile_with_proxy_test(self, profile_index, user_agent=None, proxy=None, headless=False):
        """Tworzy przeglądarkę - NAJPROSTSZA WERSJA"""
        print(f"\n[Profil {profile_index}] 🚀 Tworzenie przeglądarki...")
        
        if not self.chromedriver_path:
            print(f"[Profil {profile_index}] ❌ BRAK ChromeDriver!")
            return None
        
        try:
            # 1. Opcje Chrome
            chrome_options = Options()
            
            # 2. User Agent
            if user_agent:
                chrome_options.add_argument(f'user-agent={user_agent}')
            else:
                chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
            
            # 3. Proxy (jeśli podano)
            if proxy:
                print(f"[Profil {profile_index}] 🌐 Proxy: {proxy[:50]}...")
                chrome_options.add_argument(f'--proxy-server={proxy}')
            
            # 4. Headless
            if headless:
                chrome_options.add_argument('--headless')
            
            # 5. Anti-detection
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            
            # 6. Utwórz driver
            service = Service(executable_path=self.chromedriver_path)
            driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # 7. Anti-detection script
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            print(f"[Profil {profile_index}] ✅ Przeglądarka utworzona")
            return driver
            
        except Exception as e:
            error_msg = str(e)
            print(f"[Profil {profile_index}] ❌ Błąd: {error_msg[:100]}")
            
            # Szczegółowy błąd dla proxy
            if proxy and "PROXY" in error_msg.upper():
                print(f"[Profil {profile_index}] 💡 Błąd proxy - spróbuj bez proxy")
            
            return None
    
    def close_profile(self, driver, profile_index):
        """Zamyka przeglądarkę"""
        if driver:
            try:
                driver.quit()
                print(f"[Profil {profile_index}] ✅ Zamknięto")
            except:
                pass
    
    def get_random_user_agent(self):
        """Zwraca user agent"""
        agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0',
        ]
        return random.choice(agents)

# Eksport
BrowserManager.create_profile = BrowserManager.create_profile_with_proxy_test