from django.conf.urls import url
from .views import RegisterView,ActiveView,LoginView,LogoutView,UserAddressView,UserInfoView,UserOrderView,Set_Default_addr
from django.contrib.auth.decorators import login_required

urlpatterns = [

    url(r'^register$',RegisterView.as_view(),name='register'),
    url(r'^active/(?P<token>.*)$',ActiveView.as_view(),name='active'),
    url(r'^login$',LoginView.as_view(),name='login'),
    url(r'^logout$',LogoutView.as_view(),name='logout'),

    # 装饰器灵魂代码
    # func = login_required(func),手动对函数进行装饰，传入被装饰的函数调用，返回被装饰后的同名函数调用
    # url(r'^$',login_required(UserInfoView.as_view()),name='info'),
    # url(r'^order$',login_required(UserOrderView.as_view()),name='order'),
    # url(r'^address',login_required(UserAddressView.as_view()),name='address'),

    url(r'^$',UserInfoView.as_view(),name='info'),
    url(r'^order$',UserOrderView.as_view(),name='order'),
    url(r'^address',UserAddressView.as_view(),name='address'),
    url(r'^set_addr$',Set_Default_addr.as_view(),name='set_addr')

]