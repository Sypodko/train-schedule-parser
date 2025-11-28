import json
import argparse
from bs4 import BeautifulSoup
import re

def parse_schedule(html_file, day_filter=None):
    """
    Парсер расписания электричек для актуальной структуры Туту.ру
    """
    with open(html_file, 'r', encoding='utf-8') as file:
        html_content = file.read()
    
    soup = BeautifulSoup(html_content, 'html.parser')
    trains = []
    
    print("🔍 Поиск расписания электричек...")
    
    # Находим все строки таблицы с расписанием
    schedule_rows = soup.find_all('tr', class_='gBhE1wA30JAwoPLW')
    
    print(f"Найдено строк расписания: {len(schedule_rows)}")
    
    for row in schedule_rows:
        try:
            # Получаем весь текст строки
            row_text = row.get_text(strip=True)
            
            # Ищем время отправления (формат ЧЧ:ММ)
            time_match = re.search(r'\b\d{1,2}:\d{2}\b', row_text)
            if not time_match:
                continue
                
            departure_time = time_match.group()
            
            # Извлекаем маршрут - текст между названием поезда и временем/номером
            # Убираем лишние части из текста
            clean_text = re.sub(r'\d{4}', '', row_text)  # Убираем номера поездов
            clean_text = re.sub(r'\b\d{1,2}:\d{2}\b', '', clean_text)  # Убираем время
            
            # Разделяем текст на части и находим маршрут
            parts = clean_text.split()
            route_parts = []
            
            # Ищем части, которые выглядят как станции (содержат дефис или длинные слова)
            for part in parts:
                if '-' in part or len(part) > 4:
                    route_parts.append(part)
            
            route = ' '.join(route_parts) if route_parts else "Маршрут не определен"
            
            # Определяем дни следования
            days_info = "ежедневно"
            if 'Будни' in row_text:
                days_info = "будни"
            elif 'Ежедневно' in row_text:
                days_info = "ежедневно"
            elif 'Выходные' in row_text or 'Суббот' in row_text or 'Воскресен' in row_text:
                days_info = "выходные"
            
            # Применяем фильтр по дням
            if day_filter and days_info != day_filter:
                continue
            
            train_info = {
                'departure_time': departure_time,
                'route': route,
                'days': days_info
            }
            
            trains.append(train_info)
            
        except Exception as e:
            print(f"Ошибка при обработке строки: {e}")
            continue
    
    return trains

def parse_schedule_advanced(html_file, day_filter=None):
    """
    Альтернативный метод парсинга - более точный
    """
    with open(html_file, 'r', encoding='utf-8') as file:
        html_content = file.read()
    
    soup = BeautifulSoup(html_content, 'html.parser')
    trains = []
    
    # Ищем все div и tr элементы, которые содержат расписание
    elements = soup.find_all(['div', 'tr'], class_=True)
    
    for element in elements:
        element_text = element.get_text(strip=True)
        
        # Проверяем, что это строка с расписанием (содержит время и маршрут)
        if not re.search(r'\b\d{1,2}:\d{2}\b', element_text):
            continue
            
        # Пропускаем заголовки таблицы
        if any(word in element_text for word in ['Маршрут', 'Отправление', 'Дни следования']):
            continue
        
        try:
            # Извлекаем время
            time_match = re.search(r'\b\d{1,2}:\d{2}\b', element_text)
            departure_time = time_match.group() if time_match else "00:00"
            
            # Извлекаем маршрут - более точный метод
            # Убираем номера поездов, время и служебные слова
            clean_text = re.sub(r'\d{4}', '', element_text)  # Номера поездов
            clean_text = re.sub(r'\b\d{1,2}:\d{2}\b', '', clean_text)  # Время
            clean_text = re.sub(r'\b(Спутник|Электричка|Иволга|Ласточка)\b', '', clean_text)  # Типы поездов
            clean_text = re.sub(r'\s+', ' ', clean_text).strip()  # Лишние пробелы
            
            # Маршрут - оставшийся текст
            route = clean_text if clean_text else "Маршрут не определен"
            
            # Определяем дни
            days_info = "ежедневно"
            if 'Будни' in element_text:
                days_info = "будни"
            elif 'Ежедневно' in element_text:
                days_info = "ежедневно"
            
            # Применяем фильтр
            if day_filter and days_info != day_filter:
                continue
                
            train_info = {
                'departure_time': departure_time,
                'route': route,
                'days': days_info
            }
            
            # Проверяем, что это валидный рейс
            if (departure_time != "00:00" and 
                route != "Маршрут не определен" and
                len(route) > 5):
                trains.append(train_info)
                
        except Exception as e:
            continue
    
    return trains

def main():
    parser = argparse.ArgumentParser(description='Парсер расписания электричек')
    parser.add_argument('--filter', choices=['будни', 'ежедневно'], 
                       help='Фильтр по дням: будни или ежедневно')
    
    args = parser.parse_args()
    
    try:
        # Пробуем оба метода парсинга
        trains1 = parse_schedule('schedule.html', args.filter)
        trains2 = parse_schedule_advanced('schedule.html', args.filter)
        
        # Объединяем результаты, убирая дубликаты
        all_trains = trains1 + trains2
        unique_trains = []
        seen = set()
        
        for train in all_trains:
            key = (train['departure_time'], train['route'])
            if key not in seen:
                seen.add(key)
                unique_trains.append(train)
        
        if not unique_trains:
            print("❌ Рейсы не найдены.")
            return
        
        # Сортируем по времени
        unique_trains.sort(key=lambda x: x['departure_time'])
        
        print(f"\n🎉 Найдено рейсов: {len(unique_trains)}")
        if args.filter:
            print(f"📅 Фильтр: {args.filter}")
        print("=" * 70)
        
        for train in unique_trains:
            print(f"⏰ {train['departure_time']} | 🚆 {train['route']} | 📅 {train['days']}")
        
        # Сохраняем в JSON
        with open('schedule.json', 'w', encoding='utf-8') as f:
            json.dump(unique_trains, f, ensure_ascii=False, indent=2)
            
        print(f"\n✅ Результат сохранен в schedule.json")
        
    except FileNotFoundError:
        print("❌ Файл schedule.html не найден!")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    main()