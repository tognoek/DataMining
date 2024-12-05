FROM python
COPY . ./api
RUN pip install flask flask-cors pymongo python-dotenv pydantic
WORKDIR ./api
EXPOSE 7000
CMD ["python", "main.py"]
