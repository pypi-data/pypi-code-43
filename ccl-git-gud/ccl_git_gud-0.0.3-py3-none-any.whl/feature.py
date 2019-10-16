import sys
import time

from loguru import logger
from datetime import datetime, timedelta

from .utils import git, get_merge_request


def is_clean_git():
    res = git('status -s')
    for short in bytes('MADRCU', 'ascii'):
        if short in res.stdout:
            return False
    return True


def wait_for_pipeline(project, pipeline_id, timeout=3600):
    details = project.pipelines.get(pipeline_id)
    logger.info('Waiting for pipeline {}', details['web_url'])
    limit = datetime.now() + timedelta(seconds=timeout)
    while datetime.now() < limit:
        details = project.pipelines.get(pipeline_id)
        if details.status not in ['success', 'failed']:
            logger.debug('Pipeline status: {}', details.status)
            time.sleep(5)
        else:
            return details


def wait_for_mr_pipeline(project, mr, timeout=3600):
    pipelines = mr.pipelines()
    if not len(pipelines):
        logger.debug(
            'No pipeline have yet run for this merge request. Skipping wait')
        return None
    p = pipelines[0]
    return wait_for_pipeline(p['id'])


class FeatureStart():
    COMMAND = 'start'

    @logger.catch
    def __call__(self, parser, args):
        git('fetch -q origin')
        try:
            git('checkout -b feature/{} {}'.format(args.name, args.base))
        except:
            logger.warning(
                'feature branch {} already exists. Using remote one', args.name)
        else:
            logger.debug('Created branch feature/{}', args.name)
        try:
            git('push -u origin feature/{}:feature/{}'.format(args.name, args.name))
        except Exception as e:
            logger.warning('Could not push branch to remote {}', args.base)
        else:
            logger.debug(
                'Synchronized branch feature/{} with remote.', args.name)

        git('fetch -q origin feature/{}'.format(args.name))
        git('checkout feature/{}'.format(args.name))

        project = args.gl().projects.get(args.gl.project_url)
        mr = project.mergerequests.create({
            'source_branch': 'feature/{}'.format(args.name),
            'target_branch': args.base,
            'title': 'WIP: feature {}'.format(args.name),
            'labels': ['WIP', 'Doing'],
            'remove_source_branch': True,
            'allow_collaboration': True,
            'squash': False,
        })
        logger.info('Merge request created at {}', mr.web_url)


class FeatureFinish():
    COMMAND = 'finish'

    @logger.catch
    def __call__(self, parser, args):
        project = args.gl().projects.get(args.gl.project_url)
        mr = get_merge_request(args.gl, 'feature/{}'.format(args.name))
        if mr is None:
            return

        last_pipeline = wait_for_mr_pipeline(project, mr)
        if last_pipeline is not None and last_pipeline.status == 'failed':
            logger.error(
                'The last build failed for branch feature/{}. Exiting.', args.name)
            sys.exit(1)

        if not is_clean_git():
            logger.error('Git state need to be clean for this operation')
            sys.exit(1)

        logger.info('Merge request URL: {}', mr.web_url)
        logger.info('Labels edition.')
        mrl = mr.labels
        mr.labels = list(
            filter(
                lambda x: x not in ['Doing', 'WIP', 'Done'],
                mr.labels
            )
        ) + ['Done']
        logger.debug('Previous labels: {}', mrl)
        logger.debug('Current labels : {}', mr.labels)

        logger.info('Remove WIP tag in title')
        mr.title = mr.title.replace('WIP:', '').lstrip()

        git('checkout develop')
        git('branch -d feature/{}'.format(args.name))

        logger.info('Upload changes to Gitlab')
        mr.save()

        if args.merge:
            logger.info('Accept merge request.')
            mr.merge()
            pipelines = project.pipelines.list(ref='develop')
            if len(pipelines):
                last_pipeline = wait_for_pipeline(project, pipelines[0]['id'])
                logger.info('Merge pipeline status: ', last_pipeline.status)
            else:
                logger.debug('No merge pipeline triggered. Skipping wait')
            git('fetch -q origin')
            git('pull origin develop')


class FeatureDelete():
    COMMAND = 'delete'

    @logger.catch
    def __call__(self, parser, args):
        mr = get_merge_request(args.gl, 'feature/{}'.format(args.name))
        if mr is None:
            return
        try:
            mr.delete()
        except Exception:
            logger.exception('Merge request delete failed.')
            return
        logger.info('Merge request deleted')

        logger.info('Moving to branch develop')
        git("checkout develop".format(args.name))
        logger.info('deleting local branch feature/{}', args.name)
        git("branch -d feature/{}".format(args.name))
        logger.info('deleting remote branch feature/{}', args.name)
        git("push --delete origin feature/{}".format(args.name))
        logger.info('refreshing remote state')
        git("fetch -q origin")


class Feature():
    COMMAND = 'feature'
    FTAB = {
        FeatureStart.COMMAND: FeatureStart,
        FeatureFinish.COMMAND: FeatureFinish,
        FeatureDelete.COMMAND: FeatureDelete,
    }

    @logger.catch
    def __call__(self, parser, args):
        if args.feature_cmd is None:
            parser.print_help()
            sys.exit(1)
        elif args.feature_cmd in Feature.FTAB.keys():
            Feature.FTAB[args.feature_cmd]()(parser, args)
        else:
            logger.error('Feature command not implemented', args.feature_cmd)
            sys.exit(1)
