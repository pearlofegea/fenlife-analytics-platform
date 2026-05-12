"""Student veri erişim katmanı + fuzzy identity resolution."""
from __future__ import annotations

import uuid

from rapidfuzz import fuzz
from sqlalchemy.orm import Session

from app.db.models import Student

# ─── Fuzzy matching sabitleri ─────────────────────────────────────────────────

# token_sort_ratio eşiği: kelime sırasından bağımsız benzerlik.
# 92 seçildi: "YAVUZ POYRAZ KEREM" ↔ "YAVUZ POYRAZ KAREM" = ~94 (eşleşir),
#             "AHMET YILMAZ" ↔ "MEHMET YILMAZ" = ~88 (eşleşmez).
_MATCH_THRESHOLD = 92

_TR_MAP = str.maketrans(
    "ığüşöçİĞÜŞÖÇ",
    "igusocIGUSOC",
)


def _normalize(name: str) -> str:
    """Türkçe karakterleri ASCII'ye çevirir, trim + uppercase + tekli boşluk."""
    return " ".join(name.translate(_TR_MAP).upper().split())


# ─── Temel CRUD ───────────────────────────────────────────────────────────────

def get_by_id(db: Session, student_id: str) -> Student | None:
    try:
        uid = uuid.UUID(student_id)
    except ValueError:
        return None
    return db.get(Student, uid)


def get_or_create(
    db: Session,
    name: str,
    grade: str,
    institution: str = "FENlife Maltepe",
    tc_no: str | None = None,
) -> tuple[Student, bool]:
    """Tam isim + sınıf eşleşmesiyle öğrenci bul; yoksa oluştur."""
    query = db.query(Student).filter(Student.name == name, Student.grade == grade)
    if tc_no:
        query = query.filter(Student.tc_no == tc_no)

    student = query.first()
    if student:
        return student, False

    student = Student(
        id=uuid.uuid4(),
        name=name,
        grade=grade,
        institution=institution,
        tc_no=tc_no,
    )
    db.add(student)
    db.commit()
    db.refresh(student)
    return student, True


# ─── Fuzzy identity resolution ────────────────────────────────────────────────

def find_matching_student(
    db: Session,
    name: str,
    grade: str,
) -> Student | None:
    """
    Fuzzy isim + tam sınıf eşleşmesiyle öğrenci ara.

    Eşleme mantığı:
    - Sınıf tam eşleşmeli (farklı sınıf = kesinlikle farklı öğrenci).
    - İsim için token_sort_ratio kullanılır (kelime sırası farkını tolere eder,
      Türkçe karakterler normalize edilir).
    - Eşik: 92 — agresif yanlış birleştirmeyi önler; küçük yazım hatalarını tolere eder.

    Returns:
        Eşleşen Student veya None (eşik altındaysa → yeni kayıt daha güvenli).
    """
    candidates = db.query(Student).filter(Student.grade == grade).all()
    if not candidates:
        return None

    norm_query = _normalize(name)
    best_student: Student | None = None
    best_score = 0

    for s in candidates:
        score = fuzz.token_sort_ratio(norm_query, _normalize(s.name))
        if score > best_score:
            best_score = score
            best_student = s

    if best_score >= _MATCH_THRESHOLD:
        return best_student
    return None


def get_or_create_with_matching(
    db: Session,
    name: str,
    grade: str,
    institution: str = "FENlife Maltepe",
) -> tuple[Student, bool]:
    """
    Fuzzy matching ile öğrenci bul; bulunamazsa yeni kayıt oluştur.

    Returns:
        (student, created) — created=True ise yeni kayıt oluşturuldu.
    """
    existing = find_matching_student(db, name, grade)
    if existing:
        return existing, False

    student = Student(
        id=uuid.uuid4(),
        name=name,
        grade=grade,
        institution=institution,
    )
    db.add(student)
    db.commit()
    db.refresh(student)
    return student, True
