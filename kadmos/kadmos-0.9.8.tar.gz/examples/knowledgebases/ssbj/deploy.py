import os

from examples.knowledgebases.ssbj.create_cmdows_file import create_cmdows_file
from ssbjkadmos.utils.database import deploy, clean

def deploy_repo():
    dir_path = os.path.dirname(os.path.realpath(__file__))

    clean(dir_path)

    deploy(dir_path)

    removes = ['Constraints-input.xml',
               'Constraints-output.xml',
               'Constraints-partials.xml',
               'Objective-input.xml',
               'Objective-output.xml',
               'Objective-partials.xml']

    for file in os.listdir(os.path.dirname(__file__)):
        checks = ['Aerodynamics-', 'Performance-', 'Propulsion-', 'Structures-', 'DpdxCalc-']
        replaces = ['AeroAnalysis-', 'PerformanceAnalysis-', 'PropulsionAnalysis-', 'StructuralAnalysis-', 'DpdxAnalysis-']
        for i, check in enumerate(checks):
            if check in file:
                os.rename(os.path.join(dir_path, file),
                          os.path.join(dir_path, replaces[i] + file[len(check):]))
        if file in removes:
            os.remove(os.path.join(dir_path, file))

    create_cmdows_file(dir_path)

if __name__ == '__main__':
    deploy_repo()