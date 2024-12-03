import requests
import json
import pandas as pd

# Xử lý dữ liệu ở đây
# Set time để tạo mỗi ngày

url = 'http://127.0.0.1:5000/api/year_month_count_car_motorbike_all'
params = {
    'year': 2023,
    'month': 3
}
response = requests.get(url, params=params)
if response.status_code == 200:
    datas = response.json()
    df = pd.DataFrame(datas)
    df_grouped = df.groupby('hour', as_index=False).sum()
    url = 'http://127.0.0.1:5000/api/insert_count_month'
    for _, data in df_grouped.iterrows():
        year = int(data['date'].split('/')[0])
        month = int(data['date'].split('/')[1])
        data = {
            "year": year,
            "month": month,
            "hour": int(data['hour']),
            "car": int(data['car']),
            "motorbike": int(data['motorbike'])
        }
        response = requests.post(url, json=data)
else:
    print("Lỗi khi gửi GET request:", response.status_code)
