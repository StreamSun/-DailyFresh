from django.conf import settings
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import render,redirect
from django.views.generic import View
import re
from .models import User,Address
from apps.goods.models import GoodsSKU
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import SignatureExpired
from django.contrib.auth import authenticate, login, logout
from celery_tasks.tasks import send_register_active_email
# /register
def register(request):
    return render(request,'register.html')
"""
1.接受参数
2.校验参数
3.逻辑处理
4.返回响应
"""

class RegisterView(View):
    """注册"""
    def get(self,request):
        return render(request,'register.html')

    def post(self,request):
        # print('post')
        # 接收数据
        username = request.POST.get('user_name')
        password = request.POST.get('pwd')
        email = request.POST.get('email')

        # 校验数据
        if not all([username,password,email]):
            return render(request, 'register.html',{'errmsg':'注册信息不完整'})
        # 邮箱验证
        if not re.match(r'^[a-z0-9][\w.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$',email):
            return render(request, 'register.html', {'errmsg': '邮箱格式不正确'})

        # 验证用户是否存在
        try:
            user = User.objects.get(username=username)
            return render(request, 'register.html',{'errmsg':'用户名已被注册'})
        except User.DoesNotExist:
            user = None

        # 创建新用户
        user = User.objects.create_user(username, email, password)
        user.is_active = 0
        user.save()
        # 对用户信息进行加密
        seriallizer = Serializer(settings.SECRET_KEY,3600)
        userinfo = {'uid':user.id}
        token = seriallizer.dumps(userinfo) # bytes
        token = token.decode()
        # 组织邮件内容

        # subject = '天天生鲜欢迎信息'
        # message = ''
        # sender = settings.EMAIL_FROM
        # reciver = [email]
        # html_message ="""
        #     <h1>%s, 欢迎您成为天天生鲜注册会员</h1>
        #     请点击以下链接激活您的账号<br/>
        #     <a href="http://127.0.0.1:8000/user/active/%s">http://127.0.0.1:8000/user/active/%s</a>
        #     """ % (username, token, token)
        #
        # # send_mail(subject='邮件标题', message='邮件正文', from_email='发件人', recipient_list='收件人邮箱列表',html_message='带html格式的信息)
        # send_mail(subject,message,sender,reciver,html_message=html_message)
        # print('邮件已发送')
        #发送任务
        # print(email)
        # print(username)
        # print(token)
        send_register_active_email.delay(email,username,token)

        # 返回响应
        return redirect(reverse('goods:index'))

class ActiveView(View):
    """激活"""
    def get(self,request,token):
        print('激活')
        """激活处理"""
        serializer = Serializer(settings.SECRET_KEY,36000)
        try:
            # 解密
            userinfo = serializer.loads(token)
            uid = userinfo['uid']
            # 激活用户
            user = User.objects.get(id=uid)
            user.is_active = 1
            user.save()

            return redirect(reverse('user:login'))
        except SignatureExpired as e:
            return HttpResponse("<h1>激活链接已失效</h1>")

class LoginView(View):
    """登录"""
    def get(self,request):
        if "username" in request.COOKIES:
            username = request.COOKIES['username']
            checked = 'checked'
        else:
            username = ''
            checked = ''
        context = {'username':username,
                   'checked':checked}
        return render(request,'login.html',context)

    def post(self,request):
        username = request.POST.get('username')
        password = request.POST.get('pwd')
        # 参数校验
        if not all([username, password]):
            return render(request, 'login.html', {'errmsg': '数据不完整'})

        # 鉴定用户为username密码为password的用户是否存在，如果存在返回用户对象，否则返回None
        user = authenticate(username=username,password=password)
        if user is not None:
            if user.is_active:
                # 账户已激活
                # 记住用户的登录状态
                login(request,user)
                # 获取地址栏参数
                next_url = request.GET.get('next',reverse('goods:index')) # 第二个参数为默认返回值，如果next为空，则返回第二个参数的值
                response = redirect(next_url)
                # 设置是否记住用户名
                remember = request.POST.get('remember')
                if remember == 'on':
                    response.set_cookie('username',username,max_age=7*24*3600)
                else:
                    response.delete_cookie('username')
                return response
            else:
                return render(request, 'login.html', {'errmsg': '账户未激活'})
        else:
            return render(request, 'login.html', {'errmsg': '用户名或密码错误'})

class LogoutView(View):
    def get(self,request):
        logout(request)
        return redirect(reverse('user:login'))

from utils.mixin import LoginRequiredView
from utils.mixin import LoginRequiredMixin
# 用户中心信息页
# class UserInfoView(View):
# class UserInfoView(LoginRequiredView):
class UserInfoView(LoginRequiredMixin,View):
    def get(self,request):
        # 接收数据
        user = request.user
        print(user)
        try:
            address = Address.objects.get(user=user,is_default=True)
        except Address.DoesNotExist as e:
            address = None
        # 获取浏览记录
        # 连接数据库
        from django_redis import get_redis_connection
        conn = get_redis_connection('default')
        # 拼接key
        history_key = 'history_%d'%user.id
        # 获取用户最新浏览的5个商品id
        sku_ids = conn.lrange(history_key,0,4) # 返回列表[2,3,5,1,4]
        # 重新排序
        skus = []
        for sku_id in sku_ids:
            sku = GoodsSKU.objects.get(id=sku_id)
            skus.append(sku)

        # 组织模板上下文
        context = {'page': 'info',
                   'address': address,
                   'skus':skus}
        return render(request, 'user_center_info.html', context)
# 用户中心订单页
# class UserOrderView(View):
# class UserOrderView(LoginRequiredView):
class UserOrderView(LoginRequiredMixin,View):
    def get(self,request):
        return render(request,'user_center_order.html',{'page':'order'})
# 用户中心地址页
# class UserAddressView(View):
# class UserAddressView(LoginRequiredView):
class UserAddressView(LoginRequiredMixin,View):
    def get(self,request):
        user = request.user
        print(user)
        address = Address.objects.get_default_addr(user)
        other_addrs = Address.objects.filter(user=user).exclude(is_default=True)
        context = {'page':'address',
                   'address':address,
                   'other_addrs':other_addrs}
        return render(request,'user_center_site.html',context)

    def post(self,request):
        # 接收数据
        receiver = request.POST.get('receiver')
        addr = request.POST.get('addr')
        zip_code = request.POST.get('zip_code')
        phone = request.POST.get('phone')
        remember = request.POST.get('remember')
        # 校验数据
        if not all([receiver,addr,phone]):
            return render(request,'user_center_site.html',{'errmsg':'数据不完整'})
        # 业务处理
        #判断要不要设置为默认地址
        user = request.user
        is_default = False
        if remember == 'on':
            address = Address.objects.get_default_addr(user)
            if address:
                address.is_default = False
                address.save()
            is_default = True


        # try:
        #     address = Address.objects.get(user=user,is_default=True)
        #     is_default = False
        # except Address.DoesNotExist:
        #     address = None
        #     is_default = True

        # 设置默认为True
        # is_default = True
        # # 如果能在数据库查到默认地址，就改为False
        # if address:
        #     is_default = False
        # # 添加地址
        Address.objects.create(user=user,
                               receiver=receiver,
                               addr=addr,
                               zip_code=zip_code,
                               phone=phone,
                               is_default=is_default)
        # 返回响应
        return redirect(reverse('user:address'))

class Set_Default_addr(LoginRequiredMixin,View):
    def get(self,request):
        user = request.user
        address = Address.objects.get(user=user, is_default=True)
        address.is_default = False
        address.save()
        receiver = request.GET.get('name')
        addr = Address.objects.get(user=user,receiver=receiver)
        addr.is_default = True
        addr.save()

        return redirect(reverse('user:address'))














