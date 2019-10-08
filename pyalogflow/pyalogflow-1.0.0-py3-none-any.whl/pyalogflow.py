import dialogflow_v2 as dialogflow
import os
from audyo.speaker import Speaker


class Pyalogflow(object):

    def __init__(self, session_id, microphone,
                 voice_type = "waveF2",
                 response_audio="dialogflow_response.wav",
                 project_id=None,
                 output_audio_encoding=dialogflow.enums.OutputAudioEncoding.OUTPUT_AUDIO_ENCODING_LINEAR_16,
                 audio_encoding=dialogflow.enums.AudioEncoding.AUDIO_ENCODING_LINEAR_16,
                 language_code='it-IT'):
        __VOICES = {"waveM1": {"name": "it-IT-Wavenet-C",
                              "ssml_gender": dialogflow.enums.SsmlVoiceGender.SSML_VOICE_GENDER_MALE},
                    "waveM2": {"name": "it-IT-Wavenet-D",
                              "ssml_gender": dialogflow.enums.SsmlVoiceGender.SSML_VOICE_GENDER_MALE},
                    "waveF1": {"name": "it-IT-Wavenet-A",
                              "ssml_gender": dialogflow.enums.SsmlVoiceGender.SSML_VOICE_GENDER_MALE},
                    "waveF2": {"name": "it-IT-Wavenet-B",
                              "ssml_gender": dialogflow.enums.SsmlVoiceGender.SSML_VOICE_GENDER_MALE},
                    "baseM": {"name": "it-IT-Standard-C",
                              "ssml_gender": dialogflow.enums.SsmlVoiceGender.SSML_VOICE_GENDER_MALE},
                    "baseF": {"name": "it-IT-Standard-A",
                              "ssml_gender": dialogflow.enums.SsmlVoiceGender.SSML_VOICE_GENDER_FEMALE}

                    }
        project_id = os.environ.get("GOOGLE_PROJECT_ID") if not project_id else project_id
        self.__session = dialogflow.SessionsClient().session_path(project=project_id, session=session_id)
        self.__microphone = microphone
        self.__request_audio = microphone.out_file
        self.__response_audio = response_audio

        self.__input_audio_config = dialogflow.types.InputAudioConfig(
            audio_encoding=audio_encoding, language_code=language_code,
            sample_rate_hertz=microphone.rate)

        speech_config = dialogflow.types.SynthesizeSpeechConfig(
            voice=__VOICES[voice_type])
        self.__output_audio_config = dialogflow.types.OutputAudioConfig(
            audio_encoding=output_audio_encoding, synthesize_speech_config=speech_config)

        self.__query_input = None
        self.__input_audio = None

    def __continuous_conversation(self):
        self.audio_request()
        return self.get_audio_response()

    def audio_request(self, file=None):
        if not file:
            file = self.__request_audio
            self.__microphone.record_to_file()

        with open(file, 'rb') as request_file:
            self.__input_audio = request_file.read()
        request_file.close()

        self.__query_input = dialogflow.types.QueryInput(audio_config=self.__input_audio_config)

        if self.__input_audio == b'':
            return None
        return self.__input_audio

    def get_audio_response(self, mute=False):
        if self.__input_audio and self.__query_input:
            response = dialogflow.SessionsClient().detect_intent(
                session=self.__session, query_input=self.__query_input,
                input_audio=self.__input_audio, output_audio_config=self.__output_audio_config)
            if response.output_audio == b'':
                return None
            with open(self.__response_audio, 'wb') as out:
                out.write(response.output_audio)
            if not mute:
                Speaker.play(self.__response_audio)

            # if continuous conversation -> response = recursive_function()
            return response
        else:
            return None

    def get_text_response(self):
        response = dialogflow.SessionsClient().detect_intent(
            session=self.__session, query_input=self.__query_input,
            input_audio=self.__input_audio)
        if response.output_audio == b'':
            return None
        with open(self.__response_audio, 'wb') as out:
            out.write(response.output_audio)
        # if not mute:
        Speaker.play(self.__response_audio)

        print("Text: \n"+response)
        return response


