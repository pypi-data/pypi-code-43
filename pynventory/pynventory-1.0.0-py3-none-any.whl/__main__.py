import sys
import argparse
import ipaddress
import threading

from queue import Queue
from pynventory.hosts import LinuxHost


parser = argparse.ArgumentParser(description='Create a DokuWiki friendly inventory table of you servers',
                                 usage='python ServerMgnt/main.py  192.168.238.0/24 --hostname --cpu_cores --memory')
parser.add_argument('ip_range', action='store', help='CIDR IP range. ie: 192.168.0.0/24')
parser.add_argument('--cpu_cores', action='append_const', const=LinuxHost.GetCpuCores, dest='host_checks')
parser.add_argument('--hostname', action='append_const', const=LinuxHost.GetHostname, dest='host_checks')
parser.add_argument('--os_version', action='append_const', const=LinuxHost.GetOsRelease, dest='host_checks')
parser.add_argument('--ntp_host', action='append_const', const=LinuxHost.GetNtpServer, dest='host_checks')
parser.add_argument('--memory', action='append_const', const=LinuxHost.GetMemory, dest='host_checks')
parser.add_argument('--disk', action='append_const', const=LinuxHost.GetDiskSize, dest='host_checks')
parser.add_argument('--kernel', action='append_const', const=LinuxHost.GetKernelVersion, dest='host_checks')
parser.add_argument('-d', action='store_true', dest='debug', help='enable verbose output to stderr')
args = parser.parse_args()

# Defining globals
# Creating queue
compress_queue = Queue()
# Main result list.
result = []


def check_host(host):
    if not args.debug:
        print('.', end='', file=sys.stderr, flush=True)

    try:
        i = LinuxHost(host)
        host_result = [i, ]
        for check in args.host_checks:
            host_result.append(check(i))

        result.append(host_result)

    except Exception as e:
        empty_list = ['' for _ in range(len(args.host_checks))]
        result.append([host, ] + empty_list)
        if args.debug:
            print('Host: %s Error: %s' % (host, e), file=sys.stderr)
        return

    if args.debug:
        print('Host: %s Ok' % host, file=sys.stderr)

    return


def process_queue():
    while True:
        host_data = compress_queue.get()
        check_host(host_data)
        compress_queue.task_done()


def main():
    # Exit if no checks are given
    if not args.host_checks:
        parser.print_help()
        exit(1)

    # Starting threads
    threads = 10
    for _ in range(threads):
        t = threading.Thread(target=process_queue)
        t.daemon = True
        t.start()

    # Providing threads with work
    ip_range = list(ipaddress.ip_network(args.ip_range))
    # Ignore first and last address -> Network and Broadcast addresses
    for host in ip_range[1:-1]:
        compress_queue.put(str(host))

    # Wait for queue to finish
    compress_queue.join()

    # Force a clean line break before output
    print(file=sys.stderr)

    # Results from queues are not sorted.
    host_result = sorted(result[1:], key=lambda a: int(str(a[0]).split('.')[3]))

    header_title = ['Host', ] + [check.display_name() for check in args.host_checks]

    # Convert all the cells into strings
    cells = [[str(cell) for cell in row] for row in [header_title, ] + host_result]
    # Get longest entry for every column
    column_length = [max(map(len, col)) for col in zip(*cells)]

    # Create spacing for cells
    format_header = '^ {} ^'.format(' ^ '.join('{{:{}}}'.format(length) for length in column_length))
    format_body = '| {} |'.format(' | '.join('{{:{}}}'.format(length) for length in column_length))

    # Print output...
    print(format_header.format(*header_title))

    for row in cells[1:]:
        print(format_body.format(*row))


if __name__ == '__main__':
    main()
