# test_chromedriver.py
import os

print("🔍 Sprawdzanie ChromeDriver...")
print(f"Aktualny folder: {os.getcwd()}")
print(f"Zawartość folderu:")
for f in os.listdir():
    if 'chrome' in f.lower():
        print(f"  - {f}")

chromedriver_path = "chromedriver.exe"
print(f"\nCzy chromedriver.exe istnieje? {os.path.exists(chromedriver_path)}")
print(f"Ścieżka: {os.path.abspath(chromedriver_path)}")
print(f"Rozmiar: {os.path.getsize(chromedriver_path) if os.path.exists(chromedriver_path) else 0} bajtów")