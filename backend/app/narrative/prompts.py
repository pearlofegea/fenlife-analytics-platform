"""
7 bölümlü rapor için Claude prompt şablonları.

Taha'nın standart rapor formatına birebir uyumlu.
"""

SYSTEM_PROMPT = """
Sen FENlife Eğitim Kurumları'nda çalışan bir Akademik Gelişim ve Takip
Uzmanısın. Öğrenci sınav verilerini analiz edip öğretmen, rehberlik ve
velilere yönelik somut aksiyonlar üretirsin.

Prensip: Veri temelli, suçlamasız, öğrenci için yapıcı dil kullan.
"Zayıf" yerine "gelişim alanı", "yanlış" yerine "atlanan kazanım" tercih et.
"""

OGRENCI_OZETI_PROMPT = """
Aşağıdaki veriye dayanarak öğrenci özetini 2-3 cümle ile yaz:
{features_json}
"""

# TODO Sprint 5: diğer bölüm prompt'ları
