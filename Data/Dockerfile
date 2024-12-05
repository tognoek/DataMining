FROM python
COPY . ./data
RUN pip install python-dotenv opencv-python yt-dlp ultralytics scikit-image numpy
WORKDIR ./data
CMD ["python", "main.py"]
