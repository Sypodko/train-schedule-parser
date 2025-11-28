import json
import argparse
from bs4 import BeautifulSoup
import re

def parse_schedule(html_file, day_filter=None):
    """
    Улучшенный парсер расписания электричек
    """
    with open(html_file, 'r', encoding='utf-8') as file:
        html_content = file.read()
    
    soup = BeautifulSoup(html_content, 'html.parser')
    trains = []
    
    print("Поиск расписания...")
    
    # Различные возможные селекторы для расписания
    possible_selectors = [
        'div.schedule-item',
        'div.train-item', 
        'tr.train-row',
        'div.g-hidden',
        'div[class*="train"]',
        'div[class*="schedule"]',
        'tr[class*="train"]',
        'table tr'  # Все строки таблиц
    ]
    
    # Попробуем найти расписание разными способами
    schedule_items = []
    
    for selector in possible_selectors:
        items = soup.select(selector)
        if items:
            print(f"Найдено элементов с селектором '{selector}': {len(items)}")
            schedule_items.extend(items)
    
    # Если не нашли по селекторам, ищем по структуре
    if not schedule_items:
        # Ищем все элементы, которые могут содержать время
        all_elements = soup.find_all(['div', 'tr', 'li'])
        schedule_items = [el for el in all_elements if len(el.get_text(strip=True)) > 10]
        print(f"Найдено потенциальных элементов: {len(schedule_items)}")
    
    for i, item in enumerate(schedule_items[:20]):  # Проверим первые 20 элементов
        try:
            print(f"\n--- Элемент {i+1} ---")
            print(f"Классы: {item.get('class', [])}")
            print(f"Текст: {item.get_text(strip=True)[:100]}...")
            
            # Ищем время (формат ЧЧ:ММ)
            time_pattern = r'\b\d{1,2}:\d{2}\b'
            time_match = re.search(time_pattern, item.get_text())
            
            if time_match:
                departure_time = time_match.group()
                print(f"Найдено время: {departure_time}")
                
                # Ищем маршрут (текст между временем и следующими цифрами/спецсимволами)
                route_text = item.get_text()
                
                # Упрощенный поиск маршрута
                route = "Маршрут не определен"
                
                # Ищем текст после времени
                time_pos = route_text.find(departure_time)
                if time_pos != -1:
                    after_time = route_text[time_pos + len(departure_time):].strip()
                    # Берем первые 50 символов после времени как маршрут
                    route = after_time[:50].strip()
                
                # Определяем дни
                days_info = "ежедневно"
                days_text = item.get_text().lower()
                
                if any(word in days_text for word in ['будни', 'пн-пт', 'рабоч', 'понедельник-пятница']):
                    days_info = "будни"
                elif any(word in days_text for word in ['ежедневно', 'ежедн', 'кажд', 'все дни']):
                    days_info = "ежедневно"
                elif any(word in days_text for word in ['выходн', 'сб-вс', 'суббот', 'воскресен']):
                    days_info = "выходные"
                
                # Применяем фильтр
                if day_filter and days_info != day_filter:
                    continue
                
                train_info = {
                    'departure_time': departure_time,
                    'route': route,
                    'days': days_info
                }
                
                trains.append(train_info)
                print(f"✅ Добавлен рейс: {departure_time} - {route} - {days_info}")
                
        except Exception as e:
            print(f"Ошибка при обработке элемента: {e}")
            continue
    
    return trains

def main():
    parser = argparse.ArgumentParser(description='Улучшенный парсер расписания электричек')
    parser.add_argument('--filter', choices=['будни', 'ежедневно'], 
                       help='Фильтр по дням: будни или ежедневно')
    
    args = parser.parse_args()
    
    try:
        trains = parse_schedule('schedule.html', args.filter)
        
        if not trains:
            print("\n❌ Рейсы не найдены. Возможные причины:")
            print("1. Структура страницы сильно изменилась")
            print("2. Нужно использовать другие селекторы")
            print("3. Страница требует JavaScript для отображения данных")
            return
        
        print(f"\n🎉 Найдено рейсов: {len(trains)}")
        print("=" * 80)
        
        for train in trains:
            print(f"⏰ {train['departure_time']} | 🚆 {train['route']} | 📅 {train['days']}")
        
        # Сохраняем в JSON
        with open('schedule.json', 'w', encoding='utf-8') as f:
            json.dump(trains, f, ensure_ascii=False, indent=2)
            
        print(f"\n✅ Результат сохранен в schedule.json")
        
    except FileNotFoundError:
        print("❌ Файл schedule.html не найден!")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    main()