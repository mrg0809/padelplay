from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Union, Optional
from app.db.connection import supabase
from app.core.security import get_current_user
from app.utils.supabase_utils import handle_supabase_response
from datetime import date, time, datetime

router = APIRouter()

class Match(BaseModel):
    id: str
    match_date: date
    match_time: time
    clubs: Optional[dict] = None
    tournament_id: Optional[str]
    type: str = "match"

class Lesson(BaseModel):
    id: str
    lesson_date: date
    lesson_time: time
    clubs: Optional[dict] = None
    lesson_type: str
    type: str = "lesson"

UpcomingEvent = Union[Match, Lesson]

@router.get("/player/upcoming_events/", response_model=List[UpcomingEvent])
async def get_upcoming_player_events(current_user: dict = Depends(get_current_user)):
    player_id = current_user["id"]
    today = date.today()
    now = datetime.now().strftime("%H:%M:%S")

    # Consultar partidos
    matches_response = (
    supabase
    .from_("matches")
    .select("id, match_date, match_time, clubs (name), tournament_id")
    .filter("match_date", "gte", str(today))
    .or_(f"team1_players.cs.{{{player_id}}},team2_players.cs.{{{player_id}}}")
    .order("match_date")
    .order("match_time")
    .execute()
    )
    if not matches_response.data:
        matches_data = []
    matches_data = [Match(**match) for match in matches_response.data]

    # Consultar clases
    lessons_response = (
    supabase
    .from_("lessons")
    .select("id, lesson_date, lesson_time, clubs (name), lesson_type")
    .filter("lesson_date", "gte", str(today))
    .filter("players", "cs", f"{{{player_id}}}")
    .order("lesson_date")
    .order("lesson_time")
    .execute()
    )
    if not lessons_response.data:
        lessons_data = []
    lessons_data = [Lesson(**lesson) for lesson in lessons_response.data]

    # Filtrar por hora para los eventos de hoy
    upcoming_matches = [match for match in matches_data if match.match_date > today or (match.match_date == today and match.match_time.strftime("%H:%M:%S") >= now)]
    upcoming_lessons = [lesson for lesson in lessons_data if lesson.lesson_date > today or (lesson.lesson_date == today and lesson.lesson_time.strftime("%H:%M:%S") >= now)]

    all_events = sorted(upcoming_matches + upcoming_lessons, key=lambda x: (x.match_date if isinstance(x, Match) else x.lesson_date, x.match_time if isinstance(x, Match) else x.lesson_time, x.tournament_id if isinstance(x, Match) else x.lesson_type))
    return all_events