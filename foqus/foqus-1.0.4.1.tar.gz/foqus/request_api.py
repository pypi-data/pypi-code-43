import requests, json

from foqus.configuration import *
headers = {"Content-Type": "application/json", 'Authorization': SECRET_KEY}


class APIFoqus:

    def apipost(self, post_fonction, customer_name, customer_type, project, file_path=None, customer_universe=None, url_shop=None, input_seesion_id=None):
        if post_fonction == 'retrieve_images_json':
            response = requests.post(url="http://0.0.0.0:8001/api/train/" + post_fonction,
                                     json={"customer_name": customer_name,
                                           "customer_type": customer_type,
                                           "project_name": project,
                                           "url_file": file_path},
                                     headers=headers)

        elif post_fonction == 'training_similars':

            response = requests.post(url="http://0.0.0.0:8001/api/train/" + post_fonction,
                                        json={"customer_name": customer_name,
                                              "customer_type": customer_type,
                                              "project_name": project},
                                        headers=headers)

        elif post_fonction == "training_classification":
            response = requests.post(url="http://0.0.0.0:8001/api/train/" + post_fonction,
                                        json={"customer_name": customer_name,
                                              "customer_type": customer_type,
                                              "project_name": project,
                                              "customer_universe": customer_universe,
                                              "url_file": file_path},
                                        headers=headers)

        elif post_fonction == "training_text_detection":
            response = requests.post(url="http://0.0.0.0:8001/api/train/" + post_fonction,
                                     json={"customer_name": customer_name,
                                              "customer_type": customer_type,
                                              "project_name": project,
                                              "customer_universe": customer_universe,
                                              "url_file": file_path},
                                     headers=headers)

            response_text = json.loads(response.text)
            result = response_text['status']
            if result == 'True':
                response = requests.post(url="http://0.0.0.0:8001/api/train/training_image",
                                         json={"customer_name": customer_name,
                                              "customer_type": customer_type,
                                              "customer_universe": customer_universe},
                                         headers=headers)

        elif post_fonction == "shopify_training":
            response = requests.post(url="http://0.0.0.0:8001/api/train/" + post_fonction,
                                     json={"customer_name": customer_name,
                                           "customer_type": customer_type,
                                           "project_name": customer_universe,
                                           "url_shop": url_shop,
                                           "input_session_id": input_seesion_id},
                                     headers=headers)
        elif post_fonction == "correction_training":
            response = requests.post(url="http://0.0.0.0:8001/api/train/" + post_fonction,
                                     json={"customer_name": customer_name,
                                           "customer_type": customer_type,
                                           "project_name": project,
                                           "customer_universe": customer_universe,
                                           "url_file": file_path},
                                     headers=headers)

        else:
            response = None

        return response

    def apiget(self, post_fonction, customer_name, customer_type, project, url):
        if post_fonction == 'get_similars':

            response = requests.post(url="http://0.0.0.0:8001/api/similars/" + post_fonction,
                                        json={"customer_name": customer_name,
                                              "customer_type": customer_type,
                                              "project_name": project,
                                              "url_image": url},
                                        headers=headers)
            return response.text
        elif post_fonction == 'get_category':
            response = requests.post(url="http://0.0.0.0:8001/api/predict/" + post_fonction,
                                         json={"customer_name": customer_name,
                                               "customer_type": customer_type,
                                               "project_name": project,
                                               "url_image": url},
                                         headers=headers)
            return response.text
        elif post_fonction == 'predict_customer':
            response = requests.post(url="http://0.0.0.0:8001/api/predict/" + post_fonction,
                                         json={"customer_name": customer_name,
                                               "customer_type": customer_type,
                                               "customer_universe": project,
                                               "url_file": url},
                                         headers=headers)
            result = json.loads(response.text)
            return result['response']
        return None