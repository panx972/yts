"""
Channel Verifier - Weryfikacja kanałów YouTube
"""

import os
import re
from colorama import Fore, Style


class ChannelVerifier:
    def __init__(self):
        pass
    
    def load_channels_from_file(self, filename):
        """Ładuje listę kanałów z pliku"""
        channels = []
        
        if not os.path.exists(filename):
            print(f"{Fore.RED}❌ Plik {filename} nie istnieje{Fore.RESET}")
            return channels
        
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    
                    parts = line.split('|')
                    if len(parts) >= 2:
                        channel = {
                            'url': parts[0].strip(),
                            'name': parts[1].strip(),
                            'keywords': parts[2].strip() if len(parts) > 2 else parts[1].strip()
                        }
                        
                        if self.is_valid_youtube_url(channel['url']):
                            channels.append(channel)
                        else:
                            print(f"{Fore.YELLOW}⚠️  Nieprawidłowy URL: {channel['url']}{Fore.RESET}")
            
            print(f"{Fore.GREEN}✅ Załadowano {len(channels)} kanałów{Fore.RESET}")
            return channels
            
        except Exception as e:
            print(f"{Fore.RED}❌ Błąd: {e}{Fore.RESET}")
            return []
    
    def is_valid_youtube_url(self, url):
        """Sprawdza czy URL jest prawidłowym linkiem YouTube"""
        patterns = [
            r'^https?://(www\.)?youtube\.com/@[\w-]+',
            r'^https?://(www\.)?youtube\.com/c/[\w-]+',
            r'^https?://(www\.)?youtube\.com/channel/[\w-]+',
            r'^https?://(www\.)?youtube\.com/user/[\w-]+',
            r'^https?://(www\.)?youtu\.be/[\w-]+'
        ]
        
        url_lower = url.lower()
        for pattern in patterns:
            if re.match(pattern, url_lower):
                return True
        
        return False