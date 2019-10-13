from . import sceleton


DEVELOPMENT_STATUS = []
ENVIRONMENTS = []
FRAMEWORKS = []
TOPICS = []
PROGRAMMING_LANGUAGES = []
LANGUAGES = []
OS = []
LICENSES = []
AUDIENCE = []


def init():

    global DEVELOPMENT_STATUS
    global ENVIRONMENTS
    global FRAMEWORKS
    global TOPICS
    global PROGRAMMING_LANGUAGES
    global LANGUAGES
    global OS
    global LICENSES
    global AUDIENCE

    content = sceleton('classifiers.txt')

    DEVELOPMENT_STATUS = [line for line in content if line.startswith('Development Status')]
    ENVIRONMENTS = [line for line in content if line.startswith('Environment')]
    FRAMEWORKS = [line for line in content if line.startswith('Framework')]
    TOPICS = [line for line in content if line.startswith('Topic')]
    PROGRAMMING_LANGUAGES = [line for line in content if line.startswith('Programming Language')]
    LANGUAGES = [line for line in content if line.startswith('Natural Language')]
    OS = [line for line in content if line.startswith('Operating System')]
    LICENSES = [line for line in content if line.startswith('License')]
    AUDIENCE = [line for line in content if line.startswith('Intended Audience')]


def format(version='0.0.1', development_status=None, environment=None, \
            framework=None, auidence=None, license=None, language=None, \
            operating_sys=None, programming_language=None, topic=None):
    
    global DEVELOPMENT_STATUS
    global ENVIRONMENTS
    global FRAMEWORKS
    global TOPICS
    global PROGRAMMING_LANGUAGES
    global LANGUAGES
    global OS
    global LICENSES
    global AUDIENCE


    classifiers = []

    if development_status:
        if len(development_status.split(' ')) > 1:
            raise ValueError("Only one development status can be chosen.")

        classifiers.append(DEVELOPMENT_STATUS[int(development_status) - 1])
    
    if environment:

        for env in environment.split(' '):
            classifiers.append(ENVIRONMENTS[int(env) - 1])

    if framework:

        for fr in framework.split(' '):
            classifiers.append(FRAMEWORKS[int(fr) - 1])

    if auidence:

        for aud in auidence.split(' '):
            classifiers.append(AUDIENCE[int(aud) - 1])

    if language:

        for lang in language.split(' '):
            classifiers.append(LANGUAGES[int(lang) - 1])

    if programming_language:

        for planguage in programming_language.split(' '):
            classifiers.append(PROGRAMMING_LANGUAGES[int(planguage) - 1])

    if operating_sys:

        for os_ in operating_sys.split(' '):
            classifiers.append(OS[int(os_) - 1])

    if topic:

        for top in topic.split(' '):
            classifiers.append(TOPICS[int(top) - 1])

    if license:
        if len(license.split(' ')) > 1:
            raise ValueError("Only one license can be chosen.")

        classifiers.append(LICENSES[int(license) - 1])

    space_size = 8
    classifiers = ["{}'{}',\n".format(' ' * space_size, classifier.strip()) \
                    for classifier in classifiers]

    if not classifiers:
        classifiers = "{}\n".format(' ' * space_size)

    return classifiers