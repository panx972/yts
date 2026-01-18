import os
import sys
import subprocess
import platform
from datetime import datetime
import requests
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

# ============================================================
# FUNKCJE POMOCNICZE
# ============================================================

def print_success(message):
    print(f"  ✅ {message}")

def print_error(message):
    print(f"  ❌ {message}")

def print_warning(message):
    print(f"  ⚠️  {message}")

def print_info(message):
    print(f"  ℹ️  {message}")

# ============================================================
# FUNKCJE DO OBSŁUGI PROXY
# ============================================================

def load_proxies_from_file(file_path=os.path.join("data", "proxy.txt")):
    """Ładuje listę proxy z pliku"""
    proxies = []
    
    if not os.path.exists(file_path):
        print_error(f"Plik {file_path} nie istnieje!")
        return proxies
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    proxies.append(line)
        
        print_success(f"Załadowano {len(proxies)} proxy z {file_path}")
        return proxies
    except Exception as e:
        print_error(f"Błąd odczytu pliku proxy: {e}")
        return []

def test_single_proxy(proxy, timeout=10, test_url="http://httpbin.org/ip"):
    """Testuje pojedyncze proxy"""
    proxies_config = {
        'http': proxy,
        'https': proxy
    }
    
    try:
        start_time = time.time()
        response = requests.get(
            test_url, 
            proxies=proxies_config,
            timeout=timeout,
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        )
        response_time = round((time.time() - start_time) * 1000, 2)
        
        if response.status_code == 200:
            return {
                'proxy': proxy,
                'status': 'working',
                'response_time': response_time,
                'status_code': response.status_code
            }
        else:
            return {
                'proxy': proxy,
                'status': 'failed',
                'response_time': response_time,
                'error': f"HTTP {response.status_code}"
            }
            
    except requests.exceptions.Timeout:
        return {
            'proxy': proxy,
            'status': 'timeout',
            'response_time': timeout * 1000,
            'error': f"Timeout ({timeout}s)"
        }
    except Exception as e:
        return {
            'proxy': proxy,
            'status': 'error',
            'response_time': 0,
            'error': str(e)
        }

def test_proxy_list(proxies, max_workers=5):
    """Testuje listę proxy wielowątkowo"""
    print_info(f"Rozpoczynam testowanie {len(proxies)} proxy...")
    
    working_proxies = []
    results = {
        'working': 0,
        'failed': 0,
        'timeout': 0,
        'error': 0,
        'total': len(proxies)
    }
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_proxy = {
            executor.submit(test_single_proxy, proxy): proxy 
            for proxy in proxies
        }
        
        for i, future in enumerate(as_completed(future_to_proxy), 1):
            proxy = future_to_proxy[future]
            result = future.result()
            
            progress = f"[{i}/{len(proxies)}]"
            
            if result['status'] == 'working':
                print_success(f"{progress} {proxy} - DZIAŁA ({result['response_time']}ms)")
                working_proxies.append(result)
                results['working'] += 1
            elif result['status'] == 'timeout':
                print_warning(f"{progress} {proxy} - TIMEOUT")
                results['timeout'] += 1
            else:
                print_error(f"{progress} {proxy} - BŁĄD: {result.get('error', 'unknown')}")
                results['failed'] += 1
    
    return working_proxies, results

def save_working_proxies(proxies, file_path=os.path.join("data", "good_proxy.txt")):
    """Zapisuje działające proxy do pliku"""
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            for proxy_data in proxies:
                proxy = proxy_data['proxy']
                response_time = proxy_data.get('response_time', 0)
                f.write(f"{proxy}  # response: {response_time}ms\n")
        
        print_success(f"Zapisano {len(proxies)} działających proxy do {file_path}")
        return True
    except Exception as e:
        print_error(f"Błąd zapisu pliku: {e}")
        return False

# ============================================================
# GŁÓWNA FUNKCJA
# ============================================================

def main():
    """Główna funkcja testowania proxy"""
    print("\n" + "="*60)
    print("TEST PROXY SYSTEM".center(60))
    print("="*60)
    
    # Sprawdź czy plik istnieje
    proxy_file = os.path.join("data", "proxy.txt")
    
    if not os.path.exists(proxy_file):
        print_error(f"Plik {proxy_file} nie istnieje!")
        print_info("Utwórz folder 'data' i plik 'proxy.txt'")
        return
    
    # Załaduj proxy
    proxies = load_proxies_from_file(proxy_file)
    
    if not proxies:
        print_error("Nie znaleziono proxy do testowania!")
        return
    
    print(f"\nZnaleziono {len(proxies)} proxy do przetestowania.")
    
    try:
        max_workers = int(input(f"Ile wątków użyć (1-20, domyślnie 5): ") or "5")
        max_workers = max(1, min(20, max_workers))
    except:
        max_workers = 5
    
    # Rozpocznij testowanie
    print("\n" + "-"*60)
    print("ROZPOCZĘCIE TESTOWANIA".center(60))
    print("-"*60)
    
    start_time = time.time()
    working_proxies, results = test_proxy_list(proxies, max_workers)
    total_time = time.time() - start_time
    
    # Wyświetl statystyki
    print("\n" + "="*60)
    print("WYNIKI TESTOWANIA".center(60))
    print("="*60)
    
    print_success(f"DZIAŁAJĄCE: {results['working']}/{results['total']}")
    print_warning(f"TIMEOUT: {results['timeout']}/{results['total']}")
    print_error(f"NIEDZIAŁAJĄCE: {results['failed'] + results['error']}/{results['total']}")
    print_info(f"Czas testów: {total_time:.2f} sekund")
    
    # Zapisz działające proxy
    if working_proxies:
        save_success = save_working_proxies(working_proxies)
        
        # Pokaż najlepsze proxy
        sorted_proxies = sorted(working_proxies, key=lambda x: x.get('response_time', 9999))
        
        print("\n" + "-"*60)
        print("NAJLEPSZE PROXY (najszybsze)".center(60))
        print("-"*60)
        
        for i, proxy_data in enumerate(sorted_proxies[:10], 1):
            proxy = proxy_data['proxy']
            rt = proxy_data.get('response_time', 0)
            print(f"{i:2}. {proxy} - {rt}ms")
        
        if save_success:
            print_success(f"\nPlik zapisany: data/good_proxy.txt")
    else:
        print_error("\nNie znaleziono żadnych działających proxy!")

# ============================================================
# URUCHOMIENIE
# ============================================================

if __name__ == "__main__":
    try:
        import requests
    except ImportError:
        print("❌ Brak biblioteki 'requests'")
        print("Zainstaluj: pip install requests")
        sys.exit(1)
    
    main()
    
    if platform.system() == "Windows":
        input("\nNaciśnij Enter aby zakończyć...")