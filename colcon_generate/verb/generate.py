# Copyright 2016-2018 Dirk Thomas
# Copyright 2025 Wind River Systems, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from colcon_core.package_selection import add_arguments \
    as add_packages_arguments
from colcon_core.plugin_system import satisfies_version
from colcon_core.verb import VerbExtensionPoint
from colcon_generate.subverb import get_subverb_extensions
from colcon_core.command import add_subparsers

class GenerateVerb(VerbExtensionPoint):
    """Generate buildsystem recipes"""

    def __init__(self):  # noqa: D107
        super().__init__()
        satisfies_version(VerbExtensionPoint.EXTENSION_POINT_VERSION, '^1.0')
        self._subparser = None

    def add_arguments(self, *, parser):  # noqa: D102
        # print usage if no subverb is given
        self.__subparser = parser

        # only added so that package selection arguments can be used
        # which use the build directory to store state information
        parser.add_argument(
            '--build-base',
            default='build',
            help='The base path for all build directories (default: build)')

        subverb_extensions = get_subverb_extensions()
        add_subparsers(parser, 'colcon generate', subverb_extensions,
                       attribute='subverb_name')

        add_packages_arguments(parser)

    def main(self, *, context):  # noqa: D102
        if context.args.subverb_name is None:
            self.__subparser.print_usage()
            return "Error: No subverb provided"
