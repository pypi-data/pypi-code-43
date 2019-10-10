from rox.server.flags.rox_flag import RoxFlag
from rox.server.flags.rox_variant import RoxVariant


class Container:
    instance = None

    def __init__(self):
        self.simple_flag = RoxFlag(True)
        self.simple_flag_overwritten = RoxFlag(True)

        self.flag_for_impression = RoxFlag(False)
        self.flag_for_impression_with_experiment_and_context = RoxFlag(False)

        self.flag_custom_properties = RoxFlag()

        self.flag_target_groups_all = RoxFlag()
        self.flag_target_groups_any = RoxFlag()
        self.flag_target_groups_none = RoxFlag()

        self.variant_with_context = RoxVariant('red', ['red', 'blue', 'green'])

        self.variant = RoxVariant('red', ['red', 'blue', 'green'])
        self.variant_overwritten = RoxVariant('red', ['red', 'blue', 'green'])

        self.flag_for_dependency = RoxFlag(False)
        self.flag_colors_for_dependency = RoxVariant('White', ['White', 'Blue', 'Green', 'Yellow'])
        self.flag_dependent = RoxFlag(False)
        self.flag_color_dependent_with_context = RoxVariant('White', ['White', 'Blue', 'Green', 'Yellow'])


Container.instance = Container()
