from requests import post


def login(url, username, password):
    data = {"username": username, "password": password}
    return post(url=url, data=data)
