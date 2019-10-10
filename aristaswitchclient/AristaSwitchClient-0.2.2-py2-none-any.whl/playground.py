from __future__ import unicode_literals

from Switch import Switch
from collections import OrderedDict
import ipaddress


s = Switch(ip_address="10.20.30.26", username="cvpadmin", password="nynjlab")

import json

s.get_facts()

print(s)

#Leaf config
role = "primary"
mlag_domain_id = "MLAG_DOMAIN"
ibgp_vrfs_to_vlans = {65000: ["172.16.200.0", "172.16.200.2"]}

asn = 65001

mlag_configlet = s.build_mlag(role, mlag_domain_id=mlag_domain_id,
                                            number_of_interfaces=2, interfaces=None, port_channel=2000,
                                            vlan=4094, trunk_group_name="MLAG_Trunk_Group", ibgp=True,
                                            ibgp_vrfs_to_vlans=ibgp_vrfs_to_vlans, asn=asn)

ip_interface_config = s.build_ip_interface_underlay(interfaces_to_ips={"Ethernet1":"172.17.200.1/31", "Ethernet2":"172.17.200.3/31", "Ethernet3":"172.17.200.5/31"})

bgp_underlay_config = s.build_bgp_underlay(65001, "leaf", "172.16.0.4/32", OrderedDict({65000:["172.16.200.0", "172.16.200.2", "172.16.200.3"]}))

vxlan_data_plane_config = s.build_vxlan_data_plane({10:10010, 20:10020, 100:10100}, "1.1.1.1/32")


vtep_peers = ["172.16.0.5", "172.16.0.6"]
cvx_address = "192.168.0.1"
evpn_peers = {65000: ["172.16.0.1", "172.16.0.2", "172.16.0.3"]}
asn = 65001
svi_to_address = {12:"172.16.112.1/24", 13:"172.16.113.1/24", 14:"172.16.114.1/24"}
mac_vrf_rd = "1.1.1.1"
vrf_rd = "1.1.1.1"

vxlan_control_plane_config = s.build_vxlan_control_plane("evpn", vtep_peers=vtep_peers, cvx_address=cvx_address,
                                                        evpn_peers=evpn_peers, asn=asn, role="leaf", evpn_model="symmetric", svi_to_address=svi_to_address,
                                                        mac_vrf_route_distinguisher=mac_vrf_rd, vrf_route_distinguisher=vrf_rd
                                                        )
print("*")*50
print("* MLAG Configlet")
print("*")*50
print(mlag_config)

print("*")*50
print("* IP Interface Configlet")
print("*")*50
print(ip_interface_config)

print("*")*50
print("* BGP Underlay Configlet")
print("*")*50
print(bgp_underlay_config)

print("*")*50
print("* Vxlan Data Plane Configlet")
print("*")*50
print(vxlan_data_plane_config)

print("*")*50
print("* Vxlan Control Plane Configlet")
print("*")*50
print(vxlan_control_plane_config)

print("*")*50

#Spine config
# ip_interface_config = s.build_ip_interface_underlay(interfaces_to_ips={"ethernet1":"172.17.200.0", "ethernet2":"172.17.200.2"})
# bgp_underlay_config = s.build_bgp_underlay(65000, "spine", "172.16.0.1", {65001:["172.16.200.3"], 65002:["172.16.200.4"]})

# evpn_peers = {65001: ["172.16.0.3"], 65002:["172.16.0.4"], 65003:["172.16.0.5"]}
# asn = 65000

# vxlan_control_plane_config = s.build_vxlan_control_plane("evpn", evpn_peers=evpn_peers, asn=asn)


# print(json.dumps(ordered_interface_speeds, indent=2))