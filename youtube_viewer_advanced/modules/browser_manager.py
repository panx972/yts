"""
Browser Manager - Zarządzanie przeglądarkami
"""

import os
import random
import socket
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from colorama import Fore, Style


class BrowserManager:
    def __init__(self, proxy_manager=None):
        self.drivers = []
        self.proxy_manager = proxy_manager
        self.used_proxies = set()
    
    def set_proxy_manager(self, proxy_manager):
        """Ustawia proxy manager"""
        self.proxy_manager = proxy_manager
    
    def get_working_proxy(self, proxy_list):
        """Znajduje działające proxy"""
        if not proxy_list or not self.proxy_manager:
            return None
        
        available_proxies = [p for p in proxy_list if p not in self.used_proxies]
        if not available_proxies:
            self.used_proxies.clear()
            available_proxies = proxy_list
        
        working_proxy = self.proxy_manager.get_working_proxy(available_proxies, max_attempts=5)
        if working_proxy:
            self.used_proxies.add(working_proxy)
            return working_proxy
        
        return None
    
    def test_proxy_for_browser(self, proxy):
        """Testuje proxy dla Chrome"""
        try:
            clean_proxy = proxy
            if '|' in clean_proxy:
                clean_proxy = clean_proxy.split('|')[0].strip()
            
            print(f"{Fore.CYAN}🧪 Test proxy: {clean_proxy}{Fore.RESET}")
            
            # Test socket
            ip, port = clean_proxy.split(':')
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            
            result = sock.connect_ex((ip, int(port)))
            sock.close()
            
            if result != 0:
                return False
            
            # Test Chrome
            try:
                options = Options()
                options.add_argument("--headless")
                options.add_argument("--no-sandbox")
                options.add_argument(f"--proxy-server=http://{clean_proxy}")
                options.add_argument("--user-agent=Mozilla/5.0")
                
                driver = webdriver.Chrome(options=options)
                driver.set_page_load_timeout(10)
                driver.get("http://www.google.com")
                
                if driver.title:
                    driver.quit()
                    return True
                else:
                    driver.quit()
                    return False
                    
            except:
                return False
                
        except:
            return False
    
    def create_profile(self, profile_name, proxy_list=None, use_fingerprinting=True, headless=False):
        """Tworzy profil przeglądarki"""
        try:
            print(f"{Fore.CYAN}🖥️  Tworzę profil: {profile_name}{Fore.RESET}")
            
            if not isinstance(profile_name, str):
                profile_name = str(profile_name)
            
            profile_path = os.path.join('profiles', profile_name)
            os.makedirs(profile_path, exist_ok=True)
            
            # Wybierz proxy
            selected_proxy = None
            proxy_cleaned = None
            
            if proxy_list and self.proxy_manager:
                selected_proxy = self.get_working_proxy(proxy_list)
                if selected_proxy and self.test_proxy_for_browser(selected_proxy):
                    proxy_cleaned = selected_proxy
                    if '|' in proxy_cleaned:
                        proxy_cleaned = proxy_cleaned.split('|')[0].strip()
                    print(f"{Fore.GREEN}🎯 Używam proxy: {proxy_cleaned}{Fore.RESET}")
                else:
                    selected_proxy = None
                    proxy_cleaned = None
            
            # Opcje Chrome
            options = Options()
            options.add_argument(f"--user-data-dir={profile_path}")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            
            if headless:
                options.add_argument("--headless=new")
            else:
                options.add_argument("--start-maximized")
            
            # Proxy
            if proxy_cleaned:
                options.add_argument(f"--proxy-server=http://{proxy_cleaned}")
            
            # User-Agent
            user_agents = [
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            ]
            options.add_argument(f'--user-agent={random.choice(user_agents)}')
            
            # Utwórz driver
            max_attempts = 2
            for attempt in range(max_attempts):
                try:
                    if attempt == 1 and proxy_cleaned:
                        print(f"{Fore.YELLOW}🔄 Próbuję bez proxy...{Fore.RESET}")
                        new_args = []
                        for arg in options.arguments:
                            if not arg.startswith('--proxy-server'):
                                new_args.append(arg)
                        options._arguments = new_args
                    
                    driver = webdriver.Chrome(options=options)
                    
                    # Ukryj automatyzację
                    try:
                        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
                    except:
                        pass
                    
                    print(f"{Fore.GREEN}✅ Profil utworzony{Fore.RESET}")
                    return driver
                    
                except Exception as e:
                    if attempt < max_attempts - 1:
                        time.sleep(2)
                    else:
                        print(f"{Fore.RED}❌ Błąd: {str(e)[:80]}...{Fore.RESET}")
                        return None
            
            return None
            
        except Exception as e:
            print(f"{Fore.RED}❌ Błąd: {e}{Fore.RESET}")
            return None
    
    def close_all_drivers(self):
        """Zamyka wszystkie przeglądarki"""
        closed = 0
        for driver in self.drivers:
            try:
                driver.quit()
                closed += 1
            except:
                pass
        self.drivers = []