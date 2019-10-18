
def rest_code(okex_code , func_code=None):

    if not okex_code:
        return 0
    if okex_code in [ 30037 ] :
        return 100
    elif okex_code in [30001,30002,30003,30004,30005,30006,30007,30008 ] :
        return 200
    elif okex_code in [30010,30011,30012,30013 ,30015,30016,30017,30018,30027,30028,30029] :
        return 300
    elif okex_code in [30020,30021,30022,30023,30024,30025 ] :
        return 400
    elif okex_code in [30009,30035 ] :
        return 500
    elif okex_code in [30014,30026,30030] :
        return 600  

    elif okex_code in []:
        return 10000
    elif okex_code in []:
        return 20000
    elif okex_code in []:
        return 30000
    elif okex_code in [30031,30032,33013,33017,33024,33028,33029]:
        return 30100
    elif okex_code in [30031,30032,33013,33015,33017,33024,33028,33029]:
        return 30200
    elif okex_code in [30031,30032,33013,33017,33024,33028,33029]:
        return 30300
    elif okex_code in [30031,30032,33013,33015,33017,33024,33028,33029]:
        return 30400

    elif func_code == 40500 and okex_code in [33014]:
        return 40502

    elif func_code == 40600 and okex_code in [33014]:
        return 40602

    else :
        return 900

def ws_code(okex_code):

    if not okex_code:
        return 0
    if okex_code in [ ] :
        return 100
    elif okex_code in [ 10003]:
        return 102
    elif okex_code in [ 10000,10001,10008 ] :
        return 200
    elif okex_code in [ 10002,10005] :
        return 300
    elif okex_code in [ ] :
        return 400
    elif okex_code in [ ] :
        return 500
    elif okex_code in [ ] :
        return 600  

    elif okex_code in []:
        return 10000
    elif okex_code in [10012]:
        return 10101
    elif okex_code in [10012]:
        return 10201
    elif okex_code in [10012]:
        return 10301
    elif okex_code in []:
        return 20000
    elif okex_code in [10012]:
        return 20101
    elif okex_code in [10012]:
        return 20201
    elif okex_code in [10012]:
        return 20301

    
    elif okex_code in [ ]:
        return 30000
    elif okex_code in [  10014 ,1027 ]:
        return 30100
    elif okex_code in [ 10012 ]:
        return 30101
    elif okex_code in [ 10010  ,1002  ]:
        return 30102
    elif okex_code in [ 10011,1003,1004 ]:
        return 30103
    elif okex_code in [  10014,1004 ,1027 ]:
        return 30200
    elif okex_code in [ 10012 ]:
        return 30201
    elif okex_code in [10010,1002 ]:
        return 30202
    elif okex_code in [10011,1003,1004]:
        return 30203
    elif okex_code in [10009,1009 ]:
        return 30301
    elif okex_code in [1010 ]:
        return 30302
    else :
        return 900
