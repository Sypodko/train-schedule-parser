import json
import argparse
from bs4 import BeautifulSoup
import re

def extract_route(text):
    patterns = [
        r'([А-Я][а-я]+(?:\s+[А-Я][а-я]+)*\s*—\s*[А-Я][а-я]+(?:\s+[А-Я][а-я]+)*)',
        r'([А-Я][а-я]+\s*—\s*[А-Я][а-я]+(?:\s+[А-Я][а-я]+)*)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1).strip()
    
    clean_text = text
    clean_text = re.sub(r'^(Спутник|Электричка|Иволга|Ласточка)', '', clean_text)
    clean_text = re.sub(r'\d{4}', '', clean_text)
    clean_text = re.sub(r'\b\d{1,2}:\d{2}\b', '', clean_text)
    clean_text = re.sub(r'\b(Будни|Ежедневно)\b', '', clean_text)
    clean_text = re.sub(r'\s+', ' ', clean_text).strip()
    
    if len(clean_text) > 50:
        parts = re.split(r'\d{1,2}:\d{2}', clean_text)
        if parts:
            clean_text = parts[0].strip()
    
    return clean_text if clean_text else "Маршрут не определен"

def parse_schedule(html_file, day_filter=None):
    with open(html_file, 'r', encoding='utf-8') as file:
        html_content = file.read()
    
    soup = BeautifulSoup(html_content, 'html.parser')
    trains = []
    
    rows = soup.find_all('tr', class_=re.compile(r'gBhE1wA30JAwoPLW'))
    
    for row in rows:
        text = row.get_text(strip=True)
        
        if any(word in text for word in ['Маршрут', 'Отправление', 'Дни следования']):
            continue
            
        time_match = re.search(r'\b\d{1,2}:\d{2}\b', text)
        if not time_match:
            continue
            
        time = time_match.group()
        route = extract_route(text)
        
        days = "ежедневно"
        if 'Будни' in text:
            days = "будни"
        elif 'Ежедневно' in text:
            days = "ежедневно"
        
        if day_filter and days != day_filter:
            continue
            
        trains.append({
            'departure_time': time,
            'route': route,
            'days': days
        })
    
    if not trains:
        all_text = soup.get_text()
        pattern = r'([А-Я][^—]+—[^—]+?)\s*(\d{1,2}:\d{2})\s*(Будни|Ежедневно)'
        matches = re.findall(pattern, all_text)
        
        for route, time, days_text in matches:
            days = "будни" if "Будни" in days_text else "ежедневно"
            
            if day_filter and days != day_filter:
                continue
                
            trains.append({
                'departure_time': time,
                'route': route.strip(),
                'days': days
            })
    
    return trains

def main():
    parser = argparse.ArgumentParser(description='Парсер расписания электричек')
    parser.add_argument('--filter', choices=['будни', 'ежедневно'], 
                       help='Фильтр по дням: будни или ежедневно')
    
    args = parser.parse_args()
    
    try:
        trains = parse_schedule('schedule.html', args.filter)
        
        if not trains:
            print("Данные не найдены")
            return
        
        trains.sort(key=lambda x: x['departure_time'])
        
        print(f"Найдено рейсов: {len(trains)}")
        if args.filter:
            print(f"Фильтр: {args.filter}")
        
        for i, train in enumerate(trains, 1):
            print(f"{i:2d}. {train['departure_time']} | {train['route']} | {train['days']}")
        
        with open('schedule.json', 'w', encoding='utf-8') as f:
            json.dump(trains, f, ensure_ascii=False, indent=2)
            
        print("Результат сохранен в schedule.json")
        
    except Exception as e:
        print(f"Ошибка: {e}")

if __name__ == "__main__":
    main()