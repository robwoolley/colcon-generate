# Copyright (c) 2024 Open Source Robotics Foundation, Inc.
# Copyright (c) 2025 Wind River Systems, Inc.
# Licensed under the Apache License, Version 2.0

import os
from typing import Any

from colcon_core.command \
    import LOG_LEVEL_ENVIRONMENT_VARIABLE \
    as COLCON_LOG_LEVEL_ENVIRONMENT_VARIABLE
from colcon_core.command import main as colcon_main
from colcon_core.environment_variable import EnvironmentVariable

from ros_generate.verb.bitbake import BitbakeVerb

"""Environment variable to set the log level"""
LOG_LEVEL_ENVIRONMENT_VARIABLE = EnvironmentVariable(
    'ROS_GENERATE_LOG_LEVEL',
    COLCON_LOG_LEVEL_ENVIRONMENT_VARIABLE.description)

"""Environment variable to set the configuration directory"""
HOME_ENVIRONMENT_VARIABLE = EnvironmentVariable(
    'ROS_GENERATE_HOME',
    'Set the configuration directory (default: ~/.ros_generate)')


def main(*args: str, **kwargs: str) -> Any:
    """Execute the main logic of the command."""

    colcon_kwargs = {
        'command_name': 'ros-generate',
        'verb_group_name': 'ros_generate.verb',
        'environment_variable_group_name':
            'ros_generate.environment_variable',
        'default_verb': BitbakeVerb,
        'default_log_base': os.devnull,
        **kwargs,
    }
    return colcon_main(*args, **colcon_kwargs)


