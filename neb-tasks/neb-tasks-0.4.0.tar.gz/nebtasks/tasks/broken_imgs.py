import os

from lxml import etree
from litezip.main import COLLECTION_NSMAP
from nebtasks.task_extensions import neb_task, NebTask

def load(cli):
    @neb_task(cli, name='broken-imgs')
    def broken_images_task():
        """Find unused/missing images in a collection"""
        def module_action(id, file, resources):
            resource_basenames = list(map(lambda path: os.path.basename(path), resources))
            tree = etree.parse(file)
            content_srcs = tree.xpath('//c:image/@src', namespaces=COLLECTION_NSMAP)
            print(f'module {id}')
            for src in content_srcs:
                if not src in resource_basenames:
                    print(f'Missing {src} in module {id}')
            for resource_name in resource_basenames:
                if not resource_name in content_srcs:
                    print(f'Unused img {resource_name} in module {id}')
            print('-----')

        return NebTask(module_action=module_action)
