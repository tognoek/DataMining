FROM python:3.9-slim
COPY . ./data
RUN pip install --default-timeout=100 --no-cache-dir python-dotenv opencv-python yt-dlp ultralytics scikit-image numpy
WORKDIR ./data
CMD ["python", "main.py"]
