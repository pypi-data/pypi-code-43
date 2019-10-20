# -*- coding: utf-8 -*-
from .job import Job
from drummer.database import SqliteSession, Schedule

class JobLoader:
    """Loads schedules from database and generates related <Job> objects. """

    def __init__(self, config):

        self.config = config

    def load_jobs(self):
        """Loads <job> objects from database schedules. """

        config = self.config

        # get all enabled schedules
        session = SqliteSession.create(config)

        schedules = session.query(Schedule).filter(Schedule.enabled==True).all()

        session.close()

        jobs = [Job(sched) for sched in schedules]

        return jobs

    def load_job_by_id(self, schedule_id):
        """Loads a schedulation from database and generates the related <job>. """

        config = self.config

        # get all enabled schedules
        session = SqliteSession.create(config)

        sched = session.query(Schedule).filter(Schedule.id==schedule_id).one()

        session.close()

        return Job(sched)
