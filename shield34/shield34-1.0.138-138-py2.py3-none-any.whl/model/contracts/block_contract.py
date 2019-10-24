from shield34_reporter.model.enums.block_type import BlockType


class BlockContract:

    id = ""
    blockType = BlockType.UNKNOWN
    blockName = ""
    blockClassName = ""
    version = 0
    suiteName = ""
    blockParams = ""
    externalParams = ""

    def __init__(self, block_type=BlockType.UNKNOWN, block_name="", block_class_name="", version=0, suite_name="", block_params="", external_params=""):
        self.blockType = block_type
        self.blockName = block_name
        self.blockClassName = block_class_name
        self.version = version
        self.suiteName = suite_name
        self.blockParams = block_params
        self.externalParams = external_params

    def reprJSON(self):
        return dict(id=self.id, blockType=self.blockType, blockName=self.blockName, blockClassName=self.blockClassName, version=self.version, suiteName=self.suiteName, blockParams=self.blockParams, externalParams=self.externalParams)
