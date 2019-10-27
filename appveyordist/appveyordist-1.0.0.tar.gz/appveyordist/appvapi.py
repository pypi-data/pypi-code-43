"""Library routines for pulling from appveyor"""
import typing, logging, requests, os
log = logging.getLogger(__name__)

BASE_URL = 'https://ci.appveyor.com/api/%(entry_point)s'

def appveyor_api( entry_point, timeout=15, session=None ):
    """Pull json from the given appveyor sub-entry-point"""
    url = BASE_URL%locals()
    entry_point = entry_point.lstrip('/')
    response = (session or requests).get( url, headers={'Content-Type':'application/json'}, timeout=timeout )
    response.raise_for_status()
    try:
        return response.json()
    except Exception as err:
        raise RuntimeError("Failed to parse the response: %s"%(response.text))

def get_last_build(username, project, session=None):
    return appveyor_api(
        '/projects/%(username)s/%(project)s'%locals(),
        session=session,
    )['build']

def get_artifacts( job, session=None ):
    """Get the list of artfacts for a given job"""
    job_id = job['jobId']
    return appveyor_api('/buildjobs/%(job_id)s/artifacts'%locals(),session=session) 

def latest_build_artifacts( username, project, build=None, session=None ):
    """Get the latest build artifact records from the given project"""
    if build is None:
        build = get_last_build( username, project, session=session, )
    return build_artifacts(username, project, build, session=session )

def build_artifacts(username, project, build, session=None):
    log.info('Branch: %s Commit: %s', build['branch'], build['commitId'])
    log.info("Message: %s", build['message'])
    # log.debug("Build record: %s", build)
    # log.info("Jobs: %s", jobs)
    session = requests.session
    for job in build.get('jobs'):
        log.debug("Job record: %s", job)
        if job.get('status') != 'success':
            log.warning("Job %s in status %r", job['name'], job['status'])
            continue 
        log.info("%s has %s artifacts", job['name'], job['artifactsCount'])
        job_id = job['jobId']
        artifacts = get_artifacts(job)
        # log.debug("Artifacts: %s", artifacts)
        for artifact in artifacts:
            log.debug("Found artifact: %s", artifact)
            filename = artifact['fileName']
            base = os.path.basename(filename)
            entry_point =  '/buildjobs/%(job_id)s/artifacts/%(filename)s'%locals()
            final_url = BASE_URL%locals()
            yield base, final_url

