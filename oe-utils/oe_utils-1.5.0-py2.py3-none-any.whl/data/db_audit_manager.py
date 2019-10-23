# -*- coding: utf-8 -*-
import logging

from oe_utils.data.data_managers import AuditManager

log = logging.getLogger(__name__)


def audit_manager(request):
    """
    Initialize and return the audit manager.

    The request must contain a method `request.db` to retrieve the current session.

    :param request: `pyramid.request.Request`
    :return: the audit manager
    """
    session = request.db
    return AuditManager(session)


def includeme(config):
    """
    Configure a `request.audit_managers` method to retrieve the audit manager.

    :param config:
    """
    config.add_request_method(audit_manager, reify=True)
