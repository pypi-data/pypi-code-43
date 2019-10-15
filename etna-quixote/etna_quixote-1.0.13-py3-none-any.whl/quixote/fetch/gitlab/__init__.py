from datetime import datetime
import EtnaAPI
import EtnaAPI.Groups
import git
from quixote import get_context


def gitlab(*, ignore_end_date: bool = False):
    """
    Fetch the delivery from our own GitLab server

    The following entries must be provided in the context:
    - module_id:        the ID of the corresponding module, as integer
    - activity_id:      the ID of the corresponding activity, as integer
    - group_id:         the ID of the target group, as integer
    - stage_end:        the stage's end date in %Y-%m-%dT%H:%M:%S%z format
    - intra_user:       the username to use to connect to the intranet
    - intra_password:   the password to use to connect to the intranet
    - gitlab_token:     the OAuth token to use to authenticate to GitLab
    - stage_end:        the date at which the stage ends, as a string like "2019-05-15T18:02:00+1:00"
    """
    module_id = get_context()["module_id"]
    activity_id = get_context()["activity_id"]
    group_id = get_context()["group_id"]

    session = EtnaAPI.Session(request_retries=10, retry_on_statuses=(500, 502, 504))
    session.authenticate(get_context()["intra_user"], get_context()["intra_password"])
    controller = EtnaAPI.Groups.Controller(session, module_id, activity_id)

    grp = controller.get_group_by_id(group_id)
    url = "https://" + "oauth2:" + get_context()["gitlab_token"] + "@" + grp['rendu'][8:]
    repo = git.Repo.clone_from(url, get_context()["delivery_path"])
    if not ignore_end_date and repo.active_branch.is_valid():
        stage_end = get_context()["stage_end"]
        end_timestamp = int(datetime.strptime(stage_end, '%Y-%m-%dT%H:%M:%S%z').timestamp())
        accepted_commits = repo.iter_commits(until=end_timestamp)
        repo.git.checkout(next(accepted_commits))
