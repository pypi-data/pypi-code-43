class ConstantsYealinkManager:
  IP = 'ip'
  ACTION = 'action'
  CREDENTIAL = 'credential'
  OPERATIVECOMMENT = 'operativeComment'

  HELPMESSAGELIST = (
    " ---- Formato della lista ---- "
    "ip, azione, credenziali, commento operativo"
    '"|" è il quote char'
  )

  NOPATH = "ERRORE non è stato specificato il path di lista"
  INVALIDCSV = "Attenzione Formato lista non valido!"

  LOGO = """
----------------------------------------------------------------------------
 __   __         _ _       _      __  __                                   
 \ \ / /__  __ _| (_)_ __ | | __ |  \/  | __ _ _ __   __ _  __ _  ___ _ __ 
  \ V / _ \/ _` | | | '_ \| |/ / | |\/| |/ _` | '_ \ / _` |/ _` |/ _ \ '__|
   | |  __/ (_| | | | | | |   <  | |  | | (_| | | | | (_| | (_| |  __/ |   
   |_|\___|\__,_|_|_|_| |_|_|\_\ |_|  |_|\__,_|_| |_|\__,_|\__, |\___|_|   
                                                           |___/           
----------------------------------------------------------------------------
"""

  HELPMESSAGE = """
----------------------------------------------------------
Da shell lanciare il comando in questo modo:  

$ ym nomeFileLista.csv

oppure:

$ YealinkManager nomeFileLista.csv

----------------------------------------------------------

nomeFileLista.csv deve avere il seguente formato:
192.168.9.1,Reboot,admin:admin,Yealink T27P - Ufficio Commerciale
192.168.9.2,Reboot,admin:admin,Yealink T27P - Ufficio Amministrazione
192.168.9.3,Reboot,admin:admin,Yealink T23  - Ufficio Tecnico

i carattere # ad inizio riga commenta la riga stessa:

192.168.9.1,Reboot,admin:admin,Commento1
#192.168.9.2,Reboot,admin:admin,Commento1 <- questa riga sarà saltata
192.168.9.3,Reboot,admin:admin,Commento1

L'ultimo elemento della lista è un commento operativo:

----------------------------------------------------------
I possibili comandi sono i seguenti:

* "OK" / "ENTER"
  Press the OK key or the Enter soft   key.
 
* "SPEAKER"
  Press the Speaker key.
 
* "F_TRANSFER"
  Press the Transfer key.
 
* "VOLUME_UP"
  Increase the volume.
 
* "VOLUME_DOWN"
  Decrease the volume.
 
* "MUTE"
  Mute the call.
 
* "F_HOLD"
  Press the Hold key.
 
* "X"
  Press the X key.
 
* "0-9/*/POUND"
  Send the DTMF digit (0-9, * or #).  
 
* "L1-L6"
  Press the Line key.
 
* "D1-D10"
  Press the DSS key.
 
* "F_CONFERENCE"
  Press the Conference key.
 
* "F1-F4"
  Press the Soft key.
 
* "MSG"
  Press the MESSAGE key.
 
* "HEADSET"
  Press the HEADSET key.
 
* "RD"
  Press the Redial key.
 
* "UP/DOWN/LEFT/RIGHT"
  Press the Navigation keys.
 
* "Reboot"
  Reboot the IP phone.
 
* "AutoP"
  Let the IP phone do auto   provisioning.
 
* "DNDOn"
  Activate the DND mode.
 
* "DNDOff"
  Deactivate the DND mode.
----------------------------------------------------------
"""