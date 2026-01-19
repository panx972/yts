"""
BrowserManager bez problemów z uprawnieniami i ścieżkami
"""

import os
import random
import time
import tempfile
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from fake_useragent import UserAgent

class BrowserManager:
    def __init__(self, profile_index=1, use_proxy=None):
        self.profile_index = profile_index
        self.use_proxy = use_proxy
        self.driver = None
        
        # Używamy TYLKO katalogu tymczasowego systemu
        self.temp_dir = tempfile.gettempdir()
        
        self.init_browser()
    
    def get_safe_profile_path(self):
        """Tworzy bezpieczną ścieżkę profilu BEZ spacji"""
        # Utwórz bazowy katalog dla profili
        base_dir = os.path.join(self.temp_dir, 'ytbot_profiles')
        os.makedirs(base_dir, exist_ok=True)
        
        # Nazwa profilu bez spacji i znaków specjalnych
        profile_name = f"p{self.profile_index}_{int(time.time())}_{random.randint(1000,9999)}"
        
        # Pełna ścieżka
        profile_path = os.path.join(base_dir, profile_name)
        os.makedirs(profile_path, exist_ok=True)
        
        return profile_path
    
    def init_browser(self):
        """Inicjalizuje przeglądarkę z bezpieczną ścieżką"""
        try:
            chrome_options = Options()
            
            # OPCJE DLA WINDOWS - MINIMALNY ZESTAW
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            
            # WYŁĄCZ WSZYSTKIE PROBLEMATYCZNE FUNKCJE
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # User agent
            ua = UserAgent()
            user_agent = ua.random
            chrome_options.add_argument(f'user-agent={user_agent}')
            
            # Rozmiar okna
            chrome_options.add_argument('--window-size=1920,1080')
            
            # Proxy
            if self.use_proxy:
                chrome_options.add_argument(f'--proxy-server={self.use_proxy}')
            
            # WAŻNE: Ścieżka profilu w katalogu tymczasowym
            profile_path = self.get_safe_profile_path()
            chrome_options.add_argument(f'--user-data-dir={profile_path}')
            
            # DODAJ TE OPCJE DLA WINDOWS:
            chrome_options.add_argument('--disable-software-rasterizer')
            chrome_options.add_argument('--disable-features=VizDisplayCompositor')
            chrome_options.add_argument('--disable-logging')
            chrome_options.add_argument('--log-level=3')
            chrome_options.add_argument('--silent')
            
            print(f"🚀 Inicjalizacja przeglądarki...")
            print(f"   📁 Profil: {os.path.basename(profile_path)}")
            print(f"   👤 User Agent: {user_agent[:60]}...")
            
            # Inicjalizuj ChromeDriver
            try:
                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
            except Exception as e:
                print(f"⚠ Fallback do Chrome bez service...")
                self.driver = webdriver.Chrome(options=chrome_options)
            
            # Ukryj automatyzację
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            print(f"✅ Przeglądarka gotowa!")
            return True
            
        except Exception as e:
            print(f"❌ Błąd: {str(e)}")
            return self.try_headless_mode()
    
    def try_headless_mode(self):
        """Próbuje uruchomić w trybie headless (bez GUI)"""
        try:
            print("🔄 Próba uruchomienia w trybie headless...")
            
            chrome_options = Options()
            chrome_options.add_argument('--headless=new')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            
            # User agent
            ua = UserAgent()
            user_agent = ua.random
            chrome_options.add_argument(f'user-agent={user_agent}')
            
            if self.use_proxy:
                chrome_options.add_argument(f'--proxy-server={self.use_proxy}')
            
            # NIE używaj user-data-dir w headless (mniej problemów)
            chrome_options.add_argument('--incognito')
            
            self.driver = webdriver.Chrome(options=chrome_options)
            
            print(f"✅ Przeglądarka headless gotowa!")
            return True
            
        except Exception as e:
            print(f"❌ Błąd headless: {str(e)}")
            return False
    
    def get_driver(self):
        return self.driver
    
    def quit(self):
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass