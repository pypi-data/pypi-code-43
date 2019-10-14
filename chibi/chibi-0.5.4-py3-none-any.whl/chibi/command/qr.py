from chibi.command import command
from chibi.command.nmcli import connection
from chibi.file.image import Chibi_image
from chibi.madness.file import make_empty_file


def qr( *args ):
    return command( 'qrencode', *args )


def wifi( ssid, s=3, f=None ):
    if f is None:
        f = make_empty_file( '.png' )

    connection_atlas = connection.show( ssid )[ ssid ]
    T = connection_atlas[ '802-11-wireless-security.key-mgmt' ]
    if T == 'wpa-psk':
        T = 'WPA'
    data = "WIFI:S:{ssid};T:{T};P:{password};;".format(
        ssid=connection_atlas[ '802-11-wireless.ssid' ],
        password=connection_atlas[ '802-11-wireless-security.psk' ],
        T=T
    )

    qr( '-o', f, '-s', str( s ), data )
    return Chibi_image( f )
