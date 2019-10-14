import requests as _requests
print("Informe o seu e-mail do Oplab")
username = input()
print("Informe o seu password do Oplab")
password = input()
url = "https://api.oplab.com.br/v2/users/authenticate"
headers = {
    "Content-Type": "application/json"}
parameters = {"email": username, "password": password}
r = _requests.post(url=url, headers=headers, params=parameters)
print(r)
rj = {}
if r.status_code == 200:
    rj = r.json()
    token = rj["access-token"]
    with open('token.json','w') as f:
        f.write(' {"token" : "' + token + '" } ')
