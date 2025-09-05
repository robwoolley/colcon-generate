from colcon_core.plugin_system import satisfies_version
from colcon_core.verb import VerbExtensionPoint

class GenerateVerb(VerbExtensionPoint):
    """Generate buildsystem recipes"""

    def __init__(self):  # noqa: D107
        super().__init__()
        satisfies_version(VerbExtensionPoint.EXTENSION_POINT_VERSION, '^1.0')

    def main(self, *, context):  # noqa: D102
        print("Colcon generate")

        return 0
