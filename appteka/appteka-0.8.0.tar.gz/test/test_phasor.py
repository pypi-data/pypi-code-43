import sys

from PyQt5 import QtWidgets
from PyQt5 import QtCore

import sys
import os
import time
from random import randint

sys.path.insert(0, os.path.abspath("."))

from appteka.pyqt import gui, testing
from appteka.pyqtgraph import phasor


class TestPhasor(testing.TestDialog):
    def test_just_visible(self):
        self.set_widget(phasor.PhasorDiagram())
        self.set_text("Widget is visible")
        text = "- Widget is visible\n"
        text += "- Widget seems to be OK"
        self.set_text(text)

    def test_radius_labels(self):
        d = phasor.PhasorDiagram()
        self.set_widget(d)
        text = "Widget seems to be OK"
        self.set_text(text)

    def test_range_is_two(self):
        d = phasor.PhasorDiagram()
        self.set_widget(d)
        d.set_range(2)
        text = "- Grid is OK\n"
        text += "- The max circle in grid has radius of 2"
        self.set_text(text)

    def test_change_range(self):
        d = phasor.PhasorDiagram()
        self.set_widget(d)
        d.set_range(2)
        d.set_range(4)
        text = "- Grid is OK\n"
        text += "- The max circle in grid has radius of 4"
        self.set_text(text)

    def test_add_phasor(self):
        d = phasor.PhasorDiagram()
        self.set_widget(d)
        d.set_range(100)
        d.add_phasor('ph-1', 80, 1)
        text = "- There is a phasor in first quadrant\n"
        text += "- The color of phasor is white"
        self.set_text(text)

    def test_update_phasor(self):
        d = phasor.PhasorDiagram()
        self.set_widget(d)
        d.set_range(100)
        d.add_phasor('ph-1', 80, 1)
        d.update_phasor('ph-1', 80, 2)
        text = "- There is a phasor in second quadrant\n"
        text += "- Phasor in single"
        self.set_text(text)

    def test_phasor_color(self):
        d = phasor.PhasorDiagram()
        self.set_widget(d)
        d.set_range(100)
        d.add_phasor('ph-1', 80, 1, (255, 0, 0))
        text = "There is a red phasor in first quadrant"
        self.set_text(text)

    def test_three_phasors(self):
        d = phasor.PhasorDiagram()
        self.set_widget(d)
        d.set_range(100)
        d.add_phasor('ph-1', 80, 0, (255, 0, 0))
        d.add_phasor('ph-2', 80, 2 * 3.1415 / 3, (0, 255, 0))
        d.add_phasor('ph-3', 80, -2 * 3.1415 / 3, (0, 0, 255))
        text = "- There are 3 phasors: red, green and blue\n"
        text += "- About 120 degrees between every two phasors"
        self.set_text(text)

    def test_three_phasors_rotated(self):
        d = phasor.PhasorDiagram()
        self.set_widget(d)
        d.set_range(100)
        d.add_phasor('ph-1', 80, 0, (255, 0, 0))
        d.add_phasor('ph-2', 80, 2 * 3.1415 / 3, (0, 255, 0))
        d.add_phasor('ph-3', 80, -2 * 3.1415 / 3, (0, 0, 255))
        d.update_phasor('ph-1', 80, 1)
        d.update_phasor('ph-2', 80, 1 + 2 * 3.1415 / 3)
        d.update_phasor('ph-3', 80, 1 - 2 * 3.1415 / 3)
        text = "- There are 3 phasors: red, green and blue\n"
        text += "- About 120 degrees between every two phasors\n"
        text += "- Red phasor has angle about 1 radian"
        self.set_text(text)

    def test_range_to_phasor(self):
        d = phasor.PhasorDiagram()
        self.set_widget(d)
        d.add_phasor('ph-1', color=(255, 255, 0))
        d.update_phasor('ph-1', 1, 1)
        d.update_phasor('ph-1', 100, 1)
        d.set_range(100)
        text = "Grid corresponds to phasor"
        self.set_text(text)

    def test_legend(self):
        d = phasor.PhasorDiagram()
        self.set_widget(d)
        d.add_phasor('ph-1', 80, 0, (255, 0, 0))
        d.add_phasor('ph-2', 80, 2 * 3.1415 / 3, (0, 255, 0))
        d.add_phasor('ph-3', 80, -2 * 3.1415 / 3, (0, 0, 255))
        d.show_legend()
        d.set_range(80)
        text = "Legend is correct"
        self.set_text(text)

    def test_three_phasors_animation(self):
        d = phasor.PhasorDiagram()
        self.set_widget(d)
        d.add_phasor('ph-1', color=(255, 0, 0))
        d.add_phasor('ph-2', color=(0, 255, 0))
        d.add_phasor('ph-3', color=(0, 0, 255))
        d.show_legend()

        self.timer = QtCore.QTimer(self)
        self.timer.setInterval(10)

        self.step = 0

        def rotate():
            a = 2 * 3.1415 / 3
            sh = self.step / 200
            ash = self.step / 10
            d.update_phasor('ph-1', ash + 10, sh)
            d.update_phasor('ph-2', 10, sh + a)
            d.update_phasor('ph-3', 10, sh - a)
            d.set_range(ash + 10)

            self.step += 1
            if self.step > 100:
                self.timer.stop()
                self.enable_buttons()

        self.timer.timeout.connect(rotate)
        self.timer.start()
        self.disable_buttons()

        text = "- Phasors smoothly rotating\n"
        text += "- Amplitude of red phasor grows"
        self.set_text(text)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    d = TestPhasor()
    d.run()
    sys.exit(app.exec())
