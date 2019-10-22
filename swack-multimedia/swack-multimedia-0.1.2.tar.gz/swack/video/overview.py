import os

import numpy as np
from cv2 import cv2

"""
cv2 的像素点按(b,g,r)的方式
方案1：关闭shrink，提供一组缩略图分辨率元组。可能与原视频不匹配导致失真。
方案2：开启shrink，可以保持缩略图为原宽高比。
"""


class VideoOverview:
    """
    制作视频概览图。
    """
    version = "1.1.3"
    _margin_top = 200  # 顶部（200~300，需要刻视频信息）
    _margin_bottom = 30  # 底部（10~100）
    _margin_in = 10  # 内部（10~20）
    _margin_side = 25  # 左右两侧（20~50）
    thumb_dpi_list = [(480, 270), (384, 216)]  # 默认提供16:9的几种缩略图。可能与原视频不匹配导致失真。
    img_base_bgr = (127, 127, 127)  # 底图颜色
    capture = None
    thumbs_list = []

    def __init__(
            self,
            video: str,
            output: str = None,
            w: int = 4,
            h: int = 8,
            thumb_dpi: tuple = None,
            shrink: float = None,
            start_second: int or float = None,
            end_second: int or float = None,
            show_rank: bool = False,
            show_time: bool = True,
            save_thumbs: bool = False,
            save_result: bool = True,
            *args,
            **kwargs
            ):
        self.video = video
        self.output = output if output else self.video + ".overview.png"
        self.thumb_name = self.video + ".thumb_%02d_%02d.png"
        self.w_layout = w
        self.h_layout = h
        self.w_thumb, self.h_thumb = thumb_dpi if thumb_dpi else self.thumb_dpi_list[0]
        self.shrink = self.__check_shrink(shrink)
        self.start_second = start_second
        self.end_second = end_second
        self.show_rank = show_rank  # 缩略图是否显示编号
        self.show_time = show_time  # 缩略图是否显示时刻
        self.save_thumbs = save_thumbs
        self.save_result = save_result

    @staticmethod
    def __check_shrink(shrink):
        # 方案2：缩略图的分辨率按原视频等比缩小
        if isinstance(shrink, float):
            if 0.1 <= shrink <= 0.5:
                return shrink
        return None

    def _get_video_attr(self):
        # cv2 读取、计算
        print("\n>>>获取视频信息：")
        self.v_width = int(self.capture.get(3))  # 宽度
        self.v_height = int(self.capture.get(4))  # 高度
        self.v_fps = self.capture.get(5)  # 帧速率
        self.v_frame_count = int(self.capture.get(7))  # 视频文件的总帧数
        self.vs_resolution = str(self.v_width) + " x " + str(self.v_height)
        self.v_duration = self.v_frame_count / self.v_fps
        self.vs_duration = self.__seconds_to_hhmmss(int(self.v_duration))
        # os读取、计算
        self.vs_basename = os.path.basename(self.video)
        self.vs_size = self.__get_file_size(self.video)

        # 方案2：把视频缩略图大小按原视频大小缩小
        if self.shrink:
            self.w_thumb = int(self.shrink * self.v_width)
            self.h_thumb = int(self.shrink * self.v_height)

    @staticmethod
    def __get_file_size(video):
        stat = os.stat(video)
        size = stat.st_size
        if size > 1 * 1024 * 1024 * 1024:  # GB
            str_size = "%.2f GB" % (size / 1024 / 1024 / 1024)
        elif size > 1 * 1024 * 1024:  # MB
            str_size = "%.2f MB" % (size / 1024 / 1024)
        else:
            str_size = "%d Bytes" % size
        return str_size

    @staticmethod
    def __seconds_to_hhmmss(seconds):
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)
        return "%02d:%02d:%02d" % (h, m, s)

    def _calc_image_base(self):
        # 计算底图base的宽高，制作底图
        print("\n>>>生成底图：")
        w_base = self.w_thumb * self.w_layout + self._margin_in * (self.w_layout - 1) + self._margin_side * 2
        h_base = self._margin_top + self.h_thumb * self.h_layout + self._margin_in * (self.h_layout - 1) + self._margin_bottom
        self.img_base = np.zeros((h_base, w_base, 3), dtype=np.uint8)
        self.img_base[:, :, 0:3] = self.img_base_bgr
        print("像素宽 : %d" % w_base)
        print("像素高 : %d" % h_base)

    def __check_time(self):
        # 检查起始时间
        if isinstance(self.start_second, int) or isinstance(self.start_second, float):
            if 0 <= self.start_second <= self.v_duration:
                pass
            else:
                self.start_second = 0
        else:
            self.start_second = 0

        if isinstance(self.end_second, int) or isinstance(self.end_second, float):
            if 0 <= self.end_second <= self.v_duration:
                pass
            else:
                self.end_second = 0
        else:
            self.end_second = 0

        if self.start_second > self.end_second and self.end_second:
            self.start_second, self.end_second = self.end_second, self.start_second

    def _calc_thumbnails(self):
        # 计算、分割、截取缩略图的信息

        self.__check_time()

        print("\n>>>计算缩略图信息：")
        self.thumbnails = self.w_layout * self.h_layout
        count_head = 0
        count_tail = 0
        head_frames = 0
        if self.start_second:
            count_head = 1
            head_frames = self.start_second * self.v_fps  # 头部抛弃的帧数
        tail_frames = 0
        if self.end_second:
            count_tail = 1
            tail_frames = (self.v_duration - self.end_second) * self.v_fps  # 尾部抛弃的帧数
        sample = (self.v_frame_count - head_frames - tail_frames) / (self.thumbnails + 1 - count_head - count_tail)

        for num in range(self.thumbnails):
            h_array = int(num / self.w_layout)
            w_array = num % self.w_layout
            # 以下按像素在（行，列）的关系，对应像素xy为  x是列，y是行
            h_pos = h_array * self.h_thumb + h_array * self._margin_in + self._margin_top
            w_pos = w_array * self.w_thumb + w_array * self._margin_in + self._margin_side
            name_pos = self.thumb_name % (h_array + 1, w_array + 1)
            cur_frame = int(head_frames + sample * (num + 1 - count_head))
            cur_second = int(cur_frame / self.v_fps)
            cur_second_str = self.__seconds_to_hhmmss(cur_second)
            t = ((num + 1), h_pos, w_pos, name_pos, cur_frame, cur_second_str)
            print(t)
            # 自然顺序号，左上角坐标h，左上角坐标w，名字，当前帧数，当前秒数
            self.thumbs_list.append(t)

    def _split_thumbnails(self):
        # 分割缩略图，并刻编号、刻时间、保存缩略图
        print("\n>>>缩略图合并到底图：")
        for thumb in self.thumbs_list:
            num, h, w, name, frame, sec = thumb
            self.capture.set(cv2.CAP_PROP_POS_FRAMES, frame)
            get, img = self.capture.read()
            if get:
                img_tmp = cv2.resize(img, (self.w_thumb, self.h_thumb), cv2.INTER_LINEAR)
                if self.show_time:  # 写入时刻？
                    cv2.putText(img_tmp, sec, (self.w_thumb - 150, 35), cv2.FONT_HERSHEY_DUPLEX, 0.9, (0, 0, 255), 1)
                if self.show_rank:  # 写入编号？
                    cv2.putText(img_tmp, str(num), (10, 45), cv2.FONT_HERSHEY_DUPLEX, 1.2, (255, 0, 127), 2)
                if self.save_thumbs:  # 保存缩略图？
                    cv2.imwrite(name, img_tmp)
                print("当前进度：%d/%d" % (num, self.thumbnails))
                self.img_base[h:h + self.h_thumb,
                w:w + self.w_thumb, :] = img_tmp

    def _make_header_attr(self):
        print("\n>>>创建头部信息：")
        str_1 = "File Name  :  " + self.vs_basename
        str_2 = "File Size  :  " + self.vs_size
        str_3 = "Resolution :  " + self.vs_resolution
        str_4 = "Duration   :  " + self.vs_duration
        # 头部刻字与字形、字号、坐标位置、线宽，布局w、缩略图分辨率,等多个参数相关
        # 以下参数在w>=3，缩略图分辨率>=384*216时效果较好
        cv2.putText(self.img_base, str_1, (30, 40), cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 255, 255), 1)
        cv2.putText(self.img_base, str_2, (30, 80), cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 255, 255), 1)
        cv2.putText(self.img_base, str_3, (30, 120), cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 255, 255), 1)
        cv2.putText(self.img_base, str_4, (30, 160), cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 255, 255), 1)

    def _save_result(self):
        start = 0
        end = self.v_duration
        if self.start_second:
            start = self.start_second
        if self.end_second:
            end = self.end_second
        if self.save_result:
            print("\n>>>最终截取的时间范围：（%.1f，%.1f）" % (start, end))
            print("\n>>>最终结果存档至：%s" % self.output)
            cv2.imwrite(self.output, self.img_base)
            return
        else:
            print("\n>>>用户设置为最终结果不存档！")

    def run(self):
        self.capture = cv2.VideoCapture(self.video)
        if not self.capture.isOpened():
            print("\n>>>无法打开指定文件！")
            return 1
        self._get_video_attr()
        self._calc_image_base()
        self._calc_thumbnails()
        self._split_thumbnails()
        self._make_header_attr()
        self._save_result()
        print("\n>>>全部结束。")
        return 0
