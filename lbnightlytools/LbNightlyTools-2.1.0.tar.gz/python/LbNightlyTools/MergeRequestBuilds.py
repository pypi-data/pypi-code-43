#!/usr/bin/env python
###############################################################################
# (c) Copyright 2019 CERN for the benefit of the LHCb Collaboration           #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################
import datetime
import gitlab
import json
import logging
import os
from .Configuration import cloneSlot, Project, slot_factory
from .GitlabUtils import _gitlabServer, _getGitlabProject, cached

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# TODO use something from LbNightlyTools?
def full_name(project_name):
    '''
    Return the full project name. i.e. lhcb/Rec for 'Rec' or gaudi/Gaudi for 'gaudi'

    @param project_name: This is the name of the project in gitlab we want the full name for
    '''
    # Get the full_name of the project
    if '/' in project_name:
        return project_name
    prefix = 'gaudi/' if project_name == 'Gaudi' else 'lhcb/'
    return prefix + project_name


def mr_link(mr, project):
    '''
    Construct a html link based on the project mr and project objects

    @param mr: mr object from gitlab
    @param project: project object from gitlab
    '''
    # Make a MR link to reference back to the gitlab webpage of the MR
    return '<a href="{}" target="_blank">{}!{}</a>'.format(
        mr.attributes['web_url'], project.attributes['path_with_namespace'],
        mr.get_id())


def mr_getrefdate(mrs):
    '''
    Return the newest date that any MR was forked from it's target branch
    The value returned is to the second so is sufficient to lookup the git ref of all external projects at that time

    @param mrs: This is a list of (mr, project) which are the gitlab objects
    '''
    # Get the latest date that the given MRs were forked at.
    # This is used to know what to do with projects we've not explicitly included in the build slot
    # e.g. if we depend on LHCb forked at date X we will want to take the last Gaudi master commit before this

    mr_ref_dates = []
    # Loop through all MRs
    for mr, project in mrs:
        # Parse the date of the time when the MR was committed
        ref_sha1 = mr.attributes['diff_refs']['start_sha']
        mr_ref_dates.append(
            datetime.datetime.strptime(
                project.commits.get(ref_sha1).attributes['committed_date'],
                "%Y-%m-%dT%H:%M:%S.%fZ"))

    # Return the latest time corresponsing to the last MR branched from it's project
    return sorted(mr_ref_dates)[-1].isoformat()


def clone_slot(parent_slot, slot_name, slot_desc, platforms):
    '''
    Constructs a new Slot object and returns it after re-configuring it

    @param parent_slot: this is the slot we're supposed to use as a reference to construct a new one
    @param slot_name: this is the name the new slot will have
    @param slot_desc: this is the description applied to the new slot
    @param platforms: these are the plarforms the new slot is to be built against
    '''
    # Clone from a given slot and define some common parameters
    new_slot = cloneSlot(parent_slot, slot_name)
    new_slot.desc = slot_desc
    if platforms:
        new_slot.platforms = platforms
    return new_slot


@cached
def getLastCommit(project, ref_date, branch):
    '''
    Return the most recent commit id from a project on a branch before a
    given date.
    '''
    project = _getGitlabProject(project)
    # TODO here we rely on gitlab reverse ordering the commits
    commit = project.commits.list(until=ref_date, ref_name=branch)[0]
    return commit.attributes['id']


def set_last_commits(build_slot, ref_date, commits, target_branch):
    '''
    This method sets the external commit ids for all of the projects.
    This is either the commit corresponding to the time of the last MR fork (this date is defined as ref_date)
    or, the commit of the project as defined in the external_commits dictionary

    @param build_slot: This is the Slot object we want to define the projects for
    @param ref_date: This is the date which is taken to be the time when the last MR was forked
    @param commits: This is the dictionary containing the external_commit refs with project_names as keys
    @param target_branch: This is the branch that we should be targetting with our MRs
    '''

    # Loop through the MRs
    for project in build_slot.projects:
        # Get the project name, i.e. Rec, Lbcom
        name = project.name
        path_name = full_name(name)
        try:
            commit = commits[path_name]
        except KeyError:
            commit = getLastCommit(path_name, ref_date, target_branch)

        logger.debug("Setting checkout for '{}' to be '{}'".format(
            name, commit))
        build_slot.projects[name].checkout_opts['commit'] = commit


def _find_slot(slots, name):
    found = [s for s in slots if s.name == name]
    assert len(found) == 1, 'Expected exactly one slot, got {!r}'.format(found)
    return found[0]


def get_model_slot(target_branch, slots):
    '''
    Return the Slot which we use as a model for the ref and test builds.

    @param target_branch: Target branch of the MR.
    @param slots: Model slots to pick from.
    '''

    # This copies the reference Slot from the target branch, i.e. master, lhcb-patches-2018, etc
    if target_branch == 'master':
        return _find_slot(slots, 'lhcb-master')
    elif target_branch == 'run2-patches':
        return _find_slot(slots, 'lhcb-run2-patches')
    message = ('Cannot determine Slot configuration from target branch "{}".'.
               format(target_branch))
    logger.error(message)
    raise NotImplementedError(message)


def create_mr_slots(sources, platforms, merge, model_slots):
    '''
    Constructs and returns two new Slot objects.

    The first is the reference slot, while the second is the testing
    slot, based on the MRs/commits/branches specified with `sources`.
    The model slot is picked from `model_slots` based on the target
    branch of MRs, which must all be consistent.

    In case of "branch" mode (`merge` is False), the newest date that
    any MR in `sources` was forked from its target branch is determined.
    For projects not specified in `sources` the last commit on the
    target branch before that date is used.

    In case of "integration" mode (`merge` is True), the target branch
    of unspecified projects is taken, while for MRs in `sources` a
    merge with the target branch is requested. This matches the usual
    nightly behaviour.

    @param sources: A list of ids of the merge requests to be included
    in the MR build, e.g. ['lhcb/Rec!123', 'lhcb/LHCb@3a63e54a'].
    @param platforms: A list of the platforms that these slots are to
    request builds for.
    @param merge: Use integration mode (tip of target branch + MRs).
    @model_slots: Model slots to choose from.
    '''

    # Split sources into MRs and commits and fetch MRs
    mrs = {}
    commits = {}
    for source in sources:
        if '!' in source:
            p, m = source.split('!')
            gp = _getGitlabProject(p)
            mrs[p] = (gp.mergerequests.get(m), gp)
        elif '@' in source:
            p, c = source.split('@')
            commits[p] = c
        else:
            raise ValueError('Unexpected source {!r}'.format(source))

    # Obtain the target branch
    target_branches = set(
        mr.attributes['target_branch'] for mr, _ in mrs.values())
    if len(target_branches) > 1:
        raise RuntimeError('Refuse to create slot with inconsistent target '
                           'branches: {}'.format(target_branches))
    target_branch = target_branches.pop()

    logger.info('Getting model slot')
    model_slot = get_model_slot(target_branch, model_slots)
    logger.info('Model slot is: {}'.format(model_slot.name))

    for mr, project in mrs.values():
        name = project.attributes['path']
        if not hasattr(model_slot, name):
            logger.warning(
                'The project: "{}" was not in the Slot {}, is this expected? '
                'Adding anyway.'.format(name, model_slot.name))
            model_slot.projects.append(Project(name, target_branch))

    if not merge:
        # Find the date of the last branch for any of the given MRs
        ref_date = mr_getrefdate(mrs.values())
        logger.info('Will attempt to grab target branch for unspecified '
                    'projects as of: {}'.format(ref_date))

    # Give a detailed description to the slot for this build
    # Will make the build meta-data more informative
    description = ('slot for testing {}, based on {}'.format(
        ', '.join(mr_link(mr, p) for mr, p in mrs.values()), model_slot.name))

    logger.info('Creating Ref Slot')
    logger.info('name: {}'.format(model_slot.name + '-ref'))
    # Build the reference slot and then freeze the external
    ref_slot = clone_slot(model_slot, model_slot.name + '-ref',
                          'MR reference ' + description, platforms)
    if not merge:
        set_last_commits(ref_slot, ref_date, {}, target_branch)

    logger.info('Creating Test Slot')
    logger.info('name: {}'.format(model_slot.name + '-mr'))
    # Build the test slot and then 'freeze' the external projects to be
    # the last possible commit before the last rebase of the MR
    # It is assumed the user can't have developed against code that
    # wasn't yet committed and they can always rebase
    test_slot = clone_slot(model_slot, model_slot.name + '-mr',
                           'MR test ' + description, platforms)
    # For the test slot now set the checkout opts to sync the project to
    # the latest commit on the MRs
    # NB this is why we can't support multiple interdependent MR on the
    # same project in a test build
    if not merge:
        for p, (mr, project) in mrs.items():
            commits[p] = mr.attributes['sha']
        set_last_commits(test_slot, ref_date, commits, target_branch)
    else:
        for p, (mr, project) in mrs.items():
            name = project.attributes['path']
            test_slot.projects[name].checkout_opts['merges'] = [
                mr.attributes['iid']
            ]

    return ref_slot, test_slot


@slot_factory
def make_mr_slots(config, model_slots):
    '''
    Create reference and testing slot for some merge requests

    @param config: Configuration speciftying the new slots and where
                   feedback should go.

    An example of `config` is
        {
        "sources": [
            "lhcb/Rec!1753"
        ],
        "trigger": {
            "merge_request_iid": 1753,
            "project_id": 401,
            "discussion_id": "d708ea762deae76f7d718eb0eefbc9b66c134190",
            "note_id": 2913001
        },
        "platforms": null,
        "merge": true,
        }

    '''
    logger.debug('make_mr_slots called with configuration\n' +
                 json.dumps(config, indent=2))
    if not config['sources']:
        raise ValueError('config["sources"] must contain at least one project')

    # Call the create_mr_slots main method
    ref_slot, test_slot = create_mr_slots(
        sources=config['sources'],
        platforms=config['platforms'],
        merge=config['merge'],
        model_slots=model_slots)
    return [ref_slot, test_slot]


def post_gitlab_feedback(ref_slot, test_slot, flavour, mr_slots_config):
    """Post feedback on GitLab using the build ids."""
    prefix = 'https://lhcb-nightlies.cern.ch/' + flavour
    message = ('Started [reference]({prefix}/{ref_slot}/build/{ref_build}) '
               'and [{mode} test]({prefix}/{test_slot}/build/{test_build}) '
               'builds. Once done, check the [comparison]({prefix}/compare/'
               '{test_slot}/{test_build}/{ref_slot}/{ref_build}) of build '
               'and test results.'.format(
                   prefix=prefix,
                   mode=('integration'
                         if mr_slots_config['merge'] else 'branch'),
                   ref_slot=ref_slot.name,
                   ref_build=ref_slot.build_id,
                   test_slot=test_slot.name,
                   test_build=test_slot.build_id))
    logger.info('GitLab feedback: {!r}'.format(message))
    if os.environ.get('GITLAB_TOKEN'):
        trigger_source = mr_slots_config['trigger']
        try:
            gitlab_server = _gitlabServer()
            project = gitlab_server.projects.get(trigger_source['project_id'])
            mr = project.mergerequests.get(trigger_source['merge_request_iid'])
            discussion = mr.discussions.get(trigger_source['discussion_id'])
            # reply to discussion
            discussion.notes.create({'body': message})
            # add a label to MR (creates a project label if not existing,
            # noop if already labeled)
            mr.labels.append('ci-test-triggered')
            mr.save()
        except gitlab.GitlabError as e:
            # never fail when feedback can't be posted
            logger.error('Could not post feedback to gitlab: ' + e.message)
            pass
