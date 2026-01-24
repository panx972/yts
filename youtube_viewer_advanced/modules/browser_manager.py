"""
BrowserManager z fingerprint, proxy-lokalizacją, bezpiecznymi ścieżkami i ZAWAŻONĄ automatyczną akceptacją cookies
"""

import os
import random
import time
import tempfile
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from modules.fingerprint_engine import FingerprintEngine
from webdriver_manager.chrome import ChromeDriverManager
import urllib.request
import socket

class BrowserManager:
    def __init__(self, profile_index=1, use_proxy=None, use_fingerprint=True, auto_accept_cookies=True):
        self.profile_index = profile_index
        self.use_proxy = use_proxy
        self.use_fingerprint = use_fingerprint
        self.auto_accept_cookies = auto_accept_cookies
        self.driver = None
        self.fingerprint_engine = None
        self.fingerprint = None
        self.cookies_accepted = False  # Flaga śledzenia czy cookies już zaakceptowane
        
        # Mapowanie krajów proxy -> języki -> teksty cookies
        self.country_configs = {
            'pl': {
                'language': 'pl-PL,pl;q=0.9,en-US;q=0.8,en;q=0.7',
                'timezone': 'Europe/Warsaw',
                'cookies_texts': ['Akceptuję', 'Zaakceptuj wszystkie', 'Zgadzam się', 'Akceptuj cookies', 'Przejdź do serwisu']
            },
            'us': {
                'language': 'en-US,en;q=0.9',
                'timezone': 'America/New_York',
                'cookies_texts': ['Accept all', 'I accept', 'Accept cookies', 'Agree', 'OK', 'Allow all', 'Continue']
            },
            'gb': {
                'language': 'en-GB,en;q=0.9',
                'timezone': 'Europe/London',
                'cookies_texts': ['Accept all', 'I accept', 'Accept cookies', 'Agree', 'OK', 'Allow all', 'Continue']
            },
            'de': {
                'language': 'de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7',
                'timezone': 'Europe/Berlin',
                'cookies_texts': ['Alle akzeptieren', 'Akzeptieren', 'Einverstanden', 'Cookies akzeptieren', 'OK']
            },
            'fr': {
                'language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
                'timezone': 'Europe/Paris',
                'cookies_texts': ['Tout accepter', 'J\'accepte', 'Accepter les cookies', 'D\'accord', 'Continuer']
            },
            'es': {
                'language': 'es-ES,es;q=0.9,en-US;q=0.8,en;q=0.7',
                'timezone': 'Europe/Madrid',
                'cookies_texts': ['Aceptar todas', 'Acepto', 'Aceptar cookies', 'De acuerdo', 'Continuar']
            },
            'it': {
                'language': 'it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7',
                'timezone': 'Europe/Rome',
                'cookies_texts': ['Accetta tutto', 'Accetto', 'Accetta i cookie', 'Acconsento', 'Continua']
            },
            'nl': {
                'language': 'nl-NL,nl;q=0.9,en-US;q=0.8,en;q=0.7',
                'timezone': 'Europe/Amsterdam',
                'cookies_texts': ['Alles accepteren', 'Ik accepteer', 'Cookies accepteren', 'Akkoord', 'Doorgaan']
            },
            'se': {
                'language': 'sv-SE,sv;q=0.9,en-US;q=0.8,en;q=0.7',
                'timezone': 'Europe/Stockholm',
                'cookies_texts': ['Acceptera alla', 'Jag accepterar', 'Acceptera cookies', 'Okej', 'Fortsätt']
            },
            'no': {
                'language': 'nb-NO,nb;q=0.9,en-US;q=0.8,en;q=0.7',
                'timezone': 'Europe/Oslo',
                'cookies_texts': ['Godta alle', 'Jeg godtar', 'Godta informasjonskapsler', 'OK', 'Fortsett']
            },
            'ua': {
                'language': 'uk-UA,uk;q=0.9,ru;q=0.8,en-US;q=0.7',
                'timezone': 'Europe/Kiev',
                'cookies_texts': ['Прийняти все', 'Я приймаю', 'Прийняти cookies', 'Згоден', 'Продовжити']
            },
            'ru': {
                'language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
                'timezone': 'Europe/Moscow',
                'cookies_texts': ['Принять все', 'Я принимаю', 'Принять cookies', 'Согласен', 'Продолжить']
            },
            'jp': {
                'language': 'ja-JP,ja;q=0.9,en-US;q=0.8,en;q=0.7',
                'timezone': 'Asia/Tokyo',
                'cookies_texts': ['すべて受け入れる', '同意する', 'クッキーを受け入れる', 'OK', '続行']
            },
            'kr': {
                'language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
                'timezone': 'Asia/Seoul',
                'cookies_texts': ['모두 수락', '동의합니다', '쿠키 수락', '확인', '계속']
            },
            'cn': {
                'language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
                'timezone': 'Asia/Shanghai',
                'cookies_texts': ['接受所有', '我接受', '接受Cookies', '同意', '继续']
            },
            'br': {
                'language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
                'timezone': 'America/Sao_Paulo',
                'cookies_texts': ['Aceitar tudo', 'Eu aceito', 'Aceitar cookies', 'Concordo', 'Continuar']
            },
            'mx': {
                'language': 'es-MX,es;q=0.9,en-US;q=0.8,en;q=0.7',
                'timezone': 'America/Mexico_City',
                'cookies_texts': ['Aceptar todas', 'Acepto', 'Aceptar cookies', 'De acuerdo', 'Continuar']
            }
        }
        
        # Używamy TYLKO katalogu tymczasowego systemu
        self.temp_dir = tempfile.gettempdir()
        
        # Inicjalizuj silnik fingerprint
        if self.use_fingerprint:
            self.fingerprint_engine = FingerprintEngine()
        
        self.init_browser()
    
    def detect_proxy_country(self, proxy):
        """Wykrywa kraj z proxy (z IP lub z formatu proxy)"""
        try:
            # Spróbuj wyciągnąć kraj z formatu proxy (np. 123.45.67.89:8080:pl:user:pass)
            if ':' in proxy:
                parts = proxy.split(':')
                if len(parts) >= 3 and len(parts[2]) == 2:
                    country = parts[2].lower()
                    if country in self.country_configs:
                        print(f"📍 Wykryto kraj z formatu proxy: {country.upper()}")
                        return country
            
            # Jeśli nie ma w formacie, spróbuj wykryć z IP
            ip = proxy.split(':')[0]
            
            # API do geolokalizacji (darmowe)
            try:
                response = urllib.request.urlopen(f"http://ip-api.com/json/{ip}?fields=countryCode")
                data = json.loads(response.read().decode())
                country = data.get('countryCode', '').lower()
                if country in self.country_configs:
                    print(f"📍 Wykryto kraj z IP API: {country.upper()}")
                    return country
            except:
                pass
            
            # Fallback: sprawdź strefę IP
            try:
                first_octet = int(ip.split('.')[0])
                if 1 <= first_octet <= 191:
                    print("📍 Wykryto strefę IP: USA (domyślnie)")
                    return 'us'
                elif 192 <= first_octet <= 223:
                    print("📍 Wykryto strefę IP: Europa (domyślnie DE)")
                    return 'de'
                else:
                    print("📍 Nieznana strefa IP, domyślnie USA")
                    return 'us'
            except:
                print("📍 Nie udało się odczytać IP, domyślnie USA")
                return 'us'
                
        except Exception as e:
            print(f"⚠ Nie udało się wykryć kraju proxy: {e}")
            return 'us'  # Domyślnie USA
    
    def get_location_based_config(self, country=None):
        """Zwraca spójną konfigurację językową i czasową na podstawie kraju"""
        # Jeśli nie podano kraju lub nie ma w mapowaniu, użyj USA
        if not country or country not in self.country_configs:
            print(f"⚠ Kraj '{country}' nieobsługiwany, używam USA")
            country = 'us'
        
        # Pobierz konfigurację dla tego kraju
        config = self.country_configs[country].copy()
        config['country'] = country.upper()
        
        # Wybierz odpowiedni device_type na podstawie kraju
        if country in ['us', 'ca', 'gb', 'au']:
            config['device_type'] = random.choice(['windows_chrome', 'mac_chrome'])
        elif country in ['pl', 'de', 'fr', 'es', 'it', 'nl']:
            config['device_type'] = 'windows_chrome'
        elif country in ['jp', 'kr', 'cn']:
            config['device_type'] = random.choice(['windows_chrome', 'mac_chrome'])
        else:
            config['device_type'] = 'windows_chrome'
        
        # Debugowanie spójności
        self.debug_location_consistency(country, config)
        
        return config
    
    def debug_location_consistency(self, detected_country, config):
        """Debugowanie spójności danych lokalizacyjnych"""
        print(f"🔍 DEBUG SPÓJNOŚCI LOKALIZACJI:")
        print(f"   Wykryty kraj: {detected_country.upper() if detected_country else 'Brak'}")
        print(f"   Config kraj: {config['country']}")
        print(f"   Język: {config['language'].split(',')[0]}")
        print(f"   Strefa: {config['timezone']}")
        print(f"   Cookies: {config['country']} ({len(config['cookies_texts'])} tekstów)")
        
        # Sprawdź czy język i strefa pasują do kraju
        if detected_country and detected_country in self.country_configs:
            expected_config = self.country_configs[detected_country]
            
            if config['language'] != expected_config['language']:
                print(f"   ⚠ NIESPÓJNOŚĆ: język powinien być: {expected_config['language'].split(',')[0]}")
            else:
                print(f"   ✓ Język spójny")
                
            if config['timezone'] != expected_config['timezone']:
                print(f"   ⚠ NIESPÓJNOŚĆ: strefa powinna być: {expected_config['timezone']}")
            else:
                print(f"   ✓ Strefa spójna")
                
            print(f"   ✓ Cookies spójne z krajem")
        print()
    
    def get_cookies_emoji(self, country_code):
        """Zwraca emoji flagi dla kraju cookies"""
        flag_emojis = {
            'US': '🇺🇸', 'GB': '🇬🇧', 'PL': '🇵🇱', 'DE': '🇩🇪', 'FR': '🇫🇷',
            'ES': '🇪🇸', 'IT': '🇮🇹', 'NL': '🇳🇱', 'SE': '🇸🇪', 'NO': '🇳🇴',
            'UA': '🇺🇦', 'RU': '🇷🇺', 'JP': '🇯🇵', 'KR': '🇰🇷', 'CN': '🇨🇳',
            'BR': '🇧🇷', 'MX': '🇲🇽'
        }
        return flag_emojis.get(country_code, '🍪')
    
    def get_safe_profile_path(self):
        """Tworzy bezpieczną ścieżkę profilu BEZ spacji"""
        # Utwórz bazowy katalog dla profili
        base_dir = os.path.join(self.temp_dir, 'ytbot_profiles')
        os.makedirs(base_dir, exist_ok=True)
        
        # Nazwa profilu bez spacji i znaków specjalnych
        profile_name = f"p{self.profile_index}_{int(time.time())}_{random.randint(1000,9999)}"
        
        # Pełna ścieżka
        profile_path = os.path.join(base_dir, profile_name)
        os.makedirs(profile_path, exist_ok=True)
        
        return profile_path
    
    def inject_cookies_auto_accept(self, country_code='us'):
        """Wstrzykuje skrypt automatycznej akceptacji cookies (działa przed załadowaniem strony)"""
        cookies_script = """
        // ==UserScript==
        // @name         Auto Accept YouTube Cookies
        // @namespace    http://tampermonkey.net/
        // @version      3.0
        // @description  Automatically accepts YouTube cookies
        // @author       Bot
        // @match        *://*.youtube.com/*
        // @grant        none
        // @run-at       document-start
        // ==/UserScript==
        
        (function() {
            'use strict';
            
            console.log('🍪 Auto-cookies script loaded');
            
            // Uniwersalne teksty akceptacji (wielojęzyczne)
            const acceptTexts = [
                // English
                'accept', 'agree', 'allow all', 'continue', 'yes', 'ok', 'got it', 
                // Polish
                'akceptuj', 'zgadzam', 'przejdź', 'tak', 
                // German
                'akzeptieren', 'einverstanden', 'zustimmen',
                // French
                'accepter', 'd\'accord', 'continuer',
                // Spanish
                'aceptar', 'de acuerdo', 'continuar',
                // Italian
                'accetta', 'accetto', 'accettare', 'continuare'
            ];
            
            function clickAcceptButton() {
                // Metoda 1: Szukaj po atrybucie aria-label (najskuteczniejsze dla YouTube)
                const ariaSelectors = [
                    'button[aria-label*="accept" i]',
                    'button[aria-label*="akceptuj" i]',
                    'button[aria-label*="agree" i]',
                    'button[aria-label*="zgadzam" i]',
                    'button[aria-label*="allow" i]',
                    'tp-yt-paper-button[aria-label*="accept" i]',
                    'yt-button-renderer[aria-label*="accept" i]'
                ];
                
                for (const selector of ariaSelectors) {
                    try {
                        const elements = document.querySelectorAll(selector);
                        for (const el of elements) {
                            if (el.offsetParent !== null && el.getAttribute('aria-disabled') !== 'true') {
                                el.click();
                                console.log('🍪 Clicked via aria-label:', selector);
                                return true;
                            }
                        }
                    } catch(e) {}
                }
                
                // Metoda 2: Szukaj po tekście w przyciskach
                const buttons = document.querySelectorAll('button, [role="button"], tp-yt-paper-button, yt-button-renderer');
                for (const btn of buttons) {
                    const btnText = (btn.textContent || btn.innerText || '').toLowerCase().trim();
                    const btnAria = (btn.getAttribute('aria-label') || '').toLowerCase();
                    
                    for (const text of acceptTexts) {
                        if (btnText.includes(text) || btnAria.includes(text)) {
                            if (btn.offsetParent !== null && btn.getAttribute('aria-disabled') !== 'true') {
                                btn.click();
                                console.log('🍪 Clicked via text match:', text);
                                return true;
                            }
                        }
                    }
                }
                
                // Metoda 3: Specyficzne selektory YouTube
                const youtubeSelectors = [
                    'button.yt-spec-button-shape-next--call-to-action',
                    'form[action*="consent"] button',
                    'div[role="dialog"] button:last-child',
                    'ytd-consent-bump-v2-lightbox button',
                    '#content ytd-button-renderer'
                ];
                
                for (const selector of youtubeSelectors) {
                    try {
                        const elements = document.querySelectorAll(selector);
                        for (const el of elements) {
                            if (el.offsetParent !== null) {
                                const text = (el.textContent || '').toLowerCase();
                                if (text && (text.includes('accept') || text.includes('agree') || text.includes('ok'))) {
                                    el.click();
                                    console.log('🍪 Clicked via YouTube selector:', selector);
                                    return true;
                                }
                            }
                        }
                    } catch(e) {}
                }
                
                return false;
            }
            
            // Główna funkcja akceptacji
            function acceptCookies() {
                if (clickAcceptButton()) {
                    console.log('🍪 Successfully accepted cookies');
                    return true;
                }
                
                // Jeśli nie znaleziono, poczekaj na dynamiczne załadowanie
                setTimeout(() => {
                    if (!clickAcceptButton()) {
                        // Spróbuj raz jeszcze po sekundzie
                        setTimeout(clickAcceptButton, 1000);
                    }
                }, 500);
                
                return false;
            }
            
            // Uruchom natychmiast po załadowaniu DOM
            if (document.readyState === 'loading') {
                document.addEventListener('DOMContentLoaded', function() {
                    setTimeout(acceptCookies, 1000);
                });
            } else {
                setTimeout(acceptCookies, 1000);
            }
            
            // Obserwuj zmiany DOM (dla SPA jak YouTube)
            const observer = new MutationObserver(function(mutations) {
                for (const mutation of mutations) {
                    if (mutation.addedNodes.length > 0) {
                        // Sprawdź czy dodano elementy z dialogiem/modalem
                        for (const node of mutation.addedNodes) {
                            if (node.nodeType === 1) { // ELEMENT_NODE
                                const role = node.getAttribute && node.getAttribute('role');
                                if (role === 'dialog' || 
                                    node.tagName.toLowerCase().includes('dialog') ||
                                    node.classList && (
                                        node.classList.contains('modal') ||
                                        node.classList.contains('dialog') ||
                                        node.classList.contains('consent')
                                    )) {
                                    setTimeout(acceptCookies, 300);
                                }
                            }
                        }
                    }
                }
            });
            
            observer.observe(document.body, {
                childList: true,
                subtree: true
            });
            
            // Zatrzymaj obserwator po 15 sekundach
            setTimeout(() => observer.disconnect(), 15000);
            
            // Ponów próbę kilka razy z opóźnieniami
            const attempts = [1000, 2500, 4000, 6000, 8000];
            attempts.forEach((delay, index) => {
                setTimeout(() => {
                    clickAcceptButton();
                }, delay);
            });
            
        })();
        """
        
        try:
            self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                'source': cookies_script
            })
            print(f"✅ Wstrzyknięto auto-accept cookies script")
            return True
        except Exception as e:
            print(f"⚠ Błąd wstrzykiwania cookies script: {e}")
            return False
    
    def init_browser(self):
        """Inicjalizuje przeglądarkę z fingerprint i lokalizacją"""
        try:
            chrome_options = Options()
            
            # PODSTAWOWE OPCJE BEZPIECZEŃSTWA
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            
            # ANTY-DETECT OPCJE
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # Wykryj kraj z proxy
            detected_country = None
            if self.use_proxy:
                detected_country = self.detect_proxy_country(self.use_proxy)
                chrome_options.add_argument(f'--proxy-server={self.use_proxy}')
                print(f"🌐 Używam proxy: {self.use_proxy.split('@')[-1] if '@' in self.use_proxy else self.use_proxy}")
            
            # Pobierz SPÓJNĄ konfigurację na podstawie wykrytego kraju
            location_config = self.get_location_based_config(detected_country)
            
            # Ustaw język i strefę czasową ZAWSZE z location_config
            accept_language = location_config['language']
            timezone = location_config['timezone']
            config_country = location_config['country']
            cookies_country = config_country  # Używamy tego samego kraju dla cookies!
            
            # Dodaj argumenty językowe i strefowe
            chrome_options.add_argument(f'--accept-language={accept_language}')
            chrome_options.add_argument(f'--lang={accept_language.split(",")[0].split("-")[0]}')
            chrome_options.add_argument(f'--timezone={timezone}')
            
            # Stwórz lub załaduj fingerprint (jeśli włączone)
            if self.use_fingerprint and self.fingerprint_engine:
                device_type = location_config['device_type']
                self.fingerprint = self.fingerprint_engine.load_fingerprint(self.profile_index)
                
                if not self.fingerprint:
                    # Generuj nowy fingerprint z LOKALIZACJĄ
                    self.fingerprint = self.fingerprint_engine.generate_fingerprint_with_location(
                        self.profile_index, 
                        device_type,
                        location_config
                    )
                    print(f"👆 Wygenerowano nowy fingerprint dla kraju: {config_country}")
                
                # Dodaj argumenty z fingerprint
                fingerprint_args = self.fingerprint_engine.get_fingerprint_as_arguments(self.fingerprint)
                for arg in fingerprint_args:
                    chrome_options.add_argument(arg)
                
                # NADPISZ język i lokalizację z fingerprint (jeśli są)
                fingerprint_lang = self.fingerprint.get('accept_language')
                fingerprint_tz = self.fingerprint.get('timezone')
                
                if fingerprint_lang and fingerprint_tz:
                    print(f"👆 Używam języka i strefy z fingerprint:")
                    print(f"   Język: {fingerprint_lang.split(',')[0]}")
                    print(f"   Strefa: {fingerprint_tz}")
                    
                    # Nadpisz argumenty
                    chrome_options.add_argument(f'--accept-language={fingerprint_lang}')
                    chrome_options.add_argument(f'--lang={fingerprint_lang.split(",")[0].split("-")[0]}')
                    chrome_options.add_argument(f'--timezone={fingerprint_tz}')
                    
                    accept_language = fingerprint_lang
                    timezone = fingerprint_tz
                    
                    # Jeśli fingerprint ma inny język, dostosuj cookies
                    # Sprawdź czy język fingerprint pasuje do któregoś kraju
                    for country_code, country_data in self.country_configs.items():
                        if country_data['language'].split(',')[0] == fingerprint_lang.split(',')[0]:
                            cookies_country = country_code.upper()
                            print(f"👆 Cookies dostosowane do języka fingerprint: {cookies_country}")
                            break
            
            # Rozmiar okna
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--start-maximized')
            
            # Ścieżka profilu
            profile_path = self.get_safe_profile_path()
            chrome_options.add_argument(f'--user-data-dir={profile_path}')
            
            # OPCJE OPTYMALIZACYJNE
            chrome_options.add_argument('--disable-software-rasterizer')
            chrome_options.add_argument('--disable-features=VizDisplayCompositor')
            chrome_options.add_argument('--disable-logging')
            chrome_options.add_argument('--log-level=3')
            chrome_options.add_argument('--disable-extensions')
            chrome_options.add_argument('--disable-browser-side-navigation')
            chrome_options.add_argument('--disable-features=TranslateUI')
            
            # DODATKOWE OPCJE ANTY-DETECT
            chrome_options.add_argument('--disable-web-security')
            chrome_options.add_argument('--allow-running-insecure-content')
            chrome_options.add_argument('--disable-features=IsolateOrigins,site-per-process')
            chrome_options.add_argument('--disable-site-isolation-trials')
            
            # LOGI INICJALIZACJI - ZAWSZE SPÓJNE
            cookies_emoji = self.get_cookies_emoji(cookies_country)
            print(f"🚀 INICJALIZACJA PRZEGLĄDARKI:")
            print(f"   📁 Profil: {os.path.basename(profile_path)}")
            print(f"   🌍 Kraj: {config_country}")
            print(f"   🗣️ Język: {accept_language.split(',')[0]}")
            print(f"   🕐 Strefa: {timezone}")
            print(f"   {cookies_emoji} Cookies: {cookies_country}")
            if self.use_fingerprint and self.fingerprint:
                print(f"   👆 Fingerprint: Tak")
            
            # Inicjalizuj ChromeDriver
            try:
                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
            except Exception as e:
                print(f"⚠ Fallback do Chrome bez service: {e}")
                self.driver = webdriver.Chrome(options=chrome_options)
            
            # ★★★ WAŻNE: Wstrzyknij auto-accept cookies PRZED fingerprint ★★★
            if self.auto_accept_cookies:
                self.inject_cookies_auto_accept(cookies_country.lower())
                print("✅ Wstrzyknięto auto-accept cookies przed fingerprint")
            
            # Wstrzyknij fingerprint JS (jeśli włączone)
            if self.use_fingerprint and self.fingerprint and self.fingerprint_engine:
                self.inject_fingerprint_js()
            
            # Ukryj automatyzację
            self.hide_automation()
            
            # Ustaw geolokację jeśli mamy kraj
            if detected_country:
                self.set_geolocation(detected_country)
            
            # Zapisz konfigurację cookies dla tego instancji
            self.cookies_config = {
                'country': cookies_country,
                'texts': location_config['cookies_texts'],
                'emoji': cookies_emoji
            }
            
            print(f"✅ Przeglądarka gotowa!")
            return True
            
        except Exception as e:
            print(f"❌ Błąd inicjalizacji: {str(e)}")
            return self.try_headless_mode()
    
    def inject_fingerprint_js(self):
        """Wstrzykuje kod JavaScript ochrony fingerprint"""
        if self.fingerprint and self.driver and self.fingerprint_engine:
            try:
                js_code = self.fingerprint_engine.get_js_injection(self.fingerprint)
                self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                    'source': js_code
                })
                print("✅ Wstrzyknięto fingerprint protection JavaScript")
            except Exception as e:
                print(f"⚠ Błąd wstrzykiwania fingerprint JS: {e}")
    
    def hide_automation(self):
        """Ukrywa ślady automatyzacji"""
        try:
            # Usuń webdriver flag
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            # Override permissions
            self.driver.execute_cdp_cmd('Browser.grantPermissions', {
                'origin': 'https://www.youtube.com',
                'permissions': ['geolocation', 'notifications']
            })
            
            # Ustaw user agent override
            if self.fingerprint and 'user_agent' in self.fingerprint:
                self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {
                    "userAgent": self.fingerprint['user_agent'],
                    "platform": self.fingerprint.get('platform', 'Win32'),
                    "acceptLanguage": self.fingerprint.get('accept_language', 'en-US,en;q=0.9')
                })
                print(f"🔄 Ustawiono User-Agent: {self.fingerprint['user_agent'].split(' ')[0]}")
            
        except Exception as e:
            print(f"⚠ Błąd ukrywania automatyzacji: {e}")
    
    def set_geolocation(self, country):
        """Ustawia geolokalizację przeglądarki"""
        try:
            # Współrzędne dla różnych krajów
            coordinates = {
                'pl': {'latitude': 52.2297, 'longitude': 21.0122, 'accuracy': 100},  # Warszawa
                'us': {'latitude': 40.7128, 'longitude': -74.0060, 'accuracy': 100},  # NYC
                'gb': {'latitude': 51.5074, 'longitude': -0.1278, 'accuracy': 100},  # Londyn
                'de': {'latitude': 52.5200, 'longitude': 13.4050, 'accuracy': 100},  # Berlin
                'fr': {'latitude': 48.8566, 'longitude': 2.3522, 'accuracy': 100},  # Paryż
                'es': {'latitude': 40.4168, 'longitude': -3.7038, 'accuracy': 100},  # Madryt
                'it': {'latitude': 41.9028, 'longitude': 12.4964, 'accuracy': 100},  # Rzym
                'nl': {'latitude': 52.3676, 'longitude': 4.9041, 'accuracy': 100},   # Amsterdam
                'se': {'latitude': 59.3293, 'longitude': 18.0686, 'accuracy': 100},  # Sztokholm
                'no': {'latitude': 59.9139, 'longitude': 10.7522, 'accuracy': 100},  # Oslo
                'ua': {'latitude': 50.4501, 'longitude': 30.5234, 'accuracy': 100},  # Kijów
                'ru': {'latitude': 55.7558, 'longitude': 37.6173, 'accuracy': 100},  # Moskwa
                'jp': {'latitude': 35.6762, 'longitude': 139.6503, 'accuracy': 100},  # Tokio
                'kr': {'latitude': 37.5665, 'longitude': 126.9780, 'accuracy': 100},  # Seul
                'cn': {'latitude': 39.9042, 'longitude': 116.4074, 'accuracy': 100},  # Pekin
                'br': {'latitude': -23.5505, 'longitude': -46.6333, 'accuracy': 100}, # São Paulo
                'mx': {'latitude': 19.4326, 'longitude': -99.1332, 'accuracy': 100},  # Mexico City
            }
            
            if country in coordinates:
                self.driver.execute_cdp_cmd("Emulation.setGeolocationOverride", coordinates[country])
                print(f"📍 Ustawiono geolokalizację dla {country.upper()}: {coordinates[country]['latitude']}, {coordinates[country]['longitude']}")
        except Exception as e:
            print(f"⚠ Błąd ustawiania geolokalizacji: {e}")
    
    def accept_cookies(self, url=None, max_attempts=2):
        """ULEPSZONA: Automatycznie akceptuje cookies na stronie - BEZ NADMIERNYCH ODSWIEŻEŃ"""
        if not self.auto_accept_cookies or not self.driver or self.cookies_accepted:
            return True  # Jeśli już zaakceptowane, zwróć True
        
        try:
            # Jeśli podano URL, przejdź do niego
            if url:
                self.driver.get(url)
                time.sleep(3)  # ★ ZWIĘKSZ CZAS NA ZAŁADOWANIE ★
            
            print(f"{self.cookies_config['emoji']} Próba akceptacji cookies...")
            
            for attempt in range(max_attempts):
                found = False
                
                # ★★★ METODA 1: Specyficzne selektory YouTube (najskuteczniejsze) ★★★
                youtube_selectors = [
                    # Nowy design YouTube (najważniejsze!)
                    'button[aria-label*="Accept" i]',
                    'button[aria-label*="Akceptuj" i]',
                    'button[aria-label*="agree" i]',
                    'button[aria-label*="zgadzam" i]',
                    
                    # Typowe selektory YouTube
                    'tp-yt-paper-button[aria-label*="accept" i]',
                    'yt-button-renderer[aria-label*="accept" i]',
                    'button.yt-spec-button-shape-next',
                    'form[action*="consent"] button',
                    
                    # Stare selektory
                    'button#accept-button',
                    'button[onclick*="accept"]',
                ]
                
                for selector in youtube_selectors:
                    try:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        for element in elements:
                            try:
                                if element.is_displayed() and element.is_enabled():
                                    # Przewiń do elementu
                                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                                    time.sleep(0.5)
                                    
                                    # Kliknij
                                    element.click()
                                    print(f"{self.cookies_config['emoji']} ✅ Zaakceptowano cookies (selector: {selector})")
                                    time.sleep(2)
                                    self.cookies_accepted = True
                                    return True
                            except:
                                continue
                    except:
                        continue
                
                # ★★★ METODA 2: Szukaj po tekście (wielojęzycznie) ★★★
                if not found:
                    for cookie_text in self.cookies_config['texts']:
                        try:
                            # Szukaj po tekście w button/span/a
                            xpath = f"""
                            //*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 
                            '{cookie_text.lower()}')]
                            | //button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 
                            '{cookie_text.lower()}')]
                            | //*[contains(translate(@aria-label, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 
                            '{cookie_text.lower()}')]
                            """
                            
                            elements = self.driver.find_elements(By.XPATH, xpath)
                            for element in elements:
                                try:
                                    if element.is_displayed() and element.is_enabled():
                                        element.click()
                                        print(f"{self.cookies_config['emoji']} ✅ Zaakceptowano cookies (tekst: '{cookie_text}')")
                                        time.sleep(2)
                                        self.cookies_accepted = True
                                        return True
                                except:
                                    continue
                        except:
                            continue
                
                # ★★★ METODA 3: Szukaj modal/dialog i kliknij ostatni przycisk ★★★
                if not found:
                    try:
                        # Szukaj dialogów/modalów
                        dialogs = self.driver.find_elements(By.XPATH, 
                            "//div[@role='dialog'] | //div[contains(@class, 'modal')] | //div[contains(@class, 'dialog')]")
                        
                        for dialog in dialogs:
                            if dialog.is_displayed():
                                # Znajdź przyciski w dialogu
                                buttons = dialog.find_elements(By.XPATH, ".//button")
                                if buttons:
                                    # Kliknij ostatni przycisk (zazwyczaj "Accept")
                                    buttons[-1].click()
                                    print(f"{self.cookies_config['emoji']} ✅ Zaakceptowano cookies (modal dialog)")
                                    time.sleep(2)
                                    self.cookies_accepted = True
                                    return True
                    except:
                        pass
                
                # Jeśli nie znaleziono w tej próbie, poczekaj i spróbuj ponownie
                if attempt < max_attempts - 1:
                    print(f"{self.cookies_config['emoji']} ⏳ Próba {attempt + 1} nieudana, czekam 2s...")
                    time.sleep(2)
            
            print(f"{self.cookies_config['emoji']} ⚠️ Nie znaleziono przycisku cookies po {max_attempts} próbach")
            print(f"{self.cookies_config['emoji']} ℹ️ Kontynuuję bez akceptacji cookies (może już zaakceptowane)")
            
            # Ustaw flagę żeby nie próbować ciągle
            self.cookies_accepted = True
            return False  # Ale zwróć False, bo nie udało się znaleźć
            
        except Exception as e:
            print(f"{self.cookies_config['emoji']} ❌ Błąd akceptowania cookies: {e}")
            # Nadal ustaw flagę, żeby nie próbować w kółko
            self.cookies_accepted = True
            return False
    
    def get(self, url, accept_cookies=True):
        """Wrapper dla driver.get z ROZSĄDNĄ automatyczną akceptacją cookies"""
        if not self.driver:
            return False
        
        try:
            self.driver.get(url)
            time.sleep(3)  # ★ ZWIĘKSZ CZAS NA ZAŁADOWANIE ★
            
            if accept_cookies and self.auto_accept_cookies and not self.cookies_accepted:
                # ★ TYLKO RAZ próbuj zaakceptować cookies ★
                self.accept_cookies()
            else:
                # Jeśli już wcześniej zaakceptowane, nie próbuj ponownie
                print(f"{self.cookies_config['emoji']} ✅ Cookies już zaakceptowane wcześniej, pomijam")
            
            return True
        except Exception as e:
            print(f"❌ Błąd ładowania strony {url}: {e}")
            return False
    
    def try_headless_mode(self):
        """Próbuje uruchomić w trybie headless (bez GUI)"""
        try:
            print("🔄 Próba uruchomienia w trybie headless...")
            
            chrome_options = Options()
            chrome_options.add_argument('--headless=new')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            
            # Wykryj kraj z proxy
            detected_country = None
            if self.use_proxy:
                detected_country = self.detect_proxy_country(self.use_proxy)
                chrome_options.add_argument(f'--proxy-server={self.use_proxy}')
            
            # Pobierz spójną konfigurację
            location_config = self.get_location_based_config(detected_country)
            
            # Ustaw język i strefę
            chrome_options.add_argument(f'--accept-language={location_config["language"]}')
            chrome_options.add_argument(f'--lang={location_config["language"].split(",")[0].split("-")[0]}')
            chrome_options.add_argument(f'--timezone={location_config["timezone"]}')
            
            # NIE używaj user-data-dir w headless
            chrome_options.add_argument('--incognito')
            
            self.driver = webdriver.Chrome(options=chrome_options)
            
            # Ukryj automatyzację
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            # Zapisz konfigurację cookies
            self.cookies_config = {
                'country': location_config['country'],
                'texts': location_config['cookies_texts'],
                'emoji': self.get_cookies_emoji(location_config['country'])
            }
            
            cookies_emoji = self.cookies_config['emoji']
            print(f"✅ Przeglądarka headless gotowa!")
            print(f"   🌍 Kraj: {location_config['country']}")
            print(f"   🗣️ Język: {location_config['language'].split(',')[0]}")
            print(f"   {cookies_emoji} Cookies: {location_config['country']}")
            
            return True
            
        except Exception as e:
            print(f"❌ Błąd headless: {str(e)}")
            return False
    
    def get_driver(self):
        return self.driver
    
    def quit(self):
        if self.driver:
            try:
                self.driver.quit()
                print(f"👋 Przeglądarka zamknięta")
            except:
                pass