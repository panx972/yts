"""
Konfiguracja YouTube Viewer Advanced
"""

CONFIG = {
    # Ustawienia ogólne
    'max_concurrent_channels': 3,      # Maksymalna liczba równoległych kanałów
    'max_proxy_attempts': 15,          # Maksymalna liczba prób znalezienia proxy
    
    # Ustawienia oglądania filmów
    'max_videos_per_channel': 5,       # Maksymalna liczba filmów do obejrzenia z kanału
    'min_watch_time': 30,              # Minimalny czas oglądania (sekundy)
    'max_watch_time': 120,             # Maksymalny czas oglądania (sekundy)
    'min_break_between_videos': 10,    # Minimalna przerwa między filmami (sekundy)
    'max_break_between_videos': 30,    # Maksymalna przerwa między filmami (sekundy)
    
    # Ustawienia proxy
    'use_proxy': True,                 # Czy używać proxy (True/False)
    'proxy_test_timeout': 10,          # Timeout testu proxy (sekundy)
    
    # Ustawienia przeglądarki
    'headless_mode': False,            # Tryb headless (bez GUI)
    'random_user_agent': True,         # Losowy user agent
    'window_width_min': 1200,          # Minimalna szerokość okna
    'window_width_max': 1920,          # Maksymalna szerokość okna
    'window_height_min': 800,          # Minimalna wysokość okna
    'window_height_max': 1080,         # Maksymalna wysokość okna
    
    # Ustawienia logowania
    'log_level': 'INFO',               # Poziom logowania (DEBUG, INFO, WARNING, ERROR)
    'save_reports': True,              # Czy zapisywać raporty
}

def save_config():
    """Zapisuje konfigurację do pliku"""
    import json
    try:
        with open('data/config.json', 'w', encoding='utf-8') as f:
            json.dump(CONFIG, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"❌ Błąd zapisywania konfiguracji: {str(e)}")
        return False

def load_config():
    """Wczytuje konfigurację z pliku"""
    import json
    import os
    
    config_file = 'data/config.json'
    
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                loaded_config = json.load(f)
            
            # Aktualizuj domyślną konfigurację
            CONFIG.update(loaded_config)
            print("✅ Wczytano konfigurację z pliku")
            return True
        except Exception as e:
            print(f"⚠ Błąd wczytywania konfiguracji: {str(e)}")
            return False
    else:
        print("⚠ Brak pliku konfiguracyjnego, używam domyślnych ustawień")
        save_config()  # Utwórz domyślny plik
        return False

def get_config(key, default=None):
    """Pobiera wartość z konfiguracji"""
    return CONFIG.get(key, default)

def set_config(key, value):
    """Ustawia wartość w konfiguracji"""
    CONFIG[key] = value
    save_config()
    return True