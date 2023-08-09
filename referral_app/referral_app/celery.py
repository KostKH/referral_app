import os

from celery import Celery

from referral_app.settings import CELERY_BROKER_URL

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'referral_app.settings')
app = Celery('referral_app',
             broker=CELERY_BROKER_URL,
             include=['users.tasks'])
