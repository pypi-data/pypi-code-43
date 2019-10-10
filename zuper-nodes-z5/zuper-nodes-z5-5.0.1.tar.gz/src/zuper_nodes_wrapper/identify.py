import argparse
import dataclasses
import json
import subprocess
import sys
from dataclasses import dataclass
from io import BytesIO, BufferedReader

import cbor2
import yaml

from zuper_nodes import InteractionProtocol
from zuper_nodes_wrapper.meta_protocol import BuildDescription, NodeDescription, ConfigDescription, ProtocolDescription
from contracts import indent
from zuper_json import read_cbor_or_json_objects
from zuper_json.ipce import ipce_to_object
from . import logger

def identify_main():
    usage = None
    parser = argparse.ArgumentParser(usage=usage)

    parser.add_argument('--image', default=None)

    parser.add_argument('--command', default=None)

    parsed = parser.parse_args()

    image = parsed.image
    if image is not None:
        ni: NodeInfo = identify_image2(image)
    elif parsed.command is not None:
        command = parsed.command.split()
        ni: NodeInfo = identify_command(command)
    else:
        msg = 'Please specify either --image or --command'
        logger.error(msg)
        sys.exit(1)

    print('\n\n')
    print(indent(describe_nd(ni.nd), '', 'desc: '))
    print('\n\n')
    print(indent(describe_bd(ni.bd), '', 'build: '))
    print('\n\n')
    print(indent(describe_cd(ni.cd), '', 'config: '))
    print('\n\n')
    print(indent(describe(ni.pd.data), '', 'data: '))
    print('\n\n')
    print(indent(describe(ni.pd.meta), '', 'meta: '))


def describe_nd(nd: NodeDescription):
    return str(nd.description)


def describe_bd(nd: BuildDescription):
    return str(nd)


def describe_cd(nd: ConfigDescription):
    s = []
    for f in dataclasses.fields(nd.config):
        # for k, v in nd.config.__annotations__.items():
        s.append('%20s: %s = %s' % (f.name, f.type, f.default))
    if not s:
        return 'No configuration switches available.'

    if hasattr(nd.config, '__doc__'):
        s.insert(0, nd.config.__doc__)
    return "\n".join(s)


def describe(ip: InteractionProtocol):
    s = "InteractionProtocol"

    s += '\n\n' + '* Description:'
    s += '\n\n' + indent(ip.description.strip(), '    ')

    s += '\n\n' + '* Inputs:'
    for name, type_ in ip.inputs.items():
        s += '\n  %25s: %s' % (name, type_)

    s += '\n\n' + '* Outputs:'
    for name, type_ in ip.outputs.items():
        s += '\n  %25s: %s' % (name, type_)

    s += '\n\n' + '* Language:'
    s += '\n\n' + ip.language

    return s


@dataclass
class NodeInfo:
    pd: ProtocolDescription
    nd: NodeDescription
    bd: BuildDescription
    cd: ConfigDescription


def identify_command(command) -> NodeInfo:
    d = [{'topic': 'wrapper.describe_protocol'},
         {'topic': 'wrapper.describe_config'},
         {'topic': 'wrapper.describe_node'},
         {'topic': 'wrapper.describe_build'}
         ]
    to_send = b''
    for p in d:
        p['compat'] = ['aido2']
        # to_send += (json.dumps(p) + '\n').encode('utf-8')
        to_send += cbor2.dumps(p)
    cp = subprocess.run(command, input=to_send, capture_output=True)
    s = cp.stderr.decode('utf-8')

    sys.stderr.write(indent(s.strip(), '|', ' stderr: |') + '\n\n')
    # noinspection PyTypeChecker
    f = BufferedReader(BytesIO(cp.stdout))
    stream = read_cbor_or_json_objects(f)

    res = stream.__next__()
    logger.debug(yaml.dump(res))
    pd: ProtocolDescription = ipce_to_object(res['data'], {}, {}, expect_type=ProtocolDescription)
    res = stream.__next__()
    logger.debug(yaml.dump(res))
    cd: ConfigDescription = ipce_to_object(res['data'], {}, {}, expect_type=ConfigDescription)
    res = stream.__next__()
    logger.debug(yaml.dump(res))
    nd: NodeDescription = ipce_to_object(res['data'], {}, {}, expect_type=NodeDescription)
    res = stream.__next__()
    logger.debug(yaml.dump(res))
    bd: BuildDescription = ipce_to_object(res['data'], {}, {}, expect_type=BuildDescription)
    logger.debug(yaml.dump(res))
    return NodeInfo(pd, nd, bd, cd)


def identify_image2(image) -> NodeInfo:
    cmd = ['docker', 'run', '--rm', '-i', image]
    return identify_command(cmd)

# def identify_image(image):
#     import docker
#     client = docker.from_env()
#
#
#     container: Container = client.containers.create(image, detach=True,   stdin_open=True)
#     print(container)
#     # time.sleep(4)
#     # attach to the container stdin socket
#     container.start()
#     # s  = container.exec_run()
#     s: SocketIO = container.attach_socket(params={'stdin': 1, 'stream': 1,  'stderr': 0, 'stdout': 0})
#     s_out: SocketIO = container.attach_socket(params={ 'stream': 1, 'stdout': 1, 'stderr': 0, 'stdin': 0})
#     s_stderr: SocketIO = container.attach_socket(params={'stream': 1, 'stdout': 0, 'stderr': 1, 'stdin': 0})
#     print(s.__dict__)
#     print(s_out.__dict__)
#     # send text
#     # s.write(j)
#     os.write(s._sock.fileno(), j)
#     os.close(s._sock.fileno())
#     s._sock.close()
#     # s.close()
#
#     f = os.fdopen(s_out._sock.fileno(), 'rb')
#     # there is some garbage: b'\x01\x00\x00\x00\x00\x00\x1e|{
#     f.read(8)
#
#     for x in read_cbor_or_json_objects(f):
#         print(x)
#     print(f.read(10))
#     # print(os.read(s_out._sock.fileno(), 100))
#
#     print(os.read(s_stderr._sock.fileno(), 100))
#     # close, stop and disconnect
#     s.close()
