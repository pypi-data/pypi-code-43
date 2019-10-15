# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division, print_function
from .app_auth_api import *
from .app_asr_base_api import *
import wave
from pyaudio import PyAudio, paInt16, paContinue

MODEL_ASR_POWER = "model_asr_power"
MODEL_ASR_NUMBER = "model_asr_number"


class ASRClient:
    def __init__(self, app_id, app_secret, host="wss://test.cloudv2.voiceaitech.com", call_back=None, access_token=""):
        self.socket_host = host
        if self.socket_host.endswith("/"):
            self.socket_host = self.socket_host + "api/app/asr/streaming"
        else:
            self.socket_host = self.socket_host + "/api/app/asr/streaming"

        url = ""
        if "wss://" in host:
            url = host.replace("wss://", "https://")
        elif "ws://" in host:
            url = host.replace("ws://", "http://")
        else:
            raise ASRException("host must prefix wss:// or ws://")

        self.auth = AppAuthAPI(app_id=app_id, base_url=url, access_token=access_token)
        ok, err, data = self.auth.app_auth_get(app_secret)
        if ok is False:
            raise ASRException(data)
        ok1, err, data1 = self.auth.app_auth_token_get()
        if ok1 is False:
            raise ASRException(data1)

        self.auth.app_auth_token_refresh()
        self.token = self.auth.get_access_token()
        self.app_id = app_id
        self.call_back = call_back

        self.pyaudio = None
        self.stream = None
        self.sampling_rate = 16000
        self.model_type = "model_asr_power"
        self.write_wav_file = ""
        self.wavefile = None
        self.asr_api = None

    def asr(self, sample_rate, model_type, file_name, delay=800):
        self.auth.app_auth_token_refresh()
        ws = ASRBaseClient(url=self.socket_host, app_id=self.app_id, token=self.token, sample_rate=sample_rate,
                           model_type=model_type, file_name=file_name, delay=delay)
        ws.daemon = True
        try:
            ws.connect()
            logging.debug("wait, please...may be long long.")
            while True:
                ok, result = ws.get_real_time_txt()
                if ok and result is not None:
                    if self.call_back is not None:
                        self.call_back(result)
                        # logging.debug("asr2:%s" % result)
        except ASRCloseException as e:
            # 获取最终结果
            logging.debug("asr err inner %r" % e)
            result = ws.get_final_txt()
            return result

        return ""

    def start_asr_stream(self, sample_rate, model_type, write_wav_file=""):
        if self.pyaudio is None:
            self.pyaudio = PyAudio()
        else:
            raise ASRException("asr stream already started")

        self.sampling_rate = sample_rate
        self.model_type = model_type
        self.write_wav_file = write_wav_file

        if self.write_wav_file != "":
            self.wavefile = wave.open(self.write_wav_file, 'wb')
            self.wavefile.setnchannels(1)
            self.wavefile.setsampwidth(2)
            self.wavefile.setframerate(self.sampling_rate)

        self.auth.app_auth_token_refresh()
        if self.asr_api is None:
            self.asr_api = ASRBaseClient(url=self.socket_host, app_id=self.app_id, token=self.token,
                                         sample_rate=sample_rate, model_type=model_type, func=self.call_back)
            self.asr_api.daemon = True
        try:
            self.asr_api.connect()
        except ASRCloseException as e:
            logging.debug("asr_stream err: %r" % e)

        self.stream = self.pyaudio.open(format=paInt16, channels=1, rate=self.sampling_rate, input=True,
                                        stream_callback=self._pyaudio_callback)
        self.stream.start_stream()

    def stop_asr_stream(self):
        if self.stream is not None:
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None

        if self.wavefile is not None:
            self.wavefile.close()

        if self.pyaudio is not None:
            self.pyaudio.terminate()
            self.pyaudio = None

        if self.asr_api is not None:
            self.asr_api.diy_send_binary_end()
            self.asr_api.close()
            self.asr_api = None

    def _pyaudio_callback(self, in_data, frame_count, time_info, status):
        if self.wavefile is not None:
            self.wavefile.writeframes(in_data)

        try:
            if self.asr_api is not None:
                self.asr_api.diy_send_binary(in_data)
        except ASRCloseException as e:
            logging.debug("_pyaudio_callback err: %r" % e)

        return (in_data, paContinue)
