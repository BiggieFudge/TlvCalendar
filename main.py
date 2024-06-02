from bs4 import BeautifulSoup
import requests
import re
from datetime import datetime
import pandas as pd

# Initialize an empty DataFrame
events_database = pd.DataFrame(columns=["Subject", "Start date", "End date", "Start time", "End time"])

# Dictionary mapping Hebrew months to their corresponding numbers
hebrew_months = {
    'ינואר': '01',
    'פברואר': '02',
    'מרץ': '03',
    'אפריל': '04',
    'מאי': '05',
    'יוני': '06',
    'יולי': '07',
    'אוגוסט': '08',
    'ספטמבר': '09',
    'אוקטובר': '10',
    'נובמבר': '11',
    'דצמבר': '12'
}

def extract_date(date_str):
    date_pattern = r'\b(ינואר|פברואר|מרץ|אפריל|מאי|יוני|יולי|אוגוסט|ספטמבר|אוקטובר|נובמבר|דצמבר) (\d{1,2}), (\d{4})\b'
    dates = re.findall(date_pattern, date_str)
    hebrew_month, day, year = dates[0]
    month_number = hebrew_months[hebrew_month]
    return f"{month_number}/{int(day):02d}/{year}"

def extract_time(start_time):
    end_time = '{:02d}:{:02d}'.format(*((23, 59) if (int(start_time[:2]) + 4) > 23 else ((int(start_time[:2]) + 4), int(start_time[3:]))))
    return end_time

url = 'https://www.sportpalace.co.il/bloomfield/%D7%9C%D7%95%D7%97-%D7%90%D7%A8%D7%95%D7%A2%D7%99%D7%9D/'
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0",
}


response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.content, 'html.parser')

event_cells = soup.find_all('td', class_='has-events')

next_page_link = soup.find('li', class_="my-calendar-next").a['href']
response = requests.get(next_page_link, headers=headers)
soup = BeautifulSoup(response.content, 'html.parser')
event_cells += soup.find_all('td', class_='has-events')

for event in event_cells:
    date_str = event.find('span', class_='mc-date').get_text(strip=True)
    start_time = event.text.split('\n')[-5]
    formatted_date = extract_date(date_str)
    end_time = extract_time(start_time)
    description = event.find('div', class_="longdesc").text

    new_event= {
        "Subject": description,
        "Start date": formatted_date,
        "End date": formatted_date,
        "Start time": start_time,
        "End time": end_time,
    }
    events_database = events_database.append(new_event, ignore_index=True)

file_name = "Bloomfield_Events-" + events_database.iloc[0]['Start date'][0:2] +  "-"  +events_database.iloc[-1]['Start date'][0:2]
events_database.to_csv(file_name + ".csv", index=False, encoding='utf-8-sig')

print(events_database)