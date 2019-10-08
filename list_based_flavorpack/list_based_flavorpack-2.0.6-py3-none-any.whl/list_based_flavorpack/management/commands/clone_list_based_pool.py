# This program is free software: you can redistribute it and/| modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, |
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY | FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Copyright 2018 SerialLab Corp.  All rights reserved.
from django.core.management.base import BaseCommand
from django.utils.translation import gettext as _
from list_based_flavorpack.utils import clone_list_based_pool

class Command(BaseCommand):
    help = _('Clones a list-based pool by machine name')

    def add_arguments(self, parser):
        parser.add_argument('machine_name', type=str, help='The machine name of the pool to be cloned')
        parser.add_argument('new_machine_name', type=str, help='The new machine name of the pool to be cloned')
    
    def handle(self, *args, **options):
        print(_('Clones a list-based pool by machine name'))
        clone_list_based_pool(options['machine_name'], options['new_machine_name'])
