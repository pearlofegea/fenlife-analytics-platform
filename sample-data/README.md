# Sample Data

Bu klasöre gerçek öğrenci PDF'lerini koyabilirsiniz. `.gitignore` kuralı
nedeniyle PDF/XLSX/CSV dosyaları Git'e gitmez (gizlilik).

## İçerik

- `ornek_rapor_kaan_colpan.docx` — sistem tarafından üretilmiş örnek FENlife raporu.
  Kaan Çolpan (13 deneme) için 7 bölümlü format, 4 grafik içerir.
  Sistem hazır olunca bu raporun aynısı otomatik üretilecek.

## Test için PDF ekleme

Geliştirme sırasında AKBİM/TÖDER/Nartest gibi örnek PDF'leri buraya koyun:
```
sample-data/
├── akbim_ornek_01.pdf
├── toder_ornek_01.pdf
└── ...
```

Parser test ederken:
```bash
cd backend
.venv/bin/python scripts/test_parser.py --input ../sample-data/akbim_ornek_01.pdf
```
