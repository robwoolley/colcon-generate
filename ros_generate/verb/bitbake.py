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
from git import Repo, GitCommandError
from rosdistro import get_index, get_index_url, get_cached_distribution
from ros_generate.BitbakeRecipe import BitbakeRecipe
from ros_generate.PackageMetadata import PackageMetadata
from urllib.parse import urlparse

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
                 '(default: build_ros_generate)'
        )

        parser.add_argument(
            '--rosdistro',
            default=os.environ.get('ROSDISTRO'),
            help='Name of rosdistro'
        )

        add_packages_arguments(parser)


    def format_src_uri(self, uri):  # noqa: D102
        p = urlparse(uri)
        return f"git://{p.netloc}{p.path};${{ROS_BRANCH}};protocol={p.scheme}"

    def list_packages(self, distro_name):
        index_url = get_index_url()
        index = get_index(index_url)
        distro = get_cached_distribution(index, distro_name)

        if not distro:
            raise ValueError(f"Distro '{distro_name}' not found")

        versioned_packages = []
        unversioned_packages = []
        for pkg_name, pkg in distro.release_packages.items():
            repo = distro.repositories[pkg.repository_name]
            release_repo = repo.release_repository

            if release_repo is None:
                continue
            elif release_repo.version:
                versioned_packages.append(pkg_name)
            else:
                unversioned_packages.append(pkg_name)

        return versioned_packages, unversioned_packages

    def main(self, *, context):  # noqa: D102
        args = context.args

        (released_packages, _) = self.list_packages(args.rosdistro)

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

                bitbake_recipe = BitbakeRecipe()
                bitbake_recipe.set_rosdistro(args.rosdistro)
                bitbake_recipe.set_internal_packages(released_packages)
                bitbake_recipe.importPackage(pkg_metadata)
                bitbake_recipe.set_pkg_path(str(pkg.path))

                repo = None
                # Get source URI and revision
                try:
                    repo = Repo(pkg.path, search_parent_directories=True)
                except Exception as e:
                    repo = None
                    print(f"\t- Warning: Could not open git repository for package {pkg.name}: {e}")

                src_uri = None
                branch = None
                src_rev = None
                tag_name = None
                if repo is not None:
                    try:
                        # Use origin remote
                        src_uri = self.format_src_uri(repo.remotes.origin.url)
                    except Exception as e:
                        # Fallback to first remote
                        if repo.remotes:
                            src_uri = self.format_src_uri(repo.remotes[0].url)

                    try:
                        branch = repo.active_branch.name
                    except Exception as e:
                        branches = []
                        # Check local branches that contain the current commit
                        for head in repo.heads:
                            if repo.is_ancestor(repo.head.commit, head.commit):
                                branches.append(head.name)

                        # Check remote branches that contain the current commit
                        for remote in repo.remotes:
                            for ref in remote.refs:
                                if repo.is_ancestor(repo.head.commit, ref.commit):
                                    branches.append(ref.name)

                        # Remove duplicates
                        unique_branches = list(set(branches))

                        # Select branch based on rosdistro or common defaults
                        if len(unique_branches) > 0:
                            if f"origin/{args.rosdistro}" in unique_branches:
                                branch = args.rosdistro
                            elif "main" in unique_branches:
                                branch = "main"
                            elif "master" in unique_branches:
                                branch = "master"
                            else:
                                branch = unique_branches[0].removeprefix("origin/")

                        # print(f"\t- Found branches for package {pkg.name}: {unique_branches}, selected branch: {branch}")

                    # Get the current commit hash
                    src_rev = repo.head.commit.hexsha

                    repo_name = repo.working_tree_dir.split("/")[-1]

                    try:
                        tag_name = repo.git.describe('--tags', '--abbrev=0')
                    except GitCommandError:
                        tag_name = None

                    bitbake_recipe.set_git_metadata(src_uri, branch, src_rev, repo_name, tag_name)


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
