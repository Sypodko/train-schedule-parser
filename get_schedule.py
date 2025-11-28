import requests

def download_schedule():
    url = "https://www.tutu.ru/station.php?nnst=45807"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        print("Скачиваю расписание...")
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        with open('schedule.html', 'w', encoding='utf-8') as file:
            file.write(response.text)
            
        print("✅ Страница успешно скачана и сохранена как schedule.html")
        print("Теперь можно запустить парсер: python parse_sputnik.py")
        
    except Exception as e:
        print(f"❌ Ошибка при скачивании: {e}")

if __name__ == "__main__":
    download_schedule()