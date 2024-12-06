import requests
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import MinMaxScaler
from datetime import datetime, timedelta
from collections import defaultdict
import time
from flask import Flask, request, jsonify
from flask_cors import CORS
import threading


app = Flask(__name__)

CORS(app, resources={r"*": {"origins": "*"}}) 

def get_data_from_api(date):
    url = f'http://127.0.0.1:5000/api/year_month_day_car_motorbike?date={date}'
    print(url)
    response = requests.get(url)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        return None

def calculate_ratios(data):
    total_car_left = sum(item['car_left'] for item in data)
    total_car_right = sum(item['car_right'] for item in data)
    total_motorbike_left = sum(item['motorbike_left'] for item in data)
    total_motorbike_right = sum(item['motorbike_right'] for item in data)
    
    total_car_stand = sum(item['car_stand'] for item in data)
    total_motorbike_stand = sum(item['motorbike_stand'] for item in data)
    
    total_car_moving = total_car_left + total_car_right
    total_motorbike_moving = total_motorbike_left + total_motorbike_right

    car_left_ratio = total_car_left / total_car_moving if total_car_moving != 0 else 0
    car_right_ratio = total_car_right / total_car_moving if total_car_moving != 0 else 0
    motorbike_left_ratio = total_motorbike_left / total_motorbike_moving if total_motorbike_moving != 0 else 0
    motorbike_right_ratio = total_motorbike_right / total_motorbike_moving if total_motorbike_moving != 0 else 0
    
    car_stand_ratio = total_car_stand / (total_car_stand + total_car_moving) if total_car_stand + total_car_moving != 0 else 0
    motorbike_stand_ratio = total_motorbike_stand / (total_motorbike_stand + total_motorbike_moving) if total_motorbike_stand + total_motorbike_moving != 0 else 0
    
    return {
        "car_left_ratio": car_left_ratio,
        "car_right_ratio": car_right_ratio,
        "motorbike_left_ratio": motorbike_left_ratio,
        "motorbike_right_ratio": motorbike_right_ratio,
        "car_stand_ratio": car_stand_ratio,
        "motorbike_stand_ratio": motorbike_stand_ratio
    }

def aggregate_data_by_hour(data):
    hourly_data = defaultdict(list)
    for item in data:
        hour = item['hour']
        hourly_data[hour].append(item)
    
    return hourly_data
def save_data_to_db(data):
    url = "http://127.0.0.1:5000/api/insert_rate_left_right"
    response = requests.post(url, json=data)
    
    if response.status_code == 200:
        print(f"Data for hour {data['hour']} saved successfully")
    else:
        print(f"Failed to save data for hour {data['hour']}: {response.status_code}")

def process_and_save_data(date):
    data = get_data_from_api(date)
    if not data:
        print(f"No data found for {date}")
        return
    hourly_data = aggregate_data_by_hour(data)
    for hour, hour_data in hourly_data.items():
        ratios = calculate_ratios(hour_data)
        record = {
            'year': hour_data[0]['year'],  
            'month': hour_data[0]['month'],
            'day': hour_data[0]['day'],
            'hour': hour,
            'car_left_ratio': ratios['car_left_ratio'],
            'car_right_ratio': ratios['car_right_ratio'],
            'motorbike_left_ratio': ratios['motorbike_left_ratio'],
            'motorbike_right_ratio': ratios['motorbike_right_ratio'],
            'car_stand_ratio': ratios['car_stand_ratio'],
            'motorbike_stand_ratio': ratios['motorbike_stand_ratio']
        }
        
        save_data_to_db(record)

def fetch_data_by_day(date):
    try:
        formatted_date = date.replace("/", "/")  
        
        params = {'date': formatted_date}
        response = requests.get("http://localhost:5000/api/year_month_day_speed_car_motorbike", params=params)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Không lấy được dữ liệu cho ngày {date}: {response.json()}")
            return []
    except Exception as e:
        print(f"Lỗi khi gọi API GET: {str(e)}")
        return []
def calculate_hourly_speed(data):
    df = pd.DataFrame(data)
    if df.empty:
        return []
    df['hour'] = df['hour'].astype(int)
    df['minute'] = df['minute'].astype(int)
    hourly_data = df.groupby('hour').agg({
        'car_speed': 'mean',
        'motorbike_speed': 'mean'
    }).reset_index()
    return hourly_data

def cluster_data(data, n_clusters=3):
    if data.empty:
        return []

    scaler = MinMaxScaler()
    scaled_data = scaler.fit_transform(data[['car_speed', 'motorbike_speed']])
    kmeans = KMeans(n_clusters=n_clusters, random_state=0)
    data['cluster_id'] = kmeans.fit_predict(scaled_data)
    return data
def save_cluster_to_db(date, clusters):
    try:
        year, month, day = map(int, date.split('-'))
        for _, row in clusters.iterrows():
            payload = {
                'year': year,
                'month': month,
                'day': day,
                'hour': int(row['hour']),  # Thêm giờ vào payload
                'cluster_id': int(row['cluster_id']),
                'car_speed': float(row['car_speed']),
                'motorbike_speed': float(row['motorbike_speed'])
            }
            response = requests.post("http://localhost:5000/api/insert_collision_clustering", json=payload)
            if response.status_code != 200:
                print(f"Lỗi khi lưu cụm vào DB: {response.json()}")
    except Exception as e:
        print(f"Lỗi khi gọi API POST: {str(e)}")

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

def clus(date_str):
    data = fetch_data_by_day(date_str)
        
    if data:
        hourly_speed = calculate_hourly_speed(data)
        if not hourly_speed.empty:
            clustered_data = cluster_data(hourly_speed)
            save_cluster_to_db(date_str, clustered_data)
        else:
            print(f"Không có dữ liệu trung bình cho ngày {date_str}.")
    else:
        print(f"Không có dữ liệu nào cho ngày {date_str}.")

def run_in_thread(target, *args):
    thread = threading.Thread(target=target, args=args)
    thread.start()

def loop():
    last_month = 12
    last_year = 2024
    last_day = 6
    while True:
        print("IS RUN")
        current_time = datetime.now()
        current_day = current_time.day     
        current_month = current_time.month  
        
        if last_month != current_month:
            if last_month == 12:
                last_year += 1
            last_month = current_month
            run_in_thread(count_car_motorbike_month, last_year, last_month)
        
        if last_day != current_day:
            date_str = f"{last_year}/{current_month}/{last_day}"
            run_in_thread(process_and_save_data, date_str)
            run_in_thread(clus, date_str)
            last_day = current_day
        
        time.sleep(10)
@app.route('/', methods=['GET'])
def ap_api():
    return 'Xin chao cac ban!! Day la nha cua minh'
@app.route('/api_create/callback', methods=['GET'])
def api_tognoek():
    key = request.args.get('key', None) 
    if key == 1:
        count_car_motorbike_month(2024, 11)
    if key == 2:
        process_and_save_data("2024/11/30")
    if key == 3:
        clus("2024/11/30")
    return 'Xin chao cac ban!!'
def start_loop():
    loop_thread = threading.Thread(target=loop)
    loop_thread.daemon = True
    loop_thread.start()
if __name__ == "__main__":
    start_loop()
    app.run(debug=True, host='0.0.0.0', port=5000) 
