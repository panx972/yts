"""
Proxy Manager - Zaawansowany system zarządzania proxy
"""

import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import os
import socket
import random
from colorama import Fore, Style


class ProxyManager:
    def __init__(self):
        self.proxy_sources = [
            'https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all',
            'https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt',
            'https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/http.txt',
            'https://raw.githubusercontent.com/hookzof/socks5_list/master/proxy.txt',
            'https://raw.githubusercontent.com/roosterkid/openproxylist/main/HTTPS_RAW.txt',
            'https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt',
        ]
        self.working_proxies_cache = []
        self.last_cache_update = 0
    
    def clean_proxy(self, proxy):
        """Czyści proxy z formatu IP:PORT|type do IP:PORT"""
        if not proxy:
            return ""
        
        proxy = str(proxy).strip()
        if '|' in proxy:
            proxy = proxy.split('|')[0].strip()
        
        protocols = ['http://', 'https://', 'socks4://', 'socks5://']
        for protocol in protocols:
            if proxy.startswith(protocol):
                proxy = proxy[len(protocol):]
        
        return proxy
    
    def is_valid_proxy_format(self, proxy):
        """Sprawdza czy proxy ma prawidłowy format"""
        proxy = self.clean_proxy(proxy)
        
        if not proxy:
            return False
        
        if ':' not in proxy:
            return False
        
        parts = proxy.split(':')
        
        if len(parts) == 2:  # IP:PORT
            ip, port = parts
            try:
                port_int = int(port)
                if 1 <= port_int <= 65535:
                    return True
            except:
                return False
        
        elif len(parts) == 4:  # IP:PORT:USER:PASS
            ip, port, user, password = parts
            try:
                port_int = int(port)
                if port_int and user and password:
                    return True
            except:
                return False
        
        return False
    
    def test_single_proxy_socket(self, proxy, timeout=3):
        """Szybki test socket"""
        try:
            clean_proxy = self.clean_proxy(proxy)
            if not clean_proxy:
                return None
            
            ip, port = clean_proxy.split(':')
            port = int(port)
            
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            
            start_time = time.time()
            result = sock.connect_ex((ip, port))
            elapsed = time.time() - start_time
            
            sock.close()
            
            if result == 0:
                return {'proxy': proxy, 'time': elapsed}
            return None
                
        except:
            return None
    
    def test_single_proxy_http(self, proxy, timeout=5):
        """Test HTTP"""
        try:
            clean_proxy = self.clean_proxy(proxy)
            if not clean_proxy:
                return None
            
            test_urls = [
                "http://httpbin.org/ip",
                "http://api.ipify.org?format=json",
                "http://icanhazip.com",
            ]
            
            proxy_dict = {'http': f'http://{clean_proxy}', 'https': f'http://{clean_proxy}'}
            headers = {'User-Agent': 'Mozilla/5.0'}
            
            for test_url in test_urls:
                try:
                    start_time = time.time()
                    response = requests.get(test_url, proxies=proxy_dict, headers=headers, timeout=timeout)
                    elapsed = time.time() - start_time
                    
                    if response.status_code == 200:
                        content = response.text.strip()
                        if content and ('.' in content or ':' in content):
                            return {
                                'proxy': proxy,
                                'time': elapsed,
                                'response_time': elapsed
                            }
                except:
                    continue
            
            return None
                
        except:
            return None
    
    def test_proxy_comprehensive(self, proxy, timeout=5):
        """Kompleksowy test proxy"""
        socket_result = self.test_single_proxy_socket(proxy, timeout=2)
        if not socket_result:
            return None
        
        http_result = self.test_single_proxy_http(proxy, timeout=timeout)
        if http_result:
            return http_result
        
        return None
    
    def get_working_proxy(self, proxies, max_attempts=10, timeout=5):
        """Zwraca pierwsze działające proxy"""
        if not proxies:
            return None
        
        print(f"{Fore.CYAN}🔍 Szukam działającego proxy...{Fore.RESET}")
        
        proxies_to_test = proxies[:min(max_attempts * 2, len(proxies))]
        
        for i, proxy in enumerate(proxies_to_test, 1):
            print(f"{Fore.CYAN}  [{i}/{len(proxies_to_test)}] {proxy[:40]}...{Fore.RESET}")
            
            result = self.test_proxy_comprehensive(proxy, timeout=timeout)
            if result:
                print(f"{Fore.GREEN}🎯 Znaleziono: {proxy}{Fore.RESET}")
                self.working_proxies_cache.append({'proxy': proxy, 'time': time.time()})
                self.last_cache_update = time.time()
                return proxy
            
            time.sleep(0.1)
        
        print(f"{Fore.YELLOW}⚠️  Brak działających proxy{Fore.RESET}")
        return None
    
    def test_proxies_batch(self, proxies, max_workers=10, timeout=5):
        """Testuje wiele proxy"""
        if not proxies:
            return []
        
        total = len(proxies)
        print(f"{Fore.CYAN}🧪 Testuję {total} proxy...{Fore.RESET}")
        
        good_proxies = []
        
        def test_wrapper(proxy):
            result = self.test_proxy_comprehensive(proxy, timeout=timeout)
            return result
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(test_wrapper, proxy): proxy for proxy in proxies}
            
            for i, future in enumerate(as_completed(futures), 1):
                if i % 10 == 0:
                    print(f"{Fore.CYAN}📊 {i}/{total} - Dobre: {len(good_proxies)}{Fore.RESET}")
                
                result = future.result()
                if result:
                    good_proxies.append(result['proxy'])
        
        print(f"{Fore.GREEN}📊 Znaleziono {len(good_proxies)}/{total} działających{Fore.RESET}")
        return good_proxies
    
    def fetch_proxies(self, max_proxies=500):
        """Pobiera proxy"""
        all_proxies = set()
        
        print(f"{Fore.CYAN}📥 Pobieram proxy...{Fore.RESET}")
        
        for source_idx, source in enumerate(self.proxy_sources, 1):
            try:
                headers = {'User-Agent': 'Mozilla/5.0'}
                response = requests.get(source, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    proxies = response.text.split('\n')
                    added = 0
                    
                    for proxy in proxies:
                        proxy = proxy.strip()
                        if proxy and self.is_valid_proxy_format(proxy):
                            all_proxies.add(proxy)
                            added += 1
                    
                    if added > 0:
                        print(f"{Fore.GREEN}✅ Źródło {source_idx}: {added} proxy{Fore.RESET}")
                    
                    if len(all_proxies) >= max_proxies:
                        break
                        
            except:
                continue
        
        proxies_list = list(all_proxies)[:max_proxies]
        print(f"{Fore.GREEN}📊 Pobrano {len(proxies_list)} proxy{Fore.RESET}")
        return proxies_list
    
    def save_proxies(self, proxies, filename):
        """Zapisuje proxy do pliku"""
        try:
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            
            with open(filename, 'w', encoding='utf-8') as f:
                for proxy in proxies:
                    f.write(f"{proxy}\n")
            
            print(f"{Fore.GREEN}💾 Zapisano {len(proxies)} proxy{Fore.RESET}")
            return True
            
        except Exception as e:
            print(f"{Fore.RED}❌ Błąd zapisu: {e}{Fore.RESET}")
            return False
    
    def load_proxies(self, filename):
        """Ładuje proxy z pliku"""
        proxies = []
        
        if not os.path.exists(filename):
            return proxies
        
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and self.is_valid_proxy_format(line):
                        proxies.append(line)
            
            return proxies
            
        except:
            return []
    
    def load_good_proxies(self, filename):
        """Ładuje działające proxy"""
        return self.load_proxies(filename)