import abc
import logging
import os
import re
import sys
import time
from contextlib import closing
from io import BytesIO

import boto3
# import pysnooper
import requests
from botocore.exceptions import BotoCoreError, ClientError
from pydub import AudioSegment

import news2play.common.config as config
from news2play.ssml import SSML

current_path = os.path.dirname(__file__)
logger = logging.getLogger(__name__)


class Text2Speech(abc.ABC):
    @abc.abstractmethod
    def save_audio(self, f_name, txt, audio_type):
        pass


class PolllyTextToSpeech(Text2Speech):
    def __init__(self):
        self.ssml = SSML()

    def save_audio(self, f_name, txt, audio_type):
        f_name = f'{f_name}.{audio_type}'

        ssml_txt = self.ssml.dump(txt)

        ssml_txt = f'''<speak>{ssml_txt}</speak>'''

        session = boto3.Session()

        polly = session.client("polly")

        try:
            logger.info(f'''ssml:\n{ssml_txt}''')
            response = polly.synthesize_speech(Text=ssml_txt, OutputFormat=audio_type, TextType='ssml',
                                               VoiceId=config.polly_voice)
        except (BotoCoreError, ClientError) as error:
            # the service return an error, exit gracefully
            print(error)
            sys.exit(-1)

        if "AudioStream" in response:
            # Notes: Closing the stream is important because the service throttles on the
            # number of parallel connections. Here we are using contextlib.closing to
            # ensure the close method of the stream object will be called automatically
            # at the end of the with statement's scope.
            with closing(response["AudioStream"]) as stream:
                try:
                    # Open a file for writing the output as a binary stream
                    file_path, file_name = os.path.split(f_name)
                    if not os.path.exists(file_path):
                        os.makedirs(file_path)
                    with open(f_name, 'wb') as file:
                        file.write(stream.read())
                    logger.info(f"Your audio of speech is saved in {f_name}.")
                except IOError as error:
                    # Could not write to file, exit gracefully
                    print(error)
                    sys.exit(-1)


class AzureTextToSpeech(Text2Speech):
    def __init__(self):
        self.cognitive_base_url = 'https://southeastasia.api.cognitive.microsoft.com'
        self.tts_base_url = 'https://southeastasia.tts.speech.microsoft.com'
        # self.style = 'cheerful'
        self.style = config.azure_voice_style
        self.voice = config.azure_voice
        self.access_token = None
        self.token_duration = None
        self.token_start = None
        self.subscription_key = None
        self.ssml = SSML()

    def key_setup(self):
        """
            If you prefer, you can hardcode your subscription key as a string and remove
            the provided conditional statement. However, we do recommend using environment
            variables to secure your subscription keys. The environment variable is
            set to SPEECH_SERVICE_KEY in our sample.
            For example:
            subscription_key = "Your-Key-Goes-Here"

            Endpoint: https://westus.api.cognitive.microsoft.com/sts/v1.0
            Key 1: cb42e8ea292e494c846e6d5b58289a06
            Key 2: 74fc753639094567a7733791ec9d8b02
            Key 3: 16a9c49e080d4bbbb168b572fc1579f3
            export SPEECH_SERVICE_KEY='cb42e8ea292e494c846e6d5b58289a06'
            :return:
            """
        self.subscription_key = '16a9c49e080d4bbbb168b572fc1579f3'

        if not self.subscription_key:
            if 'SPEECH_SERVICE_KEY' in os.environ:
                self.subscription_key = os.environ['SPEECH_SERVICE_KEY']
            else:
                print('Environment variable for your subscription key is not set.')
                exit()

    def get_token(self):
        """
        The TTS endpoint requires an access token. This method exchanges your
        subscription key for an access token that is valid for 10 minutes.
        :return:
        """
        fetch_token_url = self.cognitive_base_url + "/sts/v1.0/issueToken"
        headers = {
            'Ocp-Apim-Subscription-Key': self.subscription_key
        }
        response = requests.post(fetch_token_url, headers=headers)
        self.access_token = str(response.text)

    # @pysnooper.snoop()
    def tts(self, txt):
        """
        Convert text to speech
        :param txt: text need to convert to speech
        :return: bytes of audio of the speech
        """

        if self.token_start is None:
            self.get_token()
            self.token_start = time.time()

        self.token_duration = time.time() - self.token_start

        # todo: token will expire in 10 mins, if the tts process it too slow, the token will expire and azure will return 401
        if self.token_duration / 60 > 10:
            self.get_token()
            self.token_start = time.time()

        constructed_url = self.tts_base_url + '/cognitiveservices/v1'
        headers = {
            'Authorization': 'Bearer ' + self.access_token,
            'Content-Type': 'application/ssml+xml',
            'X-Microsoft-OutputFormat': 'riff-24khz-16bit-mono-pcm',
            'User-Agent': 'YOUR_RESOURCE_NAME'
        }

        # todo:
        # if not validate(txt):
        #     raise Exception('News contains html escape characters.')

        body = self.build_ssml(txt).encode('utf-8')

        logger.debug(f"SSML:\n\n{body}\n")

        response = requests.post(constructed_url, headers=headers, data=body)

        if response.status_code == 200:
            logger.info(f"Status code: {response.status_code}")
            logger.info("Your TTS is ready.")
            return response.content

        else:
            logger.error(f"Status code: {response.status_code}")
            logger.error("Something went wrong. Check your subscription key and headers.")
            return None

    def build_ssml(self, txt):
        ssml_body = self.ssml.dump(txt)

        if self.voice in ['en-US-GuyNeural', 'en-US-JessaNeural']:
            ssml_head = f'''<speak version='1.0' xmlns="https://www.w3.org/2001/10/synthesis" xmlns:mstts="http://www.w3.org/2001/mstts" xml:lang='en-US'>
            <voice name="{self.voice}">'''
            ssml_body = f'''<mstts:express-as type="{self.style}">''' + ssml_body + '''</mstts:express-as>'''
        else:
            ssml_head = f'''<speak version='1.0' xmlns="https://www.w3.org/2001/10/synthesis" xml:lang='en-US'>
                                    <voice  name="{self.voice}" type="{self.style}">'''

        ssml_tail = '''</voice></speak>'''

        return ssml_head + ssml_body + ssml_tail

    # @pysnooper.snoop()
    def save_audio(self, f_name, txt, audio_type='mp3'):
        """
        If tts process run successfully, the binary audio will be written
        to file in current working directory or other specify path.
        :param f_name: audio file name, or additional path ahead
        :param txt: text that will be convert to speech
        :param audio_type: the audio type
        :return:
        """
        if f_name is None or f_name.strip() == "":
            raise TypeError('Parameter file_name must not be None')

        if txt is None or txt.strip() == "":
            raise TypeError('Parameter text must not be None')

        self.__save_audio(f_name, txt, audio_type)

    def __save_audio(self, f_name, txt, audio_type):
        p = re.compile(r'\n\n', re.S)
        p_list = p.split(txt)

        audio = AudioSegment.empty()
        for paragraph in p_list:
            audio_bytes_stream = self.tts(paragraph)
            if audio_bytes_stream:
                audio += AudioSegment.from_file(BytesIO(audio_bytes_stream))

        f_name = f'{f_name}.{audio_type}'
        audio.export(f_name, format=audio_type)

        logger.info(f"Your audio of speech is saved in {f_name}.")
