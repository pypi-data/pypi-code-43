from platform import system


class Platform:

    WINDOWS = ["windows", "cygwin", "cygwin_nt-10.0"]
    UNIX = ["linux", "darwin"]

    @classmethod
    def get(cls):
        """
        Returns the current platform.
        """
        return system().lower()

    @classmethod
    def is_windows(cls):
        """
        Checks if the current platform is in our windows list.
        """

        return cls.get() in cls.WINDOWS

    @classmethod
    def is_unix(cls):
        """
        Checks if the current platform is in our unix list.
        """

        return cls.get() in cls.UNIX
