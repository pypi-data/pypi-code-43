#
# PySNMP MIB module IPV6-TC (http://snmplabs.com/pysmi)
# ASN.1 source http://mibs.snmplabs.com:80/asn1/IPV6-TC
# Produced by pysmi-0.3.1 at Thu Sep 20 16:37:34 2018
# On host kirill-HP-ProBook-450-G5 platform Linux version 4.15.0-34-generic by user kirill
# Using Python version 2.7.15rc1 (default, Apr 15 2018, 21:51:34) 
#
Integer, ObjectIdentifier, OctetString = mibBuilder.importSymbols("ASN1", "Integer", "ObjectIdentifier", "OctetString")
NamedValues, = mibBuilder.importSymbols("ASN1-ENUMERATION", "NamedValues")
ConstraintsUnion, SingleValueConstraint, ConstraintsIntersection, ValueSizeConstraint, ValueRangeConstraint = mibBuilder.importSymbols("ASN1-REFINEMENT", "ConstraintsUnion", "SingleValueConstraint", "ConstraintsIntersection", "ValueSizeConstraint", "ValueRangeConstraint")
NotificationGroup, ModuleCompliance = mibBuilder.importSymbols("SNMPv2-CONF", "NotificationGroup", "ModuleCompliance")
Integer32, MibScalar, MibTable, MibTableRow, MibTableColumn, NotificationType, MibIdentifier, IpAddress, TimeTicks, Counter64, Unsigned32, iso, Gauge32, ModuleIdentity, ObjectIdentity, Bits, Counter32 = mibBuilder.importSymbols("SNMPv2-SMI", "Integer32", "MibScalar", "MibTable", "MibTableRow", "MibTableColumn", "NotificationType", "MibIdentifier", "IpAddress", "TimeTicks", "Counter64", "Unsigned32", "iso", "Gauge32", "ModuleIdentity", "ObjectIdentity", "Bits", "Counter32")
DisplayString, TextualConvention = mibBuilder.importSymbols("SNMPv2-TC", "DisplayString", "TextualConvention")
class Ipv6Address(TextualConvention, OctetString):
    status = 'obsolete'
    displayHint = '2x:'
    subtypeSpec = OctetString.subtypeSpec + ValueSizeConstraint(16, 16)
    fixedLength = 16

class Ipv6AddressPrefix(TextualConvention, OctetString):
    status = 'obsolete'
    displayHint = '2x:'
    subtypeSpec = OctetString.subtypeSpec + ValueSizeConstraint(0, 16)

class Ipv6AddressIfIdentifier(TextualConvention, OctetString):
    status = 'obsolete'
    displayHint = '2x:'
    subtypeSpec = OctetString.subtypeSpec + ValueSizeConstraint(0, 8)

class Ipv6IfIndex(TextualConvention, Integer32):
    status = 'obsolete'
    displayHint = 'd'
    subtypeSpec = Integer32.subtypeSpec + ValueRangeConstraint(1, 2147483647)

class Ipv6IfIndexOrZero(TextualConvention, Integer32):
    status = 'obsolete'
    displayHint = 'd'
    subtypeSpec = Integer32.subtypeSpec + ValueRangeConstraint(0, 2147483647)

mibBuilder.exportSymbols("IPV6-TC", Ipv6Address=Ipv6Address, Ipv6AddressIfIdentifier=Ipv6AddressIfIdentifier, Ipv6AddressPrefix=Ipv6AddressPrefix, Ipv6IfIndexOrZero=Ipv6IfIndexOrZero, Ipv6IfIndex=Ipv6IfIndex)
