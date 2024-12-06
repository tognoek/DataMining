FROM python
COPY . ./service
RUN pip install --no-cache-dir flask flask-cors requests pandas scikit-learn
WORKDIR ./service
EXPOSE 7070
CMD ["python", "main.py"]
