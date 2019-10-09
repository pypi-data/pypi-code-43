import os, sys, string


def greet(name):
    with open(os.path.join(
        os.path.dirname(__file__),
        'template.txt'
    )) as f:
        template = string.Template(f.read())
    print(template.safe_substitute({'name': name}))
    
    
def greet_main():
    if len(sys.argv) > 1:
        name = sys.argv[1]
    else:
        name = 'unknown human'
    greet(name)
