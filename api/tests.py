from django.test import TestCase

# Create your tests here.
def list(self, request, *args, **kwargs):
    response = BaseResponse()
    try:
        shopping_car_course_list = []

        # pattern = "shopping_car_%s_*" % (USER_ID,)
        pattern = settings.LUFFY_SHOPPING_CAR % (USER_ID, '*',)

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
        response.code = 10005
        response.error = '获取购物车数据失败'

    return Response(response.dict)