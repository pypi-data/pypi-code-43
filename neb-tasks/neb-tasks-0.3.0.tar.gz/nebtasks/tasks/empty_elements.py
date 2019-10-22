import click
from lxml import etree
from litezip.main import COLLECTION_NSMAP
from nebtasks.task_extensions import neb_task, NebTask

def load(cli):
    @neb_task(cli, name='empty-elements')
    @click.option('-i', '--ignore', multiple=True)
    @click.option('-n', '--ignore-ns', multiple=True)
    def empty_elements_task(ignore, ignore_ns):
        """identify location of empty elements in collection"""

        def get_ns_prefix(element):
            namespace = etree.QName(element).namespace
            if namespace == 'http://cnx.rice.edu/cnxml':
                return ''
            prefixes = filter(lambda item: item[1] == namespace, COLLECTION_NSMAP.items())
            try:
                return next(prefixes)[0]
            except IndexError:
                return ''

        def action(id, file, resources):
            tree = etree.parse(file)
            empty_elements = tree.xpath('//*[not(normalize-space())]', namespaces=COLLECTION_NSMAP)
            for element in empty_elements:
                prefix = get_ns_prefix(element)
                prefix_with_delimiter = prefix + ':' if len(prefix) > 0 else ''
                localname = etree.QName(element).localname
                if localname in ignore:
                    continue
                if prefix in ignore_ns:
                    continue
                print(f'Empty element - {id} - line {element.sourceline} - {prefix_with_delimiter}{localname}')
        return NebTask(module_action=action, collection_action=action)