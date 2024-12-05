import requests
import pandas as pd
from datetime import datetime
import time

def fetch_data(url, params):
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Lỗi GET request: {params}, Status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"Lỗi khi gửi GET request: {e}, Params: {params}")
        return None
    
def post_data(url, data):
    try:
        response = requests.post(url, json=data)
        if response.status_code == 200:
            print(f"POST thành công: {data}")
        else:
            print(f"Lỗi POST request: {data}, Status code: {response.status_code}")
    except Exception as e:
        print(f"Lỗi khi gửi POST request: {e}, Data: {data}")
        
def process(year, month, url_get, url_post):
    params = {
        'year': year,
        'month': month
    }
    datas = fetch_data(url_get, params)
    if datas:
            df = pd.DataFrame(datas)
            df_grouped = df.groupby('hour', as_index=False).sum()
            for _, data in df_grouped.iterrows():
                year = int(data['date'].split('/')[0])
                month = int(data['date'].split('/')[1])
                post_payload = {
                    "year": year,
                    "month": month,
                    "hour": int(data['hour']),
                    "car": int(data['car']),
                    "motorbike": int(data['motorbike'])
                }
                post_data(url_post, post_payload)


def count_car_motorbike_month(year, month):
    url_get = 'http://127.0.0.1:8000/api/year_month_count_car_motorbike_all'
    url_post = 'http://127.0.0.1:8000/api/insert_count_month'
    print('Tạo dữ liệu theo tháng về số lượng xe di chuyển')
    process(year, month, url_get, url_post)

def loop():
    last_month = 12
    last_year = 2024
    while True:
        print("IS RUN")
        current_time = datetime.now()
        current_day = current_time.day     
        current_month = current_time.month  
        current_minute = current_time.minute 
        current_second = current_time.second
        if last_month != current_month:
            if last_month == 12:
                last_year += 1
            last_month = current_day
            count_car_motorbike_month(last_year, last_month)
        time.sleep(10)

if __name__ == "__main__":
    loop()
