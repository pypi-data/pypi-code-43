import sys
from loguru import logger

from .utils import git, \
    get_merge_request, \
    ensure_clean_git, \
    wait_for_pipeline, \
    wait_for_mr_pipeline, \
    ensure_mr_pipeline_succeeded


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

    def merge_branches(self, gl, source, target):
        project = gl().projects.get(gl.project_url)
        mr = get_merge_request(gl, source)

        if mr.state == 'merged':
            logger.info('branch was already merged. Skipping.')
            return mr
        ensure_mr_pipeline_succeeded(project, mr)
        logger.info('Accept the merge request')
        git('checkout {}'.format(target))
        git('pull origin {}'.format(target))
        git('merge --no-ff {}'.format(source))
        try:
            git('push origin {}'.format(target))
        except Exception as e:
            logger.error('Push failed : {}', e)
            logger.error('Reverting local merge')
            git('reset --hard origin/{}'.format(target))
            raise
        return get_merge_request(gl, source)

    def merge_realign_mr(self, gl, project, realign_mr):
        return self.merge_branches(gl, 'master', 'develop')

    def merge_release_branch(self, gl, version):
        return self.merge_branches(gl, 'release/{}'.format(version), 'master')

    def ensure_merge_commit_pipeline_succeeded(self, project, merge_commit_sha):
        pipelines = list(filter(
            lambda x: x.sha == merge_commit_sha,
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

        if pipeline_failed:
            logger.error('master merge pipeline failed. Skipping the release.')
            raise Exception('merge pipeline failed')

    def tag_release_on_master(self, version, merge_commit_sha):
        git("fetch -q origin".format(version))
        logger.info('Tag the merge commit {}', merge_commit_sha)
        try:
            git('tag -d {}'.format(version), quiet=True)
        except:
            pass
        git("tag -m {} -a {} {}".format(
            version, version, merge_commit_sha
        ))
        logger.info('propagate tag')
        git("push --tags origin")

    def create_realign_mr(self, project, version):
        existing_post_release_mrs = list(filter(
            lambda x:
            x.source_branch == 'master' and
            x.target_branch == 'develop' and
            version in x.title,
            project.mergerequests.list()
        ))
        develop_mr = None
        if len(existing_post_release_mrs):
            logger.info('Develop realign merge request already exists')
            develop_mr = existing_post_release_mrs[0]
        else:
            develop_mr = project.mergerequests.create({
                'source_branch': 'master',
                'target_branch': 'develop',
                'title': 'Release {}'.format(version),
                'labels': ['release'],
                'remove_source_branch': False,
                'allow_collaboration': True,
                'squash': False,
            })
        return develop_mr

    def realign_develop(self, gl, project, version):
        mr = self.create_realign_mr(project, version)
        return self.merge_realign_mr(gl, project, mr)

    @logger.catch
    def __call__(self, parser, args):
        ensure_clean_git()
        git("fetch -q origin".format(args.version))
        project = args.gl().projects.get(args.gl.project_url)

        mr = self.merge_release_branch(args.gl, args.version)
        try:
            self.ensure_merge_commit_pipeline_succeeded(
                project, mr.merge_commit_sha
            )
        except:
            logger.error('Pipeline for merge into master failed.')
            logger.info('What to do next:')
            logger.info('- remove the merge commit from master')
            logger.info('- reopen the merge request')
            logger.info('- fix the bug')
            logger.info('- try to release again')
            sys.exit(1)

        self.tag_release_on_master(args.version, mr.merge_commit_sha)
        logger.info('Realign develop')
        develop_mr = self.realign_develop(args.gl, project, args.version)
        logger.info('Waiting for develop pipeline')
        try:
            self.ensure_merge_commit_pipeline_succeeded(
                project, develop_mr.merge_commit_sha
            )
        except:
            logger.warning('Develop branch pipeline failed')

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
