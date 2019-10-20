# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.apps import AppConfig


class RuntimeConfig(AppConfig):
    name = 'goflow.runtime'

    def ready(self):
        from goflow.runtime.signals import workflow_item_forwarded, workflow_item_completed, workflow_item_activated, \
            workflow_process_instance_created, workflow_process_instance_completed

        from goflow.runtime.signals import workflow_process_instance_created_log, \
            workflow_process_instance_completed_log, workflow_item_activated_log, workflow_item_completed_log, \
            workflow_item_forwarded_log

        # # Fired when some event happens during the life of a WorkItem
        # workflow_item_created = django.dispatch.Signal()
        workflow_process_instance_created.connect(workflow_process_instance_created_log)
        workflow_process_instance_completed.connect(workflow_process_instance_completed_log)
        workflow_item_activated.connect(workflow_item_activated_log)
        workflow_item_completed.connect(workflow_item_completed_log)
        workflow_item_forwarded.connect(workflow_item_forwarded_log)
