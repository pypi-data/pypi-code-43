from ..core import api, releases
import subprocess
from cement import shell
from cement import Controller, ex
from tabulate import tabulate

model_types = ["PredictEvent", "PredictProperty", "AnomalyDetector"]

def get_release_branch(release_id):
    return "release/" + release_id


def gco_existing(app, branch_name):
    (_, error, exit_code) = shell.cmd(f"git checkout {branch_name}")
    if exit_code > 0:
        app.log.error(error.decode('utf-8'))
        raise Exception("Branch checkout failed.")

def print_df(app, df):
    app.log.info("\n"+ tabulate(df, headers='keys', tablefmt='psql'))

def forge_deploy(release_id):
    return shell.cmd(f"forge --branch {release_id} deploy", capture=False)

def forge_delete(release_id):
    return shell.cmd(f"forge delete ${release_id}", capture=False)

def select_release():
    """ 
    Get a valid release id. 
    If the user is on a release branch return the release_id for that branch.
    Otherwise prompt the user to select which branch they'd like to operate on.
    """
    branch_name = str(subprocess.check_output(["git","rev-parse", "--abbrev-ref", "HEAD"]).decode("utf-8") ).strip()
    is_release_branch = "release/" in branch_name

    if is_release_branch:
      release_id = branch_name.split("release/")[1]
    else:
      release_list = releases.list()
      release_options = list(release_list[['name', 'id']].apply(lambda x: ' / '.join(x), axis=1))
      release_prompt = shell.Prompt('Which release?', options=release_options, numbered=True)
      release_id = release_prompt.input.split("/ ")[1]

    return release_id


class Releases(Controller):
    class Meta:
        label = 'release'
        help = "Manage releases"
        stacked_type = 'nested'
        stacked_on = 'base'
    
    @ex(help='list releases')
    def list(self):
        release_list = releases.list()
        print_df(self.app, release_list)
        pass
        
    @ex(help='Create release (branch and undeployed service)')
    def create(self):
        name_prompt = shell.Prompt('Release name? (ex: "Anomaly detection v4")')
        release_name = name_prompt.input
        id_prompt = shell.Prompt('Release id? (ex: "anomaly-detection-v4")')
        release_id = id_prompt.input.replace('/', '-')[:40]

        model_type_prompt = shell.Prompt('Model type?', options=model_types)
        model_type = model_type_prompt.input

        gco_existing(self.app, "master")
        releases.create(release_name, release_id, model_type)

        release_branch = get_release_branch(release_id)
        shell.cmd(f"git checkout -b {release_branch}")
        self.app.log.info(f'Created release branch "{release_name}" at {release_branch}')

        pass


    @ex(help="Check out a release locally")
    def checkout(self):
        gco_existing(self.app, "master")
        release_id = select_release()
        gco_existing(self.app, get_release_branch(release_id))
        # shell.cmd(f"git checkout release/{release_id}", capture=False)
        self.app.log.info(f"Checked out release {release_id}")


    @ex(help='Deploy release branch')
    def deploy(self):
        # if release isActive, exit and prompt for hotfix
        # if release doesn't exist, call create release w/ git branch name, set isActive + latest hash. Increment version.
        release_id = select_release()
        gco_existing(self.app, get_release_branch(release_id))

        confirm_prompt = shell.Prompt(f"Deploy release {release_id}? [y/n]")

        if confirm_prompt.input == "n" or confirm_prompt.input == "no":
          self.app.log.info("Release canceled.")
          return

        releases.deploy(release_id)

        self.app.log.info("Release deployed.")


    @ex(help='Create a hotfix branch')
    def hotfix_start(self):
        release_id = select_release()
        description = shell.Prompt(f"What should we call this hotfix? (ex: content-save-function)").input.strip()
        branch_name = f"hotfix/{release_id}/{description}"

        gco_existing(self.app, get_release_branch(release_id))
        shell.cmd(f"git checkout -b {branch_name}", capture=False)


    @ex(help='Deploy a commited hotfix to an existing release.')
    def hotfix_deploy(self):
        release_id = select_release()
        gco_existing(self.app, get_release_branch(release_id))
        shell.cmd("git pull")

        confirm_prompt = shell.Prompt(f"""
        This command should only be run after a hotfix pull request (created with release start_hotfix) has been merged.
        Please confirm that you've PR'd in the hotfix by typing 'I PR'd a hotfix'.
        """)

        if confirm_prompt.input != "I PR'd a hotfix":
          self.app.log.info("Text does not match prompt, exiting.")
          return

        forge_deploy("release_id")

        git_hash = subprocess.check_output(['git', 'rev-parse', 'HEAD']).strip()
        shell.cmd(f"gco master && git cherry-pick {git_hash}", capture=False)
        
        pass

    
    @ex(help='Disable a release')
    def disable(self):
        release_id = select_release()
        forge_delete(release_id)
        releases.disable(release_id)
        pass

    def revert(self):
        # list commits since master on this branch. Allow user to select one.
        # Check out that commit, run self.deploy
        pass