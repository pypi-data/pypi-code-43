#!/usr/bin/python

"""
This example creates a multi-controller network from semi-scratch by
using the net.add*() API and manually starting the switches and controllers.
"""

from mininet.clean import Cleanup  #
from mininet.net import Mininet
from mininet.node import RemoteController
from mininet.cli import CLI
from mininet.log import setLogLevel


ip = '192.168.56.10'


def single_domain():
    """ Create AmLight network for tests """

    net = Mininet(topo=None, build=False)

    # Add switches
    ampath1 = net.addSwitch('s1', listenPort=6601, dpid="0024389406000000")
    ampath2 = net.addSwitch('s2', listenPort=6602, dpid="002438af17000000")
    sol2 = net.addSwitch('s3', listenPort=6603, dpid="cc4e244b11000000")
    sjuan = net.addSwitch('s4', listenPort=6604, dpid="cc4e249e95000000")
    andes1 = net.addSwitch('s5', listenPort=6605, dpid="cc4e249126000000")
    andes2 = net.addSwitch('s6', listenPort=6606, dpid="cc4e249102000000")
    sax = net.addSwitch('s7', listenPort=6607, dpid="cc4e24967b000000")
    ampath3 = net.addSwitch('s8', listenPort=6608, dpid="00013417eb145c00")

    # Add links
    net.addLink(ampath1, ampath2, port1=289, port2=289)  # 7/1 to 7/1
    net.addLink(ampath1, sol2, port1=53, port2=52)  # 2/5 to 2/4
    net.addLink(ampath1, sax, port1=290, port2=97)  # 7/2 to 3/1
    net.addLink(ampath2, andes2, port1=53, port2=49)  # 2/5 to 2/1
    net.addLink(sol2, sax, port1=241, port2=98)  # 6/1 to 3/2
    net.addLink(sol2, andes1, port1=289, port2=97)  # 7/1 to 3/1
    net.addLink(andes1, andes2, port1=98, port2=98)  # 3/2 to 3/2
    net.addLink(andes2, sjuan, port1=97, port2=241)  # 3/1 to 6/1
    net.addLink(sjuan, ampath2, port1=193, port2=290)  # 5/1 to 7/2
    net.addLink(ampath1, ampath3, port1=242, port2=29)  # 6/2 to 1/29

    # Add hosts
    h1 = net.addHost('h1', mac='00:00:00:00:00:01')
    h2 = net.addHost('h2', mac='00:00:00:00:00:02')
    h3 = net.addHost('h3', mac='00:00:00:00:00:03')
    h4 = net.addHost('h4', mac='00:00:00:00:00:04')
    h5 = net.addHost('h5', mac='00:00:00:00:00:05')
    h6 = net.addHost('h6', mac='00:00:00:00:00:06')
    h7 = net.addHost('h7', mac='00:00:00:00:00:07')
    h8 = net.addHost('h8', mac='00:00:00:00:00:08')

    # Add links to switches
    net.addLink(h1, ampath1, port1=1, port2=1)
    net.addLink(h2, ampath2, port1=1, port2=1)
    net.addLink(h3, sol2, port1=1, port2=1)
    net.addLink(h4, sjuan, port1=1, port2=1)
    net.addLink(h5, andes1, port1=1, port2=1)
    net.addLink(h6, andes2, port1=1, port2=1)
    net.addLink(h7, sax, port1=1, port2=1)
    net.addLink(h8, ampath3, port1=1, port2=1)

    net.addController('ctrl', controller=RemoteController, ip=ip, port=6633)

    net.build()
    net.start()
    CLI(net)
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')  # for CLI output
    Cleanup.cleanup()
    single_domain()
