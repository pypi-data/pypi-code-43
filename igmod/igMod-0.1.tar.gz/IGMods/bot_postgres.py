from instapy import InstaPy

import psycopg2
import psycopg2.extras
import time


class bot_postgres():

    def __init__(self):
        pass

    def add(profile_name):
        conn = psycopg2.connect("dbname=insta user=postgres password=password")
        cur = conn.cursor()

        cur.execute("SELECT * FROM profiles WHERE name=%s", (profile_name,))

        try:
            assert cur.fetchall()[0] is not None
            print(profile_name, "already exists in databank, u want to scan if its an old user?")

        except IndexError or AssertionError:
            print("will get added:.....\n")
            cur.execute("INSERT INTO profiles(name,since) VALUES (%s,%s)",
                        (profile_name, time.strftime("%m%d%Y %H%M%S", time.gmtime())))
            conn.commit()
            print(profile_name, "is added")
        finally:
            print("Function add() is feddich:]")
            conn.close()


    def detailer(profile_name,self):
        conn = psycopg2.connect("dbname=insta user=postgres password=password")
        cur = conn.cursor()
        cur.execute("SELECT * FROM profiles WHERE name=%s", (profile_name,))
        shortbuffer = cur.fetchone()[0]
        cur.execute("SELECT * FROM detailed_accounts WHERE profile_id=%s", (shortbuffer,))

        try:                                                                                                            # new added line
            assert cur.fetchall()[0] is not None                                                                        # new added line
            print(profile_name, "already exists in databank, u want to scan if its an old user?")                       # new added line
                                                                                                                        # new added line
        except IndexError or AssertionError:                                                                            # new added line
            try:
                cur.execute("SELECT id FROM profiles WHERE name=%s", (profile_name,))
                data_insta = self.instagrammer(profile_name, "both")
                buffer = cur.fetchall()[0][0]
                print("users id found:",  buffer)
                cur.execute("INSERT INTO detailed_accounts(profile_id, followers, following) VALUES(%s, %s, %s)",
                            ([buffer][0],
                             [psycopg2.extras.Json({"data": data_insta["followers"]})],
                             [psycopg2.extras.Json({"data": data_insta["following"]})]))
                conn.commit()
                print(profile_name, "was added as a detailed one")

            except IndexError:
                print("Account doesnt exists yet...")
                if input("You would like to add user?[Y/N]\n") == ("Y"or "y"):
                    print(profile_name, "will be added")
                    self.add(profile_name)
                    self.detailer(profile_name)
                    print("New data was added:) [detailed and normal profile]")

                else:
                    print("Account wont be added..")

            finally:
                conn.close()



    def instagrammer(profile_name, request):
        session = InstaPy(username="fotopedia2000", password="CQlR+nein1_i", disable_image_load=True)
        session.set_relationship_bounds(enabled=True, max_followers=3500)
        session.login()
        if request == "following":
            buffer = session.grab_following(username=profile_name, amount="full", live_match=True, store_locally=False)
            session.end()
            return buffer
        elif request == "follwers":
            buffer = session.grab_followers(username=profile_name, amount="full", live_match=True, store_locally=False)
            session.end()
            return buffer
        elif request == "both":
            buffer1 = session.grab_following(username=profile_name, amount="full", live_match=True, store_locally=False)
            buffer2 = session.grab_followers(username=profile_name, amount="full", live_match=True, store_locally=False)
            session.end()
            return {"following": buffer1, "followers": buffer2}
        else:
            print("Cant handle your request...")


    def assholer(username,self):
        list=[]
        check=self.instagrammer("fotopedia2000","following")
        base=self.instagrammer("fotopedia2000","follwers")
        for i in check:

            if i not in list:
                if i not in base:
                    list.append(i)

        return list

hallo=bot_postgres
hallo.assholer("fotopedia2000","n")