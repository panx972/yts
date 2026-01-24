#!/usr/bin/env python3
"""
Skrypt do pobierania świeżych proxy z internetu
"""

import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime

def get_proxies_from_sslproxies():
    """Pobiera proxy z sslproxies.org"""
    print("🔍 Pobieram proxy z sslproxies.org...")
    proxies = []
    
    try:
        url = "https://www.sslproxies.org/"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Znajdź tabelę z proxy
        table = soup.find('table', {'id': 'proxylisttable'})
        if table:
            rows = table.find_all('tr')[1:51]  # Pierwsze 50 proxy
            for row in rows:
                cols = row.find_all('td')
                if len(cols) >= 2:
                    ip = cols[0].text.strip()
                    port = cols[1].text.strip()
                    if ip and port:
                        proxies.append(f"http://{ip}:{port}")
        
        print(f"   Znaleziono {len(proxies)} proxy")
        return proxies
        
    except Exception as e:
        print(f"❌ Błąd: {e}")
        return []

def get_proxies_from_free_proxy_list():
    """Pobiera proxy z free-proxy-list.net"""
    print("🔍 Pobieram proxy z free-proxy-list.net...")
    proxies = []
    
    try:
        url = "https://free-proxy-list.net/"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Znajdź textarea z proxy
        textarea = soup.find('textarea', class_='form-control')
        if textarea:
            lines = textarea.text.strip().split('\n')
            for line in lines[3:53]:  # Linie 4-53 (pomiń nagłówki)
                if re.match(r'\d+\.\d+\.\d+\.\d+:\d+', line):
                    proxies.append(f"http://{line}")
        
        print(f"   Znaleziono {len(proxies)} proxy")
        return proxies
        
    except Exception as e:
        print(f"❌ Błąd: {e}")
        return []

def save_proxies(proxies, filename='data/proxy.txt'):
    """Zapisuje proxy do pliku"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"# Świeże proxy pobrane automatycznie\n")
            f.write(f"# Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"# Źródło: sslproxies.org i free-proxy-list.net\n\n")
            
            for proxy in proxies:
                f.write(proxy + "\n")
        
        print(f"\n✅ Zapisano {len(proxies)} proxy do {filename}")
        print(f"📋 Pierwsze 5 proxy:")
        for i, proxy in enumerate(proxies[:5], 1):
            print(f"   {i}. {proxy}")
        
        return True
        
    except Exception as e:
        print(f"❌ Błąd zapisywania: {e}")
        return False

def test_few_proxies(proxies, count=5):
    """Testuje kilka proxy"""
    print(f"\n🧪 Testuję pierwsze {count} proxy...")
    
    import requests
    
    working = []
    for i, proxy in enumerate(proxies[:count], 1):
        print(f"   [{i}/{count}] Test: {proxy}...", end="")
        try:
            response = requests.get(
                'http://httpbin.org/ip',
                proxies={'http': proxy, 'https': proxy},
                timeout=10
            )
            if response.status_code == 200:
                print(" ✅ DZIAŁA")
                working.append(proxy)
            else:
                print(" ❌")
        except:
            print(" ❌")
    
    print(f"\n📊 Wynik testu: {len(working)}/{count} proxy działa")
    return working

if __name__ == "__main__":
    print("🔄 Pobieranie świeżych proxy z internetu...")
    print("=" * 50)
    
    # Pobierz proxy z różnych źródeł
    all_proxies = []
    
    proxies1 = get_proxies_from_sslproxies()
    all_proxies.extend(proxies1)
    
    proxies2 = get_proxies_from_free_proxy_list()
    all_proxies.extend(proxies2)
    
    # Usuń duplikaty
    all_proxies = list(dict.fromkeys(all_proxies))
    
    if all_proxies:
        print(f"\n📊 Łącznie znaleziono: {len(all_proxies)} unikalnych proxy")
        
        # Zapisz do pliku
        save_proxies(all_proxies)
        
        # Przeprowadź szybki test
        test_few_proxies(all_proxies, 5)
        
        print(f"\n🎯 Następne kroki:")
        print(f"1. Uruchom: python test_proxy_system.py")
        print(f"2. Sprawdź czy bot znajduje działające proxy")
        print(f"3. Jeśli nadal problem, spróbuj VPN zamiast proxy")
        
    else:
        print("❌ Nie udało się pobrać żadnych proxy!")
        print("\n💡 Alternatywne rozwiązania:")
        print("1. Użyj VPN i uruchom bota bez proxy")
        print("2. Kup prywatne proxy (bardziej stabilne)")
        print("3. Sprawdź swoje połączenie internetowe")