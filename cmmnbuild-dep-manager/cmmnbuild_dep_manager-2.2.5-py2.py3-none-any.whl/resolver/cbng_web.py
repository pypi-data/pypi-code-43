import os
import requests
import sys
import tempfile
import xml.etree.ElementTree as ET
import zipfile
import logging
import shutil


class CbngWebResolver(object):
    dependency_variable = '__cmmnbuild_deps__'
    description = 'CBNG Web Service'

    @classmethod
    def is_available(cls):
        # check if CBNG web service is reachable
        try:
            requests.get('http://bewww.cern.ch/ap/', timeout=5.0)
            return True
        except:
            try:
                import platform
                hostname = platform.node()
                if 'cern.ch' in hostname:
                    logging.warning(('This appears to be a CERN machine ({0}), but CBNG is not available. Will try ' +
                                     'to resolve dependencies from public repositories, which may not work for ' +
                                     'CERN internal modules.').format(hostname))
            except:
                pass
            return False

    def __init__(self, dependencies):
        """Resolve dependencies using the CBNG web service"""
        self.log = logging.getLogger(__package__)

        valid_deps = []
        for dep in dependencies:
            if isinstance(dep, str):
                valid_deps.append({'product': dep})
            elif isinstance(dep, dict):
                valid_deps.append({str(k): str(v) for k, v in dep.items()})
            else:
                self.log.warning('IGNORING "{0}" - __cmmnbuild_deps__ must be a list of str or dict'.format(dep))

        # Generate product.xml
        cmmnbuild_dep_mgr = __package__.split('.')[0]
        pxml = ET.Element('products')
        pxml_prod = ET.SubElement(pxml, 'product', attrib={
            'name': cmmnbuild_dep_mgr,
            'version': sys.modules[cmmnbuild_dep_mgr].__version__,
            'directory': cmmnbuild_dep_mgr
        })
        pxml_deps = ET.SubElement(pxml_prod, 'dependencies')

        for dep in valid_deps:
            ET.SubElement(pxml_deps, 'dep', attrib=dep)

        # Post product.xml to CBNG web service
        self.log.info('resolving dependencies using CBNG web service: '
                      'https://wikis.cern.ch/display/DVTLS/CBNG+Web+service')

        resp = requests.post('http://bewww.cern.ch/ap/cbng-web/', {
            'action': 'get-deps',
            'product_xml': ET.tostring(pxml)
        }).json()

        if not resp['result']:
            raise Exception(resp['message'])

        self.log.info('CBNG results: {0}'.format(resp['data']['wd_url']))
        self.zip_url = resp['data']['lib_all_url']

    def save_jars(self, dir):
        # Download archive file
        self.log.info('downloading archive: {0}'.format(self.zip_url))

        with tempfile.TemporaryFile() as tmp_file:
            lib_all = requests.get(self.zip_url, stream=True)

            for chunk in lib_all.iter_content(chunk_size=1024):
                tmp_file.write(chunk)

            # Unzip jar archive
            with zipfile.ZipFile(tmp_file) as zip_file:
                for f in zip_file.namelist():
                    if os.path.dirname(f) == 'lib':
                        self.log.info('extracting {0}'.format(f))
                        source_jar = zip_file.open(f)
                        dest_jar = open(os.path.join(dir, os.path.basename(f)), 'wb')
                        with source_jar, dest_jar:
                            shutil.copyfileobj(source_jar, dest_jar)

    @classmethod
    def get_help(cls, classnames, class_info):
        for classname in classnames:
            lst = classname.split('.')
            data = {'u': 'http://artifactory.cern.ch/beco-release-local',
                    'r': '/'.join(lst),
                    'o': lst[0],
                    'a': lst[1]}
            for package, version in class_info[classname]:
                print('Info for "{0}" in "{1}" version "{2}"'.format(
                    classname, package, version
                ))
                data['v'] = version
                data['p'] = package
                url = ('JavaDoc: {u}/{o}/{a}/{p}/{v}/{p}-{v}-javadoc.jar'
                       '!/index.html?{r}.html')
                print(url.format(**data))
                url = ('Sources: {u}/{o}/{a}/{p}/{v}/{p}-{v}-sources.jar'
                       '!/{r}.java')
                print(url.format(**data))
