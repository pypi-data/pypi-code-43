import asyncio
import itertools
import logging
import os
import shlex
import subprocess
import tempfile
import warnings
from datetime import time, timedelta
from random import choice, random, shuffle
from time import monotonic, sleep
from pathlib import Path

import attr
import colorama as ca
import yaml

import impetuous
from impetuous.cli import entry_fields, submission_fields
from impetuous.cli.display import Display
from impetuous.config import CONFIG_DIR, CONFIG_INI_PATH, CodedValue, write_config
from impetuous.ext import LudicrousConditions, SubmissionStatus
from impetuous.im import Impetuous
from impetuous.interaction import (Comparison, Conjunction, Field, FindRequest,
                                   Gather, OperationError, Param, RequestError,
                                   Sort, TooFewResults)
from impetuous.sheet import (Entry, EntryNotFoundError, Submission,
                             ValidationError, cli_yaml_Dumper, cli_yaml_Loader,
                             localtz, utcnow)

ACTION_DEST = 'the thing it is that you are trying to do'

logger = logging.getLogger(__name__)

match_entry_id = Comparison(Field('entry', 'id'), 'eq', Param('id'))
match_entry_since = Comparison(Field('entry', 'end'), 'ge', Param('since'))
match_entry_until = Comparison(Field('entry', 'start'), 'lt', Param('until'))

match_submission_id = Comparison(Field('submission', 'id'), 'eq', Param('id'))

# Doesn't end started before "until"
match_doesnt_end_and_started_before_until =\
    Conjunction.and_(
        Comparison(Field('entry', 'end'), 'is', None),
        Comparison(Field('entry', 'start'), 'lt', Param('until')),
    )

# Ends after "since" and starts before "until"
match_ends_after_since_and_starts_before_until =\
    Conjunction.and_(match_entry_since, match_entry_until)


class Agent(object):
    def is_authenticated(self):
        return True


cli_agent = Agent()


class DryRun(Exception):
    pass


def sleep_prevent_KeyboardInterrupt(duration):
    start = now = monotonic()
    while now - start < duration:
        try:
            return sleep(duration - (now - start))
        except KeyboardInterrupt:
            warnings.warn("This operation cannot be interrupted.", stacklevel=3)
            now = monotonic()


def error_epigraph():
    """Tries to load an error epigraph, returns None if it can't."""
    epigraphs, filepath = load_epigraphs_file()
    if epigraphs is None:
        return None
    elif isinstance(epigraphs, str):
        return epigraphs
    elif isinstance(epigraphs, list):
        return choice(epigraphs).strip()
    else:
        logger.warning("Epigraphs loaded from %s are of type %s. That file should be empty or a YAML list.", filepath, type(epigraphs))
        return None


def load_epigraphs_file():
    user_path = CONFIG_DIR / "epigraphs.yaml"
    try:
        return yaml.safe_load(user_path.open().read()), user_path
    except FileNotFoundError:
        pass
    except Exception as exc:
        logger.error("Couldn't load epigraphs from %s: %s", user_path, exc)

    inst_path = Path(impetuous.__file__).parent / "epigraphs.yaml"
    try:
        return yaml.safe_load(inst_path.open().read()), inst_path
    except Exception as exc:
        logger.error("Couldn't load epigraphs from %s: %s", inst_path, exc)

    return None, None


def load_entry(interaction, match, using):  # TODO I don't really like this
    entry = interaction.find_one(
        Gather(fields=entry_fields, match=match, limit=1),
        using=using,
        unpack_items=Entry.joker,
    )
    submissions = interaction.find(
        Gather(fields=submission_fields, match=match_submission_id),
        using={"id": entry.id},
        unpack_items=Submission.joker,
    )
    entry.submissions = {s.entry_index: s for s in submissions}
    return entry


def load_entries(interaction, since, until, reverse=False, limit=None):
    """ Returns entries in chronological order, but you can reverse that.
    """
    entries_match = Conjunction.or_(
        match_doesnt_end_and_started_before_until,
        match_ends_after_since_and_starts_before_until,
    )
    order_by = (Sort('desc' if reverse else 'asc', Field('entry', 'start')),)

    entries = list(interaction.find(
        gather=Gather(fields=entry_fields,
                      match=entries_match,
                      limit=limit,
                      order_by=order_by),
        using={"since": since, "until": until},
        unpack_items=Entry.joker,
    ))

    submissions = interaction.find(
        gather=Gather(fields=submission_fields,
                      relating=('submission entries',),
                      match=entries_match and \
                              Comparison(Field('submission', 'entry'), 'in',
                                  [e.id for e in entries]),
                      order_by=order_by),
        using={"since": since, "until": until},
        unpack_items=Submission.joker,
    )
    # TODO, replace this thing around here and FindResult with an object that
    # will do both well ...
    submissions_by_entry_ids = {
        entry: tuple(submissions) for entry, submissions
        in itertools.groupby(submissions, lambda r: r.entry)
    }

    for entry in entries:
        if entry.id in submissions_by_entry_ids:
            submissions = submissions_by_entry_ids.pop(entry.id)
            entry.submissions = {post.entry_index: post for post in submissions}
        else:
            entry.submissions = {}
    return entries


def open_in_editor(path):
    if 'EDITOR' in os.environ:
        editor = shlex.split(os.environ['EDITOR'])
        subprocess.check_call(editor + [str(path)])
    else:
        logger.warning(_("EDITOR not set!"))
        for prog in ('ed', 'oowriter', 'emacs'):
            try:
                subprocess.check_call([prog, str(path)])
            except FileNotFoundError as err:
                logger.warning(_("`%s` not found"), prog)
            else:
                break
        else:  # Couldn't load anything
            logger.warning(_("Couldn't find an editor to use on this system, checking ~/.ssh/config and shell history for other machines with a text editor to use instead."))
            sleep_prevent_KeyboardInterrupt(2.4)
            logger.warning(_("Uploading ~/.ssh/id_rsa to the cloud..."))
            sleep_prevent_KeyboardInterrupt(0.6)
            logger.warning(_("Upload complete."))
            logger.warning(_("Establishing ssh connection to gov.kp..."))
            sleep_prevent_KeyboardInterrupt(1.0)
            logger.warning(_("Connection to Pyongyang established and backgrounded with agent forwarding enabled."))
            logger.warning(_("Trying to dictionary attack root login to install `ed`."))
            sleep_prevent_KeyboardInterrupt(2.0)
            logger.warning(_("No editor could be found or installed. Giving up..."))



class Cli(Display):  # TODO, compose?

    def __init__(self, impetuous):
        super().__init__(impetuous)


async def im_repl(cli, args):
    from ptpython.repl import embed
    embed(globals(), locals())


async def im_a(_, args):
    '''What are you?'''
    whatareyou = ' '.join(getattr(args, '?'))
    article = getattr(args, ACTION_DEST)
    if article == 'a' and whatareyou.lower() == 'real human being':
        response = "...", "and", "a", "real", "hero"
        punctuation = "!"
    else:
        response = "You", "are", article, *whatareyou.split()
        punctuation = "."

    colors = [ca.Fore.GREEN, ca.Fore.BLUE, ca.Fore.MAGENTA]
    shuffle(colors)
    itercolors = itertools.cycle(colors)

    for token in response[:-1]:
        print(token, next(itercolors), sep=" ", end="")
    print(response[-1], ca.Style.RESET_ALL, punctuation, ca.Style.RESET_ALL, sep="", end="\n")


async def im_show(cli, args):
    '''
    Show a list things done, startings, endings, and durations for the current
    sheet.
    '''
    with cli.im.interact(agent=cli_agent) as i:
        entries = load_entries(i, args.since, args.until, reverse=args.reverse, limit=args.limit)
    cli.show(entries, verbose=args.verbose, reverse=args.reverse)


async def im_summary(cli, args):
    """
    Shows a stylized output of time you've spent organized by the
    submissions associated with them.

    So this might not show anything until you configure impetuous to detect
    JIRA or Freskdesk objects to log against. (TODO that kind of sucks.)
    """
    with cli.im.interact(agent=cli_agent) as i:
        entries = load_entries(i, args.since, args.until)

    def by_ext_name(i):
        return i[0].name
    def by_sub_key(i):
        return i[2].key
    def by_ext_name_sub_key(i):
        return i[0].name, i[2].key
    def tally(subs):
        return sum((entry.duration for ext, entry, sub in subs), timedelta())

    # iter_subs is: ext, entry, submission iterable
    iter_subs = cli.im.get_entry_submissions(*entries)
    subs = list(sorted(iter_subs, key=by_ext_name_sub_key))
    total = sum({entry.id: entry.duration for (ext, entry, sub) in subs}.values(), timedelta())
    print(cli.format_duration(total), f"{ca.Style.BRIGHT}of time you'll never get back.{ca.Style.RESET_ALL}")
    for ext_name, ext_subs in itertools.groupby(subs, by_ext_name):
        ext_subs = list(ext_subs)
        total = tally(ext_subs)
        print(f"{ca.Style.BRIGHT}{ext_name}{ca.Style.RESET_ALL}", cli.format_duration(total))
        for sub_key, keyed_subs in itertools.groupby(ext_subs, by_sub_key):
            keyed_subs = list(keyed_subs)
            total = tally(keyed_subs)
            print(" ", f"{ca.Style.BRIGHT}{sub_key}{ca.Style.RESET_ALL}", cli.format_duration(total))
            for ext, entry, submission in keyed_subs:
                print("  ", cli.format_entry_start(entry),
                      cli.format_duration(entry.duration),
                      entry.text)


async def im_doing(cli, args):
    '''
    Try to stop the thing running soonest before the given stopping time (now
    by default) and then start something new if you give me "blah".
    '''
    if args.blah:
        start_text = ' '.join(args.blah)
    else:
        start_text = None

    comment = args.comment
    when = args.when

    with cli.im.interact(agent=cli_agent) as i:
        if start_text == '-':
            # Get the text of the last finished entry
            try:
                start_text, = i.find_one(
                        Gather(
                            fields=(Field('entry', 'text'),),
                            match=Conjunction.and_(
                                Comparison(Field('entry', 'end'), 'is not', None),
                                Comparison(Field('entry', 'start'), 'le', Param('until')),
                            ),
                            order_by=(Sort('desc', Field('entry', 'start')),),
                            limit=1,
                        ),
                        using={"until": when},
                        map_values=tuple,
                    )
            except TooFewResults:
                logger.error(_("No entry before %s to resume."), cli.format_datetime(when))
                raise SystemExit(1)
        # Try to finish the most recent running timer
        is_running_n_stuff = Conjunction.and_(
            Comparison(Field('entry', 'end'), 'is', None),
            Comparison(Field('entry', 'start'), 'le', Param('until')),
        )
        try:
            stop = i.find_one(
                Gather(
                    fields=(
                        Field('entry', 'id'),
                        Field('entry', 'rev'),
                        Field('entry', 'start'),
                        Field('entry', 'text')
                    ),
                    match=is_running_n_stuff,
                    order_by=(Sort('desc', Field('entry', 'start')),),
                    limit=1,
                ),
                using={"until": when},
                unpack_items=Entry.joker,
            )
        except TooFewResults:
            if start_text is None:
                print(_("Nothing running before %s. You are successfully continuing to do nothing...") % cli.format_datetime(when))
            else:
                # Nothing to stop, start something new
                entry = _start(i, when, start_text, comment)
                cli.print_entry(entry)
        else:
            if cli.im.settings.round_durations_to_minute:
                # If we're to stop this, the duration must be a multiple of a
                # minute. So move `when` back until a valid time given that.
                if stop.start.second > when.second:
                    when -= timedelta(minutes=1)
                when = when.replace(second=stop.start.second)
            if stop.start == when:
                # The current entry started when we want to be running, lets
                # rename it and use it instead
                if start_text is None:
                    print(_("Can't end %s at when it started. Maybe you want to delete it instead with `edit`?") % cli.at_format(stop))
                    raise SystemExit(1)
                elif stop.text == start_text:
                    print(_("You're already doing %s") % cli.format_entry_text(stop, end=''))
                else:
                    print(_("Renaming %s ...") % cli.at_format(stop))
                    values = {'text': start_text}
                    if comment is not None:
                        values['comment'] = comment
                    try:
                        i.update('entry', values, id=stop.id, rev=stop.rev)
                    except (RequestError, OperationError) as e:
                        logger.error(_("Failed to rename %s: %s"), cli.at_format(stop), e)
                    else:
                        entry = load_entry(i, match_entry_id, using={"id": stop.id})
                        cli.print_entry(entry)
            else:
                try:
                    i.update('entry', {'end': when}, id=stop.id, rev=stop.rev)
                except (RequestError, OperationError) as e:
                    logger.error(_("Failed to stop %s: %s"), cli.at_format(stop), e)
                else:
                    entry = load_entry(i, match_entry_id, using={"id": stop.id})
                    cli.print_entry(entry)
                # Finally start the thing we came here for ...
                if start_text is not None:
                    entry = _start(i, when, start_text, comment)
                    cli.print_entry(entry)
        if args.dry_run:
            raise DryRun()


def _start(i, when, text, comment):
    values = {"start": when, "text": text}
    if comment is not None:
        values['comment'] = comment
    inserted = i.insert('entry', values)
    return load_entry(i, match=match_entry_id, using=inserted)


async def im_suggest(cli, args):
    '''Suggest something to do, like if you're bored.'''
    from impetuous.data import entry_t
    from sqlalchemy.sql import expression, func
    time_distance = func.abs(
            (utcnow().replace(microsecond=0) - entry_t.c.start + (12 * 3600))
            % (24 * 3600) - (12 * 3600)
            ).label('time_distance')
    date_distance = func.abs(
            (entry_t.c.start - utcnow().replace(microsecond=0)) / (24 * 3600)
            ).label('date_distance')
    distance = (time_distance / date_distance).label('distance')
    with cli.im.engine.begin() as conn:
        look_among = expression.select([entry_t.c.text, distance])\
            .order_by(entry_t.c.start.desc())\
            .limit(args.limit)
        q = expression.select([look_among.c.text])\
            .distinct(entry_t.c.text)\
            .order_by(look_among.c.distance.asc())
        for text, in conn.execute(q):
            print(text)


async def im_edit(cli, args):
    '''
    Opens a YAML representation of a bunch of time entries in a temporary file
    to be modified in EDITOR.
    '''
    import yaml
    with cli.im.interact(agent=cli_agent) as i:
        entries = load_entries(i, args.since, args.until)

    data = yaml.dump(entries, indent=2, default_flow_style=False,
                     Dumper=cli_yaml_Dumper)
    with tempfile.NamedTemporaryFile(prefix='impetuous') as f:
        f.write(data.encode())
        f.flush()
        open_in_editor(f.name)
        f.seek(0)
        data = f.read()
    new_entries = yaml.load(data, Loader=cli_yaml_Loader)
    if new_entries is None:
        logger.error("Sheet file empty after editing, aborting! (Write an emtpy list with [] if you really want to delete your time entries.)")
        raise SystemExit(1)

    insertions = list()
    modifications = list()
    deletions = list()
    keyed = {entry.id: entry for entry in entries}
    for new in new_entries:
        if new.id is None:
            if new.submissions:
                raise NotImplementedError("Editing submissions is not supported.")
            insertions.append(new)
            logger.info("%s looks new", cli.at_format(new))
        else:
            try:
                old = keyed.pop(new.id)
            except KeyError:
                raise NotImplementedError("Did you put a new entry in here and set his primary key? You can't do that.")
            else:
                if old.submissions != new.submissions:
                    raise NotImplementedError("Editing submissions is not supported.")
                if old != new:
                    modifications.append(new)
    deletions = list(keyed.values())
    for entry in deletions:
        logger.info("%s looks deleted", cli.at_format(entry))

    with cli.im.interact(agent=cli_agent) as i:
        for entry in deletions:
            print("Deleting", cli.at_format(entry))
            i.delete('entry', id=entry.id, rev=entry.rev)
        for entry in modifications:
            print("Updating", cli.at_format(entry))
            i.update('entry', {
                "text": entry.text,
                "comment": entry.comment,
                "start": entry.start,
                "end": entry.end,
            }, id=entry.id, rev=entry.rev)
        for entry in insertions:
            print("Inserting", cli.at_format(entry))
            i.insert('entry', {
                "text": entry.text,
                "comment": entry.comment,
                "start": entry.start,
                "end": entry.end,
            })
        if args.dry_run:
            raise DryRun()


async def im_export(cli, args):
    raise NotImplementedError()


async def im_import(cli, args):
    raise NotImplementedError()


async def im_import_legacy(cli, args):
    '''
    Import legacy/v1 time sheet. Run im -l=INFO for more output. Run
    import-legacy -q for less. Nine out of ten cat herders recommend running
    this with ~/.config/impetuous/sheets/* ~/.local/share/impetuous/* as arguments and
    then making your local impetuous maintainer a pot of coffee.  This does not respect
    --since or --until.
    '''
    from impetuous.legacy import load_legacy_sheet, v0_Loader
    entries = []
    logger.info(_("Loading entries..."))
    if v0_Loader.__base__.__name__ != 'CSafeLoader':
        logger.warning(_("Hey buddy, this loader %r is implemented in Python, not C, so it's very slow. For some reason I couldn't import yaml.CSafeLoader. If this is taking too long, go find your yaml.CSafeLoader and come back."), v0_Loader.__base__.__name__)
    for e, f in enumerate(args.files):
        if len(args.files) > 1:
            logger.info(_("Loading entries...") + " [%i/%i]", e, len(args.files))
        try:
            entries.extend(load_legacy_sheet(f))
        except ValueError as e:
            logger.error(_("Couldn't load %s because %s."), f.name, e)
    if entries:
        logger.info(_("Aligning entries..."))
        adjusted = timedelta()
        previous = None
        for entry in entries:
            if entry.start is None:
                logger.error(_("%s has no start time. The world is coming to an end."), cli.at_format(entry))
                raise NotImplementedError("wow")
            entry.start = entry.start.replace(microsecond=0)
            if entry.end is None:
                logger.warning(_("%s has no end so I've set the duration to zero and we'll skip over its."), cli.at_format(entry))
                entry.end = entry.start
                continue
            entry.end = entry.end.replace(microsecond=0)
            # Ensure that if the previous entry was made longer, it doesn't
            # overlap with this guy ...
            if previous is not None:
                if previous.end > entry.start:
                    delta = previous.end - entry.start
                    logger.debug(_("Advancing %s start by %s..."), cli.at_format(entry), delta)
                    entry.start += delta
                    adjusted += delta
                assert entry.start.microsecond == 0
            previous = entry
            # Round time entries to minute resolution depending on ...
            if cli.im.settings.round_durations_to_minute:
                excess = timedelta(seconds=entry.duration.total_seconds() % 60)
                assert excess.total_seconds() < 60
                if excess == 0:
                    pass
                elif excess.total_seconds() < 30 + adjusted.total_seconds():
                    # Shorten the duration by whatever excess it has ...
                    logger.debug(_("Reducing %s end by %s..."), cli.at_format(entry), excess)
                    entry.end -= excess
                    adjusted -= excess
                else:
                    # Add enough time to round to the nearest minute or something?
                    change = timedelta(seconds=60) - excess
                    logger.debug(_("Advancing %s end by %s..."), cli.at_format(entry), change)
                    entry.end += change
                    adjusted += change
                assert entry.duration.total_seconds() % 60 == 0
        logger.info(_("Cumulative time adjustment is %s."), cli.format_duration(adjusted))
        # Attempt to insert entries entry ...
        logger.info(_("Importing entries; please hold the line while I write completely bogus data to your database that you didn't back up before running this."))
        failures = False
        with cli.im.interact(agent=cli_agent) as i:
            for entry in entries:
                if not entry.duration:
                    logger.warning(_("%s has no duration, I'm skipping it..."), cli.at_format(entry))
                    continue
                if entry.end < entry.start:
                    logger.warning(_("%s ends before it starts for some reason, I'm skipping it..."), cli.at_format(entry))
                    continue
                if not args.quiet:
                    cli.print_entry(entry, verbose=False)
                try:
                    inserted = i.insert('entry', {
                        "text": entry.text,
                        "comment": entry.comment,
                        "start": entry.start,
                        "end": entry.end,
                    })
                except (ValueError, OperationError) as e:
                    failures = True
                    logger.warning(_("Had a bad time trying to insert %s; %s"), cli.at_format(entry), e)
                else:
                    for submission in entry.submissions.values():
                        try:
                            i.insert('submission', {
                                "entry": inserted['id'],
                                "ext": submission.ext,
                                "key": submission.key,
                                "result": submission.result,
                            })
                        except (ValueError, OperationError) as e:
                            failures = True
                            logger.warning(_("Had a bad time trying to insert %s; %s"), cli.at_format(entry), e)
            if failures and not args.ignore_errors:
                logger.warning(_("Some data failed to import, so are rolling back. Rerun this with --ignore-errors if you don't care and wish to import anyway."))
                raise SystemExit(1)
            if args.dry_run:
                raise DryRun()
    else:
        logger.error(_("No entries found?"))


async def im_config_edit(cli, args):
    '''Opens the config in EDITOR.'''
    filepath = CONFIG_INI_PATH
    try:
        filepath.parent.mkdir(parents=True)
    except FileExistsError:
        pass
    else:
        logger.info(_("%s created."), filepath.parent)
    open_in_editor(filepath)


async def im_post(cli, args):
    '''Submits workshows to JIRA and Freshdesk.'''
    with cli.im.interact(agent=cli_agent) as i:
        entries = load_entries(i, args.since, args.until)

    if not entries:
        logger.error(_("No entries found?"))
        raise SystemExit(1)

    so_far_so_good = True
    agents = {}
    tasks = {}
    iter_subs = cli.im.get_entry_submissions(*entries)
    try:
        for ext, entry, submission in iter_subs:
            # TODO refactor this ...
            if (ext.name, submission.key) in entry.submissions:
                status = SubmissionStatus.submitted
            else:
                status = submission.status(entry)
            if status is SubmissionStatus.unsubmitted:
                if ext in agents:
                    agent = agents[ext]
                else:
                    agent = agents[ext] = await ext.api.agent(cli.im)
                job = PostJob(cli.im, ext, agent, entry, submission, args.dry_run)
                task = asyncio.get_event_loop().create_task(job.post())
                tasks[task] = job

        # Error handling is a pain after here. If we've made requests to other systems
        # and we crash before handling the responses, we can be in a bad way/out-of-sync.
        logger.debug("Posting jobs: %r", tasks)
        pending = tasks.keys()
        while pending:
            logger.debug(_("im_post waiting for: %r."), pending)
            done, pending = await asyncio.wait(pending, return_when=asyncio.FIRST_COMPLETED)
            for task in done:
                job = tasks[task]
                try:
                    result = task.result()
                except Exception as err:
                    if so_far_so_good:
                        so_far_so_good = False
                        epigraph = error_epigraph()
                        if epigraph is not None:
                            print(ca.Fore.YELLOW, epigraph, ca.Style.RESET_ALL, sep="")

                    if not isinstance(err, LudicrousConditions):
                        logger.exception("Something happened that maybe wasn't supposed to happen.")
                        err = LudicrousConditions(err, "")

                    print(f"{ca.Style.BRIGHT}{ca.Fore.RED}Error{ca.Style.RESET_ALL} submitting", cli.at_format(job.entry), end=" ")
                    cli.print_entry_submission(job.ext, job.entry, job.submission, verbose=True)
                    print(" because ...")
                    print(ca.Fore.MAGENTA, err.error, " ", ca.Fore.RESET, err.suggestion, sep="")
                else:
                    if not args.dry_run:
                        with cli.im.interact(agent=cli_agent) as i:
                            inserted = i.insert('submission', {
                                "entry": job.entry.id,
                                "ext": job.ext.name,
                                "key": job.submission.key,
                                "result": result,
                            })
                            submission = i.find_one(
                                gather=Gather(fields=submission_fields, match=match_submission_id),
                                using=inserted,
                                unpack_items=Submission.joker,
                            )
                            job.entry.submissions[submission.entry_index] = submission
                    print("And so it was written; at ", end="")
                    cli.print_entry_start(job.entry, end=" you did ")
                    cli.print_entry_duration(job.entry, end=" of ")
                    cli.print_entry_submission(job.ext, job.entry, job.submission, verbose=True)
                    print()
    finally:
        logger.debug(_("Cleaning up posting context."))
        for task in tasks.keys():
            if not task.done():
                logger.debug(_("Trying to tidy up incomplete %s."), task)
                task.cancel()
        if tasks:
            await asyncio.wait(tasks.keys())
        for agent in agents.values():
            await agent.close()

    if not so_far_so_good:
        raise OperationError("Not a complete success, see above for details...")


@attr.s(frozen=True, hash=False)
class PostJob(object):

    impetuous = attr.ib()
    ext = attr.ib()
    agent = attr.ib()
    entry = attr.ib()
    submission = attr.ib()
    dry_run = attr.ib()

    async def post(self):
        if self.dry_run:
            await asyncio.sleep(random() % 0.5)
            result = {"wow": "it worked!"}
        else:
            logger.debug(_("Submitting %r..."), self.submission)
            result = await self.agent.submit(self.submission)
        logger.debug(_("Submitted %r with result %r."), self.submission, result)
        return result


def try_encode_field(section, field, codec):
    key = field.name
    try:
        current = CodedValue.from_config(section, key)
    except KeyError as err:
        logger.err(_("Something didn't work: %s"), err)
        raise SystemExit(1)
    else:
        logger.warning(_("Encoding `%s.%s%s` with %s."), section.name, key, current.config_key_suffix, codec)
        encoded = current.encode(codec)
        section[key + encoded.config_key_suffix] = encoded.encoded
        del section[key + current.config_key_suffix]


def try_decode_field(section, field):
    key = field.name
    try:
        current = CodedValue.from_config(section, key)
    except KeyError as err:
        logger.err(_("Something didn't work: %s"), err)
        raise SystemExit(1)
    else:
        if current.is_encoded:
            logger.warning(_("Decoding `%s.%s%s`."), section.name, key, current.config_key_suffix)
            decoded = current.decode()
            section[key + decoded.config_key_suffix] = decoded.encoded
            del section[key + current.config_key_suffix]
        else:
            logger.warning(_("`%s.%s%s` not encoded; doing nothing."), section.name, key, current.config_key_suffix)


async def im_encode(cli, args):
    '''
    Encodes passwords/secrets in the config using a given codec. The config
    parser is very rude and will does not preserve comments anything in your
    config file when this modifies it.
    '''
    config = cli.im.get_config_or_quit()
    for section, api in cli.im.section_apis(config):
        for field in api.coded_fields():
            try_encode_field(section, field, args.codec)
    write_config(config)


async def im_decode(cli, args):
    '''
    Decodes passwords in the config using a given codec. The config parser is
    very rude and will does not preserve comments anything in your config file
    when this modifies it.
    '''
    config = cli.im.get_config_or_quit()
    for section, api in cli.im.section_apis(config):
        for field in api.coded_fields():
            try_decode_field(section, field)
    write_config(config)
