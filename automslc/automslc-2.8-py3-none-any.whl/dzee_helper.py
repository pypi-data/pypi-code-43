
import deezer as deezer
import requests, json, os, re

from deezer import request

localdir = os.getcwd()
headers = {'content-type': 'application/json',
               'Authorization': 'Token bb1131f893f91f1bf5461285b26c0b622d21a37e'}
def crawl_auto(gmail, password, arl, sv, ip, output):
    dez = deezer.Login(gmail, password, arl)
    tracks = requests.get("http://54.39.49.17:8031/api/tracks/?status=0&sv={}".format(sv)).json()['results']
    for track in tracks:
        print("Update Status audio: " + str(track['deezer_id']) + " - " + track['title'] + " - " + track['artist'])
        track['status'] = True
        try:
            requests.put("http://54.39.49.17:8031/api/tracks/{}/".format(track['id']),
                         data=json.dumps(track), headers=headers)
        except:
            requests.put("http://54.39.49.17:8031/api/tracks/{}/".format(track['id']),
                         data=json.dumps(track), headers=headers)
            pass

    for track in tracks:
        try:
            print("crawl audio: " + str(track['deezer_id']) + " - " + track['title'] + " - " + track['artist'])
            track['status'] = True
            track = dez.download(track['deezer_id'], track,ip, output)
            if (os.path.exists(track['url_128'])):
                track['error_code'] = 0
            else:
                track['error_code'] = 1
            try:
                requests.put("http://54.39.49.17:8031/api/tracks/{}/".format(track['id']),
                             data=json.dumps(track), headers=headers)
            except:
                requests.put("http://54.39.49.17:8031/api/tracks/{}/".format(track['id']),
                             data=json.dumps(track), headers=headers)
                pass
        except Exception as e:
            print("error Download:" + str(e))
            pass
def find_audio(deezer_id):
    tracks = requests.get("http://54.39.49.17:8031/api/tracks/?deezer_id={}".format(deezer_id)).json()['results']
    return tracks
def get_info(deezer_id,ip,output,quality):
    dez = deezer.Login("getmoneykhmt5@gmail.com", "asd123a@", "4b9ad4a420bedb7ac4002b7e49c3a875dcf0277b9b96d09138fbc58d8d49623d677a20ce84ffdfeae5a51ff205349c16d74249c525a7ca5990bae94ff5dbf1743b1df41629417e9ba548ac8526f5c40a8d22b87900f17024bd3c73eb3d58046c")
    track={}
    track_j=requests.get("https://api.deezer.com/track/"+deezer_id).json()
    track['deezer_id']=track_j['id']
    track['title']=track_j['title'][:255]
    track['title_short'] = track_j['title_short'][:255]
    track['isrc'] =  track_j['isrc']
    track['duration'] = track_j['duration']
    track['rank'] = track_j['rank']
    track['explicit_lyrics'] = track_j['explicit_lyrics']
    track['status']=1
    track['artist']= track_j['artist']['name']
    track = dez.download(track['deezer_id'], track, ip, output,quality)
    track['error_code'] = 0
    track['status'] = 1
    try:
        requests.post("http://54.39.49.17:8031/api/tracks/",
                     data=json.dumps(track), headers=headers)
    except:
        requests.post("http://54.39.49.17:8031/api/tracks/",
                      data=json.dumps(track), headers=headers)
    return track

def get_audio(deezer_id,ip,output,quality,force):
    tracks = find_audio(deezer_id)
    if len(tracks) == 0:
        print(json.dumps(get_info(deezer_id, ip, output,quality)))
    else:
        track = tracks[0]
        if track['url_128'] == None or force:
            if force:
                dataD={}
                dataD['paths']=[track['url_128'],track['url_320'],track['url_flac']]
                requests.post(re.findall(r'http:\/\/[\d\.]+\/',track['url_128'])[0]+"clientMusic/delete_music.php",
                      data=json.dumps(dataD), headers=headers)
            dez = deezer.Login("getmoneykhmt5@gmail.com", "asd123a@", "4b9ad4a420bedb7ac4002b7e49c3a875dcf0277b9b96d09138fbc58d8d49623d677a20ce84ffdfeae5a51ff205349c16d74249c525a7ca5990bae94ff5dbf1743b1df41629417e9ba548ac8526f5c40a8d22b87900f17024bd3c73eb3d58046c")
            track = dez.download(track['deezer_id'], track, ip, output,quality)
            track['error_code'] = 0
            track['status'] = 1
            try:
                requests.put("http://54.39.49.17:8031/api/tracks/{}/".format(track['id']),
                             data=json.dumps(track), headers=headers)
            except:
                requests.put("http://54.39.49.17:8031/api/tracks/{}/".format(track['id']),
                             data=json.dumps(track), headers=headers)
        print(json.dumps(track))




