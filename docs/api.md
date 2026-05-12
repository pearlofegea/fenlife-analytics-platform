# API Referansı

Backend base URL: `http://localhost:8000`
Tam Swagger UI: `http://localhost:8000/docs`

## Endpoints

### `GET /health`
Backend ayakta mı kontrol.

**Response:**
```json
{ "status": "ok", "service": "fenlife-backend" }
```

### `POST /api/generate-report`
Birden fazla PDF yükle, rapor üretimi başlat.

**Request:** `multipart/form-data`, field adı `files` (tekrarlı)

**Response:**
```json
{
  "job_id": "uuid-v4",
  "status": "pending",
  "file_count": 5
}
```

### `GET /api/download/{job_id}`
Üretilen DOCX raporunu indir.

**Response:** DOCX dosyası (application/vnd.openxmlformats-officedocument.wordprocessingml.document)

### `GET /api/students`
Tüm öğrencileri listele. (Sprint 5+ gerçek veri)

### `GET /api/students/{student_id}`
Tek öğrenci detayı.
