import re
import requests
from urllib.parse import urlparse

class ChannelVerifier:
    """Weryfikacja kanałów YouTube"""
    
    def __init__(self):
        print("✅ ChannelVerifier zainicjalizowany")
    
    def verify_channel_url(self, url):
        """Weryfikuje czy URL jest poprawnym kanałem YouTube"""
        patterns = [
            r'https?://(www\.)?youtube\.com/@[\w-]+',
            r'https?://(www\.)?youtube\.com/channel/[\w-]+',
            r'https?://(www\.)?youtube\.com/c/[\w-]+',
            r'https?://(www\.)?youtube\.com/user/[\w-]+'
        ]
        
        for pattern in patterns:
            if re.match(pattern, url, re.IGNORECASE):
                return True
        
        return False
    
    def extract_channel_id(self, url):
        """Wyciąga ID kanału z URL"""
        try:
            # Dla formatu @username
            match = re.search(r'youtube\.com/@([\w-]+)', url)
            if match:
                return f"@{match.group(1)}"
            
            # Dla formatu channel/UC...
            match = re.search(r'youtube\.com/channel/([\w-]+)', url)
            if match:
                return f"channel/{match.group(1)}"
            
            # Dla formatu c/...
            match = re.search(r'youtube\.com/c/([\w-]+)', url)
            if match:
                return f"c/{match.group(1)}"
            
            return None
            
        except:
            return None
    
    def check_channel_accessibility(self, url):
        """Sprawdza czy kanał jest dostępny"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                return True
            else:
                return False
                
        except:
            return False
    
    def normalize_channel_url(self, url):
        """Normalizuje URL kanału"""
        if not url.startswith('http'):
            url = 'https://' + url
        
        # Jeśli to tylko nazwa użytkownika bez pełnego URL
        if '@' in url and 'youtube.com' not in url:
            url = f'https://www.youtube.com/@{url.replace("@", "")}'
        
        return url

# Testowanie modułu
if __name__ == "__main__":
    print("🧪 Testowanie ChannelVerifier...")
    cv = ChannelVerifier()
    
    test_urls = [
        "https://www.youtube.com/@example",
        "https://www.youtube.com/channel/UC123456",
        "https://youtube.com/c/example",
        "invalid-url"
    ]
    
    for url in test_urls:
        print(f"\nURL: {url}")
        print(f"  Czy poprawny: {cv.verify_channel_url(url)}")
        print(f"  ID kanału: {cv.extract_channel_id(url)}")
        print(f"  Znormalizowany: {cv.normalize_channel_url(url)}")
    
    print("\n✅ Test zakończony")