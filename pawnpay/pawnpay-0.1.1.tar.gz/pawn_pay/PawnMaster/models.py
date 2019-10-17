# coding: utf-8

#  Copyright (c) 2019 | Advancing Technology Systems, LLC
#  See LICENSE for any grants of usage, distribution, or modification

from sqlalchemy import CHAR, Column, DateTime, Float, ForeignKey, Index, Integer, SmallInteger, String, text, and_
from sqlalchemy import case
from sqlalchemy.dialects.mssql import BIT, MONEY, SMALLDATETIME, TINYINT, UNIQUEIDENTIFIER
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from sqlalchemy.orm import relationship, joinedload, Load, foreign

Base = declarative_base()
metadata = Base.metadata


class SysInfo1(Base):
    __tablename__ = "SysInfo1"

    STO_PK = Column("STO_PK", SmallInteger, primary_key=True, nullable=False, unique=True)
    MINCHG = Column("MINCHG", MONEY, nullable=False, server_default=text("(0)"))
    LOGON = Column("LOGON", BIT, nullable=False, server_default=text("(0)"))
    USEPASS = Column("USEPASS", BIT, nullable=False, server_default=text("(0)"))
    PERIOD = Column("PERIOD", SmallInteger, nullable=False, server_default=text("(0)"))
    PAWNDAYS = Column("PAWNDAYS", SmallInteger, nullable=False, server_default=text("(0)"))
    OPTIONDAYS = Column("OPTIONDAYS", SmallInteger, nullable=False, server_default=text("(0)"))
    GRACEDAYS = Column("GRACEDAYS", SmallInteger, nullable=False, server_default=text("(0)"))
    BUYHOLDDAY = Column("BUYHOLDDAY", SmallInteger, nullable=False, server_default=text("(0)"))
    CNTWEEKEND = Column("CNTWEEKEND", BIT, nullable=False, server_default=text("(0)"))
    POLTICPICK = Column("POLTICPICK", BIT, nullable=False, server_default=text("(0)"))
    POLTICMAIL = Column("POLTICMAIL", BIT, nullable=False, server_default=text("(0)"))
    SAMPAWNPOL = Column("SAMPAWNPOL", BIT, nullable=False, server_default=text("(0)"))
    SAMPAWNPUR = Column("SAMPAWNPUR", BIT, nullable=False, server_default=text("(0)"))
    NUMPOLTIC = Column("NUMPOLTIC", SmallInteger, nullable=False, server_default=text("(0)"))
    REPRNTTICK = Column("REPRNTTICK", BIT, nullable=False, server_default=text("(0)"))
    REPRNTPOL = Column("REPRNTPOL", BIT, nullable=False, server_default=text("(0)"))
    PRINTATF = Column("PRINTATF", BIT, nullable=False, server_default=text("(0)"))
    GUNLOG = Column("GUNLOG", BIT, nullable=False, server_default=text("(0)"))
    FEDGUNNUM = Column(
        "FEDGUNNUM", String(25, "SQL_Latin1_General_CP1_CI_AS"), nullable=False, server_default=text("('')")
    )
    BACKPAYMNT = Column("BACKPAYMNT", BIT, nullable=False, server_default=text("(0)"))
    EXTENDDATE = Column("EXTENDDATE", BIT, nullable=False, server_default=text("(0)"))
    PRICTAGPAW = Column("PRICTAGPAW", BIT, nullable=False, server_default=text("(0)"))
    PRICTAGPUL = Column("PRICTAGPUL", BIT, nullable=False, server_default=text("(0)"))
    RESPRICEPAWN = Column("RESPRICEPAWN", BIT, nullable=False, server_default=text("(0)"))
    PRNSALEREC = Column("PRNSALEREC", BIT, nullable=False, server_default=text("(0)"))
    COMPNDINT = Column("COMPNDINT", BIT, nullable=False, server_default=text("(0)"))
    EMPSLPRCNT = Column("EMPSLPRCNT", Float(53), nullable=False, server_default=text("(0)"))
    SERIALNUM = Column(
        "SERIALNUM", String(12, "SQL_Latin1_General_CP1_CI_AS"), nullable=False, server_default=text("('')")
    )
    NAME = Column("NAME", String(35, "SQL_Latin1_General_CP1_CI_AS"), nullable=False, server_default=text("('')"))
    ADDRESS1 = Column(
        "ADDRESS1", String(30, "SQL_Latin1_General_CP1_CI_AS"), nullable=False, server_default=text("('')")
    )
    ADDRESS2 = Column(
        "ADDRESS2", String(30, "SQL_Latin1_General_CP1_CI_AS"), nullable=False, server_default=text("('')")
    )
    CITY = Column("CITY", String(20, "SQL_Latin1_General_CP1_CI_AS"), nullable=False, server_default=text("('')"))
    STATE = Column("STATE", String(2, "SQL_Latin1_General_CP1_CI_AS"), nullable=False, server_default=text("('')"))
    ZIP = Column("ZIP", String(10, "SQL_Latin1_General_CP1_CI_AS"), nullable=False, server_default=text("('')"))
    PHONE = Column("PHONE", String(14, "SQL_Latin1_General_CP1_CI_AS"), nullable=False, server_default=text("('')"))
    STTAXRATE = Column("STTAXRATE", MONEY, nullable=False, server_default=text("(0)"))
    CTTAXRATE = Column("CTTAXRATE", MONEY, nullable=False, server_default=text("(0)"))
    LCTAXRATE = Column("LCTAXRATE", MONEY, nullable=False, server_default=text("(0)"))
    PARTPAY = Column("PARTPAY", BIT, nullable=False, server_default=text("(0)"))
    PARTEXTDAT = Column("PARTEXTDAT", BIT, nullable=False, server_default=text("(0)"))
    FUTUREPAY = Column("FUTUREPAY", BIT, nullable=False, server_default=text("(0)"))
    LAYAWAYDAY = Column("LAYAWAYDAY", SmallInteger, nullable=False, server_default=text("(0)"))
    LAYAWAYPCT = Column("LAYAWAYPCT", Float(53), nullable=False, server_default=text("(0)"))
    BACKUPDATE = Column("BACKUPDATE", SMALLDATETIME)
    MINAGE = Column("MINAGE", SmallInteger, nullable=False, server_default=text("(0)"))
    LATECHRG = Column("LATECHRG", BIT, nullable=False, server_default=text("(0)"))
    LASTUSE = Column("LASTUSE", SMALLDATETIME)
    POLICENUMS = Column("POLICENUMS", BIT, nullable=False, server_default=text("(0)"))
    MTOU = Column("MTOU", BIT, nullable=False, server_default=text("(0)"))
    V1 = Column("V1", Integer, nullable=False, server_default=text("(0)"))
    V2 = Column("V2", Integer, nullable=False, server_default=text("(0)"))
    V3 = Column("V3", Integer, nullable=False, server_default=text("(0)"))
    V4 = Column("V4", Integer, nullable=False, server_default=text("(0)"))
    V5 = Column("V5", Integer, nullable=False, server_default=text("(0)"))
    V6 = Column("V6", Integer, nullable=False, server_default=text("(0)"))
    NSAOTS = Column("NSAOTS", String(8, "SQL_Latin1_General_CP1_CI_AS"), nullable=False, server_default=text("('')"))
    CASHDRAWER = Column("CASHDRAWER", BIT, nullable=False, server_default=text("(0)"))
    TAXCOLFEE1 = Column("TAXCOLFEE1", MONEY, nullable=False, server_default=text("(0.0)"))
    TAXCOLAMT = Column("TAXCOLAMT", MONEY, nullable=False, server_default=text("(0.0)"))
    TAXCOLFEE2 = Column("TAXCOLFEE2", MONEY, nullable=False, server_default=text("(0.0)"))
    ENTPAWNDAT = Column("ENTPAWNDAT", BIT, nullable=False, server_default=text("(0)"))
    PASSCLOS = Column(
        "PASSCLOS", String(1, "SQL_Latin1_General_CP1_CI_AS"), nullable=False, server_default=text("('')")
    )
    MODINVQTY = Column("MODINVQTY", BIT, nullable=False, server_default=text("(0)"))
    PRINLOWER = Column("PRINLOWER", BIT, nullable=False, server_default=text("(0)"))
    LAYLABEL = Column("LAYLABEL", BIT, nullable=False, server_default=text("(0)"))
    LOSTTIKCHG = Column("LOSTTIKCHG", BIT, nullable=False, server_default=text("(0)"))
    LOSTTIKAMT = Column("LOSTTIKAMT", MONEY, nullable=False, server_default=text("(0.00)"))
    BACKDRIVE = Column(
        "BACKDRIVE", String(1, "SQL_Latin1_General_CP1_CI_AS"), nullable=False, server_default=text("('')")
    )
    CTTAXCOL1 = Column("CTTAXCOL1", Float(53), nullable=False, server_default=text("(0)"))
    CTTAXCOLAT = Column("CTTAXCOLAT", Float(53), nullable=False, server_default=text("(0)"))
    CTTAXCOL2 = Column("CTTAXCOL2", Float(53), nullable=False, server_default=text("(0)"))
    LCTAXCOL1 = Column("LCTAXCOL1", Float(53), nullable=False, server_default=text("(0)"))
    LCTAXCOLAT = Column("LCTAXCOLAT", Float(53), nullable=False, server_default=text("(0)"))
    LCTAXCOL2 = Column("LCTAXCOL2", Float(53), nullable=False, server_default=text("(0)"))
    DIFMONFEE = Column("DIFMONFEE", BIT, nullable=False, server_default=text("(0)"))
    DIFPOLITMS = Column("DIFPOLITMS", BIT, nullable=False, server_default=text("(0)"))
    REPURCHTAX = Column("REPURCHTAX", BIT, nullable=False, server_default=text("(0)"))
    DIFPWPLTIK = Column("DIFPWPLTIK", BIT, nullable=False, server_default=text("(0)"))
    STARTPOL = Column("STARTPOL", Integer, nullable=False, server_default=text("(0)"))
    CANSWNPM = Column("CANSWNPM", CHAR(1, "SQL_Latin1_General_CP1_CI_AS"), nullable=False, server_default=text("(0)"))
    CANSW = Column("CANSW", CHAR(8, "SQL_Latin1_General_CP1_CI_AS"), nullable=False, server_default=text("('')"))
    PAWNRECPT = Column("PAWNRECPT", BIT, nullable=False, server_default=text("(0)"))
    EXTENDLAY = Column("EXTENDLAY", SmallInteger, nullable=False, server_default=text("(1)"))
    ENCODECOST = Column(
        "ENCODECOST", String(11, "SQL_Latin1_General_CP1_CI_AS"), nullable=False, server_default=text("('')")
    )
    EXTBAKREST = Column("EXTBAKREST", BIT, nullable=False, server_default=text("(0)"))
    EXTRESTREB = Column("EXTRESTREB", BIT, nullable=False, server_default=text("(0)"))
    StorageFee = Column("StorageFee", MONEY, nullable=False, server_default=text("(0)"))
    BLANKLABEL = Column("BLANKLABEL", BIT, nullable=False, server_default=text("(0)"))
    PAWNOPTION = Column("PAWNOPTION", TINYINT, nullable=False, server_default=text("(1)"))
    NEWCUSTLBL = Column("NEWCUSTLBL", BIT, nullable=False, server_default=text("(0)"))
    NONINVCOST = Column("NONINVCOST", BIT, nullable=False, server_default=text("(0)"))
    BCODEINV = Column("BCODEINV", BIT, nullable=False, server_default=text("(0)"))
    BCODERNG = Column("BCODERNG", BIT, nullable=False, server_default=text("(0)"))
    BCODEPWN = Column("BCODEPWN", BIT, nullable=False, server_default=text("(0)"))
    BCODECST = Column("BCODECST", BIT, nullable=False, server_default=text("(0)"))
    BCODEITM = Column("BCODEITM", BIT, nullable=False, server_default=text("(0)"))
    BCODELTG = Column("BCODELTG", BIT, nullable=False, server_default=text("(0)"))
    BCODELTK = Column("BCODELTK", BIT, nullable=False, server_default=text("(0)"))
    BCODERTG = Column("BCODERTG", BIT, nullable=False, server_default=text("(0)"))
    BCODERTK = Column("BCODERTK", BIT, nullable=False, server_default=text("(0)"))
    BCODERTK = Column("BCODERTK", BIT, nullable=False, server_default=text("(0)"))
    POLICEDEPT = Column(
        "POLICEDEPT", String(50, "SQL_Latin1_General_CP1_CI_AS"), nullable=False, server_default=text("('')")
    )
    POLICEANUM = Column(
        "POLICEANUM", String(25, "SQL_Latin1_General_CP1_CI_AS"), nullable=False, server_default=text("('')")
    )
    ASKSALEREC = Column("ASKSALEREC", BIT, nullable=False, server_default=text("(0)"))
    GUNAMT = Column("GUNAMT", MONEY, nullable=False, server_default=text("(0.00)"))
    ALLGUNSAMT = Column("ALLGUNSAMT", BIT, nullable=False, server_default=text("(0)"))
    GLHGUNACCT = Column("GLHGUNACCT", Integer, nullable=False, server_default=text("(0)"))
    GUNINTEXIT = Column("GUNINTEXIT", BIT, nullable=False, server_default=text("(0)"))
    BACKCKEXIT = Column("BACKCKEXIT", BIT, nullable=False, server_default=text("(0)"))
    OVERGUNSAL = Column("OVERGUNSAL", BIT, nullable=False, server_default=text("(0)"))
    THERMALLBL = Column("THERMALLBL", BIT, nullable=False, server_default=text("(0)"))
    ONLYCREDIT = Column("ONLYCREDIT", BIT, nullable=False, server_default=text("(0)"))
    CANADATAXS = Column("CANADATAXS", BIT, nullable=False, server_default=text("(0)"))
    CASHCRDPAS = Column(
        "CASHCRDPAS", String(2, "SQL_Latin1_General_CP1_CI_AS"), nullable=False, server_default=text("('')")
    )
    GLPRTCHECK = Column("GLPRTCHECK", BIT, nullable=False, server_default=text("(0)"))
    FEDEXEMPT = Column("FEDEXEMPT", Float(53), nullable=False, server_default=text("(0)"))
    IDNUMBERS = Column(
        "IDNUMBERS", String(40, "SQL_Latin1_General_CP1_CI_AS"), nullable=False, server_default=text("('')")
    )
    PRINTCHECK = Column("PRINTCHECK", BIT, nullable=False, server_default=text("(0)"))
    BENFTEXMPT = Column(
        "BENFTEXMPT", String(2, "SQL_Latin1_General_CP1_CI_AS"), nullable=False, server_default=text("('')")
    )
    GLBENFTACT = Column("GLBENFTACT", Integer, nullable=False, server_default=text("(0)"))
    GLEICACCT = Column("GLEICACCT", Integer, nullable=False, server_default=text("(0)"))
    PAYCHEKQTR = Column("PAYCHEKQTR", Float(53), nullable=False, server_default=text("(0)"))
    YEARPRINT = Column("YEARPRINT", BIT, nullable=False, server_default=text("(0)"))
    RECONCLPAY = Column("RECONCLPAY", BIT, nullable=False, server_default=text("(0)"))
    PWBYCHECKS = Column(
        "PWBYCHECKS", String(12, "SQL_Latin1_General_CP1_CI_AS"), nullable=False, server_default=text("('')")
    )
    MEMODAYCHG = Column(
        "MEMODAYCHG", String(4, "SQL_Latin1_General_CP1_CI_AS"), nullable=False, server_default=text("('')")
    )
    MEMOREBATE = Column(
        "MEMOREBATE", String(18, "SQL_Latin1_General_CP1_CI_AS"), nullable=False, server_default=text("('')")
    )
    LCNSBACK = Column("LCNSBACK", Float(53), nullable=False, server_default=text("(0)"))
    POLLSTUPTO = Column(
        "POLLSTUPTO", String(24, "SQL_Latin1_General_CP1_CI_AS"), nullable=False, server_default=text("('')")
    )
    DLSCAN = Column("DLSCAN", String(17, "SQL_Latin1_General_CP1_CI_AS"), nullable=False, server_default=text("('')"))
    DATACOLECT = Column(
        "DATACOLECT", String(17, "SQL_Latin1_General_CP1_CI_AS"), nullable=False, server_default=text("('')")
    )
    PROREPSTRT = Column("PROREPSTRT", Integer, nullable=False, server_default=text("(0)"))
    CREDITSALE = Column(
        "CREDITSALE", String(9, "SQL_Latin1_General_CP1_CI_AS"), nullable=False, server_default=text("('')")
    )
    CRDSALACCT = Column("CRDSALACCT", Integer, nullable=False, server_default=text("(0)"))
    CREDSALMSG = Column(
        "CREDSALMSG", String(80, "SQL_Latin1_General_CP1_CI_AS"), nullable=False, server_default=text("('')")
    )
    CRDEXPACCT = Column("CRDEXPACCT", Integer, nullable=False, server_default=text("(0)"))
    CRDSVCACCT = Column("CRDSVCACCT", Integer, nullable=False, server_default=text("(0)"))
    CHECKADVNC = Column(
        "CHECKADVNC", String(17, "SQL_Latin1_General_CP1_CI_AS"), nullable=False, server_default=text("('')")
    )
    TITLEPAWN = Column(
        "TITLEPAWN", String(17, "SQL_Latin1_General_CP1_CI_AS"), nullable=False, server_default=text("('')")
    )
    CKADVGLACT = Column(
        "CKADVGLACT", String(24, "SQL_Latin1_General_CP1_CI_AS"), nullable=False, server_default=text("('')")
    )
    TITLPRTDEV = Column(
        "TITLPRTDEV", String(12, "SQL_Latin1_General_CP1_CI_AS"), nullable=False, server_default=text("('')")
    )
    NOUTAOTS = Column(
        "NOUTAOTS", String(10, "SQL_Latin1_General_CP1_CI_AS"), nullable=False, server_default=text("('')")
    )
    LATEFEEQST = Column(
        "LATEFEEQST", String(13, "SQL_Latin1_General_CP1_CI_AS"), nullable=False, server_default=text("('')")
    )
    CustSalRec = Column("CustSalRec", BIT, nullable=False, server_default=text("(0)"))
    OnlyTitle = Column("OnlyTitle", BIT, nullable=False, server_default=text("(0)"))
    Auction = Column(
        "Auction", String(17, "SQL_Latin1_General_CP1_CI_AS"), nullable=False, server_default=text("('')")
    )
    SY1_id = Column("SY1_id", UNIQUEIDENTIFIER, server_default=text("(newid())"))
    MultiMgmt = Column("MultiMgmt", BIT, nullable=False, server_default=text("(0)"))
    CreditCard = Column("CreditCard", BIT, nullable=False, server_default=text("(0)"))
    OnlineSale = Column("OnlineSale", BIT, nullable=False, server_default=text("(0)"))
    PoliceComm = Column("PoliceComm", BIT, nullable=False, server_default=text("(0)"))
    V7 = Column("V7", Integer, nullable=False, server_default=text("(1)"))
    V8 = Column("V8", Integer, nullable=False, server_default=text("(1)"))
    V9 = Column("V9", Integer, nullable=False, server_default=text("(1)"))
    V10 = Column("V10", Integer, nullable=False, server_default=text("(1)"))
    V11 = Column("V11", Integer, nullable=False, server_default=text("(1)"))
    V12 = Column("V12", Integer, nullable=False, server_default=text("(1)"))
    V13 = Column("V13", Integer, nullable=False, server_default=text("(1)"))
    V14 = Column("V14", Integer, nullable=False, server_default=text("(1)"))
    CustPoints = Column("CustPoints", BIT, nullable=False, server_default=text("(0)"))
    V15 = Column("V15", Integer, nullable=False, server_default=text("(1)"))
    V16 = Column("V16", Integer, nullable=False, server_default=text("(1)"))
    DlScan2 = Column("DlScan2", BIT, nullable=False, server_default=text("(0)"))
    V17 = Column("V17", Integer, nullable=False, server_default=text("(1)"))
    V18 = Column("V18", Integer, nullable=False, server_default=text("(1)"))
    Biometrix = Column("Biometrix", BIT, nullable=False, server_default=text("(0)"))
    V19 = Column("V19", Integer, nullable=False, server_default=text("(1)"))
    V20 = Column("V20", Integer, nullable=False, server_default=text("(1)"))
    ShareDrawers = Column("ShareDrawers", BIT, nullable=False, server_default=text("(0)"))
    DebitLoad = Column("DebitLoad", BIT, nullable=False, server_default=text("(0)"))
    V21 = Column("V21", Integer, nullable=False, server_default=text("(1)"))
    V22 = Column("V22", Integer, nullable=False, server_default=text("(1)"))
    SecureCam = Column("SecureCam", BIT, nullable=False, server_default=text("(0)"))
    V23 = Column("V23", Integer, nullable=False, server_default=text("(1)"))
    V24 = Column("V24", Integer, nullable=False, server_default=text("(1)"))
    Audit = Column("Audit", BIT, nullable=False, server_default=text("(0)"))
    V25 = Column("V25", Integer, nullable=False, server_default=text("(1)"))
    V26 = Column("V26", Integer, nullable=False, server_default=text("(1)"))
    Analysis = Column("Analysis", BIT, nullable=False, server_default=text("(0)"))
    V27 = Column("V27", Integer, nullable=False, server_default=text("(1)"))
    V28 = Column("V28", Integer, nullable=False, server_default=text("(1)"))
    ExcelExprt = Column("ExcelExprt", BIT, nullable=False, server_default=text("(0)"))
    V29 = Column("V29", Integer, nullable=False, server_default=text("(1)"))
    V30 = Column("V30", Integer, nullable=False, server_default=text("(1)"))
    RTimePhys = Column("RTimePhys", BIT, nullable=False, server_default=text("(0)"))
    V31 = Column("V31", Integer, nullable=False, server_default=text("(1)"))
    V32 = Column("V32", Integer, nullable=False, server_default=text("(1)"))
    RFID = Column("RFID", BIT, nullable=False, server_default=text("(0)"))
    V33 = Column("V33", Integer, nullable=False, server_default=text("(1)"))
    V34 = Column("V34", Integer, nullable=False, server_default=text("(1)"))
    LastUpdatedUSR_ID = Column("LastUpdatedUSR_ID", UNIQUEIDENTIFIER)
    BuySell = Column("BuySell", BIT, nullable=False, server_default=text("(0)"))
    V35 = Column("V35", Integer, nullable=False, server_default=text("(1)"))
    V36 = Column("V36", Integer, nullable=False, server_default=text("(1)"))
    BuySellLR = Column("BuySellLR", BIT, nullable=False, server_default=text("(0)"))
    V37 = Column("V37", Integer, nullable=False, server_default=text("(1)"))
    V38 = Column("V38", Integer, nullable=False, server_default=text("(1)"))
    Lite = Column("Lite", BIT, nullable=False, server_default=text("(0)"))
    V39 = Column("V39", Integer, nullable=False, server_default=text("(1)"))
    V40 = Column("V40", Integer, nullable=False, server_default=text("(1)"))
    EmpDrwOptn = Column("EmpDrwOptn", BIT, nullable=False, server_default=text("(0)"))
    V41 = Column("V41", Integer, nullable=False, server_default=text("(1)"))
    V42 = Column("V42", Integer, nullable=False, server_default=text("(1)"))
    GunLogOptn = Column("GunLogOptn", BIT, nullable=False, server_default=text("(0)"))
    V43 = Column("V43", Integer, nullable=False, server_default=text("(1)"))
    V44 = Column("V44", Integer, nullable=False, server_default=text("(1)"))
    MenuLvOptn = Column("MenuLvOptn", BIT, nullable=False, server_default=text("(0)"))
    V45 = Column("V45", Integer, nullable=False, server_default=text("(1)"))
    V46 = Column("V46", Integer, nullable=False, server_default=text("(1)"))
    TextMsg = Column("TextMsg", BIT, nullable=False, server_default=text("(0)"))
    V47 = Column("V47", Integer, nullable=False, server_default=text("(1)"))
    V48 = Column("V48", Integer, nullable=False, server_default=text("(1)"))
    ElecScale = Column("ElecScale", BIT, nullable=False, server_default=text("(0)"))
    V49 = Column("V49", Integer, nullable=False, server_default=text("(1)"))
    V50 = Column("V50", Integer, nullable=False, server_default=text("(1)"))
    PolDown = Column("PolDown", BIT, nullable=False, server_default=text("(0)"))
    V51 = Column("V51", Integer, nullable=False, server_default=text("(1)"))
    V52 = Column("V52", Integer, nullable=False, server_default=text("(1)"))
    QuickQuote = Column("QuickQuote", BIT, nullable=False, server_default=text("(0)"))
    V53 = Column("V53", Integer, nullable=False, server_default=text("(1)"))
    V54 = Column("V54", Integer, nullable=False, server_default=text("(1)"))
    VMNetPro = Column("VMNetPro", BIT, nullable=False, server_default=text("(0)"))
    V55 = Column("V55", Integer, nullable=False, server_default=text("(1)"))
    V56 = Column("V56", Integer, nullable=False, server_default=text("(1)"))
    AdvReports = Column("AdvReports", BIT, nullable=False, server_default=text("(0)"))
    V57 = Column("V57", Integer, nullable=False, server_default=text("(1)"))
    V58 = Column("V58", Integer, nullable=False, server_default=text("(1)"))
    keydx = Column("keydx", BIT, nullable=False, server_default=text("(0)"))
    MultiLang = Column("MultiLang", BIT, nullable=False, server_default=text("(0)"))
    V59 = Column("V59", Integer, nullable=False, server_default=text("(1)"))
    V60 = Column("V60", Integer, nullable=False, server_default=text("(1)"))
    ProtPlan = Column("ProtPlan", BIT, nullable=False, server_default=text("(0)"))
    V61 = Column("V61", Integer, nullable=False, server_default=text("(1)"))
    V62 = Column("V62", Integer, nullable=False, server_default=text("(1)"))
    RmtPay = Column("RmtPay", BIT, nullable=False, server_default=text("(0)"))
    V63 = Column("V63", Integer, nullable=False, server_default=text("(1)"))
    V64 = Column("V64", Integer, nullable=False, server_default=text("(1)"))
    PoleDisp = Column("PoleDisp", BIT, nullable=False, server_default=text("((0))"))
    V65 = Column("V65", Integer, nullable=False, server_default=text("((1))"))
    V66 = Column("V66", Integer, nullable=False, server_default=text("((1))"))
    AcuSport = Column("AcuSport", BIT, nullable=False, server_default=text("((0))"))
    V67 = Column("V67", Integer, nullable=False, server_default=text("((1))"))
    V68 = Column("V68", Integer, nullable=False, server_default=text("((1))"))

    @property
    def name(self):
        return str(self.NAME).strip().title()

    @property
    def address(self):
        return str(
            str(self.ADDRESS1).strip().title()
            + ", "
            + ((str(self.ADDRESS2).strip().title() + ", ") if len(str(self.ADDRESS2).strip()) > 0 else "")
            + str(self.CITY).strip().title()
            + ", "
            + str(self.STATE).strip().upper()
            + " "
            + str(self.ZIP).strip()
        )

    @property
    def phone(self):
        return str(self.PHONE).strip()

    def __repr__(self):
        return self.name


class C_Rates(Base):
    __tablename__ = "c_rates"

    rate_pk = Column(Integer, primary_key=True)
    STO_PK = Column(SmallInteger, ForeignKey("pawn.STORE_NO"), server_default=text("((1))"))
    DESCRIPT = Column(String(20, "SQL_Latin1_General_CP1_CI_AS"), server_default=text("('')"))
    PERIOD = Column(SmallInteger, server_default=text("((0))"))
    AllHigh = Column(BIT, server_default=text("((1))"))
    HD = Column(MONEY, server_default=text("((0))"))
    DP = Column(String(1, "SQL_Latin1_General_CP1_CI_AS"), server_default=text("('')"))
    AP = Column(MONEY, server_default=text("((0))"))
    MINAMT = Column(MONEY, server_default=text("((0))"))
    MAXAMT = Column(MONEY, server_default=text("((0))"))
    ONECHRG = Column(MONEY, server_default=text("((0))"))
    MONCHRG = Column(MONEY, server_default=text("((0))"))
    Interest = Column(MONEY, server_default=text("((0))"))
    NewRateTable = Column(String(20, "SQL_Latin1_General_CP1_CI_AS"), server_default=text("('')"))
    NewDefaults = Column(BIT, server_default=text("((0))"))
    cRates_id = Column(UNIQUEIDENTIFIER, server_default=text("(newid())"))
    SimpleInterest = Column(BIT, server_default=text("((0))"))
    LastUpdatedUSR_ID = Column(UNIQUEIDENTIFIER)

    Index("IDX_c_rates_Sto_PK_Descript", "STO_PK", "DESCRIPT")

    pawn_rate = relationship(
        "Pawn",
        primaryjoin="C_Rates.STO_PK == Pawn.STORE_NO and C_Rates.DESCRIPT == Pawn.RateTable",
        backref="c_rates",
    )

    def __repr__(self):
        return self.DESCRIPT.strip()


class LookupC(Base):
    __tablename__ = "Lookup_C"

    Sto_PK = Column(SmallInteger, nullable=False, server_default=text("(1)"))
    lc_pk = Column(Integer, primary_key=True, server_default=text("(1)"))
    lc_Descript = Column(String(20, "SQL_Latin1_General_CP1_CI_AS"), nullable=False, server_default=text("('')"))
    LB_FK = Column(Integer, nullable=False, index=True, server_default=text("(0)"))
    LUC_id = Column(UNIQUEIDENTIFIER, unique=True, server_default=text("(newid())"))
    LastUpdatedUSR_ID = Column(UNIQUEIDENTIFIER)


class CSSCustStatsStore(Base):
    __tablename__ = "CSS_CustStatsStore"

    CSS_ID = Column(UNIQUEIDENTIFIER, primary_key=True, unique=True, server_default=text("(newid())"))
    CSS_Sto_pk = Column(SmallInteger, ForeignKey("SysInfo1.STO_PK"), primary_key=True, nullable=False)
    CSS_Cus_fk = Column(Integer, ForeignKey("cust.Cus_PK"), primary_key=True, nullable=False)
    CSS_TotalPawns = Column(Integer, nullable=False, server_default=text("(0)"))
    CSS_ActivePawn = Column(Integer, nullable=False, server_default=text("(0)"))
    CSS_Redeemed = Column(Integer, nullable=False, server_default=text("(0)"))
    CSS_Buys = Column(Integer, nullable=False, server_default=text("(0)"))
    CSS_Sales = Column(MONEY, nullable=False, server_default=text("(0)"))
    CSS_Amt1 = Column(MONEY, nullable=False, server_default=text("(0)"))
    CSS_Amt2 = Column(MONEY, nullable=False, server_default=text("(0)"))

    store = relationship(SysInfo1, primaryjoin=(CSS_Sto_pk == SysInfo1.STO_PK), backref="CSS_CustStatsStore")

    def __repr__(self):
        return (
                "Lifetime Pawns: {l_pawns}, "
                + "Active Pawns: {a_pawns}, "
                + "Redeemed Pawns: {r_pawns}, "
                + "Buys: {buys}, Total Sales: ${ts}, "
                + "AMT1: {amt1}, AMT2: {amt2}"
        ).format(
            l_pawns=str(self.CSS_TotalPawns),
            a_pawns=str(self.CSS_ActivePawn),
            r_pawns=str(self.CSS_Redeemed),
            buys=str(self.CSS_Buys),
            ts=str(self.CSS_Sales),
            amt1=str(self.CSS_Amt1),
            amt2=str(self.CSS_Amt2),
        )


class Cust(Base):
    __tablename__ = "cust"
    __table_args__ = (
        Index("IDX_Cust_cus_pk_cus_store", "Cus_PK", "Cus_Store"),
        Index("IDX_Cust_K1_K80", "Cus_Store", "Cus_Entered"),
        Index("IDX_Cust_K1_K2", "Cus_Store", "Cus_PK"),
        Index("IDX_cust_LName_FNAME_MNAME_IDNUM1", "CUS_LNAME", "CUS_FNAME", "CUS_MNAME", "CUS_IDNUM1"),
    )

    Cus_Store = Column(Integer, ForeignKey(SysInfo1.STO_PK), nullable=False, server_default=text("(0)"))
    Cus_PK = Column(Integer, primary_key=True, server_default=text("(0)"))
    CUS_FNAME = Column(String(15, "SQL_Latin1_General_CP1_CI_AS"), nullable=False, server_default=text("('')"))
    CUS_MNAME = Column(String(15, "SQL_Latin1_General_CP1_CI_AS"), nullable=False, server_default=text("('')"))
    CUS_LNAME = Column(String(25, "SQL_Latin1_General_CP1_CI_AS"), nullable=False, server_default=text("('')"))
    CUS_ADD1 = Column(String(25, "SQL_Latin1_General_CP1_CI_AS"), nullable=False, server_default=text("('')"))
    CUS_ADD2 = Column(String(25, "SQL_Latin1_General_CP1_CI_AS"), nullable=False, server_default=text("('')"))
    CUS_CITY = Column(String(20, "SQL_Latin1_General_CP1_CI_AS"), nullable=False, server_default=text("('')"))
    CUS_STATE = Column(String(2, "SQL_Latin1_General_CP1_CI_AS"), nullable=False, server_default=text("('')"))
    CUS_ZIP = Column(String(10, "SQL_Latin1_General_CP1_CI_AS"), nullable=False, server_default=text("('')"))
    CUS_COUNTRY = Column(String(20, "SQL_Latin1_General_CP1_CI_AS"), nullable=False, server_default=text("('')"))
    CUS_AC1 = Column(String(3, "SQL_Latin1_General_CP1_CI_AS"), nullable=False, server_default=text("('')"))
    CUS_PHONE1 = Column(String(8, "SQL_Latin1_General_CP1_CI_AS"), nullable=False, server_default=text("('')"))
    CUS_HEIGHT = Column(String(6, "SQL_Latin1_General_CP1_CI_AS"), nullable=False, server_default=text("('')"))
    CUS_WEIGHT = Column(SmallInteger, nullable=False, server_default=text("(0)"))
    CUS_HAIRFK = Column(ForeignKey("Lookup_C.lc_pk"), nullable=False, server_default=text("(0)"))
    CUS_EYESFK = Column(ForeignKey("Lookup_C.lc_pk"), nullable=False, server_default=text("(0)"))
    CUS_RACEFK = Column(ForeignKey("Lookup_C.lc_pk"), nullable=False, server_default=text("(0)"))
    CUS_SEX = Column(
        String(1, "SQL_Latin1_General_CP1_CI_AS"), nullable=False, index=True, server_default=text("('')")
    )
    CUS_MARKS = Column(String(40, "SQL_Latin1_General_CP1_CI_AS"), nullable=False, server_default=text("('')"))
    CUS_BIRTHDate = Column(SMALLDATETIME)
    CUS_BIRTHCITY = Column(String(15, "SQL_Latin1_General_CP1_CI_AS"), nullable=False, server_default=text("('')"))
    CUS_BIRTHSTATE = Column(String(2, "SQL_Latin1_General_CP1_CI_AS"), nullable=False, server_default=text("('')"))
    CUS_BIRTH2 = Column(String(15, "SQL_Latin1_General_CP1_CI_AS"), nullable=False, server_default=text("('')"))
    CUS_IDTYP1 = Column(ForeignKey("Lookup_C.lc_pk"), nullable=False, server_default=text("(0)"))
    CUS_IDNUM1 = Column(
        String(20, "SQL_Latin1_General_CP1_CI_AS"), nullable=False, index=True, server_default=text("('')")
    )
    CUS_ID1EXP = Column(SMALLDATETIME)
    CUS_ID1ISSUE = Column(String(50, "SQL_Latin1_General_CP1_CI_AS"), nullable=False, server_default=text("('')"))
    CUS_IDTYP2 = Column(ForeignKey("Lookup_C.lc_pk"), nullable=False, server_default=text("(0)"))
    CUS_IDNUM2 = Column(String(20, "SQL_Latin1_General_CP1_CI_AS"), nullable=False, server_default=text("('')"))
    CUS_ID2EXP = Column(SMALLDATETIME)
    CUS_ID2ISSUE = Column(String(2, "SQL_Latin1_General_CP1_CI_AS"), nullable=False, server_default=text("('')"))
    CUS_KNOWN = Column(BIT, nullable=False, server_default=text("(0)"))
    CUS_SSNUM = Column(
        String(11, "SQL_Latin1_General_CP1_CI_AS"), nullable=False, index=True, server_default=text("('   -  -    ')")
    )
    CUS_VEHIC1 = Column(String(10, "SQL_Latin1_General_CP1_CI_AS"), nullable=False, server_default=text("('')"))
    CUS_VEHIC2 = Column(String(8, "SQL_Latin1_General_CP1_CI_AS"), nullable=False, server_default=text("('')"))
    CUS_VEHIC3 = Column(String(2, "SQL_Latin1_General_CP1_CI_AS"), nullable=False, server_default=text("('')"))
    CUS_EMPLOYER = Column(String(40, "SQL_Latin1_General_CP1_CI_AS"), nullable=False, server_default=text("('')"))
    CUS_EMPAD1 = Column(String(35, "SQL_Latin1_General_CP1_CI_AS"), nullable=False, server_default=text("('')"))
    CUS_EMPAD2 = Column(String(35, "SQL_Latin1_General_CP1_CI_AS"), nullable=False, server_default=text("('')"))
    CUS_EMPCITY = Column(String(20, "SQL_Latin1_General_CP1_CI_AS"), nullable=False, server_default=text("('')"))
    CUS_EMPSTATE = Column(String(2, "SQL_Latin1_General_CP1_CI_AS"), nullable=False, server_default=text("('')"))
    CUS_EMPZIP = Column(String(10, "SQL_Latin1_General_CP1_CI_AS"), nullable=False, server_default=text("('')"))
    CUS_AC2 = Column(String(3, "SQL_Latin1_General_CP1_CI_AS"), nullable=False, server_default=text("('')"))
    CUS_EMPPHONE = Column(String(14, "SQL_Latin1_General_CP1_CI_AS"), nullable=False, server_default=text("('')"))
    CUS_COMMENT = Column(String(200, "SQL_Latin1_General_CP1_CI_AS"), nullable=False, server_default=text("('')"))
    CUS_TOTALPAWNS = Column(Integer, nullable=False, server_default=text("(0)"))
    CUS_ACTIVEPAWN = Column(Integer, nullable=False, server_default=text("(0)"))
    CUS_REDEEMED = Column(Integer, nullable=False, server_default=text("(0)"))
    CUS_BUYS = Column(Integer, nullable=False, server_default=text("(0)"))
    CUS_SALES = Column(MONEY, nullable=False, server_default=text("(0.00)"))
    CUS_AMT1 = Column(MONEY, nullable=False, server_default=text("(0.00)"))
    CUS_AMT2 = Column(MONEY, nullable=False, server_default=text("(0.00)"))
    CUS_FFLNUM = Column(String(25, "SQL_Latin1_General_CP1_CI_AS"), nullable=False, server_default=text("('')"))
    CUS_DELETE = Column(BIT, nullable=False, server_default=text("(0)"))
    CUS_LOCKED = Column(BIT, nullable=False, server_default=text("(0)"))
    CUS_PAWNER = Column(BIT, nullable=False, server_default=text("(0)"))
    CUS_BUYER = Column(BIT, nullable=False, server_default=text("(0)"))
    CUS_IDADD1 = Column(String(25, "SQL_Latin1_General_CP1_CI_AS"), nullable=False, server_default=text("('')"))
    CUS_IDADD2 = Column(String(25, "SQL_Latin1_General_CP1_CI_AS"), nullable=False, server_default=text("('')"))
    CUS_IDCITY = Column(String(20, "SQL_Latin1_General_CP1_CI_AS"), nullable=False, server_default=text("('')"))
    CUS_IDSTATE = Column(String(2, "SQL_Latin1_General_CP1_CI_AS"), nullable=False, server_default=text("('')"))
    CUS_IDZIP = Column(String(10, "SQL_Latin1_General_CP1_CI_AS"), nullable=False, server_default=text("('')"))
    CUS_CREDIT = Column(MONEY, nullable=False, server_default=text("(0.00)"))
    CUS_SPECIAL = Column(ForeignKey("Lookup_C.lc_pk"), nullable=False, server_default=text("(0)"))
    CUS_PIC_FK = Column(Integer, nullable=False, server_default=text("((-1))"))
    cus_Thum_fk = Column(Integer, nullable=False, server_default=text("((-1))"))
    CUS_Action_Spec = Column(CHAR(1, "SQL_Latin1_General_CP1_CI_AS"), nullable=False, server_default=text("(' ')"))
    Cus_id = Column(UNIQUEIDENTIFIER, unique=True, server_default=text("(newid())"))
    Cus_PatriotAct = Column(BIT, server_default=text("(0)"))
    Cus_PointsPawnBuy = Column(Integer, nullable=False, server_default=text("(0)"))
    Cus_PointsSale = Column(Integer, nullable=False, server_default=text("(0)"))
    Cus_PointsAvail = Column(Integer, nullable=False, server_default=text("(0)"))
    Cus_PointsMailer = Column(BIT, nullable=False, server_default=text("(0)"))
    Cus_TaxID = Column(String(25, "SQL_Latin1_General_CP1_CI_AS"), nullable=False, server_default=text("('')"))
    Cus_CellPhone = Column(String(20, "SQL_Latin1_General_CP1_CI_AS"))
    Cus_Email = Column(String(254, "SQL_Latin1_General_CP1_CI_AS"), index=True)
    Cus_Entered = Column(DateTime)
    Usr_ID = Column(UNIQUEIDENTIFIER)
    Cus_NoRemind = Column(BIT, nullable=False, server_default=text("(0)"))
    Cus_Preferred = Column(String(20, "SQL_Latin1_General_CP1_CI_AS"))
    Cus_AnnivDate = Column(DateTime)
    Cus_Search_IDNum1 = Column(String(20, "SQL_Latin1_General_CP1_CI_AS"), index=True)
    Cus_PatriotMsg = Column(BIT, server_default=text("(0)"))
    Cus_Form8300Sent = Column(DateTime)
    Cus_Search_SSNUM4 = Column(String(4, "SQL_Latin1_General_CP1_CI_AS"), index=True)
    Cus_Military = Column(BIT, server_default=text("(0)"))
    LastUpdatedUSR_ID = Column(UNIQUEIDENTIFIER)
    Cus_TxtMsg = Column(BIT, server_default=text("(0)"))
    Cus_TxtMsgSent = Column(DateTime)
    Cus_FFLExpireDate = Column(DateTime)
    Cus_TxtVerified = Column(BIT, nullable=False, server_default=text("(0)"))
    Cus_ID1IssueDate = Column(DateTime)
    Cus_ID2IssueDate = Column(DateTime)
    cus_taxexempt = Column(BIT, nullable=False, server_default=text("((0))"))
    cus_MLARate = Column(BIT, nullable=False, server_default=text("((0))"))

    Lookup_C = relationship("LookupC", primaryjoin="Cust.CUS_EYESFK == LookupC.lc_pk")
    Lookup_C1 = relationship("LookupC", primaryjoin="Cust.CUS_HAIRFK == LookupC.lc_pk")
    Lookup_C2 = relationship("LookupC", primaryjoin="Cust.CUS_IDTYP1 == LookupC.lc_pk")
    Lookup_C3 = relationship("LookupC", primaryjoin="Cust.CUS_IDTYP2 == LookupC.lc_pk")
    Lookup_C4 = relationship("LookupC", primaryjoin="Cust.CUS_RACEFK == LookupC.lc_pk")
    Lookup_C5 = relationship("LookupC", primaryjoin="Cust.CUS_SPECIAL == LookupC.lc_pk")

    stats = relationship(
        CSSCustStatsStore,
        primaryjoin=((Cus_PK == CSSCustStatsStore.CSS_Cus_fk) and (Cus_Store == CSSCustStatsStore.CSS_Sto_pk)),
        uselist=False,
        backref="Cust",
    )

    @property
    def name(self):
        return (
                self.CUS_FNAME.strip().title()
                + (" " + self.CUS_MNAME.title()[:1] if self.CUS_MNAME is not None else "")
                + " "
                + self.CUS_LNAME.strip().title()
        )

    @property
    def email(self):
        return self.Cus_Email.strip() if self.Cus_Email is not None else None

    @property
    def phone(self):
        c = (
            ("".join(x if x.isnumeric() else "" for x in self.Cus_CellPhone.strip()))
            if self.Cus_CellPhone is not None
            else ("".join(x if x.isnumeric() else "" for x in (self.CUS_AC1 + self.CUS_PHONE1)))
            if self.CUS_AC1 is not None and self.CUS_PHONE1 is not None
            else ("".join(x if x.isnumeric() else "" for x in (self.CUS_AC2 + self.CUS_PHONE2)))
            if self.CUS_AC2 is not None and self.CUS_PHONE2 is not None
            else None
        )
        return c[:10] if len(c) > 9 else None

    def __repr__(self):
        return self.name


class Acct(Base):
    __tablename__ = "Acct"

    __table_args__ = (
        Index("IDX_Acct_Sto_PK_Station", "sto_pk", "Station"),
        Index("IDX_Acct_Sto_PK_TicketNum", "TICKETNUM", "sto_pk"),
        Index("IDX_Acct_MultiKey2", "DATEin", "sto_pk", "TYPE", "TENDERTYP1", "TENDERTYP2"),
        Index("IDX_Acct_Sto_PK_Type", "sto_pk", "TYPE"),
        Index("IDX_Acct_MultiKey", "sto_pk", "TICKETNUM", "DATEin", "Acct_PK", "TYPE", "AMOUNT"),
    )

    Acct_PK = Column("Acct_PK", Integer, primary_key=True, nullable=False)
    sto_pk = Column("sto_pk", SmallInteger, nullable=False, server_default=text("(1)"))
    DATEin = Column("DATEin", DateTime, index=True)
    TICKETNUM = Column("TICKETNUM", Integer, ForeignKey("pawn.TICKETNUM"), nullable=False, server_default=text("(0)"))
    CUS_FK = Column(
        "CUS_FK", Integer, ForeignKey("cust.Cus_PK"), nullable=False, index=True, server_default=text("(0)")
    )
    TYPE = Column("TYPE", CHAR(3, "SQL_Latin1_General_CP1_CI_AS"), nullable=False, server_default=text("('')"))
    AMOUNT = Column("AMOUNT", MONEY, nullable=False, server_default=text("(0.00)"))
    Usr_FK = Column("Usr_FK", Integer, nullable=False, server_default=text("(1)"))
    dPERCENT = Column("dPERCENT", Float(53), server_default=text("(0)"))
    TOWHOM = Column("TOWHOM", String(20, "SQL_Latin1_General_CP1_CI_AS"), nullable=False, server_default=text("('')"))
    Enter_UsrFK = Column("Enter_UsrFK", Integer, nullable=False, server_default=text("(0)"))
    TAXSALES = Column("TAXSALES", MONEY, nullable=False, server_default=text("(0.00)"))
    STATETAX = Column("STATETAX", MONEY, nullable=False, server_default=text("(0.00)"))
    COUNTYTAX = Column("COUNTYTAX", MONEY, nullable=False, server_default=text("(0.00)"))
    LOCALTAX = Column("LOCALTAX", MONEY, nullable=False, server_default=text("(0.00)"))
    TENDERTYP1 = Column("TENDERTYP1", Integer, nullable=False, server_default=text("(0)"))
    TENDERAMT1 = Column("TENDERAMT1", MONEY, nullable=False, server_default=text("(0.00)"))
    TENDERTYP2 = Column("TENDERTYP2", Integer, nullable=False, server_default=text("(0)"))
    TENDERAMT2 = Column("TENDERAMT2", MONEY, nullable=False, server_default=text("(0.00)"))
    TENDCHANGE = Column("TENDCHANGE", MONEY, nullable=False, server_default=text("(0.00)"))
    Cus_Credit = Column("Cus_Credit", MONEY, nullable=False, server_default=text("(0.00)"))
    CreditSale = Column("CreditSale", MONEY, nullable=False, server_default=text("(0.00)"))
    Per1 = Column("Per1", MONEY, nullable=False, server_default=text("(0.00)"))
    Per2 = Column("Per2", MONEY, nullable=False, server_default=text("(0.00)"))
    OneTime = Column("OneTime", MONEY, nullable=False, server_default=text("(0.00)"))
    Ticket = Column("Ticket", MONEY, nullable=False, server_default=text("(0.00)"))
    Prep = Column("Prep", MONEY, nullable=False, server_default=text("(0.00)"))
    Gun = Column("Gun", MONEY, nullable=False, server_default=text("(0.00)"))
    Daily = Column("Daily", MONEY, nullable=False, server_default=text("(0.00)"))
    RTint = Column("RTint", MONEY, nullable=False, server_default=text("(0.00)"))
    RTsvc = Column("RTsvc", MONEY, nullable=False, server_default=text("(0.00)"))
    RTper = Column("RTper", MONEY, nullable=False, server_default=text("(0.00)"))
    RTonetime = Column("RTonetime", MONEY, nullable=False, server_default=text("(0.00)"))
    LATE = Column("LATE", MONEY, nullable=False, server_default=text("(0.00)"))
    OvrRideAmt = Column("OvrRideAmt", MONEY, nullable=False, server_default=text("(0.00)"))
    Cost = Column("Cost", MONEY, nullable=False, server_default=text("(0.00)"))
    LostTicket = Column("LostTicket", MONEY, nullable=False, server_default=text("(0.00)"))
    ExemptSales = Column("ExemptSales", MONEY, nullable=False, server_default=text("(0)"))
    cFlag = Column("cFlag", CHAR(2, "SQL_Latin1_General_CP1_CI_AS"), nullable=False, server_default=text("(' ')"))
    AuctionEntry = Column("AuctionEntry", BIT, nullable=False, server_default=text("(0)"))
    RetSvcChg = Column("RetSvcChg", MONEY, nullable=False, server_default=text("(0.00)"))
    Act_id = Column("Act_id", UNIQUEIDENTIFIER, unique=True, server_default=text("(newid())"))
    Station = Column("Station", TINYINT, nullable=False, server_default=text("(1)"))
    CountyExemptSales = Column("CountyExemptSales", MONEY, nullable=False, server_default=text("(0)"))
    CountyTaxSales = Column("CountyTaxSales", MONEY, nullable=False, server_default=text("(0)"))

    customer = relationship(
        Cust, primaryjoin=((CUS_FK == Cust.Cus_PK) and (sto_pk == Cust.Cus_Store)), backref="Acct"
    )
    pawn_ticket = relationship(
        "Pawn", primaryjoin="((Acct.TICKETNUM == Pawn.TICKETNUM) and (Acct.sto_pk == Pawn.STORE_NO))", backref="Acct"
    )

    def __repr__(self):
        return str(
            "Renewal"
            if self.TYPE.strip() == "PPP"
            else "Pawn Loan"
            if self.TYPE.strip() == "P"
            else "Renewal + Principal Paydown"
            if self.TYPE.strip() == "PPL"
            else "Redemption"
            if self.TYPE.strip() == "PPU"
            else "Unknown Transaction Type ({trn})".format(trn=self.TYPE.strip())
        ) + (" ($%.2f)" % (float(self.AMOUNT) if self.TYPE.strip() != "P" else float(self.AMOUNT * -1)))


class Pawn(Base):
    __tablename__ = "pawn"
    __table_args__ = (
        Index("IDX_PAWN_MultiKey1", "STORE_NO", "usr_fk", "CUS_FK", "TICKETNUM", "DATEIN"),
        Index("IX_pawn_OrigTicket", "ORIGTICKET", "STORE_NO"),
        Index("IDX_Pawn_MultiKey3", "STATUS", "STORE_NO", "TRANS", "PWN_id"),
        Index("IDX_PAWN_MultiKey2", "TICKETNUM", "DATEIN", "STORE_NO"),
    )

    CUS_FK = Column(ForeignKey("cust.Cus_PK"), index=True, server_default=text("(1)"))
    STORE_NO = Column(SmallInteger, ForeignKey("SysInfo1.STO_PK"), nullable=False, server_default=text("(1)"))
    TICKETNUM = Column(Integer, nullable=False, server_default=text("(0)"))
    POLTICNUM = Column(Integer, nullable=False, server_default=text("(0)"))
    usr_fk = Column(Integer, nullable=False, server_default=text("(0)"))
    DATEIN = Column(SMALLDATETIME)
    NUMDAYS = Column(SmallInteger, nullable=False, server_default=text("(0)"))
    DATEOUT = Column(SMALLDATETIME, index=True)
    PawnAMT = Column(MONEY, nullable=False, server_default=text("(0.0)"))
    TRANS = Column(String(1, "SQL_Latin1_General_CP1_CI_AS"), nullable=False, server_default=text("('P')"))
    PAIDAMT = Column(MONEY, nullable=False, server_default=text("(0.0)"))
    TRANSDATE = Column(SMALLDATETIME)
    STATUS = Column(String(1, "SQL_Latin1_General_CP1_CI_AS"), nullable=False, server_default=text("('')"))
    NUMITEMS = Column(SmallInteger, nullable=False, server_default=text("(0)"))
    RateTable = Column(
        String(20, "SQL_Latin1_General_CP1_CI_AS"),
        ForeignKey("c_rates.DESCRIPT"),
        nullable=False,
        server_default=text("('')"),
    )
    CHARGEDATE = Column(SMALLDATETIME)
    COMMENT = Column(String(20, "SQL_Latin1_General_CP1_CI_AS"), nullable=False, server_default=text("('')"))
    SERVPERIOD = Column(SmallInteger, nullable=False, server_default=text("(0)"))
    COMPNDSERV = Column(BIT, nullable=False, server_default=text("(0)"))
    FLOATAMT = Column(MONEY, nullable=False, server_default=text("(0.0)"))
    GunChrg = Column(MONEY, nullable=False, server_default=text("(0.0)"))
    TICKCHRG = Column(MONEY, server_default=text("(0.0)"))
    MONTHCHRG = Column(MONEY, nullable=False, server_default=text("(0.0)"))
    MonthChrg2 = Column(MONEY, nullable=False, server_default=text("(0.0)"))
    MONTHLYCHG = Column(BIT, nullable=False, server_default=text("(0.0)"))
    PrepChrg = Column(MONEY, nullable=False, server_default=text("(0.0)"))
    StorageChrg = Column(MONEY, nullable=False, server_default=text("(0.0)"))
    REMINDER = Column(SMALLDATETIME)
    RePawned = Column(BIT, nullable=False, server_default=text("(0)"))
    ORIGTICKET = Column(Integer, nullable=False, server_default=text("(0)"))
    ORIGTICKCHRG = Column(MONEY, nullable=False, server_default=text("(0.00)"))
    ORIGONEFEE = Column(MONEY, nullable=False, server_default=text("(0)"))
    OrigDateIN = Column(SMALLDATETIME)
    OrigDateOut = Column(SMALLDATETIME)
    OrigChgDate = Column(SMALLDATETIME)
    OrigGunChrg = Column(MONEY, nullable=False, server_default=text("(0.00)"))
    OrigPawnAmt = Column(MONEY, nullable=False, server_default=text("(0.00)"))
    OrigPrepChrg = Column(MONEY, nullable=False, server_default=text("(0.00)"))
    OrigPrevPawnAmt = Column(MONEY, nullable=False, server_default=text("(0.00)"))
    OrigFloatAmt = Column(MONEY, nullable=False, server_default=text("(0.00)"))
    PrevPawnAmt = Column(MONEY, nullable=False, server_default=text("(0.00)"))
    PrevCustPK = Column(Integer, nullable=False, index=True, server_default=text("(0)"))
    PAWNNOTE = Column(String(200, "SQL_Latin1_General_CP1_CI_AS"), nullable=False, server_default=text("(' ')"))
    DAILYFEE = Column(MONEY, nullable=False, server_default=text("(0.0)"))
    OvrRideAmt = Column(MONEY, nullable=False, server_default=text("(0.00)"))
    UnExtendDate = Column(SMALLDATETIME)
    StartDate = Column(SMALLDATETIME)
    TitleLoan = Column(BIT, nullable=False, server_default=text("(0)"))
    PWN_id = Column(UNIQUEIDENTIFIER, primary_key=True, unique=True, server_default=text("(newid())"))
    CheckNum = Column(String(20, "SQL_Latin1_General_CP1_CI_AS"), nullable=False, server_default=text("('')"))
    StartPawnAmt = Column(MONEY, nullable=False, server_default=text("(0.0000)"))
    LastUpdatedUSR_ID = Column(UNIQUEIDENTIFIER)
    Text_Msg = Column(BIT, nullable=False, server_default=text("(0)"))
    PdDate = Column(SMALLDATETIME)
    OrigPdDate = Column(SMALLDATETIME)
    MLARate = Column(BIT, nullable=False, server_default=text("((0))"))

    store = relationship(
        SysInfo1, primaryjoin=(STORE_NO == SysInfo1.STO_PK), backref="pawn", uselist=False, lazy="joined"
    )

    customer = relationship(
        Cust,
        primaryjoin=(and_(foreign(CUS_FK) == Cust.Cus_PK, foreign(STORE_NO) == Cust.Cus_Store)),
        backref="pawn",
        uselist=False,
        lazy="joined",
    )

    __acct = relationship(
        Acct,
        primaryjoin=(
            and_(
                (foreign(TICKETNUM) == Acct.TICKETNUM),
                (foreign(STORE_NO) == Acct.sto_pk),
                (foreign(CUS_FK) == Acct.CUS_FK),
            )
        ),
        backref="pawn",
        uselist=True,
    )

    @property
    def pay_count(self):
        return len(
            list(filter(lambda x: x.TYPE in "PPP" and x.AMOUNT > 0 and x.sto_pk == self.STORE_NO, self.__acct))
        )

    @property
    def original_station(self):
        return (
            next(filter(lambda x: x.TYPE.strip() == "P", self.__acct)).Station
            if next(filter(lambda x: x.TYPE.strip() == "P", self.__acct), None) is not None
            else 1
        )

    _rates = relationship(
        "C_Rates",
        primaryjoin=(
            and_(
                (foreign(RateTable) == C_Rates.DESCRIPT),
                (foreign(STORE_NO) == C_Rates.STO_PK),
                (PawnAMT >= C_Rates.MINAMT),
                (PawnAMT <= C_Rates.MAXAMT),
                (PawnAMT <= C_Rates.HD),
            )
        ),
        uselist=True,
        backref="pawn",
    )

    def __repr__(self):
        return ("Pawn " if self.TRANS == "P" else "Purchase ") + (
                str(self.TICKETNUM) + " ($" + str(self.PawnAMT) + ")"
        )

    @property
    def rate(self):
        # Any given ticket's self.__rates list should only include rates whose description
        # matches, where the ticket's PawnAMT is between the rate's MIN and MAX amounts,
        # *and* whose highest dollar amount (rate.HD) is greater then or equal to the PawnAMT
        # Therefore, we should technically only have to sort out any rate whose HD amount isn't
        # the lowest in the list -and- whose PERIOD value lines up with the ticket's pay_count

        # Start by sorting out all the rates whose HD amount
        # doesn't match the lowest available amount in the rate list
        r = list(filter(lambda x: x.HD == min([x.HD for x in list(self._rates)]), list(self._rates)))

        # Check if the ticket we're dealing with has ever been paid against
        if self.pay_count == 0:
            # If it doesn't, filter out any rates whose PERIOD is greater than the lowest entry in the rate list
            r = list(filter(lambda x: x.PERIOD == min([x.PERIOD for x in r]), r))

        # If the ticket has ever been paid against,
        # check if rate list has an entry whose PERIOD matches the ticket's pay_count
        elif self.pay_count in [x.PERIOD for x in self._rates]:
            # If it does, filter out any rates that don't match
            r = list(filter(lambda x: x.PERIOD == self.pay_count, r))

        # If the ticket has a payment history and we didn't find the matching period,
        # we're probably dealing with a ticket whose payment rate is covered by the
        # entry with the highest PERIOD value
        else:
            r = list(filter(lambda x: x.PERIOD == max([x.PERIOD for x in r]), r))

        # At this point, we should have whittled the list of rates
        # down to a single correct entry, so we'll return it and call it done
        if len(r) == 1:
            return r[0]
        else:
            raise RuntimeError("Found more than one possible rate!")

    @property
    def payment_amount(self):
        return int(
            float(self.PawnAMT * ((self.rate.AP + self.rate.Interest + self.rate.MONCHRG + self.rate.ONECHRG) / 100))
            * 100
        )
