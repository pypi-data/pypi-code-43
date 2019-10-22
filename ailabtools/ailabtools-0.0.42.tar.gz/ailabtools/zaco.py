import json
import time
from multiprocessing import Pool
import multiprocessing
import numpy as np
from tqdm import tqdm

def _isArrayLike(obj):
    return hasattr(obj, '__iter__') and hasattr(obj, '__len__')
    
def get_supper_item(argument):
    item, datasets, label_task_data = argument
    super_item = {}
    super_item['id'] = item['id']
    super_item['dataset_id'] = item['dataset_id']
    super_item['path'] = {}
    super_item['path']['base_path'] = datasets[item['dataset_id']]['base_path']
    super_item['path']['server_path'] = item['server_path']
    #extra-info
    super_item['annotations'] = []
    for annotation in label_task_data['annotations']:
        if annotation['data_item_id'] == item['id']:
            super_item['annotations'].append(annotation)
            
    return item['id'], super_item
    
class LabelTask:
    def __init__(self, annotation_file=None, num_worker=None):
        '''
        init label task data
        '''
        self.super_item = {}
        
        if not annotation_file == None:
            print('loading annotations into memory...')
            tic = time.time()
            label_task_data = json.load(open(annotation_file, 'r'))
            assert type(label_task_data)==dict, 'annotation file format {} not supported'.format(type(label_task_data))
            print('Done (t={:0.2f}s)'.format(time.time() - tic))
            self.label_task_data = label_task_data
            print('start create index')
            
        if num_worker == None:
            self.num_worker = multiprocessing.cpu_count()
        else:
            self.num_worker = num_worker
            
        self.createIndex()
        self.num_labeled_data = len(self.data_items)
        self.num_all_data = np.sum([self.datasets[key]['data_num'] for key in self.datasets])
        print('DONE loading ', len(self.data_items), ' items')

    def createIndex(self):
        print('index data_items')
        self.data_items = {}
        for data_item in self.label_task_data['data_items']:
            self.data_items[data_item['id']] = data_item
        
        print('index datasets')
        self.datasets = {}
        for dataset in self.label_task_data['datasets']:
            self.datasets[dataset['id']] = dataset
            
        print('index classes')
        self.classes = {}
        for c in self.label_task_data['classes']:
            self.classes[c['id']] = c
            
        print('index anotations')
        self.anotations = {}
        for annotation in self.label_task_data['annotations']:
            self.anotations[annotation['id']] = annotation
        
        print('index items')
        arguments = []
        for item in self.label_task_data['data_items']:
            arguments.append((item, self.datasets, self.label_task_data))
        
        print('Pool start!')
        s = time.time()
        with Pool(self.num_worker) as p:
            id_super_item = p.map(get_supper_item, arguments)
        e = time.time()
        print('Pool:', e - s)
    
        for item in id_super_item:
            _id, super_item = item
            self.super_item[_id] = super_item
        
        self.info = self.label_task_data['info']
        print('index created!')
   
    def show_info(self):
        '''
        show info of lable task
        '''
        print('LABEL TASK INFO:')
        for key, value in self.label_task_data['info'].items():
            print('{}: {}'.format(key, value))
        print()
        print()
        print('DATASETS INFO:')
        for item in self.label_task_data['datasets']:
            for key, value in item.items():
                print('{}: {}'.format(key, value))
            print()
        print()
        print('CLASSES INFO:')
        for item in self.label_task_data['classes']:
            for key, value in item.items():
                print('{}: {}'.format(key, value))
            print()

    def convert2COCO(self):
        '''
        convert LabelTask info to COCO format for eval model
        '''
        pass
    
    
    def get_item_ids(self, dataset_ids=[], class_ids=[], rating=-1):
        '''
        return item ids belong to (dataset_ids AND class_ids)
        '''
        def intersection(lst1, lst2): 
            return set(lst1).intersection(lst2) 

        class_ids = class_ids if _isArrayLike(class_ids) else [class_ids]
        dataset_ids = dataset_ids if _isArrayLike(dataset_ids) else [dataset_ids]

        item_ids = [key for key in self.super_item]
        
        filted_ids = []
        for item_id in item_ids:
            
            get_flag = True

            if dataset_ids:
                if self.super_item[item_id]['dataset_id'] not in dataset_ids:
                    continue
            
            if class_ids:
                item_classes = [ann['class_id'] for ann in self.super_item[item_id]['annotations']]
                if len(intersection(item_classes, class_ids)) == 0:
                    get_flag = False

            if get_flag:
                filted_ids.append(item_id)
                    
        return filted_ids  

    def get_items(self, item_ids):
        '''
        get item by item_id
        '''
        with Pool(self.num_worker) as p:
            res = p.map(self.super_item.__getitem__, item_ids)
        return res
        
    def get_path_by_id(self, item_id):
        item = self.super_item[item_id]
        return get_path_by_item(self, item)
    
    def get_path_by_item(self, item):
        pre_path = 'https://label.lab.zalo.ai/label/database'
        base_path = item['path']['base_path']
        server_path = item['path']['server_path']
        full_path = '{}/{}/{}'.format(pre_path, base_path, server_path)
        return full_path
    
    def get_path_items(self, item_ids):
        with Pool(self.num_worker) as p:
            res = p.map(self.get_path_by_item, item_ids)
        return res
    
    def get_class(self, item_id):
        return self.super_item[item_id]['annotations'][0]['class_id']
    
    def get_class_items(self, item_ids):
        with Pool(self.num_worker) as p:
            res = p.map(self.get_class, item_ids)
        return res
    
    def get_ann_ids(self, item_ids=[], class_ids=[]):
        '''
        get annotation ids by (item_ids AND class_ids)
        '''
        def condition(annotation, _item_ids, _class_ids):
            res = True
            if len(_item_ids) > 0:
                res = res and annotation['data_item_id'] in _item_ids
            if len(_class_ids) > 0:
                res = res and annotation['class_id'] in _class_ids
            return res
        return [ann['id'] for ann in self.label_task_data['annotations'] if condition(ann, item_ids, class_ids)]
            

    def get_ann(self, ann_ids):
        '''
        load full annotation info
        '''
        return [self.anotations[ann_id] for ann_id in ann_ids]

    def show_ann(self, ann):
        '''
        show anno tation
        '''
        pass
        