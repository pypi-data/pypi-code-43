

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import and_

from syncurity_utils.db.base import Base
from syncurity_utils.db.alert import Alert


class StackstormDB(object):
    """
        This class helps in connecting to the stackstorm db.
    """
    def __init__(self, user= None, password=None, db_name=None, host=None, port=5432):
        self._build_session(user, password, db_name, host, port)

    def _build_session(self, user, password=None, db_name=None, host=None, port=5432):
        if (user is None
                or password is None
                or db_name is None
                or host is None):
            raise Exception("StackstormDB - Error creating instance - please check your parameters")

        connection = 'postgresql://{}:{}@{}:{}/{}'.format(user, password, host, port, db_name)

        engine = create_engine(connection)
        session = sessionmaker(bind=engine)
        Base.metadata.create_all(engine)
        self.session = session()

    def add_alert(self, alert):
        """
            Adds a single alert
        """
        try:
            self.session.add(alert)
            self.session.commit()
            self.session.close()
        except SQLAlchemyError as e:
            error = str(e.__dict__['orig'])
            return error

    def add_bulk_alerts(self, alerts):
        """
            Adds a bunch of alerts in one transaction
        """
        try:
            self.session.bulk_save_objects(alerts)
            self.session.commit()
            self.session.close()
        except SQLAlchemyError as e:
            error = str(e.__dict__['orig'])
            return error

    def query_alerts(self, alert):
        """
            Gets a list of alerts.
        """
        try:
            alerts = self.session.query(alert).all()
            return alerts
        except SQLAlchemyError as e:
            error = str(e.__dict__['orig'])
            return error

    def get_alert(self, alert_id):
        """
            Gets a single alert by Id
        """
        try:
            query = self.session.query(Alert).get(alert_id)
            return query
        except SQLAlchemyError as e:
            error = str(e.__dict__['orig'])
            return error

    def get_all_alerts(self):
        """
            Gets all alerts
        """
        try:
            alerts = self.session.query(Alert).all()
            return alerts

        except SQLAlchemyError as e:
            error = str(e.__dict__['orig'])
            return error

    def get_alerts(self, sensor_ref_name, tenant_name= None):
        """
            Gets all alerts
        """
        try:
            if tenant_name is None:
                alerts = self.session.query(Alert).filter(
                        and_(Alert.sensor_ref_name == sensor_ref_name)).all()
            else:
                alerts = self.session.query(Alert).filter(
                        and_(Alert.sensor_ref_name == sensor_ref_name, Alert.tenant_name == tenant_name)).all()
            return alerts
        except SQLAlchemyError as e:
            error = str(e.__dict__['orig'])
            return error

    def get_child_alerts(self, parent_id):
        """
        Returns a dictionary of alerts
        :param parent_id: Parent Alert Id
        :return: dictionary of alerts
        """
        try:
            alerts = self.session.query(Alert).filter(
                        and_(Alert.parent_alert_id == parent_id)).all()
            return alerts
        except SQLAlchemyError as e:
            error = str(e.__dict__['orig'])
            return error

    def delete_alert(self, alert):
        """
            Deletes Alert by alert object.
        """

        try:
            self.session.delete(self, alert)
            self.session.commit()
            self.session.close()
        except SQLAlchemyError as e:
            error = str(e.__dict__['orig'])
            return error

    def delete_alert_by_id(self, alert_id):
        """
            Deletes alert by alert_id
        """
        try:
            self.session.query(Alert).filter(Alert.id == alert_id).delete()
            self.session.commit()
            self.session.close()
        except SQLAlchemyError as e:
            error = str(e.__dict__['orig'])
            return error

    def __del__(self):
        """
            Make sure we kill the session when this object is destroyed.
        """
        self.session.close()


