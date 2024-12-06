from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
# import logging

load_dotenv()

# logging.basicConfig(
#     filename="logs/api.log",  
    # level=logging.INFO,      
#     format="%(asctime)s - %(levelname)s - %(message)s",  
#     datefmt="%Y-%m-%d %H:%M:%S",  
# )

# logging.info("Ứng dụng đã bắt đầu")

MONGODB_URL = os.getenv("MONGODB_URL")
MONGODB_NAME = os.getenv("MONGODB_NAME")
MONGODB_NGUYENHUE = os.getenv("MONGODB_NGUYENHUE")
MONGODB_COUNT_MONTH = os.getenv("MONGODB_COUNT_MONTH")
MONGODB_CLUS = os.getenv("MONGODB_CLUS")
MONGO_DB_RATE_LEFT_RIGHT = os.getenv("MONGO_DB_RATE_LEFT_RIGHT")
print(MONGODB_URL, MONGODB_NAME)
app = Flask(__name__)

CORS(app, resources={r"*": {"origins": "*"}}) 

client = MongoClient("mongodb://mongodb:27017/")

try:
    # Kiểm tra thông tin server
    client.admin.command('ping')
    print("Kết nối MongoDB thành công!")
except ConnectionError as e:
    print(f"Lỗi kết nối MongoDB: {e}")
except Exception as e:
    print(f"Có lỗi xảy ra: {e}")
    
db = client[MONGODB_NAME] 
collection_nguyenhue = db[MONGODB_NGUYENHUE]
collection_count_month = db[MONGODB_COUNT_MONTH]
collection_clustering = db[MONGODB_CLUS]
collection_rate_left_right = db[MONGO_DB_RATE_LEFT_RIGHT]

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
def create_query_year_month_day_int(date):
    query = {
        "year": int(date.split("/")[0]),
        "month":  int(date.split("/")[1]),
        "day":  int(date.split("/")[2]),
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
def execution_query_clustering(query):
    cursor = collection_clustering.find(query)
    result = []
    for document in cursor:
        document['_id'] = str(document['_id'])
        result.append(document)
    return result
def execution_query_rate(query):
    cursor = collection_rate_left_right.find(query)
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
    
def insert_collision_clustering(year, month, day, hour, cluster_id, car_speed, motorbike_speed):
    data_dict = {
        "year": year,
        "month": month,
        "day": day,
        "hour": hour,
        "cluster_id": cluster_id,
        "car_speed": car_speed,
        "motorbike_speed": motorbike_speed
    }
    collection_clustering.insert_one(data_dict)
    
def insert_rate_left_right(year, month, day, hour, car_left_ratio, car_right_ratio,
                           motorbike_left_ratio, motorbike_right_ratio, car_stand_ratio,
                           motorbike_stand_ratio):
    data_dict = {
        "year": year,
        "month": month,
        "day": day,
        "hour": hour,
        "car_left_ratio": car_left_ratio,
        "car_right_ratio": car_right_ratio,
        "motorbike_left_ratio": motorbike_left_ratio,
        "motorbike_right_ratio": motorbike_right_ratio,
        "car_stand_ratio": car_stand_ratio,
        "motorbike_stand_ratio": motorbike_stand_ratio
    }
    collection_rate_left_right.insert_one(data_dict)

@app.route('/')
# Cái này của [tognoek]
def home():
    return "Welcome to the Home Page By Tognoek"

@app.route('/api/year_month_day_hour_rate', methods=['GET'])
# Lấy ra dữ liệu lượng xe ô tô và xe máy di chuyển của một giờ trong ngày
def get_data_by_hour_in_db_rate():
    date = request.args.get('date', None) 
    if date:
        query = create_query_year_month_day_int(date)
        data = execution_query_rate(query)
        if data:
            result = []
            for item in data:
                result.append({
                    'year': item['year'],
                    'month': item['month'],
                    'day': item['day'],
                    'hour': item['hour'],
                    'car_left_ratio': item['car_left_ratio'],
                    'car_right_ratio': item['car_right_ratio'],
                    'motorbike_left_ratio': item['motorbike_left_ratio'],
                    'motorbike_right_ratio': item['motorbike_right_ratio'],
                    'car_stand_ratio': item['car_stand_ratio'],
                    'motorbike_stand_ratio': item['motorbike_stand_ratio']
                })
            return jsonify(result)
        else:
            return jsonify({"error": "No data found"}), 404
    # logging.error("Lỗi xảy ra trong ứng dụng")
    return jsonify({"error": "Missing both parameters"}), 400
@app.route('/api/year_month_day_hour_count_car_motorbike_all', methods=['GET'])
# Lấy ra dữ liệu lượng xe ô tô và xe máy di chuyển của một giờ trong ngày
def get_data_by_hour_in_db_nguyenhue_count_all():
    date = request.args.get('date', None) 
    hour = request.args.get('hour', None) 
    if date and hour:
        query = create_query_hour_nguyenhue(date, int(hour))
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
            # logging.error("Lỗi xảy ra trong ứng dụng")
            return jsonify({"error": "No data found"}), 404
    # logging.error("Lỗi xảy ra trong ứng dụng")
    return jsonify({"error": "Missing both parameters"}), 400


@app.route('/api/year_month_day_hour_car_motorbike', methods=['GET'])
# Lấy ra dữ liệu lượng xe ô tô và xe máy di chuyển trái phải của một giờ trong ngày
def get_data_by_hour_in_db_nguyenhue():
    date = request.args.get('date', None) 
    hour = request.args.get('hour', None) 
    if date and hour:
        query = create_query_hour_nguyenhue(date, int(hour))
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
            # logging.error("Lỗi xảy ra trong ứng dụng")
            return jsonify({"error": "No data found"}), 404
    # logging.error("Lỗi xảy ra trong ứng dụng")
    return jsonify({"error": "Missing both parameters"}), 400
@app.route('/api/year_month_day_car_motorbike', methods=['GET'])
# Lấy ra dữ liệu lượng xe ô tô và xe máy di chuyển trái phải của một ngày trong năm
def get_data_by_day_in_db_nguyenhue():
    date = request.args.get('date', None) 
    if date:
        query = create_query_year_month_day(date)
        data = execution_query_nguyenhue(query)
        print(data)
        if data:
            result = []
            for item in data:
                hour = int(item['time'].split(':')[0])
                result.append({
                    'year': int(item['date'].split('/')[0]),
                    'month': int(item['date'].split('/')[1]),
                    'day': int(item['date'].split('/')[2]),
                    'hour': hour,
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
            # logging.error("Lỗi xảy ra trong ứng dụng")
            return jsonify({"error": "No data found"}), 404
    # logging.error("Lỗi xảy ra trong ứng dụng")
    return jsonify({"error": "Missing both parameters"}), 400

@app.route('/api/year_month_day_speed_car_motorbike', methods=['GET'])
# Lấy ra dữ liệu tốc độ xe trong một ngày trong năm
def get_data_by_day_spped_in_db_nguyenhue():
    date = request.args.get('date', None) 
    if date:
        query = create_query_year_month_day(date)
        data = execution_query_nguyenhue(query)
        if data:
            result = []
            for item in data:
                hour = int(item['time'].split(':')[0])
                minute = int(item['time'].split(':')[1])
                result.append({
                    'car_speed': item['car_speed'],
                    'motorbike_speed': item['motorbike_speed'],
                    'minute': minute,
                    'hour': hour
                })
            return jsonify(result)
        else:
            # logging.error("Lỗi xảy ra trong ứng dụng")
            return jsonify({"error": "No data found"}), 404
    
    # logging.error("Lỗi xảy ra trong ứng dụng")
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
            # logging.error("Lỗi xảy ra trong ứng dụng")
            return jsonify({"error": "No data found"}), 404
    # logging.error("Lỗi xảy ra trong ứng dụng")
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
            # logging.error("Lỗi xảy ra trong ứng dụng")
            return jsonify({"error": "No data found"}), 404
    # logging.error("Lỗi xảy ra trong ứng dụng")
    return jsonify({"error": "Missing both parameters"}), 400

@app.route('/api/year_month_day_clustering_speed_time', methods=['GET'])
# Lấy dữ liệu phân cụm tốc độ theo thời gian
def api_get_year_month_date_clustering():
    date = request.args.get('date', None) 
    if date:
        query = create_query_year_month_day_int(date)
        data = execution_query_clustering(query)
        if data:
            result = []
            for item in data:
                result.append({
                    'hour': item["hour"],
                    'cluster': item["cluster_id"],
                    'car_speed': item["car_speed"],
                    'motorbike_speed': item["motorbike_speed"],
                })
            return jsonify(result)
        else:
            # logging.error("Lỗi xảy ra trong ứng dụng")
            return jsonify({"error": "No data found"}), 404
    # logging.error("Lỗi xảy ra trong ứng dụng")
    return jsonify({"error": "Missing both parameters"}), 400
@app.route('/api/insert', methods=['POST'])
# Chèn dữ liệu vào bảng chinh
def api_post_insert_big_data():
    try:
        data = request.get_json()
        date = data.get('date')
        time = data.get('time')
        car_left = data.get('car_left')
        car_right = data.get('car_right')
        car_stand = data.get('car_stand')
        car_speed = data.get('car_speed')
        motorbike_left = data.get('motorbike_left')
        motorbike_right = data.get('motorbike_right')
        motorbike_stand = data.get('motorbike_stand')
        motorbike_speed = data.get('motorbike_speed')
        temper = data.get('temper')
        rain = data.get('rain')
        insert(date, time, car_left, car_right, car_stand, car_speed, motorbike_left, motorbike_right, motorbike_stand, motorbike_speed, temper, rain)
        
        # logging.info("Chèn vào bảng chính thành công")
        return jsonify({"message": "Dữ liệu đã được chèn thành công!"}), 200
    except Exception as e:
        # logging.error("Lỗi xảy ra trong ứng dụng")
        return jsonify({"error": str(e)}), 500
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

        if not all([year, month, car, motorbike]):
            # logging.error("Lỗi xảy ra trong ứng dụng")
            return jsonify({"error": "Thiếu dữ liệu đầu vào"}), 400
        insert_count_month(year, month, hour, car, motorbike)

        # logging.info("Chèn vào bảng tính theo tháng thành công")
        return jsonify({"message": "Dữ liệu đã được chèn thành công!"}), 200
    except Exception as e:
        # logging.error("Lỗi xảy ra trong ứng dụng")
        return jsonify({"error": str(e)}), 500

@app.route('/api/insert_collision_clustering', methods=['POST'])
# Chèn dữ liệu vào bảng phân cụm tốc độ
def api_post_insert_collision_clustering():
    try:
        data = request.get_json()
        year = data.get('year')
        month = data.get('month')
        day = data.get('day')
        hour = data.get('hour')
        cluster_id = data.get('cluster_id')
        car_speed = data.get('car_speed')
        motorbike_speed = data.get('motorbike_speed')
        if not all([year, month, day, car_speed, motorbike_speed]):
            # logging.error("Lỗi xảy ra trong ứng dụng")
            return jsonify({"error": "Thiếu dữ liệu đầu vào"}), 400
        insert_collision_clustering(year, month, day, hour, cluster_id, car_speed, motorbike_speed)
        # logging.info("Chèn vào bảng phân cụmg thành công")
        return jsonify({"message": "Dữ liệu đã được chèn thành công!"}), 200
    except Exception as e:
        # logging.error("Lỗi xảy ra trong ứng dụng")
        return jsonify({"error": str(e)}), 500
@app.route('/api/insert_rate_left_right', methods=['POST'])
# Chèn dữ liệu và gọi hàm insert_rate_left_right
def insert_rate():
    try:
        data = request.get_json()
        required_fields = ['year', 'month', 'day', 'hour', 'car_left_ratio', 'car_right_ratio',
                           'motorbike_left_ratio', 'motorbike_right_ratio', 'car_stand_ratio', 'motorbike_stand_ratio']
        
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        insert_rate_left_right(
            data['year'], data['month'], data['day'], data['hour'],
            data['car_left_ratio'], data['car_right_ratio'],
            data['motorbike_left_ratio'], data['motorbike_right_ratio'],
            data['car_stand_ratio'], data['motorbike_stand_ratio']
        )
        # logging.info("Chèn vào bảng rate thành công")
        return jsonify({"message": "Data inserted successfully!"}), 200

    except Exception as e:
        # logging.error("Lỗi xảy ra trong ứng dụng")
        return jsonify({"error": str(e)}), 500
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 