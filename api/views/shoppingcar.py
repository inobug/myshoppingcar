import json
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.viewsets import ViewSetMixin
from rest_framework.response import Response
# 将json数据进行序列化放在respon.data中
from rest_framework.parsers import JSONParser,FormParser
from api import models
from api.serializers import course as api_serializers
from api.utils.response import BaseResponse
import redis
# 用户id默认为1
USER_ID=1
# 链接存放redis 的地址及端口
CONN=redis.Redis(host='132.232.38.108',port=6379)
class ShoppingCarView(ViewSetMixin,APIView):


    def list(self, request, *args, **kwargs):
        """
        显示购物车内的信息
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        response = BaseResponse()
        try:
            shopping_car_course_list = []
        # 生成此用户的所有课程字典名称
            pattern = settings.LUFFY_SHOPPING_CAR % (USER_ID, '*',)
            # 找到所有课程字典名称饼放在字典里
            user_key_list = CONN.keys(pattern)
            for key in user_key_list:
                temp = {
                    'id': CONN.hget(key, 'id').decode('utf-8'),
                    'name': CONN.hget(key, 'name').decode('utf-8'),
                    'img': CONN.hget(key, 'img').decode('utf-8'),
                    'default_price_id': CONN.hget(key, 'default_price_id').decode('utf-8'),
                    'price_policy_dict': json.loads(CONN.hget(key, 'price_policy_dict').decode('utf-8'))
                }
                shopping_car_course_list.append(temp)
                response.data = shopping_car_course_list
        except Exception as e:
            response.code = 10001
            response.error = '获取购物车数据失败'
        return Response(response.dict)
    # 用户将课程加入购物车
    def create(self, request, *args, **kwargs):
        """
        用户将课程加入购物车
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        # 接收后端发送的数据
        response=BaseResponse()
        ret = json.loads(request.body.decode('utf8'))
        # 课程id
        id = ret['1']['course_id']
        # 价格策略id
        price_id = ret['1']['price_id']
        # 先找到此课程
        verify_course = models.Course.objects.filter(id=id).first()
        # 如果存在
        if not verify_course:
            # 不存在课程返回数据
            response.code=10001
            response.error='课程不存在'
            return Response(response.dict)
        # 找价格策略
        ser_obj = api_serializers.CourseModelSerializer(verify_course)
        # 如果存在
        if price_id not in ser_obj.data.get('pricepolicy'):
            # 价格策略失败返回数据
            response.code=10001
            response.error= '价格策略有问题！'
            return Response(response.dict)
        # 写入购物车
        # 给redis起键名/以shoppingcar_用户id_课程id为键名
        key = settings.LUFFY_SHOPPING_CAR % (USER_ID,id,)
        CONN.hmset(key, {'id': id,
                         'name': verify_course.name,
                         'img':verify_course.course_img,
                         'default_price_id':price_id,
                         'price_policy_dict':json.dumps(ser_obj.data.get('pricepolicy'))})
        # 成功返回数据
        response.data = '加入购物车成功！'
        return Response(response.dict)

    def destroy(self, request, *args, **kwargs):
        """
        删除购物车中的某个课程
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        response = BaseResponse()
        try:
            # 获取请求的课程id
            courseid = request.GET.get('courseid')
            # 从redis中获取此条信息
            key = settings.LUFFY_SHOPPING_CAR % (USER_ID, courseid,)
            CONN.delete(key)
            response.data = '删除成功'
        except Exception as e:
            response.code = 10001
            response.error = '删除失败'
        return Response(response.dict)
    def update(self,request,*args,**kwargs):
        """
        修改用户选中的价格策略
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        """
        1. 获取课程ID、要修改的价格策略ID
        2. 校验合法性（去redis中）
        """
        response = BaseResponse()
        try:
            # 1.从后端去的发送过来的数据
            # 课程id
            course_id = request.data.get('course_id')
            # 价格策略id
            policy_id = str(request.data.get('price_id'))
            # 2.取得价格策略在redis中的键名，进行数据判断
            key = settings.LUFFY_SHOPPING_CAR % (USER_ID, course_id,)
            #2.1判断课程是否存在
            if not CONN.exists(key):
                response.code = 10001
                response.error = '课程不存在'
                return Response(response.dict)
            # 2.2课程存在.判断价格策略是否存在
            price_policy_dict = json.loads(CONN.hget(key, 'price_policy_dict').decode('utf-8'))
            # 价格策略不存在
            if policy_id not in price_policy_dict:
                response.code = 10001
                response.error = '价格策略不存在'
                return Response(response.dict)
            # 2.3价格策略存在，进行价格策略修改
            CONN.hset(key,'default_price_id',policy_id)
            response.data = '修改成功'
        except Exception as e:
            response.code = 10001
            response.error = '修改失败'

        return Response(response.dict)

