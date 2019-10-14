import os
import pickle


class Hard(object):
    def __init__(self, foldername=None, dumper=pickle):
        if foldername is None:
            foldername = "hard"
        self.__dict__["foldername"] = os.path.abspath(
            foldername
        )
        self.__dict__["dumper"] = dumper

    def __getattr__(self, key):
        try:
            foldername = self.__dict__["foldername"]
            dumper = self.__dict__["dumper"]
            if key in self.__dict__:
                return self.__dict__[key]
            else:
                filename_ = os.path.join(foldername, key)
                if not os.path.exists(filename_):
                    return None
                with open(filename_, "rb") as dumpfile:
                    self.__dict__[key] = dumper.load(
                        dumpfile
                    )
                return self.__dict__[key]

        except Exception as e:
            raise e

    def __setattr__(self, key, value):
        try:
            foldername = self.__dict__["foldername"]
            dumper = self.__dict__["dumper"]
            if not os.path.exists(foldername):
                os.mkdir(foldername)
            self.__dict__[key] = value
            filename_ = os.path.join(foldername, key)
            with open(filename_, "wb") as dumpfile:
                dumper.dump(self.__dict__[key], dumpfile)

        except Exception as e:
            raise e


if __name__ == "__main__":
    print("It works!")
