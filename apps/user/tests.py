from django.test import TestCase
from celery_tasks.tasks import send_register_active_email
# Create your tests here.

email = 'flows_sun@163.com'
username = 'zhuyanzhang'
token = 'ajsdahs'
send_register_active_email.delay(email,username,token)