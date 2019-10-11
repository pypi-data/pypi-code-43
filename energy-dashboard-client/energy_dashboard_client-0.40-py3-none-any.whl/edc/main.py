# edc : Energy Dashboard Command Line Interface
# Copyright (C) 2019  Todd Greenwood-Geer (Enviro Software Solutions, LLC)
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from edl.cli import feed as clifeed
from edl.cli import feeds as clifeeds
from edl.cli import repo as clirepo
from edl.resources.exec import runyield
from edl.resources import filesystem as fs
from edl.resources import xmlparser
from edl.resources import log
import click
import os
import sys
import logging
import copy

# CTX OBJ KEYS
EDDIR           ='eddir'
LOGGER          ='logger'
FEED            ='feed'

@click.group()
@click.option('--ed-dir', help="Energy Dashboard directory (defaults to cwd)")
@click.option('--log-level', type=click.Choice(log.LOG_LEVELS), default="INFO")
@click.pass_context
def cli(ctx,  ed_dir, log_level):
    """
    Command Line Interface for the Energy Dashboard. This tooling 
    collects information from a number of data feeds, imports that data, 
    transforms it, and inserts it into a database.
    """
    # pass this logger as a child logger to the edl methods
    log.configure_logging()
    logger = logging.getLogger(__name__)
    logger.setLevel(log_level)
    log.debug(logger, {
        "name"      : __name__,
        "method"    : "cli",
        "ed_dir"    : ed_dir,
        "log_level" : "%s" % log_level})

    if ed_dir is None:
        ed_dir = os.path.curdir
    else:
        if not os.path.exists(ed_dir):
            log.critical(logger, {
                "name"      : __name__,
                "method"    : "cli",
                "ed_dir"    : ed_dir,
                "CRITICAL"  : "ed_dir does not exist"
                })
    eddir = os.path.abspath(os.path.expanduser(ed_dir))
    ctx.obj = {
            LOGGER          : logger,
            EDDIR           : eddir
            }

#------------------------------------------------------------------------------
# License
#------------------------------------------------------------------------------
@cli.command()
def license():
    """
    Show the license (GPL v3).
    """
    click.echo("""    
    edc : Energy Dashboard Command Line Interface
    Copyright (C) 2019  Todd Greenwood-Geer (Enviro Software Solutions, LLC)

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
    """)

#------------------------------------------------------------------------------
# Init
#------------------------------------------------------------------------------
@cli.command('clone', short_help="Clone energy-dashboard locally")
@click.pass_context
def repo_clone(ctx):
    """
    Use git to clone the energy-dashboard locally.
    
    Clone operation(s):

        git clone ... [current_directory]/energy-dashboard
    or
        git clone ... [--ed-dir]/energy-dashboard

    After cloning, use the 'update' command to bring in
    all the data in the submodules.
    """
    logger  = ctx.obj[LOGGER]
    path = ctx.obj[EDDIR]
    for output in clirepo.clone(logger, path):
        click.echo(output)

@cli.command('update', short_help="Update the submodules")
@click.pass_context
def repo_update(ctx):
    """
    Update the submodules that have been previously cloned
    via the 'clone' command.
    """
    logger  = ctx.obj[LOGGER]
    path = ctx.obj[EDDIR]
    for output in clirepo.update(logger, path):
        click.echo(output)

#------------------------------------------------------------------------------
# Feeds (plural)
#------------------------------------------------------------------------------
@cli.group()
@click.pass_context
def feeds(ctx):
    """
    Manage the full set of data 'feeds' (plural).
    """
    pass

@feeds.command('list', short_help='List feeds')
@click.pass_context
def feeds_list(ctx):
    """
    List feeds by name. Feeds are implemented as submodules under the energy-dashboard/data directory.
    """
    logger  = ctx.obj[LOGGER]
    path = ctx.obj[EDDIR]
    for item in clifeeds.list(logger, path):
        click.echo(item)

@feeds.command('search', short_help='Search feeds (NYI)')
def feeds_search():
    """
    NYI -- implement a full text search against the feed's manifest.json
    """
    pass

#------------------------------------------------------------------------------
# Feed (singular)
#------------------------------------------------------------------------------
@cli.group()
@click.argument('feed')
@click.pass_context
def feed(ctx, feed):
    """
    Manage individual 'feed' (singular).
    """
    ctx.obj[FEED] = feed

@feed.command('dir', short_help='Feed directory')
@click.pass_context
def feed_dir(ctx):
    feed    = ctx.obj[FEED]
    path    = ctx.obj[EDDIR]
    logger  = ctx.obj[LOGGER]
    click.echo(os.path.join(path, "data", feed))

@feed.command('create', short_help='Create new feed')
@click.option('--maintainer',   default="Sarah Connor")
@click.option('--company',      default="robots.com")
@click.option('--email',        default="sc@robots.com")
@click.option('--url',          default="http://datafeeds.robots.com/feed01")
@click.option('--start-date-year', '-sdy',  help="Start date year, e.g. 2013", default=2019, type=int)
@click.option('--start-date-month', '-sdm', help="Start date month, e.g. 12", default=1, type=int)
@click.option('--start-date-day', '-sdd',   help="Start date day, e.g. 1", default=1, type=int)
@click.option('--delay',          default=5, help="Delay between downloads", type=int)
@click.pass_context
def feed_create(ctx, maintainer, company, email, url, start_date_year, start_date_month, start_date_day, delay):
    """
    Create a new data feed from a template.
 
    Arguments:
        feed        : name of the feed (lower case alpha-numeric with dashes)
        maintainer  : name of the feed curator
        company     : name of the company or organization the owner belongs to
        url         : data feed url, with replacement strings in url (see below)

    URL Replacements:
        
        The default tooling generates a URL for each day between the _START_
        date, and today. This makes it trivial to download daily resources from
        a target URL for the past N years.  Other use cases are supported, too.
        The default tooling can be overriden in the generated `src/10_down.py`
        script. 
        
        For the default behaviour, ensure that the data feed URL has the
        following replacement strings:

        _START_
        _END_

        Example:

            "url": "http://oasis.caiso.com/oasisapi/SingleZip?queryname=AS_MILEAGE_CALC&anc_type=ALL&startdatetime=_START_T07:00-0000&enddatetime=_END_T07:00-0000&version=1",
    """
    feed    = ctx.obj[FEED]
    path    = ctx.obj[EDDIR]
    logger  = ctx.obj[LOGGER]
    click.echo(clifeed.create(
        logger, path, feed, maintainer, 
        company, email, url, 
        [start_date_year, start_date_month, start_date_day], 
        delay))


@feed.command('invoke', short_help='Invoke a shell command in the feed directory')
@click.argument('command')
@click.pass_context
def feed_invoke(ctx, command):
    """
    CD to feed directory, and invoke command.

    Coupled with the `feeds list` command, the `feed invoke` command allows advanced
    processing on the feeds in the data directory:

    Example:
    # print the 'url' of all the feeds with 'atl' in the name

    $ edc feeds list | grep atl | xargs -L 1 -I {} edc feed invoke {} "jq .url < manifest.json"
    "http://oasis.caiso.com/oasisapi/SingleZip?queryname=ATL_GEN_CAP_LST&startdatetime=_START_T07:00-0000&enddatetime=_END_T07:00-0000&version=4"
    "http://oasis.caiso.com/oasisapi/SingleZip?queryname=ATL_HUB&startdatetime=_START_T07:00-0000&enddatetime=_END_T07:00-0000&version=1"
    "http://oasis.caiso.com/oasisapi/SingleZip?queryname=ATL_OSM&msg_severity=ALL&startdatetime=_START_T07:00-0000&enddatetime=_END_T07:00-0000&version=1"
    "http://oasis.caiso.com/oasisapi/SingleZip?queryname=ATL_PEAK_ON_OFF&startdatetime=_START_T07:00-0000&enddatetime=_END_T07:00-0000&version=1"
    
    Example:
    # dump record count
    $ edc feeds list | grep mileage | xargs -L 1 -I {} edc feed invoke {} "echo {}; sqlite3 db/{}.db 'select count(*) from oasis'"
    data-oasis-as-mileage-calc-all
    42
    """
    feed    = ctx.obj[FEED]
    path    = ctx.obj[EDDIR]
    logger  = ctx.obj[LOGGER]
    for output in clifeed.invoke(logger, feed, path, command):
        click.echo(output)


@feed.command('status', short_help='Show feed status')
@click.option('--separator', '-s', default=',')
@click.option('--header/--no-header', default=True)
@click.pass_context
def feed_status(ctx, separator, header):
    """
    Return the feed status as:

        "feed name","download count","unzipped count","inserted count", "db count"
    """
    feed    = ctx.obj[FEED]
    path    = ctx.obj[EDDIR]
    logger  = ctx.obj[LOGGER]
    for line in clifeed.status(logger, feed, path, separator, header):
        click.echo(line)

@feed.command('prune', short_help='prune feed stage')
@click.argument('stages', nargs=-1)
@click.option('--confirm/--no-confirm', default=True)
@click.pass_context
def feed_prune(ctx, stages, confirm):
    """
    !!!USE WITH CAUTION!!!

    prune a stage. This is a destructive action, make backups first!.
    This will delete the stage files, but not the directory and not
    the state file.

    !!!USE WITH CAUTION!!!

    Stages are: ['download', 'unzip', 'parse' ]

    """
    feed    = ctx.obj[FEED]
    path    = ctx.obj[EDDIR]
    logger  = ctx.obj[LOGGER]

    valid_stages    = ['download', 'unzip', 'parse']
    all_stages      = copy.copy(valid_stages)
    vstages = [filter_input_to_stage(all_stages, stage) for stage in stages]

    for stage in vstages:
        if confirm:
            p = clifeed.pre_prune(logger, feed, path, stage)
            if click.confirm('About to prune: %s. Do you want to continue?' % p):
                click.echo(clifeed.prune(logger, feed, path, stage))
        else:
            click.echo(clifeed.prune(logger, feed, path, stage))

@feed.command('reset', short_help='Reset feed stage')
@click.argument('stages', nargs=-1)
@click.option('--confirm/--no-confirm', default=True)
@click.pass_context
def feed_reset(ctx, stages, confirm):
    """
    !!!USE WITH CAUTION!!!

    Reset a stage. This is a destructive action, make backups first!.
    This will delete the stage directory, including the state file and
    all the processed resources.

    !!!USE WITH CAUTION!!!

    Stages are: ['download', 'unzip', 'parse', 'insert', 'dist']

    """
    feed    = ctx.obj[FEED]
    path    = ctx.obj[EDDIR]
    logger  = ctx.obj[LOGGER]

    valid_stages    = ['download', 'unzip', 'parse', 'insert', 'dist']
    all_stages      = copy.copy(valid_stages)
    all_stages.append('all')
    vstages = [filter_input_to_stage(all_stages, stage) for stage in stages]

    if 'all' in vstages:
        vstages = valid_stages

    for stage in vstages:
        if confirm:
            p = clifeed.pre_reset(logger, feed, path, stage)
            if click.confirm('About to delete: %s. Do you want to continue?' % p):
                click.echo(clifeed.reset(logger, feed, path, stage))
        else:
            click.echo(clifeed.reset(logger, feed, path, stage))

@feed.command('archive', short_help='Archive feed to tar.gz')
@click.option('--archivedir', help="Path to save archive", required=False, default="archive")
@click.pass_context
def feed_archive_to_targz(ctx, archivedir):
    """
    Archive a feed. Especially useful before a destructive action like:
    'feed X reset'

    If archivedir starts with "/" then this is an absolute path.
    """
    feed    = ctx.obj[FEED]
    path    = ctx.obj[EDDIR]
    logger  = ctx.obj[LOGGER]
    click.echo(clifeed.archive_locally(logger, feed, path, archivedir))

@feed.command('restore', short_help='Restore feed from tar.gz')
@click.argument('archive', type=click.Path(exists=True))
@click.pass_context
def feed_restore_from_targz(ctx, archive):
    """
    Restore a feed from an archive.

    archive : tar.gz to restore
    """
    feed    = ctx.obj[FEED]
    path    = ctx.obj[EDDIR]
    logger  = ctx.obj[LOGGER]
    click.echo(clifeed.restore_locally(logger, feed, path, archive))


@feed.command('proc', short_help='Process a feed through the provided stage in ./src')
@click.argument('stages', nargs=-1)
@click.pass_context
def feed_procstage(ctx, stages):
    """
    Process the feed through the stages.

    If stage is 'all' then all stages will be processed.

    Otherwise the stage argument can be any combination of these stages:

        ['download', 'unzip', 'parse', 'insert', 'save', 'dist', 'arch']

    """
    feed    = ctx.obj[FEED]
    path    = ctx.obj[EDDIR]
    logger  = ctx.obj[LOGGER]

    valid_stages = copy.copy(clifeed.STAGES)
    all_stages = copy.copy(valid_stages)
    all_stages.append('all')
    vstages = [filter_input_to_stage(all_stages, stage) for stage in stages]
    
    if 'all' in vstages:
        vstages = valid_stages

    for sout in clifeed.process_stages(logger, feed, path, vstages):
        for output in sout:
            for output2 in output:
                click.echo(output)

#@feed.command('procfile', short_help='Process a file through the stages in ./src')
#@click.argument('stage')
#@click.pass_context
#def feed_procfile(ctx, stage):
#    """
#    Process a single file through the feed's stage procesing file in the './src' 
#    directory.
#
#    Stages are: ['download', 'unzip', 'parse', 'insert', 'save', 'all']
#
#    """
#
#    procstages = copy.copy(clifeed.STAGES)
#    procstages.extend(['all'])
#    stage = filter_input_to_stage(procstages, stage)
#    feed    = ctx.obj[FEED]
#    path    = ctx.obj[EDDIR]
#    logger  = ctx.obj[LOGGER]
#    # TODO: invoke a proc file on an individual input file accross the stages



@feed.command('s3archive', short_help='Archive feed to S3 bucket')
@click.option('--service', '-s', type=click.Choice(['wasabi', 'digitalocean',]), default='wasabi')
@click.pass_context
def feed_archive_to_s3(ctx, service):
    """
    Archive feed to an S3 bucket.
    """
    feed    = ctx.obj[FEED]
    path    = ctx.obj[EDDIR]
    logger  = ctx.obj[LOGGER]
    for output in clifeed.archive_to_s3(logger, feed, path, service):
        click.echo(output)


@feed.command('s3restore', short_help='Restore feed from from S3 bucket')
@click.option('--service', '-s', type=click.Choice(['wasabi', 'digitalocean',]), default='wasabi')
@click.pass_context
def feed_restore_from_s3(ctx, service):
    """
    Restore from dist files on S3:

        [s3]/zip/*.zip      -> [feed]/zip/*.zip
        [s3]/db/*.db.7z     -> [feed]/db/*.db   (decompresses after file transfer)
        
    """
    feed            = ctx.obj[FEED]
    path            = ctx.obj[EDDIR]
    logger          = ctx.obj[LOGGER]

    for output in clifeed.restore_from_s3(logger, feed, path, service):
        click.echo(output)

@feed.command('s3urls', short_help='Urls to download artifacts from S3 bucket')
@click.option('--service', '-s', type=click.Choice(['wasabi', 'digitalocean',]), default='wasabi')
@click.pass_context
def feed_s3_urls(ctx, service):
    """
    Urls to download artifacts from S3 bucket
    """
    feed            = ctx.obj[FEED]
    path            = ctx.obj[EDDIR]
    logger          = ctx.obj[LOGGER]

    for (url, target) in clifeed.s3_artifact_urls(logger, feed, path, service):
        click.echo(url)

#------------------------------------------------------------------------------
# Feed.Manifest (singular)
#------------------------------------------------------------------------------
@feed.group()
def db():
    """
    Manage a feed's database(s).
    """
    pass

@db.command('createddl')
@click.option("--xmlfile", "-x", help="File to scan")
@click.option("--save/--no-save", default=False, help="Save ddl to manifest")
@click.pass_context
def feed_db_create_ddl(ctx, xmlfile, save):
    """
    Generate SQL DDL for table creation.

    If no xmlfile is provided, looks at the newest xml file in the feed.
    """
    feed    = ctx.obj[FEED]
    path    = ctx.obj[EDDIR]
    logger  = ctx.obj[LOGGER]
    click.echo(clifeed.create_and_save_ddl(logger, feed, path, xmlfile, save))

@db.command('insertsql')
@click.argument('xmlfile')
@click.pass_context
def feed_db_generate_insertion_sql(ctx, xmlfile, save):
    """
    Generate SQL for data insertion into table.

    This is really just for testing.
    """
    feed    = ctx.obj[FEED]
    path    = ctx.obj[EDDIR]
    logger  = ctx.obj[LOGGER]
    click.echo(clifeed.generate_insertion_sql(logger, feed, path, xmlfile))

@db.command('list', short_help='List the feed databases')
@click.pass_context
def feed_database_console(ctx):
    """
    A feed may have multiple databases if the schema has changed.

    List the available databases with a number for use with the 'console'
    command.
    """
    feed    = ctx.obj[FEED]
    path    = ctx.obj[EDDIR]
    logger  = ctx.obj[LOGGER]
    feed_dir    = os.path.join(path, 'data', feed)
    db_dir      = os.path.join(feed_dir, "db")
    dbs     = fs.glob_dir(db_dir, ".db")
    for db in dbs:
        click.echo("%s\n" % db)

@db.command('console', short_help='launch sqlite3 database console')
@click.argument('db')
@click.pass_context
def feed_database_console(ctx, db):
    """
    Display the feed manifest.
    """
    feed    = ctx.obj[FEED]
    path    = ctx.obj[EDDIR]
    logger  = ctx.obj[LOGGER]
    feed_dir    = os.path.join(path, 'data', feed)
    fqp_db  = os.path.join(feed_dir, "db", db)
    os.system("sqlite3 %s" % fqp_db)

#------------------------------------------------------------------------------
# Feed.Manifest (singular)
#------------------------------------------------------------------------------
@feed.group()
def manifest():
    """
    Manage a feed's manifest.
    """
    pass

@manifest.command('show', short_help='Display the feed manifest')
@click.pass_context
def feed_manifest_show(ctx):
    """
    Display the feed manifest.
    """
    feed    = ctx.obj[FEED]
    path    = ctx.obj[EDDIR]
    logger  = ctx.obj[LOGGER]
    feed_dir    = os.path.join(path, 'data', feed)
    manifest    = os.path.join(feed_dir, 'manifest.json')
    with open(manifest, 'r') as f:
        for line in f:
            click.echo(line.rstrip())

@manifest.command('update', short_help='Update the feed manifest')
@click.option('--field', '-f', help="Field to update")
@click.option('--value-str', help="Value to update item to", type=str)
@click.option('--value-int', help="Value to update item to", type=int)
@click.pass_context
def feed_manifest_update(ctx, field, value_str, value_int):
    """
    Update the manifest.field with the value provided.
    """
    feed    = ctx.obj[FEED]
    path    = ctx.obj[EDDIR]
    logger  = ctx.obj[LOGGER]
    clifeed.manifest_update(logger, feed, path, field, value_str, value_int)

def filter_input_to_stage(valid_stages, s):
    """
    Typically stages = clifeed.STAGES, and 's' is a particular stage
    """
    for vstage in valid_stages:
        if vstage.startswith(s):
            return vstage
    click.echo("ERROR: invalid stage argument '%s'; stages must be (or start with letters from) one of these stages: %s" % (s, valid_stages))
    sys.exit(1)
