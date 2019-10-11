import gzip
import os
import zipfile

def zipDir(dirpath, outFullName):
    '''
    压缩指定文件夹
    :param dirpath: 目标文件夹路径
    :param outFullName:  压缩文件保存路径+XXXX.zip
    :return: 无
    '''
    zip = zipfile.ZipFile(outFullName, 'w', zipfile.ZIP_DEFLATED)
    for path, dirnames, filenames in os.walk(dirpath):
        # 去掉目标和路径，只对目标文件夹下边的文件及文件夹进行压缩（包括父文件夹本身）
        this_path = os.path.abspath('.')
        fpath = path.replace(this_path, '')
        for filename in filenames:
            zip.write(os.path.join(path, filename), os.path.join(fpath, filename))
    zip.close()


def unzip(dst_dir, zip_src):
    r = zipfile.is_zipfile(zip_src)
    if r:
        fz = zipfile.ZipFile(zip_src)
        for file in fz.namelist():
            fz.extract(file, dst_dir)
    else:
        print('This is not zip')


def zip_no_dir(yadir, zipfilepath):
    filelists = os.listdir(yadir)
    if filelists == None or len(filelists) < 1:
        print(">>>>>>待压缩的文件目录：" + yadir + " 里面不存在文件,无需压缩. <<<<<<")
    else:
        z = zipfile.ZipFile(zipfilepath, 'w', zipfile.ZIP_DEFLATED)
        for fil in filelists:
            filefullpath = os.path.join(yadir, fil)
            # filefullpath是文件的全路径，fil是文件名，这样就不会带目录啦
            z.write(filefullpath, fil)


if __name__ == '__main__':
    zip_no_dir("train_word_bag", "train_word_bag.zip")
    # unzip("train_corpus", "train_corpus.zip")
    # unzip("train_word_bag", "train_word_bag.zip")
