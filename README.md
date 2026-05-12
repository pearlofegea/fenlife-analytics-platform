# FENlife Analytics

**Akademik Gelişim ve Takip Planlama Sistemi**
LGS öğrencileri için PDF sınav sonuçlarını analiz edip otomatik DOCX raporu üreten, dashboard destekli platform.

---

## Projenin Güncel Amacı

Herhangi bir kuruma veya PDF formatına bağımlı olmayan, kaynak bağımsız öğrenci sınav analiz sistemi. Öğrenciye ait sınav sonuçları (tek dosya veya birden fazla dosya olarak) sisteme alınır; normalize edilir, analiz edilir ve FENlife markalı DOCX raporu üretilir. Tüm veri PostgreSQL'de kalıcı olarak saklanır.

**Veri esnekliği:**
- Tek PDF yüklenilebilir veya birden fazla PDF yüklenebilir
- Sistem dosya sayısından değil, içindeki normalize edilmiş sınav verisi sayısından etkilenir
- **En az 5 sınav verisi önerilir** — eğilim analizi ve karşılaştırmalı içgörüler için
- 5'ten az veriyle de rapor üretilir; analiz derinliği sınav sayısına göre uyarlanır
- Sert "5 dosya zorunlu" engeli yoktur; kullanıcıya bilgilendirici uyarı gösterilir

**Analiz kalitesi seviyeleri:**
| Sınav Sayısı | Seviye | Sunulan Analiz |
|---|---|---|
| 1–2 | Sınırlı | Anlık görüntü; trend/karşılaştırma yoktur |
| 3–4 | Temel | Temel karşılaştırma yapılabilir; eğilim yorumu sınırlıdır |
| 5+ | Güçlü | Eğilim analizi, risk değerlendirmesi, gelişim takibi |

**Mimari ilke:** Input Adapters → Normalized Schema → Analysis Engine → Report Output.
AKBIM, TÖDER, Nartest gibi yayınevleri birer örnek input kaynağıdır; zorunlu bağımlılık değildir.
LLM/Claude entegrasyonu şu an kapsam dışındadır.

---

## Genel Mimari

```
Kullanıcı
    ↓ 1+ PDF yükler (5+ önerilir)
[Next.js /reports/generate]
    ↓ POST /api/reports (multipart)
[FastAPI]
    ├─ repositories/report_job_repo  → ReportJob kaydı oluştur (PostgreSQL)
    ├─ detector.detect_publisher()   → yayınevi tespiti        (Sprint 2)
    ├─ PublisherParser.parse()       → ParsedExam listesi      (Sprint 2)
    ├─ IdentityResolver.resolve()    → öğrenci gruplandırma    (Sprint 2)
    ├─ compute_trend() + classify_risk()                        (Sprint 2)
    ├─ weakness() + difficulty_gap()                            (Sprint 2)
    └─ ReportGenerator + charts     → {job_id}.docx            (Sprint 3)
    ↓ { job_id, status }
[Next.js /reports/preview/{jobId}]
    ↓ GET /api/reports/{jobId}  (3s polling)
    ↓ GET /api/reports/{jobId}/download
Kullanıcı DOCX alır

Dashboard (ayrı akış):
[Next.js /dashboard]
    ↓ mock-data.ts (şu an) → GET /api/students/{id}/dashboard (Sprint 2+)
[DashboardShell → StudentSelector + 5 sekme]

Veri katmanı:
[Repository Layer] ← tüm route'lar buraya bağlı
    └─ [PostgreSQL] ← kalıcı depolama
```

---

## Frontend Yapısı

```
frontend/
├── app/
│   ├── layout.tsx                  ← root layout, font'lar
│   ├── page.tsx                    ← ana sayfa (2 kart: Dashboard / Rapor Üret)
│   ├── globals.css                 ← FENlife design tokens
│   ├── dashboard/
│   │   └── page.tsx                ← DashboardShell'i import eder
│   └── reports/
│       ├── generate/page.tsx       ← PDF yükleme, UploadZone bileşeni
│       └── preview/[jobId]/page.tsx← 3s polling, DOCX indirme
│
├── components/
│   ├── dashboard/
│   │   ├── DashboardShell.tsx      ← ana orchestrator (state: seçili öğrenci, aktif sekme)
│   │   ├── StudentSelector.tsx     ← 6 öğrenci kartı
│   │   ├── shared/
│   │   │   ├── StatCard.tsx
│   │   │   └── RiskBadge.tsx
│   │   └── tabs/
│   │       ├── OverviewTab.tsx     ← stat cards, area chart, ders bar
│   │       ├── TrendTab.tsx        ← ders line chart, deneme tablosu
│   │       ├── DifficultyTab.tsx   ← zorluk bar + radar chart
│   │       ├── TopicsTab.tsx       ← öncelikli kazanım listesi
│   │       └── ActionsTab.tsx      ← branş/rehber/çalışma kağıdı önerileri
│   └── reports/
│       └── UploadZone.tsx          ← drag-drop PDF upload bileşeni
│
└── lib/
    ├── types.ts                    ← tüm TypeScript tipleri + SUBJECT_META sabiti
    ├── api-client.ts               ← tüm backend HTTP çağrıları
    ├── analytics.ts                ← computeTrend, computeRisk, computeSubjectAverages
    └── mock-data.ts                ← dev/test fixture (MOCK_STUDENTS — 6 öğrenci)
```

### Dashboard Entegrasyon Planı

Dashboard şu an `mock-data.ts`'deki sabit verilerle çalışır.
Parser pipeline hazır olduğunda geçiş adımı yalnızca `DashboardShell.tsx`'de gerçekleşir:

```typescript
// Şu an:
import { MOCK_STUDENTS } from '@/lib/mock-data';

// Geçiş sonrası:
const data = await apiClient.getDashboard(studentId);
```

Tüm tab bileşenleri değişmez; sadece veri kaynağı değişir.

---

## FastAPI Backend Yapısı

```
backend/app/
├── main.py                    ← FastAPI init, CORS, router kayıt
├── config.py                  ← Pydantic BaseSettings (env dosyasından okur)
│
├── api/routes/
│   ├── health.py              ← GET /health
│   ├── reports.py             ← POST /api/reports, GET /api/reports/{id}, GET /api/reports/{id}/download
│   └── students.py            ← GET /api/students, GET /api/students/{id}/dashboard
│
├── db/
│   ├── session.py             ← engine, SessionLocal, get_db() dependency
│   └── models.py              ← 6 SQLAlchemy ORM modeli (PostgreSQL-first)
│
├── repositories/
│   ├── report_job_repo.py     ← create, get, update_status, get_all_completed
│   └── student_repo.py        ← get_by_id, get_or_create (Sprint 2'de kullanılır)
│
├── storage/
│   └── job_store.py           ← DEPRECATED — yalnızca referans, aktif değil
│
├── services/                  ← (Sprint 2'de dolacak)
│   ├── report_service.py      ← pipeline orchestration
│   └── student_service.py
│
├── parser/
│   ├── detector.py            ← 8 yayınevi tespiti (ÇALIŞIYOR)
│   ├── schemas.py             ← ParsedExam, SubjectResult, KazanimBreakdown
│   └── parsers/
│       ├── base.py            ← abstract BasePublisherParser
│       ├── akbim.py           ← TODO Sprint 2
│       ├── toder.py           ← TODO Sprint 2
│       └── nartest.py         ← TODO Sprint 2
│
├── features/
│   ├── trend.py               ← compute_trend() (ÇALIŞIYOR)
│   ├── risk.py                ← classify_risk() (ÇALIŞIYOR)
│   ├── weakness.py            ← TODO Sprint 2
│   └── difficulty_gap.py      ← TODO Sprint 2
│
├── report/
│   ├── generator.py           ← TODO Sprint 3
│   └── charts.py              ← TODO Sprint 3
│
├── narrative/                 ← düşük öncelik (LLM şu an kapsam dışı)
│   ├── claude_client.py
│   └── prompts.py
│
└── models/
    ├── student.py             ← Student (grade kullanılır, class değil)
    ├── exam.py
    └── report.py
```

---

## Veri Akışı

```
POST /api/reports
  → report_job_repo.create()          [PostgreSQL — status: "processing"]
  → (Sprint 2) detect_publisher()
  → (Sprint 2) parser.parse()         → ParsedExam[]
  → (Sprint 2) IdentityResolver       → student gruplandırma
  → (Sprint 2) compute_trend() + classify_risk()
  → (Sprint 2) report_job_repo.update_status() + student/exam kayıtları
  → (Sprint 3) ReportGenerator        → DOCX
  → generated_reports tablosuna kayıt + _output/{job_id}.docx

GET /api/reports/{job_id}
  → report_job_repo.get()             → durum + metadata JSON

GET /api/reports/{job_id}/download
  → FileResponse(_output/{job_id}.docx)
```

---

## API Contract Özeti

| Method | Endpoint | Açıklama |
|--------|----------|----------|
| GET  | `/health` | Sağlık kontrolü |
| POST | `/api/reports` | 1+ PDF yükle, job başlat (5+ önerilir; 202 Accepted) |
| GET  | `/api/reports/{job_id}` | Job durumu + metadata |
| GET  | `/api/reports/{job_id}/download` | DOCX dosyasını indir |
| GET  | `/api/students` | Tamamlanmış job'lardan öğrenci listesi |
| GET  | `/api/students/{id}` | Öğrenci detayı |
| GET  | `/api/students/{id}/dashboard` | Tam dashboard verisi (Sprint 2+) |

**Alan adı kuralı:** Tüm API ve TypeScript modellerinde `grade` kullanılır (`class` değil — reserved keyword).

---

## Klasör Yapısı

```
fenlife-analytics/
├── docker-compose.yml  PostgreSQL local dev container
├── frontend/           Next.js 14 (App Router, React 18, Tailwind, TypeScript)
├── backend/            FastAPI (Python 3.11, SQLAlchemy, Alembic, PyMuPDF, python-docx)
│   ├── alembic.ini     Alembic konfigürasyonu
│   └── alembic/        DB migration'ları
├── sample-data/        Test PDF'leri + örnek çıktı DOCX (gitignore'da)
├── docs/               Mimari ve API dokümantasyonu
├── .vscode/            Workspace ayarları + debug config'leri
├── Makefile            Geliştirme komutları
└── fenlife.code-workspace
```

---

## Nasıl Çalıştırılır

```bash
# 0. PostgreSQL başlat (Docker Desktop açık olmalı)
docker compose up -d db

# 1. Backend kurulumu
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # DATABASE_URL'yi düzenle, ANTHROPIC_API_KEY opsiyonel

# 2. Migration uygula
alembic upgrade head          # 6 tabloyu oluşturur (fenlife.db veya PostgreSQL)

# 3. Frontend kurulumu
cd ../frontend
npm install
cp .env.local.example .env.local   # veya elle: NEXT_PUBLIC_API_URL=http://localhost:8000

# 4. Çalıştır (root dizininden)
make backend    # FastAPI → http://localhost:8000
make frontend   # Next.js → http://localhost:3000
make dev        # ikisi paralel
```

VS Code kullanıcıları: `fenlife.code-workspace` dosyasını açın, önerilen extension'ları kabul edin.

Swagger UI: http://localhost:8000/docs

---

## Mevcut Durum / Roadmap

| Sprint | Odak | Durum |
|--------|------|-------|
| 1 | Skeleton: FastAPI routes, Next.js UI, design system | ✅ Tamamlandı |
| 1b | Dashboard decompose + entegrasyon | ✅ Tamamlandı |
| 1.5 | DB Layer: PostgreSQL + SQLAlchemy + Alembic + repository katmanı | ✅ Tamamlandı |
| 2A | Normalized schema + adapter mimarisi + publisher nullable migration | 🚧 Sıradaki |
| 2B | GenericPDFAdapter — herhangi PDF → NormalizedExamResult | 🔜 Bekliyor |
| 2C | IdentityResolver + DB write (Student, Exam, SubjectResult) | 🔜 Bekliyor |
| 2D | Pipeline orchestration + BackgroundTasks bağlantısı | 🔜 Bekliyor |
| 2E | Dashboard → gerçek API geçişi (mock-data kaldırılır) | 🔜 Bekliyor |
| 3 | DOCX report generator + matplotlib charts | ✅ Tamamlandı (graceful degradation dahil) |
| 4 | Upload UI + preview (polling) | ✅ Tamamlandı |
| 5 | (Opsiyonel) LLM narrative — Claude API | 📋 Kapsam dışı şimdilik |
| 6+ | ML modeller (BKT, forecasting) | 📋 Planlandı |

---

## Yapılan Değişiklikler

### 2026-04-21 — Dashboard Entegrasyonu & Mimari Refactor

**Backend**
- `backend/app/storage/job_store.py` oluşturuldu — in-memory + JSON sidecar job persistence
- `POST /api/generate-report` → `POST /api/reports` (RESTful hizalama)
- `GET /api/reports/{job_id}` endpoint eklendi (önceden yoktu; frontend bunu çağırıyordu ama hata veriyordu)
- `GET /api/reports/{job_id}/download` refactor: job_store üzerinden durum kontrolü, öğrenci adıyla dosya adı
- `GET /api/students/{id}/dashboard` endpoint eklendi
- `backend/app/services/` dizini oluşturuldu (Sprint 2'de dolacak)

**Frontend**
- `lib/types.ts` genişletildi: `DifficultyProfile`, `SubjectDifficulty`, `SubjectAverage`, `RiskResult`, `TrendResult`, `DashboardData`, `CreateReportResponse`, `ReportStatusResponse`, `SUBJECT_META`, `DIFFICULTY_LEVELS` eklendi; `Student.class` → `Student.grade`
- `lib/api-client.ts` güncellendi: `createReport` (yeni isim + doğru URL), `getReportStatus` (doğru URL), `getDashboard`, `listStudents`, `downloadUrl` helper eklendi
- `lib/analytics.ts` oluşturuldu: `computeTrend`, `computeRisk`, `computeSubjectAverages`, `formatDate` — FenlifeDashboard'dan çıkarıldı, TypeScript ile tipli
- `lib/mock-data.ts` oluşturuldu: 6 öğrenci × tam sınav/zorluk/kazanım verisi; dev/test fixture olarak korunur
- `FenlifeDashboard.tsx` (29K satır monolith) → ayrı bileşenlere bölündü:
  - `components/dashboard/DashboardShell.tsx`
  - `components/dashboard/StudentSelector.tsx`
  - `components/dashboard/shared/StatCard.tsx`
  - `components/dashboard/shared/RiskBadge.tsx`
  - `components/dashboard/tabs/OverviewTab.tsx`
  - `components/dashboard/tabs/TrendTab.tsx`
  - `components/dashboard/tabs/DifficultyTab.tsx`
  - `components/dashboard/tabs/TopicsTab.tsx`
  - `components/dashboard/tabs/ActionsTab.tsx`
- `app/dashboard/page.tsx`: placeholder kaldırıldı, `DashboardShell` import edildi
- `components/reports/UploadZone.tsx` refactor: drag-drop desteği, `onFilesAdded` prop, label/sublabel parametreleri
- `app/reports/generate/page.tsx`: inline upload zone → `UploadZone` bileşeni; duplicate dosya filtresi eklendi
- `app/reports/preview/[jobId]/page.tsx`: 3s polling, tüm job metadata gösterimi, `apiClient.downloadUrl()` helper

---

FENlife Eğitim Kurumları · Maltepe / İstanbul
