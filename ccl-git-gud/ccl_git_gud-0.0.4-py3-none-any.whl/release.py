import sys
from loguru import logger

from .utils import git, get_merge_request, ensure_clean_git, wait_for_pipeline, wait_for_mr_pipeline


class ReleaseStart():
    COMMAND = 'start'

    @logger.catch
    def __call__(self, parser, args):
        # ensure_clean_git()
        git('checkout -b release/{} {}'.format(args.version, args.base))
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
        ensure_clean_git()
        git("fetch -q origin".format(args.version))
        project = args.gl().projects.get(args.gl.project_url)
        mr = get_merge_request(args.gl, 'release/{}'.format(args.version))

        if mr.state == 'merged':
            logger.info('release branch was already merged. Skipping.')
        else:
            last_pipeline = wait_for_mr_pipeline(project, mr)
            if last_pipeline is None:
                logger.warning('No pipeline found for release merge request')
            elif last_pipeline.status == 'failed':
                logger.error(
                    'The last build failed for branch release/{}.', args.name)
                sys.exit(1)
            logger.info('Accept the release merge request')
            mr.merge()

        pipelines = list(filter(
            lambda x: x.sha == mr.merge_commit_sha,
            project.pipelines.list()
        ))
        pipeline_failed = False
        if len(pipelines):
            last_pipeline = wait_for_pipeline(project, pipelines[0].id)
            logger.info('Merge pipeline status: ', last_pipeline.status)
            if last_pipeline.status == 'failed':
                pipeline_failed = True
        else:
            logger.warning('No merge pipeline triggered. Skipping wait')
        git("fetch -q origin".format(args.version))

        if pipeline_failed:
            logger.error('master merge pipeline failed. Skipping the release.')
            sys.exit(1)

        logger.info('Tag the merge commit {}', mr.merge_commit_sha)
        try:
            git('tag -d {}'.format(args.version))
        except:
            pass
        git("tag -m {} -a {} {}".format(
            args.version, args.version, mr.merge_commit_sha
        ))
        logger.info('propagate tag')
        git("push --tags origin")

        logger.info('Realign develop')
        existing_post_release_mrs = list(filter(
            lambda x:
            x.source_branch == 'release/{}'.format(args.version) and
            x.target_branch == 'develop' and
            args.version in x.title,
            project.mergerequests.list()
        ))
        develop_mr = None
        if len(existing_post_release_mrs):
            logger.info('Develop realign merge request already exists')
            develop_mr = existing_post_release_mrs[0]
        else:
            develop_mr = project.mergerequests.create({
                'source_branch': 'release/{}'.format(args.version),
                'target_branch': 'develop',
                'title': 'Release {}'.format(args.version),
                'labels': ['release'],
                'remove_source_branch': False,
                'allow_collaboration': True,
                'squash': False,
            })

        if develop_mr.state == 'merged':
            logger.info('develop branch was already realigned. Skipping.')
        else:
            last_pipeline = wait_for_mr_pipeline(project, develop_mr)
            if last_pipeline is None:
                logger.warning('No pipeline found for realigned branch')
            elif last_pipeline.status == 'failed':
                logger.error('The last build failed for branch master.')
                sys.exit(1)
            logger.info('Accept the release MR')
            develop_mr.merge()

        logger.info('Waiting for develop pipeline')
        pipelines = list(filter(
            lambda x: x.sha == develop_mr.merge_commit_sha,
            project.pipelines.list()
        ))
        if len(pipelines):
            last_pipeline = wait_for_pipeline(project, pipelines[0].id)
            logger.info('Merge pipeline status: ', last_pipeline.status)
        else:
            logger.warning('No merge pipeline triggered. Skipping wait')

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
