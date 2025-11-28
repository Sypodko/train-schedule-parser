import json
import argparse
from bs4 import BeautifulSoup
import re

def parse_schedule_clean(html_file, day_filter=None):
    """
    Чистый парсер с правильным извлечением маршрутов
    """
    with open(html_file, 'r', encoding='utf-8') as file:
        html_content = file.read()
    
    soup = BeautifulSoup(html_content, 'html.parser')
    trains = []
    
    print("🔍 Анализ расписания...")
    
    # Находим все строки таблицы с классом gBhE1wA30JAwoPLW
    schedule_rows = soup.find_all('tr', class_='gBhE1wA30JAwoPLW')
    
    for row in schedule_rows:
        try:
            text = row.get_text(strip=True)
            
            # Пропускаем заголовки
            if any(word in text for word in ['Маршрут', 'Отправление', 'Дни следования']):
                continue
            
            # Ищем время
            time_match = re.search(r'\b\d{1,2}:\d{2}\b', text)
            if not time_match:
                continue
                
            time = time_match.group()
            
            # ЧИСТЫЙ поиск маршрута - ищем паттерн "Станция — Станция"
            route = "Маршрут не определен"
            
            # Паттерн 1: "Москва Ярославская — Монино"
            route_match = re.search(r'([А-Я][а-я]+(?:\s+[А-Я][а-я]+)*\s*—\s*[А-Я][а-я]+(?:\s+[А-Я][а-я]+)*)', text)
            if route_match:
                route = route_match.group(1).strip()
            else:
                # Паттерн 2: Ищем текст между типом поезда и номером/временем
                # Убираем тип поезда, номер, время
                clean_text = re.sub(r'^(Спутник|Электричка|Иволга|Ласточка)', '', text)
                clean_text = re.sub(r'\d{4}', '', clean_text)  # Номер поезда
                clean_text = re.sub(r'\b\d{1,2}:\d{2}\b', '', clean_text)  # Время
                clean_text = re.sub(r'\b(Будни|Ежедневно)\b', '', clean_text)  # Дни
                route = clean_text.strip()
                
                # Если маршрут слишком длинный, обрезаем
                if len(route) > 50:
                    # Ищем вхождение " — " как разделитель маршрута
                    if ' — ' in route:
                        parts = route.split(' — ')
                        if len(parts) >= 2:
                            route = parts[0] + ' — ' + parts[1]
            
            # Определяем дни
            days = "ежедневно"
            if 'Будни' in text:
                days = "будни"
            elif 'Ежедневно' in text:
                days = "ежедневно"
            
            # Применяем фильтр
            if day_filter and days != day_filter:
                continue
                
            trains.append({
                'departure_time': time,
                'route': route,
                'days': days
            })
            
        except Exception as e:
            continue
    
    return trains

def main():
    parser = argparse.ArgumentParser(description='Чистый парсер расписания электричек')
    parser.add_argument('--filter', choices=['будни', 'ежедневно'], 
                       help='Фильтр по дням: будни или ежедневно')
    
    args = parser.parse_args()
    
    try:
        trains = parse_schedule_clean('schedule.html', args.filter)
        
        if not trains:
            print("❌ Не удалось извлечь данные.")
            return
        
        # Сортируем по времени
        trains.sort(key=lambda x: x['departure_time'])
        
        print(f"\n🎉 Найдено рейсов: {len(trains)}")
        if args.filter:
            print(f"📅 Фильтр: {args.filter}")
        print("=" * 70)
        
        for i, train in enumerate(trains, 1):
            print(f"{i:2d}. ⏰ {train['departure_time']} | 🚆 {train['route']} | 📅 {train['days']}")
        
        # Сохраняем в JSON
        with open('schedule.json', 'w', encoding='utf-8') as f:
            json.dump(trains, f, ensure_ascii=False, indent=2)
            
        print(f"\n✅ Результат сохранен в schedule.json")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    main()