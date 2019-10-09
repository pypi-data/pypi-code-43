

class ProjectNotFound(Exception):
    pass

class ProjectParserError(Exception):
    pass

class InvalidProject(Exception):
    pass


class ToolchainError(Exception):
    pass


class InvalidTarget(Exception):
    pass


class InstallError(Exception):
    pass


class SerialCannotOpenException(Exception):
    pass


class ReadElfError(Exception):
    pass


class CodeSyncError(Exception):
    pass



class BranchError(Exception):
    pass


class ProcessTimeout(Exception):
    pass