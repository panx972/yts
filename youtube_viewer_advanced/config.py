"""
Konfiguracja YouTube Viewer Advanced
"""

CONFIG = {
    # ============ USTAWIENIA GŁÓWNE ============
    'max_concurrent_channels': 3,      # Maks. równoległych kanałów (OKNA/THREADS!)
    'threads': 5,                      # Liczba wątków
    
    # ============ USTAWIENIA OGLĄDANIA ============
    'max_videos_per_channel': 5,       # Maks. filmów z kanału
    'min_watch_time': 30,              # Min. czas oglądania
    'max_watch_time': 120,             # Max. czas oglądania
    'view_duration_min': 30,           # Alias dla min_watch_time
    'view_duration_max': 180,          # Alias dla max_watch_time
    'min_break_between_videos': 10,    # Min. przerwa między filmami
    'max_break_between_videos': 30,    # Max. przerwa między filmami
    
    # ============ USTAWIENIA PROXY ============
    'use_proxy': False,                # Czy używać proxy
    'use_proxy_rotation': True,        # Rotacja proxy
    'max_proxy_retries': 5,            # Maks. prób proxy
    'max_proxy_attempts': 15,          # Maks. prób znalezienia proxy
    'max_proxies_to_fetch': 1000,      # Maks. proxy do pobrania
    'proxy_test_timeout': 10,          # Timeout testu proxy
    'test_proxy_timeout': 15,          # Inny timeout proxy
    
    # ============ USTAWIENIA PRZEGLĄDARKI ============
    'headless_mode': False,            # Tryb headless
    'random_user_agent': True,         # Losowy user agent
    'window_width_min': 1200,          # Min. szerokość okna
    'window_width_max': 1920,          # Max. szerokość okna
    'window_height_min': 800,          # Min. wysokość okna
    'window_height_max': 1080,         # Max. wysokość okna
    'use_fingerprinting': True,        # Fingerprint (anty-detekcja)
    'max_profiles': 10,                # Maks. profili
    
    # ============ USTAWIENIA FUNKCJI ============
    'enable_likes': True,              # Czy lajkować
    'enable_scroll': True,             # Czy scrollować
    'organic_search': True,            # Wyszukiwanie organiczne
    
    # ============ USTAWIENIA LOGOWANIA ============
    'log_level': 'INFO',               # Poziom logowania
    'save_reports': True,              # Czy zapisywać raporty
    
    # ============ NOWE USTAWIENIA (dodaj) ============
    'max_views_per_session': 50,       # Maks. oglądnięć na sesję
    'auto_restart_after': 100,         # Auto-restart po X sesjach
    'proxy_rotation_every': 10,        # Rotacja proxy co X sesji
}

def save_config():
    """Zapisuje konfigurację do pliku JSON"""
    import json
    try:
        # Dodaj aliasy aby były spójne
        CONFIG['view_duration_min'] = CONFIG['min_watch_time']
        CONFIG['view_duration_max'] = CONFIG['max_watch_time']
        
        with open('data/config.json', 'w', encoding='utf-8') as f:
            json.dump(CONFIG, f, indent=4, ensure_ascii=False)
        print("✅ Zapisano konfigurację")
        return True
    except Exception as e:
        print(f"❌ Błąd zapisywania konfiguracji: {str(e)}")
        return False

def load_config():
    """Wczytuje konfigurację z pliku JSON i ujednolica klucze"""
    import json
    import os
    
    config_file = 'data/config.json'
    
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                loaded_config = json.load(f)
            
            # UJEDNOLICANIE KONTROWERSYJNYCH KLUCZY:
            # 1. Jeśli w JSON jest threads, ale nie ma max_concurrent_channels
            if 'threads' in loaded_config and 'max_concurrent_channels' not in loaded_config:
                CONFIG['max_concurrent_channels'] = loaded_config['threads']
            
            # 2. Sync watch_time z view_duration
            if 'min_watch_time' in loaded_config:
                CONFIG['view_duration_min'] = loaded_config['min_watch_time']
            if 'max_watch_time' in loaded_config:
                CONFIG['view_duration_max'] = loaded_config['max_watch_time']
            
            # 3. Sync view_duration z watch_time (odwrotnie)
            if 'view_duration_min' in loaded_config:
                CONFIG['min_watch_time'] = loaded_config['view_duration_min']
            if 'view_duration_max' in loaded_config:
                CONFIG['max_watch_time'] = loaded_config['view_duration_max']
            
            # Aktualizuj resztę konfiguracji
            for key in loaded_config:
                CONFIG[key] = loaded_config[key]
            
            print("✅ Wczytano i zsynchronizowano konfigurację")
            return True
        except Exception as e:
            print(f"⚠ Błąd wczytywania konfiguracji: {str(e)}")
            return False
    else:
        print("⚠ Brak pliku konfiguracyjnego, tworzę domyślny...")
        save_config()  # Utwórz domyślny plik
        return False

def get_config(key, default=None):
    """Pobiera wartość z konfiguracji (z obsługą aliasów)"""
    
    # MAPOWANIE ALIASÓW - jeśli szukasz jednego klucza, a jest inny
    alias_map = {
        # Stare klucze -> nowe klucze
        'threads': 'max_concurrent_channels',
        'view_duration_min': 'min_watch_time',
        'view_duration_max': 'max_watch_time',
        'max_watch_time': 'view_duration_max',
        'min_watch_time': 'view_duration_min',
    }
    
    # Sprawdź bezpośrednio
    if key in CONFIG:
        return CONFIG[key]
    
    # Sprawdź alias
    if key in alias_map and alias_map[key] in CONFIG:
        return CONFIG[alias_map[key]]
    
    # Sprawdź odwrotne aliasy
    for alias, original in alias_map.items():
        if original == key and alias in CONFIG:
            return CONFIG[alias]
    
    return default

def set_config(key, value):
    """Ustawia wartość w konfiguracji (z synchronizacją aliasów)"""
    CONFIG[key] = value
    
    # SYNCHRONIZACJA ALIASÓW:
    if key == 'min_watch_time':
        CONFIG['view_duration_min'] = value
    elif key == 'max_watch_time':
        CONFIG['view_duration_max'] = value
    elif key == 'view_duration_min':
        CONFIG['min_watch_time'] = value
    elif key == 'view_duration_max':
        CONFIG['max_watch_time'] = value
    elif key == 'max_concurrent_channels':
        CONFIG['threads'] = value
    elif key == 'threads':
        CONFIG['max_concurrent_channels'] = value
    
    save_config()
    return True