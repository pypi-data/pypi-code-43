import subprocess
from instapy import InstaPy
import json

#völlig irrelevant


session = InstaPy(username="user", password="password")  #Nuterdaten von Instagram
session.set_relationship_bounds(enabled=True, max_followers=3500)
session.login()

x=session.grab_following(username="", amount="full", live_match=True, store_locally=False)
print(json.dumps(x))

print(x)
print("done")
