from flask import Flask
from flask_socketio import SocketIO
import time, subprocess
from zumi.zumi import Zumi
from zumi.util.screen import Screen
import zumidashboard.scripts as scripts
import zumidashboard.sounds as sound
import zumidashboard.updater as updater
import os
import logging
from logging.handlers import RotatingFileHandler

if not os.path.isdir('/home/pi/Dashboard/debug'):
    os.mkdir('/home/pi/Dashboard/debug')
app = Flask(__name__, static_url_path="", static_folder='dashboard')
app.zumi = Zumi()
app.screen = Screen(clear=False)
app.ssid = ''
app.action = ''
socketio = SocketIO(app)
handler = RotatingFileHandler('/home/pi/Dashboard/debug/dashboard.log', maxBytes=10000, backupCount=1)
app.logger.setLevel(logging.DEBUG)
app.logger.addHandler(handler)


def _awake():
    app.screen.hello()
    sound.wake_up_sound(app.zumi)

def log(msge):
    app.logger.info(time.strftime('{%Y-%m-%d %H:%M:%S} ')+msge)

@app.after_request
def set_response_headers(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response


# first page render (select wifi page)
@app.route('/')
@app.route('/index')
def index():
    return app.send_static_file('index.html')


@app.route('/select-network')
def select_network():
    return app.send_static_file('index.html')

@app.route('/success')
def success():
    return app.send_static_file('index.html')

@socketio.on('ssid_list')
def ssid_list(sid):
    print('getting ssid list')
    app.action = 'ssid_list'
    log('getting ssid list')

    _list = scripts.get_ssid_list()
    socketio.emit('ssid_list',str(_list))


@socketio.on('disconnect')
def test_disconnect():
    print('Socket disconnected')
    log('client disconnected')

@socketio.on('connect')
def test_connect():
    print('a client is connected')
    log('a client is connected')
    log(app.action)
    if app.action == 'check_internet':
        time.sleep(1)
        socketio.emit(app.action, app.action_payload)
        app.action = ''
        app.action_payload = ''

# confirm check internet msge was receive
@socketio.on('acknowledge_check_internet')
def acknowledge_check_internet():
     log('msge check internet was receive')
     app.action = ''

# connect wifi functions
@socketio.on('connect_wifi')
def connect_wifi(ssid, passwd):
    print('app.py : connecting wifi start')
    log('app.py : connecting wifi start')

    print(ssid)
    scripts.add_wifi(ssid, passwd)
    print("personality start")
    app.screen.draw_image_by_name("tryingtoconnect")
    sound.try_calibrate_sound(app.zumi)
    sound.try_calibrate_sound(app.zumi)
    print("personality done")
    log('app.py : connecting wifi:'+ssid+' end')
    print('app.py : connecting wifi end')


@socketio.on('check_internet')
def check_internet():
    app.action = 'check_internet'
    connected, ssid = scripts.check_wifi()
    app.ssid = ssid
    connected_to_internet = scripts.check_internet()
    if connected and "zumidashboard" in connected_to_internet:
        print('app.py: emit check internet success')
        log('app.py : emit check internet success')
        socketio.emit('check_internet', connected_to_internet)
    
    elif connected:
        print('app.py : conected to local network but not internet')
        log('app.py : conected to local network but not internet')
        socketio.emit('check_internet', 'LOCAL_NETWORK')
    else:
        print('emit fail to connect')
        log('app.py : emit fail to connect')
        app.screen.draw_text_center("Failed to connect.\n Try again.")
        socketio.emit('check_internet', '')
    app.action_payload = connected_to_internet

@socketio.on('zumi_success')
def zumi_success():
    app.screen.draw_text_center("I'm connected to \"" + app.ssid + "\"")
    sound.calibrated_sound(app.zumi)
    time.sleep(2)
    _awake()


@socketio.on('zumi_fail')
def zumi_success():
    app.screen.draw_text_center("Failed to connect.\n Try again.")


# zumi run demo and lesson event link is in frontend already
@socketio.on('activate_offline_mode')
def activate_offline_mode():
    app.screen.draw_text_center("Starting offline mode")
    subprocess.Popen(['sudo', 'killall', 'wpa_supplicant'])
    time.sleep(3)
    _awake()


@socketio.on('run_demos')
def run_demos():
    print('Run demos event from dashboard')


@socketio.on('goto_lessons')
def goto_lessons():
    print('Go to lessons event from dashboard')


# updater function and page
@app.route('/update')
def update():
    return app.send_static_file('index.html')


@socketio.on('update_firmware')
def update_firmware():
    print('update firmware from dashboard')
    print('server down soon')
    time.sleep(1)
    subprocess.run(["sudo killall -9 python3 && sudo python3 -c 'import zumidashboard.updater as update; update.run()'"], shell=True)


@socketio.on('update_content')
def update_content():
    print('update content from dashboard')
    updater.update_content(app.screen) #return True or False
    print('emit update content')
    socketio.emit('update_content')



# shutdown function and page
@app.route('/shutting-down')
def shutting_down():
    return app.send_static_file('index.html')


@socketio.on('shutdown')
def shutdown():
    app.screen.draw_text_center("Please switch off after 15 seconds.")
    scripts.shutdown()


# this is for refresh page
@app.route('/step2')
def step2():
    return app.send_static_file('index.html')

@socketio.on('battery_percent')
def battery_percent():
   socketio.emit('battery_percent',str(app.zumi.get_battery_percent()))

@app.route('/lesson')
def lesson():
    return app.send_static_file('index.html')


def firmware_updater_check(base):

    if not os.path.isdir(base+'update'):
        os.mkdir(base+'update')
    if not os.path.isfile(base+'update/update_log.txt'):
        f = open(base+'update/update_log.txt','w')
        f.close()

    try:
        update_list = os.listdir(os.path.dirname(os.path.abspath(__file__)) + '/update_scripts/')
        for line in open(base + 'update/update_log.txt'):
            update_list.remove(line.rstrip('\n'))

    except FileNotFoundError:
        update_list = []

    if len(update_list):
        firmware_updater(update_list)
        return "updated"
    else:
        return "no update"


def firmware_updater(update_list):
    f = open('/home/pi/Dashboard/update/update_log.txt', 'a')
    for version in update_list:
        p = subprocess.Popen(
            ['sudo', 'sh', os.path.dirname(os.path.abspath(__file__)) + '/update_scripts/'+version, '.'],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT)
        stdout, stderr = p.communicate()
        p.wait()
        f.write(version+"\n")



def run(_debug=False):
    if not os.path.isfile('/usr/local/lib/python3.5/dist-packages/zumidashboard/dashboard/hostname.json'):
        subprocess.run(["sudo ln -s /etc/hostname /usr/local/lib/python3.5/dist-packages/zumidashboard/dashboard/hostname.json"], shell=True)
    firmware_updater_check('/home/pi/Dashboard/')

    socketio.run(app, debug=_debug, host='0.0.0.0', port=80)


if __name__ == '__main__':
    run()
