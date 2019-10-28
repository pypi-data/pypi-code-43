# -*- coding: utf-8 -*-
"""Job events.

This module includes all commands related to job management.

All these commands subclass RemoteCommand because they are executed remotely by
Drummered service.
"""
from drummer.messages import Response, StatusCode, FollowUp
from drummer.database import SqliteSession, Schedule

class JobAddEvent:

    def __init__(self, config):

        self.config = config

    def execute(self, request):

        config = self.config

        response = Response()
        follow_up = FollowUp('RELOAD')

        # create db session
        session = SqliteSession.create(config)

        try:

            # get schedulation data from the user
            job_data = request.data

            # create and add job object
            job = Schedule(name=job_data['name'],
                description=job_data['description'],
                cronexp=job_data['cronexp'],
                parameters=job_data['parameters'],
                enabled=job_data['enabled'])

            # save
            session.add(job)
            session.commit()

        except Exception as err:
            response.set_status(StatusCode.STATUS_ERROR)
            msg = f'Impossible to add the job: {str(err)}.'
            response.set_data({'msg': msg})

        else:
            response.set_status(StatusCode.STATUS_OK)
            response.set_data({'msg': 'Job has been added.'})

        finally:
            session.close()

        return response, follow_up


class JobListEvent:

    def __init__(self, config):

        self.config = config

    def execute(self, request):

        config = self.config

        response = Response()

        follow_up = FollowUp(None)

        data = {}

        try:

            # get all schedules
            session = SqliteSession.create(config)
            schedules = session.query(Schedule).group_by(Schedule.name).all()
            session.close()

            job_list = []
            for s in schedules:

                d = {}
                d['id'] = s.id
                d['name'] = s.name
                d['description'] = s.description
                d['cronexp'] = s.cronexp
                d['enabled'] = s.enabled

                job_list.append(d)

            data['Result'] = job_list

        except Exception:
            response.set_status(StatusCode.STATUS_ERROR)

        else:
            response.set_status(StatusCode.STATUS_OK)

        finally:
            response.set_data(data)

        return response, follow_up


class JobRemoveEvent:

    def __init__(self, config):

        self.config = config

    def execute(self, request):

        config = self.config

        # get schedulation id
        args = request.data
        job_id = args['job_id']

        response = Response()
        follow_up = FollowUp('RELOAD')

        # create db session
        session = SqliteSession.create(config)

        try:

            # delete
            sched_to_remove = session.query(Schedule).filter(Schedule.id==job_id).one()
            session.delete(sched_to_remove)

            # save
            session.commit()

        except Exception:
            response.set_status(StatusCode.STATUS_ERROR)
            response.set_data({'msg': 'Impossible to remove the job.'})

        else:
            response.set_status(StatusCode.STATUS_OK)
            response.set_data({'msg': 'Job has been removed.'})

        finally:
            session.close()

        return response, follow_up


class JobDisableEvent:

    def __init__(self, config):

        self.config = config

    def execute(self, request):

        config = self.config

        # get schedulation id
        args = request.data
        job_id = args['job_id']

        response = Response()
        follow_up = FollowUp('RELOAD')

        # create db session
        session = SqliteSession.create(config)

        try:

            # disable
            sched = session.query(Schedule).filter(Schedule.id==job_id).one()
            sched.enabled = False

            # save
            session.add(sched)
            session.commit()

        except Exception:
            response.set_status(StatusCode.STATUS_ERROR)
            response.set_data({'msg': 'Impossible to disable the job.'})

        else:
            response.set_status(StatusCode.STATUS_OK)
            response.set_data({'msg': 'Job has been disabled.'})

        finally:
            session.close()

        return response, follow_up


class JobEnableEvent:

    def __init__(self, config):

        self.config = config

    def execute(self, request):

        config = self.config

        # get schedulation id
        args = request.data
        job_id = args['job_id']

        response = Response()
        follow_up = FollowUp('RELOAD')

        # create db session
        session = SqliteSession.create(config)

        try:

            # enable
            sched = session.query(Schedule).filter(Schedule.id==job_id).one()
            sched.enabled = True

            # save
            session.add(sched)
            session.commit()

        except Exception:
            response.set_status(StatusCode.STATUS_ERROR)
            response.set_data({'msg': 'Impossible to enable the job.'})

        else:
            response.set_status(StatusCode.STATUS_OK)
            response.set_data({'msg': 'Job has been enabled.'})

        finally:
            session.close()

        return response, follow_up


class JobExecEvent:

    def __init__(self, config):

        self.config = config

    def execute(self, request):

        config = self.config

        # get schedulation id
        args = request.data
        job_id = args['job_id']

        follow_up = FollowUp('EXECUTE', job_id)

        response = Response()
        response.set_status(StatusCode.STATUS_OK)
        response.set_data({'msg': 'Job has been queued for execution.'})

        return response, follow_up


class JobGetEvent:

    def __init__(self, config):

        self.config = config

    def execute(self, request):

        config = self.config

        response = Response()
        follow_up = FollowUp(None)

        data = {}

        try:

            # get schedulation id
            args = request.data
            job_id = args['job_id']

            # get all schedules
            session = SqliteSession.create(config)

            job = session.query(Schedule).filter(Schedule.id==job_id).one()

            session.close()

            job_dict = {
                'id': job.id,
                'name': job.name,
                'description': job.description,
                'cronexp': job.cronexp,
                'enabled': job.enabled,
                'parameters': job.parameters,
            }

            data['Result'] = job_dict

        except Exception:
            response.set_status(StatusCode.STATUS_ERROR)

        else:
            response.set_status(StatusCode.STATUS_OK)

        finally:
            response.set_data(data)

        return response, follow_up
