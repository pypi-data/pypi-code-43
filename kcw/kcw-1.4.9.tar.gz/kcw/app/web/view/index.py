def index(): #浏览器打开该地址：http://0.0.0.0:39001/index/index
    return returnjson({"desc":"您好，这是基与kcw开发的api框架，注意：您应该是在app/web/view/目录下开发接口，接下来祝您的开发愉快，","name":"/index/index"})
def login():
    "登录"
    userinfo={'username':'kcw'}
    session['user']=userinfo
    return returnjson()
def outlogin():
    "退出登录"
    session['user']=None
    return returnjson()
def html():
    return render_template("index/html.html",title="标题",desc="描述",content="这就是html模板")