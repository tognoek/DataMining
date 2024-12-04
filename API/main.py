from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime
import os
from flask import Flask, request, jsonify
from flask_cors import CORS

load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL")
MONGODB_NAME = os.getenv("MONGODB_NAME")
MONGODB_NGUYENHUE = os.getenv("MONGODB_NGUYENHUE")
MONGODB_COUNT_MONTH = os.getenv("MONGODB_COUNT_MONTH")

app = Flask(__name__)
CORS(app)

client = MongoClient(MONGODB_URL)  
db = client[MONGODB_NAME] 
collection_nguyenhue = db[MONGODB_NGUYENHUE]
collection_count_month = db[MONGODB_COUNT_MONTH]

def create_query_year_nguyenhue(year):
    start_date = f"{year}/01/01"
    end_date = f"{year+1}/01/01"
    query = {"date": {"$gte": start_date, "$lt": end_date}}
    return query

def create_query_month_nguyenhue(year, month):
    start_date = f"{year}/{month:02d}/01" 
    next_month = month + 1 if month < 12 else 1
    next_year = year if month < 12 else year + 1
    end_date = f"{next_year}/{next_month:02d}/01"
    query = {"date": {"$gte": start_date, "$lt": end_date}}
    return query

def create_query_month_count_month(year, month):
    query = {
            "year": year,
            "month": month
        }
    return query
def create_query_hour_nguyenhue(date, hour):
    start_time = f"{hour}:00"
    end_time = f"{hour}:59"
    
    query = {
        "date": date,
        "time": {
            "$gte": start_time,
            "$lte": end_time
        }
    }
    return query

def create_query_year_month_day(date):
    query = {
        "date": date,
    }
    return query

def execution_query_nguyenhue(query):
    cursor = collection_nguyenhue.find(query)
    result = []
    for document in cursor:
        document['_id'] = str(document['_id'])
        result.append(document)
    return result
def execution_query_count_month(query):
    cursor = collection_count_month.find(query)
    result = []
    for document in cursor:
        document['_id'] = str(document['_id'])
        result.append(document)
    return result
def insert(date, time, car_left, car_right, car_stand, car_speed, motorbike_left, motorbike_right, motorbike_stand, motorbike_speed, temper, rain):
    data_dict = {
        "date":  date,
        "time": time,
        "car_left": car_left,
        "car_right": car_right,
        "car_stand": car_stand,
        "car_speed": car_speed,
        "motorbike_left": motorbike_left,
        "motorbike_right": motorbike_right,
        "motorbike_stand": motorbike_stand,
        "motorbike_speed": motorbike_speed,
        "temper": temper,
        "rain": rain
    }
    collection_nguyenhue.insert_one(data_dict)
    
def insert_count_month(year, month, hour, car, motorbike):
    data_dict = {
        "year":  year,
        "month":  month,
        "hour": hour,
        "car": car,
        "motorbike": motorbike
    }
    collection_count_month.insert_one(data_dict)
    
@app.route('/')
# Cái này của [tognoek]
def home():
    return "Welcome to the Home Page By Tognoek"

@app.route('/api/year_month_day_hour_count_car_motorbike_all', methods=['GET'])
# Lấy ra dữ liệu lượng xe ô tô và xe máy di chuyển của một giờ trong ngày
def get_data_by_hour_in_db_nguyenhue():
    date = request.args.get('date', None) 
    hour = request.args.get('hour', None) 
    if date and hour:
        query = create_query_hour_nguyenhue(date, int(hour))
        print(query)
        data = execution_query_nguyenhue(query)
        if data:
            result = []
            for item in data:
                minute = int(item['time'].split(':')[1])
                count_car = item['car_left'] + item['car_right']
                count_motorbike = item['motorbike_left'] + item['motorbike_right']
                result.append({
                    'hour': hour,
                    'minute': minute,
                    'car': count_car,
                    'motorbike': count_motorbike,
                    'temper': item['temper'],
                    'rain': item['rain']
                })
            return jsonify(result)
        else:
            return jsonify({"error": "No data found"}), 404
    return jsonify({"error": "Missing both parameters"}), 400


@app.route('/api/year_month_day_car_motorbike', methods=['GET'])
# Lấy ra dữ liệu lượng xe ô tô và xe máy di chuyển trái phải của một ngày trong năm
def get_data_by_day_in_db_nguyenhue():
    date = request.args.get('date', None) 
    hour = request.args.get('hour', None) 
    if date and hour:
        query = create_query_hour_nguyenhue(date, int(hour))
        print(query)
        data = execution_query_nguyenhue(query)
        if data:
            result = []
            for item in data:
                result.append({
                    'car_left': item['car_left'],
                    'car_right': item['car_right'],
                    'car_stand': item['car_stand'],
                    'motorbike_left': item['motorbike_left'],
                    'motorbike_right': item['motorbike_right'],
                    'motorbike_stand': item['motorbike_stand'],
                    'tempr': item['temper'],
                    'rain': item['rain']
                })
            return jsonify(result)
        else:
            return jsonify({"error": "No data found"}), 404
    return jsonify({"error": "Missing both parameters"}), 400

@app.route('/api/year_month_count_car_motorbike_all', methods=['GET'])
# Lấy ra dữ liệu lượng xe di chuyern của một tháng trong năm
def get_data():
    year = request.args.get('year', None) 
    month = request.args.get('month', None) 
    if year and month:
        query = create_query_month_nguyenhue(int(year), int(month))
        data = execution_query_nguyenhue(query)
        if data:
            result = []
            for item in data:
                hour = int(item['time'].split(':')[0])
                minute = int(item['time'].split(':')[1])
                count_car = item['car_left'] + item['car_right']
                count_motorbike = item['motorbike_left'] + item['motorbike_right']
                result.append({
                    'date': item['date'],
                    'hour': hour,
                    'minute': minute,
                    'car': count_car,
                    'motorbike': count_motorbike
                })
            return jsonify(result)
        else:
            return jsonify({"error": "No data found"}), 404
    return jsonify({"error": "Missing both parameters"}), 400

@app.route('/api/year_month_count_car_motorbike', methods=['GET'])
# Lấy dữ liệu lượng xe ô tô và di chuyển của một tháng trông năm đã đưọc tính tổng lại
def api_get_year_month_count_car_motorbike():
    year = request.args.get('year', None) 
    month = request.args.get('month', None) 
    if year and month:
        query = create_query_month_count_month(int(year), int(month))
        data = execution_query_count_month(query)
        if data:
            result = []
            for item in data:
                result.append({
                    'hour': item["hour"],
                    'year': item["year"],
                    'month': item["month"],
                    'car': item["car"],
                    'motorbike': item["motorbike"]
                })
            return jsonify(result)
        else:
            return jsonify({"error": "No data found"}), 404
    return jsonify({"error": "Missing both parameters"}), 400


@app.route('/api/insert_count_month', methods=['POST'])
# Chèn dữ liệu vào bảng tổng xe di chuyển theo giờ của một tháng trong năm
def api_post_insert_count_month():
    try:
        data = request.get_json()
        year = data.get('year')
        month = data.get('month')
        hour = data.get('hour')
        car = data.get('car')
        motorbike = data.get('motorbike')

        if not all([year, month, hour, car, motorbike]):
            return jsonify({"error": "Thiếu dữ liệu đầu vào"}), 400
        insert_count_month(year, month, hour, car, motorbike)

        return jsonify({"message": "Dữ liệu đã được chèn thành công!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
if __name__ == '__main__':
    app.run(debug=True)