from django.views.generic import View
from django.contrib.auth.decorators import login_required


class LoginRequiredView(View):
    # 调用父类as_view方法
    @classmethod
    def as_view(cls, **initkwargs):
        view = super(LoginRequiredView,cls).as_view(**initkwargs)
        return login_required(view)

class LoginRequiredMixin(object):
    @classmethod
    def as_view(cls, **initkwargs):
        view = super(LoginRequiredMixin, cls).as_view(**initkwargs)
        return login_required(view)

# super调用的不一定是父类方法，是按__mro__调用顺序进行调用（可以理解为不光可以调用父类方法，还可以调用兄弟类方法，兄弟类执行顺序在本类之后）
