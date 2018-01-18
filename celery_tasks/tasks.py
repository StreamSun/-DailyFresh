from django.conf import settings
from django.core.mail import send_mail
from celery import Celery

# 配置环境变量
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "DailyFresh.settings")



# 创建一个Celery类对象
app = Celery('celecry_tasks.tasks',broker='redis://127.0.0.1:6379/13')



# 定义任务函数
@app.task
def send_register_active_email(to_email,username,token):
    print('发送邮件')
    # 组织邮件内容
    subject = '天天生鲜欢迎信息'
    message = ''
    sender = settings.EMAIL_FROM
    reciver = [to_email]
    html_message = """
               <h1>%s, 欢迎您成为天天生鲜注册会员</h1>
               请点击以下链接激活您的账号<br/>
               <a href="http://127.0.0.1:8000/user/active/%s">http://127.0.0.1:8000/user/active/%s</a>
               """ % (username, token, token)

    # send_mail(subject='邮件标题', message='邮件正文', from_email='发件人', recipient_list='收件人邮箱列表',html_message='带html格式的信息)
    send_mail(subject, message, sender, reciver, html_message=html_message)
