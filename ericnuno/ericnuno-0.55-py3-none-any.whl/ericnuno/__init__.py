"""
Author: Eric Nuno

These are for making my own life easier, nothing else.
"""


import time
import os
import subprocess
import telnetlib
import smtplib
import json
import sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import getpass
import paramiko
import bs4
import requests
from pyvim.connect import SmartConnectNoSSL
from pyvim import *
from pyVmomi import vim

def FindVMIP(IP, usern, passw, vIP):
    """ This finds virtual machine IP addresses in vSphere """
    def find_IP(virtual_machine, IPLook):

        summary = virtual_machine.summary
        for nic in virtual_machine.guest.net:

            if nic.ipConfig is not None:
                addresses = nic.ipConfig.ipAddress

                for adr in addresses:
                    if IPLook == adr.ipAddress:
                        print("IP being used by: " + summary.config.name)

    c = SmartConnectNoSSL(host=vIP, user=usern, pwd=passw)

    content = c.RetrieveContent()
    container = content.rootFolder
    viewType = [vim.VirtualMachine]
    recursive = True
    containerView = content.viewManager.CreateContainerView(
        container, viewType, recursive)
    children = containerView.view

    for child in children:
        find_IP(child, IP)

def RESTGet(url, usern="", passw="", devicetype=""):
    """ Performs a RESTful API 'GET' """
    authskip = False
    if devicetype.lower() == "dell":
        usern = "root"
        passw = "calvin"
    elif devicetype.lower() == "quanta":
        usern = "admin"
        passw = "cmb9.admin"
    elif devicetype.lower() == 'supermicro':
        usern = "ADMIN"
        passw = "ADMIN"

    if usern == "" and passw == "":
        authskip = True

    requests.packages.urllib3.disable_warnings()
    try:
        if not authskip:
            response = requests.get(url, verify=False, auth=(usern, passw))
        else:
            response = requests.get(url, verify=False)

        JSONparsed = json.loads(response.text)
        JSONPrettyOutput = json.dumps(JSONparsed, indent=4, sort_keys=True)
        return JSONparsed, JSONPrettyOutput
    except requests.exceptions.RequestException as err:
        print(err)
        sys.exit(1)

def RESTPost(url, body, usern="", passw="", devicetype=""):
    """ Performs a RESTful API 'POST' """
    authskip = False
    if devicetype.lower() == "dell":
        usern = "root"
        passw = "calvin"
    elif devicetype.lower() == "quanta":
        usern = "admin"
        passw = "cmb9.admin"
    elif devicetype.lower() == 'supermicro':
        usern = "ADMIN"
        passw = "ADMIN"

    if usern == "" and passw == "":
        authskip = True

    headers = {
        'Content-Type': "application/json",
        'Cache-Control': "no-cache",
        'Postman-Token': "119935c1-644c-419e-897a-be07c62f74bf"
        }

    requests.packages.urllib3.disable_warnings() #pylint: disable=E1101
    try:
        if not authskip:
            response = requests.post(url, headers=headers, json=body, verify=False, auth=(usern, passw))
        else:
            response = requests.post(url, headers=headers, json=body, verify=False)

        JSONparsed = json.loads(response.text)
        JSONPrettyOutput = json.dumps(JSONparsed, indent=4, sort_keys=True)
        return JSONparsed, JSONPrettyOutput
    except requests.exceptions.RequestException as err:
        print(err)
        sys.exit(1)

def CMD(phrase):
    """ Need to ask Ricky what this does again """
    def formatCMDs(phrase):
        cmds = [] #final list of commands to return
        quotedCMD = '' #for appending command if in quotes
        nonQuotedCMD = '' #for appending command if not in quotes
        quoted = False #used as toggle to know which variable to append to
        for ch in phrase: #iterating through each character - "'s are used to toggle quoted boolean
            if ch == '"':
                quoted = not quoted
                if len(quotedCMD) > 0: #logic for if it's an end quote
                    cmds.append(quotedCMD)
                    quotedCMD = ''
                if len(nonQuotedCMD) > 0: #if starting new quote after unquoted argument
                    cmds.append(nonQuotedCMD)
                    nonQuotedCMD = ''
            if ch != '"':
                if quoted: #appending to quotedCMD until toggle turned back off
                    quotedCMD += ch
                else:
                    if ch == ' ' and len(nonQuotedCMD) > 0: #splitting unquoted commands
                        cmds.append(nonQuotedCMD)
                        nonQuotedCMD = ''
                    elif ch != ' ': #appending unquoted command
                        nonQuotedCMD += ch
                        #doing nothing if encountering space with len(nonQuotedCMD) == 0

        if len(nonQuotedCMD) > 0: #appending any stragglers at the end since can't use space as trigger
            cmds.append(nonQuotedCMD)
            nonQuotedCMD = ''
        return cmds

    cmds = formatCMDs(phrase)
    output = subprocess.check_output(cmds, shell=True).decode()
    return output

def email(fromField, toField, subject, message, IP, port="25"):

    """ email function """

    #you can pass message as string, dict or an array of strings/dicts (or both)
    def formatMessage(message):
        #can format message as dict: {"Msg": "enter message here", "Tags": ["<ex1>", "<ex2>"]}
        #order your tags in the order you want them nested
        #closeTags() will automatically close them for you
        def dictFormat(message):
            def closeTags(tags):
                closeTags = []
                for tag in tags[::-1]: #reversing tags for proper nesting and returning as string
                    closeTags.append(tag[0] + '/' + tag[1:])
                return ''.join(closeTags)

            #return only Msg for plain text
            return message["Msg"], ''.join(message["Tags"]) + message["Msg"] + closeTags(message["Tags"])

        def listFormat(message):
            #will append each line to one main string per text and html
            #text will append \n at end and html will append <br/> to signal end of line
            joinText = ''
            joinHTML = ''
            for line in message:
                if isinstance(line, str):
                    joinText += line + '\n'
                    joinHTML += line + '<br/>'
                elif isinstance(line, dict):
                    text, html = dictFormat(line)
                    joinText += text + '\n'
                    joinHTML += html + '<br/>'
                else:
                    return #error handling
            return joinText, joinHTML

        if isinstance(message, str):
            text = message
            html = message
        elif isinstance(message, dict):
            text, html = dictFormat(message)
        elif isinstance(message, list):
            text, html = listFormat(message)
        else:
            return #error handling
        return text, html

    # Converts a "to" string into a list for the email
    if isinstance(toField, str):
        if toField.count("@") == 1:
            toFieldString = toField
            toField = []
            toField.append(toFieldString)
        elif toField.count(";") > 1 and toField.count(",") == 0: # emails can be separated by ","
            toField = toField.split(";")
        elif toField.count(",") > 1 and toField.count(";") == 0: # emails can also be separated by ";"
            toField = toField.split(",")

    from_field = fromField #"First Last <first.last@wwt.com>"
    to_field = ', '.join(toField) #["First Last <first.last@wwt.com>", "First Last <first.last@wwt.com>"]
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject #string
    msg["From"] = from_field
    msg["To"] = to_field
    text, html = formatMessage(message)
    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")
    msg.attach(part1)
    msg.attach(part2)

    try:
        server = smtplib.SMTP(IP, port)
        server.sendmail(from_field, to_field, msg.as_string())
        server.quit()
        print("\nThe email was sent successfully!\n")
        return
    except Exception: # except by itself catches keyboard interrupts and system exits
        print("\n!!!The email failed to send!!!\n")
        return
    #need error checking to ensure tags are valid syntax
    #need error checking to ensure tag is list
    #need to handle exceptions
    #look into handling "Msg" as potential list in order to split up bodies to allow for inline html tags

def ping(hostname, n=3):
    """ standard Windows ping """
    output = subprocess.run(["ping", hostname, "-n", str(n)], stdout=subprocess.PIPE)
    result = output.stdout.decode()

    #and then check the response...
    if 'Reply from ' + hostname + ': bytes=' in result:
        return True
    elif hostname.count('.') != 3:
        if ': bytes=' in result and 'Reply from ' in result:
            return True
    else:
        return False

def ZipToZone(zipcode, msgbox=False):
    """ returns time zone from a zip code """
    zipcode = str(zipcode)
    try:
        req = requests.get('http://www.zip-info.com/cgi-local/zipsrch.exe?tz=tz&zip=' + zipcode +'&Go=Go')
        req.raise_for_status()
        ZipObj = bs4.BeautifulSoup(req.text, "lxml")

        if "PST" in ZipObj.encode('ascii').decode():
            return "Pacific"
        elif "MST" in ZipObj.encode('ascii').decode():
            return "Mountain"
        elif "CST" in ZipObj.encode('ascii').decode():
            return "Central"
        elif "EST" in ZipObj.encode('ascii').decode():
            return "Eastern"

    except Exception:
        try:
            if msgbox:
                print("Couldn't pull the time zone, please make sure you're connected to the internet and try again.")
        except Exception:
            print("Couldn't pull the time zone, please make sure you're connected to the internet and try again.")
            return
    return

def eprint(Sentence):
    """ This is just to pretty up a text sentence """
    SentLeng = len(Sentence)
    print("="* SentLeng *3)
    print(("=" * SentLeng) + Sentence + ("=" * SentLeng))
    print("="* SentLeng *3)

def ssh_connect(device_ip, username, password, screenprint=False):
    """ Creates a my standard used paramiko client and channel """
    if screenprint:
        print("Connecting to: " + device_ip)

    hostname = device_ip
    port = 22

    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname, port=port, username=username, password=password)
    channel = client.invoke_shell()

    if screenprint:
        print("Successfully connected to: " + device_ip)

    return client, channel

def psend(command, channel):
    """ This just sends the command through the channel. Mainly so it can be used with pwait function. """
    channel.send(command)

def pwait(waitstr, channel, tout=0, screenprint=False):
    """ paramiko wait with optional timeout """
    startTime = int(time.time())
    stroutput = ''
    while waitstr not in stroutput:
        currentTime = int(time.time())
        if channel.recv_ready():
            try:
                current = channel.recv(9999).decode()
                stroutput += current
                if current.strip() != '':
                    if screenprint:
                        print(current, end='')
            except Exception:
                continue

        if tout != 0:
            if (currentTime - startTime) > tout:
                try:
                    if current.strip() != '':
                        if screenprint:
                            print(current, end='')
                except Exception:
                    pass
                return stroutput
    return stroutput

def twait(phrase, tn, tout=-1, logging='off', rcontent=False, screenprint=False):
    """ telnetlib wait with optional timeout and optional logging"""

    # Adding code to allow lists for phrase
    finalcontent = ' '

    #This is the time of the epoch
    startTime = int(time.time())
    while True:
        # This is the current time
        currentTime = int(time.time())
        if tout != -1:

            # This is the time since the start of this loop
            # if it exceeds the timeout value passed to it
            # then exit with a return of 0
            if (currentTime - startTime) > tout:
                if logging == 'on':
                    #Adding the -e-e-> to differentiate from device output
                    if screenprint:
                        print('-e-e->It has been ' + str(tout) +  ' seconds. Timeout!')
                if not rcontent:
                    return 0
                return 0, finalcontent

        # Eager reading back from the device
        content = (tn.read_very_eager().decode().strip())

        if content.strip() != '':
            finalcontent += content

        # if the returned content isn't blank. This stops
        # it from spamming new line characters
        if content.strip() != '':
            if screenprint:
                print(content, end='')

        # content was found! Return a 1 for success
        if isinstance(phrase, str):
            if phrase in content:
                if not rcontent:
                    return 1
                return 1, finalcontent

        if isinstance(phrase, list):
            count = 1
            for p in phrase:
                if p in content:
                    if not rcontent:
                        return count
                    return count, finalcontent
                count += 1

def tsend(phrase, tn):
    """ This performs a telnetlib send, and encodes to bytes, first """
    #Sends the phrase that was passed to it as bytes
    tn.write(phrase.encode())

def shortfiles(parentdir, extensions=None):
    """
    This recursively searches a given folder and
    returns just the file names found
    """
    TotalFiles = []
    if extensions is None:
        # underscore means unused variable
        for _, _, filenames in os.walk(parentdir):
            for filename in filenames:
                TotalFiles.append(filename)

    elif extensions is not None:
        extensions = list(extensions)
        for _, _, filenames in os.walk(parentdir):
            for filename in filenames:
                for ext in extensions:
                    if ext in filename:
                        TotalFiles.append(filename)

    return TotalFiles

def longfiles(parentdir, extensions=None):
    """
    This recursively searches the given folder and
    returns the full path of all files found
    """
    TotalFiles = []
    if extensions is None:
        for root, _, filenames in os.walk(parentdir):
            for filename in filenames:
                TotalFiles.append(os.path.join(root, filename))

    elif extensions is not None:
        extensions = list(extensions)
        for root, _, filenames in os.walk(parentdir):
            for filename in filenames:
                for ext in extensions:
                    if ext in os.path.join(root, filename):
                        TotalFiles.append(os.path.join(root, filename))

    return TotalFiles

def get_secret(secretID, server=None, port=None, Username=None, Password=None):
    """
    This allows you to provide a secret ID and
    returns the password from a local database
    """
    #pass in mongodb _id to retrieve associated secret
    #pass in creds at function call - you can exclude password and enter it at prompt for extra security
    if not server or not port or not Username or not Password: #if a param is not passed into function
        #alternatively to passing args, put creds.csv within working dir that include either:
        #http://url:,port,user,pass
        #or
        #http://url:,port,user - leaving off password will ask you to enter it at prompt
        if 'creds.csv' in os.listdir():
            f = open('./creds.csv', 'r')
            contents = f.readlines()[0].split(',')
            if len(contents) >= 3: #will skip to prompt for input if creds.csv incorrectly formatted
                server = contents[0].replace('\n', '')
                port = contents[1].replace('\n', '')
                Username = contents[2].replace('\n', '')
                if len(contents) == 4:
                    Password = contents[3].replace('\n', '') #will pull password if it exists
            f.close()
        if not server or not port or not Username: #if main 3 not passed or acquired via csv, enter at prompt
            server = input('Server address: ')
            port = input('Port number: ')
            Username = input('Username: ')
        if not Password: #if password not passed or acquired via csv, enter at prompt - even if main 3 already specified
            Password = getpass.getpass()
    if server[-1] != ':': #will automatically append : if left off of end of server path
        server += ':'

    creds = {'Username': Username, 'Password': Password}
    loginURL = server + port + '/api/login/'

    #try except in case api is not accessible
    try:
        #using creds to login/retrieve token
        tokenRes = requests.post(url=loginURL, json=creds)
    except Exception:
        print('Unable to access API')
        return

    tokenJSON = tokenRes.json()

    #checking to see if creds are valid
    if 'token' not in tokenJSON:
        print('Invalid login credentials!')
        return

    token = tokenJSON['token']

    #using provided
    secretsURL = server + port + '/api/secrets/' + secretID

    #using token to retrieve secret by _id
    secretRes = requests.get(url=secretsURL, headers={'Authorization': token})
    secretJSON = secretRes.json()

    #checking to see if valid _id was provided
    if 'Secret' not in secretJSON:
        print('Invalid secret _id has been provided')
        return

    secret = secretJSON["Secret"]
    return secret #returning secret as string
