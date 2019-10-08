from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QBrush, QPen
from PyQt5.QtCore import Qt

import math

class QBarPlot(QWidget):

    def __init__(self):
        super().__init__()

        self.horizontal_margin = 10
        self.vertical_margin = 10

        self.data = None
        self.data_index = None
        self.data_color = None
        self.title = None
        self.title_size = 32
        self.title_margin = 5

        self.hlines = None

        self.ymin = None
        self.ymax = None

        self.x_label_height = 50

        # Set window background color
        self.setAutoFillBackground(True)

        palette = self.palette()
        palette.setColor(self.backgroundRole(), Qt.white)

        self.setPalette(palette)


    def paintEvent(self, event):
        qp = QPainter(self)

        try:
            num_bar = len(self.data)
        except:
            num_bar = 0

        if self.data_index is not None and len(self.data_index) != len(self.data):
            raise ValueError("len(data_index) != len(data)")              # TODO

        size = self.size()
        widget_width = size.width()
        widget_height = size.height()

        if num_bar > 0:
            plot_area_width = max(0, widget_width - 2 * self.horizontal_margin)
            plot_area_height = max(0, widget_height - 2 * self.vertical_margin)

            # Set antialiasing ################################################

            # Set anti-aliasing  See https://wiki.python.org/moin/PyQt/Painting%20and%20clipping%20demonstration

            qp.setRenderHint(QPainter.Antialiasing)

            # Set Font ########################################################

            font = qp.font()
            font.setPointSize(self.title_size)
            qp.setFont(font)

            # Draw title ######################################################

            title_x_start = self.title_margin
            title_y_start = self.title_margin
            title_width = widget_width - 2 * self.title_margin
            title_height = self.title_size
            title_x_end = title_x_start + title_width
            title_y_end = title_y_start + title_height

            qp.drawText(title_x_start, title_y_start, title_width, title_height, Qt.AlignCenter, self.title)

            # Prepare coordinates transform ###################################

            filtered_data = [data_value for data_value in self.data if data_value is not None]
            self.top_ordinate_value = max(filtered_data) if self.ymax is None else self.ymax
            self.bottom_ordinate_value = min(filtered_data) if self.ymin is None else self.ymin

            plot_area_x_start = self.horizontal_margin
            plot_area_x_end = widget_width - self.horizontal_margin
            plot_area_width = plot_area_x_end - plot_area_x_start

            self.plot_area_y_start = title_y_end + self.title_margin + self.vertical_margin
            self.plot_area_y_end = widget_height - self.vertical_margin - self.x_label_height
            plot_area_height = self.plot_area_y_end - self.plot_area_y_start

            brush = QBrush(Qt.white, Qt.SolidPattern)
            qp.setBrush(brush)
            qp.drawRect(plot_area_x_start, self.plot_area_y_start, plot_area_width, plot_area_height)   # TODO

            # Set Pen and Brush ###############################################
            
            #see https://hci.isir.upmc.fr/wp-content/uploads/2018/03/PyQt-Dessin.pdf

            #pen = QPen(Qt.black, 3, Qt.SolidLine)
            pen = QPen()
            pen.setStyle(Qt.SolidLine)   # Qt.DashDotLine
            pen.setWidth(2)
            pen.setBrush(Qt.black)       # Qt.green
            pen.setCapStyle(Qt.RoundCap)
            pen.setJoinStyle(Qt.RoundJoin)
            qp.setPen(pen)
            
            white_brush = QBrush(Qt.white, Qt.SolidPattern)
            green_brush = QBrush(Qt.green, Qt.SolidPattern)
            yellow_brush = QBrush(Qt.yellow, Qt.SolidPattern)
            red_brush = QBrush(Qt.red, Qt.SolidPattern)

            # Draw horizontal lines ###########################################

            if self.hlines is not None:
                for hline_value in self.hlines:
                    hline_position = self.ordinateTransform(hline_value)

                    if hline_position is not None:
                        qp.drawLine(plot_area_x_start, hline_position, plot_area_x_end, hline_position)   # x_start, y_start, x_end, y_end

            # Draw bars #######################################################

            if self.data_color is None:
                self.data_color = [None for data_value in self.data]

            for data_index, (data_value, data_color) in enumerate(zip(self.data, self.data_color)):

                if data_value is not None:
                    if data_color == "green":
                        qp.setBrush(green_brush)
                    elif data_color == "yellow":
                        qp.setBrush(yellow_brush)
                    elif data_color == "red":
                        qp.setBrush(red_brush)
                    else:
                        qp.setBrush(white_brush)

                    x_length = math.floor(plot_area_width / num_bar)
                    x_start = self.horizontal_margin + data_index * x_length
                    
                    y_start = self.ordinateTransform(data_value)  # TODO: what if y_start is None ?
                    if y_start is None:
                        if data_value > self.bottom_ordinate_value:
                            y_start = self.plot_area_y_start
                        else:
                            y_start = self.plot_area_y_end

                    y_end = self.ordinateTransform(0)
                    if y_end is None:
                        y_end = self.plot_area_y_end

                    y_length = y_end - y_start

                    # Draw bar
                    qp.drawRect(x_start, y_start, x_length, y_length)


    def ordinateTransform(self, data_ordinate):
        # self.top_ordinate_value    -> self.plot_area_y_start
        # self.bottom_ordinate_value -> self.plot_area_y_end
        if self.bottom_ordinate_value <= data_ordinate <= self.top_ordinate_value:
            data_ordinate_ratio = (self.top_ordinate_value - data_ordinate) / (self.top_ordinate_value - self.bottom_ordinate_value)
            data_ordinate_position = self.plot_area_y_start + data_ordinate_ratio * (self.plot_area_y_end - self.plot_area_y_start)
            return math.floor(data_ordinate_position)
        else:
            return None
