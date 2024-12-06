import cv2
from ultralytics import YOLO
import math
import numpy as np
import os
from skimage.metrics import structural_similarity as ssim
import yt_dlp

class Kernel:
    def __init__(self, name_model="yolov8n.pt", threshold=0.8, min_dis = 10):
        self.model = YOLO(name_model)
        self.threshold = threshold
        self.min_dis = min_dis
        self.ydl_opts = {'format': 'best'}
        self.target = [2, 3]
        self.frames = []
        self.images = []
        self.images_verify = []
        self.dis_car = 0
        self.dis_motorbike = 0
        self.rate_car = [0, 0, 0]
        self.rate_motorbike = [0, 0, 0]
        self.min_dis = 40
        # cut -> solve => result
        # filter -> active => result

    def cut(self, url):
        cap = cv2.VideoCapture(url)
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        self.frames, self.images, self.images_verify = [], [], []
        while True:
            ret, frame = cap.read()
            if not ret: break
            if int(cap.get(cv2.CAP_PROP_POS_FRAMES)) % fps == 0:
                results = self.model(frame, conf=0.5, verbose=False)
                self.frames.append(frame)
                for result in results[0].boxes:
                    cls_id = int(result.cls)
                    if cls_id in self.target:
                        x1, y1, x2, y2 = map(int, result.xyxy[0])
                        image = frame[y1:y2, x1:x2]
                        if not any(self.find(image, verify["image"], 0.6) for verify in self.images):
                            self.images.append({"id": cls_id, "x1": x1, "x2": x2, "y1": y1, "y2": y2, "image": image})
    
    def filter(self, url, rate = 1):
        cap = cv2.VideoCapture(url)
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        self.images = []
        while True:
            ret, frame = cap.read()
            if not ret: break
            if int(cap.get(cv2.CAP_PROP_POS_FRAMES)) % (fps * rate) == 0:
                results = self.model(frame, conf=0.5, verbose=False)
                for result in results[0].boxes:
                    cls_id = int(result.cls)
                    if cls_id in self.target:
                        x1, y1, x2, y2 = map(int, result.xyxy[0])
                        image = frame[y1:y2, x1:x2]
                        is_compre = False
                        for image_verify in self.images:
                            if self.compare_images(image, image_verify["image"], 0.3):
                                is_compre = True
                                image_verify["x2"] = x1
                                image_verify["y2"] = y1
                                image_verify["fps"] += 1
                                break
                        if is_compre == False:
                            self.images.append({"id": cls_id, "x1": x1, "x2": None, "y1": y1, "y2": None, "image": image, "fps": 0})
        
    def saves(self, folder_path):
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        count = 0  
        for image in self.images:
            file_path = os.path.join(folder_path, f'image_{count}.jpg') 
            cv2.imwrite(file_path, image["image"])  
            count += 1  
        
    def active(self, show = False):
        self.dis_car, self.dis_motorbike = 0, 0
        self.frame_car, self.frame_motorbike = 0, 0
        self.rate_car, self.rate_motorbike = [0, 0, 0], [0, 0, 0]
        for data in self.images:
            x1, y1 = data["x1"], data["y1"]
            x2, y2 = data["x2"], data["y2"]
            if x1 is not None and x2 is not None and y1 is not None and y2 is not None: 
                distance = self.calculate_distance_2d(x1, y1, x2, y2)
                if data["id"] == 2:
                    if show:
                        print(f"Xe o to, toc do: {distance["value"]}, huong {distance["vec"]}")
                    if distance["value"] < self.min_dis:
                        self.rate_car[2] += 1
                    else:
                        self.frame_car += data["fps"]
                        self.dis_car += distance["value"]
                        self.rate_car[distance["vec"]] += 1
                else:
                    if show:
                        print(f"Xe may, toc do: {distance["value"]}, huong {distance["vec"]}")
                    if distance["value"] < self.min_dis:
                        self.rate_motorbike[2] += 1
                    else:
                        self.frame_motorbike += data["fps"]
                        self.dis_motorbike += distance["value"]
                        self.rate_motorbike[distance["vec"]] += 1
        return self.dis_car, self.dis_motorbike, self.rate_car, self.rate_motorbike, self.frame_car, self.frame_motorbike

    def solve(self):
        self.dis_car, self.dis_motorbike = 0, 0
        self.frame_car, self.famre_motorbike = 0, 0
        self.rate_car, self.rate_motorbike = [0, 0, 0], [0, 0, 0]
        print(len(self.images))
        for data in self.images:
            image = data["image"]
            if any(self.find(image, verify, 0.7) for verify in self.images_verify): continue
            self.images_verify.append(image)
            for frame in self.frames:
                result = self.find(frame, image)
                if result:
                    x1, y1 = data["x1"], data["y1"]
                    x2, y2 = result["x1"], result["y1"]
                    distance = self.calculate_distance_2d(x1, y1, x2, y2)
                    if data["id"] == 2:
                        self.dis_car += distance["value"]
                        self.rate_car[distance["vec"]] += 1
                    else:
                        self.dis_motorbike += distance["value"]
                        self.rate_motorbike[distance["vec"]] += 1
        return self.dis_car, self.dis_motorbike, self.rate_car, self.rate_motorbike

    def find(self, large_image, small_image, threshold=None):
        if large_image.shape[0] < small_image.shape[0] or large_image.shape[1] < small_image.shape[1]:
            return None
        result = cv2.matchTemplate(large_image, small_image, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)
        if max_val >= (self.threshold if threshold is None else threshold):
            top_left = max_loc
            bottom_right = (top_left[0] + small_image.shape[1], top_left[1] + small_image.shape[0])
            return {"x1": top_left[0], "x2": bottom_right[0], "y1": top_left[1], "y2": bottom_right[1], "rate": max_val}
        return None

    def calculate_distance_2d(self, x1, y1, x2, y2):
        return {"value": math.sqrt((x2 - x1)**2 + (y2 - y1)**2), "vec": 0 if x2 > x1 else 1}

    def compare_images_resize(slef, img1, img2):
        img2_resized = cv2.resize(img2, (img1.shape[1], img1.shape[0]))
        mse = np.sum((img1 - img2_resized) ** 2) / float(img1.size)
        img1_gray = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
        img2_gray = cv2.cvtColor(img2_resized, cv2.COLOR_BGR2GRAY)
        ssim_value, _ = ssim(img1_gray, img2_gray, full=True)
        return mse, ssim_value
    
    def resize_images_to_fixed_size(self, large_image, small_image):
        h_large, w_large = large_image.shape[:2]
        h_small, w_small = small_image.shape[:2]
        target_size = (min(w_large, w_small), min(h_large, h_small))
        large_image_resized = cv2.resize(large_image, target_size)
        small_image_resized = cv2.resize(small_image, target_size)
        return large_image_resized, small_image_resized

    def compare_images(self, large_image, small_image, threshold = None):
        large_image_resized, small_image_resized = self.resize_images_to_fixed_size(large_image, small_image)
        result = cv2.matchTemplate(large_image_resized, small_image_resized, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        threshold = threshold if threshold != None else self.threshold
        # print(f'Max value: {max_val}')  
        if max_val >= threshold:
            return True
        else:
            return False
        
    def getUrlFromYoutube(self, url):
        with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False)
            video_url = info_dict['url']
        return video_url
    
    def youtube(self, url, date, hour, minute, size = 60, rate = 1):
        cap = cv2.VideoCapture(self.getUrlFromYoutube(url))
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        self.images = []
        data = []
        print("=====BEGIN=====")
        print(f"Url: {url}")
        while True:
            ret, frame = cap.read()
            if not ret: break
            if int(cap.get(cv2.CAP_PROP_POS_FRAMES)) % (fps * rate) == 0:
                results = self.model(frame, conf=0.5, verbose=False)
                for result in results[0].boxes:
                    cls_id = int(result.cls)
                    if cls_id in self.target:
                        x1, y1, x2, y2 = map(int, result.xyxy[0])
                        image = frame[y1:y2, x1:x2]
                        is_compre = False
                        for image_verify in self.images:
                            if self.compare_images(image, image_verify["image"], 0.3):
                                is_compre = True
                                image_verify["x2"] = x1
                                image_verify["y2"] = y1
                                image_verify["fps"] += 1
                                break
                        if is_compre == False:
                            self.images.append({"id": cls_id, "x1": x1, "x2": None, "y1": y1, "y2": None, "image": image, "fps": 0})
            if int(cap.get(cv2.CAP_PROP_POS_FRAMES)) % (fps * size) == 0:
                # print(f"Time: {count_time}, Value: {self.active()}")
                data.append(self.create(date, hour, minute))
                self.images = []
                minute += 1
                if minute > 59:
                    minute = 0
                    hour += 1
                        
        return data
    def url(self, url, date, hour, minute, size = 60, rate = 1):
        cap = cv2.VideoCapture(url)
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        self.images = []
        data = []
        print("=====BEGIN=====")
        print(f"Url: {url}")
        while True:
            ret, frame = cap.read()
            if not ret: break
            if int(cap.get(cv2.CAP_PROP_POS_FRAMES)) % (fps * rate) == 0:
                results = self.model(frame, conf=0.5, verbose=False)
                for result in results[0].boxes:
                    cls_id = int(result.cls)
                    if cls_id in self.target:
                        x1, y1, x2, y2 = map(int, result.xyxy[0])
                        image = frame[y1:y2, x1:x2]
                        is_compre = False
                        for image_verify in self.images:
                            if self.compare_images(image, image_verify["image"], 0.3):
                                is_compre = True
                                image_verify["x2"] = x1
                                image_verify["y2"] = y1
                                image_verify["fps"] += 1
                                break
                        if is_compre == False:
                            self.images.append({"id": cls_id, "x1": x1, "x2": None, "y1": y1, "y2": None, "image": image, "fps": 0})
            if int(cap.get(cv2.CAP_PROP_POS_FRAMES)) % (fps * size) == 0:
                # print(f"Time: {count_time}, Value: {self.active()}")
                data.append(self.create(date, hour, minute))
                self.images = []
                minute += 1
                if minute > 59:
                    minute = 0
                    hour += 1
                        
        return data
    
    def video(self, cap, date, hour, minute, size = 60, rate = 1):
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        self.images = []
        data = []
        while True:
            ret, frame = cap.read()
            if not ret: break
            if int(cap.get(cv2.CAP_PROP_POS_FRAMES)) % (fps * rate) == 0:
                results = self.model(frame, conf=0.5, verbose=False)
                for result in results[0].boxes:
                    cls_id = int(result.cls)
                    if cls_id in self.target:
                        x1, y1, x2, y2 = map(int, result.xyxy[0])
                        image = frame[y1:y2, x1:x2]
                        is_compre = False
                        for image_verify in self.images:
                            if self.compare_images(image, image_verify["image"], 0.3):
                                is_compre = True
                                image_verify["x2"] = x1
                                image_verify["y2"] = y1
                                image_verify["fps"] += 1
                                break
                        if is_compre == False:
                            self.images.append({"id": cls_id, "x1": x1, "x2": None, "y1": y1, "y2": None, "image": image, "fps": 0})
            if int(cap.get(cv2.CAP_PROP_POS_FRAMES)) % (fps * size) == 0:
                # print(f"Time: {count_time}, Value: {self.active()}")
                data.append(self.create(date, hour, minute))
                self.images = []
                minute += 1
                if minute > 59:
                    minute = 0
                    hour += 1
                        
        return data
    def create(self, date, hour, minute, show = False):
        if show:
            print(f"Date: {date} -- Time: {hour}h:{minute}m")
        dis_car, dis_motorbike, rate_car, rate_motorbike, frame_car, frame_motorbike = self.active()
        data = {
            "date": date,
            "time": f"{hour}:{minute}",
            "dis_car": dis_car,
            "dis_motorbike": dis_motorbike,
            "car_left": rate_car[0],
            "car_right": rate_car[1],
            "car_stand": rate_car[2],
            "motorbike_left": rate_motorbike[0],
            "motorbike_right": rate_motorbike[1],
            "motorbike_stand": rate_motorbike[2],
            "frame_car": frame_car,
            "frame_motorbike" : frame_motorbike
        }
        return data