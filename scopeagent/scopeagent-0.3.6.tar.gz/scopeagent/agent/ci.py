import os

from ..tracer import tags


def get_ci_tags():
    if os.getenv('TRAVIS'):
        return {
            tags.CI: True,
            tags.CI_PROVIDER: 'Travis',
            tags.CI_BUILD_ID: os.getenv('TRAVIS_BUILD_ID'),
            tags.CI_BUILD_NUMBER: os.getenv('TRAVIS_BUILD_NUMBER'),
            tags.CI_BUILD_URL: "https://travis-ci.com/%s/builds/%s" % (os.getenv('TRAVIS_REPO_SLUG'),
                                                                       os.getenv('TRAVIS_BUILD_ID')),
        }
    elif os.getenv('CIRCLECI'):
        return {
            tags.CI: True,
            tags.CI_PROVIDER: 'CircleCI',
            tags.CI_BUILD_NUMBER: os.getenv('CIRCLE_BUILD_NUM'),
            tags.CI_BUILD_URL: os.getenv('CIRCLE_BUILD_URL'),
        }
    elif os.getenv('JENKINS_URL'):
        return {
            tags.CI: True,
            tags.CI_PROVIDER: 'Jenkins',
            tags.CI_BUILD_ID: os.getenv('BUILD_ID'),
            tags.CI_BUILD_NUMBER: os.getenv('BUILD_NUMBER'),
            tags.CI_BUILD_URL: os.getenv('BUILD_URL'),
        }
    elif os.getenv('GITLAB_CI'):
        return {
            tags.CI: True,
            tags.CI_PROVIDER: 'GitLab',
            tags.CI_BUILD_ID: os.getenv('CI_JOB_ID'),
            tags.CI_BUILD_URL: os.getenv('CI_JOB_URL'),
        }
    elif os.getenv('CI'):
        return {
            tags.CI: True
        }
    else:
        return {
            tags.CI: False
        }
