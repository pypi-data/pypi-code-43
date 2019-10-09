model_mapping = {
    'mappings': {
        'properties': {
            'id': {
                'type': 'keyword',
                'ignore_above': 128,
                'index': True
            },
            'timestamp': {
                'type': 'date',
                'format': 'epoch_millis',
                'index': True
            },
            'algorithm': {
                'type': 'keyword',
                'ignore_above': 64,
            },
            'model_file': {
                'type': 'keyword',
                'ignore_above': 64,
            },
            'scaler_file': {
                'type': 'keyword',
                'ignore_above': 64,
            },
            'metadata': {
                'type': 'object',
            },
            'labelencoder': {
                'type': 'object'
            },
            'model_params': {
                "type" : "object" ,
                "properties" : {
                    "data_type" : {
                        "type" : "keyword"
                    },
                    "num_previous_measures" : {
                        "type" : "keyword"
                    },
                    "num_forecasts" : {
                        "type" : "keyword"
                    },
                    "time_index" : {
                        "type" : "keyword"
                    },
                    "inference_features" : {
                        "type" : "keyword"
                    },
                    "dataset_features" : {
                        "type" : "keyword"
                    }
                }
            }
        }
    }
}

predictions_mapping = {
    "mappings": {
        "properties": {
            "model_file": {
                "type": "text",
                "fields": {
                    "keyword": {
                        "type": "keyword",
                        "ignore_above": 256
                    }
                }
            },
            "algorithm": {
                "type": "text",
                "fields": {
                    "keyword": {
                        "type": "keyword",
                        "ignore_above": 256
                    }
                }
            },
            "id": {
                "type": "text",
                "fields": {
                    "keyword": {
                        "type": "keyword",
                        "ignore_above": 256
                    }
                }
            },
            "prediction_times": {
                "type": "date"
            },
            'timestamp': {
                'type': 'date',
                'index': True
            },
            "values": {
                "type": "object"
            },
            "latency": {
                "type": "float"
            }
        }
    }
}

classifications_mapping = {
    "mappings": {
        "properties": {
           "model_file": {
                "type": "text",
                "fields": {
                    "keyword": {
                        "type": "keyword",
                        "ignore_above": 256
                    }
                }
            },
            "algorithm": {
                "type": "text",
                "fields": {
                    "keyword": {
                        "type": "keyword",
                        "ignore_above": 256
                    }
                }
            },
            "id": {
                "type": "text",
                "fields": {
                    "keyword": {
                        "type": "keyword",
                        "ignore_above": 256
                    }
                }
            }, 
            "class": {
                "type": "text"
            },
            "confidence": {
                "type": "float"
            },
            "latency": {
                "type": "float"
            }
        }
    }

}
