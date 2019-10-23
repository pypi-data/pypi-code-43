import json
from xmljson import parker
from xml.etree.ElementTree import fromstring

def keep_keys(old_dict):
	new_dict = {}
	for key in old_dict:
		if key in ["object","segmented","size"]:
			new_dict[key]=old_dict[key]
	return new_dict

def annotation_xml_to_json(xml_file):
	f = open(xml_file, "rb")
	json_dict = keep_keys(parker.data(fromstring(f.read())))
	if not "object" in json_dict:
		json_dict = {"object": {}}
	json_output = json.dumps(json_dict["object"])
	f.close()
	return json_output

def process_annotations(image_name, annotation_path):
	if annotation_path.endswith('.json'):
		json_data = open(annotation_path, 'r').read()
	elif annotation_path.endswith('.xml'):
		json_data = annotation_xml_to_json(annotation_path)
	annotation = {"filename": image_name, 
		      "object": json.loads(json_data)}
	return annotation	

def read_prediction_response(response_list, model):
	if model == 'ImageCategorization' or model == 'MultiLabelClassification':
		file_key = 'file'
	else:
		file_key = 'input'
	if len(response_list) > 1:
		resp = [x.json() for x in response_list]
		res = [x['result'] for x in resp]
		file = [y[file_key] for x in res for y in x]
		pred = [y['prediction'] for x in res for y in x]
		final = dict(zip(file, pred))
	else:
		resp = response_list[0].json()
		res = resp['result']
		file = [x[file_key] for x in res]
		pred = [x['prediction'] for x in res]
		final = dict(zip(file, pred))
	return final
