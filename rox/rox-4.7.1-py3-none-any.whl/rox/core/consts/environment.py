import os


class classproperty(object):
    def __init__(self, f):
        self.f = f

    def __get__(self, obj, owner):
        return self.f(owner)


class Environment:
    ROXY_INTERNAL_PATH = 'device/request_configuration'

    @classproperty
    def CDN_PATH(self):
        result = 'https://conf.rollout.io'
        rollout_mode = os.getenv('ROLLOUT_MODE', '')
        if rollout_mode == 'QA':
            result = 'https://qa-conf.rollout.io'
        elif rollout_mode == 'LOCAL':
            result = 'https://development-conf.rollout.io'
        return result

    @classproperty
    def API_PATH(self):
        result = 'https://x-api.rollout.io/device/get_configuration'
        rollout_mode = os.getenv('ROLLOUT_MODE', '')
        if rollout_mode == 'QA':
            result = 'https://qax.rollout.io/device/get_configuration'
        elif rollout_mode == 'LOCAL':
            result = 'http://127.0.0.1:8557/device/get_configuration'
        return result

    @classproperty
    def CDN_STATE_PATH(self):
        result = 'https://statestore.rollout.io'
        rollout_mode = os.getenv('ROLLOUT_MODE', '')
        if rollout_mode == 'QA':
            result = 'https://qa-statestore.rollout.io'
        elif rollout_mode == 'LOCAL':
            result = 'https://development-statestore.rollout.io'
        return result

    @classproperty
    def API_STATE_PATH(self):
        result = 'https://x-api.rollout.io/device/update_state_store'
        rollout_mode = os.getenv('ROLLOUT_MODE', '')
        if rollout_mode == 'QA':
            result = 'https://qax.rollout.io/device/update_state_store'
        elif rollout_mode == 'LOCAL':
            result = 'http://127.0.0.1:8557/device/update_state_store'
        return result

    @classproperty
    def ANALYTICS_PATH(self):
        result = 'https://analytic.rollout.io'
        rollout_mode = os.getenv('ROLLOUT_MODE', '')
        if rollout_mode == 'QA':
            result = 'https://qaanalytic.rollout.io'
        elif rollout_mode == 'LOCAL':
            result = 'http://127.0.0.1:8787'
        return result

    @classproperty
    def NOTIFICATIONS_PATH(self):
        result = 'https://push.rollout.io/sse'
        rollout_mode = os.getenv('ROLLOUT_MODE', '')
        if rollout_mode == 'QA':
            result = 'https://qax-push.rollout.io/sse'
        elif rollout_mode == 'LOCAL':
            result = 'http://127.0.0.1:8887/sse'

        return result
