import json, os, requests, argparse

def login(host, email, password):
    try:
        tenantsList = []
        user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36"
        loginURL="https://%s/mobile/global/login.action?appType=0&_vs=4.1.1&source=1"%host
        #login
        loginRes=requests.post(url=loginURL,data={'passport':email,'password':password,'remeber':'true'},headers={'Content-Type':'application/x-www-form-urlencoded','User-Agent':user_agent})
        if "head" in loginRes.json():
            head = loginRes.json()["head"]
            tenantsList.append({'name': head.get("company")})
            return tenantsList
        else:
            tenants=loginRes.json()["body"]["tenants"]
            for tenant in tenants:
                tenantsList.append({'name':tenant.get("name")})
            return tenantsList
    except:
        return tenantsList 
