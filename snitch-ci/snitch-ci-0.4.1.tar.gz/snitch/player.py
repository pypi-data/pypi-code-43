"""
Module providing tools to replay recorded  inputs sequences.
"""
from tempfile import gettempdir
import logging as log
import time

import pyautogui
import imutils
from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QMessageBox
from skimage.measure import compare_ssim
import cv2

from .model.data import screenshot
from .model.data.screenshot import ImageConverter
from .ui.diff import Diff


DEFAULT_DELAY = .2

class EventPlayer(QObject):
    """ Class handling the event replay """
    def __init__(self, event_list, delay=DEFAULT_DELAY, parent=None):
        """
        :param delay: The interval, in seconds, between two repalyed events. If -1, the
                        recording interval is used.
        """
        super().__init__(parent)

        self._event_list = event_list
        self._delay = delay
        self._playing = False

    def play(self, start_at=0, event_played_callback=None, key_event_catcher=None):
        """
        Executes sequentially all the events in the list
        :param start_at: The index of the event in the list to start playing from
        :param event_played_callback: A callback function, taking an event as parameter,
            and called after each event play
        :param key_event_catcher: A KeyEventCatcher object, on which the stop method
            will be called before executing the event, and restarted just after
        :return: the last event played
        """
        first_event = max(0, start_at)
        log.info('Starting playback from event %d/%d', first_event, self._event_list.size())
        last_event = None
        self._playing = True
        for event in self._event_list.events[first_event:]:
            if self._playing:
                if last_event is None:
                    delay = 0
                elif self._delay == -1:
                    delay = event.time - last_event.time
                else:
                    delay = self._delay

                time.sleep(delay)

                if key_event_catcher:
                    key_event_catcher.stop()
                event.execute()
                if key_event_catcher:
                    key_event_catcher.start()

                last_event = event
                if event_played_callback:
                    event_played_callback(last_event)
            else:
                break

    def stop(self):
        """ Stop the replay sequence """
        self._playing = False



class SnapshotPlayer(QObject):
    """ Class handling snapshot reenactment and comparison """

    def __init__(self, snap_list, parent=None):
        """
        :type snap_list: list of Screenshot objects
        """
        super().__init__(parent)

        self._snap_list = snap_list

        self._originals = []
        self._results = []
        self._results_with_diff = []
        self._diff_performed = False

        self._diff_win = None

    def play(self):
        """ Reperforms all the recorded snapshots """
        self._originals = [ImageConverter(s.as_image()) for s in self._snap_list.snaps]
        self._results.clear()
        self._results_with_diff.clear()

        for snap in self._snap_list.snaps:
            path = '{0}/capture-{1}.png'.format(gettempdir(), round(time.time()*1000))
            image = ImageConverter(pyautogui.screenshot(path, region=snap.region()))
            self._results.append(image)
            snap.result = screenshot.pixmap_to_base64(image.pixmap)

        self.diff()

    def diff(self):
        """
        Computes the differences between the reference image and the result one.
        :return: True if there's no difference between the images.
        """
        if not self._results:
            log.error("No results to compare. Try launching a replay sequence.")
            return False

        if len(self._results) != self._snap_list.size():
            log.error("Results snapshot count does not match testcase, aboritng diff.")
            return False

        self._results_with_diff.clear()
        self._diff_performed = True
        no_diff = True
        for orig, res in zip(self._originals, self._results):
            original = orig.opencv
            gray_original = cv2.cvtColor(original, cv2.COLOR_BGR2GRAY)

            result = res.opencv
            gray_result = cv2.cvtColor(result, cv2.COLOR_BGR2GRAY)

            # compute the Structural Similarity Index (SSIM) between the two
            # images, ensuring that the difference image is returned
            (score, diff) = compare_ssim(gray_original, gray_result, full=True)

            diff = (diff * 255).astype("uint8")
            log.info("Diff score = %f", score)

            # threshold the difference image, followed by finding contours to
            # obtain the regions of the two input images that differ
            thresh = cv2.threshold(diff, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
            cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            cnts = imutils.grab_contours(cnts)

            # loop over the contours
            for c in cnts:
                # compute the bounding box of the contour and then draw the
                # bounding box on both input images to represent where the two
                # images differ
                (x, y, w, h) = cv2.boundingRect(c)
                cv2.rectangle(result, (x, y), (x + w, y + h), (0, 0, 255), 2)

            if cnts:
                no_diff = False
                self._results_with_diff.append(ImageConverter(result))
            else:
                self._results_with_diff.append(None)

        return no_diff

    def show_diff(self, snap_id):
        """ Shows the window with images side by side. """
        if self._diff_performed:
            snaps = [s for s in zip(self._originals, self._results, self._results_with_diff)][snap_id]
            if not all(snaps): # at least one value is none
                if not any(snaps): # all values are none
                    QMessageBox.information(self.parent(), "Snitch", "Captures are identical")
                else:
                    log.error("Some of the snaps are missing")
            else: # no value is none
                self._diff_win = Diff(*[s.pixmap for s in snaps], None)
                self._diff_win.show()
