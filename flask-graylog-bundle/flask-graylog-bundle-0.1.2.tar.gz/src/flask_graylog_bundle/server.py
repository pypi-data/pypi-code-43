#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. codeauthor:: Cédric Dumay <cedric.dumay@gmail.com>


"""
import logging
from cdumay_error import NotFound, ValidationError
from flask_graylog_bundle import GraylogExt, MESSAGE_MAP
from cdumay_rest_client.client import RESTClient
from flask_graylog_bundle import validators

logger = logging.getLogger(__name__)


class GraylogAPIServer(GraylogExt):
    @property
    def client(self):
        if self._client is None:
            self._client = RESTClient(
                server=self.app.config['GRAYLOG_API_URL'],
                username=self.app.config['GRAYLOG_API_USERNAME'],
                password=self.app.config['GRAYLOG_API_PASSWORD'],
                timeout=self.app.config.get("GRAYLOG_API_TIMEOUT", 10),
                headers={"X-Requested-By": "flask-graylog-bundle"}
            )

        return self._client

    @staticmethod
    def _build_path(spath):
        return "/" + "/".join(spath)

    def _get(self, spath):
        return self.client.do_request(
            method="GET", path=self._build_path(spath)
        )

    def _list(self, spath):
        return self.client.do_request(
            method="GET", path=self._build_path(spath)
        )[spath[0]]

    def _add(self, spath, data=None, params=None):
        return self.client.do_request(
            method="POST", path=self._build_path(spath), data=data,
            params=params
        )

    def _del(self, spath, data=None, params=None):
        return self.client.do_request(
            method="DELETE", path=self._build_path(spath), data=data,
            params=params
        )

    def _update(self, spath, data=None, params=None):
        return self.client.do_request(
            method="PUT", path=self._build_path(spath), data=data,
            params=params
        )

    def _exists(self, spath):
        try:
            self._get(spath=spath)
            return True
        except NotFound:
            return False

    ############################################################################
    # users
    @property
    def users(self):
        return self._list(spath=['users'])

    def user_add(self, data):
        return self._add(
            spath=['users'], data=validators.UserSchema().load(data)
        )

    def user_del(self, username):
        return self._del(spath=['users', username])

    def user_get(self, username):
        return self._get(spath=['users', username])

    def user_exists(self, username):
        return self._exists(spath=['users', username])

    def user_is_admin(self, username):
        return "*" in self.user_get(username).get('permissions', list())

    def user_set_password(self, username, password):
        if password in ("", None):
            logger.error(MESSAGE_MAP["PasswordNull"])
            raise ValidationError(
                message=MESSAGE_MAP["PasswordNull"],
                extra=dict(msgid="PasswordNull")
            )
        return self._update(
            spath=['users', username, 'password'],
            data={"password": password}
        )

    ############################################################################
    # roles
    @property
    def roles(self):
        return self._list(spath=['roles'])

    def role_add(self, data):
        return self._add(
            spath=['roles'],
            data=validators.RoleSchema().load(data)
        )

    def role_del(self, rolename):
        return self._del(spath=['roles', rolename])

    def role_get(self, rolename):
        return self._get(spath=['roles', rolename])

    def role_exists(self, rolename):
        return self._exists(spath=['roles', rolename])

    def role_member_add(self, rolename, username):
        return self._update(spath=['roles', rolename, 'members', username])

    def role_member_del(self, rolename, username):
        return self._del(spath=['roles', rolename, 'members', username])

    def role_update(self, rolename, data):
        return self._update(
            spath=['roles', rolename],
            data=validators.RoleSchema().load(data)
        )

    def role_permissions_add(self, rolename, permissions):
        grole = self.role_get(rolename)
        has_change = False
        for permission in permissions:
            if permission not in grole['permissions']:
                grole['permissions'].append(permission)
                has_change = True

        if has_change is True:
            self.role_update(rolename, grole)

        return grole

    def role_permissions_del(self, rolename, permissions):
        grole = self.role_get(rolename)
        has_change = False
        for permission in permissions:
            if permission in grole['permissions']:
                grole['permissions'].remove(permission)
                has_change = True

        if has_change is True:
            self.role_update(rolename, grole)

        return grole

    ############################################################################
    # dashboards
    @property
    def dashboards(self):
        return self._list(spath=['dashboards'])

    def dashboard_add(self, data):
        return self._add(
            spath=['dashboards'],
            data=validators.DashboardSchema().load(data)
        )

    def dashboard_del(self, dashboard_id):
        return self._del(spath=['dashboards', dashboard_id])

    def dashboard_get(self, dashboard_id):
        return self._get(spath=['dashboards', dashboard_id])

    def dashboard_exists(self, dashboard_id):
        return self._exists(spath=['dashboards', dashboard_id])

    def dashboard_update(self, dashboard_id, data):
        return self._update(
            spath=['dashboards', dashboard_id],
            data=validators.DashboardSchema().load(data)
        )

    def dashboard_widget_add(self, dashboard_id, data):
        return self._add(
            spath=['dashboards', dashboard_id, 'widgets'],
            data=validators.DashboardWidgetSchema().load(data)
        )

    def dashboard_widgets_positions(self, dashboard_id, data):
        return self._update(
            spath=['dashboards', dashboard_id, 'positions'],
            data=validators.DashboardPositionSchema().load(data)
        )

    ############################################################################
    # streams
    @property
    def streams(self):
        return self._list(spath=['streams'])

    def stream_add(self, data):
        return self._add(
            spath=['streams'],
            data=validators.StreamSchema().load(data)
        )

    def stream_update(self, stream_id, data):
        return self._update(
            spath=['streams', stream_id],
            data=validators.StreamSchema().load(data)
        )

    def stream_del(self, stream_id):
        return self._del(spath=['streams', stream_id])

    def stream_get(self, stream_id):
        return self._get(spath=['streams', stream_id])

    def stream_exists(self, stream_id):
        return self._exists(spath=['streams', stream_id])

    def stream_resume(self, stream_id):
        return self._add(spath=['streams', stream_id, 'resume'])

    def stream_pause(self, stream_id):
        return self._add(spath=['streams', stream_id, 'pause'])

    def stream_rule_add(self, stream_id, data):
        return self._add(
            spath=['streams', stream_id, 'rules'],
            data=validators.StreamRuleSchema().load(data)
        )

    def stream_rule_update(self, stream_id, rule_id, data):
        return self._update(
            spath=['streams', stream_id, 'rules', rule_id],
            data=validators.StreamRuleSchema().load(data)
        )

    def stream_rule_list(self, stream_id):
        return self._list(spath=['streams', stream_id, 'rules'])

    def stream_rule_del(self, stream_id, rule_id):
        return self._del(spath=['streams', stream_id, 'rules', rule_id])

    def stream_alert_condition_add(self, stream_id, data):
        return self._add(
            spath=['streams', stream_id, 'alerts', 'conditions'],
            data=validators.AlertConditionSchema().load(data)
        )

    def stream_alert_condition_del(self, stream_id, condition_id):
        return self._del(
            spath=['streams', stream_id, 'alerts', 'conditions', condition_id]
        )

    def stream_alert_condition_update(self, stream_id, condition_id, data):
        return self._update(
            spath=['streams', stream_id, 'alerts', 'conditions', condition_id],
            data=validators.AlertConditionSchema().load(data)
        )

    def stream_alert_receiver_add(self, stream_id, user_or_email,
                                  typeof="users"):
        return self._add(
            spath=['streams', stream_id, 'alerts', 'receivers'],
            params=validators.AlertReceiverSchema().load(
                {"entity": user_or_email, "type": typeof}
            )
        )

    def stream_alert_receiver_del(self, stream_id, user_or_email,
                                  typeof="users"):
        return self._del(
            spath=['streams', stream_id, 'alerts', 'receivers'],
            params=validators.AlertReceiverSchema().load(
                {"entity": user_or_email, "type": typeof}
            )
        )
