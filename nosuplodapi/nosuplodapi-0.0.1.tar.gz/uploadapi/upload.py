# encoding=utf8
import nos
import os
import uuid
import time
import hashlib


class UploadClient(object):
    def __init__(self, access_key, secret_key, bucket, end_point, access_point=None):
        self.access_key = access_key
        self.secret_key = secret_key
        self.bucket = bucket
        self.end_point = end_point
        self.access_point = access_point if access_point else end_point
        self.client = nos.Client(self.access_key, self.secret_key, end_point=self.end_point)

    @staticmethod
    def get_key(filemode):
        return time.strftime('%Y%m%d%H%M%S', time.localtime(time.time())) + "_" + str(uuid.uuid4()) + filemode

    @staticmethod
    def get_md5(filename):
        md5 = hashlib.md5()
        f = open(filename, 'rb')
        while True:
            b = f.read(8096)
            if not b:
                break
            md5.update(b)
        f.close()
        return md5.hexdigest()

    # 上传文件入口
    def upload(self, path=None):
        if os.path.exists(path):
            size = os.path.getsize(path)
            if size > 100 * 1024 * 1024:
                # 分片上传
                return self.upload_piece(path, size)
            else:
                return self.upload_once(path, size)
        return None

    # 一次性上传文件
    def upload_once(self, path, size):
        try:
            index = path.rfind(".")
            mode = path[index:] if index >= 0 else ""
            file_key = self.get_key(mode)
            md5 = self.get_md5(path)
            self.client.put_object(self.bucket, key=file_key, body=open(path, "rb"))
            return {
                "url": "https://%s.%s/" % (self.bucket, self.access_point) + file_key,
                "fileByteSize": size,
                "fileName": os.path.basename(path),
                "md5": md5
            }
        except Exception as e:
            print e, e.message
        return None

    # 分段上传文件
    def upload_piece(self, path, size):
        try:
            index = path.rfind(".")
            mode = path[index:] if index >= 0 else ""
            file_key = self.get_key(mode)
            result = self.client.create_multipart_upload(self.bucket, file_key)
            upload_id = result["response"].find("UploadId").text
            index = 0
            slice_size = 100 * 1024 * 1024
            with open(path, "rb") as fp:
                while True:
                    print "分片上传中，请等候..."
                    index += 1
                    part = fp.read(slice_size)
                    if not part:
                        break
                    self.client.upload_part(self.bucket, file_key, index, upload_id, part)
            rParts = self.client.list_parts(self.bucket, file_key, upload_id)
            Parts = rParts["response"]
            partETags = []
            for k in Parts.findall("Part"):
                partETags.append({"part_num": k.find("PartNumber").text, "etag": k.find("ETag").text})
            self.client.complete_multipart_upload(self.bucket, file_key, upload_id, partETags)
            return {
                "url": "https://%s.%s/" % (self.bucket, self.access_point) + file_key,
                "fileByteSize": size,
                "fileName": os.path.basename(path),
                "md5": self.get_md5(path)
            }
        except Exception, e:
            print e, e.message
        return None
