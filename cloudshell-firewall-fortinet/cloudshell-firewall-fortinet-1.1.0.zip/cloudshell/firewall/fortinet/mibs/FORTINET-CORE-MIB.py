#
# PySNMP MIB module FORTINET-CORE-MIB (http://snmplabs.com/pysmi)
# ASN.1 source http://mibs.snmplabs.com:80/asn1/FORTINET-CORE-MIB
# Produced by pysmi-0.3.1 at Thu Sep 20 16:37:34 2018
# On host kirill-HP-ProBook-450-G5 platform Linux version 4.15.0-34-generic by user kirill
# Using Python version 2.7.15rc1 (default, Apr 15 2018, 21:51:34) 
#
Integer, ObjectIdentifier, OctetString = mibBuilder.importSymbols("ASN1", "Integer", "ObjectIdentifier", "OctetString")
NamedValues, = mibBuilder.importSymbols("ASN1-ENUMERATION", "NamedValues")
ConstraintsUnion, SingleValueConstraint, ConstraintsIntersection, ValueSizeConstraint, ValueRangeConstraint = mibBuilder.importSymbols("ASN1-REFINEMENT", "ConstraintsUnion", "SingleValueConstraint", "ConstraintsIntersection", "ValueSizeConstraint", "ValueRangeConstraint")
ifIndex, = mibBuilder.importSymbols("IF-MIB", "ifIndex")
InetAddress, InetAddressPrefixLength, InetAddressType = mibBuilder.importSymbols("INET-ADDRESS-MIB", "InetAddress", "InetAddressPrefixLength", "InetAddressType")
NotificationGroup, ModuleCompliance, ObjectGroup = mibBuilder.importSymbols("SNMPv2-CONF", "NotificationGroup", "ModuleCompliance", "ObjectGroup")
sysName, = mibBuilder.importSymbols("SNMPv2-MIB", "sysName")
Integer32, MibScalar, MibTable, MibTableRow, MibTableColumn, NotificationType, MibIdentifier, IpAddress, TimeTicks, Counter64, Unsigned32, enterprises, ModuleIdentity, Gauge32, iso, ObjectIdentity, Bits, Counter32 = mibBuilder.importSymbols("SNMPv2-SMI", "Integer32", "MibScalar", "MibTable", "MibTableRow", "MibTableColumn", "NotificationType", "MibIdentifier", "IpAddress", "TimeTicks", "Counter64", "Unsigned32", "enterprises", "ModuleIdentity", "Gauge32", "iso", "ObjectIdentity", "Bits", "Counter32")
DisplayString, TextualConvention = mibBuilder.importSymbols("SNMPv2-TC", "DisplayString", "TextualConvention")
fortinet = ModuleIdentity((1, 3, 6, 1, 4, 1, 12356))
fortinet.setRevisions(('2015-01-14 00:00', '2014-12-10 00:00', '2014-04-10 00:00', '2014-03-22 00:00', '2012-05-09 00:00', '2012-04-23 00:00', '2011-12-23 00:00', '2011-04-25 00:00', '2010-05-14 00:00', '2009-05-20 00:00', '2008-11-19 00:00', '2008-10-21 00:00', '2008-06-25 00:00', '2008-06-16 00:00', '2008-04-17 00:00',))
if mibBuilder.loadTexts: fortinet.setLastUpdated('201501140000Z')
if mibBuilder.loadTexts: fortinet.setOrganization('Fortinet Technologies, Inc.')
class FnBoolState(TextualConvention, Integer32):
    status = 'current'
    subtypeSpec = Integer32.subtypeSpec + SingleValueConstraint(1, 2)
    namedValues = NamedValues(("disabled", 1), ("enabled", 2))

class FnLanguage(TextualConvention, Integer32):
    status = 'current'
    subtypeSpec = Integer32.subtypeSpec + SingleValueConstraint(1, 2, 3, 4, 5, 6, 7, 8, 255)
    namedValues = NamedValues(("english", 1), ("simplifiedChinese", 2), ("japanese", 3), ("korean", 4), ("spanish", 5), ("traditionalChinese", 6), ("french", 7), ("portuguese", 8), ("undefined", 255))

class FnIndex(TextualConvention, Integer32):
    status = 'current'
    displayHint = 'd'
    subtypeSpec = Integer32.subtypeSpec + ValueRangeConstraint(0, 2147483647)

class FnSessionProto(TextualConvention, Integer32):
    status = 'current'
    subtypeSpec = Integer32.subtypeSpec + SingleValueConstraint(0, 1, 2, 4, 6, 8, 12, 17, 22, 41, 46, 47, 50, 51, 89, 103, 108, 255)
    namedValues = NamedValues(("ip", 0), ("icmp", 1), ("igmp", 2), ("ipip", 4), ("tcp", 6), ("egp", 8), ("pup", 12), ("udp", 17), ("idp", 22), ("ipv6", 41), ("rsvp", 46), ("gre", 47), ("esp", 50), ("ah", 51), ("ospf", 89), ("pim", 103), ("comp", 108), ("raw", 255))

fnCoreMib = MibIdentifier((1, 3, 6, 1, 4, 1, 12356, 100))
fnCommon = MibIdentifier((1, 3, 6, 1, 4, 1, 12356, 100, 1))
fnSystem = MibIdentifier((1, 3, 6, 1, 4, 1, 12356, 100, 1, 1))
fnSysSerial = MibScalar((1, 3, 6, 1, 4, 1, 12356, 100, 1, 1, 1), DisplayString()).setMaxAccess("readonly")
if mibBuilder.loadTexts: fnSysSerial.setStatus('current')
fnMgmt = MibIdentifier((1, 3, 6, 1, 4, 1, 12356, 100, 1, 2))
fnMgmtLanguage = MibScalar((1, 3, 6, 1, 4, 1, 12356, 100, 1, 2, 1), FnLanguage()).setMaxAccess("readonly")
if mibBuilder.loadTexts: fnMgmtLanguage.setStatus('current')
fnAdmin = MibIdentifier((1, 3, 6, 1, 4, 1, 12356, 100, 1, 2, 100))
fnAdminNumber = MibScalar((1, 3, 6, 1, 4, 1, 12356, 100, 1, 2, 100, 1), Integer32()).setMaxAccess("readonly")
if mibBuilder.loadTexts: fnAdminNumber.setStatus('current')
fnAdminTable = MibTable((1, 3, 6, 1, 4, 1, 12356, 100, 1, 2, 100, 2), )
if mibBuilder.loadTexts: fnAdminTable.setStatus('current')
fnAdminEntry = MibTableRow((1, 3, 6, 1, 4, 1, 12356, 100, 1, 2, 100, 2, 1), ).setIndexNames((0, "FORTINET-CORE-MIB", "fnAdminIndex"))
if mibBuilder.loadTexts: fnAdminEntry.setStatus('current')
fnAdminIndex = MibTableColumn((1, 3, 6, 1, 4, 1, 12356, 100, 1, 2, 100, 2, 1, 1), Integer32().subtype(subtypeSpec=ValueRangeConstraint(1, 2147483647)))
if mibBuilder.loadTexts: fnAdminIndex.setStatus('current')
fnAdminName = MibTableColumn((1, 3, 6, 1, 4, 1, 12356, 100, 1, 2, 100, 2, 1, 2), DisplayString()).setMaxAccess("readonly")
if mibBuilder.loadTexts: fnAdminName.setStatus('current')
fnAdminAddrType = MibTableColumn((1, 3, 6, 1, 4, 1, 12356, 100, 1, 2, 100, 2, 1, 3), InetAddressType()).setMaxAccess("readonly")
if mibBuilder.loadTexts: fnAdminAddrType.setStatus('current')
fnAdminAddr = MibTableColumn((1, 3, 6, 1, 4, 1, 12356, 100, 1, 2, 100, 2, 1, 4), InetAddress()).setMaxAccess("readonly")
if mibBuilder.loadTexts: fnAdminAddr.setStatus('current')
fnAdminMask = MibTableColumn((1, 3, 6, 1, 4, 1, 12356, 100, 1, 2, 100, 2, 1, 5), InetAddressPrefixLength()).setMaxAccess("readonly")
if mibBuilder.loadTexts: fnAdminMask.setStatus('current')
fnTraps = MibIdentifier((1, 3, 6, 1, 4, 1, 12356, 100, 1, 3))
fnTrapsPrefix = MibIdentifier((1, 3, 6, 1, 4, 1, 12356, 100, 1, 3, 0))
fnTrapObjects = MibIdentifier((1, 3, 6, 1, 4, 1, 12356, 100, 1, 3, 1))
fnGenTrapMsg = MibScalar((1, 3, 6, 1, 4, 1, 12356, 100, 1, 3, 1, 1), DisplayString()).setMaxAccess("accessiblefornotify")
if mibBuilder.loadTexts: fnGenTrapMsg.setStatus('current')
fnTrapCpuThreshold = NotificationType((1, 3, 6, 1, 4, 1, 12356, 100, 1, 3, 0, 101)).setObjects(("FORTINET-CORE-MIB", "fnSysSerial"), ("SNMPv2-MIB", "sysName"))
if mibBuilder.loadTexts: fnTrapCpuThreshold.setStatus('current')
fnTrapMemThreshold = NotificationType((1, 3, 6, 1, 4, 1, 12356, 100, 1, 3, 0, 102)).setObjects(("FORTINET-CORE-MIB", "fnSysSerial"), ("SNMPv2-MIB", "sysName"))
if mibBuilder.loadTexts: fnTrapMemThreshold.setStatus('current')
fnTrapLogDiskThreshold = NotificationType((1, 3, 6, 1, 4, 1, 12356, 100, 1, 3, 0, 103)).setObjects(("FORTINET-CORE-MIB", "fnSysSerial"), ("SNMPv2-MIB", "sysName"))
if mibBuilder.loadTexts: fnTrapLogDiskThreshold.setStatus('current')
fnTrapTempHigh = NotificationType((1, 3, 6, 1, 4, 1, 12356, 100, 1, 3, 0, 104)).setObjects(("FORTINET-CORE-MIB", "fnSysSerial"), ("SNMPv2-MIB", "sysName"))
if mibBuilder.loadTexts: fnTrapTempHigh.setStatus('current')
fnTrapVoltageOutOfRange = NotificationType((1, 3, 6, 1, 4, 1, 12356, 100, 1, 3, 0, 105)).setObjects(("FORTINET-CORE-MIB", "fnSysSerial"), ("SNMPv2-MIB", "sysName"))
if mibBuilder.loadTexts: fnTrapVoltageOutOfRange.setStatus('current')
fnTrapPowerSupplyFailure = NotificationType((1, 3, 6, 1, 4, 1, 12356, 100, 1, 3, 0, 106)).setObjects(("FORTINET-CORE-MIB", "fnSysSerial"), ("SNMPv2-MIB", "sysName"))
if mibBuilder.loadTexts: fnTrapPowerSupplyFailure.setStatus('current')
fnTrapAmcIfBypassMode = NotificationType((1, 3, 6, 1, 4, 1, 12356, 100, 1, 3, 0, 107)).setObjects(("FORTINET-CORE-MIB", "fnSysSerial"), ("SNMPv2-MIB", "sysName"))
if mibBuilder.loadTexts: fnTrapAmcIfBypassMode.setStatus('current')
fnTrapFanFailure = NotificationType((1, 3, 6, 1, 4, 1, 12356, 100, 1, 3, 0, 108)).setObjects(("FORTINET-CORE-MIB", "fnSysSerial"), ("SNMPv2-MIB", "sysName"))
if mibBuilder.loadTexts: fnTrapFanFailure.setStatus('current')
fnTrapIpChange = NotificationType((1, 3, 6, 1, 4, 1, 12356, 100, 1, 3, 0, 201)).setObjects(("FORTINET-CORE-MIB", "fnSysSerial"), ("SNMPv2-MIB", "sysName"), ("IF-MIB", "ifIndex"))
if mibBuilder.loadTexts: fnTrapIpChange.setStatus('current')
fnTrapTest = NotificationType((1, 3, 6, 1, 4, 1, 12356, 100, 1, 3, 0, 999)).setObjects(("FORTINET-CORE-MIB", "fnSysSerial"), ("SNMPv2-MIB", "sysName"))
if mibBuilder.loadTexts: fnTrapTest.setStatus('current')
fnMIBConformance = MibIdentifier((1, 3, 6, 1, 4, 1, 12356, 100, 10))
fnSystemComplianceGroup = ObjectGroup((1, 3, 6, 1, 4, 1, 12356, 100, 10, 1)).setObjects(("FORTINET-CORE-MIB", "fnSysSerial"))
if getattr(mibBuilder, 'version', (0, 0, 0)) > (4, 4, 0):
    fnSystemComplianceGroup = fnSystemComplianceGroup.setStatus('current')
fnMgmtComplianceGroup = ObjectGroup((1, 3, 6, 1, 4, 1, 12356, 100, 10, 2)).setObjects(("FORTINET-CORE-MIB", "fnMgmtLanguage"))
if getattr(mibBuilder, 'version', (0, 0, 0)) > (4, 4, 0):
    fnMgmtComplianceGroup = fnMgmtComplianceGroup.setStatus('current')
fnAdminComplianceGroup = ObjectGroup((1, 3, 6, 1, 4, 1, 12356, 100, 10, 3)).setObjects(("FORTINET-CORE-MIB", "fnAdminNumber"), ("FORTINET-CORE-MIB", "fnAdminName"), ("FORTINET-CORE-MIB", "fnAdminAddrType"), ("FORTINET-CORE-MIB", "fnAdminAddr"), ("FORTINET-CORE-MIB", "fnAdminMask"))
if getattr(mibBuilder, 'version', (0, 0, 0)) > (4, 4, 0):
    fnAdminComplianceGroup = fnAdminComplianceGroup.setStatus('current')
fnTrapsComplianceGroup = NotificationGroup((1, 3, 6, 1, 4, 1, 12356, 100, 10, 4)).setObjects(("FORTINET-CORE-MIB", "fnTrapCpuThreshold"), ("FORTINET-CORE-MIB", "fnTrapMemThreshold"), ("FORTINET-CORE-MIB", "fnTrapLogDiskThreshold"), ("FORTINET-CORE-MIB", "fnTrapTempHigh"), ("FORTINET-CORE-MIB", "fnTrapVoltageOutOfRange"), ("FORTINET-CORE-MIB", "fnTrapPowerSupplyFailure"), ("FORTINET-CORE-MIB", "fnTrapAmcIfBypassMode"), ("FORTINET-CORE-MIB", "fnTrapFanFailure"), ("FORTINET-CORE-MIB", "fnTrapIpChange"), ("FORTINET-CORE-MIB", "fnTrapTest"))
if getattr(mibBuilder, 'version', (0, 0, 0)) > (4, 4, 0):
    fnTrapsComplianceGroup = fnTrapsComplianceGroup.setStatus('current')
fnNotifObjectsComplianceGroup = ObjectGroup((1, 3, 6, 1, 4, 1, 12356, 100, 10, 5)).setObjects(("FORTINET-CORE-MIB", "fnGenTrapMsg"))
if getattr(mibBuilder, 'version', (0, 0, 0)) > (4, 4, 0):
    fnNotifObjectsComplianceGroup = fnNotifObjectsComplianceGroup.setStatus('current')
fnMIBCompliance = ModuleCompliance((1, 3, 6, 1, 4, 1, 12356, 100, 10, 100)).setObjects(("FORTINET-CORE-MIB", "fnSystemComplianceGroup"), ("FORTINET-CORE-MIB", "fnMgmtComplianceGroup"), ("FORTINET-CORE-MIB", "fnAdminComplianceGroup"), ("FORTINET-CORE-MIB", "fnTrapsComplianceGroup"), ("FORTINET-CORE-MIB", "fnNotifObjectsComplianceGroup"))

if getattr(mibBuilder, 'version', (0, 0, 0)) > (4, 4, 0):
    fnMIBCompliance = fnMIBCompliance.setStatus('current')
mibBuilder.exportSymbols("FORTINET-CORE-MIB", fnSystemComplianceGroup=fnSystemComplianceGroup, fnTrapsComplianceGroup=fnTrapsComplianceGroup, fnTrapMemThreshold=fnTrapMemThreshold, FnSessionProto=FnSessionProto, fnTrapPowerSupplyFailure=fnTrapPowerSupplyFailure, fnAdminNumber=fnAdminNumber, fnTrapVoltageOutOfRange=fnTrapVoltageOutOfRange, fnTrapTempHigh=fnTrapTempHigh, fnAdminAddrType=fnAdminAddrType, PYSNMP_MODULE_ID=fortinet, fortinet=fortinet, fnNotifObjectsComplianceGroup=fnNotifObjectsComplianceGroup, FnLanguage=FnLanguage, fnTrapFanFailure=fnTrapFanFailure, fnAdminComplianceGroup=fnAdminComplianceGroup, fnMgmtComplianceGroup=fnMgmtComplianceGroup, fnAdminTable=fnAdminTable, fnTrapCpuThreshold=fnTrapCpuThreshold, FnIndex=FnIndex, fnTrapIpChange=fnTrapIpChange, fnTrapsPrefix=fnTrapsPrefix, fnGenTrapMsg=fnGenTrapMsg, fnMgmtLanguage=fnMgmtLanguage, fnCommon=fnCommon, fnTrapAmcIfBypassMode=fnTrapAmcIfBypassMode, fnAdminName=fnAdminName, fnSysSerial=fnSysSerial, fnSystem=fnSystem, fnTraps=fnTraps, fnCoreMib=fnCoreMib, fnAdminEntry=fnAdminEntry, fnAdmin=fnAdmin, fnTrapLogDiskThreshold=fnTrapLogDiskThreshold, fnAdminIndex=fnAdminIndex, fnTrapTest=fnTrapTest, fnAdminMask=fnAdminMask, fnTrapObjects=fnTrapObjects, fnMIBConformance=fnMIBConformance, fnMgmt=fnMgmt, fnAdminAddr=fnAdminAddr, FnBoolState=FnBoolState, fnMIBCompliance=fnMIBCompliance)
