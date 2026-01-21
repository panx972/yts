#!/usr/bin/env python3
"""
Test systemu proxy - KOMPLETNE testowanie WSZYSTKICH proxy
"""

import os
import sys
import time
from colorama import init, Fore, Style

init(autoreset=True)
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

from proxy_manager import ProxyManager

def main():
    print(f"{Fore.CYAN}" + "="*70)
    print("🧪 SYSTEM TESTOWANIA PROXY - TESTUJE WSZYSTKIE PROXY")
    print("="*70 + f"{Style.RESET_ALL}")
    
    pm = ProxyManager()
    
    # Test 1: Sprawdź ile proxy załadowano
    print(f"\n{Fore.YELLOW}[1] SPRAWDZANIE LISTY PROXY{Style.RESET_ALL}")
    
    if not pm.proxies:
        print(f"   {Fore.RED}❌ BRAK PROXY W PLIKU data/proxy.txt!{Style.RESET_ALL}")
        print(f"   Uruchom: python get_fresh_proxies.py")
        return
    
    print(f"   ✅ Załadowano {len(pm.proxies)} proxy z pliku")
    print(f"   Pierwsze 5: {pm.proxies[:5]}")
    print(f"   Ostatnie 5: {pm.proxies[-5:]}")
    
    # Test 2: Testuj WSZYSTKIE proxy
    print(f"\n{Fore.YELLOW}[2] TESTOWANIE WSZYSTKICH {len(pm.proxies)} PROXY{Style.RESET_ALL}")
    print(f"   Rozpoczynam kompleksowe testowanie...")
    
    start_total = time.time()
    working_proxies = pm.find_all_working_proxies()
    total_time = time.time() - start_total
    
    # Test 3: Wyniki
    print(f"\n{Fore.YELLOW}[3] ANALIZA WYNIKÓW{Style.RESET_ALL}")
    
    if working_proxies:
        print(f"   {Fore.GREEN}✅ Znaleziono {len(working_proxies)} działających proxy{Style.RESET_ALL}")
        
        # Test rotacji
        print(f"\n   🔄 Test rotacji proxy:")
        pm.current_index = 0
        pm.working_proxies = working_proxies
        
        for i in range(min(5, len(working_proxies))):
            proxy = pm.get_next_proxy()
            print(f"      {i+1}. {proxy}")
        
        print(f"\n   📊 Przykłady działających proxy:")
        for i, proxy in enumerate(working_proxies[:10], 1):
            print(f"      {i:2d}. {proxy}")
        
        if len(working_proxies) > 10:
            print(f"      ... i {len(working_proxies)-10} więcej")
    else:
        print(f"   {Fore.RED}❌ Nie znaleziono żadnych działających proxy!{Style.RESET_ALL}")
        print(f"   {Fore.YELLOW}💡 Spróbuj:")
        print(f"   1. Uruchom ponownie: python get_fresh_proxies.py")
        print(f"   2. Sprawdź połączenie internetowe")
        print(f"   3. Użyj VPN i spróbuj bez proxy")
    
    # Statystyki
    print(f"\n{Fore.YELLOW}[4] STATYSTYKI{Style.RESET_ALL}")
    print(f"   Czas testowania: {total_time:.1f}s")
    print(f"   Średnio na proxy: {total_time/len(pm.proxies):.1f}s")
    
    if working_proxies:
        success_rate = (len(working_proxies) / len(pm.proxies)) * 100
        print(f"   Wskaźnik sukcesu: {Fore.CYAN}{success_rate:.1f}%{Style.RESET_ALL}")
    
    print(f"\n{Fore.GREEN}✅ Test zakończony!{Style.RESET_ALL}")
    print(f"📁 Pliki z wynikami:")
    print(f"   - data/good_proxy.txt - działające proxy")
    print(f"   - data/proxy_full_report.txt - pełny raport")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}⏹️ Przerwano przez użytkownika{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}❌ Błąd: {str(e)}{Style.RESET_ALL}")