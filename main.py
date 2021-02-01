# -*- encoding: utf-8 -*-
"""
茅台秒杀-京东-天猫-苏宁

登录判断
    登录成功 return 信息
    不成功 登录

选择操作类型
    预约
    秒杀
"""
import sys
from seckill_jd import JdSeckill


if __name__ == '__main__':
    a = """
    功能列表：                                                                                
     1.预约商品
     2.秒杀抢购商品
        """
    print(a)

    jd_seckill = JdSeckill()
    choice_function = input('请选择:')
    if choice_function == '1':
        jd_seckill.reserve()
    elif choice_function == '2':
        jd_seckill.seckill_by_proc_pool()
    else:
        print('没有此功能')
        sys.exit(1)

