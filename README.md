# News.uz

**Yangilikni admin panelida tayyorlang, saytda e’lon qiling va Telegram kanaliga yuboring.**

![News.uz uchun Toshkent mavzusidagi illyustratsiya](news/static/news/newsroom-cover.webp)

**Python · Django · Django REST Framework · SQLite**

News.uz — o‘zbek tilidagi yangiliklar portali. Bosh sahifa e’lon qilingan yangiliklarni, xronologik lentani va haqiqiy ko‘rishlar soniga asoslangan **Ko‘p o‘qilgan** bo‘limini ko‘rsatadi. Sayt kompyuter va telefon ekranlariga moslashadi.

## Ishlaydigan funksiyalar

- Yangiliklar arxivi, qidiruv, kategoriya filtri va qo‘shimcha rasmlar
- Ro‘yxatdan o‘tish, email yoki username bilan kirish, profil va avatar
- Izoh yozish va admin tasdig‘idan so‘ng saytda ko‘rsatish
- Yangilikni saqlab qo‘yish va email obunasi API’lari
- Yangilikni rasm va havola bilan Telegramga yuborish, yuborish jurnali va qayta urinish

## Lokal ishga tushirish

Python 3.14 o‘rnatilgan PowerShell terminalida:

```powershell
py -3.14 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
$env:DJANGO_SECRET_KEY = (.\.venv\Scripts\python.exe -c "import secrets; print(secrets.token_urlsafe(64))")
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py createsuperuser
.\.venv\Scripts\python.exe manage.py runserver
```

[Sayt](http://127.0.0.1:8000/) va [admin panel](http://127.0.0.1:8000/admin/) lokal serverda ochiladi. Admin panelida avval kategoriya yarating, keyin yangilik qo‘shib **E’lon qilingan** holatiga o‘tkazing. Yangi lokal bazada yangiliklarni admin orqali qo‘shasiz.

Telegram uchun `TELEGRAM_BOT_TOKEN`ni muhit o‘zgaruvchisi sifatida kiriting. So‘ng admin’dagi **Telegram settings** bo‘limida kanalni belgilang va **Auto send**ni yoqing. Yangilik nashrida **Send to telegram**ni belgilang. Tashqi o‘quvchilar havolani ochishi uchun `SITE_URL`ni saytning ochiq manziliga sozlang.

Lokal muhitda email xatlari terminalga chiqadi. SMTP uchun `EMAIL_BACKEND` qiymatini `django.core.mail.backends.smtp.EmailBackend`ga o‘rnating va Gmail manzili hamda ilova parolini muhit o‘zgaruvchilaridan bering. Kerakli nomlar [.env.example](.env.example) faylida keltirilgan. Loyiha ularni operatsion tizim muhitidan o‘qiydi.

## Kod tuzilishi

| Papka | Vazifasi |
|---|---|
| `config` | Sozlamalar va URL manzillari |
| `accounts` | Hisoblar, login, profil va parol tiklash |
| `news` | Yangiliklar, kategoriyalar, bannerlar va sayt sahifalari |
| `engagement` | Izohlar, saqlangan yangiliklar va obunalar |
| `telegram_integration` | Telegramga yuborish va yuborish jurnali |

Sayt sahifalarini Django HTML qilib beradi. Login va izoh yuborish uchun frontend shu serverdagi REST API’ga murojaat qiladi. E’lon qilingan yangilik uchun Telegramga yuborish bazadagi saqlash muvaffaqiyatli tugagach boshlanadi.

---

PROWEB Python backend kursi uchun tayyorlangan o‘quv loyihasi.
