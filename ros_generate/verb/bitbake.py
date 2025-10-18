# Copyright 2016-2018 Dirk Thomas
# Copyright 2024 Open Source Robotics Foundation, Inc.
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

import logging

from colcon_core.logging import colcon_logger
from colcon_core.logging import get_effective_console_level
from colcon_core.package_selection import get_package_descriptors
from colcon_core.package_selection import select_package_decorators
from colcon_core.package_selection import add_arguments as add_packages_arguments
from colcon_core.plugin_system import satisfies_version
from colcon_core.topological_order import topological_order_packages
from colcon_core.verb import VerbExtensionPoint
from ros_generate.PackageMetadata import PackageMetadata
from ros_generate.BitbakeRecipe import BitbakeRecipe

import os

class BitbakeVerb(VerbExtensionPoint):
    """Generate Bitbake recipes for ROS 2 packages"""
    ros_package_manifest = 'package.xml'

    def __init__(self):  # noqa: D107
        super().__init__()
        satisfies_version(VerbExtensionPoint.EXTENSION_POINT_VERSION, '^1.0')
        log_level = get_effective_console_level(colcon_logger)
        logging.getLogger('git').setLevel(log_level)

    def add_arguments(self, *, parser):  # noqa: D102
        parser.add_argument(
            '--build-base',
            default='build_ros_generate',
            help='The base directory for build files '
                 '(default: build_ros_generate)')

        add_packages_arguments(parser)

    def main(self, *, context):  # noqa: D102
        args = context.args

        descriptors = get_package_descriptors(args)

        # always perform topological order for the select package extensions
        decorators = topological_order_packages(
            descriptors, recursive_categories=('run', ))

        select_package_decorators(args, decorators)

        lines = []
        for decorator in decorators:
            if not decorator.selected:
                continue
            pkg = decorator.descriptor

            lines.append(f"{pkg.name:<30}\t{str(pkg.path):<30}\t({pkg.type})")

            self.path = os.path.abspath(
                os.path.join(os.getcwd(), str(pkg.path)))

            self.build_base = os.path.abspath(os.path.join(
                os.getcwd(), args.build_base, pkg.name))

            package_manifest_path = os.path.join(pkg.path, self.ros_package_manifest)
            if os.path.exists(package_manifest_path):
                lines.append(f"\t- ROS package manifest: {package_manifest_path}")
                with open(package_manifest_path, 'r') as h:
                    package_manifest = h.read()
                    pkg_metadata = PackageMetadata(package_manifest, None)
                    bitbake_recipe = BitbakeRecipe(pkg_metadata)

                ros_bitbake_recipe = os.path.join(self.build_base, bitbake_recipe.bitbake_recipe_filename())
                lines.append(f"\t- Bitbake recipe: {ros_bitbake_recipe}")

                os.makedirs(self.build_base, exist_ok=True)

                with open(ros_bitbake_recipe, 'w') as h:
                    h.write(bitbake_recipe.get_recipe_text())
            else:
                lines.append(f"\t- No ROS package manifest found for {pkg.name}")
                continue

        for line in lines:
            print(line)
