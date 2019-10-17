import json
import os
import sys
json_dir={}	
abs_path = os.path.dirname(os.path.abspath(__file__))
for filename in os.listdir(abs_path):
		if filename.endswith(".json"):
			file_path = os.path.join(abs_path,filename)
			try:
				with open(file_path) as f:
					object_name = os.path.splitext(filename)[0]
					json_dir[object_name] = json.load(f)
			except Exception as e:
				print("%s json format is error!"%filename)
				print(e)
				sys.exit(1)

Schema_json = type("Schema_json",(),json_dir)
#print(Schema_json.Custom)
#print(Schema_json.Preset_Algorithm)
#print(Schema_json.Basic_Framework)
