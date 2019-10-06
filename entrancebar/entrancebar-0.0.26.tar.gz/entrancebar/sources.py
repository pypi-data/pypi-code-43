import importlib.util
import os.path
from pathlib import Path
import sys
from .modulext import Modulext
import time
from typing import Dict, Any
from .config import config
import inspect
import copy

printed = False
configuration = config()
 
class BaseSource:
    def pathRender(self, target):
        return target

    def __init__(self, target, namespace="$"):
        target = self.pathRender(target) # 加上alias...
        self.target = Path(target)
        self.namespace = namespace

    def finder(self):
        pass

    def render(self, spec):
        origin = spec.loader.load_module()
        
        R = Modulext({"default": origin}, {
            "filePath": spec.origin,
            "spec": spec,
            "name": spec.name,
            "time": time.time()
        })
        return R

class FromSitePackage(BaseSource):
    def finder(self):
        return importlib.util.find_spec(str(self.target))

class FromFileLocation(BaseSource):
    def pathRender(self, target):
        t = copy.copy(target)
        if 'alias' in configuration:
            l = list(configuration['alias'].keys())
            l.sort()
            l = l[::-1]
            for i in l:
                t.replace(i, configuration['alias'][i])
        return t

    def finder(self):
        if self.target.is_absolute():
            return importlib.util.spec_from_file_location(
                os.path.abspath(self.target),
                self.target.absolute()
            )
        else:
            # 1 是Import, 2 也是Import....
            try:
                print(str(Path(sys._getframe(3).f_code.co_filename).parent / self.target))
                if sys._getframe(13).f_code.co_filename == str(Path(sys._getframe(3).f_code.co_filename).parent / self.target):
                    # 这样就可以获取到上层的上层的上层了, importlib的bootstrap层有4个, wsl
                    # 2(v_const) + {1:1:t1} + 4(v_const) + {2:1:t2} + 4(v_const) + {3:1:t1} = 13
                    # 在这种情况下, t1是entry, 而t2则是target, 但在实际中则互为target和entry....
                    # 得想个法子...哦...
                    # entry....是对target的调用, 但是他们两个互相调用...
                    # 那么两个node互相提供对象, 阶层就平滑了.
                    # 
                    return type(f"path={sys._getframe(13).f_code.co_filename}", (object,), {
                        "name": f"path={sys._getframe(13).f_code.co_filename}",
                        "origin": sys._getframe(13).f_code.co_filename, # 即后面可以,

                        "submodule_search_locations": None,
                        "has_location": True,
                        "cached": False,

                        "__getattr__": classmethod(
                            lambda this, value: sys._getframe(13).f_globals[value] if value in sys._getframe(13).f_globals else getattr(this, value)
                        ),

                        "loader": type("entrancebar.GlobalsLoader", (object,), {
                            "_entrancebar_mixins": type("envinfo", (object,), {
                                "f_globals": sys._getframe(13).f_globals,
                                "f_fname": Path(sys._getframe(13).f_code.co_filename)
                            })(),

                            "contents": classmethod(
                                lambda this: iter([f"__main__.cwd.{sys._getframe(3).f_code.co_filename}"])
                            ), # contents: 迷一般的函数 通常返回一个iterable...

                            "create_module": classmethod(
                                lambda this, spec: None
                            ), # create_module: https://docs.python.org/zh-cn/3.7/reference/import.html#loaders

                            "exec_module": classmethod( # 通常你都得把importlib.util.find_spec得到的spec放importlib.util.module_from_spec搞到一个non-loaded的module
                                lambda this, module: module.__dict__.update(sys._getframe(3).f_globals) # 然后把那个module丢进exec_module
                            ), # duang, 那个module就被加载了, 当然这种方式在eb中没法用, 你得把module.__dict__给他update一下....

                            "get_code": classmethod(
                                lambda this, fullname: this._entrancebar_mixins.f_globals if fullname == this._entrancebar_mixins.f_fname else None
                            ),

                            "get_data": classmethod(
                                lambda this, path: this._entrancebar_mixins.f_globals.__doc__.encode("utf-8") if "__doc__" in this._entrancebar_mixins.f_globals else None
                            ),
                            # get_data 在我实际测试中返回了module的doc....并且是bytes

                            "get_filename": classmethod(
                                lambda this: this._entrancebar_mixins.f_fname
                            ),
                            
                            "get_resource_reader": classmethod(
                                lambda this: None
                            ), # 因为导入了一个实际存在的File,所以这玩意没用....个鬼, 是用在package里的,用来获取那个所谓"数据文件"的

                            "get_source": classmethod(
                                lambda this, fullname: Path(
                                    importlib.util.find_spec(fullname).loader.get_filename()
                                ).read_text("utf-8")
                            ),

                            "is_package": classmethod(
                                lambda this, fullname: False
                            ),

                            "is_resource": classmethod(
                                lambda this, fullname: False
                            ),

                            "load_module": classmethod(
                                lambda this: type(f"{this._entrancebar_mixins.f_globals['__name__']}", (object,), this._entrancebar_mixins.f_globals)()
                            ),

                            "name": property(
                                lambda this: this._entrancebar_mixins.f_globals['__name__']
                            ),

                            "open_resource": classmethod(
                                lambda this: None
                            ),

                            "path": property(
                                lambda this: this._entrancebar_mixins.f_fname
                            ),

                            "path_stats": lambda path: None,
                        })()
                    })()
                    # 还是不知道为什么eb会把两个相互调用的module各执行2次....
            except ValueError:
                pass
            
            return importlib.util.spec_from_file_location(
                f"path={self.target}",
                Path(sys._getframe(3).f_code.co_filename).parent / self.target
            )