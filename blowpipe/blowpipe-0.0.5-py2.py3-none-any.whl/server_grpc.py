import time
from blowpipe import App
from blowpipe import model
from blowpipe import constants
from blowpipe.logger import Logger, LogLine
from datetime import datetime
from blowpipe.protos import objects_pb2
from blowpipe.protos import services_pb2_grpc
from concurrent import futures
import grpc


class ServerImpl(services_pb2_grpc.BlowpipeServicer):

    def __init__(self, parent):
        self.parent = parent
        self.logger = Logger("ServerImpl")

    def GetAllConfig(self, request, context):
        self.logger.debug(".GetAllConfig(..)")
        server = self.parent
        session = server.db.create_session()
        try:
            all_config = server.db.get_all_config(session)
            for c in all_config:
                response = objects_pb2.GetConfigResponse(success=True, key=c.key, value=c.value)
                yield response
        finally:
            session.close()

    def GetConfig(self, request, context):
        self.logger.debug(".GetConfig(..)")
        server = self.parent
        session = server.db.create_session()
        try:
            c = server.db.get_config(key=request.key, session=session)
            if c is None:
                response = objects_pb2.GetConfigResponse(success=False, key=request.key, value=None)
            else:
                response = objects_pb2.GetConfigResponse(success=True, key=request.key, value=c.value)
            return response
        finally:
            session.close()

    def SetConfig(self, request, context):
        self.logger.debug(".SetConfig(..)")
        server = self.parent
        session = server.db.create_session()
        try:
            server.db.set_config(request.key, request.value, session)
            session.commit()
            response = objects_pb2.SetConfigResponse(success=True, key=request.key)
            return response
        finally:
            session.close()

    def DeleteConfig(self, request, context):
        self.logger.debug(".DeleteConfig(..)")
        server = self.parent
        session = server.db.create_session()
        try:
            server.db.delete_config(request.key, session)
            session.commit()
            response = objects_pb2.DeleteConfigResponse(success=True, key=request.key, message="Ok")
            return response
        finally:
            session.close()

    def ManualTrigger(self, request, context):
        self.logger.debug(".ManualTrigger(..)")
        workflow_id = request.id
        server = self.parent
        if server.config.is_repository:
            response = objects_pb2.ManualTriggerResponse(success=False, workflow_id=None, run_id=None,
                                                         message="This is a repository, not a server.")
            return response
        else:
            session = server.db.create_session()
            try:
                defn = server.db.get_workflow_definition(workflow_id=request.id, session=session)
                if defn is None:
                    response = objects_pb2.ManualTriggerResponse(success=False, workflow_id=workflow_id, message="No such workflow.")
                else:
                    job = server.manual_trigger(defn, session)
                    response = objects_pb2.ManualTriggerResponse(success=True, workflow_id=workflow_id, run_id=job.id, message="OK (got workflow and manually triggered it).")
                return response
            finally:
                session.close()

    def SetWorkflowState(self, request, context):
        self.logger.debug(".SetWorkflowState(..)")
        server = self.parent
        session = server.db.create_session()
        try:
            defn = server.db.get_workflow_definition(workflow_id=request.id, session=session)
            if defn is None:
                response = objects_pb2.SetWorkflowStateResponse(id=request.id, success=False, message="No such workflow.")
            else:
                if request.state == constants.STATE_ENABLED:
                    server.db.enable_workflow(request.id, session)
                elif request.state == constants.STATE_DISABLED:
                    server.db.disable_workflow(request.id, session)
                response = objects_pb2.SetWorkflowStateResponse(id=request.id, success=True, message="OK.")
            return response
        finally:
            session.close()

    def ListWorkflows(self, request, context):
        self.logger.debug(".ListWorkflows(..)")
        server = self.parent
        session = server.db.create_session()
        try:
            defns = server.db.get_workflow_definitions(include_deleted=request.include_deleted, session=session)
            for defn in defns:
                workflow = defn.get_workflow()
                date_created = datetime.strftime(defn.created, "%Y-%m-%d %H:%M%:%S")
                last_modified = datetime.strftime(defn.last_modified, "%Y-%m-%d %H:%M:%S")
                rpcworkflow = objects_pb2.Workflow(id=defn.id, version=defn.version, is_enabled=defn.is_enabled, yaml=workflow.to_yaml(), is_deleted=defn.is_deleted, created=date_created, last_modified=last_modified)
                yield rpcworkflow
        finally:
            session.close()

    def ListRunningWorkflows(self, request, context):
        self.logger.debug(".ListRunningWorkflows(..)")
        server = self.parent
        session = server.db.create_session()
        try:
            if request.include_completed:
                is_active_only = False
            else:
                is_active_only = True

            defns = server.db.get_running_workflows(session=session, is_active_only=is_active_only)
            for defn in defns:
                workflow = defn.get_workflow()
                date_created = datetime.strftime(defn.created, "%Y-%m-%d %H:%M%:%S")
                last_modified = datetime.strftime(defn.last_modified, "%Y-%m-%d %H:%M:%S")
                definition = defn.workflow_definition
                rpcworkflow = objects_pb2.Workflow(id=definition.id, version=definition.version, is_enabled=definition.is_enabled, yaml=workflow.to_yaml(), is_deleted=defn.workflow_definition.is_deleted, created=datetime.strftime(definition.created, "%Y-%m-%d %H:%M%:%S"), last_modified=datetime.strftime(definition.last_modified, "%Y-%m-%d %H:%M%:%S"))
                response = objects_pb2.RunningWorkflow(workflow=rpcworkflow, id=defn.id, created=date_created, state=defn.state, last_modified=last_modified)
                yield response
        finally:
            session.close()

    def GetLog(self, request, context):
        self.logger.debug(".GetLog(..)")
        try:

            date_from = request.date_from
            date_to = request.date_to

            def filter_fn(line:LogLine):
                # filters the line based on the request selection criteria
                run_id_ok = line.run_id == request.run_id
                workflow_id_ok = line.workflow_id == request.workflow_id
                date_from_ok = True
                date_to_ok = True
                if request.date_from != "":
                    date_from_ok = line.date >= request.date_from
                if request.date_to != "":
                    date_to_ok = line.date <= request.date_to
                return date_from_ok and date_to_ok and run_id_ok and workflow_id_ok

            from blowpipe import tail
            t = tail.Tail(App.Config.get_syslog_filename(), sleep=1)

            def callback():
                t.stop()

            context.add_callback(callback)

            # first off just write out the syslog
            f = open(App.Config.get_syslog_filename(), 'r')
            for line in f:
                log_line = LogLine(line)
                if filter_fn(log_line):
                    rpclog = objects_pb2.GetLogResponse(log_level="", log_class="", log_time="", log_message=str(line))
                    yield rpclog
            f.close()

            if request.tail:
                # ok this is complicated
                # so in this situation, I need to stop tailing the file when
                # the RPC connection is dropped; this is done by
                # registering a callback with the context

                # the tail is the thing that watches the syslog and writes out the results
                # from blowpipe import tail
                # t = tail.Tail(App.Config.get_syslog_filename(), sleep=1)
                #
                # def callback():
                #     t.stop()
                #
                # context.add_callback(callback)

                for line in t.start():
                    log_line = LogLine(line)
                    if filter_fn(log_line):
                        rpclog = objects_pb2.GetLogResponse(log_level="", log_class="", log_time="", log_message=str(line))
                        yield rpclog

            self.logger.debug("./GetLog(..)")

        except Exception as err:
            self.logger.debug("./GetLog(..) exiting with error")
            self.logger.debug(err)

    def ListWorkflowHistory(self, request, context):
        self.logger.debug(".ListWorkflowHistory(..)")
        server = self.parent
        session = server.db.create_session()
        try:
            defns = server.db.get_workflow_definitions_history(request.id, session)
            for defn in defns:
                rpcworkflow = objects_pb2.WorkflowHistory(id=defn.id, date=str(defn.created), version=defn.version, reason=defn.reason, yaml=defn.yaml)
                yield rpcworkflow
        finally:
            session.close()

    def AddWorkflow(self, request, context):
        self.logger.debug(".AddWorkflow(..)")
        workflow = model.Workflow()
        workflow.load_raw(request.yaml)
        session = self.parent.db.create_session()
        try:
            workflow_definition = self.parent.db.add_workflow_definition(workflow, session)
            workflow_id = workflow_definition.id
            return objects_pb2.AddWorkflowResponse(id=workflow_id, success=True)
        finally:
            session.close()

    def UpdateWorkflow(self, request, context):
        self.logger.debug(".UpdateWorkflow(..)")
        workflow_id = request.id
        reason = request.reason
        yaml = request.yaml
        session = self.parent.db.create_session()
        try:
            workflow_definition = self.parent.db.update_workflow_definition(workflow_id, yaml, reason, session)
            return objects_pb2.UpdateWorkflowResponse(id=workflow_id, success=True)
        finally:
            session.close()

    def DeleteWorkflow(self, request, context):
        self.logger.debug(".DeleteWorkflow(); request=" + str(request))
        workflow_id = request.id
        self.logger.debug(".DeleteWorkflow: workflow_id: " + workflow_id)
        session = self.parent.db.create_session()
        try:
            result = self.parent.db.delete_workflow_definition(workflow_id, session)
            response = objects_pb2.DeleteWorkflowResponse(id=workflow_id, success=result)
            session.commit()
            return response
        finally:
            session.close()

    def Status(self, request, context):
        server = self.parent
        session = self.parent.db.create_session()
        try:
            workflow_count = self.parent.db.count_workflow_definitions(session)
            msg = ">>> Blowpipe Server"
            msg += "\n>>> Version   : " + constants.SERVER_VERSION
            msg += "\n>>> Started   : " + datetime.strftime(server.get_started(), "%Y-%m-%d %H:%M:%S")
            msg += "\n>>> DB_Path   : " + server.db.get_sqlite_filename()
            msg += "\n>>> Workflows : " + str(workflow_count)
            from blowpipe import docker_utils
            if docker_utils.is_docker_available():
                msg += "\n>>> Docker    : available."
            else:
                msg += "\n>>> Docker    : unavailable."

            response = objects_pb2.StatusResponse(message=msg)
            return response
        finally:
            session.close()

    def GetWorkflow(self, request, context):
        server = self.parent
        workflow_id = request.id
        version = request.version
        session = server.db.create_session()
        try:
            if version == 0:
                defn = server.db.get_workflow_definition(workflow_id, session)
                if defn is not None:
                    workflow = objects_pb2.Workflow(id=defn.id, yaml=defn.yaml)
                    response = objects_pb2.GetWorkflowResponse(success=True, message="", workflow=workflow)
                    return response
                else:
                    response = objects_pb2.GetWorkflowResponse(success=False, message="No such workflow.", workflow=None)
                    return response

            else:
                defn = server.db.get_workflow_definition_history_with_version(workflow_id, version, session)
                if defn is None:
                    response = objects_pb2.GetWorkflowResponse(success=False, message="Version '" + str(version) + "' not found.", workflow=None)
                    return response
                else:
                    workflow = objects_pb2.Workflow(id=defn.id, yaml=defn.yaml)
                    response = objects_pb2.GetWorkflowResponse(success=True, message="", workflow=workflow)
                    return response
        finally:
            session.close()


class GRPCServer:
    def __init__(self, parent):
        self.parent = parent
        self._is_running = False
        self._quit = False
        self.name = "GRPCServer"
        self.logger = Logger("GRPCServer")
        self.server = None

    def execute(self, blocking=True):
        try:
            self.logger.debug(".execute(), starting, setting _is_running to True")
            self._is_running = True
            self.server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
            server = self.server
            services_pb2_grpc.add_BlowpipeServicer_to_server(ServerImpl(self.parent), server)
            ip = self.parent.config.get_grpc_server_ip()
            if ip in ["localhost", "127.0.0.1"]:
                ip = "::"
            address = "[" + ip + "]:" + str(self.parent.config.get_grpc_port())
            server.add_insecure_port(address)
            server.start()
            if blocking:
                self.logger.debug(".execute(), blocking = true, will now sleep")
                while not self._quit:
                    time.sleep(0.1)
                self.logger.debug(".execute() quit is True, now calling .stop on the grpc server.")
                server.stop(grace=None)
                self.logger.debug(".execute() quit is True, called stop, will now set is_running to false.")
        except Exception as e:
            self.logger.debug(".execute() exception")
            print(e)
        finally:
            self._is_running = False

    def quit(self):
        self._quit = True

    def on_quit(self):
        """
        called by the threadpool when it has quit
        :return:
        """
        self.logger.debug("on_quit()")

    def is_running(self):
        return self._is_running
