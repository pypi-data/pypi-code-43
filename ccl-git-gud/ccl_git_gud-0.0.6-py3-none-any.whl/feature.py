import sys

from loguru import logger

from .utils import git, \
    get_merge_request, \
    ensure_clean_git, \
    wait_for_pipeline, \
    wait_for_mr_pipeline, \
    ensure_mr_pipeline_succeeded


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

    def get_gitlab_mr(self, gl, name):
        project = gl().projects.get(gl.project_url)
        mr = get_merge_request(gl, 'feature/{}'.format(name))
        if mr is None:
            return None
        return project, mr

    def edit_gitlab_mr_attrs(self, mr):
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

        logger.info('Upload changes to Gitlab')
        mr.save()

    def merge_feature(self, project, mr, name):
        git('checkout feature/{}'.format(name))
        git('pull origin feature/{}'.format(name))

        pipelines = list(filter(
            lambda x: x.sha == mr.merge_commit_sha,
            project.pipelines.list()
        ))
        if len(pipelines):
            logger.info('Merge already occured, skipping.')
            return
        logger.info('Accept merge request.')
        git('checkout develop')
        git('merge --no-ff feature/{}'.format(name))
        try:
            git('push origin develop')
        except Exception as e:
            logger.error('Push failed : {}', e)
            logger.error('Reverting local merge')
            git('reset --hard origin/develop')
            sys.exit(1)

        pipelines = list(filter(
            lambda x: x.sha == mr.merge_commit_sha,
            project.pipelines.list()
        ))
        git('fetch -q origin')
        git('push --delete origin feature/{}'.format(name))
        if len(pipelines):
            last_pipeline = wait_for_pipeline(project, pipelines[0].id)
            logger.info('Merge pipeline status: {}',
                        last_pipeline.status)
        else:
            logger.debug('No merge pipeline triggered. Skipping wait')

        git('branch -d feature/{}'.format(name))

    def rebase_feature(self, name):
        git('fetch -q origin')
        git('checkout feature/{}'.format(name))
        git('pull origin feature/{}'.format(name))
        try:
            git('rebase origin/develop')
        except:
            logger.error('Could not perform automatic rebase.')
            logger.error(
                'Please finish rebase manually before launching git gud again.')
            sys.exit(1)
        else:
            git('push --force origin feature/{}'.format(name))

    @logger.catch
    def __call__(self, parser, args):
        project, mr = self.get_gitlab_mr(args.gl, args.name)
        logger.info('Merge request URL: {}', mr.web_url)
        ensure_clean_git()
        ensure_mr_pipeline_succeeded(project, mr)
        self.edit_gitlab_mr_attrs(mr)

        if not args.no_rebase:
            self.rebase_feature(args.name)
            ensure_mr_pipeline_succeeded(project, mr)

        if not args.no_merge:
            self.merge_feature(project, mr, args.name)


class FeatureDelete():
    COMMAND = 'delete'

    @logger.catch
    def __call__(self, parser, args):
        mr = get_merge_request(args.gl, 'feature/{}'.format(args.name))
        if mr is None:
            return
        try:
            project = args.gl().projects.get(args.gl.project_url)
            pipelines = list(filter(
                lambda x: x.sha == mr.merge_commit_sha,
                project.pipelines.list()
            ))
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
