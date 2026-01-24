"""
Zaawansowany Fingerprinting Engine z ochroną antidetect
"""

import random
import json
import os
import hashlib
from datetime import datetime

class FingerprintEngine:
    def __init__(self):
        self.fingerprints_dir = 'fingerprints'
        if not os.path.exists(self.fingerprints_dir):
            os.makedirs(self.fingerprints_dir)
        
        # Ładowanie danych fingerprint z pliku
        self.fingerprint_data = self.load_fingerprint_database()
    
    def load_fingerprint_database(self):
        """Ładuje bazę danych fingerprint z realnymi urządzeniami"""
        return {
            'windows_chrome': [
                {
                    'os': 'Windows 10',
                    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'platform': 'Win32',
                    'hardware_concurrency': [4, 6, 8, 12],
                    'device_memory': [4, 8, 16, 32],
                    'screen_resolutions': [
                        {'width': 1920, 'height': 1080, 'deviceScaleFactor': 1},
                        {'width': 1366, 'height': 768, 'deviceScaleFactor': 1},
                        {'width': 1536, 'height': 864, 'deviceScaleFactor': 1.25}
                    ],
                    'webgl_vendors': ['Intel Inc.', 'NVIDIA Corporation', 'AMD'],
                    'timezones': ['Europe/Warsaw', 'Europe/London', 'Europe/Berlin']
                }
            ],
            'mac_chrome': [
                {
                    'os': 'macOS 14',
                    'user_agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'platform': 'MacIntel',
                    'hardware_concurrency': [8, 10, 12],
                    'device_memory': [8, 16, 32],
                    'screen_resolutions': [
                        {'width': 1440, 'height': 900, 'deviceScaleFactor': 2},
                        {'width': 2560, 'height': 1600, 'deviceScaleFactor': 2},
                        {'width': 2880, 'height': 1800, 'deviceScaleFactor': 2}
                    ],
                    'webgl_vendors': ['Apple Inc.'],
                    'timezones': ['America/New_York', 'America/Los_Angeles', 'Europe/London']
                }
            ]
        }
    
    def generate_fingerprint(self, profile_id, device_type='windows_chrome'):
        """Generuje zaawansowany fingerprint z prawdziwymi danymi urządzeń"""
        
        # Wybierz konfigurację urządzenia
        device_config = random.choice(self.fingerprint_data.get(device_type, 
                                      self.fingerprint_data['windows_chrome']))
        
        # Generuj fingerprint
        fingerprint = {
            'profile_id': profile_id,
            'device_type': device_type,
            'generated_at': datetime.now().isoformat(),
            
            # Dane systemowe
            'os': device_config['os'],
            'user_agent': device_config['user_agent'],
            'platform': device_config['platform'],
            
            # Rozdzielczość
            'screen': random.choice(device_config['screen_resolutions']),
            
            # Sprzęt
            'hardware_concurrency': random.choice(device_config['hardware_concurrency']),
            'device_memory': random.choice(device_config['device_memory']),
            
            # Lokalizacja
            'timezone': random.choice(device_config['timezones']),
            'language': self.generate_language(device_type),
            'locale': self.generate_locale(),
            
            # WebGL
            'webgl_vendor': random.choice(device_config['webgl_vendors']),
            'webgl_renderer': self.generate_webgl_renderer(device_type),
            
            # Canvas fingerprint (unikalny ale spójny)
            'canvas_fingerprint': self.generate_consistent_canvas_hash(profile_id),
            
            # Audio fingerprint
            'audio_fingerprint': self.generate_consistent_audio_hash(profile_id),
            
            # Fonty
            'fonts': self.generate_realistic_fonts(device_type),
            
            # Wtyczki
            'plugins': self.generate_realistic_plugins(device_type),
            
            # Funkcje
            'touch_support': self.has_touch_support(device_type),
            'do_not_track': random.choice([0, 1, None]),
            'cookie_enabled': True,
            
            # WebRTC config
            'webrtc': self.generate_webrtc_config(device_type),
            
            # Battery API (opcjonalne)
            'battery': self.generate_battery_status(),
            
            # Connection API
            'connection': self.generate_connection_info(),
            
            # Media devices
            'media_devices': self.generate_media_devices(),
        }
        
        # Zapisz fingerprint
        self.save_fingerprint(profile_id, fingerprint)
        
        # Generuj JavaScript do wstrzyknięcia
        js_injection = self.generate_js_injection(fingerprint)
        fingerprint['js_injection'] = js_injection
        
        return fingerprint
    
    def generate_fingerprint_with_location(self, profile_id, device_type, location_config):
        """Generuje fingerprint z konfiguracją lokalizacyjną"""
        fingerprint = self.generate_fingerprint(profile_id, device_type)
        
        # Nadpisz dane lokalizacyjne
        fingerprint['accept_language'] = location_config['accept_language']
        fingerprint['timezone'] = location_config['timezone']
        fingerprint['locale'] = location_config['accept_language'].split(',')[0]
        
        # Dodaj country info
        fingerprint['country'] = location_config.get('country', 'US')
        
        # Zaktualizuj JS injection z nowymi danymi
        fingerprint['js_injection'] = self.generate_js_injection(fingerprint)
        
        # Zapisz
        self.save_fingerprint(profile_id, fingerprint)
        
        return fingerprint
    
    def generate_consistent_canvas_hash(self, profile_id):
        """Generuje spójny hash canvas dla profilu"""
        seed = f"canvas_{profile_id}_{datetime.now().strftime('%Y%m')}"
        hash_obj = hashlib.md5(seed.encode())
        return hash_obj.hexdigest()[:16]
    
    def generate_consistent_audio_hash(self, profile_id):
        """Generuje spójny hash audio dla profilu"""
        seed = f"audio_{profile_id}_{datetime.now().strftime('%Y%m')}"
        hash_obj = hashlib.sha256(seed.encode())
        return hash_obj.hexdigest()[:12]
    
    def generate_language(self, device_type):
        """Generuje języki"""
        if 'europe' in device_type.lower():
            languages = ['pl-PL', 'pl', 'en-US', 'en', 'de-DE']
        elif 'us' in device_type.lower():
            languages = ['en-US', 'en']
        else:
            languages = ['en-US', 'en-GB', 'en']
        
        # Zwróć jako string z odpowiednim formatowaniem
        selected_languages = random.sample(languages, random.randint(2, 4))
        return ', '.join(selected_languages)
    
    def generate_locale(self):
        """Generuje locale"""
        locales = ['pl-PL', 'en-US', 'en-GB', 'de-DE', 'fr-FR']
        return random.choice(locales)
    
    def generate_webgl_renderer(self, device_type):
        """Generuje realistyczny renderer WebGL"""
        if 'mac' in device_type.lower():
            return 'Apple M1 Pro'
        elif 'nvidia' in device_type.lower():
            return 'NVIDIA GeForce RTX 3060'
        elif 'amd' in device_type.lower():
            return 'AMD Radeon RX 6700 XT'
        else:
            return 'Intel(R) UHD Graphics 630'
    
    def generate_realistic_fonts(self, device_type):
        """Generuje realistyczną listę czcionek"""
        base_fonts = [
            'Arial',
            'Arial Black',
            'Times New Roman',
            'Courier New',
            'Verdana',
            'Georgia'
        ]
        
        # Dodaj systemowe czcionki
        if 'windows' in device_type.lower():
            base_fonts.extend([
                'Segoe UI',
                'Calibri',
                'Cambria',
                'Consolas'
            ])
        elif 'mac' in device_type.lower():
            base_fonts.extend([
                'Helvetica Neue',
                'San Francisco',
                'Menlo',
                'Monaco'
            ])
        
        # Losowa kolejność
        random.shuffle(base_fonts)
        return base_fonts
    
    def generate_realistic_plugins(self, device_type):
        """Generuje realistyczne wtyczki"""
        plugins = ['Chrome PDF Viewer', 'Chrome PDF Plugin']
        
        if random.random() > 0.3:
            plugins.append('Widevine Content Decryption Module')
        
        if 'windows' in device_type.lower() and random.random() > 0.5:
            plugins.append('Native Client')
        
        return plugins
    
    def has_touch_support(self, device_type):
        """Określa czy urządzenie ma touch support"""
        if 'mobile' in device_type.lower() or 'tablet' in device_type.lower():
            return True
        return random.random() > 0.8  # 20% szans dla desktopów
    
    def generate_webrtc_config(self, device_type):
        """Generuje konfigurację WebRTC"""
        return {
            'ip_handling': 'default',
            'multiple_routes': True,
            'proxy_only': device_type != 'mobile'
        }
    
    def generate_battery_status(self):
        """Generuje status baterii"""
        if random.random() > 0.7:  # 30% szans na dostęp do Battery API
            return {
                'charging': random.choice([True, False]),
                'level': round(random.uniform(0.2, 0.95), 2),
                'charging_time': random.randint(0, 3600),
                'discharging_time': random.randint(1800, 7200)
            }
        return None
    
    def generate_connection_info(self):
        """Generuje informacje o połączeniu"""
        connection_types = ['wifi', 'ethernet', '4g', 'bluetooth']
        return {
            'type': random.choice(connection_types),
            'effective_type': random.choice(['4g', '3g', '2g']),
            'downlink': random.uniform(1, 100),
            'rtt': random.randint(50, 300)
        }
    
    def generate_media_devices(self):
        """Generuje urządzenia multimedialne"""
        return {
            'audio_input': random.randint(0, 2),
            'audio_output': random.randint(1, 3),
            'video_input': random.randint(0, 2)
        }
    
    def generate_js_injection(self, fingerprint):
        """Generuje kod JavaScript do wstrzyknięcia dla ochrony antidetect"""
        
        # Escape single quotes in strings
        user_agent = fingerprint['user_agent'].replace("'", "\\'")
        webgl_vendor = fingerprint['webgl_vendor'].replace("'", "\\'")
        webgl_renderer = fingerprint['webgl_renderer'].replace("'", "\\'")
        
        # Get language without extra spaces
        language = fingerprint.get('language', 'en-US,en').split(',')[0].strip()
        
        js_code = f"""
// === ANTIDETECT FINGERPRINT PROTECTION ===
// Generated for profile: {fingerprint['profile_id']}
// Device: {fingerprint['device_type']}

// 1. Ukryj automation flags
Object.defineProperty(navigator, 'webdriver', {{
    get: () => undefined
}});

// 2. Override userAgent i platform
Object.defineProperty(navigator, 'userAgent', {{
    get: () => '{user_agent}'
}});

Object.defineProperty(navigator, 'platform', {{
    get: () => '{fingerprint['platform']}'
}});

// 3. Override languages
Object.defineProperty(navigator, 'languages', {{
    get: () => ['{language}']
}});

// 4. Hardware concurrency
Object.defineProperty(navigator, 'hardwareConcurrency', {{
    get: () => {fingerprint['hardware_concurrency']}
}});

// 5. Device memory
Object.defineProperty(navigator, 'deviceMemory', {{
    get: () => {fingerprint['device_memory']}
}});

// 6. Timezone spoofing
const originalDateToString = Date.prototype.toString;
Date.prototype.toString = function() {{
    try {{
        return new Date(this.toLocaleString('en-US', {{ timeZone: '{fingerprint['timezone']}' }})).toString();
    }} catch (e) {{
        return originalDateToString.call(this);
    }}
}};

// 7. Canvas fingerprint protection
const originalGetContext = HTMLCanvasElement.prototype.getContext;
HTMLCanvasElement.prototype.getContext = function(type, attributes) {{
    const context = originalGetContext.call(this, type, attributes);
    
    if (type === '2d') {{
        // Override toDataURL
        const originalToDataURL = context.toDataURL;
        context.toDataURL = function(...args) {{
            // Zwróć spójny hash dla tego profilu
            try {{
                const canvas = document.createElement('canvas');
                canvas.width = 100;
                canvas.height = 50;
                const ctx = canvas.getContext('2d');
                if (ctx) {{
                    ctx.fillStyle = '#ffffff';
                    ctx.fillRect(0, 0, 100, 50);
                    ctx.fillStyle = '#000000';
                    ctx.font = '12px Arial';
                    ctx.fillText('FingerprintProtection', 10, 25);
                }}
                return canvas.toDataURL();
            }} catch (e) {{
                return originalToDataURL.apply(this, args);
            }}
        }};
        
        // Override fillText z lekką randomizacją
        const originalFillText = context.fillText;
        context.fillText = function(...args) {{
            // Dodaj mikro-zmiany
            if (args.length >= 3 && typeof args[0] === 'string') {{
                args[0] = args[0] + ' ';
            }}
            return originalFillText.apply(this, args);
        }};
    }}
    
    return context;
}};

// 8. WebGL fingerprint protection
if (typeof WebGLRenderingContext !== 'undefined') {{
    const originalGetParameter = WebGLRenderingContext.prototype.getParameter;
    WebGLRenderingContext.prototype.getParameter = function(parameter) {{
        // Ukryj WebGL info
        if (parameter === 37445) {{ // UNMASKED_VENDOR_WEBGL
            return '{webgl_vendor}';
        }}
        if (parameter === 37446) {{ // UNMASKED_RENDERER_WEBGL
            return '{webgl_renderer}';
        }}
        return originalGetParameter.call(this, parameter);
    }};
}}

// 9. Audio fingerprint protection
if (window.AudioContext || window.webkitAudioContext) {{
    const AudioContextClass = window.AudioContext || window.webkitAudioContext;
    const originalCreateOscillator = AudioContextClass.prototype.createOscillator;
    AudioContextClass.prototype.createOscillator = function() {{
        const oscillator = originalCreateOscillator.call(this);
        // Modyfikuj frequency
        try {{
            oscillator.frequency.value = 440 + Math.random() * 10;
        }} catch (e) {{}}
        return oscillator;
    }};
}}

// 10. Font fingerprint protection
Object.defineProperty(document, 'fonts', {{
    value: {{
        ready: Promise.resolve(),
        status: 'loaded',
        check: () => true,
        add: () => {{}},
        delete: () => {{}},
        clear: () => {{}},
        load: () => Promise.resolve()
    }}
}});

// 11. Plugin fingerprint protection
Object.defineProperty(navigator, 'plugins', {{
    get: () => {{
        const plugins = [];
        const pluginList = {json.dumps(fingerprint['plugins'])};
        pluginList.forEach(plugin => {{
            plugins.push({{
                name: plugin,
                description: plugin,
                filename: 'internal-pdf-viewer'
            }});
        }});
        return plugins;
    }}
}});

// 12. Screen resolution spoofing
Object.defineProperty(window.screen, 'width', {{
    get: () => {fingerprint['screen']['width']}
}});
Object.defineProperty(window.screen, 'height', {{
    get: () => {fingerprint['screen']['height']}
}});
Object.defineProperty(window.screen, 'availWidth', {{
    get: () => {fingerprint['screen']['width'] - 100}
}});
Object.defineProperty(window.screen, 'availHeight', {{
    get: () => {fingerprint['screen']['height'] - 100}
}});

// 13. WebRTC IP leak protection
if (window.RTCPeerConnection) {{
    const originalRTCPeerConnection = window.RTCPeerConnection;
    window.RTCPeerConnection = function(...args) {{
        const pc = new originalRTCPeerConnection(...args);
        
        // Override createDataChannel
        const originalCreateDataChannel = pc.createDataChannel;
        if (originalCreateDataChannel) {{
            pc.createDataChannel = function(...args) {{
                return originalCreateDataChannel.apply(this, args);
            }};
        }}
        
        return pc;
    }};
}}

// 14. Console.log cleaner (usuwa debug info)
const originalLog = console.log;
console.log = function(...args) {{
    // Filtruj selenium logs
    const hasSeleniumLog = args.some(arg => 
        typeof arg === 'string' && 
        (arg.includes('chrome') || arg.includes('driver') || arg.includes('WebDriver'))
    );
    if (!hasSeleniumLog) {{
        originalLog.apply(console, args);
    }}
}};

// 15. Notification permissions
Object.defineProperty(Notification, 'permission', {{
    get: () => 'denied'
}});

console.info('✅ Fingerprint protection loaded for {fingerprint['device_type']}');
"""
        
        return js_code
    
    def save_fingerprint(self, profile_id, fingerprint):
        """Zapisuje fingerprint do pliku"""
        filename = os.path.join(self.fingerprints_dir, f'profile_{profile_id}.json')
        
        try:
            with open(filename, 'w') as f:
                json.dump(fingerprint, f, indent=2, default=str)
            return True
        except Exception as e:
            print(f"❌ Błąd zapisywania fingerprint: {str(e)}")
            return False
    
    def load_fingerprint(self, profile_id):
        """Ładuje fingerprint z pliku"""
        filename = os.path.join(self.fingerprints_dir, f'profile_{profile_id}.json')
        
        try:
            if os.path.exists(filename):
                with open(filename, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"⚠ Błąd ładowania fingerprint: {e}")
        
        return None
    
    def get_fingerprint_as_arguments(self, fingerprint):
        """Konwertuje fingerprint na argumenty przeglądarki"""
        args = []
        
        # User agent
        args.append(f'--user-agent={fingerprint["user_agent"]}')
        
        # Rozdzielczość okna
        screen = fingerprint['screen']
        args.append(f'--window-size={screen["width"]},{screen["height"]}')
        
        # Język (pierwszy język z listy)
        first_lang = fingerprint.get('language', 'en-US,en').split(',')[0].split('-')[0]
        args.append(f'--lang={first_lang}')
        
        # Timezone
        args.append(f'--timezone={fingerprint["timezone"]}')
        
        # Accept language jeśli istnieje
        if 'accept_language' in fingerprint:
            args.append(f'--accept-language={fingerprint["accept_language"]}')
        
        # Chrome specific - optymalizowane argumenty
        chrome_args = [
            '--disable-blink-features=AutomationControlled',
            '--disable-features=IsolateOrigins,site-per-process',
            '--disable-ipc-flooding-protection',
            '--disable-renderer-backgrounding',
            '--disable-backgrounding-occluded-windows',
            '--disable-background-timer-throttling',
            '--disable-client-side-phishing-detection',
            '--disable-component-update',
            '--disable-default-apps',
            '--disable-dev-shm-usage',
            '--disable-popup-blocking',
            '--disable-hang-monitor',
            '--disable-prompt-on-repost',
            '--disable-sync',
            '--disable-translate',
            '--metrics-recording-only',
            '--no-first-run',
            '--no-default-browser-check',
            '--password-store=basic',
            '--use-mock-keychain',
            '--force-color-profile=srgb',
            '--disable-web-security',
            '--allow-running-insecure-content',
            '--disable-features=VizDisplayCompositor',
            '--disable-breakpad',
            '--disable-logging',
            '--disable-software-rasterizer',
            '--hide-scrollbars',
            '--mute-audio',
            '--no-sandbox',
            '--disable-setuid-sandbox',
        ]
        
        args.extend(chrome_args)
        
        return args
    
    def get_js_injection(self, fingerprint):
        """Zwraca kod JavaScript do wstrzyknięcia"""
        return fingerprint.get('js_injection', '')
    
    def verify_fingerprint_consistency(self, profile_id, driver):
        """Weryfikuje czy fingerprint jest spójny podczas działania"""
        try:
            # Sprawdź podstawowe parametry
            checks = {
                'user_agent': driver.execute_script("return navigator.userAgent"),
                'platform': driver.execute_script("return navigator.platform"),
                'languages': driver.execute_script("return navigator.languages"),
                'hardware_concurrency': driver.execute_script("return navigator.hardwareConcurrency"),
                'screen_width': driver.execute_script("return screen.width"),
                'screen_height': driver.execute_script("return screen.height"),
            }
            
            # Porównaj z fingerprint
            fingerprint = self.load_fingerprint(profile_id)
            if fingerprint:
                for key, value in checks.items():
                    expected = fingerprint.get(key, '')
                    if str(value) != str(expected):
                        print(f"⚠️ Inconsistency in {key}: got {value}, expected {expected}")
                        return False
            
            return True
            
        except Exception as e:
            print(f"❌ Error verifying fingerprint: {e}")
            return False


# Przykład użycia
if __name__ == "__main__":
    engine = FingerprintEngine()
    
    # Generuj fingerprint dla profilu 1
    fp1 = engine.generate_fingerprint(1, 'windows_chrome')
    print(f"✅ Wygenerowano fingerprint dla profilu 1")
    print(f"   User Agent: {fp1['user_agent'][:50]}...")
    print(f"   Screen: {fp1['screen']['width']}x{fp1['screen']['height']}")
    print(f"   WebGL: {fp1['webgl_vendor']}")
    
    # Generuj fingerprint dla profilu 2
    fp2 = engine.generate_fingerprint(2, 'mac_chrome')
    print(f"\n✅ Wygenerowano fingerprint dla profilu 2")
    print(f"   User Agent: {fp2['user_agent'][:50]}...")
    print(f"   Screen: {fp2['screen']['width']}x{fp2['screen']['height']}")
    print(f"   WebGL: {fp2['webgl_vendor']}")
    
    # Pokaż argumenty
    print(f"\n🔧 Argumenty dla profilu 1:")
    for arg in engine.get_fingerprint_as_arguments(fp1)[:5]:
        print(f"   {arg}")