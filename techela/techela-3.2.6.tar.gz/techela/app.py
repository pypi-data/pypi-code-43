"""A flask of techela."""

import argparse
from datetime import datetime
from email import encoders
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import glob
import os
import json
import random
import shutil
import smtplib
import subprocess
import sys
import time
import urllib
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from flask import Flask, render_template, redirect, url_for, request
from techela import __version__
import webbrowser


parser = argparse.ArgumentParser(description='Open techela.')
parser.add_argument('course_id', nargs='?', default=None, help='The course id')
parser.add_argument('--debug', help='Print debug info', action='store_true')
parser.add_argument('-v', action='store_true', help='Print version and exit.')

args = parser.parse_args()

COURSE = args.course_id
COURSEDIR = os.path.expanduser(f'~/.techela/{COURSE}/')
COURSEREPO = f'https://github.com/jkitchin/{COURSE}'

if args.v:
    print(f'Techela version {__version__}')
    sys.exit()

if args.debug:
    print(COURSEDIR)
    sys.exit()

if not args.course_id:
    raise Exception('You must provide a course id.')

if not os.path.isdir(os.path.expanduser(f'~/.techela/')):
    os.makedirs(os.path.expanduser(f'~/.techela/'))

if not os.path.isdir(COURSEDIR):
    # We have not cloned before and need to.
    cpe = subprocess.run(['git',
                          'clone',
                          COURSEREPO,
                          COURSEDIR],
                         check=True)


with open(os.path.join(COURSEDIR, 'course-data.json'), encoding="utf-8") as f:
    COURSEDATA = json.loads(f.read())

if os.path.exists(os.path.join(COURSEDIR, 'local-course-data.json')):
    with open(os.path.join(COURSEDIR, 'local-course-data.json'),
              encoding="utf-8") as f:
        COURSEDATA.update(json.loads(f.read()))

try:
    wb = webbrowser.get('chrome')
    BROWSER = '--browser=chrome'
except:
    print('Unable to locate chrome!!!!')
    BROWSER = None


# cmd to run jupyter notebook. I use this instead of "jupyter notebook" because
# in the way jupyter was installed on the student laptops, jupyter was not
# executable, and this was.
JUPYTER = 'jupyter-notebook'


app = Flask(__name__)


BOX_EMAIL = COURSEDATA['submit-email']

# This file contains user data, andrew id, name
USERCONFIG = f'{COURSEDIR}/techela.json'

# This is to store Popen instances
NOTEBOOKS = []


def get_course_data():
    '''Return dictionary of course data.'''
    lectures = sorted(glob.glob(f'{COURSEDIR}/lectures/*.ipynb'))
    assignments = glob.glob(f'{COURSEDIR}/assignments/*.ipynb')
    solutions = glob.glob(f'{COURSEDIR}/solutions/*.ipynb')

    # the assignments are like assignments/label.ipynb
    assignment_data = {}
    for assignment in assignments:
        with open(assignment, encoding="utf-8") as f:
            j = json.loads(f.read())
            duedate = None
            md = j.get('metadata', None)
            if md:
                org = md.get('org', None)
                if org:
                    duedate = org.get('DUEDATE', None)
                    grader = org.get('GRADER', None)
                    points = org.get('POINTS', '?')
                    category = org.get('CATEGORY', '?')
                    label = os.path.splitext(os.path.split(assignment)[-1])[0]
        assignment_data[f'assignments/{label}.ipynb'] = {'label': label,
                                                         'duedate': duedate,
                                                         'points': points,
                                                         'category': category,
                                                         'grader': grader}

    lecture_keywords = []
    for lf in lectures:
        with open(lf, encoding="utf-8") as f:
            jd = json.loads(f.read())
            md = jd['metadata']
            org = md.get('org', {})
            if org:
                lecture_keywords += [org.get('KEYWORDS', '')]
            else:
                lecture_keywords += ['']

    if os.path.exists(f'{COURSEDIR}/announcements.html'):
        with open(f'{COURSEDIR}/announcements.html', encoding="utf-8") as f:
            announcements = f.read()
    else:
        announcements = ''

    data = {'lectures': lectures,
            'lecture_keywords': lecture_keywords,
            'assignments': assignment_data,
            'solutions': solutions,
            'announcements': announcements}

    return data


@app.route("/coursedir")
def open_course(path=None):
    """Open the course directory in a file explorer."""
    d = COURSEDIR
    path = request.args.get('path')

    if path:
        d += path
    if sys.platform == "win32":
        os.startfile(d)
    else:
        opener = "open" if sys.platform == "darwin" else "xdg-open"
        subprocess.call([opener, d])

    return redirect(url_for('hello'))


def update_course_repo():
    '''Update the course repo.
TODO: this is not graceful if the repo is not clean.'''
    pwd = os.getcwd()

    try:
        os.chdir(COURSEDIR)
        subprocess.run(['git', 'fetch', '--all'], check=True)
        subprocess.run(['git', 'reset', '--hard', 'origin/master'])

    except:
        print('There was a git pull exception...')
    finally:
        os.chdir(pwd)


@app.route("/")
def hello():
    "This is the opening page."

    update_course_repo()

    if not os.path.exists(USERCONFIG):
        return redirect(url_for('setup_view'))

    with open(USERCONFIG, encoding='utf-8') as f:
        data = json.loads(f.read())
        ANDREWID = data['ANDREWID']
        NAME = data['NAME']

    # Should be setup now. Make sure we are online
    ONLINE = True
    try:
        urllib.request.urlretrieve(f'https://www.cmu.edu')
    except urllib.error.HTTPError:
        ONLINE = False

    data = get_course_data()

    # First get lecture status
    lecture_paths = [os.path.join(COURSEDIR, path)
                     for path in data['lectures']]
    lecture_files = [os.path.split(path)[-1] for path in lecture_paths]

    lecture_labels = [os.path.splitext(f)[0] for f in lecture_files]

    mylectures = [os.path.join(COURSEDIR, 'my-lectures', lf)
                  for lf in lecture_files]

    lecture_status = ['Opened' if os.path.exists(path)
                      else '<font color="red">Not opened</font>'
                      for path in mylectures]

    lecture_keywords = data['lecture_keywords']

    # Next get assignments. These are in assignments/label.ipynb For students I
    # construct assignments/andrewid-label.ipynb to check if they have local
    # versions.
    assignments = data['assignments']

    assignment_files = [os.path.split(assignment)[-1]
                        for assignment in assignments]
    assignment_labels = [os.path.splitext(f)[0] for f in assignment_files]
    assignment_paths = ['{}assignments/{}-{}.ipynb'.format(COURSEDIR,
                                                           ANDREWID,
                                                           label)
                        for label in assignment_labels]
    myassignments = [os.path.join(COURSEDIR, 'my-assignments', f'{ANDREWID}-{label}.ipynb')
                     for label in assignment_labels]
    assignment_status = ['Opened' if os.path.exists(path)
                         else '<font color="red">Not opened</font>'
                         for path in myassignments]

    duedates = [assignments[f]['duedate'] for f in assignments]
    colors = []
    for dd in duedates:
        today = datetime.utcnow()
        d = datetime.strptime(dd, "%Y-%m-%d %H:%M:%S")

        if (d - today).days < 0:
            colors.append('black')
        elif (d - today).days <= 2:
            colors.append('red')
        elif (d - today).days <= 7:
            colors.append('orange')
        else:
            colors.append('green')

    turned_in = []
    for path in myassignments:
        if os.path.exists(path):
            with open(path, encoding='utf-8') as f:
                d = json.loads(f.read())
                ti = d['metadata'].get('TURNED-IN', None)
                if ti:
                    turned_in.append(ti['timestamp'])
                else:
                    turned_in.append('Not yet.')
        else:
            turned_in.append(None)

    solution_paths = data['solutions']
    solution_files = [os.path.split(path)[-1] for path in solution_paths]
    solution_labels = [os.path.splitext(f)[0] for f in solution_files]

    solutions = [label if label in solution_labels else None
                 for label in assignment_labels]

    # graded assignments
    graded_assignments = []
    for ipynb in glob.glob(COURSEDIR + 'graded-assignments/*.ipynb'):
        with open(ipynb, encoding='utf-8') as f:
            gd = json.loads(f.read())

            graded_assignments += [[os.path.split(ipynb)[-1],
                                    gd['metadata'].get('grade',
                                                       {}).get('overall',
                                                               None),
                                    gd['metadata']['org'].get('GRADER',
                                                              'unknown')]]

    return render_template('hello.html',
                           COURSEDATA=COURSEDATA,
                           COURSEDIR=COURSEDIR,
                           ANDREWID=ANDREWID,
                           NAME=NAME,
                           ONLINE=ONLINE,
                           announcements=data['announcements'],
                           version=__version__,
                           lectures=list(zip(lecture_labels,
                                             lecture_status,
                                             lecture_keywords)),
                           assignments4templates=list(zip(assignment_labels,
                                                          assignment_paths,
                                                          assignment_status,
                                                          colors,
                                                          duedates,
                                                          turned_in,
                                                          solutions)),
                           graded_assignments=graded_assignments)


@app.route("/debug")
def debug():
    "In debug mode this gets me to a console in the browser."
    raise(Exception)


@app.route("/about")
def about():
    import platform

    opsys = platform.platform()

    pyexe = sys.executable
    pyver = sys.version

    import techela
    techela_ver = techela.__version__

    try:
        import pycse
        pycse_ver = pycse.__version__
    except ModuleNotFoundError:
        pycse_ver = None
    return render_template('about.html',
                           **locals())


@app.route("/setup")
def setup_view():
    return render_template('setup.html')


@app.route("/setup_post", methods=['POST'])
def setup_post():
    ANDREWID = request.form['andrewid']
    NAME = request.form['fullname']
    password = request.form['password']

    with open(USERCONFIG, 'w', encoding='utf-8') as f:
        f.write(json.dumps({'ANDREWID': ANDREWID.lower(),
                            'NAME': NAME}))

    # TODO make s
    with smtplib.SMTP_SSL('smtp.andrew.cmu.edu', port=465) as s:
        try:
            s.login(ANDREWID, password)
        except smtplib.SMTPAuthenticationError:
            return redirect(url_for('setup_view'))

    return redirect(url_for('hello'))


@app.route("/lecture/<label>")
def open_lecture(label):
    global NOTEBOOKS
    fname = '{}/lectures/{}.ipynb'.format(COURSEDIR, label)
    if not os.path.isdir(os.path.join(COURSEDIR, 'my-lectures')):
        os.makedirs(os.path.join(COURSEDIR, 'my-lectures'))

    mname = '{}/my-lectures/{}.ipynb'.format(COURSEDIR, label)
    if not os.path.exists(mname):
        shutil.copy(fname, mname)
        # We need to check for images. Boo...
        # They look like this in the cells: ![img](./images/control-volume.png)

    # Now open the notebook.
    cmd = [JUPYTER]
    if BROWSER:
        cmd += [BROWSER]
    cmd += [mname]
    print(cmd)
    NOTEBOOKS += [subprocess.Popen(cmd)]

    return redirect(url_for('hello'))


@app.route("/course-lecture/<label>")
def open_course_lecture(label):
    global NOTEBOOKS
    fname = f'{COURSEDIR}/lectures/{label}.ipynb'

    # Now open the notebook.
    cmd = [JUPYTER]
    if BROWSER:
        cmd += [BROWSER]
    cmd += [fname]
    NOTEBOOKS += [subprocess.Popen(cmd)]

    return redirect(url_for('hello'))


@app.route("/solution/<label>")
def open_solution(label):
    global NOTEBOOKS
    fname = f'{COURSEDIR}/solutions/{label}.ipynb'

    # Now open the notebook.
    cmd = [JUPYTER]
    if BROWSER:
        cmd += [BROWSER]
    cmd += [fname]
    NOTEBOOKS += [subprocess.Popen(cmd)]

    return redirect(url_for('hello'))


@app.route("/admin-solution/<label>")
def admin_solution(label):
    "Open admin solution"
    global NOTEBOOKS
    fname = os.path.expanduser(f"{COURSEDATA['admin-box-path']}/solutions/{label}.ipynb")

    # Now open the notebook.
    cmd = [JUPYTER]
    if BROWSER:
        cmd += [BROWSER]
    cmd += [fname]

    NOTEBOOKS += [subprocess.Popen(cmd)]

    return redirect(url_for('admin'))


@app.route("/assignment/<label>")
def open_assignment(label):
    global NOTEBOOKS
    with open(USERCONFIG, encoding='utf-8') as f:
        data = json.loads(f.read())
        ANDREWID = data['ANDREWID']
        NAME = data['NAME']

    fname = f'{COURSEDIR}my-assignments/{ANDREWID}-{label}.ipynb'
    if not os.path.exists(fname):
        shutil.copy(f'{COURSEDIR}assignments/{label}.ipynb', fname)
        # Insert their full name at the top
        with open(fname, encoding='utf-8') as f:
            j = json.loads(f.read())

        dt = datetime.now()

        author = {'cell_type': 'markdown',
                  'metadata': {},
                  'source': [f'{NAME} ({ANDREWID}@andrew.cmu.edu)\n',
                             'Date: {}\n'.format(dt.isoformat(" "))]}
        j['cells'].insert(0, author)

        # Also put Author metadata in so it is easy to email these back.
        j['metadata']['author'] = {}
        j['metadata']['author']['name'] = NAME
        j['metadata']['author']['email'] = f'{ANDREWID}@andrew.cmu.edu'

        with open(fname, 'w', encoding='utf-8') as f:
            f.write(json.dumps(j))

    # Now open the notebook.
    cmd = [JUPYTER]
    if BROWSER:
        cmd += [BROWSER]
    cmd += [fname]
    NOTEBOOKS += [subprocess.Popen(cmd)]

    return redirect(url_for('hello'))


@app.route("/graded-assignment/<fname>")
def open_graded_assignment(fname):
    """Open the assignment FNAME.
    It is in the graded-assignments directory."""
    global NOTEBOOKS
    fname = COURSEDIR + f'graded-assignments/{fname}'

    cmd = [JUPYTER]
    if BROWSER:
        cmd += [BROWSER]
    cmd += [fname]
    NOTEBOOKS += [subprocess.Popen(cmd)]

    return redirect(url_for('hello'))


@app.route("/new")
def new_notebook():
    global NOTEBOOKS
    CWD = os.getcwd()
    os.chdir(COURSEDIR)
    cmd = [JUPYTER]
    if BROWSER:
        cmd += [BROWSER]
    NOTEBOOKS += [subprocess.Popen(cmd)]
    os.chdir(CWD)
    return redirect(url_for('hello'))


@app.route("/submit/<label>")
def authenticate(label):
    "Get the andrew password."
    return render_template("email.html", label=label)


@app.route("/submit_post", methods=['POST'])
def submit_post():
    """Turn in LABEL by email."""

    with open(USERCONFIG, encoding='utf-8') as f:
        data = json.loads(f.read())
        ANDREWID = data['ANDREWID']
        NAME = data['NAME']

    password = request.form['password']
    label = request.form['label']

    # Create the container (outer) email message.
    msg = MIMEMultipart()
    subject = '[{}] - Turning in {} from {}'
    msg['Subject'] = subject.format(COURSE, label, NAME)
    msg['From'] = f'{ANDREWID}@andrew.cmu.edu'
    msg['To'] = BOX_EMAIL
    msg['Cc'] = f'{ANDREWID}@andrew.cmu.edu'

    ctype = 'application/octet-stream'
    maintype, subtype = ctype.split('/', 1)

    fname = f'{COURSEDIR}/my-assignments/{ANDREWID}-{label}.ipynb'
    if not os.path.exists(fname):
        raise Exception(f'{fname} not found.')

    # Save some turn in data.
    with open(fname, encoding='utf-8') as f:
        j = json.loads(f.read())

    j['metadata']['TURNED-IN'] = {}
    dt = datetime.now()
    j['metadata']['TURNED-IN']['timestamp'] = dt.isoformat(" ")

    with open(fname, 'w', encoding='utf-8') as f:
        f.write(json.dumps(j))

    with open(fname, 'rb') as fp:
        attachment = MIMEBase(maintype, subtype)
        attachment.set_payload(fp.read())
        # Encode the payload using Base64
        encoders.encode_base64(attachment)
        # Set the filename parameter
        aname = f'{ANDREWID}-{label}.ipynb'
        attachment.add_header('Content-Disposition', 'attachment',
                              filename=aname)
        msg.attach(attachment)

    with smtplib.SMTP_SSL('smtp.andrew.cmu.edu', port=465) as s:
        try:
            s.login(ANDREWID, password)
        except smtplib.SMTPAuthenticationError:
            print('caught error for', label)
            # Remove turned in
            with open(fname, encoding='utf-8') as f:
                j = json.loads(f.read())
            del j['metadata']['TURNED-IN']
            with open(fname, 'w', encoding='utf-8') as f:
                f.write(json.dumps(j))
            return render_template("password_error.html", label=label)

        s.send_message(msg)
        s.quit()

    return redirect(url_for('hello'))

# * Admin


@app.route('/close-notebooks')
def close_notebooks():
    """Close open notebooks.
This closes all the notebooks you have opened.
"""
    global NOTEBOOKS
    for p in NOTEBOOKS:
        print(f'Killing {" ".join(p.args)}')
        p.kill()
    NOTEBOOKS = []
    return redirect(url_for('hello'))


@app.route('/admin')
def admin():
    "Setup admin page."
    # First install the new key bindings.
    import notebook.nbextensions
    from notebook.services.config import ConfigManager

    import techela
    js = f'{techela.__path__[0]}/static/techela.js'
    notebook.nbextensions.install_nbextension(js, user=True)
    cm = ConfigManager()
    cm.update('notebook', {"load_extensions": {"techela": True}})

    ONLINE = True
    try:
        urllib.request.urlretrieve('https://www.cmu.edu')
    except urllib.error.HTTPError:
        ONLINE = False

    with open(USERCONFIG, encoding='utf-8') as f:
        data = json.loads(f.read())
        ANDREWID = data['ANDREWID']
        NAME = data['NAME']

    data = get_course_data()
#    with open(f'{COURSEDIR}/course-files.json', encoding='utf-8') as f:
#        data = json.loads(f.read())

    # Next get assignments. These are in assignments/label.ipynb For students I
    # construct assignments/andrewid-label.ipynb to check if they have local
    # versions.
    assignments = data['assignments']

    assignment_files = [os.path.split(assignment)[-1]
                        for assignment in assignments]
    assignment_labels = [os.path.splitext(f)[0] for f in assignment_files]
    # this is where solutions should be
    p1 = os.path.expanduser(f"{COURSEDATA['admin-box-path']}/solutions/")
    solutions = [os.path.join(p1,
                              f'{label}.ipynb')
                 for label in assignment_labels]

    duedates = [assignments[f]['duedate'] for f in assignments]

    graders = [assignments[f]['grader'] for f in assignments]

    statuses = []
    for label in assignment_labels:
        p1 = os.path.expanduser(f"{COURSEDATA['admin-box-path']}/assignments")
        f = os.path.join(p1,
                         label, "STATUS")

        if os.path.exists(f):
            with open(f, encoding='utf-8') as tf:
                statuses.append(tf.read())
        else:
            statuses.append(None)

    colors = []
    for status, dd in zip(statuses, duedates):
        today = datetime.utcnow()

        d = datetime.strptime(dd, "%Y-%m-%d %H:%M:%S")

        if status is not None and status.startswith('Returned'):
            colors.append('black')
        elif (d - today).days <= 2:
            colors.append('orange')
        else:
            colors.append('red')

    # Add this function so we can use it in a template
    app.jinja_env.globals.update(exists=os.path.exists)

    return render_template('admin.html',
                           COURSE=COURSE,
                           COURSEDATA=COURSEDATA,
                           NAME=NAME, ANDREWID=ANDREWID,
                           ONLINE=ONLINE,
                           assignments4templates=list(zip(assignment_labels,
                                                          duedates,
                                                          graders,
                                                          statuses,
                                                          colors,
                                                          solutions)))


def get_roster():
    """Read roster and return a list of dictionaries for each student.
The roster.csv file is just the file downloaded from s3, renamed to roster.csv.
    """
    import csv
    roster = f'{COURSEDATA["admin-box-path"]}/roster.csv'
    roster_file = os.path.expanduser(roster)
    with open(roster_file, encoding='utf-8') as f:
        reader = csv.reader(f, delimiter=',')
        rows = [row for row in reader]
        roster_entries = [dict(zip(rows[0], row)) for row in rows]
    # skip first entry that is the headers
    return roster_entries[1:]


@app.route('/course-info')
def course_info():
    "Show course info."
    return render_template('course-info.html',
                           COURSEDATA=COURSEDATA)


@app.route('/roster')
def roster():
    "Render roster page"
    with open(USERCONFIG, encoding='utf-8') as f:
        data = json.loads(f.read())
        ANDREWID = data['ANDREWID']

    admin_emails = ','.join([x + '@andrew.cmu.edu'
                             for x in COURSEDATA['admin-andrewids']])
    return render_template('roster.html',
                           admin_emails=admin_emails,
                           COURSE=COURSE,
                           ANDREWID=ANDREWID,
                           roster=get_roster())


@app.route('/grade-assignment/<label>')
def grade_assignment(label):
    """Copy assignments to the archive directory, and move them to the assignments
    directory."""

    roster = get_roster()
    # the first time you visit this page, we shuffle it, but on subsequent
    # visits we don't. The shuffle is to grade them in a different order each
    # time.
    # This is triggered by a url like /grade-assignment/label?shuffle=true
    if request.args.get('shuffle'):
        random.shuffle(roster)

    data = get_course_data()
#    with open(f'{COURSEDIR}/course-files.json', encoding='utf-8') as f:
#        data = json.loads(f.read())

    today = datetime.utcnow()
    dd = data['assignments']['assignments/{}.ipynb'.format(label)]['duedate']
    d = datetime.strptime(dd, "%Y-%m-%d %H:%M:%S")

    if (today - d).days >= 0:
        POSTDUE = True
    else:
        POSTDUE = False

    submission_dir = os.path.expanduser(f"{COURSEDATA['admin-box-path']}/submissions")   # NOQA
    assignment_dir = os.path.expanduser(f"{COURSEDATA['admin-box-path']}/assignments")   # NOQA
    assignment_dir = '{}/{}'.format(assignment_dir, label)

    assignment_archive_dir = os.path.expanduser(f"{COURSEDATA['admin-box-path']}/"  # NOQA
                                                'assignments-archive')
    assignment_archive_dir = '{}/{}'.format(assignment_archive_dir, label)

    if not os.path.isdir(assignment_dir):
        os.makedirs(assignment_dir)

    if not os.path.isdir(assignment_archive_dir):
        os.makedirs(assignment_archive_dir)

    grade_data = []

    for entry in roster:
        andrewid = entry['Andrew ID']
        d = {}
        d['first-name'] = entry['Preferred/First Name']
        d['last-name'] = entry['Last Name']
        d['name'] = '{} {}'.format(entry['Preferred/First Name'],
                                   entry['Last Name'])

        # This is the file that was submitted
        sfile = '{}-{}.ipynb'.format(andrewid, label)
        SFILE = os.path.join(submission_dir, sfile)

        # This is an archive copy in case anything happens.
        AFILE = os.path.join(assignment_archive_dir, sfile)

        # The logic I want to happen is:
        # if we are not POSTDUE, copy it if it exists.
        # If we are POSTDUE, copy it if it does not exist in the archive.
        if ((not POSTDUE and os.path.exists(SFILE))
            or (POSTDUE and os.path.exists(SFILE)
                and not os.path.exists(AFILE))):
            shutil.copy(SFILE, AFILE)

        # Now we do the move. This is the file we will grade. We move it, so it
        # will be gone from submissions. We do not move it if it has been
        # graded.
        GFILE = os.path.join(assignment_dir, sfile)

        # We don't have the file and it is submitted we might as well collect
        # it.
        if not os.path.exists(GFILE) and os.path.exists(SFILE):
            # Now we move SFILE to GFILE
            shutil.move(SFILE, GFILE)

        # here the GFILE should exist. whether we update it depends. Let's check  # NOQA
        # if it is graded. If we have not graded it, we might as well update it.  # NOQA
        # Check for a grade and return timestamp
        # collect data in a dictionary
        d['filename'] = GFILE
        d['andrewid'] = andrewid
        d['label'] = label
        d['grade'] = None
        d['turned-in'] = None
        d['returned'] = None

        if os.path.exists(GFILE):
            with open(GFILE, encoding='utf-8') as f:
                j = json.loads(f.read())
                # if the file is ungraded, we go ahead and move it over.
                if (os.path.exists(SFILE)
                    and j['metadata'].get('grade', None) is None):
                    shutil.move(SFILE, GFILE)

                if j['metadata'].get('grade', None):
                    d['grade'] = j['metadata']['grade']['overall']
                else:
                    d['grade'] = None

                if j['metadata'].get('RETURNED', None):
                    d['returned'] = j['metadata']['RETURNED']
                else:
                    d['returned'] = None

                if j['metadata'].get("TURNED-IN"):
                    d['turned-in'] = j['metadata']['TURNED-IN']['timestamp']
                else:
                    d['turned-in'] = None

        grade_data.append(d)

    # this puts a figure inline in the page of the grade distribution.
    numeric_grades = [d['grade'] for d in grade_data if d['grade'] is not None]
    if numeric_grades:
        from io import BytesIO
        import base64
        plt.hist(numeric_grades, 20)
        plt.xlabel('Grade')
        plt.ylabel('Frequency')
        plt.xlim([0, 1])
        plt.title('Grade distribution for {}\nMean={:1.2f}'.format(label,
                                                                   np.mean(numeric_grades)))  # NOQA
        png = BytesIO()
        plt.savefig(png)
        plt.close()
        png.seek(0)
        histogram = urllib.parse.quote(base64.b64encode(png.read()))
    else:
        histogram = ""

    # Add this function so we can use it in a template
    app.jinja_env.globals.update(exists=os.path.exists)

    status_file = os.path.expanduser(f"{COURSEDATA['admin-box-path']}/assignments/{label}/STATUS")   # NOQA

    # if we don't have a status file create one. If we do have one, I don't
    # think it makes sense to change it since it should either be Collected or
    # Returned.
    if not os.path.exists(status_file):
        with open(status_file, 'w', encoding='utf-8') as f:
            f.write('Collected')

    return render_template('grade-assignment.html',
                           COURSE=COURSE,
                           label=label,
                           histogram=histogram,
                           grade_data=grade_data)


@app.route('/grade/<andrewid>/<label>')
def grade(andrewid, label):
    "Opens the file for andrewid and label."
    assignment_dir = os.path.expanduser(f'{COURSEDATA["admin-box-path"]}/assignments')   # NOQA
    GFILE = os.path.join(assignment_dir,
                         label,
                         f'{andrewid}-{label}.ipynb')

    with open(GFILE, encoding='utf-8') as f:
        j = json.loads(f.read())
        if j['metadata'].get('grade', None) is None:
            print('No grade in {} yet'.format(GFILE))
        else:
            tech = j['metadata']['grade']['technical']
            pres = j['metadata']['grade']['presentation']
            print('grade: ', ('technical', tech), ('presentation', pres))

    # Now open the notebook.
    cmd = [JUPYTER]
    if BROWSER:
        cmd += [BROWSER]
    cmd += [GFILE]
    NOTEBOOKS += [subprocess.Popen(cmd)]

    return ('', 204)


@app.route('/open-for-grading/<label>')
def open_for_grading(label, n=5):
    "Open N ungraded LABEL assignments for grading."
    global NOTEBOOKS
    assignment_dir = os.path.expanduser(f'{COURSEDATA["admin-box-path"]}/assignments') # NOQA
    # Get a list of ungraded notebooks
    all_ipynb = glob.glob(assignment_dir + '/' + label + '/*.ipynb')
    ungraded = []
    for ipynb in all_ipynb:
        with open(ipynb, encoding="utf-8") as f:
            data = json.loads(f.read())
            if 'grade' not in data['metadata']:
                ungraded += [ipynb]
    random.shuffle(ungraded)
    for i in range(min(n, len(ungraded))):
        # Now open the notebooks.
        cmd = [JUPYTER]
        if BROWSER:
            cmd += [BROWSER]
        cmd += [ungraded[i]]
        print(f'Running "{cmd}")')
        NOTEBOOK += [subprocess.Popen(cmd)]
    return ('', 204)


@app.route('/return/<andrewid>/<label>')
def return_one(andrewid, label):
    """Return an assignment by email.
    If a force parameter is given return even if it was returned before.
    """
    force = True if request.args.get('force') else False

    assignment_dir = os.path.expanduser(f"{COURSEDATA['admin-box-path']}/assignments")   # NOQA
    GFILE = os.path.join(assignment_dir,
                         label,
                         f'{andrewid}-{label}.ipynb')
    # Make sure file exists
    if not os.path.exists(GFILE):
        print('{} not found.'.format(GFILE))
        return redirect(url_for('grade_assignment', label=label))

    # Check for grade, we don't return ungraded files
    with open(GFILE, encoding='utf-8') as f:
        j = json.loads(f.read())
        if j['metadata'].get('grade', None) is None:
            print('No grade in {}. not returning.'.format(GFILE))
            return redirect(url_for('grade_assignment', label=label))
        tech = j['metadata']['grade']['technical']
        pres = j['metadata']['grade']['presentation']
        grade = j['metadata']['grade']['overall']
        print('grade: ', ('technical', tech), ('presentation', pres))
    # Check if it was already returned, we don't return it again unless force
    # is truthy.
    if j['metadata'].get('RETURNED', None) and not force:
        print('Returned already!')
        return redirect(url_for('grade_assignment', label=label))

    # ok, finally we have to send it back.
    EMAIL = '{}@andrew.cmu.edu'.format(andrewid)

    with open(USERCONFIG, encoding='utf-8') as f:
        data = json.loads(f.read())
        ANDREWID = data['ANDREWID']

    # Create the container (outer) email message.
    msg = MIMEMultipart()
    subject = '[{}] - {}-{}.ipynb has been graded'
    msg['Subject'] = subject.format(COURSE, andrewid, label)
    msg['From'] = '{}@andrew.cmu.edu'.format(ANDREWID)
    msg['To'] = EMAIL

    body = 'Technical: {}\nPresentation: {}\nOverall Grade = {}'.format(tech,
                                                                        pres,
                                                                        grade)

    ctype = 'application/octet-stream'
    maintype, subtype = ctype.split('/', 1)

    # Save some return data.
    with open(GFILE, encoding='utf-8') as f:
        j = json.loads(f.read())

    # Now we add the comments to the email body.
    i = 1
    comments = []
    for cell in j['cells']:
        if cell['metadata'].get('type', None) == 'comment':
            comments.append('{0}. {1}'.format(i, cell['metadata'].get('content', '')))   # NOQA
            i += 1

    if comments:
        body += '\n\nComments:\n'
        body += '\n'.join(comments)

    # Let's put a grade report in too.
    grades = get_grades(andrewid)
    # we need to delete some keys I made for convenience.
    del grades['course-overall-grade']
    del grades['name']
    del grades['first-name']
    del grades['last-name']
    # grades is a dictionary by label.

    # here we make it a list
    grades = [(k, v) for k, v in grades.items()]

    # Now we sort by the duedate. This function gets the datetime object for an
    # assignment for sorting.

    def mydate(el):
        k, v = el
        dd = v['duedate']
        d = datetime.strptime(dd, "%Y-%m-%d %H:%M:%S")
        return d

    grades = sorted(grades, key=lambda el: mydate(el), reverse=True)

    today = datetime.utcnow()
    gstring = '{0:35s} {1:15s} {2:8s} {3:10s} {4}'.format('label',
                                                          'grade',
                                                          'points',
                                                          'category',
                                                          'duedate')
    gstring += '\n' + "-" * len(gstring)

    data = get_course_data()
#    with open(f'{COURSEDIR}/course-files.json'.format(COURSEDIR),
#              encoding='utf-8') as f:
#        data = json.loads(f.read())
    adata = {}
    for k, v in data['assignments'].items():
        adata[v['label']] = v

    for label, v in grades:
        p = v['path']  # path to student file
        dd = adata[label]['duedate']
        category = adata[label]['category']
        g = v.get('overall', 0.0)  # student grade
        points = str(adata[label]['points'])

        d = datetime.strptime(dd, "%Y-%m-%d %H:%M:%S")

        if (today - d).days >= 0:
            POSTDUE = True
        else:
            POSTDUE = False

        if POSTDUE and os.path.exists(p) and g is not None:
            gstring += '\n{0:35s} {1:15.3f} {4:^8s} {2:15s} {3}'.format(label, g, category, dd, points)  # NOQA
        elif POSTDUE and os.path.exists(p) and g is None:
            gstring += '\n{0:35s} {1:>15s} {4:^8s} {2:15s} {3}'.format(label,
                                                                       'not-graded', category, dd, # NOQA
                                                                       points)
        elif POSTDUE:
            gstring += '\n{0:35s} {1:>15s} {4:^8s} {2:15s} {3}'.format(label,
                                                                       'missing', category,   # NOQA
                                                                       dd,
                                                                       points)

    body += '\n\nGrades\n======\n'
    body += gstring

    dt = datetime.now()
    j['metadata']['RETURNED'] = dt.isoformat(" ")

    with open(GFILE, 'w', encoding='utf-8') as f:
        f.write(json.dumps(j))

    with open(GFILE, 'rb') as fp:
        attachment = MIMEBase(maintype, subtype)
        attachment.set_payload(fp.read())
        # Encode the payload using Base64
        encoders.encode_base64(attachment)
        # Set the filename parameter
        attachment.add_header('Content-Disposition', 'attachment',
                              filename=os.path.split(GFILE)[-1])
        msg.attach(attachment)

    msg.attach(MIMEText(body, 'plain'))

    print(msg)

    with smtplib.SMTP_SSL('relay.andrew.cmu.edu', port=465) as s:
        s.send_message(msg)
        s.quit()

    return ('', 204)


@app.route('/return-all/<label>')
def return_all(label):
    """Return all the assignments for label."""

    roster = get_roster()
    andrewids = [d['Andrew ID'] for d in roster]

    for andrewid in andrewids:
        return_one(andrewid, label)
        time.sleep(1)

    status_file = os.path.join(os.path.expanduser(f"{COURSEDATA['admin-box-path']}/assignments/"),   # NOQA
                               label, "STATUS")

    with open(status_file, 'w', encoding='utf-8') as f:
        f.write('Returned')

    return redirect(url_for('grade_assignment', label=label))


def get_grades(andrewid):
    """Return a dictionary of grades for andrewid."""
    data = get_course_data()
    # with open(f'{COURSEDIR}/course-files.json', encoding='utf-8') as f:
    #     data = json.loads(f.read())

    # Next get assignments. These are in assignments/label.ipynb For students I
    # construct assignments/andrewid-label.ipynb to check if they have local
    # versions.
    assignments = data['assignments']

    assignment_paths = assignments.keys()

    assignment_files = [os.path.split(path)[-1]
                        for path in assignment_paths]

    assignment_labels = [os.path.splitext(f)[0] for f in assignment_files]

    assignment_dir = os.path.expanduser(f"{COURSEDATA['admin-box-path']}/assignments")   # NOQA

    duedates = [assignments[path]['duedate'] for path in assignment_paths]

    grades = {}
    for label, dd in zip(assignment_labels, duedates):
        today = datetime.utcnow()
        d = datetime.strptime(dd, "%Y-%m-%d %H:%M:%S")

        # We only look at assignments that are post due
        if (today - d).days >= 0:
            # the student file
            sfile = '{assignment_dir}/{label}/{andrewid}-{label}.ipynb'.format(**locals()) # NOQA

            if os.path.exists(sfile):
                with open(sfile, encoding='utf-8') as f:
                    j = json.loads(f.read())
                    if j['metadata'].get('grade', None):
                        grades[label] = {'andrewid': andrewid,
                                         'path': sfile,
                                         'technical': j['metadata']['grade']['technical'],  # NOQA
                                         'presentation': j['metadata']['grade']['presentation'], # NOQA
                                         'overall': j['metadata']['grade']['overall'], # NOQA
                                         'category': assignments['assignments/{}.ipynb'.format(label)]['category'], # NOQA
                                         'points': assignments['assignments/{}.ipynb'.format(label)]['points'], # NOQA
                                         'duedate': assignments['assignments/{}.ipynb'.format(label)]['duedate']} # NOQA
                    else:
                        grades[label] = {'andrewid': andrewid,
                                         'technical': None,
                                         'presentation': None,
                                         'overall': None,
                                         'category': assignments['assignments/{}.ipynb'.format(label)]['category'],  # NOQA
                                         'points': assignments['assignments/{}.ipynb'.format(label)]['points'], # NOQA
                                         'duedate': assignments['assignments/{}.ipynb'.format(label)]['duedate'], # NOQA
                                         'path': sfile}
            else:
                grades[label] = {'andrewid': andrewid,
                                 'technical': None,
                                 'presentation': None,
                                 'overall': None,
                                 'category': assignments['assignments/{}.ipynb'.format(label)]['category'], # NOQA
                                 'points': assignments['assignments/{}.ipynb'.format(label)]['points'], # NOQA
                                 'duedate': assignments['assignments/{}.ipynb'.format(label)]['duedate'], # NOQA
                                 'path': sfile}

    # add name
    roster = get_roster()
    for d in roster:
        if andrewid == d['Andrew ID']:
            grades['first-name'] = d['Preferred/First Name']
            grades['last-name'] = d['Last Name']
            grades['name'] = '{} {}'.format(d['Preferred/First Name'],
                                            d['Last Name'])
            break

    # Compute overall grade
    # these are the categories and weights
    categories = dict(list(zip(*COURSEDATA['categories'])))

    overall_possible_points = 0
    overall_earned_points = 0
    for key in grades:
        if key not in assignment_labels:
            continue
        cat = grades[key]['category']

        possible_points = int(data['assignments'][f'assignments/{key}.ipynb']['points'])  # NOQA
        overall_grade = float(grades[key]['overall'] or 0.0)

        overall_earned_points += overall_grade * possible_points * categories[cat]  # NOQA
        overall_possible_points += possible_points * categories[cat]

    grades['course-overall-grade'] = overall_earned_points / overall_possible_points  # NOQA
    return grades


@app.route('/gradebook_one/<andrewid>')
def gradebook_one(andrewid):
    """Gather grades for andrewid."""

    grades = get_grades(andrewid)
    data = get_course_data()
    # with open('{}/course-files.json'.format(COURSEDIR), encoding='utf-8') as f:
    #     data = json.loads(f.read())

    # Next get assignments. These are in assignments/label.ipynb For students I
    # construct assignments/andrewid-label.ipynb to check if they have local
    # versions.
    assignments = data['assignments']

    assignment_files = [os.path.split(assignment)[-1]
                        for assignment in assignments]
    assignment_labels = [os.path.splitext(f)[0] for f in assignment_files]

    return render_template('gradebook_one.html',
                           COURSE=COURSE,
                           name=grades['name'],
                           andrewid=andrewid,
                           course_overall_grade=round(grades['course-overall-grade'], 3),  # NOQA
                           assignment_labels=assignment_labels,
                           grades=grades)


# TODO
@app.route('/gradebook')
def gradebook():

    data = get_course_data()
    # with open('{}/course-files.json'.format(COURSEDIR), encoding='utf-8') as f:
    #     data = json.loads(f.read())

    # Next get assignments. These are in assignments/label.ipynb For students I
    # construct assignments/andrewid-label.ipynb to check if they have local
    # versions.
    assignments = data['assignments']

    assignment_files = [os.path.split(assignment)[-1]
                        for assignment in assignments]
    assignment_labels = [os.path.splitext(f)[0] for f in assignment_files]

    headings = ['First name',
                'Last name',
                'Andrew ID',
                'Overall']

    # Add each assignment label
    headings += assignment_labels

    roster = get_roster()

    ROWS = []
    for d in roster:
        ROW = []
        ROW += [d['Preferred/First Name'],
                d['Last Name'],
                d['Andrew ID']]

        grades = get_grades(d['Andrew ID'])
        ROW += [round(grades['course-overall-grade'], 3)]

        for label in assignment_labels:
            asn = grades.get(label, None)
            if asn:
                if asn['overall'] is not None:
                    ROW += [round(asn['overall'], 2)]
                else:
                    ROW += [None]
            else:
                ROW += [None]

        ROWS += [ROW]

    app.jinja_env.globals.update(isinstance=isinstance,
                                 float=float)
    return render_template('gradebook.html',
                           headings=headings,
                           ROWS=ROWS)
