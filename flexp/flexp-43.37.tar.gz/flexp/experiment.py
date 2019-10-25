from pyglet.canvas.xlib import NoSuchDisplayException
try:
    # psychopy can't be imported on travis
    from psychopy import visual  # Raises NoSuchDisplayException on travis
    from psychopy import event

    from .display import dppWindow
except NoSuchDisplayException:
    from unittest import mock
    import logging
    logging.error(
        'Could not import psychopy')
    event = mock.MagicMock()
    visual = mock.MagicMock()
    dppWindow = mock.MagicMock()

from psychopy.sound.backend_pygame import SoundPygame as Sound


class BaseExperiment(object):

    def __init__(self, develop=True, **kwargs):
        """
        Arguments:
            develop:
                run in development mode. Development mode has two effects
                    (i) a plain psychopy.visual.Window is used
                    (ii) by default, winType='pygame' to allow testing your
                        display on crappy graphics cards that don't support
                        setting gamma tables.
                If you pick "non-development mode" (i.e. develop=False), then
                the experiment will be based on a flexp.display.dppWindow that
                automatically makes use of the connected Display++
        """
        if develop:
            kwargs.setdefault('winType', 'pygame')  # independent of nvidia gc
            self.win = visual.Window(**kwargs)
        else:
            self.win = dppWindow(**kwargs)
        self.fixation = visual.Circle(self.win, size=1, units='pix')
        self.txt = visual.TextStim(self.win)
        self.beep = Sound(200, secs=0.2)

    def do_a_trial(self, *args, **kwargs):
        raise NotImplementedError(
            'If you want to run a trial, you should implement how it looks.\n'
            'You can do that by implementing a "do_a_trial" method.')

    def feedback(self, iscorrect, rt=None):
        if not iscorrect:
            self.beep.play()

    def draw_and_flip(self, *objects):
        """Draw all objects passed to the method and flip the window"""
        for obj in objects:
            obj.draw()
        self.win.flip()

    def message(self, msg):
        """Display a message on the screen.

        Note that the message will be shown in the experiment's txt object
        """
        self.txt.text = msg
        self.draw_and_flip(self.txt)
        event.waitKeys()
