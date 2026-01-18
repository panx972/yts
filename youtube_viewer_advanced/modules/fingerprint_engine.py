"""
Silnik fingerprintingu - modyfikacja parametrów przeglądarki
"""

import random
import json

class FingerprintEngine:
    def __init__(self):
        self.fingerprints = self._load_fingerprint_templates()
    
    def _load_fingerprint_templates(self):
        """Ładuje szablony fingerprintów"""
        templates = [
            {
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'platform': 'Win32',
                'hardware_concurrency': 8,
                'device_memory': 8,
                'screen': {'width': 1920, 'height': 1080, 'colorDepth': 24},
                'languages': ['pl-PL', 'pl', 'en-US', 'en'],
                'timezone': 'Europe/Warsaw',
                'webgl_vendor': 'Google Inc. (Intel)',
                'webgl_renderer': 'ANGLE (Intel, Intel(R) UHD Graphics Direct3D11 vs_5_0 ps_5_0)'
            },
            {
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
                'platform': 'Win32',
                'hardware_concurrency': 4,
                'device_memory': 4,
                'screen': {'width': 1366, 'height': 768, 'colorDepth': 24},
                'languages': ['en-US', 'en'],
                'timezone': 'America/New_York',
                'webgl_vendor': 'Google Inc. (NVIDIA)',
                'webgl_renderer': 'ANGLE (NVIDIA, NVIDIA GeForce GTX 1060 Direct3D11 vs_5_0 ps_5_0)'
            },
            {
                'user_agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'platform': 'MacIntel',
                'hardware_concurrency': 12,
                'device_memory': 16,
                'screen': {'width': 1440, 'height': 900, 'colorDepth': 30},
                'languages': ['en-US', 'en'],
                'timezone': 'America/Los_Angeles',
                'webgl_vendor': 'Apple Inc.',
                'webgl_renderer': 'Apple GPU'
            }
        ]
        return templates
    
    def get_random_fingerprint(self):
        """Zwraca losowy fingerprint"""
        return random.choice(self.fingerprints)
    
    def apply_fingerprint(self, driver):
        """Stosuje fingerprint do przeglądarki"""
        fingerprint = self.get_random_fingerprint()
        
        # Podstawowe patche JavaScript
        script = f"""
        // Ukryj webdriver
        Object.defineProperty(navigator, 'webdriver', {{
            get: () => undefined
        }});
        
        // Modyfikuj platformę
        Object.defineProperty(navigator, 'platform', {{
            get: () => '{fingerprint['platform']}'
        }});
        
        // Modyfikuj hardwareConcurrency
        Object.defineProperty(navigator, 'hardwareConcurrency', {{
            get: () => {fingerprint['hardware_concurrency']}
        }});
        
        // Modyfikuj deviceMemory
        if ('deviceMemory' in navigator) {{
            Object.defineProperty(navigator, 'deviceMemory', {{
                get: () => {fingerprint['device_memory']}
            }});
        }}
        
        // Modyfikuj języki
        Object.defineProperty(navigator, 'languages', {{
            get: () => {json.dumps(fingerprint['languages'])}
        }});
        
        // Ukryj chrome
        window.chrome = {{ runtime: {{}} }};
        
        // Permissions
        const originalQuery = window.navigator.permissions.query;
        window.navigator.permissions.query = (parameters) => (
            parameters.name === 'notifications' ?
                Promise.resolve({{ state: Notification.permission }}) :
                originalQuery(parameters)
        );
        
        // WebGL vendor/renderer
        const getParameter = WebGLRenderingContext.prototype.getParameter;
        WebGLRenderingContext.prototype.getParameter = function(parameter) {{
            if (parameter === 37445) {{
                return '{fingerprint['webgl_vendor']}';
            }}
            if (parameter === 37446) {{
                return '{fingerprint['webgl_renderer']}';
            }}
            return getParameter.call(this, parameter);
        }};
        
        // Canvas fingerprinting
        const toDataURL = HTMLCanvasElement.prototype.toDataURL;
        HTMLCanvasElement.prototype.toDataURL = function(type) {{
            const context = this.getContext('2d');
            if (context) {{
                // Dodaj losowy szum do canvas
                const imageData = context.getImageData(0, 0, this.width, this.height);
                for (let i = 0; i < imageData.data.length; i += 4) {{
                    imageData.data[i] = imageData.data[i] ^ 1;
                }}
                context.putImageData(imageData, 0, 0);
            }}
            return toDataURL.call(this, type);
        }};
        
        // Timezone
        Object.defineProperty(Intl.DateTimeFormat.prototype, 'resolvedOptions', {{
            get: function() {{
                const original = this._originalResolvedOptions || 
                               Intl.DateTimeFormat.prototype.resolvedOptions.get.call(this);
                return {{
                    ...original,
                    timeZone: '{fingerprint['timezone']}'
                }};
            }}
        }});
        
        console.log('Fingerprint applied:', {{
            platform: navigator.platform,
            hardwareConcurrency: navigator.hardwareConcurrency,
            languages: navigator.languages
        }});
        """
        
        # Wstrzyknij skrypt
        driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            'source': script
        })
        
        # Ustaw User-Agent przez argument
        driver.execute_cdp_cmd('Network.setUserAgentOverride', {
            'userAgent': fingerprint['user_agent'],
            'platform': fingerprint['platform']
        })
        
        # Ustaw rozmiar okna
        driver.set_window_size(
            fingerprint['screen']['width'], 
            fingerprint['screen']['height']
        )
        
        return fingerprint