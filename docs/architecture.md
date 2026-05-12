# FENlife Analytics Mimarisi

## Yüksek seviye akış

```
[Kullanıcı]
    ↓ 5+ PDF yükler
[Next.js Frontend] — app/reports/generate/page.tsx
    ↓ POST /api/generate-report (multipart)
[FastAPI Backend] — app/api/routes/reports.py
    ↓
├─ app/parser/detector.py     yayıncı tespit (pymupdf)
├─ app/parser/parsers/*.py    yayıncıya özel parser
├─ app/identity/resolver.py   kimlik çözümleme (rapidfuzz)
├─ app/features/*.py          trend, risk, zayıf kazanım, zorluk
├─ app/narrative/claude_*.py  Claude API — 7 bölüm metni
└─ app/report/generator.py    python-docx ile FENlife DOCX
    ↓ response: job_id + preview JSON
[Next.js] → reports/preview/[jobId]/page.tsx
    ↓ kullanıcı "İndir" tıklar
[FastAPI] → GET /api/download/{jobId} → DOCX response
```

## Sprint yol haritası

| Sprint | İş | Klasör | Süre |
|---|---|---|---|
| 1 | İskelet + dashboard integrasyonu | frontend/app/dashboard | Tamamlandı (bu iskelet) |
| 2 | PDF parser (AKBİM ilk) | backend/app/parser/ | 1-2 hafta |
| 3 | Feature engineering + DOCX üretimi | backend/app/features/, backend/app/report/ | 2 hafta |
| 4 | Upload UI + preview | frontend/app/reports/ | 1 hafta |
| 5 | LLM narrative katmanı | backend/app/narrative/ | 1-2 hafta |
| 6-8 | ML modeller (BKT, zorluk tahmini, kazanım tespiti) | backend/app/ml/ (sonra) | Paralel |

## Kritik kararlar

**Python-docx kullanıyoruz, Node.js docx değil.** Backend zaten Python olduğu
için subprocess kırılganlığı yok. Mevcut örnek rapor (Node.js ile üretilmiş)
referans olarak tutulacak.

**Monorepo.** Frontend/backend tek repo, VS Code multi-root workspace.

**PDF ilk 300 karakteri keyword tabanlı tespit.** XML placeholder yaklaşımı
yerine — deneme geçmişindeki tüm yayıncıları tek bir dispatcher yönetir.

**5 deneme minimum.** İstatistiksel anlamlılık için (bkz. framework doc).
