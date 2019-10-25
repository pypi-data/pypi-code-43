class WebError(Exception):
    def __init__(self, status_code, response_text):
        print("WebError:", status_code, "returned with message:", response_text)
