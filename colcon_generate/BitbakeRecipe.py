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

class BitbakeRecipe:
    recipe_boilerplate = "\
# Recipe created by colcon-generate\n#\n\
# Copyright (c) 2025 Open Source Robotics Foundation, Inc.\
"

    def __init__(self, pkgname):
        self.name = pkgname.name
        self.version = pkgname.version

        self.summary = None
        self.description = pkgname.description
        self.homepage = pkgname.homepage

        self.section = None

        self.license = "&&".join(pkgname.upstream_license)
        self.lic_files_chksum = None

        self.src_uri = None
        self.srcrev = None

        # self.build_type

        pass

    def bitbake_recipe_filename(self):
        return f"{self.name}_{self.version}.bb"

    def get_recipe_text(self):
        lines = []
        lines.append(self.recipe_boilerplate)
        lines.append(f'SUMMARY = "{self.summary}"')
        lines.append(f'DESCRIPTION = "{self.description}"')
        lines.append(f'HOMEPAGE = "{self.homepage}"')
        lines.append("\n")
        lines.append(f'SECTION = "{self.section}"')
        lines.append(f'LICENSE = "{self.license}"')
        if self.lic_files_chksum:
            lines.append(f'LIC_FILES_CHKSUM = "{self.lic_files_chksum}"')
        lines.append("\n")

        if self.src_uri:
            lines.append(f'SRC_URI = "{self.src_uri}"')
        if self.srcrev:
            lines.append(f'SRCREV = "{self.srcrev}"')

        return "\n".join(lines) + "\n"
