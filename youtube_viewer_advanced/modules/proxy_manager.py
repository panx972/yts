"""
Manager proxy - wczytywanie, testowanie i zarządzanie proxy
Testuje WSZYSTKIE dostępne proxy z różnymi metodami testowania
"""

import os
import random
import time
import socket
import requests
from urllib.parse import urlparse
from colorama import Fore, Style
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from fake_useragent import UserAgent

class ProxyManager:
    def __init__(self):
        self.proxies = []
        self.working_proxies = []
        self.current_index = 0
        self.ua = UserAgent()
        self.test_services = [
            'http://httpbin.org/ip',
            'http://api.ipify.org?format=json',
            'http://ip-api.com/json',
            'http://checkip.amazonaws.com',
            'http://icanhazip.com'
        ]
        self.load_proxies()
    
    def load_proxies(self):
        """Ładuje proxy z pliku lub domyślnej listy"""
        proxy_file = 'data/proxy.txt'
        
        if os.path.exists(proxy_file):
            try:
                with open(proxy_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            self.proxies.append(line)
                
                if self.proxies:
                    print(f"{Fore.GREEN}✅ Załadowano {len(self.proxies)} proxy z pliku{Style.RESET_ALL}")
                else:
                    print(f"{Fore.YELLOW}⚠ Plik proxy.txt jest pusty{Style.RESET_ALL}")
                    self.load_default_proxies()
                    
            except Exception as e:
                print(f"{Fore.RED}❌ Błąd ładowania proxy: {str(e)}{Style.RESET_ALL}")
                self.load_default_proxies()
        else:
            self.load_default_proxies()
        
        # Wczytaj dobre proxy z cache
        self.load_good_proxies()
    
    def load_default_proxies(self):
        """Ładuje domyślną listę proxy"""
        # Używaj tylko tych z pliku - nie ma domyślnych
        print(f"{Fore.YELLOW}⚠ Używam proxy tylko z pliku data/proxy.txt{Style.RESET_ALL}")
        self.proxies = []
    
    def load_good_proxies(self):
        """Ładuje wcześniej znalezione dobre proxy"""
        good_proxy_file = 'data/good_proxy.txt'
        
        if os.path.exists(good_proxy_file):
            try:
                with open(good_proxy_file, 'r') as f:
                    self.working_proxies = [line.strip() for line in f if line.strip()]
                if self.working_proxies:
                    print(f"{Fore.GREEN}✅ Załadowano {len(self.working_proxies)} dobrych proxy z cache{Style.RESET_ALL}")
            except:
                self.working_proxies = []
    
    def test_proxy(self, proxy):
        """Testuje proxy różnymi metodami"""
        # Metoda 1: Podstawowe testy
        if not self.basic_connection_test(proxy):
            return False
        
        # Metoda 2: Test z różnymi serwisami
        if not self.multi_service_test(proxy):
            return False
        
        # Metoda 3: Test Selenium (opcjonalny, można wyłączyć dla szybkości)
        # if not self.selenium_test(proxy):
        #     return False
        
        return True
    
    def basic_connection_test(self, proxy):
        """Podstawowy test połączenia"""
        try:
            # Parsuj proxy
            parsed = urlparse(proxy)
            host = parsed.hostname
            port = parsed.port or (1080 if parsed.scheme == 'socks5' else 80)
            
            if not host or not port:
                return False
            
            # Test połączenia socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((host, port))
            sock.close()
            
            return result == 0
            
        except:
            return False
    
    def multi_service_test(self, proxy, required_success=2):
        """Testuje proxy z różnymi serwisami"""
        success_count = 0
        
        for service_url in random.sample(self.test_services, 3):  # Testuj 3 losowe serwisy
            try:
                response = requests.get(
                    service_url,
                    proxies={'http': proxy, 'https': proxy},
                    headers={'User-Agent': self.ua.random},
                    timeout=10
                )
                
                if response.status_code == 200:
                    success_count += 1
                    
                if success_count >= required_success:
                    return True
                    
            except:
                continue
        
        return success_count >= required_success
    
    def selenium_test(self, proxy):
        """Test z przeglądarką (dla YouTube)"""
        driver = None
        try:
            chrome_options = Options()
            chrome_options.add_argument('--headless=new')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument(f'--proxy-server={proxy}')
            
            # User agent
            chrome_options.add_argument(f'user-agent={self.ua.random}')
            
            # Inicjalizacja
            try:
                service = Service(ChromeDriverManager().install())
                driver = webdriver.Chrome(service=service, options=chrome_options)
            except:
                driver = webdriver.Chrome(options=chrome_options)
            
            driver.set_page_load_timeout(20)
            driver.get("https://www.youtube.com")
            time.sleep(2)
            
            # Sprawdź czy strona się załadowała
            page_source = driver.page_source.lower()
            driver.quit()
            
            return "youtube" in page_source
            
        except Exception as e:
            if driver:
                try:
                    driver.quit()
                except:
                    pass
            return False
    
    def find_all_working_proxies(self):
        """Testuje WSZYSTKIE proxy z listy"""
        if not self.proxies:
            print(f"{Fore.RED}❌ Brak proxy do testowania!{Style.RESET_ALL}")
            return []
        
        print(f"{Fore.CYAN}🔍 Testowanie WSZYSTKICH {len(self.proxies)} proxy...{Style.RESET_ALL}")
        print(f"   ⏱ To może zająć kilka minut{Style.RESET_ALL}")
        
        working = []
        failed = []
        
        for i, proxy in enumerate(self.proxies, 1):
            try:
                print(f"\n   [{i}/{len(self.proxies)}] 🧪 Test: {proxy}")
                
                start_time = time.time()
                
                # Test 1: Podstawowy
                print(f"      🔄 Test podstawowy...", end="", flush=True)
                if self.basic_connection_test(proxy):
                    print(f"{Fore.GREEN} OK{Style.RESET_ALL}", end="", flush=True)
                    
                    # Test 2: Multi-service
                    print(f" | Test serwisów...", end="", flush=True)
                    if self.multi_service_test(proxy):
                        elapsed = time.time() - start_time
                        print(f"{Fore.GREEN} OK ({elapsed:.1f}s){Style.RESET_ALL}")
                        working.append(proxy)
                        print(f"      {Fore.GREEN}✅ PROXY DZIAŁA!{Style.RESET_ALL}")
                    else:
                        print(f"{Fore.RED} FAIL{Style.RESET_ALL}")
                        failed.append(proxy)
                else:
                    print(f"{Fore.RED} FAIL{Style.RESET_ALL}")
                    failed.append(proxy)
                    
            except Exception as e:
                print(f"      {Fore.RED}❌ Błąd: {str(e)[:50]}{Style.RESET_ALL}")
                failed.append(proxy)
            
            # Przerwa między testami (ale nie za długa)
            if i < len(self.proxies):
                time.sleep(0.5)
        
        # Zapisz wyniki
        self.save_results(working, failed)
        
        return working
    
    def save_results(self, working, failed):
        """Zapisuje wyniki testowania"""
        print(f"\n{Fore.CYAN}" + "="*60)
        print(f"📊 PODSUMOWANIE TESTOWANIA")
        print("="*60 + f"{Style.RESET_ALL}")
        
        total = len(working) + len(failed)
        print(f"   Łącznie przetestowano: {total} proxy")
        print(f"   {Fore.GREEN}✅ Działające: {len(working)}{Style.RESET_ALL}")
        print(f"   {Fore.RED}❌ Nieudane: {len(failed)}{Style.RESET_ALL}")
        
        if total > 0:
            success_rate = (len(working) / total) * 100
            print(f"   {Fore.CYAN}📈 Wskaźnik sukcesu: {success_rate:.1f}%{Style.RESET_ALL}")
        
        # Zapisz działające proxy
        if working:
            with open('data/good_proxy.txt', 'w', encoding='utf-8') as f:
                for proxy in working:
                    f.write(proxy + '\n')
            print(f"\n{Fore.GREEN}💾 Zapisano {len(working)} proxy do data/good_proxy.txt{Style.RESET_ALL}")
        
        # Zapisz pełny raport
        self.save_full_report(working, failed)
    
    def save_full_report(self, working, failed):
        """Zapisuje pełny raport"""
        try:
            from datetime import datetime
            
            with open('data/proxy_full_report.txt', 'w', encoding='utf-8') as f:
                f.write("="*70 + "\n")
                f.write("PEŁNY RAPORT TESTOWANIA PROXY\n")
                f.write(f"Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Przetestowano: {len(working) + len(failed)} proxy\n")
                f.write("="*70 + "\n\n")
                
                f.write("DZIAŁAJĄCE PROXY:\n")
                f.write("-"*70 + "\n")
                for i, proxy in enumerate(working, 1):
                    f.write(f"{i:4d}. {proxy}\n")
                
                f.write(f"\nNIEDZIAŁAJĄCE PROXY:\n")
                f.write("-"*70 + "\n")
                for i, proxy in enumerate(failed, 1):
                    f.write(f"{i:4d}. {proxy}\n")
                
                f.write(f"\nSTATYSTYKI:\n")
                f.write("-"*70 + "\n")
                f.write(f"Działające: {len(working)} ({len(working)/max(1, len(working)+len(failed))*100:.1f}%)\n")
                f.write(f"Nieudane: {len(failed)} ({len(failed)/max(1, len(working)+len(failed))*100:.1f}%)\n")
            
            print(f"{Fore.CYAN}📄 Pełny raport: data/proxy_full_report.txt{Style.RESET_ALL}")
            
        except Exception as e:
            print(f"{Fore.YELLOW}⚠ Błąd zapisywania raportu: {str(e)}{Style.RESET_ALL}")
    
    def get_next_proxy(self):
        """Zwraca następne działające proxy"""
        if not self.working_proxies:
            # Znajdź nowe proxy
            self.working_proxies = self.find_all_working_proxies()
            
            if not self.working_proxies:
                # Jeśli nadal brak, użyj losowego
                if self.proxies:
                    proxy = random.choice(self.proxies)
                    print(f"{Fore.YELLOW}⚠ Używam losowego proxy: {proxy}{Style.RESET_ALL}")
                    return proxy
                else:
                    raise Exception("Brak dostępnych proxy!")
        
        # Rotacja proxy
        if self.current_index >= len(self.working_proxies):
            self.current_index = 0
        
        proxy = self.working_proxies[self.current_index]
        self.current_index += 1
        
        return proxy
    
    def test_specific_proxy(self, proxy):
        """Testuje konkretne proxy (do debugowania)"""
        print(f"{Fore.CYAN}🧪 Testuję proxy: {proxy}{Style.RESET_ALL}")
        
        tests = [
            ("Test podstawowy", self.basic_connection_test),
            ("Test serwisów", self.multi_service_test),
            ("Test Selenium", self.selenium_test)
        ]
        
        results = []
        for test_name, test_func in tests:
            print(f"   {test_name}...", end="", flush=True)
            try:
                result = test_func(proxy)
                status = f"{Fore.GREEN}OK{Style.RESET_ALL}" if result else f"{Fore.RED}FAIL{Style.RESET_ALL}"
                print(status)
                results.append((test_name, result))
            except Exception as e:
                print(f"{Fore.RED}ERROR: {str(e)[:50]}{Style.RESET_ALL}")
                results.append((test_name, False))
        
        # Podsumowanie
        success_count = sum(1 for _, result in results if result)
        print(f"\n{Fore.CYAN}📊 Wynik: {success_count}/{len(results)} testów passed{Style.RESET_ALL}")
        
        return success_count >= 2