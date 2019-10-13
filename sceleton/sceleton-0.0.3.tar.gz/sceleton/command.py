import os
import sys
import json
import re

from .structure.user import user
from .structure.project import project, classifier, package, setup_py, readme, license


classifier.init()


def exec(*args, **kwargs):

    args = list(args)
    command = args[1]
    args.remove(command)
    sub_options = args

    current_path = os.getcwd()

    version = '0.0.1'
    if 'new' == command:
        project_path = current_path

        if os.path.exists(os.path.join(project_path, kwargs['project_name'])):
            raise FileExistsError('File with name {} already exist.'.format(kwargs['project_name']))

        virtual_env = True if '--venv' in sub_options or '--virtualenv' in sub_options else False

        if '--django' in sub_options:

            license_type = user.license()
            if license_type:
                license_type = classifier.LICENSES[int(license_type) - 1].split('::')[-1].strip()

            project.init(version=version,
                         create_django_project=True,
                         project_path=project_path,
                         project_name=kwargs['project_name'],
                         license_type=license_type,
                         set_virtual_env=virtual_env)

        elif '--quick' in sub_options:
            project.init(project_path=project_path,
                         project_name=kwargs['project_name'],
                         version=version, set_virtual_env=virtual_env)
        else:
            version, description, author_name, author_email, project_url, \
                keywords, packages, \
                development_status, environment, framework, auidence, license_type, \
                language, operating_sys, programming_language, topic = user.init()

            classifiers = classifier.format(development_status=development_status,
                                            environment=environment, framework=framework,
                                            auidence=auidence, license=license_type,
                                            language=language, operating_sys=operating_sys,
                                            programming_language=programming_language, 
                                            topic=topic)

            if license_type:
                license_type = classifier.LICENSES[int(license_type) - 1].split('::')[-1].strip()

            project.init(project_path=project_path, project_name=kwargs['project_name'], 
                         version=version, author_email=author_email,
                         description=description, author_name=author_name, 
                         license_type=license_type, classifiers=classifiers, 
                         keywords=keywords, project_url=project_url,
                         packages=packages, set_virtual_env=virtual_env)

    elif 'init' == command:
        path = kwargs['--path'] or os.getcwd()

        if os.path.exists(path) and 'setup.py' in os.listdir(path):
            answer = input("There is another `setup.py` file in {}.\nDo you really want to replace it with a new `setup.py` file? [yN]: " \
                            .format(path))

            if answer.lower() != 'y' and answer.lower() != 'yes':
                return

        if '--quick' in sub_options:
            project.new_setup_py(project_path=path, version=version, license='MIT License')
        else:
            version, description, author_name, author_email, project_url, \
                keywords, packages, \
                development_status, environment, framework, auidence, license_type, \
                language, operating_sys, programming_language, topic = user.init()

            classifiers = classifier.format(development_status=development_status,
                                            environment=environment, framework=framework,
                                            auidence=auidence, license=license_type,
                                            language=language, operating_sys=operating_sys,
                                            programming_language=programming_language, 
                                            topic=topic)

            if license_type:
                license_type = classifier.LICENSES[int(license) - 1].split('::')[-1].strip()

            project.new_setup_py(project_path=path, version=version, author_email=author_email,
                                 author_name=author_name, description=description,
                                 license_type=license_type, classifiers=classifiers, 
                                 keywords=keywords, project_url=project_url,
                                 packages=packages)

    elif 'module' == command:

        module = os.path.join(current_path, current_path.split(os.sep)[-1])

        if kwargs['parent_module']:
            parent_module = kwargs['parent_module']
            for subdir, _, _ in os.walk(module):
                if parent_module in subdir:
                    parent_module = subdir
                    break
        else:
            parent_module = module

        if '--add' in sub_options:
            project.module(current_path, kwargs['module_name'], parent_module=parent_module, files=kwargs['selected_files'])
        else:
            project.module(current_path, kwargs['module_name'], parent_module=parent_module)

    elif 'install' == command:

        if 'packages' in kwargs:
            packages = kwargs['packages']

            if not '--no-add' in sub_options:
                setup_py.packages(option='add', package_names=packages, project_path=current_path)
        else:
            packages, _ = setup_py.get(type_field='install_requires', project_path=current_path)
            
            regex = re.compile('\[.*\]')
            packages = regex.findall(packages)[0]\
                            .replace("'", "*") \
                            .replace("\"", "'") \
                            .replace("*", "\"")
            packages = json.loads(packages)

        package.install(packages)

    elif 'add' == command:

        setup_py.packages(option='add', package_names=kwargs['packages'],
                          project_path=current_path)

    elif 'remove' == command:

        setup_py.packages(option='remove', package_names=kwargs['packages'], 
                          project_path=current_path)

    elif 'user' == command:

        author = 'author'
        email = 'author_email'

        author_name, author_index = setup_py.get(type_field=author, project_path=current_path)
        author_email, email_index = setup_py.get(type_field=email, project_path=current_path)

        sys.stdout.write("\nCurrent author\n")
        sys.stdout.write("-" * 15)

        author_name = author_name.strip()[len(author) + 1:]\
                                 .replace('\'', '')

        sys.stdout.write("\nName: ".ljust(11) 
                             + author_name.ljust(20))
        sys.stdout.write("\n")
        author_email = author_email.lstrip()[len(email) + 1:]\
                                 .replace('\'', '')
        sys.stdout.write("Email: ".ljust(10) 
                             + author_email.ljust(20))
        sys.stdout.write("\n\n")

        if '--edit' in sub_options:
            sys.stdout.write("Enter your new name and new email: \n")
            new_name, new_email = user.author(), user.email()
            setup_py.edit(author, new_name, current_path, author_index)
            setup_py.edit(email, new_email, current_path, email_index)

    elif 'classifiers' == command:

        current_classifiers, index = setup_py.get(type_field='classifiers', project_path=current_path)

        current_classifiers = current_classifiers.split('=')[-1].strip()

        sys.stdout.write("\nCurrent classifiers\n")
        sys.stdout.write("-" * 15)
        sys.stdout.write("\n")
        sys.stdout.write(current_classifiers)
        sys.stdout.write("\n")

        if '--edit' in sub_options:
            development_status, environment, framework, auidence, license_type, language, \
                operating_sys, programming_language, topic = user.select_classifiers()
            classifiers = classifier.format(development_status=development_status,
                                            environment=environment, framework=framework,
                                            auidence=auidence, license=license_type,
                                            language=language, operating_sys=operating_sys,
                                            programming_language=programming_language, 
                                            topic=topic)

            new_license = classifier.LICENSES[int(license_type) - 1].split(' :: ')[-1].strip() \
                             if license_type else 'MIT License'

            setup_py.classifiers(current_path, classifiers, index)
            current_license, index = setup_py.get(type_field='license', project_path=current_path)
            current_license = current_license.split("=")[-1]\
                                             .strip()\
                                             .replace('\'', '')\
                                             .replace(',', '')

            setup_py.edit('license', new_license, current_path, index)
            project.make_file(folder_path=current_path, filename='LICENSE',
                              content=license.init(new_license))
            readme.edit(current_path, old_value=current_license, new_value=new_license)

    elif 'license' == command:

        current_license, index = setup_py.get(type_field='license', project_path=current_path)

        sys.stdout.write("\nCurrent license\n")
        sys.stdout.write("-" * 15)
        sys.stdout.write("\n")

        current_license = current_license.split("=")[-1]\
                                         .strip()\
                                         .replace('\'', '')\
                                         .replace(',', '')

        sys.stdout.write(current_license)
        sys.stdout.write("\n")

        if '--edit' in sub_options:
            new_license = user.license().strip()
            new_license = classifier.LICENSES[int(new_license) - 1] if new_license else 'MIT License'
            new_license_name = new_license.split(' :: ')[-1].strip()
            setup_py.edit('license', new_license_name, current_path, index)
            setup_py.edit_classifier_license(current_path, current_license, new_license)
            project.make_file(folder_path=current_path, filename='LICENSE',
                              content=license.init(new_license_name))
            readme.edit(current_path, old_value=current_license, new_value=new_license_name)

    elif 'keywords' == command:
        
        current_keywords, keywords_index = setup_py.get(type_field='keywords', 
                                                        project_path=current_path)

        sys.stdout.write("\nCurrent keywords\n")
        sys.stdout.write("-" * 15)
        sys.stdout.write("\n")

        current_keywords = current_keywords.split("=")[-1]\
                                            .strip()\
                                            .replace('\'', '')
        sys.stdout.write(current_keywords)
        sys.stdout.write("\n\n")

        if '--edit' in sub_options:
            keywords = user.keywords().strip()

            project_name = current_path.split(os.sep)[-1]
            keywords = keywords or project_name
            setup_py.edit('keywords', keywords, current_path, keywords_index)

    elif 'build' == command:

        project.build(current_path)

    elif 'upload' == command:
        
        project.upload(current_path)

    elif 'local' == command:

        project.local(current_path)

    sys.stdout.write("\nDone. Enjoy :)\n")