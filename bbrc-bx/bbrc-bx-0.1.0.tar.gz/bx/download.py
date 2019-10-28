import shutil
import os
import os.path as op
import tempfile
import logging as log

def get_validation_report(x, e, report_name):
    r = x.select.experiment(e).resource('BBRC_VALIDATOR')
    pdf = {each.label():each for each in list(r.files()) \
        if report_name in each.label() and \
        each.label().endswith('.pdf')}

    if not r.exists():
        log.error('%s has no BBRC_VALIDATOR resource'%e)
        return None
    if len(pdf.items()) == 0:
        log.error('%s has no %s'%(e, report_name))
        return None

    assert(len(list(pdf.keys())) == 1)
    f = pdf[list(pdf.keys())[0]]
    return f

def download_experiment(x, e, resource_name, validation_report, overwrite,
        destdir):
    if not resource_name is None:
        r = x.select.experiment(e).resource(resource_name)
        if not r.exists():
            log.error('%s has no %s resource'%(e, resource_name))
            return
        dd = op.join(destdir, e)
        if op.isdir(dd) and not overwrite:
            msg = '%s already exists. Skipping %s.'%(dd, e)
            log.error(msg)
        else:
            if op.isdir(dd) and overwrite:
                msg = '%s already exists. Overwriting %s.'%(dd, e)
                log.warning(msg)

            os.mkdir(dd)
            r.get(dest_dir=dd)

    f = get_validation_report(x, e, validation_report)
    if not f is None:
        fp = op.join(destdir, f.label()) if resource_name is None \
            else op.join(dd, f.label())
        if resource_name is None:
            log.debug('Saving it in %s.'%fp)
            f.get(dest=fp)
