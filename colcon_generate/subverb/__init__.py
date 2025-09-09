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

from colcon_core.plugin_system import instantiate_extensions
from colcon_core.plugin_system import order_extensions_by_name

class GenerateSubverbExtensionPoint:
    """Base class for colcon-generate sub-verb extensions."""

    def add_arguments(self, *, parser):
        """Add command line arguments specific to the sub-verb.

        This method is called during the argument parsing phase.

        :param parser: The argparse parser
        :type parser: argparse.ArgumentParser
        """
        pass

    def generate(self, *, metadata, args):
        """Generate files for a package.

        This method is called once for each package.

        :param metadata: The package metadata
        :type metadata: colcon_generate.PackageMetadata
        :param args: The parsed command line arguments
        :type args: argparse.Namespace
        """
        pass

def add_generate_subverb_arguments(parser):
    """Add command line arguments specific to the sub-verb.

    This method is called during the argument parsing phase.

    :param parser: The argparse parser
    :type parser: argparse.ArgumentParser
    """
    group = parser.add_argument_group(title="Generate subverb arguments")

    group.add_argument(
        '--ros-distro',
        default='.',
        help='The ROS 2 Distro to generate recipes for (default: rolling)')

def get_subverb_extensions():
    """
    Get the available subverb extensions.

    The extensions are ordered by their entry point name.

    :rtype: OrderedDict
    """
    extensions = instantiate_extensions(__name__)
    for name, extension in extensions.items():
        extension.SUBVERB_NAME = name
    return order_extensions_by_name(extensions)