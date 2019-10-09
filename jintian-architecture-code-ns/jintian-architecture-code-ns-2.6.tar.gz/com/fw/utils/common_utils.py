from hashlib import md5
from random import Random
import inspect
import base64
from Crypto.Cipher import AES
from com.fw.base.base_exception import BaseException


class CommonUtils():
    @staticmethod
    def create_salt(length=4):
        '''
        生成盐值
        :return:
        '''
        salt = ''
        chars = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789'
        # 获取chars的最大下标
        len_chars = len(chars) - 1

        random = Random()
        for i in range(length):
            # 每次随机从chars中抽取一位,拼接成一个salt值
            salt += chars[random.randint(0, len_chars)]
        return salt

    @staticmethod
    def get_md5_pass_word(pwd, salt):
        '''
        生成md5加密密码
        :param pwd:
        :param salt:
        :return:
        '''
        md5_obj = md5()
        md5_obj.update((pwd + salt).encode("utf8"))
        return md5_obj.hexdigest()

    @staticmethod
    def isEmpty(str):
        if not str or str == "":
            return True
        else:
            return False

    @staticmethod
    def isNotEmpty(str):
        return not CommonUtils.isEmpty(str)

    @staticmethod
    def check_param(func):
        '''
        检验非空参数
        :param func:
        :return:
        '''

        def get_result(*args, **kwargs):
            data = inspect.signature(func).parameters
            data_list = [(["$check$null"] * 3) for i in range(len(data.keys()))]
            data_dict = {}
            i = 0
            for key, val in data.items():
                data_list[i][0] = key
                data_list[i][1] = val
                data_dict[key] = i
                i = i + 1

            args = list(args)
            for i, val in enumerate(args):
                data_list[i][2] = val

            for key, val in kwargs.items():
                if key in data_dict.keys():
                    data_list[data_dict[key]][2] = val

            for i in range(len(data.keys())):
                if data_list[i][0] == "self" or data_list[i][0] == "args" or data_list[i][0] == "kwargs":
                    continue
                if data_list[i][1]._default == inspect._empty and data_list[i][2] == "$check$null":
                    raise BaseException("缺少必要参数...")

            return func(*args, **kwargs)

        return get_result

    @staticmethod
    def _pkcs7padding(text, ):
        """
        明文使用PKCS7填充
        最终调用AES加密方法时，传入的是一个byte数组，要求是16的整数倍，因此需要对明文进行处理
        :param text: 待加密内容(明文)
        :return:
        """
        bs = AES.block_size  # 16
        length = len(text)
        bytes_length = len(bytes(text, encoding='utf-8'))
        # tips：utf-8编码时，英文占1个byte，而中文占3个byte
        padding_size = length if (bytes_length == length) else bytes_length
        padding = bs - padding_size % bs
        # tips：chr(padding)看与其它语言的约定，有的会使用'\0'
        padding_text = chr(padding) * padding
        return text + padding_text

    @staticmethod
    def _pkcs7unpadding(text):
        """
        处理使用PKCS7填充过的数据
        :param text: 解密后的字符串
        :return:
        """
        length = len(text)
        unpadding = ord(text[length - 1])
        return text[0:length - unpadding]

    @staticmethod
    def aes_encrypt(key, content):
        """
        AES加密
        key,iv使用同一个
        模式cbc
        填充pkcs7
        :param key: 密钥
        :param content: 加密内容
        :return:
        """
        key_bytes = bytes(key, encoding='utf-8')
        iv = key_bytes
        cipher = AES.new(key_bytes, AES.MODE_CBC, iv)
        # 处理明文
        content_padding = CommonUtils._pkcs7padding(content)
        # 加密
        encrypt_bytes = cipher.encrypt(bytes(content_padding, encoding='utf-8'))
        # 重新编码
        result = str(base64.b64encode(encrypt_bytes), encoding='utf-8')
        return result

    @staticmethod
    def aes_decrypt(key, content):
        """
        AES解密
         key,iv使用同一个
        模式cbc
        去填充pkcs7
        :param key:
        :param content:
        :return:
        """
        key_bytes = bytes(key, encoding='utf-8')
        iv = key_bytes
        cipher = AES.new(key_bytes, AES.MODE_CBC, iv)
        # base64解码
        encrypt_bytes = base64.b64decode(content)
        # 解密
        decrypt_bytes = cipher.decrypt(encrypt_bytes)
        # 重新编码
        result = str(decrypt_bytes, encoding='utf-8')
        # 去除填充内容
        result = CommonUtils._pkcs7unpadding(result)
        return result

    @staticmethod
    def get_file_size(file_stream):
        ''''
        获取文件大小
        '''
        file_stream.seek(0, 2)  # move the cursor to the end of the file
        size = file_stream.tell()

        try:
            bytes = float(size)
            kb = round(bytes / 1024, 2)
        except:
            print("传入的字节格式不对")
            return "Error"

        if kb >= 1024:
            M = round(bytes / (1024 * 1024), 2)
            if M >= 1024:
                G = round(bytes / (1024 * 1024 * 1024), 2)
                return "{}G".format(G)
            else:
                return "{}M".format(M)
        else:
            return "{}kb".format(kb)
