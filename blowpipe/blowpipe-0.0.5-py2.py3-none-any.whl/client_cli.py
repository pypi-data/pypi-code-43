import os
import sys
import blowpipe
from blowpipe import constants
from blowpipe import utils
from blowpipe import model
from blowpipe.protos import services_pb2_grpc
from blowpipe import client_grpc
from blowpipe.config import BlowpipeConfig


class BlowpipeClientConfig(BlowpipeConfig):

    def set_context(self, context):
        self.data["context"] = context

    def get_context(self):
        return self.data.get("context") or "default"


class BlowpipeClient:
    def __init__(self, config):
        self.config = config

    def ping(self):
        try:
            client = client_grpc.GRPCClient(self.config)
            client.Status()
            return True, client
        except Exception:
            return False, None

    def manage_config(self, cli, client):
        subcommand = cli.get_or_die("config", "You must specify 'get', 'set' or 'rm'")
        if subcommand == "ls":
            all_config = client.GetAllConfig()
            arrs = []
            for c in all_config:
                arr = [c.key, c.value]
                arrs.append(arr)

            from tabulate import tabulate
            print(tabulate(arrs, headers=["Key", "Value"]))

        elif subcommand == "get":
            key = cli.get_or_default(subcommand, None)
            key = cli.get_or_die(subcommand, "You must specify a configuration key.")
            response = client.GetConfig(key)
            if response.success:
                print(response.value)
            else:
                print("No such key '" + key + "'")

        elif subcommand == "set":
            key = cli.get_or_die(subcommand, "You must specify a configuration key.")
            value = cli.get_or_die(key, "You must specify a configuration value.")
            if os.path.isfile(value):
                f = open(value)
                content = f.read()
                f.close()
                client.SetConfig(key, content)
            else:
                client.SetConfig(key, value)

        elif subcommand == "rm":
            key = cli.get_or_die(subcommand, "You must specify a configuration key.")
            client.DeleteConfig(key)
        else:
            print("You must specify 'get', 'set' or 'rm'")
            sys.exit(1)

    def status(self, cli, client):
        response = client.Status()
        print(response.message)
        return True

    def context(self, cli):
        ctx = cli.get_or_default("context", None)
        if ctx is None:
            # print the current context
            print(self.config.get_context())
        else:
            self.config.set_context(ctx)
            self.config.save()
        return True

    def add(self, cli, client):
        filename = cli.get_or_die("add")
        workflow = model.Workflow()
        workflow.load_file(filename)
        response = client.AddWorkflow(workflow)
        print("Success, added '" + filename + "', id=" + response.id)
        return True

    def update(self, cli, client):
        workflow_id = cli.get_or_die("update")
        filename = cli.get_or_die(workflow_id)
        reason = cli.get_or_die("-reason")
        workflow = model.Workflow()
        workflow.load_file(filename)
        response = client.UpdateWorkflow(workflow_id, workflow, reason)
        print("OK, updated '" + response.id + "'.")
        return True

    def enable(self, cli, client):
        workflow_id = cli.get_or_die("enable")
        request = blowpipe.protos.objects_pb2.SetStateRequest(id=workflow_id, state=constants.STATE_ENABLED)
        response = client.SetState(request)
        if response.success:
            print("OK, enabled '" + response.id + "'.")
            return True
        else:
            print("Failed, did not enable the workflow, msg=" + response.message)
            return False

    def disable(self, cli, client):
        workflow_id = cli.get_or_die("disable")
        request = blowpipe.protos.objects_pb2.SetStateRequest(id=workflow_id, state=constants.STATE_DISABLED)
        response = client.SetState(request)
        if response.success:
            print("OK, enabled '" + response.id + "'.")
            return True
        else:
            print("Failed, did not disable the workflow, msg=" + response.message)
            return False

    def ls(self, cli, client):
        is_deleted = cli.contains("-d")
        workflows = client.ListWorkflows(is_deleted)
        if len(workflows) == 0:
            print("Blowpipe is empty.")
        else:
            arrs = []
            for result in workflows:

                workflow = model.Workflow()
                workflow.load_raw(result.yaml)

                arr = [result.id, workflow.get_name(), result.version, result.last_modified, result.created, result.is_enabled, result.is_deleted]
                arrs.append(arr)

                """
                msg = result.id + "\t" + workflow.name() + "\t" + str(result.version) + "\t" + result.last_modified + "\t" + result.created + "\t"
                if result.is_enabled:
                    msg += " ENABLED"
                else:
                    msg += " DISABLED"

                if result.is_deleted:
                    msg += " DELETED "
                print(msg)
                """

            from tabulate import tabulate
            print(tabulate(arrs, headers=["ID", "Name", "Version", "Last Modified", "Created", "Enabled", "Deleted"]))
        return True

    def rm(self, cli, client):
        workflow_id = cli.get_or_die("rm")
        result = client.DeleteWorkflow(workflow_id)
        print("OK.")
        return True

    def ps(self, cli, client):
        from tabulate import tabulate
        include_completed = cli.contains("-a")
        since = None
        results = client.ListRunningWorkflows(include_completed, since)
        arrs = []
        for result in results:
            workflow_yaml = result.workflow.yaml
            workflow = blowpipe.model.Workflow(workflow_yaml)
            arr = [result.id,workflow.get_name(),result.state,result.created,result.last_modified]
            arrs.append(arr)
        arrs.reverse()
        print(tabulate(arrs, headers=["run_id", "Name", "State", "Created", "Last Modified"]))
        return True

    def rename(self, cli, client):
        workflow_id = cli.get_or_die("rename")
        new_name = cli.get_or_die(workflow_id)
        workflow = client.GetWorkflow(workflow_id)
        if workflow is not None:
            old_name = workflow.get_name()
            workflow.set_name(new_name)
            response = client.UpdateWorkflow(workflow_id, workflow, "Renamed (was '" + old_name + "', is now '" + new_name + "').")
            print("OK, renamed '" + response.id + "'.")
            return True
        else:
            print("No such workflow " + workflow_id + ".")
            return False

    def describe(self, cli, client):
        workflow_id = cli.get_or_die("describe")
        new_desc = cli.get_or_die(workflow_id)
        workflow = client.GetWorkflow(workflow_id)
        old_desc = workflow.get_description()
        workflow.set_description(new_desc)
        response = client.UpdateWorkflow(workflow_id, workflow, "Updated description.")
        print("OK, updated description '" + response.id + "'.")
        return True

    def cp(self, cli, client):
        print("cp")
        return True

    def cat(self, cli, client):
        workflow_id = cli.get_or_die("cat")
        version = int(cli.get_or_default("-version", 0))
        result = client.GetWorkflow(workflow_id, version)
        if result is not None:
            print(result.to_yaml())
            return True
        else:
            print("No such workflow.")
            return False

    def history(self, cli, client):
        workflow_id = cli.get_or_die("history")
        results = client.ListWorkflowHistory(workflow_id)
        from tabulate import tabulate
        arrs = []
        for result in results:
            arr = [result.version, result.date, result.reason]
            arrs.append(arr)
        arrs.reverse()
        print(tabulate(arrs, headers=["Version", "Date", "Reason"]))
        return True

    def pause(self, cli, client):
        print("pause")
        return True

    def resume(self, cli, client):
        print("resume")
        return True

    def log(self, cli, client):
        grep = cli.get_or_default("-grep", "")
        grepv = cli.get_or_default("-grepv", "")
        username = cli.get_or_default("-username", "")
        workflow_id = cli.get_or_default("-workflow_id", "")
        run_id = cli.get_or_default("-run_id", "")
        date_to = cli.get_or_default("-to", "")
        date_from = cli.get_or_default("-from", "")
        tail = cli.contains("-f")
        try:
            for response in client.GetLog(grep, grepv, username, workflow_id, run_id, date_from, date_to, tail):
                print(response.log_message.strip())
        except KeyboardInterrupt as ke:
            # this is okay
            pass
        return True

    def trigger(self, cli, client):
        workflow_id = cli.get_or_die("trigger")
        response = client.ManualTrigger(workflow_id)
        if response.success:
            print("Blowpipe trigger " + workflow_id + " success!\nRun ID is " + response.run_id)
            return True
        else:
            print("Failed to trigger: " + response.message)
            return False

    def validate(self, cli, client):
        print("validate")
        return True

    def version(self):
        msg = "blowpipe client version " + constants.CLIENT_VERSION
        print(msg)
        return True

    def usage(self, cli=None):
        utils.print_logo()
        LJUST = 50
        msg = "Blowpipe is a tool for data processing pipelines."
        msg += "\n"
        msg += "\nUsage:"
        msg += "\n"
        msg += "\n\tblowpipe <command> [arguments]"
        msg += "\n"
        msg += "\nThe commands are:"
        msg += "\n"
        msg += "\n\tadd <FILE|URL>".ljust(LJUST) + "add a workflow"
        msg += "\n\tconfig".ljust(LJUST) + "(ls|get|set|rm) manages server configuration values"
        msg += "\n\tcancel $RUN_ID".ljust(LJUST) + "cancels a job"
        msg += "\n\tcontext".ljust(LJUST) + "manages client context"
        msg += "\n\tcat $WORKFLOW_ID".ljust(LJUST) + "print the workflow definition to STDOUT"
        msg += "\n\tdisable $WORKFLOW_ID".ljust(LJUST) + "disable a workflow"
        msg += "\n\tdescribe $WORKFLOW_ID \"the description\"".ljust(LJUST) + "alter the description of a workflow"
        msg += "\n\tenable $WORKFLOW_ID".ljust(LJUST) + "enable a workflow"
        msg += "\n\thistory $WORKFLOW_ID".ljust(LJUST) + "show revision history for workflow"
        msg += "\n\tinit".ljust(LJUST) + "initialise the db and home directory"
        msg += "\n\tls".ljust(LJUST) + "list workflows"
        msg += "\n\tlog -f ".ljust(LJUST) + "prints logs"
        msg += "\n\t    -run_id XXX "
        msg += "\n\t    -workflow_id XXXXX "
        msg += "\n\t    -grep \"xxxx\" "
        msg += "\n\t    -grepv \"xxxx\" "
        msg += "\n\t    -to \"yyyy-mm-dd hh:mm:ss\""
        msg += "\n\t    -from \"yyyy-mm-dd hh:mm:ss\""
        msg += "\n\t    -username xxxxx"
        msg += "\n\tps  -a".ljust(LJUST) + "list jobs"
        msg += "\n\tpause $RUN_ID".ljust(LJUST) + "force a job to pause processing"
        msg += "\n\trm $WORKFLOW_ID".ljust(LJUST) + "delete a workflow"
        msg += "\n\tresume $RUN_ID".ljust(LJUST) + "mark a job to resume processing"
        msg += "\n\trename $WORKFLOW_ID \"name\"".ljust(LJUST) + "rename a workflow"
        msg += "\n\trepository".ljust(LJUST) + "(ls|add|rm) manages repository"
        msg += "\n\tstatus".ljust(LJUST) + "print status of the server"
        msg += "\n\tserver".ljust(LJUST) + "run a blowpipe server"
        msg += "\n\ttrigger $WORKFLOW_ID".ljust(LJUST) + "forces a workflow to commence (starts a job)"
        msg += "\n\tupdate $WORKFLOW_ID <FILE|URL>".ljust(LJUST) + "update an existing workflow"
        msg += "\n\tversion".ljust(LJUST) + "prints out the version of the client"
        msg += "\n"
        msg += "\n"
        msg += "Use \"blowpipe help <command>\" for more information about the command."
        msg += "\n"
        print(msg)
        return True

    def test(self, cli):
        client = client_grpc.GRPCClient(self.config)
        return True

    def process(self, cli):
        if len(cli.argv) == 1:
            self.usage()
            sys.exit(1)

        command = cli.get_command()
        if command == "context":
            self.context(cli)
            return True
        elif command == "init":
            self.init()
            return True
        elif command == "version":
            self.version()
            return True

        ping_result, client = self.ping()

        if command == "login":
            return self.login(cli, client)
        elif command == "logout":
            return self.logout(cli, client)
        elif command == "search":
            return self.search(cli, client)
        elif command == "push":
            return self.push(cli, client)
        elif command == "pull":
            return self.pull(cli, client)
        elif command == "servers":
            return self.servers(cli, client)
        elif command == "config":
            return self.manage_config(cli, client)
        elif command == "add":
            if not ping_result:
                print("Server is unavailable.")
                return False
            return self.add(cli, client)
        elif command == "update":
            if not ping_result:
                print("Server is unavailable.")
                return False
            return self.update(cli, client)
        elif command == "status":
            if not ping_result:
                print("Server is unavailable.")
                return False
            return self.status(cli, client)
        elif command == "ls":
            if not ping_result:
                print("Server is unavailable.")
                return False
            return self.ls(cli, client)
        elif command == "history":
            if not ping_result:
                print("Server is unavailable.")
                return False
            return self.history(cli, client)
        elif command == "rm":
            if not ping_result:
                print("Server is unavailable.")
                return False
            return self.rm(cli, client)
        elif command == "ps":
            if not ping_result:
                print("Server is unavailable.")
                return False
            return self.ps(cli, client)
        elif command == "rename":
            if not ping_result:
                print("Server is unavailable.")
                return False
            return self.rename(cli, client)
        elif command == "describe":
            if not ping_result:
                print("Server is unavailable.")
                return False
            return self.describe(cli, client)
        elif command == "cp":
            if not ping_result:
                print("Server is unavailable.")
                return False
            return self.cp(cli, client)
        elif command == "enable":
            if not ping_result:
                print("Server is unavailable.")
                return False
            return self.enable(cli, client)
        elif command == "disable":
            if not ping_result:
                print("Server is unavailable.")
                return False
            return self.disable(cli, client)
        elif command == "cat":
            if not ping_result:
                print("Server is unavailable.")
                return False
            return self.cat(cli, client)
        elif command == "pause":
            if not ping_result:
                print("Server is unavailable.")
                return False
            return self.pause(cli, client)
        elif command == "resume":
            if not ping_result:
                print("Server is unavailable.")
                return False
            return self.resume(cli, client)
        elif command == "log":
            if not ping_result:
                print("Server is unavailable.")
                return False
            return self.log(cli, client)
        elif command == "trigger":
            if not ping_result:
                print("Server is unavailable.")
                return False
            return self.trigger(cli, client)
        elif command == "validate":
            if not ping_result:
                print("Server is unavailable.")
                return False
            return self.validate(cli, client)
        elif command == "test":
            return self.test(cli, client)
        else:
            invoke_cmd = sys.argv[0].split("/")[-1]
            print(invoke_cmd + " " + command + ": unknown command.")
            print("Run '" + invoke_cmd + " help' for usage.")
            return False
