from instapy import InstaPy
from postgres_communication import *
from bot_postgres import add, detailer
import bot_instagram
import time
#funktioniert alles, bloß private accs müssen brücksichtigt werden: das will so nd, wenn man kann eine daten hat --> new_finder kann so keine Übereinstimmungen finden..



# Funktion wird unten aufgerufen; simples Script, das jetzt spezifisch ist.
# davor müssen noch die Quaries von postgres_quaries aufgerufen werden, damit die Datenbank funtkioniert.
#wichtig ist, dass postgresql installiert ist, wenn Interesse besteht, setze ich dir den Bot gerne auf, vlt erweitere ich dir den sogar.


def pyscript_execute():
    z = 0
    while True:

        addlist = bot_instagram.new_finder(connection_minimum=3)
        print("your addlist wille be", addlist)
        time.sleep(10)
        while len(addlist) >0:
            add(addlist[-1])
            detailer(addlist[-1])
            addlist.pop()
            print("its round:", z)
            z += 1
        print("these were added:", addlist)

    print("done")



#pyscript_execute()


