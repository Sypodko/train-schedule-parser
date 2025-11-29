import requests

url = "https://www.tutu.ru/station.php?nnst=45807"
response = requests.get(url)

with open('schedule.html', 'w', encoding='utf-8') as file:
    file.write(response.text)

print("Страница сохранена как schedule.html")