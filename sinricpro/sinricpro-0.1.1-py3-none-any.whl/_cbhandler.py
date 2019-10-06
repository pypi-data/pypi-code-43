from sinric._powerController import PowerController
from sinric._brightnessController import BrightnessController
from sinric._jsoncommands import JSON_COMMANDS
from sinric._powerLevelController import PowerLevel
from sinric._colorController import ColorController
from sinric._colorTemperature import ColorTemperatureController
from sinric._thermostatController import ThermostateMode
from sinric._rangeValueController import RangeValueController
from sinric._temperatureController import TemperatureController
from sinric._tvcontorller import TvController
from sinric._speakerController import SpeakerController
from json import dumps, load, dump
from time import time
from uuid import uuid4
from base64 import b64encode, b64decode
import hmac as sinricHmac
from hashlib import sha256
from ._dataTracker import DataTracker
from ._lockController import LockStateController


# TODO fix target temperature Duration

# noinspection PyBroadException
class CallBackHandler(PowerLevel, PowerController, BrightnessController, ColorController, ColorTemperatureController,
                      ThermostateMode, RangeValueController, TemperatureController, TvController, SpeakerController,
                      LockStateController, DataTracker):
    def __init__(self, callbacks, trace_bool, logger, enable_track=False, secretKey=""):
        self.myHmac = None
        self.secretKey = secretKey
        self.data_tracker = DataTracker(enable_track)
        PowerLevel.__init__(self, 0)
        self.enable_track = enable_track
        BrightnessController.__init__(self, 0)
        PowerController.__init__(self, 0)
        RangeValueController.__init__(self, 0)
        ColorController.__init__(self, 0)
        ThermostateMode.__init__(self, 0)
        TemperatureController.__init__(self, 0)
        TvController.__init__(self, 0)
        LockStateController.__init__(self)
        SpeakerController.__init__(self, 0)
        ColorTemperatureController.__init__(self, 0, [2200, 2700, 4000, 5500, 7000])
        self.callbacks = callbacks
        self.logger = logger
        self.trace_response = trace_bool

    def dumpData(self, key, val):
        f = open('localdata.json', 'w')
        data = load(f)
        dump(data.update({key: val}), f)
        f.close()

    async def handleCallBacks(self, dataArr, connection, udp_client):

        jsn = dataArr[0]

        Trace = dataArr[1]

        def jsnHandle(action, resp, dataDict) -> dict:
            header = {
                "payloadVersion": 2,
                "signatureVersion": 1
            }
            payload = {
                "action": action,
                "clientId": jsn.get("payload").get("clientId", "alexa-skill"),
                "createdAt": int(time()),
                "deviceId": jsn.get("payload").get("deviceId", ""),
                "message": "OK",
                "replyToken": jsn.get("payload", "").get("replyToken", str(uuid4())),
                "success": resp,
                "type": "response",
                "value": dataDict
            }

            replyHmac = sinricHmac.new(self.secretKey.encode('utf-8'),
                                       dumps(payload, separators=(',', ':'), sort_keys=True).encode('utf-8'), sha256)

            encodedHmac = b64encode(replyHmac.digest())

            signature = {
                "HMAC": encodedHmac.decode('utf-8')
            }

            return {"header": header, "payload": payload, "signature": signature}

        def verfiySignature(payload, hmac) -> bool:
            self.myHmac = sinricHmac.new(self.secretKey.encode('utf-8'),
                                         dumps(payload, separators=(',', ':'), sort_keys=True).encode('utf-8'), sha256)
            return b64encode(self.myHmac.digest()).decode('utf-8') == hmac

        if jsn.get('payload').get('action') == JSON_COMMANDS.get('SETPOWERSTATE'):
            try:
                assert (verfiySignature(jsn.get('payload'), jsn.get("signature").get("HMAC")))
                resp, state = await self.powerState(jsn, self.callbacks['powerState'])
                response = jsnHandle("setPowerState", resp, {"state": state})
                if resp:
                    if self.trace_response:
                        self.logger.info(f"Response : {dumps(response)}")
                    if Trace == 'socket_response':
                        await connection.send(dumps(response))
                    elif Trace == 'udp_response':
                        udp_client.sendResponse(dumps(response).encode('ascii'), dataArr[2])
            except Exception as e:
                self.logger.exception(e)

        elif jsn.get('payload').get('action') == JSON_COMMANDS['SETPOWERLEVEL']:
            try:
                assert (verfiySignature(jsn.get('payload'), jsn.get("signature").get("HMAC")))
                resp, value = await self.setPowerLevel(jsn, self.callbacks['setPowerLevel'])

                response = jsnHandle("setPowerLevel", resp, {
                    "powerLevel": value
                })
                if self.enable_track:
                    self.data_tracker.writeData('powerLevel', value)
                if resp:
                    if self.trace_response:
                        self.logger.info(f"Response : {dumps(response)}")
                    if Trace == 'socket_response':
                        await connection.send(dumps(response))
                    elif Trace == 'udp_response':
                        udp_client.sendResponse(dumps(response).encode('ascii'), dataArr[2])
            except Exception as e:
                self.logger.exception(str(e))

        elif jsn.get('payload').get('action') == JSON_COMMANDS['ADJUSTPOWERLEVEL']:
            try:
                assert (verfiySignature(jsn.get('payload'), jsn.get("signature").get("HMAC")))
                resp, value = await self.adjustPowerLevel(jsn,
                                                          self.callbacks['adjustPowerLevel'])
                response = jsnHandle(action="adjustPowerLevel", resp=resp, dataDict={"powerLevel": value})
                if self.enable_track:
                    self.data_tracker.writeData('powerLevel', value)
                if resp:
                    if self.trace_response:
                        self.logger.info(f"Response : {dumps(response)}")
                    if Trace == 'socket_response':
                        await connection.send(dumps(response))
                    elif Trace == 'udp_response':
                        udp_client.sendResponse(dumps(response).encode('ascii'), dataArr[2])
            except Exception as e:
                self.logger.exception(e)

        elif jsn.get('payload').get('action') == JSON_COMMANDS['SETBRIGHTNESS']:
            try:
                assert (verfiySignature(jsn.get('payload'), jsn.get("signature").get("HMAC")))
                resp, value = await self.setBrightness(jsn, self.callbacks['setBrightness'])
                response = jsnHandle(action="setBrightness", resp=resp, dataDict={"brightness": value})
                if self.enable_track:
                    self.data_tracker.writeData('brightness', value)
                if resp:
                    if self.trace_response:
                        self.logger.info(f"Response : {dumps(response)}")
                    if Trace == 'socket_response':
                        await connection.send(dumps(response))
                    elif Trace == 'udp_response':
                        udp_client.sendResponse(dumps(response).encode('ascii'), dataArr[2])
            except Exception as e:
                self.logger.exception(e)

        elif jsn.get('payload').get('action') == JSON_COMMANDS['ADJUSTBRIGHTNESS']:
            try:
                assert (verfiySignature(jsn.get('payload'), jsn.get("signature").get("HMAC")))
                resp, value = await self.adjustBrightness(jsn, self.callbacks['adjustBrightness'])
                response = jsnHandle(action="adjustBrightness", resp=resp, dataDict={
                    "brightness": value
                })
                if self.enable_track:
                    self.data_tracker.writeData('brightness', value)
                if resp:
                    if self.trace_response:
                        self.logger.info(f"Response : {dumps(response)}")
                    if Trace == 'socket_response':
                        await connection.send(dumps(response))
                    elif Trace == 'udp_response':
                        udp_client.sendResponse(dumps(response).encode('ascii'), dataArr[2])
            except Exception as e:
                self.logger.exception(e)

        elif jsn.get('payload').get('action') == JSON_COMMANDS['SETCOLOR']:
            try:
                assert (verfiySignature(jsn.get('payload'), jsn.get("signature").get("HMAC")))
                resp = await self.setColor(jsn, self.callbacks['setColor'])
                response = jsnHandle(action="setColor", resp=resp, dataDict={
                    "color": {
                        "r": jsn.get("payload").get("value").get("color").get("r"),
                        "g": jsn.get("payload").get("value").get("color").get("g"),
                        "b": jsn.get("payload").get("value").get("color").get("b")
                    }
                })
                if resp:
                    if self.trace_response:
                        self.logger.info(f"Response : {dumps(response)}")
                    if Trace == 'socket_response':
                        await connection.send(dumps(response))
                    elif Trace == 'udp_response':
                        udp_client.sendResponse(dumps(response).encode('ascii'), dataArr[2])
            except Exception as e:
                self.logger.exception(e)

        elif jsn.get('payload').get('action') == JSON_COMMANDS['SETCOLORTEMPERATURE']:
            try:
                assert (verfiySignature(jsn.get('payload'), jsn.get("signature").get("HMAC")))
                resp = await self.setColorTemperature(jsn, self.callbacks['setColorTemperature'])
                response = jsnHandle(action="setColorTemperature", resp=resp, dataDict={
                    "colorTemperature": jsn.get("payload").get("value").get("colorTemperature")
                })
                if self.enable_track:
                    self.data_tracker.writeData('colorTemperature',
                                                jsn[JSON_COMMANDS['VALUE']][JSON_COMMANDS['COLORTEMPERATURE']])
                if resp:
                    if self.trace_response:
                        self.logger.info(f"Response : {dumps(response)}")
                    if Trace == 'socket_response':
                        await connection.send(dumps(response))
                    elif Trace == 'udp_response':
                        udp_client.sendResponse(dumps(response).encode('ascii'), dataArr[2])
            except Exception as e:
                self.logger.exception(e)

        elif jsn.get('payload').get('action') == JSON_COMMANDS['INCREASECOLORTEMPERATURE']:
            try:
                assert (verfiySignature(jsn.get('payload'), jsn.get("signature").get("HMAC")))
                resp, value = await self.increaseColorTemperature(jsn, self.callbacks['increaseColorTemperature'])
                response = jsnHandle(action="increaseColorTemperature", resp=resp, dataDict={
                    "colorTemperature": value
                })
                if self.enable_track:
                    self.data_tracker.writeData('colorTemperature', value)
                if resp:
                    if self.trace_response:
                        self.logger.info(f"Response : {dumps(response)}")
                    if Trace == 'socket_response':
                        await connection.send(dumps(response))
                    elif Trace == 'udp_response':
                        udp_client.sendResponse(dumps(response).encode('ascii'), dataArr[2])
            except Exception as e:
                self.logger.exception(e)

        elif jsn.get('payload').get('action') == JSON_COMMANDS['DECREASECOLORTEMPERATURE']:
            try:
                assert (verfiySignature(jsn.get('payload'), jsn.get("signature").get("HMAC")))
                resp, value = await self.decreaseColorTemperature(jsn, self.callbacks['decreaseColorTemperature'])
                response = jsnHandle(action="decreaseColorTemperature", resp=resp, dataDict={
                    "colorTemperature": value
                })
                if self.enable_track:
                    self.data_tracker.writeData('colorTemperature', value)
                if resp:
                    if self.trace_response:
                        self.logger.info(f"Response : {dumps(response)}")
                    if Trace == 'socket_response':
                        await connection.send(dumps(response))
                    elif Trace == 'udp_response':
                        udp_client.sendResponse(dumps(response).encode('ascii'), dataArr[2])
            except Exception as e:
                self.logger.exception(e)

        elif jsn.get('payload').get('action') == JSON_COMMANDS['SETTHERMOSTATMODE']:
            try:
                assert (verfiySignature(jsn.get('payload'), jsn.get("signature").get("HMAC")))
                resp, value = await self.setThermostateMode(jsn, self.callbacks['setThermostatMode'])
                response = jsnHandle(action="setThermostatMode", resp=resp, dataDict={
                    "thermostatMode": value
                })
                # Value can be "HEAT", "COOL" or "AUTO"
                if resp:
                    if self.trace_response:
                        self.logger.info(f"Response : {dumps(response)}")
                    if Trace == 'socket_response':
                        await connection.send(dumps(response))
                    elif Trace == 'udp_response':
                        udp_client.sendResponse(dumps(response).encode('ascii'), dataArr[2])
            except Exception as e:
                self.logger.exception(e)

        elif jsn.get(JSON_COMMANDS.get('ACTION')) == JSON_COMMANDS.get('SETRANGEVALUE'):
            try:
                assert (verfiySignature(jsn.get('payload'), jsn.get("signature").get("HMAC")))
                resp, value = await self.setRangeValue(jsn, self.callbacks.get('setRangeValue'))
                response = jsnHandle(action="setRangeValue", resp=resp, dataDict={
                    "rangeValue": value
                })

                if self.enable_track:
                    self.data_tracker.writeData('rangeValue', value)
                if resp:
                    if self.trace_response:
                        self.logger.info(f"Response : {dumps(response)}")
                    if Trace == 'socket_response':
                        await connection.send(dumps(response))
                    elif Trace == 'udp_response':
                        udp_client.sendResponse(dumps(response).encode('ascii'), dataArr[2])
            except Exception as e:
                self.logger.exception('Error Occurred')



        elif jsn.get(JSON_COMMANDS.get('ACTION')) == JSON_COMMANDS.get('ADJUSTRANGEVALUE'):
            try:
                assert (verfiySignature(jsn.get('payload'), jsn.get("signature").get("HMAC")))
                resp, value = await self.setRangeValue(jsn, self.callbacks.get('adjustRangeValue'))
                response = jsnHandle(action="adjustRangeValue", resp=resp, dataDict={
                    "rangeValue": value
                })
                if self.enable_track:
                    self.data_tracker.writeData('rangeValue', value)
                if resp:
                    if self.trace_response:
                        self.logger.info(f"Response : {dumps(response)}")
                    if Trace == 'socket_response':
                        await connection.send(dumps(response))
                    elif Trace == 'udp_response':
                        udp_client.sendResponse(dumps(response).encode('ascii'), dataArr[2])
            except Exception as e:
                self.logger.exception('Error Occurred')

        elif jsn.get(JSON_COMMANDS.get('ACTION')) == JSON_COMMANDS.get('TARGETTEMPERATURE'):
            try:
                assert (verfiySignature(jsn.get('payload'), jsn.get("signature").get("HMAC")))
                resp, value = await  self.targetTemperature(jsn, self.callbacks.get('targetTemperature'))
                response = jsnHandle(action="targetTemperature", resp=resp, dataDict={
                            "duration": ""
                        })
                #@ TODO target temperature
                if self.enable_track:
                    self.data_tracker.writeData('temperature', value)
                if resp:
                    if self.trace_response:
                        self.logger.info(f"Response : {dumps(response)}")
                    if Trace == 'socket_response':
                        await connection.send(dumps(response))
                    elif Trace == 'udp_response':
                        udp_client.sendResponse(dumps(response).encode('ascii'), dataArr[2])
            except Exception as e:
                self.logger.exception('Error Occurred')

        elif jsn.get(JSON_COMMANDS.get('ACTION')) == JSON_COMMANDS.get('ADJUSTTEMPERATURE'):
            try:
                assert (verfiySignature(jsn.get('payload'), jsn.get("signature").get("HMAC")))
                resp, value = await self.targetTemperature(jsn, self.callbacks.get('adjustTemperature'))
                response = jsnHandle(action="adjustTemperature", resp=resp, dataDict={
                     "temperature": value
                })

                if self.enable_track:
                    self.data_tracker.writeData('temperature', value)
                if resp:
                    if self.trace_response:
                        self.logger.info(f"Response : {dumps(response)}")
                    if Trace == 'socket_response':
                        await connection.send(dumps(response))
                    elif Trace == 'udp_response':
                        udp_client.sendResponse(dumps(response).encode('ascii'), dataArr[2])
            except Exception as e:
                self.logger.exception('Error Occurred')


        elif jsn.get(JSON_COMMANDS.get('ACTION')) == 'setVolume':
            try:
                assert (verfiySignature(jsn.get('payload'), jsn.get("signature").get("HMAC")))

                resp, value = await self.setVolume(jsn, self.callbacks.get('setVolume'))
                response = jsnHandle(action="setVolume", resp=resp, dataDict={
                     "volume": value
                })

                if self.enable_track:
                    self.data_tracker.writeData('volume', value)
                if resp:
                    if self.trace_response:
                        self.logger.info(f"Response : {dumps(response)}")
                    if Trace == 'socket_response':
                        await connection.send(dumps(response))
                    elif Trace == 'udp_response':
                        udp_client.sendResponse(dumps(response).encode('ascii'), dataArr[2])
            except Exception as e:
                self.logger.exception('Error Occurred')



        elif jsn.get(JSON_COMMANDS.get('ACTION')) == 'adjustVolume':
            try:
                assert (verfiySignature(jsn.get('payload'), jsn.get("signature").get("HMAC")))

                resp, value = await self.adjustVolume(jsn, self.callbacks.get('adjustVolume'))
                response = jsnHandle(action="setVolume", resp=resp, dataDict={
                    "volume": value
                })

                if self.enable_track:
                    self.data_tracker.writeData('volume', value)

                if resp:
                    if self.trace_response:
                        self.logger.info(f"Response : {dumps(response)}")
                    if Trace == 'socket_response':
                        await connection.send(dumps(response))
                    elif Trace == 'udp_response':
                        udp_client.sendResponse(dumps(response).encode('ascii'), dataArr[2])
            except Exception as e:
                self.logger.exception('Error Occurred')



        elif jsn.get(JSON_COMMANDS.get('ACTION')) == 'mediaControl':
            try:
                assert (verfiySignature(jsn.get('payload'), jsn.get("signature").get("HMAC")))
                resp, value = await self.mediaControl(jsn, self.callbacks.get('mediaControl'))
                response = jsnHandle(action="mediaControl", resp=resp, dataDict={
                    "control": value
                })

                if resp:
                    if self.trace_response:
                        self.logger.info(f"Response : {dumps(response)}")
                    if Trace == 'socket_response':
                        await connection.send(dumps(response))
                    elif Trace == 'udp_response':
                        udp_client.sendResponse(dumps(response).encode('ascii'), dataArr[2])
            except Exception as e:
                self.logger.exception('Error Occurred')

        elif jsn.get(JSON_COMMANDS.get('ACTION')) == 'selectInput':
            try:
                assert (verfiySignature(jsn.get('payload'), jsn.get("signature").get("HMAC")))
                resp, value = await self.selectInput(jsn, self.callbacks.get('selectInput'))
                response = jsnHandle(action="selectInput", resp=resp, dataDict={
                    "input": value
                })

                if resp:
                    if self.trace_response:
                        self.logger.info(f"Response : {dumps(response)}")
                    if Trace == 'socket_response':
                        await connection.send(dumps(response))
                    elif Trace == 'udp_response':
                        udp_client.sendResponse(dumps(response).encode('ascii'), dataArr[2])
            except Exception as e:
                self.logger.exception('Error Occurred')


        elif jsn.get(JSON_COMMANDS.get('ACTION')) == 'changeChannel':
            try:
                assert (verfiySignature(jsn.get('payload'), jsn.get("signature").get("HMAC")))

                resp, value = await self.changeChannel(jsn, self.callbacks.get('changeChannel'))
                response = jsnHandle(action="changeChannel", resp=resp, dataDict={
                    "channel": {
                        "name": value
                    }
                })


                if resp:
                    if self.trace_response:
                        self.logger.info(f"Response : {dumps(response)}")
                    if Trace == 'socket_response':
                        await connection.send(dumps(response))
                    elif Trace == 'udp_response':
                        udp_client.sendResponse(dumps(response).encode('ascii'), dataArr[2])
            except Exception as e:
                self.logger.exception('Error Occurred')


        elif jsn.get(JSON_COMMANDS.get('ACTION')) == 'skipChannels':
            try:
                assert (verfiySignature(jsn.get('payload'), jsn.get("signature").get("HMAC")))
                resp, value = await self.skipChannels(jsn, self.callbacks.get('skipChannels'))
                response = jsnHandle(action="skipChannels", resp=resp, dataDict={
                    "channel": {
                        "name": value
                    }
                })

                if resp:
                    if self.trace_response:
                        self.logger.info(f"Response : {dumps(response)}")
                    if Trace == 'socket_response':
                        await connection.send(dumps(response))
                    elif Trace == 'udp_response':
                        udp_client.sendResponse(dumps(response).encode('ascii'), dataArr[2])
            except Exception as e:
                self.logger.exception('Error Occurred')



        elif jsn.get(JSON_COMMANDS.get('ACTION')) == 'setMute':
            try:
                assert (verfiySignature(jsn.get('payload'), jsn.get("signature").get("HMAC")))
                resp, value = await self.setMute(jsn, self.callbacks.get('setMute'))
                response = jsnHandle(action="setMute", resp=resp, dataDict={
                    "mute": value
                })

                if resp:
                    if self.trace_response:
                        self.logger.info(f"Response : {dumps(response)}")
                    if Trace == 'socket_response':
                        await connection.send(dumps(response))
                    elif Trace == 'udp_response':
                        udp_client.sendResponse(dumps(response).encode('ascii'), dataArr[2])
            except Exception as e:
                self.logger.exception('Error Occurred')

        elif jsn.get(JSON_COMMANDS.get('ACTION')) == 'setBands':
            try:
                assert (verfiySignature(jsn.get('payload'), jsn.get("signature").get("HMAC")))
                resp, value = await self.setBands(jsn, self.callbacks.get('setBands'))
                response = jsnHandle(action="setBands", resp=resp, dataDict={
                    "bands": [
                            {
                                "name": value.get('name'),
                                "level": value.get('level')
                            }
                        ]
                })

                if self.enable_track:
                    self.data_tracker.writeData('band', {"name": value.get('name'),
                                                         "level": value.get('level')})
                if resp:
                    if self.trace_response:
                        self.logger.info(f"Response : {dumps(response)}")
                    if Trace == 'socket_response':
                        await connection.send(dumps(response))
                    elif Trace == 'udp_response':
                        udp_client.sendResponse(dumps(response).encode('ascii'), dataArr[2])
            except Exception as e:
                self.logger.exception('Error Occurred')

        elif jsn.get(JSON_COMMANDS.get('ACTION')) == 'adjustBands':
            try:
                assert (verfiySignature(jsn.get('payload'), jsn.get("signature").get("HMAC")))
                resp, value = await self.adjustBands(jsn, self.callbacks.get('adjustBands'))
                response = jsnHandle(action="adjustBands", resp=resp, dataDict={
                    "bands": [
                        {
                            "name": value.get('name'),
                            "level": value.get('level')
                        }
                    ]
                })
                if self.enable_track:
                    self.data_tracker.writeData('bands', {"name": value.get('name'),
                                                          "level": value.get('level')})
                if resp:
                    if self.trace_response:
                        self.logger.info(f"Response : {dumps(response)}")
                    if Trace == 'socket_response':
                        await connection.send(dumps(response))
                    elif Trace == 'udp_response':
                        udp_client.sendResponse(dumps(response).encode('ascii'), dataArr[2])
            except Exception as e:
                self.logger.exception('Error Occurred')


        elif jsn.get(JSON_COMMANDS.get('ACTION')) == 'resetBands':
            try:
                assert (verfiySignature(jsn.get('payload'), jsn.get("signature").get("HMAC")))
                resp = await self.resetBands(jsn, self.callbacks.get('resetBands'))
                response = jsnHandle(action="resetBands", resp=resp, dataDict={
                    "bands": [
                            {
                                "name": "BASS",
                                "level": 0
                            },
                            {
                                "name": "MIDRANGE",
                                "level": 0
                            },
                            {
                                "name": "TREBLE",
                                "level": 0
                            }]
                })

                if resp:
                    if self.trace_response:
                        self.logger.info(f"Response : {dumps(response)}")
                    if Trace == 'socket_response':
                        await connection.send(dumps(response))
                    elif Trace == 'udp_response':
                        udp_client.sendResponse(dumps(response).encode('ascii'), dataArr[2])
            except Exception as e:
                self.logger.exception('Error Occurred')




        elif jsn.get(JSON_COMMANDS.get('ACTION')) == 'setMode':
            try:

                assert (verfiySignature(jsn.get('payload'), jsn.get("signature").get("HMAC")))
                resp, value = await self.setMode(jsn, self.callbacks.get('setMode'))
                response = jsnHandle(action="setMode", resp=resp, dataDict={
                     "mode": value
                })

                if resp:
                    if self.trace_response:
                        self.logger.info(f"Response : {dumps(response)}")
                    if Trace == 'socket_response':
                        await connection.send(dumps(response))
                    elif Trace == 'udp_response':
                        udp_client.sendResponse(dumps(response).encode('ascii'), dataArr[2])
            except Exception as e:
                self.logger.exception('Error Occurred')


        elif jsn.get(JSON_COMMANDS.get('ACTION')) == 'setLockState':
            try:
                assert (verfiySignature(jsn.get('payload'), jsn.get("signature").get("HMAC")))
                resp, value = await self.setLockState(jsn, self.callbacks.get('setLockState'))
                response = jsnHandle(action="setLockState", resp=resp, dataDict={
                    "state": value.upper() + 'ED'
                })

                if resp:
                    if self.trace_response:
                        self.logger.info(f"Response : {dumps(response)}")
                    if Trace == 'socket_response':
                        await connection.send(dumps(response))
                    elif Trace == 'udp_response':
                        udp_client.sendResponse(dumps(response).encode('ascii'), dataArr[2])
            except Exception as e:
                self.logger.exception('Error Occurred')

        ############################ EVENTS ###########################################################
        if Trace == 'doorbell_event_response':
            self.logger.info('Sending Doorbell Event Response')
            await connection.send(dumps(jsn))

        elif Trace == 'temp_hum_event_response':
            self.logger.info('Sending temperature humidity response')
            await connection.send(dumps(jsn))

        elif Trace == 'setpowerstate_event_response':
            self.logger.info('Sending setpowerstate_event_response')
            await connection.send(dumps(jsn))

        elif Trace == 'setPowerLevel_event_response':
            self.logger.info('Sending setPowerLevel_event_response')
            await connection.send(dumps(jsn))

        elif Trace == 'setBrightness_event_response':
            self.logger.info('Sending setBrightness_event_response')
            await connection.send(dumps(jsn))

        elif Trace == 'setColor_event_response':
            self.logger.info('Sending setColor_event_response')
            await connection.send(dumps(jsn))

        elif Trace == 'setColorTemperature_event_response':
            self.logger.info('Sending setColorTemperature_event_response')
            await connection.send(dumps(jsn))

        elif Trace == 'setThermostatMode_event_response':
            self.logger.info('Sending setThermostatMode_event_response')
            await connection.send(dumps(jsn))

        elif Trace == 'setRangeValue_event_response':
            self.logger.info('Sending setRangeValue_event_response')
            await connection.send(dumps(jsn))

        elif Trace == 'motion_event_response':
            self.logger.info('Sending motion_event_response')
            await connection.send(dumps(jsn))

        elif Trace == 'contact_event_response':
            self.logger.info('Sending contact_event_response')
            await connection.send(dumps(jsn))

        elif Trace == 'set_volume_event_response':
            self.logger.info('Sending set_volume_event_response')
            await connection.send(dumps(jsn))

        elif Trace == 'select_input_event_response':
            self.logger.info('Sending select_input_event_response')
            await connection.send(dumps(jsn))

        elif Trace == 'media_control_event_response':
            self.logger.info('Sending media_control_event_response')
            await connection.send(dumps(jsn))

        elif Trace == 'change_channel_event_response':
            self.logger.info('Sending change_channel_event_response')
            await connection.send(dumps(jsn))

        elif Trace == 'set_bands_event_response':
            self.logger.info('Sending set_bands_event_response')
            await connection.send(dumps(jsn))

        elif Trace == 'set_mode_event_response':
            self.logger.info('Sending set_mode_event_response')
            await connection.send(dumps(jsn))

        elif Trace == 'set_lock_event_response':
            self.logger.info('Sending set_lock_event_response')
            await connection.send(dumps(jsn))

        elif Trace == 'reset_bands_event_response':
            self.logger.info('Sending reset_bands_event_response')
            await connection.send(dumps(jsn))
