"""Sınav Pydantic modeli."""
from datetime import date
from pydantic import BaseModel


class Exam(BaseModel):
    student_id: str
    date: date
    name: str
    publisher: str
    turkce: float
    matematik: float
    fen: float
    sosyal: float
    din: float
    ydil: float
    puan: float
