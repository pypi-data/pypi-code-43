from janis_bioinformatics.tools.pappenfuss.gridss.base_2_2 import GridssBase_2_2
from janis_bioinformatics.tools.pappenfuss.gridss.base_2_4 import GridssBase_2_4


class Gridss_2_2_3(GridssBase_2_2):

    @staticmethod
    def base_command():
        return [
            *super(Gridss_2_2_3, Gridss_2_2_3).base_command(),
            "/data/gridss/gridss-2.2.3-gridss-jar-with-dependencies.jar",
            "gridss.CallVariants"
        ]

    @staticmethod
    def container():
        return "gridss/gridss:v2.2.3"

    @staticmethod
    def version():
        return "v2.2.3"


class Gridss_2_4_0(GridssBase_2_2):

    @staticmethod
    def base_command():
        return [
            *super(Gridss_2_4_0, Gridss_2_4_0).base_command(),
            "/data/gridss/gridss-2.4.0-gridss-jar-with-dependencies.jar",
            "gridss.CallVariants"
        ]

    @staticmethod
    def container():
        return "gridss/gridss:2.4.0"

    @staticmethod
    def version():
        return "v2.4.0"


class Gridss_2_5_1(GridssBase_2_4):

    @staticmethod
    def base_command():
        return "gridss.sh"

    @staticmethod
    def container():
        return "michaelfranklin/gridss:2.5.1-dev2"

    @staticmethod
    def version():
        return "v2.5.1-dev"


GridssLatest = Gridss_2_5_1
