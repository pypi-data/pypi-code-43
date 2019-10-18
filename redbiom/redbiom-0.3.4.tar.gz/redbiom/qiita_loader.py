import qiita_db
from collections import defaultdict
import redbiom.admin
import json
import hashlib
import logging

logger = logging.getLogger(__name__)


def usable_artifacts(artifacts):
    """We only retain artifacts which are processed and are BIOM"""
    arts = []
    for art in artifacts:
        if art.processing_parameters is None:
            continue
        if art.artifact_type != 'BIOM':
            continue
        arts.append(art)
    return arts


def get_name_and_description(art):
    """Determine the context the artifact is associated with

    The name is based off the processing parameters command name. This name
    is tagged with a stable hash based on the processing parameter values
    so that a common type of processing (e.g., pick closed reference OTUs) can
    be safely partitioned by the specific runtime parameters. The runtime
    parameters themselves are returned as a description of the context.
    """
    proctype = art.processing_parameters.command.name
    parent = art.parents[0]

    if parent.processing_parameters.command.name == 'Trimming':
        trim = parent.processing_paramters.command.parameters['length'][-1]
        proctype = "%s-%snt" % (proctype, trim)

    desc = art.processing_parameters.command.parameters
    desc = json.dumps(sorted(desc))
    desc_tag = hashlib.md5(desc).hexdigest()[:6]

    context_name = "%s-%s" % (proctype.replace(' ', '_'), desc_tag)
    return context_name, desc


def get_biom_path(art):
    """Get the BIOM path to load"""
    biompath = None
    for _, fp, fptype in art.filepaths:
        if fptype == 'biom':
            if art.processing_parameters.command.name == 'deblur-workflow':
                if not fp.endswith('final.only-16s.biom'):
                    continue
            biompath = fp
    return biompath

load_stats = defaultdict(int)


for study in qiita_db.study.Study.get_by_status('public'):
    if study.sample_template is not None:
        artifacts = usable_artifacts(study.artifacts())

        # if we don't have artifacts, then there isn't a reason to go on.
        if not artifacts:
            continue

        load_stats['studies'] += 1

        df = study.sample_template.to_dataframe()

        n_loaded = redbiom.admin.load_sample_metadata(df)
        msg = "Loaded metedata for %d samples from study %d" % (n_loaded,
                                                                study.id)
        logger.info(msg)
        load_stats['sample-metadata'] += n_loaded

        for art in artifacts:
            context, description = get_context_name_and_description(art)
            redbiom.admin.create_context(context, description)

            # An artifact may be composed of multiple preps. Construct a
            # tag which represents all the prep IDs.
            prepids = [str(p.id) for p in art.prep_templates]
            preptag = '#'.join(prepids)

            biompath = get_biom_path(art)
            if biompath is None:
                logger.warn("No usable BIOM path for artifact %d" % art.id)
                continue

            table = biom.load_table(biompath)

            nobs = redbiom.admin.load_observations(table, context, preptag)
            msg = "Loaded observations from %d samples, for prep IDs %s, "
                  "in study %d, into context %s" % (n, ','.join(prepids),
                                                    study.id, context)
            logger.info(msg)
            load_stats['%s-n-samples-in-observations' % context] += nobs

            nsdat = redbiom.admin.load_sample_data(table, context, preptag)
            msg = "Loaded sample data from %d samples, for prep IDs %s, "
                  "in study %d, into context %s" % (n, ','.join(prepids),
                                                    study.id, context)
            logger.info(msg)
            load_stats['%s-n-sample-data' % context] += nsdat

            if nsdat != nobs:
                msg ("Sample data and observation data loaded different "
                     "numbers of samples: %d and %d" % (nsdat, nobs))
                logger.warn(msg)


for k, v in sorted(load_stats.items()):
    print("Loading stats:\n")
    print("%s: %d" % (k, v))
