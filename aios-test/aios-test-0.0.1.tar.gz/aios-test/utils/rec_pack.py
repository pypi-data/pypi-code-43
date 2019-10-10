import os
import cv2
import logging
import traceback
import mxnet as mx
import multiprocessing
from aios.utils.utils import *

class SegmentationPack(object):

    def __init__(self, mount_path=None):
        self.mount_path = mount_path if not mount_path else '/datakubeflow'

    def create_segmentation_txt(self, save_path, labels):
        '''从DLP导出的json文件中提取原图和切割图，分别存入txt中
        '''
        prefix, img_fmt = os.path.splitext(save_path)
        img_txt = prefix + '_img.txt'
        mask_txt = prefix + '_mask.txt'

        logging.info('start get segmentation text...')
        imgs = []
        masks = []

        for it in labels["data"]:

            img_path = self.mount_path + '/' + it["host"] + '\n'
            if not it.get('matte_url'):
                continue
            mask_path = self.mount_path + '/' + it["matte_url"] + '\n'
            imgs.append(img_path)
            masks.append(mask_path)

        with open(os.path.join(img_txt), "w") as f:
            f.writelines(imgs)

        with open(os.path.join(mask_txt), "w") as f:
            f.writelines(masks)

class MultiProcessRecPack(object):
  
    def __init__(self, mount_path=None, image_shape=None):
        self.mount_path = mount_path if not mount_path else '/datakubeflow'
        self.type = None
        self.image_shape = image_shape
        
    def image_encode(self, i, item, q_out,  pass_through=False):
        # 将lst中的文件读出来，获取label以及图片路径，读取图片数据与header形成元组(i, s, item )压入队列

        # fullpath = item["url"]
        fullpath = item["host"]
        fullpath = self.mount_path + '/' + fullpath
        quality, encoding = get_img_fmt_quality(fullpath)

        if pass_through:
            # 二进制读取模式，使用该模式就不会用下面的cv2.imread读取方式
            # 这种模式不能做resize,center_crop等变换操作，只能原图是什么就是什么
            label = self.get_label(self.type, item)
            if not label:
                q_out.put((i, None, item))
                logging.error('label is null')
                return

            header = mx.recordio.IRHeader(0, label, item['id'], 0)
            try:
                with open(fullpath, 'rb') as fin:
                    img = fin.read()

                img = self.resize_img(img)

                s = mx.recordio.pack(header, img)
                q_out.put((i, s, item))
            except Exception as e:
                traceback.print_exc()
                print('pack_img error:', item["url"], e)
                q_out.put((i, None, item))
            return
        else:
            try:
                img = cv2.imread(fullpath, 1)  # color=1是彩色读取
            except:
                traceback.print_exc()
                print('imread error trying to load file: %s ' % fullpath)
                q_out.put((i, None, item))
                return
            if img is None:
                print('imread read blank (None) image for file: %s' % fullpath)
                q_out.put((i, None, item))
                return

            try:
                # img是已经读取到内存的，不管图片本身的格式，只要设定好quality和编码方式
                # 如果不做变换，跟pass_through的处理结果是一样的
                h, w, c = img.shape
                label = get_label(self.type, item, w, h)
                if label is None:
                    q_out.put((i, None, item))
                    logging.error('label is null')
                    return
                
                img = self.resize_img(img)

                header = mx.recordio.IRHeader(0, label, item['id'], 0)
                s = mx.recordio.pack_img(header, img, quality=quality, img_fmt=encoding)
                q_out.put((i, s, item))
            except Exception as e:
                traceback.print_exc()
                print('pack_img error on file: %s' % fullpath, e)
                q_out.put((i, None, item))
                return

    def read_worker(self, q_in, q_out):
        while True:
            # 从q_in队列中取出数据处理完之后存到q_out
            deq = q_in.get()
            if deq is None:
                break
            i, item = deq
            self.image_encode(i, item, q_out)

    def write_worker(self, q_out, fname):
        """
        :param q_out: 从q_out中读取数据打包
        :param fname:  rec文件名的全路径
        :return:
        """
        logging.info('write worker start...')
        count = 0
        fname_rec = fname
        fname_idx = os.path.splitext(fname)[0] + '.idx'

        logging.info('{}, {}'.format(fname_idx, fname_rec))
        record = mx.recordio.MXIndexedRecordIO(fname_idx, fname_rec, 'w')
        buf = {}
        more = True
        while more:
            deq = q_out.get()
            if deq is not None:
                i, s, item = deq
                buf[i] = (i, s, item)
            else:
                more = False

            while count in buf:
                i, s, item, = buf[count]
                del buf[count]
                if s is not None:
                    record.write_idx(i, s)  # 第一个参数是索引即lst文件中的第一列，如果索引错了随机读取会出错，顺序读取不会出错

                count += 1

    def mxnet_multiprocess_handle(self, save_path, labels, process_num=multiprocessing.cpu_count() * 10):
        """
        使用多进程打包生成rec和idx, 参考im2rec.py, 多个进程读取image,写到rec文件只有一个进程
        lst的第一列是给图片编号，idx的第一列是对应同样的编号，idx的第二列对应的这个编号的图片的大小，rec是存储具体图片信息的文件
        """
        self.type = labels['label_type']
        image_list = labels["data"]
        process_num = 1 if process_num < 1 else process_num
        if len(image_list) < 100:
            process_num = 1

        # 初始化进程与队列
        logging.info('start pack to rec file with process num %s' % process_num)
        print('start pack to rec file with process num %s' % process_num)
        q_in = [multiprocessing.Queue(1024) for i in range(process_num)]
        q_out = multiprocessing.Queue(1024)
        read_process = [multiprocessing.Process(target=self.read_worker, args=(q_in[i], q_out)) \
                        for i in range(process_num)]
        for p in read_process:
            p.start()

        write_process = multiprocessing.Process(target=self.write_worker, args=(q_out, save_path))
        write_process.start()

        # 初始化队列，将图片均匀的分散到队列里面
        for i, item in enumerate(image_list):
            # item是lst文件中的每一行
            q_in[i % len(q_in)].put((i, item))

        for q in q_in:
            q.put(None)
        for p in read_process:
            p.join()

        q_out.put(None)
        write_process.join()

    def resize_img(self, img):
        # 图片压缩,在训练过程中应保持一致
        if self.image_shape:
            [height, width] = self.image_shape.split(',')
            resize = max(int(height), int(width))
            if img.shape[0] > img.shape[1]:
                newsize = (resize, img.shape[0] * resize // img.shape[1])
            else:
                newsize = (img.shape[1] * resize // img.shape[0], resize)
            img = cv2.resize(img, newsize)
        return img
