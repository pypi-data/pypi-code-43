import psycopg2
import json
import random

conn = psycopg2.connect("dbname=insta user=postgres password=password")
c = conn.cursor()


def numberfinder(numbers, sqllimit=0):
    numberlist = []
    print("limit:", sqllimit)
    print(sqllimit, "accs are already in databank")
    while len(numberlist) < numbers:
        x = random.randint(0, sqllimit - 15) + 33 #pluss 33, weil ich davor schon davor Daten drin hatte, ohne diese zu löschen bzw wieder zu überschreiben..
        if x not in numberlist:
            numberlist.append(x)
    return numberlist


def new_finder(connection_minimum=3, prefered_user=[]):
    newfinderlistbuffer = []
    newfinderlist = []
    try:
        print("succesfully entered new_finder")
        if len(prefered_user) < 1:
            print("you used the simple way")
            c.execute("SELECT COUNT(id) FROM profiles")
            numberlist = numberfinder(connection_minimum, sqllimit=c.fetchall()[0][0])
            print(numberlist)
            for number in numberlist:
                conn.rollback()
                c.execute("SELECT followers FROM detailed_accounts WHERE profile_id=%s", (number,))
                data = c.fetchall()
                print("unproceddata_",data)
                data = json.loads(data[0][0][0])
                print("data is:", data)
                newfinderlistbuffer.append(data["data"])
                print("listbuffer",newfinderlistbuffer)
            print("the simple way worked")
        else:

            for user in prefered_user:
                c.execute("SELECT id FROM profiles WHERE name = %s", (user,))
                buffer_id = c.fetchall()
                print(buffer_id)
                buffer_id = buffer_id[0][0]
                c.execute("SELECT followers FROM detailed_accounts WHERE profile_id=%s", (buffer_id,))
                data = json.loads(c.fetchall()[0][0][0])
                newfinderlistbuffer.append(data["data"])

        kbuffer = []
        for z in range(0, len(newfinderlistbuffer)):
            print("hehehe", z)
            for x in newfinderlistbuffer[z]:
                kbuffer.append(x)
        for x in newfinderlistbuffer[0]:
            if kbuffer.count(x) >= len(newfinderlistbuffer):
                newfinderlist.append(x)

        return newfinderlist
    except IndexError:
        print("hope u just started ur code") #ich hab keine Ahnung mehr, aber da war mal ein Error


print(new_finder(prefered_user=[]))

#irgendwelche Nutzernamen in die Liste eintragen