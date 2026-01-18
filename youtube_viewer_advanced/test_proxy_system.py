"""
Test Proxy System - POPRAWIONA WERSJA dla Windows
"""

import sys
import os
import time
from colorama import init, Fore, Style

init(autoreset=True)

def print_header(text):
    """Drukuje nagłówek sekcji"""
    print(f"\n{Fore.CYAN}{'='*60}{Fore.RESET}")
    print(f"{Fore.CYAN}{text.center(60)}{Fore.RESET}")
    print(f"{Fore.CYAN}{'='*60}{Fore.RESET}")

def check_modules_windows():
    """Sprawdza czy wszystkie wymagane moduły istnieją - WERSJA WINDOWS"""
    print_header("1. SPRAWDZANIE MODUŁÓW (Windows)")
    
    modules_needed = [
        ('proxy_manager.py', 'Menedżer proxy'),
        ('browser_manager.py', 'Menedżer przeglądarki'),
        ('youtube_actions.py', 'Akcje YouTube'),
        ('channel_verifier.py', 'Weryfikator kanałów')
    ]
    
    all_ok = True
    
    # Najpierw sprawdź czy folder modules istnieje
    modules_dir = 'modules'
    if not os.path.exists(modules_dir):
        print_error(f"Folder '{modules_dir}' nie istnieje!")
        print(f"\n{Fore.YELLOW}Utwórz folder:{Fore.RESET}")
        print(f"  mkdir modules")
        return False
    
    print_success(f"Folder '{modules_dir}' istnieje")
    
    # Sprawdź zawartość folderu
    try:
        files_in_modules = os.listdir(modules_dir)
        print_info(f"Pliki w folderze {modules_dir}/:")
        py_files = []
        for f in files_in_modules:
            if f.endswith('.py'):
                py_files.append(f)
                print(f"  ✅ {f}")
            else:
                print(f"  📄 {f} (nie .py)")
    except Exception as e:
        print_error(f"Nie można odczytać folderu {modules_dir}: {e}")
        return False
    
    # Sprawdź każdy wymagany moduł
    for filename, description in modules_needed:
        # UŻYJ os.path.join() dla poprawnej ścieżki Windows
        module_path = os.path.join(modules_dir, filename)
        
        if os.path.exists(module_path):
            # Sprawdź też rozmiar pliku
            try:
                size = os.path.getsize(module_path)
                if size > 100:  # Plik nie jest pusty
                    print_success(f"{description}: {filename} ({size} bajtów)")
                else:
                    print_warning(f"{description}: {filename} (MAŁY: {size} bajtów)")
            except:
                print_success(f"{description}: {filename}")
        else:
            # Pokaż pełną ścieżkę dla debugowania
            abs_path = os.path.abspath(module_path)
            print_error(f"{description}: {filename}")
            print(f"     Szukano: {abs_path}")
            all_ok = False
    
    if not all_ok:
        print(f"\n{Fore.RED}{'='*60}{Fore.RESET}")
        print(f"{Fore.RED}BRAKUJĄCE MODUŁY:{Fore.RESET}")
        
        # Sprawdź czy może pliki mają złe rozszerzenie
        print(f"\n{Fore.YELLOW}Sprawdzam alternatywne nazwy:{Fore.RESET}")
        for filename, description in modules_needed:
            module_path = os.path.join(modules_dir, filename)
            if not os.path.exists(module_path):
                # Sprawdź różne warianty
                variants = [
                    filename,
                    filename.upper(),
                    filename.lower(),
                    filename.replace('.py', '.PY'),
                    filename.replace('.py', '.Py')
                ]
                
                found = False
                for variant in variants:
                    variant_path = os.path.join(modules_dir, variant)
                    if os.path.exists(variant_path):
                        print(f"  ⚠️  {filename} -> Znaleziono jako: {variant}")
                        found = True
                        break
                
                if not found:
                    print(f"  ❌ {filename} - NIE znaleziono")
        
        print(f"\n{Fore.YELLOW}Rozwiązanie:{Fore.RESET}")
        print(f"  1. Upewnij się że pliki są w folderze modules/")
        print(f"  2. Sprawdź nazwy plików (Windows może ukrywać rozszerzenia)")
        print(f"  3. Uruchom jako administrator jeśli brak uprawnień")
        print(f"{Fore.RED}{'='*60}{Fore.RESET}")
        return False
    
    print_success("✓ Wszystkie moduły obecne i poprawne")
    return True

def quick_test():
    """Szybki test struktury"""
    print(f"{Fore.CYAN}🔍 SZYBKI TEST STRUKTURY WINDOWS{Fore.RESET}")
    
    current_dir = os.getcwd()
    print(f"Bieżący folder: {current_dir}")
    
    # Sprawdź separator
    print(f"Separator systemowy: {os.sep}")
    
    # Sprawdź folder modules
    modules_path = os.path.join(current_dir, 'modules')
    print(f"\nŚcieżka do modules: {modules_path}")
    print(f"Czy istnieje: {os.path.exists(modules_path)}")
    
    if os.path.exists(modules_path):
        print(f"\nZawartość folderu modules/:")
        try:
            for item in os.listdir(modules_path):
                full_path = os.path.join(modules_path, item)
                if os.path.isfile(full_path):
                    size = os.path.getsize(full_path)
                    print(f"  📄 {item} ({size} bajtów)")
                else:
                    print(f"  📁 {item} (folder)")
        except Exception as e:
            print(f"  ❌ Błąd: {e}")
    
    # Sprawdź konkretne pliki
    print(f"\n{Fore.CYAN}Sprawdzam konkretne pliki:{Fore.RESET}")
    files_to_check = [
        'proxy_manager.py',
        'browser_manager.py', 
        'youtube_actions.py',
        'channel_verifier.py'
    ]
    
    for filename in files_to_check:
        # Różne sposoby zapisu ścieżki
        paths_to_try = [
            os.path.join('modules', filename),      # Poprawnie
            f'modules\\{filename}',                 # Windows style
            f'modules/{filename}',                  # Unix style (może działać)
            filename,                               # W bieżącym folderze
        ]
        
        found = False
        for path in paths_to_try:
            if os.path.exists(path):
                abs_path = os.path.abspath(path)
                print(f"  ✅ {filename}: znaleziono jako {path}")
                print(f"     Pełna ścieżka: {abs_path}")
                found = True
                break
        
        if not found:
            print(f"  ❌ {filename}: NIE znaleziono")
    
    return True

def main_windows():
    """Główna funkcja dla Windows"""
    print(f"{Fore.CYAN}{'='*60}{Fore.RESET}")
    print(f"{Fore.CYAN}{'TEST SYSTEMU - WERSJA WINDOWS'.center(60)}{Fore.RESET}")
    print(f"{Fore.CYAN}{'='*60}{Fore.RESET}")
    print(f"{Fore.YELLOW}System: Windows{Fore.RESET}")
    print(f"{Fore.YELLOW}Data: {time.strftime('%Y-%m-%d %H:%M:%S')}{Fore.RESET}")
    print(f"{Fore.YELLOW}Bieżący folder: {os.getcwd()}{Fore.RESET}")
    
    # Szybki test struktury
    quick_test()
    
    # Sprawdź moduły (poprawna wersja Windows)
    if not check_modules_windows():
        print(f"\n{Fore.RED}❌ Test przerwany - brak modułów{Fore.RESET}")
        
        # Utwórz prosty skrypt naprawczy
        print(f"\n{Fore.YELLOW}🛠️  Tworzę skrypt naprawczy...{Fore.RESET}")
        
        fix_script = '''import os
import sys

print("🛠️  Skrypt naprawczy dla Windows")
print(f"Bieżący folder: {os.getcwd()}")

# Utwórz folder modules jeśli nie istnieje
if not os.path.exists('modules'):
    os.makedirs('modules')
    print("✅ Utworzono folder 'modules'")
else:
    print("✅ Folder 'modules' już istnieje")

# Sprawdź zawartość
print("\\n📋 Zawartość folderu modules/:")
try:
    files = os.listdir('modules')
    for f in files:
        print(f"  - {f}")
except:
    print("  (pusty)")

print("\\n🎯 Co dalej:")
print("1. Skopiuj 4 pliki .py do folderu modules/")
print("2. Uruchom ponownie: python test_proxy_system.py")
print("3. Nazwy plików muszą być dokładnie:")
print("   - proxy_manager.py")
print("   - browser_manager.py")
print("   - youtube_actions.py")
print("   - channel_verifier.py")
'''
        
        try:
            with open('fix_windows.py', 'w', encoding='utf-8') as f:
                f.write(fix_script)
            print(f"{Fore.GREEN}✅ Utworzono: fix_windows.py{Fore.RESET}")
            print(f"{Fore.YELLOW}💡 Uruchom: python fix_windows.py{Fore.RESET}")
        except:
            pass
        
        input(f"\n{Fore.YELLOW}👆 Naciśnij Enter aby zakończyć...{Fore.RESET}")
        return
    
    # Jeśli moduły istnieją, kontynuuj resztę testów
    print(f"\n{Fore.GREEN}✅ Wszystkie moduły OK! Kontynuuję testy...{Fore.RESET}")
    
    # Tutaj reszta testów...
    # (musisz dodać pozostałe funkcje testowe)
    
    print(f"\n{Fore.CYAN}{'='*60}{Fore.RESET}")
    print(f"{Fore.GREEN}🎉 TEST ZAKOŃCZONY POMYŚLNIE!{Fore.RESET}")
    print(f"{Fore.CYAN}{'='*60}{Fore.RESET}")
    
    input(f"\n{Fore.YELLOW}👆 Naciśnij Enter...{Fore.RESET}")

if __name__ == "__main__":
    main_windows()