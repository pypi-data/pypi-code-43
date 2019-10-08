'''
    Copyright 2019 SerialLab, CORP

    This file is part of ListBasedFlavorPack.

    RandomFlavorpack is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    RandomFlavorpack is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with RandomFlavorpack.  If not, see <http://www.gnu.org/licenses/>.
'''
import coreapi, coreschema
from rest_framework.schemas import ManualSchema
from rest_framework.views import APIView
from rest_framework.response import Response
from list_based_flavorpack.models import ListBasedRegion
from list_based_flavorpack.utils import clone_list_based_pool



class CloneListBasedFlavorpackView(APIView):
    """
    Clones a list based flavorpack using the same logic as the
    internal management command.
    """
    queryset = ListBasedRegion.objects.none()

    schema = ManualSchema(fields=[
        coreapi.Field(
            "machine_name",
            required=True,
            location="path",
            schema=coreschema.String()
        ),
        coreapi.Field(
            "new_machine_name",
            required=True,
            location="path",
            schema=coreschema.String()
        ),
    ])

    def post(self, request, machine_name=None, new_machine_name=None):
        if machine_name and new_machine_name:
            clone_list_based_pool(machine_name, new_machine_name)
            return Response("The pool was copied.")
