from bs4 import BeautifulSoup

with open('schedule.html', 'r', encoding='utf-8') as file:
    html_content = file.read()

soup = BeautifulSoup(html_content, 'html.parser')

print("=== АНАЛИЗ СТРУКТУРЫ HTML ===")

# Ищем все div элементы
print("\n1. Все div с классами:")
divs = soup.find_all('div', class_=True)
for div in divs[:10]:  # Первые 10 div
    classes = div.get('class', [])
    if classes:
        print(f"Классы: {classes}")

# Ищем таблицы
print("\n2. Таблицы:")
tables = soup.find_all('table')
print(f"Найдено таблиц: {len(tables)}")

# Ищем элементы с временем
print("\n3. Элементы с временем:")
time_elements = soup.find_all(text=lambda text: text and ':' in text and len(text) <= 5)
for time in time_elements[:10]:
    print(f"Время: {time}")

# Ищем ссылки с маршрутами
print("\n4. Ссылки:")
links = soup.find_all('a')
for link in links[:10]:
    href = link.get('href', '')
    text = link.get_text(strip=True)
    if text and len(text) > 3:
        print(f"Текст: {text} | Ссылка: {href}")

print("\n5. Структура заголовков:")
headers = soup.find_all(['h1', 'h2', 'h3', 'h4'])
for header in headers:
    print(f"{header.name}: {header.get_text(strip=True)}")