import sys
import logging
logger = logging.getLogger(__name__)


def get_active_window():
    if sys.platform.startswith('linux'):
        try:
            import easilyb.os_ops.linux.xprop as _xprop
            import easilyb.os_ops.linux.ps as _ps
            window = dict()
            wid = _xprop.get_active_window_id()
            window['pid'] = _xprop.get_window_pid(wid)
            window['title'] = _xprop.get_window_title(wid)
            window['cmd'] = _ps.get_process_cmd(window['pid'])
            return window
        except:
            logger.error('Error getting active window for Linux platform', exc_info=True)
            raise Exception('Error getting active window for Linux platform')
    else:
        logger.error('platform %s is not supported', sys.platform)
        raise Exception('platform %s is not supported' % sys.platform)


def get_mouse_location():
    if sys.platform.startswith('linux'):
        import easilyb.os_ops.linux.xdotool as _xdotool
        try:
            ml = _xdotool.get_mouse_location()
            return int(ml['X']), int(ml['Y'])
        except:
            logger.error('Error getting mouse location for Linux platform', exc_info=True)
            raise Exception('Error getting mouse location for Linux platform')
    else:
        logger.error('platform %s is not supported', sys.platform)
        raise Exception('platform %s is not supported' % sys.platform)