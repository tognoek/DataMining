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

output_dir = os.getenv("OUT")

URL_STREAM  = os.getenv("URL_STREAM")
os.makedirs(output_dir, exist_ok=True)
ydl_opts = {
    'format': 'best',
}
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
        print(data)
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