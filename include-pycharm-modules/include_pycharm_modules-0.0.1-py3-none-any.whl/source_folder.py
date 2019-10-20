import os
import sys
import logging
from bs4 import BeautifulSoup

log = logging.getLogger(__name__)


# generically add all pycharm source folders to the search path
def import_source_folders(path: str):
    idea_path = os.path.join(path, ".idea/")
    for file in os.listdir(idea_path):
        if file.endswith(".iml"):
            file = os.path.join(idea_path, file)
            page = open(file)
            soup = BeautifulSoup(page.read(), 'lxml')

            for source_folder in soup.find_all('sourcefolder'):
                source = os.path.basename(source_folder['url'])
                if source == "modules":
                    continue

                module_path = os.path.join(path, source)
                if os.path.exists(module_path):
                    print(f"adding module {module_path}")
                    log.info(f"adding module {module_path}")
                    sys.path.append(module_path)
