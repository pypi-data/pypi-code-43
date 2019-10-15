import os
from sickdb_client import API

FIXTURE1 = os.path.abspath(os.path.join(os.path.dirname(__file__), 'space-time-motion.mp3'))
FIXTURE2 = os.path.abspath(os.path.join(os.path.dirname(__file__), 'space-time-motion.mp3'))


print("\nCONNECT TO THE API...\n")
api = API(url="http://localhost:3030/", api_key="dev", debug=True)

print("\nGETTING YOUR USER PROFILE...\n")
r = api.users.me()
print(r.json())


# print("\nCREATING FIELDS...\n")

# r = api.fields.create(name="bpm", type="int")
# print(r.json())

# r = api.fields.create(name="genre", type="text", searchable=True)
# genre = r.json()
# print(genre)

# r = api.fields.create(name="artist", type="text", searchable=True)
# artist = r.json()
# print(artist)

# r = api.fields.create(name="key", type="text")
# d = r.json()
# print(d)


# folders #


print("\nCREATING FOLDERS...\n")
r = api.folders.create(name="Sick Jams")
d = r.json()
print(d)

r = api.folders.create(name="Sick Jams 2")
d2 = r.json()
print(d2)

r = api.folders.create(name="Deep Trax")
d3 = r.json()
print(d3)

print("\nFETCH A FOLDER...\n")
r = api.folders.get(id=d["id"])
print(r.json())

print("\nSEARCH FOR FOLDERS BY A LIST OF IDS...\n")
r = api.folders.search(id=[d["id"], d2["id"]])
print(r.json())


print("\nUPDATE A FOLDER...\n")
r = api.folders.update(id=d["id"], name="Sick Jams 3")
print(r.json())


print("\nSEARCH FOR FOLDERS WITH A TEXT QUERY...\n")
r = api.folders.search(q="Deep")
print(r.json())


import random

for i in range(0, 100, 1):

    print("\nCREATE FILES...\n")
    r = api.files.create(
        file=open(FIXTURE2, "rb"),
        ext="mp3",
        name=f"jv track {i}",
        folders=[random.choice([1,2,3])],
        fields=dict(bpm=125, key="Fm", genre="disco physics", artist=f"Jennifer Vanilla-{i}", ),
    )
    print(r.json())

    print("\nCREATE FILES...\n")
    r = api.files.create(
        file=open(FIXTURE1, "rb"),
        ext="mp3",
        name=f"wb track {i}",
        folders=[random.choice([1,2,3])],
        fields=dict(bpm=130, key="Fm", genre="techno", artist=f"Well Being-{i}"),
    )
    print(r.json())

print("\nCREATING A USER...\n")
r = api.users.create(name="John", email="john@john.com", password="secur3")
d = r.json()

print("\nACCESSING THE API VIA ANOTHER USER...\n")
john_api = API(url="http://localhost:3030/", api_key=d["api_key"])
r = john_api.users.update_me(old_password="secur3", new_password="s3cur3r")

print("\nFETCHING YOUR APIKEY WITH AN email AND password...\n")
r = john_api.users.login(email="john@john.com", password="s3cur3r")
print(r.json())

print("\nGETTING ANOTHER USER...\n")
r = john_api.users.get(id=d["id"])
print(r.json())

print("\nSEARCHING USERS...\n")
r = john_api.users.search()
print(r.json())


# fields #


# files #

# print("\nCREATE FILES...\n")
# r = api.files.create(
#     file=open(FIXTURE, "rb"), fields=dict(bpm=123, key="Bbm", genre="funk")
# )
# r = api.files.create(
#     file=open(FIXTURE, "rb"), fields={"bpm": 112, "key": "Abm", "genre": "reggae"}
# )
# r = api.files.create(
#     file=open(FIXTURE, "rb"), fields={"bpm": 111, "key": "Cm", "genre": "rnb"}
# )
# d = r.json()
# print(d)

print("\nSEARCH FILES...\n")
r = api.files.search(id=[1])
print(r.json())

print("\nGET A FILE BY ITS ID...\n")
r = api.files.get(id=1)
print(r.json())

print("\nUPDATE A FILE...\n")
r = api.files.update(id=1, name="foo-bar")
print(r.json())


# print("\nADD A NEW FIELD TO A FILE...\n")
# r = api.fields.create(name="label", type="text", searchable=True)
# field = r.json()
# print(field)

# r = api.files.add_field(id=2, field_id=field["id"], value="Globally Ltd.")
# file1 = r.json()
# print(file1)

# print("\nUPDATE A FIELD FOR A FILE...\n")
# r = api.files.update_field(id=2, field_id=field["id"], value="Globally Limited")
# file2 = r.json()
# print(file2)
# assert file1["updated_at"] != file2["updated_at"]

# print("\nDELETE A FIELD FROM A FILE...\n")
# r = api.files.remove_field(id=2, field_id=field["id"])
# file3 = r.json()
# print(file3)
# assert file2["updated_at"] != file3["updated_at"]

print("\nGET INFO ABOUT THIS FILE STORE...\n")
r = api.files.get_store()
print(r.json())
# r = api.files.stream(id=2)
# print(r.headers)
# r = api.files.download(id=2)
# print(r.headers)
