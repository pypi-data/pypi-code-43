from typing import Union

STATUS = ('PENDING', 'RESERVED', 'STARTING', 'RUNNING', 'DONE', 'ERROR', 'FAILED', 'STOPPED')


def get_create_mutations(data: list) -> str:
	if len(data) <= 0:
		raise TypeError('provide at least one dict with a driver & a site')
	for mutation in data:
		if not isinstance(mutation, dict):
			raise TypeError('parameter data must be a list of dicts')
		if 'site' not in mutation or 'driver' not in mutation or not isinstance(mutation['site'], str) \
				or not isinstance(mutation['driver'], str):
			raise TypeError('you must specify a driver & a site')
	for mutation in data:
		parts = ','.join(list(get_key_val_str(key=key, val=val) for key, val in mutation.items()))
		for status in STATUS:
			parts = parts.replace('"' + status + '"', status)
		mutation = 'mutation{createJob(data:{' + parts + '}){id}}'
		yield mutation


def get_key_val_str(key: str, val: Union[tuple, list, str, int]) -> str:
	if not isinstance(key, str):
		raise TypeError('key must be a string')
	if isinstance(val, str) and ',' in val:
		val = val.split(',')
	if isinstance(val, str):
		return key + ':"' + val + '"'
	elif isinstance(val, tuple) or isinstance(val, list):
		if not key.endswith('in'):
			return key + '_in:["' + '","'.join(val) + '"]'
		return key + ':["' + '","'.join(val) + '"]'
	elif isinstance(val, int):
		return key + ':' + str(val)
	else:
		raise TypeError('val must be a tuple, list, int or string')


def get_jobs_query(where: dict, fields: tuple, limit: int = 0) -> str:
	parts = (get_key_val_str(key=key, val=val) for key, val in where.items())
	where = '{' + ','.join(parts) + '}'
	for status in STATUS:
		where = where.replace('"' + status + '"', status)
	if limit > 0:
		where += ' first:' + str(limit)
	return '{jobs(where:' + where + '){' + ','.join(fields) + '}}'


def get_jobs_query_(where: dict, fields: tuple, limit: int = 0) -> str:
	parts = (get_key_val_str(key=key, val=val) for key, val in where.items())
	where = '{' + ','.join(parts) + '}'
	for status in STATUS:
		where = where.replace('"' + status + '"', status)
	if limit > 0:
		where += ' first:' + str(limit)
	return '{jobs(where:' + where + '){' + ','.join(fields) + '}}'


def get_delete_mutation(where: dict = None) -> str:
	if where is None:
		where = {}
	parts = (get_key_val_str(key=key, val=val) for key, val in where.items())
	where = '{' + ','.join(parts) + '}'
	for status in STATUS:
		where = where.replace('"' + status + '"', status)
	return 'mutation{deleteManyJobs(where:' + where + '){count}}'


def get_update_mutation(where: dict = None, data: dict = None) -> str:
	parts = (
		tuple(get_key_val_str(key=key, val=val) for key, val in where.items()),
		tuple(get_key_val_str(key=key, val=val) for key, val in data.items())
	)
	where = '{' + ','.join(parts[0]) + '}'
	data = str('{' + ','.join(parts[1]) + '}')
	for status in STATUS:
		data = data.replace('"' + status + '"', status)
	return 'mutation{updateManyJobs(where:' + where + ',data:' + data + '){count}}'


def get_reserve_jobs_mutation(worker: str, job_ids: tuple) -> str:
	if worker is None or worker == '' or len(job_ids) < 1:
		raise TypeError('supply a worker and list of job ids')
	return 'mutation{updateManyJobs(where:{id_in:["' + '","'.join(
		job_ids) + '"],worker:null,status:PENDING},data:{worker:"' + worker + '",status:RESERVED}){count}}'
