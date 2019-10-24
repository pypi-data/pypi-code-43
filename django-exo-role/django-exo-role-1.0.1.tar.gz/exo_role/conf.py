# -*- coding: utf-8 -*-
"""
License boilerplate should be used here.
"""

# python 3 imports
from __future__ import absolute_import, unicode_literals

# python imports
import logging

# 3rd. libraries imports
from appconf import AppConf

# django imports
from django.conf import settings  # noqa

logger = logging.getLogger(__name__)


class ExORoleConfigConfig(AppConf):
    CATEGORY_EXO_SPRINT = 'SP'
    CATEGORY_FASTRACK = 'FA'
    CATEGORY_WORKSHOP = 'WO'
    CATEGORY_SWARM = 'SW'
    CATEGORY_SUMMIT = 'SU'
    CATEGORY_SUMMIT = 'SU'
    CATEGORY_ADVISORY_CALL = 'AC'
    CATEGORY_DISRUPTION_SESSION = 'DS'
    CATEGORY_TALK = 'TA'
    CATEGORY_CERTIFICATION_PROGRAM = 'CP'
    CATEGORY_OTHER = 'OT'

    CATEGORY_CODE_CHOICES = (
        (CATEGORY_EXO_SPRINT, 'ExO Sprint'),
        (CATEGORY_FASTRACK, 'Fastrack'),
        (CATEGORY_WORKSHOP, 'Workshop'),
        (CATEGORY_SWARM, 'Swarm'),
        (CATEGORY_SUMMIT, 'Summit'),
        (CATEGORY_ADVISORY_CALL, 'Advisory Call'),
        (CATEGORY_DISRUPTION_SESSION, 'Disruption Session'),
        (CATEGORY_TALK, 'Talk'),
        (CATEGORY_CERTIFICATION_PROGRAM, 'Certification Program'),
        (CATEGORY_OTHER, 'Other'),
    )

    # EXO SPRINT
    CODE_SPRINT_HEAD_COACH = 'SHC'
    CODE_SPRINT_COACH = 'SSH'
    CODE_AWAKE_SPEAKER = 'SAS'
    CODE_ALIGN_TRAINER = 'SAT'
    CODE_ADVISOR = 'SAD'
    CODE_DISRUPTOR = 'SDI'
    CODE_DISRUPTOR_SPEAKER = 'SDS'
    CODE_DELIVERY_MANAGER = 'SDM'
    CODE_SPRINT_PARTICIPANT = 'SPA'
    CODE_SPRINT_CONTRIBUTOR = 'SCO'
    CODE_SPRINT_REPORTER = 'SRE'
    CODE_ACCOUNT_MANAGER = 'SAM'
    CODE_SHADOW_COACH = 'SSC'
    CODE_SPRINT_OBSERVER = 'SOB'
    CODE_SPRINT_OTHER = 'SOT'

    # FASTRACK
    CODE_FASTRACK_TEAM_LEADER = 'FTL'
    CODE_FASTRACK_TEAM_MEMBER = 'FTM'
    CODE_FASTRACK_CURATOR = 'FCU'
    CODE_FASTRACK_CO_CURATOR = 'FCC'
    CODE_FASTRACK_SOLUTION_ACCELERATOR = 'FSA'
    CODE_FASTRACK_OBSERVER_EVALUATOR = 'FOE'
    CODE_FASTRACK_LOCAL_TEAM_MEMBER = 'FLM'

    # WORKSHOP
    CODE_WORKSHOP_SPEAKER = 'WSP'
    CODE_WORKSHOP_TRAINER = 'WTR'

    # SWARM
    CODE_SWARM_ADVISOR = 'SWA'

    # SUMMITS
    CODE_SUMMIT_COLLABORATOR = 'SUC'
    CODE_SUMMIT_SPEAKER = 'SUS'
    CODE_SUMMIT_FACILITATOR = 'SUF'
    CODE_SUMMIT_ORGANIZER = 'SUO'

    # TICKET
    CODE_TICKET_ADVISOR = 'ACA'

    # TALK
    CODE_TALK_SPEAKER = 'TAS'

    # DISRUPTION SESION
    CODE_DISRUPTION_SPEAKER = 'DSD'

    # CERTIFICATION PROGRAM
    CODE_PROGRAM_MASTER_TRAINER = 'CMT'
    CODE_PROGRAM_MENTOR_COACH = 'CMC'
    CODE_PROGRAM_ADVISOR = 'CAD'
    CODE_PROGRAM_DISRUPTOR = 'CDI'

    # OTHER
    CODE_OTHER_ADVISOR = 'OAD'
    CODE_OTHER_COACH = 'OCO'
    CODE_OTHER_CONSULTANT = 'OCN'
    CODE_OTHER_SPEAKER = 'OSP'
    CODE_OTHER_TRAINER = 'OTR'
    CODE_OTHER_DISRUPTOR = 'ODR'
    CODE_OTHER_OTHER = 'OOO'

    CODE_CHOICES = (
        (CODE_SPRINT_HEAD_COACH, 'Head Coach'),
        (CODE_SPRINT_COACH, 'Sprint Coach'),
        (CODE_AWAKE_SPEAKER, 'Awake Speaker'),
        (CODE_ALIGN_TRAINER, 'Align Trainer'),
        (CODE_ADVISOR, 'Advisor'),
        (CODE_DISRUPTOR, 'Disruptor'),
        (CODE_DISRUPTOR_SPEAKER, 'Disruptor Speaker'),
        (CODE_DELIVERY_MANAGER, 'Delivery Manager'),
        (CODE_SPRINT_PARTICIPANT, 'Sprint Participant'),
        (CODE_SPRINT_CONTRIBUTOR, 'Sprint Contributor'),
        (CODE_SPRINT_REPORTER, 'Reporter'),
        (CODE_ACCOUNT_MANAGER, 'Account Manager'),
        (CODE_SHADOW_COACH, 'Shadow Coach'),
        (CODE_SPRINT_OTHER, 'Other'),

        (CODE_FASTRACK_TEAM_LEADER, 'Team Leader'),
        (CODE_FASTRACK_TEAM_MEMBER, 'Team Member'),
        (CODE_FASTRACK_CURATOR, 'Curator'),
        (CODE_FASTRACK_CO_CURATOR, 'Co-Curator'),
        (CODE_FASTRACK_SOLUTION_ACCELERATOR, 'Solution Accelerator'),
        (CODE_FASTRACK_OBSERVER_EVALUATOR, 'Observer/Evaluator'),
        (CODE_FASTRACK_LOCAL_TEAM_MEMBER, 'Local Team Member'),

        (CODE_WORKSHOP_SPEAKER, 'Speaker'),
        (CODE_WORKSHOP_TRAINER, 'Trainer'),

        (CODE_SWARM_ADVISOR, 'Advisor'),

        (CODE_SUMMIT_COLLABORATOR, 'Collaborator'),
        (CODE_SUMMIT_SPEAKER, 'Speaker'),
        (CODE_SUMMIT_FACILITATOR, 'Facilitator'),
        (CODE_SUMMIT_ORGANIZER, 'Organizer'),

        (CODE_TICKET_ADVISOR, 'Advisor'),

        (CODE_TALK_SPEAKER, 'Speaker'),

        (CODE_DISRUPTION_SPEAKER, 'Disruptor'),

        (CODE_OTHER_ADVISOR, 'Advisor'),
        (CODE_OTHER_COACH, 'Coach'),
        (CODE_OTHER_CONSULTANT, 'Consultant'),
        (CODE_OTHER_SPEAKER, 'Speaker'),
        (CODE_OTHER_TRAINER, 'Trainer'),
        (CODE_OTHER_DISRUPTOR, 'Disruptor'),
        (CODE_OTHER_OTHER, 'Other'),

        (CODE_PROGRAM_MASTER_TRAINER, 'Master Trainer'),
        (CODE_PROGRAM_MENTOR_COACH, 'Mentor Coach'),
        (CODE_PROGRAM_ADVISOR, 'Avisor'),
        (CODE_PROGRAM_DISRUPTOR, 'Disruptor'),

    )

    CODE_CERTIFICATION_AMBASSADOR = 'CEA'
    CODE_CERTIFICATION_BOARD_ADVISOR = 'CBA'
    CODE_CERTIFICATION_CONSULTANT = 'CCO'
    CODE_CERTIFICATION_FOUNDATIONS = 'CFO'
    CODE_CERTIFICATION_SPRINT_COACH = 'CSC'
    CODE_CERTIFICATION_TRAINER = 'CTR'

    CERTIFICATION_CODE_CHOICES = (
        (CODE_CERTIFICATION_AMBASSADOR, 'ExO Ambassador'),
        (CODE_CERTIFICATION_BOARD_ADVISOR, 'ExO Board Advisor'),
        (CODE_CERTIFICATION_CONSULTANT, 'ExO Consultant'),
        (CODE_CERTIFICATION_FOUNDATIONS, 'ExO Foundations'),
        (CODE_CERTIFICATION_SPRINT_COACH, 'ExO Sprint Coach'),
        (CODE_CERTIFICATION_TRAINER, 'ExO Trainer'),
    )
