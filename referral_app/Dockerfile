FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip3 install -r requirements.txt --no-cache-dir
COPY . .
CMD ["gunicorn", "referral_app.wsgi:application", "--workers", "2", "--bind", "0.0.0.0:8000"]
