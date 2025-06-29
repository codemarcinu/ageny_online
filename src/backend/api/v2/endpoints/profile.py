from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import json
import os

router = APIRouter()

PROFILE_FILE = "data/user_profile.json"

class Profile(BaseModel):
    nickname: Optional[str] = None
    avatar: Optional[str] = None  # Could be a URL or emoji


def load_profile() -> Profile:
    if os.path.exists(PROFILE_FILE):
        with open(PROFILE_FILE, "r") as f:
            data = json.load(f)
            return Profile(**data)
    return Profile()


def save_profile(profile: Profile):
    os.makedirs(os.path.dirname(PROFILE_FILE), exist_ok=True)
    with open(PROFILE_FILE, "w") as f:
        json.dump(profile.dict(), f)


@router.get("/profile", response_model=Profile)
def get_profile():
    """
    Get the current user profile (nickname and avatar).
    """
    return load_profile()


@router.post("/profile", response_model=Profile)
def update_profile(profile: Profile):
    """
    Update the user profile (nickname and avatar).
    """
    save_profile(profile)
    return profile 