#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket
import logging
import asyncio
import threading
import time


#_LOGGER = logging.getLogger(__name__)
#dictionary with all light status
lightData = {}
#dictionary with all probe T
temperatureData = {}
#dictionary witth all probe set T
setTemperatureData = {}
#dictionary with valve state off all probe
valveStateData = {}
#dictionary with the data from gateway_answer
gatewayData = {}
#flag to stop event bus
stopRequest = False
#flag to check if an event session is active
sessionEvent = False
#flag to check if a command session is active
sessionCmd = False
#flag for wait the connection event bus
connectingEvent = False
#flag for wait the connection comand bus
connectingCmd = False
#flag to start wakeup
wakeup = False


connectionSocketEvent = False
connectionSocketCmd = False

class OpenWeb(object):

    #OK Message from bus
    ACK = '*#*1##'
    #NON OK Message from bus
    NACK = '*#*0##'
    #end of al message on the bus
    ENDMES = "##"
    #message for connection in Command mode - write and read single data from to bus
    CMDMODE = "*99*0##"
    #message for connection in Event mode - read continuosly data from bus
    EVENTMODE = "*99*1##"
    #pwd frame lenght
    ISPSWFRAME = 6



    #init method
    def __init__ (self, host, port, psw):

        import socket
        logging.basicConfig(filename='openweb.log', filemode='w', level=logging.DEBUG)
        self._host = host
        self._port = int(port)
        self._psw = psw
        self._buffer = 1024
        #Flag to check if session is active or not
        #self._sessionevent = False
        #self._sessioncmd = False



        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        #create a dictionari for light ["address","status"] (status= "1" light ON, "0" light OFF)
        self._datafrombus =[]


    #Method to calculate the password to send to host
    def calculated_psw (self, nonce):
        logging.info('calculate psw')
        m_1 = 0xFFFFFFFF
        m_8 = 0xFFFFFFF8
        m_16 = 0xFFFFFFF0
        m_128 = 0xFFFFFF80
        m_16777216 = 0XFF000000
        flag = True
        num1 = 0
        num2 = 0
        self._psw = int(self._psw)

        for c in nonce:
            num1 = num1 & m_1
            num2 = num2 & m_1
            if c == '1':
                length = not flag
                if not length:
                    num2 = self._psw
                num1 = num2 & m_128
                num1 = num1 >> 7
                num2 = num2 << 25
                num1 = num1 + num2
                flag = False
            elif c == '2':
                length = not flag
                if not length:
                    num2 = self._psw
                num1 = num2 & m_16
                num1 = num1 >> 4
                num2 = num2 << 28
                num1 = num1 + num2
                flag = False
            elif c == '3':
                length = not flag
                if not length:
                    num2 = self._psw
                num1 = num2 & m_8
                num1 = num1 >> 3
                num2 = num2 << 29
                num1 = num1 + num2
                flag = False
            elif c == '4':
                length = not flag

                if not length:
                    num2 = self._psw
                num1 = num2 << 1
                num2 = num2 >> 31
                num1 = num1 + num2
                flag = False
            elif c == '5':
                length = not flag
                if not length:
                    num2 = self._psw
                num1 = num2 << 5
                num2 = num2 >> 27
                num1 = num1 + num2
                flag = False
            elif c == '6':
                length = not flag
                if not length:
                    num2 = self._psw
                num1 = num2 << 12
                num2 = num2 >> 20
                num1 = num1 + num2
                flag = False
            elif c == '7':
                length = not flag
                if not length:
                    num2 = self._psw
                num1 = num2 & 0xFF00
                num1 = num1 + (( num2 & 0xFF ) << 24 )
                num1 = num1 + (( num2 & 0xFF0000 ) >> 16 )
                num2 = ( num2 & m_16777216 ) >> 8
                num1 = num1 + num2
                flag = False
            elif c == '8':
                length = not flag
                if not length:
                    num2 = self._psw
                num1 = num2 & 0xFFFF
                num1 = num1 << 16
                num1 = num1 + ( num2 >> 24 )
                num2 = num2 & 0xFF0000
                num2 = num2 >> 8
                num1 = num1 + num2
                flag = False
            elif c == '9':
                length = not flag
                if not length:
                    num2 = self._psw
                num1 = ~num2
                flag = False
            else:
                num1 = num2
            num2 = num1
        return num1 & m_1

    #Method for close the connection with host
    def disconnection(self,type):
        global sessionEvent
        global sessionCmd
        global connectionSocket
        global connectionSocketCmd


        logging.info('disconnection')
        self._socket.close()
        connectionSocket = False
        if type == "cmd":
            sessionCmd = False
            connectionSocketCmd = False
            print("cmd disconnection")
        elif type == "event":
            sessionEvent = False
            print("event disconnection")
        elif type =="all":
            sessionCmd = False
            sessionEvent = False

    #Method for send data to host
    def send_data(self, data):
        #print('send_data to bus',data)
        try:
            self._socket.send(data.encode())
            #self.read_data()
            return True
        except:
            return False

    #Method for read data from host
    def read_data(self):
        try:
            message = str(self._socket.recv(1024).decode())
            #print('read data from bus',message)
            return message
        except:
            #print('read data from bus broken')
            return "Broken"

    #Method to open the connection with Gateway return True or False
    def connectToGtwOWN(self,connectionMode):
        global connectionSocketEvent


        if self._port == 0 or len(self._host) == 0 :
            logging.error ('Cannot connect to Gateway. IP or Port empty')
        else:
            if not connectionSocketEvent:
                #Open the connection
                self._socket.connect((self._host,self._port))
                #Gatway answer with an ACK or NACK, check the answer
                if self.read_data() == self.ACK :
                    #if Gatway send ACK is waiting for a session, send the string for connection type session
                    self.send_data(connectionMode)
                    answer = self.read_data()
                    #print("answer event",answer)
                    #at the first connection Gatway answer with a password request
                    if len(answer) > self.ISPSWFRAME :
                        # if the Gatway answer asking password we calculate the answer
                        psw_open = '*#' + str(self.calculated_psw(answer)) + '##'
                        #and send the password
                        self.send_data(psw_open)
                        #IF the Gatway answer with an ACK the session is active so we set the flag
                        if self.read_data() == self.ACK :
                            #print('event connect session Event True')
                            connectionSocketEvent = True
                            return  True
                        #otherwise ACK report the error
                        else:
                            logging.error("Password error")
                            return  False
                    #If the Gatway answer with a NACK report the error
                    else :
                        logging.error("Gatway refuse the section")
                        return False
                else :
                    logging.error("It's not possible to init the connection with Gatway")
                    self.disconnection("all")
                    return False

    #Method to open the connection with Gateway return True or False
    def connectToGtwOWNX(self,connectionMode):
        global connectionSocketCmd
        global connectingCmd
        #turn true the flag of connecting in progress
        connectingCmd = True

        if self._port == 0 or len(self._host) == 0 :
            logging.error ('Cannot connect to Gateway. IP or Port empty')
        else:
            if not connectionSocketCmd:
                #Open the connection
                self._socket.connect((self._host,self._port))
                #Gatway answer with an ACK or NACK, check the answer
                if self.read_data() == self.ACK :
                    #if Gatway send ACK is waiting for a session, send the string for connection type session
                    a=self.comand_connection(connectionMode)
                    #print('a',a)
                    return a
                else :
                    logging.error("It's not possible to init the connection with Gatway")
                    self.disconnection("all")
                    return False


    def comand_connection(self,connectionMode):

        #if Gatway send ACK is waiting for a session, send the string for connection type session
        self.send_data(connectionMode)
        answer = self.read_data()
        #print("answer cmd",answer)
        #at the first connection Gatway answer with a password request
        if len(answer) > self.ISPSWFRAME :
            # if the Gatway answer asking password we calculate the answer
            psw_open = '*#' + str(self.calculated_psw(answer)) + '##'
            #and send the password
            self.send_data(psw_open)
            #IF the Gatway answer with an ACK the session is active so we set the flag
            if self.read_data() == self.ACK :
                #print('CMD connect')
                connectionSocketCmd = True
                return  True
            #otherwise ACK report the error
            else:
                logging.error("Password error")
                return  False

    #Read the data from event bus
    def read_event_bus(self):
        #all dictionary must be GLOBAL variable to be modify
        global lightData
        global temperatureData
        global setTemperatureData
        global sessionEvent
        global connectingEvent
        #print('sessionEvent',sessionEvent)
        #Check if session event is not open, open it
        if not sessionEvent:


                    #turn true the flag of connecting in progress
            connectingEvent = True
            sessionEvent = self.connectToGtwOWN(self.EVENTMODE)
            self.read_event_bus()
            #otherwise
        else :
            #print('PRIMO PASSO')
            #continuosly read the bus till when a stop is request
            while not stopRequest:
                #read the bus
                answer = self.read_data()
                #print('answer',answer)
                if  answer :
                    #divide the answer from bus in single data
                    self.datafrombus = answer.split("##")
                    #print("self.datafrombus",self.datafrombus)
                    for data in self.datafrombus:
                        if data[:3] =="*1*":
                            tmp=data.split("*")
                            lightData[tmp[3]]=tmp[2]
                            #print("light data",lightData)

                        elif data[:4] =="*#4*":
                            tmp=data.split("*")
                            if tmp[3] == "14":
                                setTemperatureData[tmp[2]]=float(tmp[4])/10
                            elif tmp[3] == "0":
                                temperatureData[tmp[2]]=float(tmp[4])/10

    #Method for read the status of the solenoid valve of selected sensor
    def temperature_status(self,address):
        global sessionEvent
        global connectingEvent
        #if session Event is not started
        if not sessionEvent:
            #if we are not already connecting
            if not connectingEvent:
                #print('session event start')
                t1 = threading.Thread(target=self.read_event_bus)
                t1.start()
        else:
            #read Temperature from dictionary
            return temperatureData.get(address)

    def setTemperature_status(self,address):
        global sessionEvent
        global connectingEvent
        #if session Event is not started
        if not sessionEvent:
            #if we are not already connecting
            if not connectingEvent:
                #print('session event start setTemperature')
                t1 = threading.Thread(target=self.read_event_bus)
                t1.start()
        else:
            #read setTemperature from dictionary
            return setTemperatureData.get(address)

    def gateway_Status(self,what):
        return gatewayData.get(what)

    def light_status(self,address):
        global sessionEvent
        global connectingEvent
        global lightData
        #if session Event is not started
        if not sessionEvent:
            #if we are not already connecting
            if not connectingEvent:
                #print('session event start')
                #print('self._host',self._host)
                #print('self._port',self._port)
                #print('self._psw',self._psw)
                gate = OpenWeb(self._host,self._port,self._psw)
                #print('gate',gate)
                t1 = threading.Thread(target=gate.read_event_bus)
                t1.start()
        else:
            if lightData.get(address) == "1" :
                return True
            else:
                return False

    #read status valve from dictionary
    def valveState_status(self,address):
        return valveStateData.get(address)

    #open a comand session with Gateway
    def cmd_bus(self,who,what,where):
        #flag to check if a comand session is just active
        global sessionCmd
        global connectionSocketCmd
        global lightData
        global temperatureData
        global setTemperatureData

        #print('cmd_bus who',who)
        #print('cmd_bus what',what)
        #print('cmd_bus where',where)


        #if there isn't the comand session
        if not sessionCmd:
            #open it
            sessionCmd = self.connectToGtwOWNX(self.CMDMODE)

        #ask for valve state at address=where
        if who == '4' and what == '19':
            #create comand for Gateway
            comand = '*#4*'+ where +'*19##'
            self.send_data(comand)
            self.interpret_answer()

        elif who == '4' and what == '':
            comand = '*#4*#0##'
            self.send_data(comand)
            self.interpret_answer()

        #comand read Temperature
        elif who == '4' and what == '0':
            #print('where',where)
            #print('temperatureData.get',temperatureData.get(where))
            if not temperatureData.get(where):
                comand = '*#4*'+where+'*0##'
                self.send_data(comand)
                self.interpret_answer()

        #comand read set Temperature
        elif who == '4' and what == '14':
            #print('where',where)
            #print('settemperatureData.get',setTemperatureData.get(where))
            if not setTemperatureData.get(where):
                comand = '*#4*'+where+'*0##'
                self.send_data(comand)
                self.interpret_answer()


        #comand OFF ON light
        elif who =='1' and what != '':
            startState = True
            #send comand OpenWeb
            comand = '*1*'+what+'*'+where+'##'
            #and send to the Gateway
            self.send_data(comand)
            self.interpret_answer()
            #comand status light
        elif who =='1' and what == '':
            #print ('where',where)
            #print('lightData',lightData.get(where))
            if not lightData.get(where):
                #send comand OpenWeb
                comand = '*#1*'+where+'##'
                #print('comand light',comand)
                #and send to the Gateway
                self.send_data(comand)
                self.interpret_answer()
        #ask info from Gateway
        elif who == '13':
            comand = '*#13**'+ what + '##'
            #and send to the Gateway
            self.send_data(comand)
            self.interpret_answer()

    #interpret all answer from comand bus
    def interpret_answer(self):
        busAnswer = '*'
        answer = self.read_data().split('##')

        #print('answer from bus',answer)
        #print('len',len(answer))
        #if recive only an ACK read again the bus
        if len(answer) == 2 and answer[0]== '*#*1':
            #print('answer was ACK')
            self.interpret_answer()
        #if the answer has ACK at the begining
        elif len(answer) == 3 and answer[0] == '*#*1':
            #the answer is the second value of list
            busAnswer = answer[1]
            #print('ACK at the begining',busAnswer)
        #if the answer has ACK at the END
        elif len(answer) ==3 and answer[1] == '*#*1' :
            busAnswer= answer[0]
            #print('ACK at the end', busAnswer)
        elif len(answer) == 2 and answer[1] != '*#*1':
            busAnswer = answer[0]
            #print('answer ok',busAnswer)
        else:
            self.interpret_answer()

        #the answer is now clean and we can analyse
        result =busAnswer.split('*')
        #print('result',result)
        if len(result) != 2 :
            self.updateAllState(result)

    #write the answer from bus to dictionary
    def updateAllState(self,result):
        global valveStateData
        global gatewayData

        #print('updateAllState Result',result)
        #if the resul is about temperature frame
        if result[1] == '#4':
            #tempearature from probe
            if result[3] == '19':
                #all different possible answer for valve status
                if result[4] == '0' and result[5] == '0':
                    gateway_answer = 'OFF'
                elif result[4] == '1' and result[5] == '1':
                    gateway_answer = "ON"
                elif result[4] == '2' and result[5] == '2':
                    gateway_answer = "Opened"
                elif result[4] == '3' and result[5] == '3':
                    gateway_answer = "Closed"
                elif result[4] == '4' and result[5] == '4':
                    gateway_answer = "Stop"
                elif result[4] == '5' and result[5] == '5':
                    gateway_answer = "OFF Fan Coil"
                elif result[4] == '6' and result[5] == '6':
                    gateway_answer = "ON speed 1"
                elif result[4] == '7' and result[5] == '7':
                    gateway_answer = "ON speed 2"
                elif result[4] == '8' and result[5] == '8':
                    gateway_answer = "ON speed 3"
            valveStateData[result[2]] = gateway_answer
            #print('valvestatus',valveStateData)
        #gateway info request
        elif result[1] == '#13':
            if result[3] == '0':
                ore = result[4]
                minuti = result[5]
                secondi = result[6]
                gateway_answer = ore+':'+minuti+':'+secondi

            elif result[3] == '1':
                dayweek ={'00':'Sunday','01':'Monday','02':'Tuesday','03':'Wednesday','04':'Thursday','05':'Friday','06':'Saturday'}
                day = dayweek.get(result[4])
                gg = result[5]
                mm = result[6]
                aa = result[7]
                gateway_answer = day+'-'+gg+'/'+mm+'/'+aa

            elif result[3] == '10' :
                ip1 = result[4]
                ip2 = result[5]
                ip3 = result[6]
                ip4 = result[7]
                gateway_answer =ip1+'.'+ip2+'.'+ip3+'.'+ip4

            elif result[3] == '15' :
                if result[4] == "2*":
                    gateway_answer = "MH Server"
                elif result[4] == "4*":
                    gateway_answer = "MH200"
                elif result[4] == "6*":
                    gateway_answer = "F452"
                elif result[4] == "7*":
                    gateway_answer = "F452V"
                elif result[4] == "11":
                    gateway_answer = "MHServer2"
                elif result[4] == "13":
                    gateway_answer = "H4684"
                elif result[4] == "23":
                    gateway_answer = "H/L4684"

            elif result[3] =='16':
                #call metod to extract firmware version data from open command string
                gateway_answer = result[4]+"."+result[5]+"."+result[6]

            elif result[3] == '19':
                gateway_answer = result[4]+"d "+result[5]+"h "+result[6]+"m "+result[7]+"s"
            elif result[3] == '24':
                gateway_answer = 'wakeup'
            gatewayData[result[3]]=gateway_answer
            #print('gatewayData',gatewayData)



    def wakeup_cmd(self):
        while not stopRequest:
            time.sleep(20)
            self.send_data("*#1*0##")


    #send comand to light to turn ON and OFF
    def cmd_open(self,who,what,where):
        global sessionCmd
        global connectingCmd
        global wakeup
        #print('sessionCmd',sessionCmd)
        #print('connectingCmd',connectingCmd)
        if not sessionCmd:
            if not connectingCmd:
                t2 = threading.Thread(target=self.cmd_bus, args=(who,what,where))
                t2.start()
                #self.cmd_open(who,what,where)
                #print('t2 start')
        elif sessionCmd and not wakeup:
            wakeup = True
            t3 = threading.Thread(target=self.wakeup_cmd)
            t3.start()
            #print('t3 start')

        else:
            #print('cmd_open who',who)
            #print('cmd_open what',what)
            #print('cmd_open where',where)
            self.cmd_bus(who,what,where)



    #Info from Gateway
    def info_gateway(self,what):
        global gatewayData

        #create a dictionary with type of data to request
        #gateway_request = {'Time': '0','Date':'1','IP':'10','Net Mask':'11','MAC':'12','Type':'15','Firmware':'16','Uptime':'19'}
        #init the answer
        gateway_answer =""

        #create the open command string
        info_gateway_cmd = '*#13**'+ what + '##'
        #print('info_gateway_cmd',info_gateway_cmd)
        #and send data to Gatway
        self.send_data(info_gateway_cmd)
        answer = self.read_data()
        #print('answer_gateway',answer)
        #If the answer is NACK report the error
        if answer == OpenWeb.NACK :
            _LOGGER.exception("Gatway refuses to send Gatway data")
            return False
        tmp = answer.split('##')
        tmp1 = tmp[0].split('*')

        #create the answer
        if what == '0':
            ore = tmp1[4]
            minuti = tmp1[5]
            secondi = tmp1[6]
            gateway_answer = ore+':'+minuti+':'+secondi

        elif what == '1':
            dayweek ={'00':'Sunday','01':'Monday','02':'Tuesday','03':'Wednesday','04':'Thursday','05':'Friday','06':'Saturday'}
            day = dayweek.get(tmp1[4])
            gg = tmp1[5]
            mm = tmp1[6]
            aa = tmp1[7]
            gateway_answer = day+'-'+gg+'/'+mm+'/'+aa

        elif what == '10' :
            ip1 = tmp1[4]
            ip2 = tmp1[5]
            ip3 = tmp1[6]
            ip4 = tmp1[7]
            gateway_answer =ip1+'.'+ip2+'.'+ip3+'.'+ip4

        elif what == '15' :
            if tmp1[4] == "2*":
                gateway_answer = "MH Server"
            elif tmp1[4] == "4*":
                gateway_answer = "MH200"
            elif tmp1[4] == "6*":
                gateway_answer = "F452"
            elif tmp1[4] == "7*":
                gateway_answer = "F452V"
            elif tmp1[4] == "11":
                gateway_answer = "MHServer2"
            elif tmp1[4] == "13":
                gateway_answer = "H4684"
            elif tmp1[4] == "23":
                gateway_answer = "H/L4684"

        elif what =='16':
            #call metod to extract firmware version data from open command string
            gateway_answer = tmp1[4]+"."+tmp1[5]+"."+tmp1[6]

        elif what == '19':
            gateway_answer = tmp1[4]+"d "+tmp1[5]+"h "+tmp1[6]+"m "+tmp1[7]+"s"
        gatewayData[what]=gateway_answer
        #print('gatewayData',gatewayData)




#start to read from event bus
#def start_event_bus():

#    gate1 = OpenWeb(self._host,self._port,self._psw)
#    gate1.read_event_bus()




#create a thread to continuosly read from bus

#t1=threading.Thread(target=start_event_bus)
#t2 = threading.Thread(target=statusValve)
#print('start t1')

##t2.start()



###############################################
####
####               for TEST
####
####
#
#time.sleep(2)
#gate.cmd_bus('4','19','11')
#
#for i in range(1,13):
#
#    if gate.light_status('71'):
#        print("71 ON")
#    else:
#        print("71 OFF")
#
#    time.sleep(1)
#    if gate.light_status('72'):
#        print("72 ON")
#    else:
#        print("72 OFF")
#    time.sleep(1)
#
#    print("T 11",gate.temperature_status("11"))
#
#    gate.cmd_light("0","72")
#
#    time.sleep(1)
#    print("setT 11",gate.setTemperature_status("11"))
