from .extra_time import *
note = """
一切都是可配置的，
可以进行对 parse_time 方法 进行增删改差操作：

    1. 对数据库 quyu_time_func 各个地区的时间操作函数 进行配置
        更新：
            update(quyu, time_func, conp)
        删除：
            delete(quyu, conp)      
    
    2. 对 common.py 和 exec_func_f.py 函数地区解析时间的方法， 进行操作
        用法: 
            funcxxx = '''def extime_v2xxxxxx(ggstart_time,page):
                if ggstart_time is not None:
                    res = ggstart_time
                else:
                    res = extime(ggstart_time,page)
                return res'''
            delete_func(funcxxx)
            add_func(funcxxx)  
            
    3. 对本地 quyu_time_func.json 文件进行增加或删除操作。
        增加用法：
            add_quyu_time_func_json(quyu_name, time_func)
        删除：
            del_quyu_time_func_json(quyu_name, time_func)
            
    4. 将本地 quyu_time_func.json 文件同步到指定数据库中。
        用法：
            file_to_db(conp)
            
"""