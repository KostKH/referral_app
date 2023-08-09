from referral_app.celery import app


@app.task
def send_sms(phone, code):
    """Задача имитирует отправку sms с кодом верификации."""
    return f'Код верификации {code}, номер телефона {phone}'
