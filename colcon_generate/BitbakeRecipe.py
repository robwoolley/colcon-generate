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

from colcon_generate.SPDXLicense import is_spdx_license, map_license

class BitbakeRecipe:
    recipe_boilerplate = "\
# Recipe created by colcon-generate\n\
#\n\
# Copyright (c) 2025 Open Source Robotics Foundation, Inc.\n\
"
    recipe_depends = "\
DEPENDS = \"${ROS_BUILD_DEPENDS} ${ROS_BUILDTOOL_DEPENDS}\"\n\
# Bitbake doesn\'t support the \"export\" concept, so build them as if we needed\n\
# them to build this package (even though we actually don\'t) so that they\'re\n\
# guaranteed to have been staged should this package appear in another\'s\n\
# DEPENDS.\n\
DEPENDS += \"${ROS_EXPORT_DEPENDS} ${ROS_BUILDTOOL_EXPORT_DEPENDS}\"\n\
\n\
RDEPENDS:${PN} += \"${ROS_EXEC_DEPENDS}\"\n\
"


    def __init__(self, pkg):
        self.name = pkg.name
        self.version = pkg.version

        self.summary = None
        self.description = pkg.description
        self.homepage = pkg.homepage

        self.section = None

        # license should be an SPDX identifier
        self.license = []
        for license_str in pkg.upstream_license:
            if (is_spdx_license(license_str)):
                self.license.append(license_str)
            else:
                spdx_license = map_license(license_str)
                if (len(spdx_license) > 0):
                    print("mapped {} to {}".format(license_str, spdx_license))
                    self.license.append(spdx_license)
                else:
                    self.license.append(license_str)

        self.lic_files_chksum = None

        self.src_uri = None
        self.srcrev = None

        self.build_type = pkg.build_type

        pass

    def bitbake_recipe_filename(self):
        return f"{self.name}_{self.version}.bb"

    @staticmethod
    def get_multiline_variable(name, value):
        indent = ' ' * 4
        lines = []
        lines.append(f'{name} = "\\')
        for line in value.splitlines():
            lines.append(f'{indent}{line.strip()}\\')
        lines.append('"')
        return "\n".join(lines)

    def get_recipe_text(self):

        # XXX For now, hardcode the ROS distro to Humble
        ROS_DISTRO = "humble"
        # XXX Get SRCREV from git repo HEAD
        # XXX Get branch from git repo

        lines = []
        lines.append(self.recipe_boilerplate)
        lines.append(f"inherit ros_distro_{ROS_DISTRO}")
        lines.append(f"inherit ros_component")
        lines.append("")

        if self.summary:
            lines.append(f'SUMMARY = "{self.summary}"')

        if '\n' in self.description:
            lines.append(self.get_multiline_variable('DESCRIPTION', self.description))
        else:
            lines.append(f'DESCRIPTION = "{self.description}"')

        # AUTHOR
        # ROS_AUTHOR
        lines.append(f'HOMEPAGE = "{self.homepage}"')
        if self.section:
            lines.append(f'SECTION = "{self.section}"')
        license_expression = " && ".join(self.license)
        lines.append(f'LICENSE = "{license_expression}"')
        if self.lic_files_chksum:
            lines.append(f'LIC_FILES_CHKSUM = "{self.lic_files_chksum}"')

        # ROS_CN
        # ROS_BPN

        # ROS_BUILD_DEPENDS
        # ROS_BUILDTOOL_DEPENDS
        # ROS_EXPORT_DEPENDS
        # ROS_BUILDTOOL_EXPORT_DEPENDS
        # ROS_EXEC_DEPENDS
        # ROS_TEST_DEPENDS

        lines.append(self.recipe_depends)

        lines.append(f'SRC_URI = "{self.src_uri}"')
        lines.append(f'SRCREV = "{self.srcrev}"')
        lines.append("")
        lines.append(f"ROS_BUILD_TYPE = \"{self.build_type}\"")
        lines.append("")
        lines.append("inherit ros_${ROS_BUILD_TYPE}")

        return "\n".join(lines) + "\n"
