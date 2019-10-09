import requests
import pandas as pd
import numpy as np

COSMOS_API_URL = 'https://521krbkm78.execute-api.us-east-1.amazonaws.com/prod'

ENDPOINTS = {
    'judge_attempt': '/judge/attempt'
}

# Messages
EMAIL_MISSING_MSG = "Please set the variable 'email' to the email you used to sign up for Cosmos."
SOLUTION_MISSING_MSG = "Seems like your solutions is 'None'. Please set the required variable to your answer and try again."

HTTPCodes = {
    # 2XX Codes
    'SUCCESS': 200,
    'RESOURCE_CREATED': 201,
    # 4XX Codes
    'BAD_REQUEST': 400,
    'UNAUTHORIZED': 401,
    'NOT_FOUND': 404,
    'METHOD_NOT_ALLOWED': 405,
    'NOT_ALLOWED': 406,
    'CONFLICT': 409,
    'PRECONDITION_FAILED': 412,
    # 5XX Codes
    'SERVER_ERROR': 500,
}

def get_endpoint(task):
    if task not in ENDPOINTS:
        return None
    return COSMOS_API_URL + ENDPOINTS[task]


class CosmosProject(object):
    def __init__(self, project_id):
        self.project_id = project_id

    def judge_attempt(self, challenge_id, email, solution):
        if not email:
            return EMAIL_MISSING_MSG
        if not solution:
            return SOLUTION_MISSING_MSG
        if isinstance(solution, (pd.Series, np.ndarray)):
            solution = list(solution)
        if not isinstance(solution, list):
            solution = [solution]
        response = requests.post(get_endpoint('judge_attempt'), json={
            "email": email,
            "projectId": self.project_id,
            "challengeId": challenge_id,
            "solution": solution
        })
        if response.status_code == HTTPCodes['RESOURCE_CREATED']:
            response_data = response.json()['data']
            if response_data['passed']:
                return f"Congratulations 🎉, you have completed the challenge! You earned {response_data['points']} points."
            else:
                return f"Oh no, seems like the solution you provided is incorrect. Please check your work and try again."
        else:
            response_errors = response.json()['errors']
            return f"Seems like something went wrong. This is what we know:\n{response_errors}\nPlease contact a volunteer if you need help with solving this issue."
