from django.conf.urls import url
from api.views import course
from  api.views import shoppingcar


urlpatterns = [
    url(r'course/$',course.CoursesView.as_view({'get':'list','post':'create'})),
    url(r'course/(?P<pk>\d+)/$',course.CoursesView.as_view({'get':'retrieve','put':'update','delete':'destroy'})),
    # 购物车操作url
    url(r'shoppingcar/$',shoppingcar.ShoppingCarView.as_view({'get':'list','post':'create','delete':'destroy','put':'update'})),
]