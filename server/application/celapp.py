import os

from celery import Celery


celapp = Celery('lindep_celery')
celapp.conf.broker_url = os.environ.get('CELERY_BROKER_URL')
celapp.conf.result_backend = os.environ.get('CELERY_RESULT_BACKEND')
