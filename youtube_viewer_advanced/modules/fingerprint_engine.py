"""
Fingerprinting - generowanie unikalnych sygnatur przeglądarki (opcjonalne)
"""

import random
import json
import os
from datetime import datetime

class FingerprintEngine:
    def __init__(self):
        self.fingerprints_dir = 'fingerprints'
        if not os.path.exists(self.fingerprints_dir):
            os.makedirs(self.fingerprints_dir)
    
    def generate_fingerprint(self, profile_id):
        """Generuje unikalny fingerprint dla profilu"""
        fingerprint = {
            'profile_id': profile_id,
            'generated_at': datetime.now().isoformat(),
            'user_agent': self.generate_user_agent(),
            'screen_resolution': self.generate_screen_resolution(),
            'timezone': self.generate_timezone(),
            'language': self.generate_language(),
            'platform': self.generate_platform(),
            'hardware_concurrency': random.choice([2, 4, 6, 8]),
            'device_memory': random.choice([4, 8, 16]),
            'webgl_vendor': self.generate_webgl_vendor(),
            'webgl_renderer': self.generate_webgl_renderer(),
            'canvas_fingerprint': self.generate_canvas_hash(),
            'audio_fingerprint': self.generate_audio_hash(),
            'fonts': self.generate_fonts_list(),
            'plugins': self.generate_plugins(),
            'touch_support': random.choice([True, False]),
            'do_not_track': random.choice([0, 1, None]),
            'cookie_enabled': True,
            'adblock_detected': False
        }
        
        # Zapisz fingerprint
        self.save_fingerprint(profile_id, fingerprint)
        
        return fingerprint
    
    def generate_user_agent(self):
        """Generuje losowy user agent"""
        browsers = [
            # Chrome Windows
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.6045.159 Safari/537.36',
            # Chrome macOS
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            # Firefox Windows
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
            # Safari macOS
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15',
            # Edge Windows
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0'
        ]
        
        return random.choice(browsers)
    
    def generate_screen_resolution(self):
        """Generuje rozdzielczość ekranu"""
        resolutions = [
            {'width': 1920, 'height': 1080},
            {'width': 1366, 'height': 768},
            {'width': 1536, 'height': 864},
            {'width': 1440, 'height': 900},
            {'width': 1280, 'height': 720},
            {'width': 1600, 'height': 900}
        ]
        
        return random.choice(resolutions)
    
    def generate_timezone(self):
        """Generuje strefę czasową"""
        timezones = [
            'Europe/Warsaw',
            'Europe/London',
            'Europe/Berlin',
            'Europe/Paris',
            'America/New_York',
            'America/Los_Angeles',
            'Asia/Tokyo',
            'Australia/Sydney'
        ]
        
        return random.choice(timezones)
    
    def generate_language(self):
        """Generuje język"""
        languages = [
            'pl-PL',
            'en-US',
            'en-GB',
            'de-DE',
            'fr-FR',
            'es-ES'
        ]
        
        return random.choice(languages)
    
    def generate_platform(self):
        """Generuje platformę"""
        platforms = [
            'Win32',
            'MacIntel',
            'Linux x86_64'
        ]
        
        return random.choice(platforms)
    
    def generate_webgl_vendor(self):
        """Generuje vendor WebGL"""
        vendors = [
            'Google Inc.',
            'Intel Inc.',
            'NVIDIA Corporation',
            'AMD',
            'Apple Inc.'
        ]
        
        return random.choice(vendors)
    
    def generate_webgl_renderer(self):
        """Generuje renderer WebGL"""
        renderers = [
            'ANGLE (Intel, Intel(R) UHD Graphics Direct3D11 vs_5_0 ps_5_0)',
            'ANGLE (NVIDIA, NVIDIA GeForce RTX 3060 Direct3D11 vs_5_0 ps_5_0)',
            'ANGLE (AMD, AMD Radeon RX 6700 XT Direct3D11 vs_5_0 ps_5_0)',
            'Apple GPU (Apple M1 Pro)'
        ]
        
        return random.choice(renderers)
    
    def generate_canvas_hash(self):
        """Generuje hash canvas (symulacja)"""
        return f"{random.getrandbits(64):016x}"
    
    def generate_audio_hash(self):
        """Generuje hash audio (symulacja)"""
        return f"{random.getrandbits(32):08x}"
    
    def generate_fonts_list(self):
        """Generuje listę czcionek"""
        common_fonts = [
            'Arial',
            'Arial Black',
            'Times New Roman',
            'Courier New',
            'Verdana',
            'Georgia',
            'Trebuchet MS',
            'Impact',
            'Comic Sans MS',
            'Tahoma'
        ]
        
        # Wybierz losową podlistę
        num_fonts = random.randint(8, len(common_fonts))
        return random.sample(common_fonts, num_fonts)
    
    def generate_plugins(self):
        """Generuje listę wtyczek"""
        plugins = [
            'Chrome PDF Viewer',
            'Chrome PDF Plugin',
            'Native Client',
            'Widevine Content Decryption Module'
        ]
        
        # Losowo usuń niektóre wtyczki
        if random.random() > 0.5:
            plugins = plugins[:2]
        
        return plugins
    
    def save_fingerprint(self, profile_id, fingerprint):
        """Zapisuje fingerprint do pliku"""
        filename = os.path.join(self.fingerprints_dir, f'profile_{profile_id}.json')
        
        try:
            with open(filename, 'w') as f:
                json.dump(fingerprint, f, indent=2)
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
        except:
            pass
        
        return None
    
    def get_fingerprint_as_arguments(self, fingerprint):
        """Konwertuje fingerprint na argumenty przeglądarki"""
        args = []
        
        # User agent
        args.append(f'--user-agent={fingerprint["user_agent"]}')
        
        # Rozdzielczość okna
        args.append(f'--window-size={fingerprint["screen_resolution"]["width"]},{fingerprint["screen_resolution"]["height"]}')
        
        # Język
        args.append(f'--lang={fingerprint["language"].split("-")[0]}')
        
        return args