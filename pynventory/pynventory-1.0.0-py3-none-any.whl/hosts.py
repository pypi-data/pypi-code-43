from fabric import Connection


class LinuxHost:
    def __init__(self, host):
        self.connection = Connection(host, connect_timeout=1)
        self.host = host

    @staticmethod
    def display_name():
        return 'Host'

    def __str__(self):
        return self.host

    class GetOsRelease:
        def __init__(self, parent):
            output = parent.connection.run('cat /etc/issue', hide=True)
            if 'Server' in output.stdout:
                output = output.stdout.split('\n')[0]
            elif 'Server' not in output.stdout:
                output = parent.connection.run('cat /etc/redhat-release', hide=True).stdout
            else:
                output = 'Error getting release'

            # remove redundant output
            filter_list = ['Linux', 'release', '(Core)', '(Santiago)', '(Maipo)', 'Server', 'Enterprise']
            self.clean_output = []
            for word in output.split():
                if word not in filter_list:
                    self.clean_output.append(word)

        def __str__(self):
            return ' '.join(self.clean_output)

        @staticmethod
        def display_name():
            return 'OS Version'

    class GetHostname:
        def __init__(self, parent):
            self.output = parent.connection.run('hostname', hide=True).stdout

        @staticmethod
        def display_name():
            return 'Hostname'

        def __str__(self):
            return self.output.strip()

    class GetNtpServer:
        def __init__(self, parent):
            output = parent.connection.run('ntpq -pn', hide=True)
            # ntpq will output error if daemon is not running
            if output.stderr:
                self.output = [output.stderr.strip(), ]
            else:
                # remove header from ntpq output
                self.output = output.stdout.strip().split('\n')[2:]

        def __str__(self):
            # Filter out details and only return server ip
            servers = []
            for line in self.output:
                servers.append(line.split(' ')[0])
            return ', '.join(servers)

        @staticmethod
        def display_name():
            return 'NTP Server'

    class GetCpuCores:
        def __init__(self, parent):
            self.output = parent.connection.run('nproc', hide=True).stdout

        def __str__(self):
            return self.output.strip()

        @staticmethod
        def display_name():
            return 'Core count'

    class GetMemory:
        def __init__(self, parent):
            output = parent.connection.run('free -h', hide=True).stdout
            # Split output into lines, then split the columns and take total memory value
            self.memory = output.split('\n')[1].split()[1]

        def __str__(self):
            return self.memory

        @staticmethod
        def display_name():
            return 'Memory'

    class GetDiskSize:
        def __init__(self, parent):
            output = parent.connection.run('df -h -l --total', hide=True).stdout
            # Split output into lines, then split the columns and take disk size
            self.disk_size = output.split('\n')[-2].split()[1]

        def __str__(self):
            return self.disk_size

        @staticmethod
        def display_name():
            return 'Disk size'

    class GetKernelVersion:
        def __init__(self, parent):
            self.output = parent.connection.run('uname -r', hide=True).stdout

        def __str__(self):
            return self.output.strip()

        @staticmethod
        def display_name():
            return 'Kernel version'
