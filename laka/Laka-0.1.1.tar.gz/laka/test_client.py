from laka import Laka


CREATE_USER_COMMAND = 101

if __name__ == "__main__":
    laka = Laka("localhost", 6379)
    request_id = laka.send(CREATE_USER_COMMAND, {"username":"olivetree"})
    response = laka.accept_response(request_id)
    print(response.json())
