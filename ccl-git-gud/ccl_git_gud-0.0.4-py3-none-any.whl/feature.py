import sys

from loguru import logger

from .utils import git, get_merge_request, ensure_clean_git, wait_for_pipeline, wait_for_mr_pipeline


class FeatureStart():
    COMMAND = 'start'

    @logger.catch
    def __call__(self, parser, args):
        ensure_clean_git()
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
        logger.info('Merge request URL: {}', mr.web_url)

        last_pipeline = wait_for_mr_pipeline(project, mr)
        if last_pipeline is not None and last_pipeline.status == 'failed':
            logger.error(
                'The last build failed for branch feature/{}. Exiting.', args.name)
            sys.exit(1)
        ensure_clean_git()

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
        if bytes('feature/{}'.format(args.name), 'ascii') in git('branch').stdout:
            git('branch -d feature/{}'.format(args.name))

        logger.info('Upload changes to Gitlab')
        mr.save()

        if args.merge:
            logger.info('Accept merge request.')
            mr.merge()
            pipelines = project.pipelines.list(ref='develop')
            if len(pipelines):
                last_pipeline = wait_for_pipeline(project, pipelines[0].id)
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
