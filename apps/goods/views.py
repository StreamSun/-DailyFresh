from django.shortcuts import render
from django.views.generic import View
from .models import *
from django_redis import get_redis_connection
# Create your views here.

class IndexView(View):
    """首页"""
    def get(self,request):
        """显示"""
        # 获取商品种类信息
        types = GoodsType.objects.all()
        # print(types)
        # 获取轮播商品信息
        index_banners = IndexGoodsBanner.objects.all()
        # print(index_banners)
        # 获取促销活动商品信息
        promotion_banners = IndexPromotionBanner.objects.all()
        # print(promotion_banners)
        # 获取分类商品展示信息
        for type in types:
            # 标题显示
            title_banners = IndexTypeGoodsBanner.objects.filter(type=type,display_type=0).order_by('index')
            # 图片显示
            image_banners = IndexTypeGoodsBanner.objects.filter(type=type,display_type=1).order_by('index')
            #保存在商品种类属性中
            type.title_banners = title_banners
            type.image_banners = image_banners
        # 获取购物车商品数量
        # 默认为0
        cart_count = 0
        # 获取当前用户信息
        user = request.user
        # 判断是否有用户登录
        if user.is_authenticated():
            conn = get_redis_connection('default')
            # 拼接key
            cart_key = 'cart_%d'%user.id
            # print(cart_key)
            # 查询购物车信息
            cart_count = conn.hlen(cart_key)
            # print(cart_count)
        # 组织上下文
        context={'types':types,
            'index_banners':index_banners,
            'promotion_banners':promotion_banners,
            'cart_count':cart_count
        }

        return render(request,'index.html',context)
