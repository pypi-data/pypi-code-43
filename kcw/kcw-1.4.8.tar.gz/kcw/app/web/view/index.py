def index(): #浏览器打开该地址：http://0.0.0.0:39001/index/index
    return returnjson({"desc":"您好，这是基与kcw开发的api框架，注意：您应该是在app/web/view/目录下开发接口，接下来祝您的开发愉快，","name":"/index/index"})
def test1(): #浏览器打开该地址：http://0.0.0.0:39001/index/test1
    return returnjson({"desc":"没错，您看到的就只有这点json字符串","name":"/index/test1"})
def html():
    return render_template("index/html.html",title="标题",desc="描述",content="这就是html模板")