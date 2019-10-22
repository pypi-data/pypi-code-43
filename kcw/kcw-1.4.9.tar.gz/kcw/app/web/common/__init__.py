from kcw.packages.flask import request,render_template,session,g
#当前文件下定义的函数只能当前模块下可以使用
PATH_MOD=os.path.abspath('..') #当前模块目录
def returnjson(data=[],code=0,msg="成功",status=200):
    """在浏览器输出包装过的json

        参数 data 结果 默认[]

        参数 code body状态码 默认0

        参数 msg body状态描述 默认 成功

        参数 status http状态码 默认 200

        返回 json字符串结果集 
        """
    res={
        "code":code,
        "msg":msg,
        "time":times(),
        "data":data
    }
    return json_encode(res),status,{"Content-Type":"application/json; charset=utf-8"}
def template(template_name_or_list, **context):
    return render_template(template_name_or_list, **context)
def oauth(path):
    "权限验证方法,需要您自己完成逻辑,(这里简单使用session)"
    g.userinfo=session.get('user')
    if g.userinfo:
        data=True,g.userinfo
    else:
        data=False,returnjson({},-1,'签权验证失败',503)
    return data