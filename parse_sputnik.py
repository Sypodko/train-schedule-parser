import requests
from bs4 import BeautifulSoup
import argparse
import re

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--filter', choices=['будни', 'ежедневно'])
    args = parser.parse_args()
    
    response = requests.get('https://www.tutu.ru/station.php?nnst=45807')
    soup = BeautifulSoup(response.text, 'html.parser')

    print("РАСПИСАНИЕ ЭЛЕКТРИЧЕК")
    if args.filter:
        print(f"ФИЛЬТР: {args.filter}")
    print("====================")

    trains = []
    
    for item in soup.find_all(['tr', 'div']):
        text = item.get_text()
        
        if ':' in text and 'Москва' in text and ' — ' in text:
            time_match = re.search(r'\d{1,2}:\d{2}', text)
            if time_match:
                time = time_match.group()
                
                route_match = re.search(r'Москва.*?—.*?[А-Яа-я]+', text)
                if route_match:
                    route = route_match.group()
                    route = re.sub(r'Ярославская', '', route)
                    route = re.sub(r'\s+', ' ', route).strip()
                    if len(route) < 30:
                        days = 'ежедневно'
                        parent_text = item.parent.get_text() if item.parent else text
                        if 'Будни' in parent_text:
                            days = 'будни'
                        elif 'Ежедневно' in parent_text:
                            days = 'ежедневно'
                        
                        if args.filter and days != args.filter:
                            continue
                            
                        train = f"{time} | {route} | {days}"
                        if train not in trains:
                            trains.append(train)
    
    for train in trains:
        print(train)

if __name__ == "__main__":
    main()