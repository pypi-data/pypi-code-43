import argparse
from .prints import *


def main():

    parser = argparse.ArgumentParser(prog='vibhu',
                                     description='Interactive Resume of Vibhu Agarwal.')

    parser.add_argument('-name', action='store_const', const=True,
                        default=False, dest='wants_name',
                        help="Prints my full name.")
    parser.add_argument('-resume', action='store_const', const=True,
                        default=False, dest='wants_resume',
                        help="Prints my full Resume")
    parser.add_argument('-profile', action='store_const', const=True,
                        default=False, dest='wants_profile',
                        help="Prints my basic profile.")
    parser.add_argument('-location', action='store_const', const=True,
                        default=False, dest='wants_location',
                        help="Fetches my current whereabouts.")
    parser.add_argument('-contact', action='store_const', const=True,
                        default=False, dest='wants_contact',
                        help="Lists down my contact points.")
    parser.add_argument('-need', action='store_const', const=True,
                        default=False, dest='wants_need',
                        help="When should you contact me?")
    parser.add_argument('-summary', action='store_const', const=True,
                        default=False, dest='wants_summary',
                        help="Fetches information about which tools I've worked with and how much.")
    parser.add_argument('-skills', action='store_const', const=True,
                        default=False, dest='wants_skills',
                        help="Lists down my skill set.")
    parser.add_argument('-handles', action='store_const', const=True,
                        default=False, dest='wants_handles',
                        help="Lists down my various public profiles on various platforms (GitHub, LinkedIn, ...)")
    parser.add_argument('-education', action='store_const', const=True,
                        default=False, dest='wants_education',
                        help="Fetches my education history.")
    parser.add_argument('-foss', action='store_const', const=True,
                        default=False, dest='wants_open_source',
                        help="Fetches my major open-source contributions."),
    parser.add_argument('-projects', '-projies', action='store_const', const=True,
                        default=False, dest='wants_projects',
                        help="Lists down some of the projects I've worked on.")
    parser.add_argument('-work', action='store_const', const=True,
                        default=False, dest='wants_work_exp',
                        help="Fetches details about my past work experience.")
    parser.add_argument('-org', action='store_const', const=True,
                        default=False, dest='wants_org',
                        help="Lists down Developer Communities I've been a part of.")

    got_no_argument = True
    args = parser.parse_args()

    if args.wants_resume:
        print_resume()
        got_no_argument = False
    else:
        if args.wants_profile:
            print_profile(wants_contact=args.wants_contact,
                          wants_handles=args.wants_handles,
                          wants_skills=args.wants_skills,
                          wants_need=args.wants_need)
            got_no_argument = False
        else:
            if args.wants_name:
                print_name(sdiv=True)
                got_no_argument = False
            if args.wants_location:
                print_location(sdiv=True)
                got_no_argument = False
            if args.wants_contact:
                print_contacts(sdiv=True)
                got_no_argument = False
            if args.wants_handles:
                print_handles(sdiv=True)
                got_no_argument = False
            if args.wants_summary:
                print_summary(sdiv=True)
                got_no_argument = False
            if args.wants_skills:
                print_skills(sdiv=True)
                got_no_argument = False
            if args.wants_need:
                print_need(sdiv=True)
                got_no_argument = False

        if args.wants_education:
            print_education(sdiv=True)
            got_no_argument = False
        if args.wants_open_source:
            print_open_source(sdiv=True)
            got_no_argument = False
        if args.wants_projects:
            print_projects(sdiv=True)
            got_no_argument = False
        if args.wants_work_exp:
            print_work_exp(sdiv=True)
            got_no_argument = False
        if args.wants_org:
            print_organizations(sdiv=True)
            got_no_argument = False

    if got_no_argument:
        welcome_message = """Hi! This is Vibhu Agarwal and I welcome you to my interactive Resume.
How to get to know me better? Just see how to play with this portfolio by typing this command:

vibhu -h"""
        print(welcome_message)
    else:
        print_divider()
