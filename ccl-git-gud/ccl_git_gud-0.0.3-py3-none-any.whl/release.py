import sys
from loguru import logger

from .utils import git, get_merge_request


class ReleaseStart():
    COMMAND = 'start'

    @logger.catch
    def __call__(self, parser, args):
        git("checkout -b release/{} {}".format(args.version, args.base))
        git('fetch -q origin')
        git('push -u origin release/{}:release/{}'.format(args.version, args.version))
        git('fetch -q origin release/{}'.format(args.version))

        project = args.gl().projects.get(args.gl.project_url)
        project.mergerequests.create({
            'source_branch': 'release/{}'.format(args.version),
            'target_branch': 'master',
            'title': 'Release {}'.format(args.version),
            'labels': ['release'],
            'remove_source_branch': True,
            'allow_collaboration': True,
            'squash': True,
        })


class ReleaseFinish():
    COMMAND = 'finish'

    @logger.catch
    def __call__(self, parser, args):
        project = self.gl().projects.get(self.gl.project_url)
        mr = get_merge_request(args.gl, 'release/{}'.format(args.name))

        # TODO: Wait for pipeline validation
        # TODO: Warn if pipeline failed
        logger.info('Accept the release MR')
        mr.merge()
        # TODO: Wait for pipeline validation
        # TODO: Warn if pipeline failed

        git("fetch -q origin".format(args.version))

        logger.info('Tag the merge commit {}', mr.merge_commit_sha)
        git("tag -m {} -a {} {}".format(
            args.version, args.version, mr.merge_commit_sha
        ))
        logger.info('propagate tag')
        git("push --tags origin")

        logger.info('Realign develop')
        develop_mr = project.mergerequests.create({
            'source_branch': 'master',
            'target_branch': 'develop',
            'title': 'Release {}'.format(args.version),
            'labels': ['release'],
            'remove_source_branch': False,
            'allow_collaboration': True,
            'squash': False,
        })

        # TODO: Wait for pipeline validation
        # TODO: Warn if pipeline failed
        logger.info('Accept the release MR')
        develop_mr.merge()
        # TODO: Wait for pipeline validation
        # TODO: Warn if pipeline failed

        git("fetch -q origin")
        git("checkout develop")
        git("pull origin develop")


class ReleaseDelete():
    COMMAND = 'delete'

    @logger.catch
    def __call__(self, parser, args):
        pass


class Release():
    COMMAND = 'release'
    FTAB = {
        ReleaseStart.COMMAND:  ReleaseStart,
        ReleaseFinish.COMMAND: ReleaseFinish,
        ReleaseDelete.COMMAND: ReleaseDelete,
    }

    def __call__(self, parser, args):
        if args.release_cmd is None:
            parser.print_help()
            sys.exit(1)
        elif args.release_cmd in Release.FTAB.keys():
            Release.FTAB[args.release_cmd]()(parser, args)
        else:
            logger.error('Release command not implemented', args.release_cmd)
            sys.exit(1)
