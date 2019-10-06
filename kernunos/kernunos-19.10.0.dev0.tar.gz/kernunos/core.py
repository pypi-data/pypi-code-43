class Core():
    """
    This is where it all starts. All other modules are instanced from this one.
    """
    def __init__(self, target):
        """
        :param target: (str) a domain to target
        """
        self.target = target

    def show_help(self):
        print("""
        cernunnos
        Arguments:
        -t\t --target\t The domain name of your target.

        Examples:
        python -m cernunnos --target example.com
        """)

    def show_banner(self):
        print('###############################')
        print('#     Welcome to Cernunnos    #')
        print('###############################')
        print('--')