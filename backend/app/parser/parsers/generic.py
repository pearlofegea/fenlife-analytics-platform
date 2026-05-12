"""
Generic PDF adapter — format-agnostic LGS sınav sonucu çıkarıcı.

Yaklaşım:
  1. pymupdf ile tüm sayfaların metnini çıkar.
  2. Regex ile öğrenci adı, sınıf, tarih, sınav adı, ders netlerini yakala.
  3. Her alan için birden fazla pattern dene; hiçbiri eşleşmezse açık default kullan.

Desteklenen formatlar (gözlemsel, gerçek PDF ile test edilmemiş):
  - Satır tabanlı: "TÜRKÇE  15  4  1  13.67"
  - D/Y/B tabanlı: "D:15 Y:4 B:1 Net:13.67"
  - Karma metinsel: "Türkçe: 13,67 net"

Sınırlamalar:
  - Gerçek LGS PDF'leri görülmeden yazıldı — her yeni format için pattern genişletilmeli.
  - Kazanım kırılımı (KazanimBreakdown) bu adaptörden çıkarılmıyor.
  - Zorluk profili bu adaptörden çıkarılmıyor.
"""
import logging
import re
from datetime import date, datetime
from pathlib import Path

import pymupdf

from app.parser.parsers.base import BaseAdapter
from app.parser.schemas import NormalizedExamResult, SubjectResult

logger = logging.getLogger(__name__)


class ParseError(Exception):
    """PDF'den anlamlı veri çıkarılamadı."""


# ── Ders anahtar kelimeleri ────────────────────────────────────────────────────
# Her entry: (internal_key, regex_pattern_for_subject_name)
# Pattern'lar hem Türkçe Unicode (gerçek PDF) hem ASCII fallback (bozuk font) kapsar.
SUBJECT_RE: list[tuple[str, str]] = [
    ("turkce",    r"T[ÜU]RK[CÇ]E|TURKCE"),
    ("matematik", r"MATEMAT[İI]K|MATEMATIK"),
    ("fen",       r"FEN(?:\s+(?:VE\s+TEKN\.?|B[İI]L[İI]MLERI|B[İI]LG[İI]S[İI]|BILIMLERI|BILGISI))?"),
    ("sosyal",    r"(?:T\.C\.\s*)?[İI]NK[İI]LAP|INKILAP|SOSYAL(?:\s+B[İI]LG\.?)?|TAR[İI]H(?:\s+VE\s+VATANDA)?"),
    ("din",       r"D[İI]N(?:\s*K[ÜU]LT[ÜU]R[ÜU]|\s*KUL\.?|\s*K\.\s*VE|\s*K\.VE|\s*K\b)|DIN\s*KULTURU"),
    ("ydil",      r"[İI]NG[İI]L[İI]ZCE|INGILIZCE|YABANCI\s*D[İI]L|Y\.?\s*D[İI]L"),
]

# Soru sayısı limitleri — net aralık doğrulaması için
SUBJECT_MAX_Q = {
    "turkce": 20, "matematik": 20, "fen": 20,
    "sosyal": 10, "din": 10, "ydil": 10,
}


def _clean(text: str) -> str:
    """Çoklu boşlukları tek boşluğa indir, strip yap."""
    return re.sub(r"\s+", " ", text).strip()


def _parse_float(s: str) -> float:
    """'12,50' veya '12.50' → 12.5"""
    return float(s.replace(",", "."))


# ── Alan çıkarım fonksiyonları ─────────────────────────────────────────────────

def _extract_student_name(text: str) -> str | None:
    patterns = [
        # SBS Karne (Mozaik / Final / TÖDER): "SOYADI - ADI\nSINAV ADI\n<grubu>\n<no>\nNAME"
        # grubu ve öğrenci-no (iki sayı) araya giriyor — \d+\s+\d+\s+ ile atlanıyor
        r"SOYADI\s*[-–]\s*ADI\s+SINAV\s+ADI\s+\d+\s+\d+\s+([A-ZÇĞİÖŞÜ][A-ZÇĞİÖŞÜa-zçğışöüşü ]{2,50})",
        # Format 2 (AKBİM TG): "SOYADI - ADI\nSINAV ADI\nNAME" (sayı yok)
        r"SOYADI\s*[-–]\s*ADI\s+SINAV\s+ADI\s+([A-ZÇĞİÖŞÜ][A-ZÇĞİÖŞÜa-zçğışöüşü ]{2,50})",
        # Format 1 (SONUÇ BELGESİ): "Öğrenci\nNumara\nSınıf\nNAME\n0\n"
        r"(?:Öğrenci|OGRENCI)\s+(?:Numara|No\.?)\s+(?:Sınıf|SINIF)\s+([A-ZÇĞİÖŞÜ][A-ZÇĞİÖŞÜa-zçğışöüşü ]{2,50})\s+\d",
        # Kolon ayraçlı formatlar (ÖĞRENCİ:, ADI SOYADI:, ADI - SOYADI:)
        r"(?:ÖĞRENCİ(?:NİN ADI)?|ADI\s*SOYADI|ÖĞRENCİ ADI SOYADI)\s*[:\-]\s*([A-ZÇĞİÖŞÜ][A-ZÇĞİÖŞÜa-zçğışöüşü ]{2,50})",
        r"(?:ADI\s*[-–:]\s*SOYADI|AD\s*[-–:]\s*SOYAD)\s*[:\-]?\s*([A-ZÇĞİÖŞÜ][A-ZÇĞİÖŞÜa-zçğışöüşü ]{2,50})",
        r"(?:OGRENCI|ADI SOYADI|OGRENCININ ADI)\s*[:\-]\s*([A-Z][A-Z ]{2,50})",
        r"(?:OGRENCI|ÖĞRENCİ)\s*[:\-]\s*([A-ZÇĞİÖŞÜa-zçğışöüşü ]{3,60})",
        # MOZAİK / genel: satır başı "Öğrenci Adı Soyadı :" veya "Ad Soyad :"
        r"(?:Öğrenci\s*Adı\s*Soyadı|Öğrenci\s*Adı|Ad\s*Soyad)\s*[:\-]\s*([A-ZÇĞİÖŞÜ][A-ZÇĞİÖŞÜa-zçğışöüşü ]{2,50})",
        # TÖDER / genel: "AD SOYAD\n<NAME>" yapısı
        r"AD\s+SOYAD\s*\n\s*([A-ZÇĞİÖŞÜ][A-ZÇĞİÖŞÜa-zçğışöüşü ]{2,50})",
    ]
    for pat in patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            name = _clean(m.group(1))
            if 3 <= len(name) <= 60 and not re.search(r'\d', name):
                return name

    # Format 3 (Final/TÖDER): satır 1 = 5-6 haneli MEB kodu, satır 2 = ad
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    if lines and re.match(r'^\d{5,6}$', lines[0]):
        candidate = _clean(lines[1]) if len(lines) > 1 else ""
        if 3 <= len(candidate) <= 60 and not re.search(r'\d', candidate):
            return candidate

    return None


def _extract_grade(text: str) -> str | None:
    patterns = [
        r"(?:SINIF|Sınıf)\s*[:\-]\s*([0-9][A-Za-z0-9\-/]{1,6})",
        r"\b(8\s*/\s*[A-Z0-9]{1,4})\b",   # "8 / A" (AKBİM TG format)
        r"\b(8[-/][A-Z0-9]{1,4})\b",
        r"\b(8\s*[A-D])\b",
    ]
    for pat in patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            grade = _clean(m.group(1))
            # "8 / A" → "8-A" normalize et
            grade = re.sub(r'\s*/\s*', '-', grade)
            return grade
    return None


def _extract_date(text: str) -> date:
    """İlk geçerli DD.MM.YYYY veya DD/MM/YYYY tarihini döndür; bulunamazsa bugün."""
    patterns = [
        r"(?:TARİH|Tarih)\s*[:\-]\s*(\d{1,2}[./]\d{1,2}[./]\d{2,4})",
        r"\b(\d{1,2}[./]\d{1,2}[./]\d{4})\b",
    ]
    for pat in patterns:
        for m in re.finditer(pat, text, re.IGNORECASE):
            raw = m.group(1)
            for fmt in ("%d.%m.%Y", "%d/%m/%Y", "%d.%m.%y", "%d/%m/%y"):
                try:
                    return datetime.strptime(raw, fmt).date()
                except ValueError:
                    continue
    return date.today()


def _extract_exam_name(text: str, filename: str) -> str:
    """Sınav adını çıkar; bulunamazsa dosya adından türet."""
    patterns = [
        r"(LGS\s+DENEME\s+SINAVI[^\n]{0,30})",
        r"(DENEME\s+(?:SINAVI\s+)?(?:NO\s*[:.]?\s*)?\d+)",
        r"((?:TÜRKİYE\s+GENELİ|GENEL)\s+DENEME[^\n]{0,30})",
        r"([^\n]*(?:DENEME|SINAV)[^\n]{0,20}\d+)",
    ]
    for pat in patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            name = _clean(m.group(1))
            if 4 <= len(name) <= 80:
                return name
    # Dosya adından türet
    stem = Path(filename).stem.replace("_", " ").replace("-", " ")
    return stem if stem else "LGS Deneme"


def _extract_total_score(text: str, subjects: list[SubjectResult]) -> float:
    """Toplam LGS puanını çıkar; bulunamazsa net toplamından hesapla."""
    patterns = [
        r"LGS\s+PUAN[İI]\s*[:\-]?\s*([\d,\.]+)",
        r"TOPLAM\s+PUAN\s*[:\-]?\s*([\d,\.]+)",
        r"NET\s+PUAN\s*[:\-]?\s*([\d,\.]+)",
        r"PUAN\s*[:\-]\s*([\d,\.]+)",
        r"([3-5]\d{2}[,\.]\d{1,3})",   # 300-599 aralığındaki LGS puan benzeri sayı (3 ondalık)
    ]
    for pat in patterns:
        for m in re.finditer(pat, text, re.IGNORECASE):
            try:
                val = _parse_float(m.group(1))
                if 100.0 <= val <= 600.0:
                    return round(val, 2)
            except ValueError:
                continue

    # Fallback: net toplamından kaba puan tahmini (LGS ağırlık formülü yok)
    total_net = sum(s.net for s in subjects)
    return round(total_net * 5.0, 2) if total_net > 0 else 0.0


def _extract_subjects_akbim_tg(text: str) -> list[SubjectResult]:
    """
    Format 2: AKBİM TÜRKİYE GENELİ — sütun tabanlı yapı.

    Metin yapısı:
      TÜRKÇE\nMATEMATİK\nDİN KÜLTÜRÜ\nFEN BİLGİSİ\n
      [7 sayı: SORU] [7 sayı: DOĞRU] [7 sayı: YANLIŞ] [7 float: NET] ...
      SOSYAL\nBİLGİLER\nYABANCI DİL\nTOPLAM ...

    Konu sırası: turkce(0), matematik(1), din(2), fen(3), sosyal(4), ydil(5), toplam(6)
    """
    m = re.search(
        r"FEN\s+B[İI]LG[İI]S[İI]\s*([\d,\.\s]+?)SOSYAL",
        text, re.IGNORECASE | re.DOTALL,
    )
    if not m:
        return []

    raw = m.group(1)
    nums_raw = re.findall(r"\d+[,\.]?\d*", raw)
    try:
        nums = [_parse_float(n) for n in nums_raw]
    except ValueError:
        return []

    # 6 konu + toplam = 7 sütun; 3 satır (soru/doğru/yanlış) + NET satırı = 4×7=28 minimum
    if len(nums) < 28:
        return []

    # Satır indeksleri (her satır 7 değer)
    correct_row = nums[7:14]   # doğru
    wrong_row   = nums[14:21]  # yanlış
    net_row     = nums[21:28]  # net

    key_order = ["turkce", "matematik", "din", "fen", "sosyal", "ydil"]
    results: list[SubjectResult] = []
    for i, key in enumerate(key_order):
        net = net_row[i]
        max_q = SUBJECT_MAX_Q[key]
        if not (0 <= net <= max_q):
            continue
        results.append(SubjectResult(
            subject=key,
            correct=int(round(correct_row[i])),
            wrong=int(round(wrong_row[i])),
            blank=0,
            net=round(net, 2),
        ))
    return results


def _extract_col_after_header(text: str, header_re: str, max_n: int = 7) -> list[float]:
    """
    'header_re' ile tam bir satırı bul, ardından gelen sayıları çıkar.
    Sayı olmayan ilk satırda dur; max_n'e ulaşınca da dur.
    \xa0 (non-breaking space) dahil tüm yatay boşluklar [ \t\xa0]* ile yakalanır.
    """
    m = re.search(r'(?:^|\n)[ \t\xa0]*(?:' + header_re + r')[ \t\xa0]*\r?\n', text, re.IGNORECASE)
    if not m:
        return []
    vals: list[float] = []
    for line in text[m.end():].split('\n'):
        stripped = line.strip()
        if not stripped:
            continue
        try:
            vals.append(_parse_float(stripped))
            if len(vals) >= max_n:
                break
        except ValueError:
            break
    return vals


def _extract_subjects_sbs_karne(text: str) -> list[SubjectResult]:
    """
    SBS Karne transposed-tablo formatı — Mozaik, Final (8. Sınıf Deneme), TÖDER.

    Tablo yapısı: ders adları alt alta, ardından her metrik için ayrı sütun bloğu:
      SORU SAYISI  →  7 değer (birer satır)
      DOĞRU CEVAP  →  7 değer
      YANLIŞ CEVAP →  7 değer
      NET          →  7 float değer

    PDF'deki sabit konu sırası (TOPLAM 7. sıradadır, atlanır):
      [0]=turkce  [1]=matematik  [2]=din  [3]=fen  [4]=sosyal  [5]=ydil  [6]=TOPLAM
    """
    net_vals    = _extract_col_after_header(text, r'NET')
    dogru_vals  = _extract_col_after_header(text, r'DOĞRU\s*CEVAP')
    yanlis_vals = _extract_col_after_header(text, r'YANLIŞ\s*CEVAP')

    if len(net_vals) < 6:
        logger.debug("[SBSKarne] NET sütunu yetersiz: %d değer", len(net_vals))
        return []

    key_order = ["turkce", "matematik", "din", "fen", "sosyal", "ydil"]
    results: list[SubjectResult] = []
    for i, key in enumerate(key_order):
        net = net_vals[i]
        max_q = SUBJECT_MAX_Q[key]
        if not (0 <= net <= max_q):
            logger.debug("[SBSKarne] %s net=%.2f aralık dışı, atlanıyor", key, net)
            continue
        correct = int(round(dogru_vals[i]))  if i < len(dogru_vals)  else 0
        wrong   = int(round(yanlis_vals[i])) if i < len(yanlis_vals) else 0
        results.append(SubjectResult(
            subject=key,
            correct=correct,
            wrong=wrong,
            blank=0,
            net=round(net, 2),
        ))
    return results


def _extract_subjects_fmt3(text: str) -> list[SubjectResult]:
    """
    Format 3: Final / TÖDER — tarihten sonra gruplı sayı blokları.

    Yapı (tarihten sonra):
      [4 int: soru T/F/S/D] [4 float: başarı% - hepsi >20] [4 int: doğru]
      [4 int: yanlış] [4 float: net ≤20] ...

    Başarı% grubu (hepsi >20) referans noktası; NET grubu ondan 12 öğe sonra.
    Konu sırası: [turkce, fen, sosyal, din] — PDF sonundaki konu beyanından.
    Mat ve Y.Dil için kazanım özetinden hesaplanır.
    """
    # Tarihi bul — ilk D.M.YYYY veya DD.MM.YYYY
    date_m = re.search(r"\b\d{1,2}\.\d{1,2}\.\d{4}\b", text)
    if not date_m:
        return []

    remaining = text[date_m.end():]
    raw_nums = re.findall(r"-?\d+(?:[,\.]\d+)?", remaining)

    floats: list[float] = []
    for n in raw_nums:
        try:
            floats.append(_parse_float(n))
        except ValueError:
            break

    # Başarı% grubunu bul: art arda 4 değer hepsi > 20
    baspct_start = -1
    for i in range(len(floats) - 3):
        if all(floats[i+j] > 20 for j in range(4)):
            baspct_start = i
            break
    if baspct_start < 0 or baspct_start + 16 >= len(floats):
        return []

    net_start = baspct_start + 12  # doğru(4) + yanlış(4) + ofset(4) = +12
    net4 = floats[net_start:net_start + 4]
    doğru4 = floats[baspct_start + 4: baspct_start + 8]
    yanlış4 = floats[baspct_start + 8: baspct_start + 12]

    # İlk 4 konu sırası: turkce, fen, sosyal, din
    key_order4 = ["turkce", "fen", "sosyal", "din"]
    results: list[SubjectResult] = []
    for i, key in enumerate(key_order4):
        net = net4[i]
        max_q = SUBJECT_MAX_Q[key]
        if not (0 <= net <= max_q):
            continue
        results.append(SubjectResult(
            subject=key,
            correct=int(round(doğru4[i])),
            wrong=int(round(yanlış4[i])),
            blank=0,
            net=round(net, 2),
        ))

    # Mat ve Y.Dil: kazanım özetinden hesapla
    for subj_key, subj_label in [("matematik", "MATEMATİK"), ("ydil", "Y.D[İI]L|[İI]NG[İI]L[İI]ZCE|INGILIZCE")]:
        d_total = y_total = 0
        pattern = rf"(?:{subj_label})\n[^\n]+\n(\d+)\n(\d+)\n(\d+)\n-?\d+"
        for km in re.finditer(pattern, remaining, re.IGNORECASE):
            try:
                d_total += int(km.group(2))
                y_total += int(km.group(3))
            except (ValueError, IndexError):
                continue
        if d_total > 0 or y_total > 0:
            net = round(d_total - y_total / 3, 2)
            max_q = SUBJECT_MAX_Q[subj_key]
            if 0 <= net <= max_q:
                results.append(SubjectResult(
                    subject=subj_key,
                    correct=d_total,
                    wrong=y_total,
                    blank=0,
                    net=net,
                ))

    return results


def _extract_subjects(text: str) -> list[SubjectResult]:
    """
    Ders bazlı D/Y/B/Net verilerini çıkar.

    Dener:
      1. Tablo satırı: "TÜRKÇE  15  4  1  13.67"
      2. D:Y:B etiketli: "D:15 Y:4 B:1 Net:13.67"
      3. Sadece net: "Türkçe.*13.67"
    """
    results: list[SubjectResult] = []

    for key, subj_pat in SUBJECT_RE:
        net, correct, wrong, blank = _find_subject_scores(text, subj_pat)
        if net is None and correct is None:
            continue
        if net is None and correct is not None:
            w = wrong or 0
            net = round(correct - w / 3, 2)
        if net is None:
            continue

        max_q = SUBJECT_MAX_Q[key]
        # Basit aralık doğrulaması
        if not (0 <= net <= max_q):
            logger.debug("[GenericPDF] %s net=%.2f aralık dışı, atlanıyor", key, net)
            continue

        results.append(SubjectResult(
            subject=key,
            correct=correct or 0,
            wrong=wrong or 0,
            blank=blank or 0,
            net=net,
        ))

    return results


def _find_subject_scores(
    text: str, subj_pat: str
) -> tuple[float | None, int | None, int | None, int | None]:
    """
    Verilen ders pattern'i için (net, correct, wrong, blank) döndür.
    Bulunamazsa ilgili alan None.
    """
    num = r"(\d{1,2})"
    flt = r"([\d,\.]{1,6})"

    # ── Pattern 0: 5-column "DERS SORU D Y B NET" ─────────────────────────
    # "TÜRKÇE 20 15 4 1 13.67" → SORU=20(atla), D=15, Y=4, B=1, net=13.67
    # 4-column'dan önce denenmeli; net değeri float olduğunda 5-sütunu tercih et.
    p0 = rf"(?:{subj_pat})\s+\d{{1,2}}\s+{num}\s+{num}\s+{num}\s+{flt}"
    m = re.search(p0, text, re.IGNORECASE)
    if m:
        try:
            net_val = _parse_float(m.group(4))
            # Eğer net float kısmı var (.xx) ise 5-column parse doğru
            if ',' in m.group(4) or '.' in m.group(4):
                return net_val, int(m.group(1)), int(m.group(2)), int(m.group(3))
        except (ValueError, IndexError):
            pass

    # ── Pattern 1: tablo satırı "DERS  D  Y  B  net" ──────────────────────
    p1 = rf"(?:{subj_pat})\s+{num}\s+{num}\s+{num}\s+{flt}"
    m = re.search(p1, text, re.IGNORECASE)
    if m:
        try:
            return _parse_float(m.group(4)), int(m.group(1)), int(m.group(2)), int(m.group(3))
        except (ValueError, IndexError):
            pass

    # ── Pattern 2: D: Y: B: Net: etiketli ────────────────────────────────
    p2 = rf"(?:{subj_pat})[^\n]*?D\s*[:\s]\s*{num}[^\n]*?Y\s*[:\s]\s*{num}[^\n]*?B\s*[:\s]\s*{num}[^\n]*?Net\s*[:\s]\s*{flt}"
    m = re.search(p2, text, re.IGNORECASE | re.DOTALL)
    if m:
        try:
            return _parse_float(m.group(4)), int(m.group(1)), int(m.group(2)), int(m.group(3))
        except (ValueError, IndexError):
            pass

    # ── Pattern 3: sadece net ─────────────────────────────────────────────
    p3 = rf"(?:{subj_pat})[^\n]{{0,60}}(?:Net|NET)\s*[:\s]\s*{flt}"
    m = re.search(p3, text, re.IGNORECASE)
    if m:
        try:
            return _parse_float(m.group(1)), None, None, None
        except (ValueError, IndexError):
            pass

    # ── Pattern 4: ders adından sonraki ilk float (gevşek) ───────────────
    p4 = rf"(?:{subj_pat})\s+\d{{1,2}}\s+\d{{1,2}}\s+\d{{1,2}}\s+({flt})"
    m = re.search(p4, text, re.IGNORECASE)
    if m:
        try:
            return _parse_float(m.group(1)), None, None, None
        except (ValueError, IndexError):
            pass

    # ── Pattern 5: ders adı + satır sonu artığı + alt satırlarda D Y B net ─
    # "Din K.ve A.B.\n10\n9\n1\n8,67" gibi uzun/kesintili ders adları için
    p5 = rf"(?:{subj_pat})[^\n\d]{{0,35}}\n{num}\n{num}\n{num}\n{flt}"
    m = re.search(p5, text, re.IGNORECASE)
    if m:
        try:
            return _parse_float(m.group(4)), int(m.group(1)), int(m.group(2)), int(m.group(3))
        except (ValueError, IndexError):
            pass

    return None, None, None, None


# ── Ana adaptör sınıfı ─────────────────────────────────────────────────────────

class GenericPDFAdapter(BaseAdapter):
    """
    Herhangi bir LGS PDF'ini ayrıştırır.
    Yayıncıya özel adaptörler mevcut olmadığında veya UNKNOWN publisher'da
    bu sınıf devreye girer.
    """
    source_type = "pdf_generic"

    def parse(self, pdf_path: Path) -> NormalizedExamResult:
        with open(pdf_path, "rb") as f:
            return self.parse_bytes(f.read(), filename=pdf_path.name)

    def parse_bytes(self, content: bytes, filename: str = "upload.pdf") -> NormalizedExamResult:
        try:
            doc = pymupdf.open(stream=content, filetype="pdf")
        except Exception as exc:
            raise ParseError(f"PDF açılamadı ({filename}): {exc}") from exc

        pages = len(doc)
        full_text = "\n".join(page.get_text() for page in doc)
        doc.close()

        logger.info("[GenericPDF] %s — %d sayfa, %d karakter metin", filename, pages, len(full_text))

        if len(full_text.strip()) < 20:
            raise ParseError(
                f"PDF metin içermiyor ({filename}) — taranmış görüntü olabilir, OCR gerekebilir."
            )

        student_name = _extract_student_name(full_text)
        grade        = _extract_grade(full_text)
        exam_date    = _extract_date(full_text)
        exam_name    = _extract_exam_name(full_text, filename)

        # Format tespiti ve uygun konu çıkarıcı seçimi
        if re.search(r"SINAV\s+SONU[CÇ]\s+BELGES[İI]", full_text, re.IGNORECASE) \
                and re.search(r"SOYADI\s*[-–]\s*ADI", full_text, re.IGNORECASE):
            # Format 2: AKBİM TÜRKİYE GENELİ
            subjects = _extract_subjects_akbim_tg(full_text)
            logger.info("[GenericPDF] %s → Format 2 (AKBİM TG) kullanıldı, ders=%d", filename, len(subjects))
        elif re.search(r'SORU\s*SAYISI', full_text, re.IGNORECASE) \
                and re.search(r'DOĞRU\s*CEVAP', full_text, re.IGNORECASE):
            # SBS Karne: Mozaik, Final (8. Sınıf Deneme), TÖDER — transposed tablo
            subjects = _extract_subjects_sbs_karne(full_text)
            logger.info("[GenericPDF] %s → SBS Karne formatı kullanıldı, ders=%d", filename, len(subjects))
        elif re.search(r"^\d{5,6}$", full_text.split('\n')[0].strip()) \
                and re.search(r"\b\d{1,2}\.\d{1,2}\.\d{4}\b", "\n".join(full_text.split('\n')[:6])):
            # Format 3: Final / TÖDER (MEB kodu + 4. satırda tarih)
            subjects = _extract_subjects_fmt3(full_text)
            logger.info("[GenericPDF] %s → Format 3 (Final/TÖDER) kullanıldı, ders=%d", filename, len(subjects))
        else:
            subjects = _extract_subjects(full_text)

        total_score  = _extract_total_score(full_text, subjects)

        logger.info(
            "[GenericPDF] %s → öğrenci=%r  sınıf=%r  tarih=%s  ders_sayısı=%d  puan=%.2f",
            filename,
            student_name or "(bulunamadı)",
            grade or "(bulunamadı)",
            exam_date,
            len(subjects),
            total_score,
        )

        if not subjects:
            logger.warning(
                "[GenericPDF] %s — HİÇBİR ders neti çıkarılamadı. "
                "PDF formatı bilinmiyor olabilir.",
                filename,
            )

        return NormalizedExamResult(
            student_name=student_name or "Bilinmeyen Öğrenci",
            grade=grade,
            exam_name=exam_name,
            exam_date=exam_date,
            source_type="pdf_generic",
            publisher=None,
            raw_source_ref=filename,
            total_score=total_score,
            subjects=subjects,
        )
