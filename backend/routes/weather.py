from fastapi import APIRouter, Query
from backend.weather_service import fetch_weather

router = APIRouter(prefix="/api/weather", tags=["Weather"])

@router.get("")
@router.get("/")
def get_weather_data(location: str = Query("Pollachi")):
    return fetch_weather(location_name=location)
