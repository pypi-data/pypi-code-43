#   Copyright 2019 Intel, Inc.
#
#   Licensed under the Apache License, Version 2.0 (the "License"); you may
#   not use this file except in compliance with the License. You may obtain
#   a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#   License for the specific language governing permissions and limitations
#   under the License.
#

import json

from rsdclient.common import command


class GetResource(command.Command):
    """Show the details of one RSD resource."""

    _description = "Display the details of one RSD resource"

    def get_parser(self, prog_name):
        parser = super(GetResource, self).get_parser(prog_name)
        parser.add_argument(
            "resource", metavar="<resource>", help="ID of the RSD resource."
        )

        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)
        rsd_client = self.app.client_manager.rsd
        resource_detail = rsd_client.root.get(parsed_args.resource)
        print("{0}".format(json.dumps(resource_detail, indent=2)))


class DeleteResource(command.Command):
    """Delete a RSD resource."""

    _description = "Delete a RSD resource"

    def get_parser(self, prog_name):
        parser = super(DeleteResource, self).get_parser(prog_name)
        parser.add_argument(
            "resource",
            nargs="+",
            metavar="<resource>",
            help="ID of the RSD resource(s) to delete.",
        )

        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)
        rsd_client = self.app.client_manager.rsd
        for resource in parsed_args.resource:
            rsd_client.root.delete(resource)
            print("Resource {0} has been deleted.".format(resource))


class PatchResource(command.Command):
    """Issue HTTP PATCH to a target RSD resource."""

    _description = "Issue HTTP PATCH to a target RSD resource"

    def get_parser(self, prog_name):
        parser = super(PatchResource, self).get_parser(prog_name)
        parser.add_argument(
            "resource",
            metavar="<resource>",
            help="ID of target RSD resource to PATCH.",
        )
        parser.add_argument(
            "--data",
            dest="data",
            type=json.loads,
            metavar="<data>",
            help=("Payload of PATCH operation."),
        )

        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)
        rsd_client = self.app.client_manager.rsd
        rsd_client.root.patch(parsed_args.resource, parsed_args.data)
        print(
            "PATCH operation to resource {0} is done.".format(
                parsed_args.resource
            )
        )


class PostResource(command.Command):
    """Issue HTTP POST to a target RSD resource."""

    _description = "Issue HTTP POST to a target RSD resource"

    def get_parser(self, prog_name):
        parser = super(PostResource, self).get_parser(prog_name)
        parser.add_argument(
            "resource",
            metavar="<resource>",
            help="ID of target RSD resource to POST.",
        )
        parser.add_argument(
            "--data",
            dest="data",
            type=json.loads,
            metavar="<data>",
            help=("Payload of POST operation."),
        )

        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)
        rsd_client = self.app.client_manager.rsd
        rsd_client.root.post(parsed_args.resource, parsed_args.data)
        print(
            "POST operation to resource {0} is done.".format(
                parsed_args.resource
            )
        )
