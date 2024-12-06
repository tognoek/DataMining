import os
from dotenv import load_dotenv
from Core.kernel import Kernel
load_dotenv()
from dotenv import load_dotenv
import cv2
import yt_dlp
import threading
import queue
from datetime import datetime
import requests
import json

output_dir = os.getenv("OUT")

URL_STREAM  = os.getenv("URL_STREAM")
os.makedirs(output_dir, exist_ok=True)
ydl_opts = {
    'format': 'best',
}

def get_weather():
    api_key = "e2672e1f1879800514ec12404c0e22be"  
    lat = "16.0682"  
    lon = "108.2156"
    url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&units=metric&appid={api_key}"
    try:
        response = requests.get(url)
        response.raise_for_status() 
        weather_data = response.json()
        weather = weather_data['weather'][0]['description']
        temperature = weather_data['main']['temp']
        rain = weather_data.get('rain', {}).get('1h', 0) 
        is_rain = 1 if rain > 0 else 0  
        
        return temperature, is_rain
    
    except requests.exceptions.HTTPError as http_err:
        print(f"Lỗi HTTP: {http_err}")
    except Exception as err:
        print(f"Lỗi khác: {err}")
    
    return None, 0  


def post_data_to_api():
    url = "http://localhost:5000/api/insert"
    values = list(data[0].values())
    temperature, is_rain = get_weather()
    rate_car = (values[4] + values[5]) * values[10]
    rate_moto = (values[7] + values[8]) * values[11]
    if rate_car == 0:
        speed_car = 0
    else:
        speed_car = values[2] / rate_car
    speed_car = speed_car if speed_car < 55 else 56
    if rate_car == 0:
        speed_moto = 0
    else:
        speed_moto = values[3] / rate_moto
    speed_moto = speed_moto if speed_moto < 55 else 50
    data = {
        "date": values[0],
        "time": values[1],
        "car_left": values[4],
        "car_right": values[5],
        "car_stand": values[6],
        "car_speed": speed_car,
        "motorbike_left": values[7],
        "motorbike_right": values[8],
        "motorbike_stand": values[9],
        "motorbike_speed": speed_moto,
        "temper": temperature,
        "rain": is_rain
    }
    try:
        response = requests.post(url, json=data)
        if response.status_code == 200:
            print("Dữ liệu đã được gửi thành công!")
            print("Phản hồi từ server:", response.json())
        else:
            print(f"Lỗi! Mã trạng thái: {response.status_code}")
            print("Thông tin lỗi:", response.text)
    except requests.exceptions.RequestException as e:
        print("Lỗi trong quá trình gửi yêu cầu:", str(e))

def save_video_segment(cap, video_index, fps, frame_width, frame_height, video_queue):
    video_path = os.path.join(output_dir, f"video_{video_index:03d}.mp4")
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(video_path, fourcc, fps, (frame_width, frame_height))
    frame_count = 0
    max_frame_count = fps * 60  
    while frame_count < max_frame_count:
        ret, frame = cap.read()
        if not ret:
            print("Không thể nhận video stream!")
            break

        out.write(frame)
        frame_count += 1

    out.release()
    print(f"Đã lưu video: {video_path}")
    video_queue.put(video_path)
def handle_video(video_queue):
    while True:
        video_path = video_queue.get() 
        if video_path is None: 
            break
        
        # print(f"Đang xử lý video: {video_path}")
        kernel = Kernel()
        today = datetime.today()
        formatted_today = today.strftime("%Y/%m/%d") 
        now = datetime.now()
        hour = now.hour  # Giờ (0-23)
        minute = now.minute
        data = kernel.url(f"{video_path}", formatted_today, hour, minute)
        post_data_to_api(data)
        if os.path.exists(video_path):
            os.remove(video_path)
            print(f"Đã xóa video: {video_path}")
def stream_youtube(video_url):
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info_dict = ydl.extract_info(video_url, download=False)
            stream_url = info_dict['url']
            cap = cv2.VideoCapture(stream_url)
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 360) 
            fps = int(cap.get(cv2.CAP_PROP_FPS)) 
            frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

            video_index = 0
            video_queue = queue.Queue() 
            handler_thread = threading.Thread(target=handle_video, args=(video_queue,))
            handler_thread.start()

            while True:
                save_video_segment(cap, video_index, fps, frame_width, frame_height, video_queue)
                video_index += 1
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

            cap.release()
            cv2.destroyAllWindows()
            video_queue.put(None)
            handler_thread.join() 

        except Exception as e:
            print(f"Đã xảy ra lỗi: {e}")

stream_youtube(URL_STREAM)