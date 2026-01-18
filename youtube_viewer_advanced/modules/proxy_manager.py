import os
import random
import time
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

class SmartProxyManager:
    """Inteligentny manager proxy z testowaniem"""
    
    def __init__(self, proxy_file="data/proxy.txt"):
        self.proxy_file = proxy_file
        self.all_proxies = []
        self.working_proxies = []
        self.failed_proxies = []
        self.current_index = 0
        
        self.load_proxies()
        
        # Automatyczne testowanie przy starcie
        if self.all_proxies:
            print(f"🔍 Automatyczne testowanie {len(self.all_proxies)} proxy...")
            self.test_all_proxies_quick()
    
    def load_proxies(self):
        """Ładuje proxy z pliku"""
        if not os.path.exists(self.proxy_file):
            print(f"⚠️  Brak pliku {self.proxy_file}")
            print(f"ℹ️  Utwórz plik z listą proxy do przetestowania")
            return []
        
        try:
            with open(self.proxy_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        self.all_proxies.append(line)
            
            print(f"📁 Załadowano {len(self.all_proxies)} proxy do przetestowania")
            return self.all_proxies
            
        except Exception as e:
            print(f"❌ Błąd ładowania proxy: {e}")
            return []
    
    def test_single_proxy(self, proxy, timeout=5):
        """Testuje pojedyncze proxy"""
        try:
            # RÓŻNE strony do testu
            test_urls = [
                "http://httpbin.org/ip",  # Szybki test
                "https://www.google.com",  # Test HTTPS
                "https://www.youtube.com"  # Test YouTube (najważniejszy!)
            ]
            
            proxies = {
                'http': proxy,
                'https': proxy
            }
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
            
            start_time = time.time()
            
            # Testuj różne strony
            for i, test_url in enumerate(test_urls):
                try:
                    response = requests.get(
                        test_url,
                        proxies=proxies,
                        timeout=timeout,
                        headers=headers,
                        verify=False  # Wyłącz SSL verification dla testów
                    )
                    
                    if response.status_code != 200:
                        return {
                            'proxy': proxy,
                            'status': 'failed',
                            'error': f"HTTP {response.status_code} na {test_url}",
                            'response_time': round((time.time() - start_time) * 1000, 2)
                        }
                    
                    # Jeśli YouTube się ładuje - SUPER!
                    if "youtube.com" in test_url:
                        return {
                            'proxy': proxy,
                            'status': 'working',
                            'response_time': round((time.time() - start_time) * 1000, 2),
                            'can_access_yt': True
                        }
                        
                except requests.exceptions.Timeout:
                    return {
                        'proxy': proxy,
                        'status': 'timeout',
                        'error': f"Timeout na {test_url}",
                        'response_time': timeout * 1000
                    }
                except requests.exceptions.ConnectionError:
                    return {
                        'proxy': proxy,
                        'status': 'connection_error',
                        'error': f"Connection error na {test_url}",
                        'response_time': 0
                    }
                except Exception as e:
                    if i == len(test_urls) - 1:  # Ostatni test
                        return {
                            'proxy': proxy,
                            'status': 'error',
                            'error': str(e)[:100],
                            'response_time': 0
                        }
                    continue  # Próbuj następną stronę
            
            # Jeśli przeszło wszystkie testy
            return {
                'proxy': proxy,
                'status': 'working',
                'response_time': round((time.time() - start_time) * 1000, 2),
                'can_access_yt': False
            }
            
        except Exception as e:
            return {
                'proxy': proxy,
                'status': 'error',
                'error': str(e)[:100],
                'response_time': 0
            }
    
    def test_all_proxies_quick(self, max_workers=10, max_tests=50):
        """Szybkie testowanie wszystkich proxy"""
        if not self.all_proxies:
            print("ℹ️  Brak proxy do testowania")
            return
        
        print(f"🧪 Testowanie {min(len(self.all_proxies), max_tests)} proxy...")
        
        # Tylko pierwsze max_tests proxy (żeby nie czekać za długo)
        proxies_to_test = self.all_proxies[:max_tests]
        
        working = []
        failed = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Rozpocznij wszystkie testy
            future_to_proxy = {
                executor.submit(self.test_single_proxy, proxy, 5): proxy 
                for proxy in proxies_to_test
            }
            
            # Przetwarzaj wyniki
            for future in as_completed(future_to_proxy):
                proxy = future_to_proxy[future]
                result = future.result()
                
                if result['status'] == 'working':
                    working.append(result)
                    status = "YT OK" if result.get('can_access_yt', False) else "OK"
                    print(f"  ✅ {proxy[:40]:40} - {status} ({result['response_time']}ms)")
                else:
                    failed.append(result)
                    print(f"  ❌ {proxy[:40]:40} - {result.get('error', 'BŁĄD')}")
        
        # Zapisz wyniki
        self.working_proxies = [r['proxy'] for r in working]
        self.failed_proxies = [r['proxy'] for r in failed]
        
        print(f"\n📊 PODSUMOWANIE TESTOWANIA:")
        print(f"   ✅ DZIAŁAJĄCE: {len(self.working_proxies)}")
        print(f"   ❌ NIEDZIAŁAJĄCE: {len(self.failed_proxies)}")
        
        if self.working_proxies:
            print(f"   🎯 Skuteczność: {(len(self.working_proxies)/len(proxies_to_test)*100):.1f}%")
            # Zapisz działające proxy
            self.save_working_proxies()
        else:
            print("   ⚠️  Nie znaleziono żadnych działających proxy!")
            print("   ℹ️  Dodaj więcej proxy do pliku lub sprawdź połączenie")
    
    def save_working_proxies(self):
        """Zapisuje działające proxy do osobnego pliku"""
        try:
            working_file = "data/working_proxy.txt"
            with open(working_file, 'w', encoding='utf-8') as f:
                f.write(f"# Działające proxy - wygenerowano: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"# Liczba: {len(self.working_proxies)}\n\n")
                for proxy in self.working_proxies:
                    f.write(f"{proxy}\n")
            
            print(f"💾 Zapisano działające proxy do: {working_file}")
        except Exception as e:
            print(f"⚠️  Błąd zapisu: {e}")
    
    def get_next_proxy(self):
        """Zwraca następne DZIAŁAJĄCE proxy"""
        if not self.working_proxies:
            print("⚠️  Brak działających proxy")
            return None
        
        proxy = self.working_proxies[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.working_proxies)
        
        return proxy
    
    def mark_proxy_as_failed(self, proxy, reason=""):
        """Oznacza proxy jako niedziałające"""
        if proxy in self.working_proxies:
            self.working_proxies.remove(proxy)
            self.failed_proxies.append(proxy)
            
            print(f"🗑️  Proxy oznaczone jako nieudane: {proxy[:50]}")
            if reason:
                print(f"   Powód: {reason}")
            
            return True
        return False
    
    def has_proxies(self):
        """Czy są dostępne działające proxy?"""
        return len(self.working_proxies) > 0
    
    def count(self):
        """Liczba działających proxy"""
        return len(self.working_proxies)
    
    def get_proxy_stats(self):
        """Statystyki proxy"""
        return {
            'total_loaded': len(self.all_proxies),
            'working': len(self.working_proxies),
            'failed': len(self.failed_proxies),
            'success_rate': (len(self.working_proxies) / len(self.all_proxies) * 100) if self.all_proxies else 0
        }

ProxyManager = SmartProxyManager