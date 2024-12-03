from pydantic import BaseModel

class Data(BaseModel):
    date: str
    time: str
    car_left: int
    car_right: int
    car_stand: int
    car_speed: int
    motorbike_left: int
    motorbike_right: int
    motorbike_stand: int
    motorbike_speed: int
    temper: int
    rain: int