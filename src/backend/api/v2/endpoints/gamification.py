from fastapi import APIRouter
from typing import List, Dict

router = APIRouter()

@router.get("/challenges/daily", response_model=List[Dict])
def get_daily_challenges():
    """
    Get a list of daily challenges for gamification.
    Returns a static list of challenges (can be extended to use a database or file).
    """
    return [
        {"id": 1, "task": "Zadaj chatbotowi 3 pytania 🗨️"},
        {"id": 2, "task": "Przeskanuj dokument OCR 📄"},
        {"id": 3, "task": "Odpowiedz na quiz dnia 🎯"}
    ] 