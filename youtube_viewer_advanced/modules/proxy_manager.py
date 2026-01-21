"""
Manager proxy - testuje WSZYSTKIE proxy z listy aż znajdzie działające
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
            'http://api.ipify.org?format=json',
            'http://icanhazip.com',
            'http://checkip.amazonaws.com',
            'http://ip-api.com/json',
            'http://httpbin.org/ip'
        ]
        self.load_proxies()
    
    def load_proxies(self):
        """Ładuje WSZYSTKIE proxy z pliku"""
        proxy_file = 'data/proxy.txt'
        
        if os.path.exists(proxy_file):
            try:
                with open(proxy_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            self.proxies.append(line)
                
                print(f"{Fore.GREEN}✅ Załadowano {len(self.proxies)} proxy z pliku{Style.RESET_ALL}")
                
                if len(self.proxies) == 0:
                    print(f"{Fore.RED}❌ Plik proxy.txt jest pusty!{Style.RESET_ALL}")
                    print(f"{Fore.YELLOW}   Uruchom: python get_fresh_proxies.py{Style.RESET_ALL}")
                    
            except Exception as e:
                print(f"{Fore.RED}❌ Błąd ładowania proxy: {str(e)}{Style.RESET_ALL}")
                self.proxies = []
        else:
            print(f"{Fore.RED}❌ Brak pliku data/proxy.txt!{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}   Uruchom: python get_fresh_proxies.py{Style.RESET_ALL}")
            self.proxies = []
        
        # Wczytaj wcześniejsze dobre proxy
        self.load_good_proxies()
    
    def load_good_proxies(self):
        """Ładuje wcześniej znalezione dobre proxy"""
        good_proxy_file = 'data/good_proxy.txt'
        
        if os.path.exists(good_proxy_file):
            try:
                with open(good_proxy_file, 'r') as f:
                    self.working_proxies = [line.strip() for line in f if line.strip()]
                
                if self.working_proxies:
                    print(f"{Fore.GREEN}📂 Załadowano {len(self.working_proxies)} dobrych proxy z cache{Style.RESET_ALL}")
                    
                    # Użyj ich jako pierwsze
                    self.proxies = self.working_proxies + self.proxies
                    
            except Exception as e:
                print(f"{Fore.YELLOW}⚠ Błąd ładowania cache: {str(e)}{Style.RESET_ALL}")
                self.working_proxies = []
    
    def save_good_proxies(self, proxies):
        """Zapisuje dobre proxy do pliku"""
        try:
            with open('data/good_proxy.txt', 'w', encoding='utf-8') as f:
                for proxy in proxies:
                    f.write(proxy + '\n')
            return True
        except Exception as e:
            print(f"{Fore.RED}❌ Błąd zapisywania proxy: {str(e)}{Style.RESET_ALL}")
            return False
    
    def test_proxy(self, proxy, timeout=10):
        """Testuje czy proxy działa - ulepszona wersja"""
        #print(f"{Fore.CYAN}   🧪 Test: {proxy}{Style.RESET_ALL}")
        
        # Test 1: Podstawowe połączenie
        if not self.basic_connection_test(proxy):
            #print(f"   {Fore.RED}❌ Basic connection failed{Style.RESET_ALL}")
            return False
        
        # Test 2: HTTP request test
        if not self.http_test(proxy, timeout):
            #print(f"   {Fore.RED}❌ HTTP test failed{Style.RESET_ALL}")
            return False
        
        # Test 3: Selenium test (opcjonalny, można wyłączyć dla szybkości)
        # if not self.selenium_test(proxy):
        #     return False
        
        return True
    
    def basic_connection_test(self, proxy):
        """Test podstawowego połączenia"""
        try:
            parsed = urlparse(proxy)
            host = parsed.hostname
            port = parsed.port or (1080 if parsed.scheme == 'socks5' else 80)
            
            if not host or not port:
                return False
            
            # Test socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((host, port))
            sock.close()
            
            return result == 0
            
        except:
            return False
    
    def http_test(self, proxy, timeout=10):
        """Test HTTP request"""
        try:
            # Użyj różnych serwisów
            test_urls = random.sample(self.test_services, 2)
            
            for test_url in test_urls:
                try:
                    response = requests.get(
                        test_url,
                        proxies={'http': proxy, 'https': proxy},
                        headers={'User-Agent': self.ua.random},
                        timeout=timeout
                    )
                    
                    if response.status_code == 200:
                        return True
                        
                except requests.exceptions.ProxyError:
                    continue
                except requests.exceptions.ConnectTimeout:
                    continue
                except requests.exceptions.ConnectionError:
                    continue
                except:
                    continue
            
            return False
            
        except:
            return False
    
    def selenium_test(self, proxy):
        """Test z przeglądarką (dla YouTube)"""
        driver = None
        try:
            chrome_options = Options()
            chrome_options.add_argument('--headless=new')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument(f'--proxy-server={proxy}')
            
            # User agent
            chrome_options.add_argument(f'user-agent={self.ua.random}')
            
            # Inicjalizacja
            try:
                service = Service(ChromeDriverManager().install())
                driver = webdriver.Chrome(service=service, options=chrome_options)
            except:
                driver = webdriver.Chrome(options=chrome_options)
            
            driver.set_page_load_timeout(15)
            driver.get("https://www.youtube.com")
            time.sleep(2)
            
            # Sprawdź
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
    
    def find_working_proxy_continuous(self, max_test_time=300):
        """
        Szuka działającego proxy testując WSZYSTKIE z listy
        Kontynuuje aż znajdzie działające lub skończy się czas
        """
        if not self.proxies:
            print(f"{Fore.RED}❌ Brak proxy do testowania!{Style.RESET_ALL}")
            return None
        
        print(f"{Fore.CYAN}🔍 Szukam działającego proxy (testuję WSZYSTKIE {len(self.proxies)})...{Style.RESET_ALL}")
        print(f"   ⏱ Maksymalny czas: {max_test_time//60} minut{Style.RESET_ALL}")
        
        start_time = time.time()
        tested_count = 0
        working_found = []
        
        # Najpierw sprawdź cache (szybciej)
        if self.working_proxies:
            print(f"{Fore.CYAN}   🔄 Sprawdzam cache ({len(self.working_proxies)} proxy)...{Style.RESET_ALL}")
            
            for proxy in self.working_proxies:
                if time.time() - start_time > max_test_time:
                    break
                    
                tested_count += 1
                print(f"   [{tested_count}] 🧪 Test cache: {proxy}")
                
                if self.test_proxy(proxy):
                    print(f"      {Fore.GREEN}✅ Cache proxy działa!{Style.RESET_ALL}")
                    working_found.append(proxy)
                    
                    # Zapisz i zwróć
                    if working_found:
                        self.save_good_proxies(working_found)
                        self.working_proxies = working_found
                        return working_found[0]
        
        # Testuj wszystkie proxy z listy
        print(f"{Fore.CYAN}   🔄 Testuję wszystkie proxy z listy...{Style.RESET_ALL}")
        
        for i, proxy in enumerate(self.proxies):
            # Sprawdź czas
            if time.time() - start_time > max_test_time:
                print(f"{Fore.YELLOW}   ⏰ Koniec czasu testowania{Style.RESET_ALL}")
                break
            
            # Pomiń już przetestowane
            if proxy in working_found:
                continue
            
            tested_count += 1
            test_number = tested_count
            total_to_test = len(self.proxies)
            
            print(f"   [{test_number}/{total_to_test}] 🧪 Test: {proxy}")
            
            try:
                # Mierz czas odpowiedzi
                test_start = time.time()
                is_working = self.test_proxy(proxy, timeout=8)
                response_time = (time.time() - test_start) * 1000  # w milisekundach
                
                if is_working:
                    print(f"      {Fore.GREEN}✅ DZIAŁA ({response_time:.0f}ms){Style.RESET_ALL}")
                    working_found.append(proxy)
                    
                    # NATYCHMIAST zapisz i użyj
                    if working_found:
                        self.save_good_proxies(working_found)
                        self.working_proxies = working_found
                        return proxy  # Zwróć pierwsze działające
                else:
                    print(f"      {Fore.RED}❌ NIE DZIAŁA ({response_time:.0f}ms){Style.RESET_ALL}")
                    
            except Exception as e:
                print(f"      {Fore.RED}❌ BŁĄD: {str(e)[:30]}{Style.RESET_ALL}")
            
            # Krótka przerwa między testami
            if i < len(self.proxies) - 1:
                time.sleep(0.5)
        
        # Jeśli znaleziono jakieś działające
        if working_found:
            self.save_good_proxies(working_found)
            self.working_proxies = working_found
            print(f"{Fore.GREEN}✅ Znaleziono {len(working_found)} działających proxy{Style.RESET_ALL}")
            return working_found[0]
        else:
            print(f"{Fore.RED}❌ Nie znaleziono żadnych działających proxy{Style.RESET_ALL}")
            return None
    
    def get_next_proxy(self):
        """Zwraca następne działające proxy (dla rotacji)"""
        if not self.working_proxies:
            # Jeśli brak, znajdź nowe
            proxy = self.find_working_proxy_continuous()
            if proxy:
                return proxy
            else:
                # Jeśli nadal brak, użyj losowego
                if self.proxies:
                    return random.choice(self.proxies)
                else:
                    raise Exception("Brak dostępnych proxy")
        
        # Rotacja
        if self.current_index >= len(self.working_proxies):
            self.current_index = 0
        
        proxy = self.working_proxies[self.current_index]
        self.current_index += 1
        
        return proxy
    
    def find_all_working_proxies(self, max_time=600):
        """Testuje WSZYSTKIE proxy i zwraca listę działających"""
        if not self.proxies:
            return []
        
        print(f"{Fore.CYAN}🔍 Testuję WSZYSTKIE {len(self.proxies)} proxy...{Style.RESET_ALL}")
        print(f"   ⏱ Maksymalny czas: {max_time//60} minut{Style.RESET_ALL}")
        
        working = []
        failed = []
        start_time = time.time()
        
        for i, proxy in enumerate(self.proxies):
            # Sprawdź czas
            if time.time() - start_time > max_time:
                print(f"{Fore.YELLOW}   ⏰ Koniec czasu{Style.RESET_ALL}")
                break
            
            print(f"   [{i+1}/{len(self.proxies)}] 🧪 Test: {proxy}")
            
            test_start = time.time()
            try:
                if self.test_proxy(proxy):
                    response_time = (time.time() - test_start) * 1000
                    print(f"      {Fore.GREEN}✅ DZIAŁA ({response_time:.0f}ms){Style.RESET_ALL}")
                    working.append(proxy)
                else:
                    response_time = (time.time() - test_start) * 1000
                    print(f"      {Fore.RED}❌ NIE DZIAŁA ({response_time:.0f}ms){Style.RESET_ALL}")
                    failed.append(proxy)
                    
            except Exception as e:
                print(f"      {Fore.RED}❌ BŁĄD: {str(e)[:30]}{Style.RESET_ALL}")
                failed.append(proxy)
            
            # Przerwa
            if i < len(self.proxies) - 1:
                time.sleep(0.3)
        
        # Zapisz wyniki
        if working:
            self.save_good_proxies(working)
            self.working_proxies = working
        
        # Statystyki
        print(f"\n{Fore.CYAN}📊 PODSUMOWANIE:{Style.RESET_ALL}")
        print(f"   Przetestowano: {len(working) + len(failed)} proxy")
        print(f"   {Fore.GREEN}✅ Działające: {len(working)}{Style.RESET_ALL}")
        print(f"   {Fore.RED}❌ Nieudane: {len(failed)}{Style.RESET_ALL}")
        
        if working:
            success_rate = (len(working) / (len(working) + len(failed))) * 100
            print(f"   📈 Wskaźnik sukcesu: {success_rate:.1f}%")
        
        return working