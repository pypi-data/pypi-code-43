import ast
import copy
import subprocess
import pathlib
import re

import _ast
import astor
import astunparse
from django.apps import apps
from paraer import doc
from rest_framework.schemas import SchemaGenerator

API_VIEW_MAP = {}
ROOT_DIR = pathlib.Path(".")

FUNC_FACTORY_MAP = {
    "CharField": "factory.Sequence(lambda n: 'test_{}%s' % n)",
    "IntegerField": "factory.Sequence(lambda n: n)",
    "BigIntegerField": "factory.Sequence(lambda n: n)",
    "ForeignKey": "factory.SubFactory({})",
    "OneToOneField": "factory.SubFactory({})",
    "EmailField": "factory.sequence(lambda n: 'test_{}%s@hypers.com' % n)",
}

factoryImportMould = """
import factory
from django.utils.module_loading import import_string
"""

factoryMould = """


class {}({}):
    class Meta:
       model = {}
       abstract = {}
"""


testImportMould = """
from itertools import product
from rest_framework.test import APITestCase
from parameterized import parameterized


def login(self):
    self.user = None
    self.client.force_authenticate(user=self.user)
"""
testClassMould = """


class {}(APITestCase):
    def setUp(self) -> None:
        login(self)
        
"""
testFuncMould = """
    {testData}
    def {funcName}(self, {args}):
        api = "{api}"
        {request}
        statusCode = response.status_code
        self.assertGreaterEqual(statusCode, 200)
        self.assertLessEqual(statusCode, 300)
        
"""


class TestCaseAutomatic(object):
    def run(self):
        """启动入口"""
        nodesModule = Node().getAst(ROOT_DIR)
        self.handleModule(nodesModule)

    def handleModule(self, nodesModule):
        """nodesModule  的结构 [('/home/t1.py', _ast.Module), ('/home/t2.py', _ast.Module)]"""
        needHandleNode = {}
        for filePath, node in nodesModule:
            for node in node.body:
                if self.judgeViewClass(node):
                    needHandleNode.setdefault(filePath, []).append(node)
        if needHandleNode:
            for filePath, nodeList in needHandleNode.items():
                newFilePath = _getTestsPath(filePath)
                if not newFilePath.exists():
                    # 只处理没有创建过的文件
                    self.writeToFile(newFilePath, nodeList)

    def writeToFile(self, testFilePath, needHandleNode):
        """这个方法一次处理一个py文件,方法内部的实现是先打开文件, 然后写入头部内容,然后依次处理这个py文件包含的视图类,
        需要处理的东西有: 类名, 方法名, api,  测试数据参数化装饰器, 参数"""
        with open(testFilePath, "w") as f:
            f.write(testImportMould)
            for node in needHandleNode:
                # 每次循环 处理完一个视图类

                className = node.name
                f.write(testClassMould.format("Test" + className))

                # 开始处理视图类的方法
                funcs = self.getFunc(node)
                for func in funcs:

                    args = self.getFuncArgs(func)
                    request = self.getRequest(func)
                    api = self.getApi(className, func)

                    f.write(
                        testFuncMould.format(
                            testData=args["testData"],
                            request=request,
                            funcName=f"test_{func.name}",
                            args=args["args"],
                            api=api,
                        )
                    )
        subprocess.call(["black", testFilePath])

    def getApi(self, className, func):
        funcMap = {
            "list": "get",
            "retrieve": "get",
            "create": "post",
            "destory": "delete",
        }
        funcName = funcMap.get(func.name, func.name).upper()
        api = API_VIEW_MAP.get(className, {}).get(funcName, None)
        if func.name == "list":
            # list 方法 要去掉 {id}
            api = self.dropIdOfListMethod(api)
        return api

    def dropIdOfListMethod(self, api):
        if api.endswith("/"):
            reApi = re.match(r"(?P<pre>.*){id}", api)
        else:
            reApi = re.match(r"(?P<pre>.*)/{id}", api)
        if reApi is not None:
            api = reApi.group("pre")
        return api

    def getRequestParameter(self, func):
        parameter = ""
        args = func.args.args
        for arg in args:
            if (
                arg.arg != "request"
                and arg.arg != "self"
                and arg.arg != "id"
                and arg.arg != "pk"
            ):
                # request 这个参数不需要
                parameter += f"{arg.arg}={arg.arg}, "
        parameter = parameter.strip(" ").strip(",")
        return parameter

    def getRequest(self, func):
        parameter = self.getRequestParameter(func)
        if func.name in ["list", "get", "retrieve"]:
            request = f"response = self.client.get(api, data=dict({parameter}))"
        elif func.name in ["post", "create", "put", "patch"]:
            request = f"response = self.client.post(api, data=dict({parameter}), format='json')"
        elif func.name in ["delete", "destory"]:
            request = f"response = self.client.delete(api, data=dict({parameter}), format='json')"
        return request

    def getFuncArgs(self, func) -> dict:
        """获取请求的 参数"""
        result = ""
        testData = []
        args = func.args.args
        for arg in args:
            if arg.arg != "request" and arg.arg != "self":
                # request 这个参数不需要
                result += f"{arg.arg}=None, "
                if arg.arg == "name":
                    testData.append(("testName", ""))
        result = result.strip(" ").strip(",")
        if testData:
            testData = f"@parameterized.expand(product{tuple(testData)})"
        else:
            testData = "\n"
        return {"args": result, "testData": testData}

    def getFunc(self, node):
        func = []
        for i in node.body:
            if isinstance(i, _ast.FunctionDef) and i.name in [
                "list",
                "get",
                "retrieve",
                "post",
                "create",
                "put",
                "patch",
                "delete",
                "destory",
            ]:
                func.append(i)
        return func

    def judgeViewClass(self, node):
        if not isinstance(node, _ast.ClassDef):
            return False
        bases = node.bases
        if len(bases) != 1:
            return False
        base = bases[0]
        baseName = getattr(base, "id", None)
        if baseName is None:
            return False
        if "view" not in baseName.lower():
            return False
        return True


class FactoryAutomatic(object):
    """
    关于Base基类的逻辑, 先判断,如果是Base基类, 记录下字段和类型, 在处理其他类时,去判断是否是继承基类, 如果是,那么继承字段
    """

    def __init__(self):
        self.baseModel = {}
        self.subfactoryPath = {}
        self.factoryFiles = []
        self.fixDirName = "auto/factoryAuto"
        self.fixFileName = "factory"

    def run(self):
        nodesModule = Node().getAst(ROOT_DIR)
        self.handleModule(nodesModule)
        self.fixSubFactory()

    def fixSubFactory(self):
        """遍历一遍所有的节点,如果有没有导入的SubFactory,那么插入import 语句"""
        for factoryFile in self.factoryFiles:
            module = astor.parse_file(factoryFile)
            currentFactoryName = []
            needAddImport = []
            for node in module.body:
                if isinstance(node, _ast.ClassDef):
                    currentFactoryName.append(node.name)
                    for i in node.body:
                        try:
                            if i.value.func.attr == "SubFactory":
                                subClsName = i.value.args[0].id
                                if subClsName not in currentFactoryName:
                                    needAddImport.append(subClsName)
                        except Exception:
                            pass
            if needAddImport:
                for i in needAddImport:
                    newImportModule = (
                        str(self.subfactoryPath.get(i, None))
                        .strip(".py")
                        .replace("/", ".")
                    )
                    newImportNode = self.buildNode(newImportModule, name=i)
                    module.body.insert(0, newImportNode)
                with open(factoryFile, "w") as f:
                    f.write(astunparse.unparse(module))

    def buildNode(self, module, name):
        importFrom = ast.ImportFrom()
        alias = ast.alias()
        alias.name = name
        alias.asname = None
        importFrom.level = 0
        importFrom.module = module
        importFrom.names = [alias]
        return importFrom

    def handleModule(self, nodesModule):
        """nodesModule  的结构 [('/home/t1.py', _ast.Module), ('/home/t2.py', _ast.Module)]"""
        needHandleNode = {}
        for filePath, node in nodesModule:
            for node in node.body:
                if self.judgeModelClass(node):
                    self.assignModel(filePath, node)
                    if self.judgeBase(node):
                        self.baseModel.update({node.name: node})
                    needHandleNode.setdefault(filePath, []).append(node)
        if needHandleNode:
            for filePath, nodeList in needHandleNode.items():
                newFilePath = _getTestsPath(filePath)
                self.factoryFiles.append(newFilePath)
                if True:
                    # 只处理没有创建过的文件
                    self.writeToFile(newFilePath, nodeList)

    def assignModel(self, filePath, node):
        path = str(filePath.parent).replace("/", ".")
        modelPath = f"{path}.{node.name}"
        node.model = f"import_string('{modelPath}')"

    def judgeBase(self, node):
        body = node.body
        for childNode in body:
            if isinstance(childNode, _ast.ClassDef):
                metaBody = childNode.body
                for metaNode in metaBody:
                    try:
                        if metaNode.targets[0].id == "abstract":
                            node.abstract = True
                            return True
                    except Exception:
                        continue

    def judgeModelClass(self, node):
        if isinstance(node, _ast.ClassDef):
            if getattr(node, "name", None) == "User":
                return True
            bases = node.bases
            if not bases:
                return False
            base = bases[0]

            # 继承 models.Model
            if getattr(base, "attr", None) == "Model":
                return True
            if getattr(base, "id", None) == "Model":
                return True
            # 判断是否是继承的 基类
            if getattr(base, "id", None) in self.baseModel.keys():
                node.inherit = base.id
                return True

        return False

    def writeToFile(self, testFilePath, nodes):
        with open(testFilePath, "w") as f:
            f.write(factoryImportMould)
            for node in nodes:
                classStr = self.getClassStr(node)
                className = node.name + "Factory"
                # 记录所有的factory 和路径的对应关系,在收尾时给SubFactory添加正确的关联
                self.subfactoryPath.update({className: testFilePath})

                inheritModelName = self.getInheritModel(node)
                model = node.model
                abstract = getattr(node, "abstract", False)
                f.write(classStr.format(className, inheritModelName, model, abstract))
        subprocess.call(["black", testFilePath])

    def getInheritModel(self, node):
        inheritModelName = getattr(node, "inherit", None)
        if inheritModelName is None:
            inheritModelName = "factory.django.DjangoModelFactory"
        else:
            inheritModelName += "Factory"
        return inheritModelName

    def getClassStr(self, node):
        classStr = copy.deepcopy(factoryMould)
        for body in node.body:
            if isinstance(body, _ast.Assign):
                try:
                    key = body.targets[0].id
                    value = body.value.func.attr
                except:
                    continue
                funcStr = self.getFuncStr(value, body)
                if funcStr:
                    funcStr = f"    {key} = {funcStr}\n"
                    classStr += funcStr.format(key)
        return classStr

    def getFuncStr(self, value, body):
        """获取 字段的 等号 右边内容"""
        funcStr = FUNC_FACTORY_MAP.get(value, None)
        if value == "ForeignKey" or value == "OneToOneField":
            arg = body.value.args[0]
            if isinstance(arg, _ast.Name):
                funcStr = funcStr.format(arg.id + "Factory")
            elif isinstance(arg, _ast.Str):
                # 在model类里 Foreign 以 app.model 形式指定的情况
                foreignKeyName = re.match(
                    r"<class '.*\.(.*)'>", str(apps.get_model(arg.s))
                ).group(1)
                funcStr = funcStr.format(foreignKeyName + "Factory")

            else:
                funcStr = funcStr.format("手动指定Factory")
        return funcStr


class Node(object):
    def __init__(self):
        self.nodesModule = []

    def getAst(self, path: str = None) -> list:
        """ return: [('/home/user/dmp/manage.py', _ast.Module), ]"""
        path = pathlib.Path(path)
        for part in path.iterdir():
            if part.is_dir():
                self.getAst(part)
                # 如果是文件夹,递归处理
            elif part.is_file() and part.name.endswith("py"):
                # 如果是文件, 获取py文件的语法树
                nodes = astor.parse_file(part)
                self.nodesModule.append((part, nodes))
        return self.nodesModule


def _mkPackage(self, path: str) -> bool:
    """_mkPackage 在每个目录生成__init__.py文件
    
    :param path: 目标路径
    :type path: str
    :return: 是否生成成功
    :rtype: bool
    """
    while path.parent != ROOT_DIR:
        path = path.parent
        if str(path).endswith("views"):
            path = path.parent
        path.joinpath("__init__.py").touch()
    path.parent.mkdir(exist_ok=True, parents=True)
    return path


def _getTestsPath(self, path: pathlib.Path) -> pathlib.Path:
    """根据源代码路径获取tests目录下的路径
    
    :param path: 源代码路径
    :type path: pathlib.Path
    :return: 目标路径
    :rtype: pathlib.Path
    """
    path = pathlib.Path(str(path).replace("app", "tests").replace("apps", "tests"))
    path = _mkPackage(path)
    return path


def findApiAndView(func):
    def wrap(*args, **kwargs):
        viewName = args[0].view.__class__.__name__
        api = args[1]
        method = args[2]
        API_VIEW_MAP.setdefault(viewName, {}).update({method: api})
        func(*args, **kwargs)

    return wrap


def getApiViewMap():
    doc.SwaggerSchema.get_link = findApiAndView(doc.SwaggerSchema.get_link)
    SchemaGenerator().get_schema()


def main():
    getApiViewMap()
    TestCaseAutomatic().run()
    FactoryAutomatic().run()


if __name__ == "__main__":
    main()
