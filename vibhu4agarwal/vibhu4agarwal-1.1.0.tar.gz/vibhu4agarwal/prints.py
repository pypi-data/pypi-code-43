from .details import *

DEFAULT_BG_COLOR = 40
BAR = '\033[0;37;{bg_color}m|'.format(bg_color=DEFAULT_BG_COLOR)
END_BAR = '\033[0;37;{bg_color}m|\x1b[0m'.format(bg_color=DEFAULT_BG_COLOR)
DIVIDER = BAR + '----------------------------------------------------------------------------------------' + END_BAR
PADDING = len(DIVIDER) - (len(BAR) + len(END_BAR))
NORMAL = 0
BOLD = 1
SKILLS_LINE_LENGTH = 30


def print_divider(condition=True):
    if condition:
        print(DIVIDER)


def adjust_print(string, text_style=NORMAL, text_color=37, bg_color=DEFAULT_BG_COLOR, extra_adjust=0):
    string_print = BAR + '\033[{text_style};{text_color};{bg_color}m'+string.ljust(PADDING+extra_adjust, ' ') + END_BAR
    string_print = string_print.format(text_style=text_style,
                                       text_color=text_color,
                                       bg_color=bg_color)
    print(string_print)


def print_name(sdiv=False, ediv=False):
    print_divider(sdiv)
    adjust_print('Name: ' + profile['name'], text_style=BOLD)
    print_divider(ediv)


def print_location(sdiv=False, ediv=False):
    print_divider(sdiv)
    adjust_print('Current Location: ' + profile['location'])
    print_divider(ediv)


def print_contacts(sdiv=False, ediv=False):
    print_divider(sdiv)
    adjust_print('Contact:', text_style=BOLD)
    for platform in contact:
        adjust_print(platform + ': ' + contact[platform])
    print_divider(ediv)


def print_handles(sdiv=False, ediv=False):
    print_divider(sdiv)
    adjust_print('Handles:', text_style=BOLD)
    for platform in tech_profiles:
        colour_string = '\033[1;34;40m'
        extra_adjust = len(colour_string)
        adjust_print(platform + ": " + colour_string + tech_profiles[platform],
                     extra_adjust=extra_adjust)
    print_divider(ediv)


def print_summary(sdiv=False, ediv=False):
    print_divider(sdiv)
    for line in profile['summary'].splitlines():
        adjust_print(line)
    print_divider(ediv)


def print_skills(sdiv=False, ediv=False):
    print_divider(sdiv)
    adjust_print('Skills:', text_style=BOLD)
    skills_print, skills_line = '', ''
    first_line = True
    for skill in profile['skills']:
        skills_line += skill + ', '
        if len(skills_line) > SKILLS_LINE_LENGTH:
            if first_line:
                first_line = False
            else:
                adjust_print(skills_print)
            skills_print = skills_line
            skills_line = ''
    adjust_print(skills_print[:-2])
    print_divider(ediv)


def print_need(sdiv=False, ediv=False):
    print_divider(sdiv)
    for line in profile['need'].splitlines():
        adjust_print(line)
    print_divider(ediv)


def print_education(sdiv=False, ediv=False):
    print_divider(sdiv)
    adjust_print('Education:', text_style=BOLD)
    for institute in education.values():
        adjust_print('')
        for line in institute.splitlines():
            adjust_print(line.strip())
    print_divider(ediv)


def print_work_exp(sdiv=False, ediv=False):
    print_divider(sdiv)
    adjust_print('Work Experience:', text_style=BOLD)
    for work in work_exp:
        adjust_print('')
        adjust_print(work['company'])
        adjust_print('- ' + work['role'])
        adjust_print('- ' + work['time'])
    print_divider(ediv)


def print_open_source(sdiv=False, ediv=False):
    print_divider(sdiv)
    adjust_print('Open Source Profile:', text_style=BOLD)
    for organization in open_source:
        adjust_print('')
        adjust_print('Organization: ' + open_source[organization]['org_name'])
        adjust_print('Role: ' + open_source[organization]['role'])
        adjust_print('Repositories: ')
        links = open_source[organization]['repo_links']
        for link in links:
            adjust_print('- ' + link, text_color=34, text_style=BOLD)
    print_divider(ediv)


def print_organizations(sdiv=False, ediv=False):
    print_divider(sdiv)
    adjust_print("Organizations I've been a part of:", text_style=BOLD)
    for org in organizations:
        adjust_print('')
        adjust_print('Organization: ' + organizations[org]['org_name'])
        adjust_print('Role        : ' + organizations[org]['role'])
        if 'duration' in organizations[org]:
            adjust_print('Duration    : ' + organizations[org]['duration'])
        if 'location' in organizations[org]:
            adjust_print('Location    : ' + organizations[org]['location'])
    print_divider(ediv)


def print_projects(sdiv=False, ediv=False):
    print_divider(sdiv)
    adjust_print("Projects I've been involved with:", text_style=BOLD)
    for projy in projects:
        adjust_print('')
        adjust_print(projects[projy]['name']+' ('+projects[projy]['date']+')')
        for desc_line in projects[projy]['desc']:
            desc_words = desc_line.split()
            print_line = "-"
            for word in desc_words:
                if len(word) + len(print_line) < PADDING - 2:
                    print_line += " " + word
                else:
                    adjust_print(print_line)
                    print_line = "  " + word
            if len(print_line) > 2:
                adjust_print(print_line)
        if projects[projy]['link']:
            adjust_print('- ' + projects[projy]['link'], text_color=34, text_style=BOLD)
    print_divider(ediv)


def print_profile(wants_contact=False, wants_handles=False,
                  wants_skills=False, wants_need=False):
    print_name(sdiv=True)
    adjust_print(profile['title'])
    if wants_contact or wants_handles:
        print_divider()
    else:
        adjust_print('')
    print_location()
    if wants_contact:
        adjust_print('')
        print_contacts()
    if wants_handles:
        adjust_print('')
        print_handles()
    print_summary(sdiv=True)
    if wants_skills:
        adjust_print('')
        print_skills()
    if wants_need:
        adjust_print('')
        print_need()


def print_resume():
    print_profile(wants_contact=True, wants_handles=True,
                  wants_skills=False, wants_need=True)
    print_education(sdiv=True)
    print_open_source(sdiv=True)
    print_projects(sdiv=True)
    print_work_exp(sdiv=True)
    print_organizations(sdiv=True)
