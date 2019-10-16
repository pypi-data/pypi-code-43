from graphqlclient import GraphQLClient, json
import requests
import os

from anna_client import graphql


class Client(GraphQLClient):
	"""
	Wrapper around GraphQLClient
	"""

	def __init__(self, endpoint, task_service_url='https://task.annahub.dev/'):
		super().__init__(endpoint)
		self.task_service_url = task_service_url
		if 'ANNA_TOKEN' in os.environ:
			super().inject_token(os.environ['ANNA_TOKEN'])

	def query(self, query: str, variables: str) -> list:
		return json.loads(super().execute(query=query, variables=variables))

	def get_jobs(self, where: dict = None, fields: tuple = ('id',), limit: int = 0) -> list:
		if where is None:
			where = {}
		query = graphql.get_jobs_query(where=where, fields=fields, limit=limit)
		response = super().execute(query=query)
		response = json.loads(response)
		if 'jobs' in response:
			return response['jobs']
		return response

	def create_jobs(self, data: list) -> tuple:
		ids = []
		for mutation in graphql.get_create_mutations(data):
			response = json.loads(super().execute(mutation))
			if 'createJob' in response and 'id' in response['createJob']:
				ids.append(response['createJob']['id'])
		return tuple(ids)

	def delete_jobs(self, where: dict = None) -> tuple:
		if where is None:
			where = {}
		mutation = graphql.get_delete_mutation(where=where)
		response = json.loads(super().execute(mutation))
		return response

	def update_jobs(self, where: dict = None, data: dict = None) -> tuple:
		mutation = graphql.get_update_mutation(where=where, data=data)
		response = json.loads(super().execute(mutation))
		return response

	def reserve_jobs(self, worker: str, job_ids: tuple):
		mutation = graphql.get_reserve_jobs_mutation(worker=worker, job_ids=job_ids)
		response = json.loads(super().execute(mutation))
		return response

	def get_tasks(self, namespace: str) -> tuple:
		url = self.task_service_url + '?namespace=' + namespace
		headers = {'authorization': self.token}
		response = requests.get(url=url, headers=headers)
		if response.status_code is not 200:
			raise ValueError(response.text)
		response = json.loads(response.text)
		if len(response) is not 2:
			raise ValueError
		return response[0], response[1]
