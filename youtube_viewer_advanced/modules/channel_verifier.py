"""
Weryfikacja kanałów YouTube
"""

import re
import requests
from colorama import Fore, Style

class ChannelVerifier:
    def __init__(self):
        self.patterns = [
            r'https?://(?:www\.)?youtube\.com/@[\w\-]+',
            r'https?://(?:www\.)?youtube\.com/c/[\w\-]+',
            r'https?://(?:www\.)?youtube\.com/user/[\w\-]+',
            r'https?://(?:www\.)?youtube\.com/channel/[\w\-]+',
            r'https?://youtu\.be/[\w\-]+',
            r'https?://(?:www\.)?youtube\.com/watch\?v=[\w\-]+',
            r'https?://(?:www\.)?youtube\.com/playlist\?list=[\w\-]+'
        ]
    
    def verify_channel(self, url):
        """Weryfikuje czy URL jest prawidłowym kanałem/filmem YouTube"""
        print(f"{Fore.CYAN}   🔍 Weryfikuję URL: {url}{Style.RESET_ALL}")
        
        # 1. Sprawdź format URL
        if not self.verify_url_format(url):
            print(f"{Fore.RED}   ❌ Nieprawidłowy format URL{Style.RESET_ALL}")
            return False
        
        # 2. Sprawdź czy strona istnieje (opcjonalnie)
        if not self.check_url_exists(url):
            print(f"{Fore.YELLOW}   ⚠ Nie udało się zweryfikować istnienia strony{Style.RESET_ALL}")
            # Kontynuuj mimo to, bo może być blokada proxy
        
        print(f"{Fore.GREEN}   ✅ URL zweryfikowany{Style.RESET_ALL}")
        return True
    
    def verify_url_format(self, url):
        """Sprawdza format URL"""
        url = url.strip()
        
        # Sprawdź podstawowy format
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        # Sprawdź czy pasuje do patternów YouTube
        for pattern in self.patterns:
            if re.match(pattern, url):
                return True
        
        return False
    
    def check_url_exists(self, url):
        """Sprawdza czy strona istnieje"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
            
            response = requests.head(url, headers=headers, timeout=10, allow_redirects=True)
            
            if response.status_code == 200:
                return True
            elif response.status_code in [301, 302, 307, 308]:
                # Przekierowanie - prawdopodobnie prawidłowy URL
                return True
            else:
                return False
                
        except requests.exceptions.Timeout:
            return False
        except requests.exceptions.ConnectionError:
            return False
        except Exception as e:
            return False
    
    def extract_channel_id(self, url):
        """Wyciąga ID kanału z URL"""
        patterns = {
            'channel': r'youtube\.com/channel/([\w\-]+)',
            'user': r'youtube\.com/user/([\w\-]+)',
            'c': r'youtube\.com/c/([\w\-]+)',
            'handle': r'youtube\.com/@([\w\-]+)',
            'video': r'youtube\.com/watch\?v=([\w\-]+)'
        }
        
        for key, pattern in patterns.items():
            match = re.search(pattern, url)
            if match:
                return match.group(1), key
        
        return None, None
    
    def normalize_url(self, url):
        """Normalizuje URL kanału"""
        channel_id, type = self.extract_channel_id(url)
        
        if not channel_id:
            return url
        
        # Jeśli to film, pobierz kanał z filmu
        if type == 'video':
            # W rzeczywistym użyciu potrzebny by był request do API YouTube
            # Tutaj zwracamy oryginalny URL
            return url
        
        # Zbuduj URL kanału
        if type == 'channel':
            return f"https://www.youtube.com/channel/{channel_id}"
        elif type == 'user':
            return f"https://www.youtube.com/user/{channel_id}"
        elif type == 'c':
            return f"https://www.youtube.com/c/{channel_id}"
        elif type == 'handle':
            return f"https://www.youtube.com/@{channel_id}"
        
        return url
    
    def verify_channel_list(self, channels_file='data/channels.txt'):
        """Weryfikuje listę kanałów z pliku"""
        verified = []
        invalid = []
        
        try:
            with open(channels_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        if self.verify_channel(line):
                            verified.append(line)
                        else:
                            invalid.append(line)
            
            print(f"\n{Fore.CYAN}" + "="*60)
            print("📋 WERYFIKACJA KANAŁÓW")
            print("="*60 + f"{Style.RESET_ALL}")
            
            print(f"{Fore.GREEN}✅ Prawidłowe kanały ({len(verified)}):{Style.RESET_ALL}")
            for channel in verified:
                print(f"   • {channel}")
            
            if invalid:
                print(f"\n{Fore.RED}❌ Nieprawidłowe kanały ({len(invalid)}):{Style.RESET_ALL}")
                for channel in invalid:
                    print(f"   • {channel}")
            
            # Zapisz zweryfikowane kanały
            if verified:
                with open('data/verified_channels.txt', 'w', encoding='utf-8') as f:
                    for channel in verified:
                        f.write(channel + '\n')
                print(f"\n{Fore.GREEN}💾 Zapisano do data/verified_channels.txt{Style.RESET_ALL}")
            
            return verified
            
        except FileNotFoundError:
            print(f"{Fore.RED}❌ Plik {channels_file} nie istnieje!{Style.RESET_ALL}")
            return []