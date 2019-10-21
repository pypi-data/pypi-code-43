import glob
import logging
import os
import sys
import re
import shutil
import requests
import subprocess
import tempfile
import zipfile


class GradleResolver(object):
    dependency_variable = '__gradle_deps__'
    description = 'Pure Gradle - when the CERN CBNG is not available'

    @classmethod
    def is_available(cls):
        # check if CBNG web service is reachable
        try:
            requests.get('http://repo1.maven.org/maven2/', timeout=5.0)
            return True
        except:
            return False

    def __init__(self, dependencies):
        """Resolve dependencies using Gradle and public repos"""
        self.log = logging.getLogger(__package__)

        extra_repos = []
        valid_deps = []
        for dep in dependencies:
            if isinstance(dep, dict):
                try:
                    groupId = dep['groupId']
                    artifactId = dep['product'] if 'product' in dep else dep['artifactId']
                    version = dep['version'] if 'version' in dep else '+'
                    if 'repository' in dep:
                        extra_repos.append(str(dep['repository']))
                    dep = groupId + ':' + artifactId + ':' + version
                except Exception as e:
                    self.log.warning('IGNORING __gradle_deps__ dependency "{0}": invalid dict {1}'.format(dep, e))
                    continue
            if not re.match('[a-z0-9_.:+\\-]', dep):
                self.log.warning('IGNORING __gradle_deps__ dependency "{0}": contains invalid characters.'.format(dep))
            elif dep.count(':') != 2:
                self.log.warning(('IGNORING __gradle_deps__ dependency "{0}": it is not in gradle format '
                                  + '-> "<group>:<product>:<version>"').format(dep))
            else:
                self.log.info('will resolve "{0}" using Gradle'.format(dep))
                valid_deps.append(dep)

        gradle_buildscript = '''
            plugins {
                id "com.jfrog.bintray" version "1.7.3"
            }
            apply plugin: 'maven'
            apply plugin: 'maven-publish'
            apply plugin: 'com.jfrog.bintray'

            repositories {
                mavenCentral()
                jcenter()
                ''' + '\n'.join(extra_repos) + '''
            }

            configurations {
                pythondeps
            }
            task getJars(type: Copy) {
                from configurations.pythondeps
                into "$buildDir/jars"
            }
        '''
        gradle_buildscript += '\ndependencies {\n'
        for dep in valid_deps:
            gradle_buildscript += '    pythondeps \'{0}\'\n'.format(dep)
        gradle_buildscript += '\n}\n'

        temp_dir = tempfile.mkdtemp(prefix="cmmn-dep-manager-gradle-resolve-")
        self.log.info('Running Gradle in "{0}"...'.format(temp_dir))
        with zipfile.ZipFile(os.path.join(os.path.dirname(__file__), 'gradle-wrapper.zip')) as gradle:
            gradle.extractall(temp_dir)
        with open(os.path.join(temp_dir, 'build.gradle'), 'w') as buildfile:
            buildfile.write(gradle_buildscript)
        gradle_wrapper = 'gradlew.bat' if sys.platform.startswith('win') else 'chmod a+x ./gradlew && ./gradlew'
        retcode = subprocess.call(gradle_wrapper + ' getJars', cwd=temp_dir, shell=True)
        if retcode != 0:
            shutil.rmtree(temp_dir, ignore_errors=True)
            raise OSError('error executing gradle!')
        self.gradle_dir = temp_dir

    def save_jars(self, dir):
        self.log.info('> putting jars into {0}'.format(dir))
        for jar in glob.glob(os.path.join(self.gradle_dir, 'build', 'jars', '*.jar')):
            self.log.info('retrieving {0}'.format(os.path.basename(jar)))
            shutil.copy(jar, dir)

        self.log.info('cleaning up {0}'.format(self.gradle_dir))
        shutil.rmtree(self.gradle_dir, ignore_errors=True)

    @classmethod
    def get_help(cls, classnames, class_info):
        print("Online JavaDoc not supported for Gradle dependencies!")
