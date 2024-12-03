from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime
import os

load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL")
MONGODB_NAME = os.getenv("MONGODB_NAME")
MONGODB_NGUYENHUE = os.getenv("MONGODB_NGUYENHUE")
print(MONGODB_URL)

client = MongoClient(MONGODB_URL)  
db = client[MONGODB_NAME] 
collection_nguyenhue = db[MONGODB_NGUYENHUE]

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

def execution_query(query):
    return collection_nguyenhue.find(query)

def insert():
    data_dict = {
        "date": "2022/01/01",
        "time": "0:26",
        "car_left": 1,
        "car_right": 3,
        "car_stand": 5,
        "car_speed": 70,
        "motorbike_left": 9,
        "motorbike_right": 1,
        "motorbike_stand": 2,
        "motorbike_speed": 51,
        "temper": 15,
        "rain": 0
    }
    
    # collection_nguyenhue.insert_one(data_dict)
    print("Dữ liệu đã được chèn vào MongoDB.")
query = create_query_month_nguyenhue(2022, 3)
data = execution_query(query)
if collection_nguyenhue.count_documents(query) == 0:
    print("Không có dữ liệu cho tháng này.")
    insert()
else:
    print(f"Len: {collection_nguyenhue.count_documents(query)}")
    for d in data:
        print(d)
