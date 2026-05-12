"""Öğrenci Pydantic modeli."""
from pydantic import BaseModel


class Student(BaseModel):
    id: str
    name: str
    tc_no: str | None = None
    grade: str  # "8-01" etc
    institution: str = "FENlife Maltepe"
