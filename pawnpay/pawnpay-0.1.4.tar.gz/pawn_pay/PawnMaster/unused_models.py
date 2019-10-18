# coding: utf-8

#  Copyright (c) 2019 | Advancing Technology Systems, LLC
#  See LICENSE for any grants of usage, distribution, or modification

from sqlalchemy import BINARY, CHAR, Column, DECIMAL, DateTime, Float, ForeignKey, Index, Integer, LargeBinary, NCHAR, \
    Numeric, SmallInteger, String, Table, Text, Unicode, text
from sqlalchemy.dialects.mssql import BIT, MONEY, SMALLDATETIME, TIMESTAMP, TINYINT, UNIQUEIDENTIFIER
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata

t_c_rates = Table(
    'c_rates', metadata,
    Column('rate_pk', Integer, nullable=False),
    Column('STO_PK', SmallInteger, server_default=text("(1)")),
    Column('DESCRIPT', String(20, 'SQL_Latin1_General_CP1_CI_AS'), server_default=text("('')")),
    Column('PERIOD', SmallInteger, server_default=text("(0)")),
    Column('AllHigh', BIT, server_default=text("(1)")),
    Column('HD', MONEY, server_default=text("(0)")),
    Column('DP', String(1, 'SQL_Latin1_General_CP1_CI_AS'), server_default=text("('')")),
    Column('AP', MONEY, server_default=text("(0)")),
    Column('MINAMT', MONEY, server_default=text("(0)")),
    Column('MAXAMT', MONEY, server_default=text("(0)")),
    Column('ONECHRG', MONEY, server_default=text("(0)")),
    Column('MONCHRG', MONEY, server_default=text("(0)")),
    Column('Interest', MONEY, server_default=text("(0)")),
    Column('NewRateTable', String(20, 'SQL_Latin1_General_CP1_CI_AS'), server_default=text("('')")),
    Column('NewDefaults', BIT, server_default=text("(0)")),
    Column('cRates_id', UNIQUEIDENTIFIER, nullable=False, unique=True, server_default=text("(newid())")),
    Column('SimpleInterest', BIT, nullable=False, server_default=text("(0)")),
    Column('LastUpdatedUSR_ID', UNIQUEIDENTIFIER),
    Index('IDX_c_rates_Sto_PK_Descript', 'STO_PK', 'DESCRIPT')
)

t_AcctGroups = Table(
    'AcctGroups', metadata,
    Column('GNum', SmallInteger, index=True),
    Column('GType', Unicode(5), index=True),
    Column('GDescr', Unicode(150)),
    Index('IDX_AcctGroups_1', 'GNum', 'GType', unique=True)
)

t_AuctionItems = Table(
    'AuctionItems', metadata,
    Column('AUI_ID', UNIQUEIDENTIFIER, nullable=False, unique=True, server_default=text("(newid())")),
    Column('AUI_NO', Integer, nullable=False),
    Column('Sto_PK', SmallInteger, nullable=False, server_default=text("(0)")),
    Column('Items_PK', Integer, nullable=False),
    Column('Items_ID', UNIQUEIDENTIFIER, nullable=False),
    Column('Status', String(10, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('Level1', String(20, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('Level2', String(20, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('Level3', String(20, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('Level4', String(20, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('Brand', String(20, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('ModelNum', String(20, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('Description', String(200, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('Quantity', Integer, nullable=False),
    Column('InvNum', String(14, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('ResaleAmt', MONEY, nullable=False),
    Column('Amount', MONEY, nullable=False),
    Column('Date_Sent', DateTime),
    Column('Date_Read', DateTime),
    Column('Usr_ID', UNIQUEIDENTIFIER),
    Column('AUI_Code', String(200, 'SQL_Latin1_General_CP1_CI_AS'), server_default=text("(null)"))
)

t_AuctionTrans = Table(
    'AuctionTrans', metadata,
    Column('AUT_ID', UNIQUEIDENTIFIER, nullable=False, unique=True, server_default=text("(newid())")),
    Column('AUT_NO', Integer, nullable=False),
    Column('AUI_ID', UNIQUEIDENTIFIER, nullable=False),
    Column('State', CHAR(2, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('Quantity', Integer),
    Column('Price', MONEY, nullable=False),
    Column('Tax', MONEY),
    Column('Insurance', MONEY),
    Column('Shipping', MONEY),
    Column('Shipping_Cost', MONEY),
    Column('ShipViaCode', String(10, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('EbayFees', MONEY),
    Column('AuctionFees', MONEY),
    Column('Status', String(10, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('Date_Sent', DateTime),
    Column('Date_Read', DateTime),
    Column('Usr_ID', UNIQUEIDENTIFIER),
    Column('SaleLocation', String(1, 'SQL_Latin1_General_CP1_CI_AS'))
)

t_AuctionTransDetail = Table(
    'AuctionTransDetail', metadata,
    Column('AUTD_ID', UNIQUEIDENTIFIER, nullable=False, server_default=text("(newid())")),
    Column('AUT_ID', UNIQUEIDENTIFIER, nullable=False),
    Column('AUT_NO', Integer, nullable=False),
    Column('AUI_ID', UNIQUEIDENTIFIER, nullable=False),
    Column('State', CHAR(2, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('Quantity', Integer),
    Column('Price', MONEY, nullable=False),
    Column('Tax', MONEY),
    Column('Insurance', MONEY),
    Column('Shipping', MONEY),
    Column('Shipping_Cost', MONEY),
    Column('ShipViaCode', String(10, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('EbayFees', MONEY),
    Column('AuctionFees', MONEY),
    Column('Status', String(10, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('Date_Sent', DateTime),
    Column('Date_Read', DateTime),
    Column('Usr_ID', UNIQUEIDENTIFIER),
    Column('SaleLocation', String(1, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('eforo_id1', String(10, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('eforo_id2', String(10, 'SQL_Latin1_General_CP1_CI_AS'))
)

t_BAT_BatchHeader = Table(
    'BAT_BatchHeader', metadata,
    Column('bat_ID', UNIQUEIDENTIFIER, nullable=False, unique=True, server_default=text("(newid())")),
    Column('bat_No', Integer, nullable=False),
    Column('STO_PK', SmallInteger, nullable=False),
    Column('bat_Date', DateTime, nullable=False, server_default=text("(getdate())")),
    Column('usr_ID', UNIQUEIDENTIFIER, nullable=False),
    Column('bat_status', CHAR(1, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('bat_begindate', DateTime, nullable=False),
    Column('bat_enddate', DateTime, nullable=False),
    Column('bat_count', Integer),
    Column('bat_exportdate', DateTime),
    Column('bat_exportname', String(50, 'SQL_Latin1_General_CP1_CI_AS')),
    Index('IDX_BAT_BatchHeader_Sto_PK_Bat_Status', 'STO_PK', 'bat_status')
)


class BWILog(Base):
    __tablename__ = 'BWI_Logs'

    ID = Column(Integer, primary_key=True)
    CreatedOn = Column(DateTime, nullable=False, server_default=text("(getdate())"))
    STO_PK = Column(Integer, nullable=False)
    ResponseMessage = Column(String(1000, 'SQL_Latin1_General_CP1_CI_AS'))
    Pwn_id = Column(UNIQUEIDENTIFIER, nullable=False)
    SubmissionStatus = Column(Integer, nullable=False, index=True, server_default=text("(0)"))


class Bin(Base):
    __tablename__ = 'Bin'
    __table_args__ = (
        Index('IX_bin', 'bin', 'bin_store'),
    )

    bin_id = Column(UNIQUEIDENTIFIER, primary_key=True, server_default=text("(newid())"))
    bin_pk = Column(Integer, nullable=False)
    bin_store = Column(SmallInteger, nullable=False)
    bin = Column(String(6, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    LastUpdatedUSR_ID = Column(UNIQUEIDENTIFIER)


class CBLUCashBoxLookupUnit(Base):
    __tablename__ = 'CBLU_CashBoxLookupUnit'

    CBLU_ID = Column(UNIQUEIDENTIFIER, primary_key=True, server_default=text("(newid())"))
    STO_PK = Column(SmallInteger, nullable=False)
    CBLU_Description = Column(String(50, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    CBLU_Unit = Column(MONEY, nullable=False)


class CCLog(Base):
    __tablename__ = 'CCLog'

    CCLog_id = Column(UNIQUEIDENTIFIER, primary_key=True, server_default=text("(newid())"))
    Sto_PK = Column(SmallInteger, nullable=False)
    CCSecure_id = Column(UNIQUEIDENTIFIER, nullable=False)
    LogType = Column(CHAR(60, 'SQL_Latin1_General_CP1_CI_AS'))
    LogDate = Column(DateTime)
    ipaddress = Column(CHAR(30, 'SQL_Latin1_General_CP1_CI_AS'))
    pcname = Column(CHAR(30, 'SQL_Latin1_General_CP1_CI_AS'))


class CCSecure(Base):
    __tablename__ = 'CCSecure'

    CCSecure_ID = Column(UNIQUEIDENTIFIER, primary_key=True, server_default=text("(newid())"))
    sto_pk = Column(SmallInteger, nullable=False)
    usr_id = Column(UNIQUEIDENTIFIER, nullable=False)
    active = Column(BIT)
    last_pass_chg = Column(DateTime)
    username = Column(CHAR(3, 'SQL_Latin1_General_CP1_CI_AS'))
    password = Column(CHAR(8, 'SQL_Latin1_General_CP1_CI_AS'))
    lpassword1 = Column(CHAR(8, 'SQL_Latin1_General_CP1_CI_AS'))
    lpassword2 = Column(CHAR(8, 'SQL_Latin1_General_CP1_CI_AS'))
    lpassword3 = Column(CHAR(8, 'SQL_Latin1_General_CP1_CI_AS'))
    lpassword4 = Column(CHAR(8, 'SQL_Latin1_General_CP1_CI_AS'))
    _pass = Column('pass', SmallInteger)
    fail = Column(SmallInteger)
    lockout = Column(DateTime)
    loginattempts = Column(SmallInteger)
    pwentryattempts = Column(SmallInteger)
    pwchange = Column(SmallInteger)
    lockouts = Column(SmallInteger)
    configaccess = Column(SmallInteger)
    configchanges = Column(SmallInteger)
    createdate = Column(DateTime)
    deletedate = Column(DateTime)


class CCToken(Base):
    __tablename__ = 'CCTokens'

    CCToken_id = Column(UNIQUEIDENTIFIER, primary_key=True, server_default=text("(newid())"))
    Ticketnum = Column(Integer)
    CCToken = Column(CHAR(60, 'SQL_Latin1_General_CP1_CI_AS'))
    CCAuth = Column(CHAR(10, 'SQL_Latin1_General_CP1_CI_AS'))
    CCRef = Column(CHAR(10, 'SQL_Latin1_General_CP1_CI_AS'))
    CCAcqRefData = Column(CHAR(100, 'SQL_Latin1_General_CP1_CI_AS'))
    CCProcessData = Column(CHAR(30, 'SQL_Latin1_General_CP1_CI_AS'))
    CCDate = Column(DateTime)
    LastUpdatedUsr_id = Column(UNIQUEIDENTIFIER, nullable=False)
    CCSequence = Column(CHAR(20, 'SQL_Latin1_General_CP1_CI_AS'))
    CCPrintData = Column(Text(2147483647, 'SQL_Latin1_General_CP1_CI_AS'))
    Sto_pk = Column(SmallInteger, nullable=False, server_default=text("(0)"))


class CMABHACHBatchHeader(Base):
    __tablename__ = 'CMABH_ACHBatchHeader'

    cmabh_id = Column(UNIQUEIDENTIFIER, primary_key=True, server_default=text("(newid())"))
    cmabh_no = Column(Integer, nullable=False)
    sto_pk = Column(SmallInteger, nullable=False)
    cmabh_date = Column(DateTime, nullable=False)
    cmabh_effdate = Column(DateTime, nullable=False)
    cmabh_status = Column(CHAR(1, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    usr_id = Column(UNIQUEIDENTIFIER, nullable=False)
    cmabh_filename = Column(String(100, 'SQL_Latin1_General_CP1_CI_AS'))
    cmabh_cmdba_id = Column(UNIQUEIDENTIFIER)
    cmabh_skeddate = Column(DateTime)


class CMBATBatchHeader(Base):
    __tablename__ = 'CMBAT_BatchHeader'

    bat_ID = Column(UNIQUEIDENTIFIER, primary_key=True, server_default=text("(newid())"))
    bat_No = Column(Integer, nullable=False)
    STO_PK = Column(SmallInteger, nullable=False)
    bat_Date = Column(DateTime, nullable=False, server_default=text("(getdate())"))
    usr_ID = Column(UNIQUEIDENTIFIER, nullable=False)
    bat_status = Column(CHAR(1, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    bat_begindate = Column(DateTime, nullable=False)
    bat_enddate = Column(DateTime, nullable=False)
    bat_count = Column(Integer)
    bat_exportdate = Column(DateTime)
    bat_exportname = Column(String(50, 'SQL_Latin1_General_CP1_CI_AS'))


class CMBHBatchHeader(Base):
    __tablename__ = 'CMBH_BatchHeader'
    __table_args__ = (
        Index('IDX_CMBH_BatchHeader_K5_K1', 'cmbh_date', 'cmbh_id'),
    )

    cmbh_id = Column(UNIQUEIDENTIFIER, primary_key=True, server_default=text("(newid())"))
    cmbh_no = Column(Integer, nullable=False)
    sto_pk = Column(SmallInteger, nullable=False)
    cmbh_type = Column(CHAR(2, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("('D')"))
    cmbh_date = Column(DateTime, nullable=False)
    cmbh_status = Column(CHAR(1, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    usr_id = Column(UNIQUEIDENTIFIER, nullable=False)
    cmbh_check21 = Column(BIT, server_default=text("(0)"))
    cmbh_ck21proc = Column(CHAR(2, 'SQL_Latin1_General_CP1_CI_AS'))


class CMBKBank(Base):
    __tablename__ = 'CMBK_Bank'

    cmbk_id = Column(UNIQUEIDENTIFIER, primary_key=True, server_default=text("(newid())"))
    cmbk_transit = Column(String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, unique=True)
    cmbk_address1 = Column(String(50, 'SQL_Latin1_General_CP1_CI_AS'))
    cmbk_address2 = Column(String(25, 'SQL_Latin1_General_CP1_CI_AS'))
    cmbk_city = Column(String(50, 'SQL_Latin1_General_CP1_CI_AS'))
    cmbk_state = Column(CHAR(2, 'SQL_Latin1_General_CP1_CI_AS'))
    cmbk_zip = Column(CHAR(10, 'SQL_Latin1_General_CP1_CI_AS'))
    cmbk_ac = Column(CHAR(3, 'SQL_Latin1_General_CP1_CI_AS'))
    cmbk_phone = Column(String(20, 'SQL_Latin1_General_CP1_CI_AS'))
    cmbk_name = Column(String(50, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, index=True)


t_CMCAA_CustAuthAgent = Table(
    'CMCAA_CustAuthAgent', metadata,
    Column('cmcaa_id', UNIQUEIDENTIFIER, nullable=False, unique=True, server_default=text("(newid())")),
    Column('cus_id', UNIQUEIDENTIFIER, nullable=False),
    Column('cmcaa_agentcus_id', UNIQUEIDENTIFIER, nullable=False),
    Column('cmcaa_active', BIT)
)


class CMCBCHCashBoxCountHeader(Base):
    __tablename__ = 'CMCBCH_CashBoxCountHeader'

    CMCBCH_ID = Column(UNIQUEIDENTIFIER, primary_key=True, server_default=text("(newid())"))
    STO_PK = Column(SmallInteger, nullable=False)


class CMCBLUCashBoxLookupUnit(Base):
    __tablename__ = 'CMCBLU_CashBoxLookupUnit'

    CMCBLU_ID = Column(UNIQUEIDENTIFIER, primary_key=True, server_default=text("(newid())"))
    CMCBLU_Description = Column(String(50, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    CMCBLU_Unit = Column(MONEY, nullable=False)
    CMCBLU_Active = Column(BIT, nullable=False, server_default=text("(1)"))
    CMCBLU_Order = Column(Integer, nullable=False)
    CMCBLU_Locked = Column(BIT, nullable=False)
    CMCBLU_Lookup = Column(String(10, 'SQL_Latin1_General_CP1_CI_AS'))


class CMCBSCashBoxSlot(Base):
    __tablename__ = 'CMCBS_CashBoxSlot'
    __table_args__ = (
        Index('IX_CMCBS_cmst_type_active_id', 'CMST_ID', 'CMCBS_Type', 'CMCBS_Active', 'CMCBS_ID'),
        Index('IX_CMCBS_usr_type_active_id', 'USR_ID', 'CMCBS_Type', 'CMCBS_Active', 'CMCBS_ID')
    )

    CMCBS_ID = Column(UNIQUEIDENTIFIER, primary_key=True, server_default=text("(newid())"))
    CMLC_ID = Column(UNIQUEIDENTIFIER, nullable=False)
    CMCBS_Active = Column(BIT, nullable=False, server_default=text("(1)"))
    CMCBS_Type = Column(CHAR(2, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    CMCBS_Description = Column(String(50, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    USR_ID = Column(UNIQUEIDENTIFIER, nullable=False)
    STO_PK = Column(SmallInteger, nullable=False)
    CMST_ID = Column(UNIQUEIDENTIFIER)
    CMCBS_Printer = Column(String(100, 'SQL_Latin1_General_CP1_CI_AS'))


class CMCDTCashDrawerTransfer(Base):
    __tablename__ = 'CMCDT_CashDrawerTransfer'

    CMCDT_ID = Column(UNIQUEIDENTIFIER, primary_key=True, server_default=text("(newid())"))
    CMCDT_From_CMCD_ID = Column(UNIQUEIDENTIFIER, nullable=False, index=True)
    CMCDT_To_CMCD_ID = Column(UNIQUEIDENTIFIER, index=True)
    CMCDT_From_CMLC_ID = Column(UNIQUEIDENTIFIER, nullable=False, index=True)
    CMCDT_To_CMLC_ID = Column(UNIQUEIDENTIFIER, index=True)
    CMCDT_Date = Column(DateTime, nullable=False)
    CMCDT_Type = Column(CHAR(2, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    CMTN_ID = Column(UNIQUEIDENTIFIER)


class CMCDCashDrawer(Base):
    __tablename__ = 'CMCD_CashDrawer'
    __table_args__ = (
        Index('IX_CMCD_CashDrawer_STO_PK_CUS_ID', 'sto_pk', 'cmcd_date', 'cus_id'),
        Index('IDX_CMCD_CashDrawer_K5_K12_K7_K1_8', 'sto_pk', 'cmcbs_id', 'cmcd_date', 'cmcd_id'),
        Index('IX_CMCD_receipt_sto', 'cmcd_receipt', 'sto_pk'),
        Index('IDX_CMCD_CashDrawer_K1_K5_K11_K7_K10', 'cmcd_id', 'sto_pk', 'cus_id', 'cmcd_date', 'cmst_id'),
        Index('IDX_CMCD_CashDrawer_K1_K7', 'cmcd_id', 'cmcd_date')
    )

    cmcd_id = Column(UNIQUEIDENTIFIER, primary_key=True, server_default=text("(newid())"))
    cmcd_receipt = Column(Integer)
    cmcd_amount = Column(MONEY, nullable=False)
    sto_pk = Column(SmallInteger, nullable=False)
    cmcd_print_cknumber = Column(Integer)
    cmcd_date = Column(DateTime, nullable=False)
    usr_id = Column(UNIQUEIDENTIFIER, nullable=False)
    cmcd_print_ckreturned = Column(BIT, server_default=text("(0)"))
    cmst_id = Column(UNIQUEIDENTIFIER)
    cmcbs_id = Column(UNIQUEIDENTIFIER)
    cmck_id = Column(UNIQUEIDENTIFIER, index=True)
    cus_id = Column(UNIQUEIDENTIFIER)
    cmcd_credit = Column(MONEY, server_default=text("(0)"))


class CMCK21SCk21Send(Base):
    __tablename__ = 'CMCK21S_ck21Send'

    cmck21s_id = Column(UNIQUEIDENTIFIER, primary_key=True, server_default=text("(newid())"))
    cmbh_id = Column(UNIQUEIDENTIFIER, nullable=False, index=True)
    cmck21s_batchno = Column(Integer, nullable=False)
    sto_pk = Column(SmallInteger, nullable=False, index=True)


class CMCK21Check21(Base):
    __tablename__ = 'CMCK21_Check21'

    cmck21_id = Column(UNIQUEIDENTIFIER, primary_key=True, server_default=text("(newid())"))
    cmbd_id = Column(UNIQUEIDENTIFIER, nullable=False)
    cmck21_tranno = Column(Integer, nullable=False)
    sto_pk = Column(SmallInteger, nullable=False, index=True)


class CMCLVRCLVerifyResponse(Base):
    __tablename__ = 'CMCLVR_CLVerifyResponse'

    cmclvr_id = Column(UNIQUEIDENTIFIER, primary_key=True, server_default=text("(newid())"))
    cmtr_id = Column(UNIQUEIDENTIFIER)
    sto_pk = Column(SmallInteger, nullable=False)
    cus_id = Column(UNIQUEIDENTIFIER, nullable=False)
    usr_id = Column(UNIQUEIDENTIFIER, nullable=False)
    cmclvr_date = Column(DateTime, nullable=False)
    cmclvr_tran_id = Column(String(8, 'SQL_Latin1_General_CP1_CI_AS'))
    cmclvr_clv_id = Column(String(8, 'SQL_Latin1_General_CP1_CI_AS'))
    cmclvr_tran_link_id = Column(Text(2147483647, 'SQL_Latin1_General_CP1_CI_AS'))
    cmclvr_loannumber = Column(String(24, 'SQL_Latin1_General_CP1_CI_AS'))
    cmclvr_code = Column(String(6, 'SQL_Latin1_General_CP1_CI_AS'))
    cmclvr_desc = Column(String(128, 'SQL_Latin1_General_CP1_CI_AS'))
    cmclvr_score = Column(String(3, 'SQL_Latin1_General_CP1_CI_AS'))
    cmclvr_approval = Column(String(1, 'SQL_Latin1_General_CP1_CI_AS'))
    cmclvr_approvalamt = Column(MONEY)


class CMCLVTCLVerifyTransaction(Base):
    __tablename__ = 'CMCLVT_CLVerifyTransaction'

    cmclvt_ID = Column(UNIQUEIDENTIFIER, primary_key=True, unique=True, server_default=text("(newid())"))
    cmtr_id = Column(UNIQUEIDENTIFIER)
    cus_id = Column(UNIQUEIDENTIFIER, nullable=False)
    cmclvt_tran_id = Column(String(8, 'SQL_Latin1_General_CP1_CI_AS'))
    cmclvt_clv_id = Column(String(8, 'SQL_Latin1_General_CP1_CI_AS'))
    cmclvt_loannumber = Column(String(24, 'SQL_Latin1_General_CP1_CI_AS'))
    cmclvt_transaction = Column(String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    sto_pk = Column(SmallInteger, nullable=False)
    cmclvt_rtcharges = Column(MONEY, nullable=False)
    cmclvt_rtfees = Column(MONEY, nullable=False)
    cmclvt_fee1 = Column(MONEY, nullable=False)
    cmclvt_fee2 = Column(MONEY, nullable=False)
    cmclvt_status = Column(CHAR(2, 'SQL_Latin1_General_CP1_CI_AS'))
    cmclvt_orig_amount = Column(MONEY)
    cmclvt_loanrpt = Column(Text(2147483647, 'SQL_Latin1_General_CP1_CI_AS'))
    cmclvt_upload = Column(BIT)


t_CMCL_Collections = Table(
    'CMCL_Collections', metadata,
    Column('CMCL_ID', UNIQUEIDENTIFIER, nullable=False),
    Column('CUS_ID', UNIQUEIDENTIFIER, nullable=False, index=True),
    Column('STO_PK', SmallInteger, nullable=False),
    Column('CMTR_ID', UNIQUEIDENTIFIER),
    Column('CMCL_Emp_ID', UNIQUEIDENTIFIER),
    Column('CMCL_Letter', CHAR(10, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('CMCL_Status', CHAR(10, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('CMCL_Date', DateTime),
    Column('CMCL_Complete', BIT),
    Column('CMCL_Text', Text(2147483647, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('CMCL_Usradded', BIT)
)

t_CMCPT_CustPointsTables = Table(
    'CMCPT_CustPointsTables', metadata,
    Column('CMCPT_ID', UNIQUEIDENTIFIER, nullable=False),
    Column('Sto_pk', SmallInteger, nullable=False),
    Column('CMCPT_Type', CHAR(1, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CMCPT_Amount', MONEY, nullable=False),
    Column('CMCPT_Points', SmallInteger, nullable=False)
)


class CMCTNCashTypeNote(Base):
    __tablename__ = 'CMCTN_CashTypeNote'

    cmctn_id = Column(UNIQUEIDENTIFIER, primary_key=True, server_default=text("(newid())"))
    cmct_id = Column(UNIQUEIDENTIFIER, nullable=False, index=True)
    cmctn_note = Column(String(255, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)


class CMCUCust(Base):
    __tablename__ = 'CMCU_Cust'

    cmcu_id = Column(UNIQUEIDENTIFIER, primary_key=True, server_default=text("(newid())"))
    cus_ID = Column(UNIQUEIDENTIFIER, nullable=False, index=True)
    sto_pk = Column(SmallInteger, nullable=False)
    cmcu_maidenname = Column(String(25, 'SQL_Latin1_General_CP1_CI_AS'))
    cmcu_badcust = Column(BIT, server_default=text("(0)"))
    cmcu_paydate = Column(DateTime)
    cmcu_payfreq = Column(CHAR(1, 'SQL_Latin1_General_CP1_CI_AS'))
    cmcu_payrate = Column(Numeric(18, 0))
    cmcu_payratefreq = Column(CHAR(1, 'SQL_Latin1_General_CP1_CI_AS'))
    cmcu_directdeposit = Column(BIT, server_default=text("(0)"))
    cmcu_dba = Column(String(40, 'SQL_Latin1_General_CP1_CI_AS'), server_default=text("(null)"))
    cmcu_jobtitle = Column(String(30, 'SQL_Latin1_General_CP1_CI_AS'), server_default=text("(null)"))
    cmcu_bankruptcy = Column(BIT, server_default=text("(0)"))
    cmcu_garnishment = Column(BIT, server_default=text("(0)"))
    cmcu_ownhome = Column(BIT, server_default=text("(0)"))
    cmcu_points = Column(Integer, server_default=text("(0)"))
    cmcu_pointsavailable = Column(Integer, server_default=text("(0)"))
    cmcu_credit = Column(MONEY, server_default=text("(0)"))
    cmcu_pointsmailer = Column(BIT, server_default=text("(0)"))
    cmcu_pointtrans = Column(Integer, server_default=text("(0)"))
    cmcu_pointslast = Column(DateTime, server_default=text("(null)"))
    cmcu_taxexempt = Column(BIT, server_default=text("(0)"))


class CMDBADepositBankAccount(Base):
    __tablename__ = 'CMDBA_DepositBankAccount'

    CMDBA_ID = Column(UNIQUEIDENTIFIER, primary_key=True, server_default=text("(newid())"))
    CMBK_ID = Column(UNIQUEIDENTIFIER, nullable=False)
    STO_PK = Column(SmallInteger, nullable=False)
    CMDBA_Account = Column(String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    CMDBA_Account_Type = Column(CHAR(1, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    CMDBA_Active = Column(BIT, nullable=False)
    CMDBA_Description = Column(String(50, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    CMCBS_ID = Column(UNIQUEIDENTIFIER)
    cmdba_printendorse = Column(BIT, server_default=text("(0)"))
    cmdba_Check21 = Column(BIT)


class CMDLPDebitLoadProduct(Base):
    __tablename__ = 'CMDLP_DebitLoadProduct'

    cmdlp_id = Column(UNIQUEIDENTIFIER, primary_key=True, server_default=text("(newid())"))
    cmdlp_productno = Column(String(10, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    sto_pk = Column(SmallInteger, nullable=False)
    cmdlp_description = Column(String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    cmdlp_active = Column(BIT, nullable=False, server_default=text("(1)"))


class CMDVDevice(Base):
    __tablename__ = 'CMDV_Devices'

    CMDV_ID = Column(UNIQUEIDENTIFIER, primary_key=True, server_default=text("(newid())"))
    CMDV_Manufacturer = Column(CHAR(64, 'SQL_Latin1_General_CP1_CI_AS'))
    CMDV_ManufSupport = Column(CHAR(16, 'SQL_Latin1_General_CP1_CI_AS'))
    CMDV_ManufURL = Column(CHAR(128, 'SQL_Latin1_General_CP1_CI_AS'))
    CMDV_Model = Column(CHAR(64, 'SQL_Latin1_General_CP1_CI_AS'))
    CMDV_Type = Column(CHAR(32, 'SQL_Latin1_General_CP1_CI_AS'))
    CMDV_ExternalFile = Column(CHAR(32, 'SQL_Latin1_General_CP1_CI_AS'))
    CMDV_ExternalClass = Column(CHAR(32, 'SQL_Latin1_General_CP1_CI_AS'))
    CMDV_ExternalModule = Column(CHAR(32, 'SQL_Latin1_General_CP1_CI_AS'))
    CMDV_Timestamp = Column(BINARY(8))


t_CMEVS_IDENTIFICATION = Table(
    'CMEVS_IDENTIFICATION', metadata,
    Column('CMEVS_ID', UNIQUEIDENTIFIER, nullable=False),
    Column('CUS_ID', UNIQUEIDENTIFIER, nullable=False, index=True),
    Column('STO_PK', SmallInteger, nullable=False),
    Column('CMEVS_SEND', Text(2147483647, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('CMEVS_RECEIVE', Text(2147483647, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('CMEVS_DATE', DateTime)
)


class CMGLHHeader(Base):
    __tablename__ = 'CMGLH_Header'

    GLH_ID = Column(UNIQUEIDENTIFIER, primary_key=True, server_default=text("(newid())"))
    GLH_No = Column(Integer, nullable=False)
    STO_PK = Column(SmallInteger, nullable=False)
    BAT_ID = Column(UNIQUEIDENTIFIER)
    GLH_Date = Column(DateTime, nullable=False, server_default=text("(getdate())"))
    GLH_Reference = Column(String(200, 'SQL_Latin1_General_CP1_CI_AS'))
    GLH_Product = Column(CHAR(2, 'SQL_Latin1_General_CP1_CI_AS'), server_default=text("('CM')"))


class CMGLMAccountMask(Base):
    __tablename__ = 'CMGLM_AccountMask'

    GLM_ID = Column(UNIQUEIDENTIFIER, primary_key=True, server_default=text("(newid())"))
    GLM_NO = Column(Integer, nullable=False)
    GLM_Mask_NO = Column(TINYINT)
    GLM_Mask = Column(String(255, 'SQL_Latin1_General_CP1_CI_AS'))
    GLM_ExpInd = Column(BIT, server_default=text("(1)"))
    GLM_Length = Column(TINYINT, server_default=text("(0)"))


class CMGLTType(Base):
    __tablename__ = 'CMGLT_Type'

    GLT_ID = Column(UNIQUEIDENTIFIER, primary_key=True, server_default=text("(newid())"))
    GLT_No = Column(Integer, nullable=False)
    GLT_Type = Column(CHAR(25, 'SQL_Latin1_General_CP1_CI_AS'))
    GLT_Prompt = Column(String(200, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    GLT_Status = Column(BIT, nullable=False, server_default=text("(1)"))
    GLT_AcctType = Column(CHAR(1, 'SQL_Latin1_General_CP1_CI_AS'))
    GLT_Group = Column(CHAR(2, 'SQL_Latin1_General_CP1_CI_AS'))
    GLT_SortOrder = Column(Integer, server_default=text("(0)"))
    glt_cash_sto_pk = Column(SmallInteger)
    glt_Product = Column(CHAR(2, 'SQL_Latin1_General_CP1_CI_AS'), server_default=text("('PM')"))


class CMIBInvBrand(Base):
    __tablename__ = 'CMIB_InvBrand'

    CMIB_ID = Column(UNIQUEIDENTIFIER, primary_key=True)
    CMIB_Description = Column(String(50, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    CMIT_ID = Column(UNIQUEIDENTIFIER)
    CMIB_Active = Column(BIT, nullable=False, server_default=text("(1)"))


class CMILDNItemLotDamagedNote(Base):
    __tablename__ = 'CMILDN_ItemLotDamagedNote'

    CMILDN_ID = Column(UNIQUEIDENTIFIER, primary_key=True, server_default=text("(newid())"))
    STO_PK = Column(SmallInteger, nullable=False)
    CMILD_Note = Column(String(250, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)


class CMILUInvLookupUnit(Base):
    __tablename__ = 'CMILU_InvLookupUnit'

    CMILU_ID = Column(UNIQUEIDENTIFIER, primary_key=True)
    CMILU_Description = Column(String(50, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    CMILU_Unit = Column(Integer, nullable=False)
    CMILU_Active = Column(BIT, nullable=False)
    CMILU_Locked = Column(BIT, nullable=False)


class CMIPHInvPackageHeader(Base):
    __tablename__ = 'CMIPH_InvPackageHeader'
    __table_args__ = (
        Index('IDX_CMIPH_InvPackageHeader_K7_K1_K3', 'CMIPH_Type', 'CMIPH_ID', 'CMIPH_Description'),
        Index('IDX_CMIPH_InvPackageHeader_K7_K1', 'CMIPH_Type', 'CMIPH_ID')
    )

    CMIPH_ID = Column(UNIQUEIDENTIFIER, primary_key=True)
    STO_PK = Column(SmallInteger, nullable=False)
    CMIPH_Description = Column(String(50, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    CMIPH_RetailPrice = Column(MONEY, nullable=False)
    CMIPH_Exempt = Column(BIT, nullable=False)
    CMIPH_Active = Column(BIT, nullable=False)
    CMIPH_Type = Column(CHAR(2, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("('IT')"))
    cmiph_order = Column(Integer, server_default=text("(0)"))
    cmiph_color = Column(Integer, server_default=text("(16777215)"))
    CMIPH_Volume = Column(BIT, server_default=text("(0)"))
    CMIPH_VolBuy = Column(SmallInteger, server_default=text("(0)"))
    CMIPH_VolGet = Column(SmallInteger, server_default=text("(1)"))
    CMIPH_VolDiscount = Column(Numeric(9, 4), server_default=text("(0)"))
    CMIPH_VolLimit = Column(SmallInteger, server_default=text("(0)"))


class CMITSInvTypeSetup(Base):
    __tablename__ = 'CMITS_InvTypeSetup'

    CMITS_ID = Column(UNIQUEIDENTIFIER, primary_key=True)
    STO_PK = Column(SmallInteger, nullable=False)
    CMITS_Description = Column(String(50, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    CMITS_CMITS_ID = Column(ForeignKey('CMITS_InvTypeSetup.CMITS_ID'))
    CMITS_Required = Column(BIT, server_default=text("(0)"))

    parent = relationship('CMITSInvTypeSetup', remote_side=[CMITS_ID])


class CMITTInvTypeTime(Base):
    __tablename__ = 'CMITT_InvTypeTime'
    __table_args__ = (
        Index('IX_CMITT_Desc', 'CMITT_desc', 'sto_pk'),
    )

    CMITT_id = Column(UNIQUEIDENTIFIER, primary_key=True)
    CMITT_desc = Column(String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    sto_pk = Column(SmallInteger, nullable=False)
    CMITT_active = Column(BIT, nullable=False)
    Day1From1 = Column(SmallInteger, nullable=False)
    Day1To1 = Column(SmallInteger, nullable=False)
    Day1From2 = Column(SmallInteger, nullable=False)
    Day1To2 = Column(SmallInteger, nullable=False)
    Day2From1 = Column(SmallInteger, nullable=False)
    Day2To1 = Column(SmallInteger, nullable=False)
    Day2From2 = Column(SmallInteger, nullable=False)
    Day2To2 = Column(SmallInteger, nullable=False)
    Day3From1 = Column(SmallInteger, nullable=False)
    Day3To1 = Column(SmallInteger, nullable=False)
    Day3From2 = Column(SmallInteger, nullable=False)
    Day3To2 = Column(SmallInteger, nullable=False)
    Day4From1 = Column(SmallInteger, nullable=False)
    Day4To1 = Column(SmallInteger, nullable=False)
    Day4From2 = Column(SmallInteger, nullable=False)
    Day4To2 = Column(SmallInteger, nullable=False)
    Day5From1 = Column(SmallInteger, nullable=False)
    Day5To1 = Column(SmallInteger, nullable=False)
    Day5From2 = Column(SmallInteger, nullable=False)
    Day5To2 = Column(SmallInteger, nullable=False)
    Day6From1 = Column(SmallInteger, nullable=False)
    Day6To1 = Column(SmallInteger, nullable=False)
    Day6From2 = Column(SmallInteger, nullable=False)
    Day6To2 = Column(SmallInteger, nullable=False)
    Day7From1 = Column(SmallInteger, nullable=False)
    Day7To1 = Column(SmallInteger, nullable=False)
    Day7From2 = Column(SmallInteger, nullable=False)
    Day7To2 = Column(SmallInteger, nullable=False)


class CMLBLookupB(Base):
    __tablename__ = 'CMLB_Lookup_B'

    cmlb_id = Column(UNIQUEIDENTIFIER, primary_key=True, unique=True, server_default=text("(newid())"))
    cmlb_descript = Column(String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, index=True)
    cmlb_update = Column(BIT, nullable=False, server_default=text("(0)"))
    cmlb_replace = Column(BIT, nullable=False, server_default=text("(0)"))
    cmlb_add = Column(BIT, nullable=False, server_default=text("(0)"))
    cmlb_delete = Column(BIT, nullable=False, server_default=text("(0)"))


class CMLCLookupC(Base):
    __tablename__ = 'CMLC_Lookup_C'

    cmlc_id = Column(UNIQUEIDENTIFIER, primary_key=True, unique=True, server_default=text("(newid())"))
    cmlb_id = Column(UNIQUEIDENTIFIER, nullable=False, index=True)
    cmlc_Long_Description = Column(String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    cmlc_active = Column(BIT, server_default=text("(1)"))
    cmlc_Short_Description = Column(CHAR(12, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    cmlc_lookup = Column(CHAR(10, 'SQL_Latin1_General_CP1_CI_AS'), index=True)
    cmlc_locked = Column(BIT, nullable=False, server_default=text("(1)"))
    cmlc_order = Column(SmallInteger, nullable=False, server_default=text("(0)"))
    cmlc_color = Column(Integer)


class CMLRLoanSafeResponse(Base):
    __tablename__ = 'CMLR_LoanSafeResponse'

    CMLR_ID = Column(UNIQUEIDENTIFIER, primary_key=True, server_default=text("(newid())"))
    Sto_PK = Column(SmallInteger, nullable=False)
    CMTR_ID = Column(UNIQUEIDENTIFIER, nullable=False)
    Usr_ID = Column(UNIQUEIDENTIFIER, nullable=False)
    CMLR_Date = Column(DateTime, nullable=False)
    CMLR_ResponseCode = Column(String(6, 'SQL_Latin1_General_CP1_CI_AS'))
    CMLR_ResponseText = Column(String(25, 'SQL_Latin1_General_CP1_CI_AS'))


t_CMLTR_Letters = Table(
    'CMLTR_Letters', metadata,
    Column('CMLTR_ID', UNIQUEIDENTIFIER, nullable=False),
    Column('STO_PK', SmallInteger, nullable=False),
    Column('CMLTR_Name', CHAR(10, 'SQL_Latin1_General_CP1_CI_AS'), index=True),
    Column('CMLTR_Letter', Text(2147483647, 'SQL_Latin1_General_CP1_CI_AS'))
)


class CMLTLoanSafeTransaction(Base):
    __tablename__ = 'CMLT_LoanSafeTransaction'

    CMLT_ID = Column(UNIQUEIDENTIFIER, primary_key=True, server_default=text("(newid())"))
    Sto_PK = Column(SmallInteger, nullable=False)
    Cus_ID = Column(UNIQUEIDENTIFIER, nullable=False)
    CMLT_LSNumber = Column(String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    CMLT_LSRetSeed = Column(String(20, 'SQL_Latin1_General_CP1_CI_AS'))


class CMMAMessageArea(Base):
    __tablename__ = 'CMMA_MessageArea'

    CMMA_ID = Column(UNIQUEIDENTIFIER, primary_key=True, server_default=text("(newid())"))
    CMMA_Description = Column(CHAR(10, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)


class CMMIMenuItem(Base):
    __tablename__ = 'CMMI_MenuItems'

    cmmi_id = Column(UNIQUEIDENTIFIER, primary_key=True, server_default=text("(newid())"))
    cmmi_number = Column(SmallInteger, nullable=False)
    cmmi_cmmi_number = Column(SmallInteger, nullable=False)
    cmmi_pad = Column(SmallInteger, nullable=False)
    cmmi_level = Column(SmallInteger, nullable=False)
    cmmi_bar = Column(SmallInteger, nullable=False)
    cmmi_descript = Column(String(40, 'SQL_Latin1_General_CP1_CI_AS'))
    cmmi_allowchange = Column(BIT, nullable=False)
    cmmi_editvisible = Column(BIT, nullable=False)


class CMPYPayor(Base):
    __tablename__ = 'CMPY_Payor'

    cmpy_id = Column(UNIQUEIDENTIFIER, primary_key=True, index=True, server_default=text("(newid())"))
    sto_pk = Column(SmallInteger, nullable=False, index=True)
    cus_id = Column(UNIQUEIDENTIFIER, index=True)
    cmpy_name = Column(String(35, 'SQL_Latin1_General_CP1_CI_AS'))
    cmpy_address1 = Column(String(25, 'SQL_Latin1_General_CP1_CI_AS'))
    cmpy_address2 = Column(String(25, 'SQL_Latin1_General_CP1_CI_AS'))
    cmpy_city = Column(String(50, 'SQL_Latin1_General_CP1_CI_AS'))
    cmpy_state = Column(CHAR(2, 'SQL_Latin1_General_CP1_CI_AS'))
    cmpy_zip = Column(CHAR(10, 'SQL_Latin1_General_CP1_CI_AS'))
    cmpy_entered = Column(DateTime)
    cmpy_badpayor = Column(BIT, server_default=text("(0)"))
    cmpy_min = Column(MONEY)
    cmpy_max = Column(MONEY)
    cmpy_ac = Column(CHAR(3, 'SQL_Latin1_General_CP1_CI_AS'))
    cmpy_phone = Column(String(20, 'SQL_Latin1_General_CP1_CI_AS'))
    cmpy_patriotact = Column(BIT)


class CMRFReference(Base):
    __tablename__ = 'CMRF_Reference'

    cmrf_id = Column(UNIQUEIDENTIFIER, primary_key=True, server_default=text("(newid())"))
    cus_id = Column(UNIQUEIDENTIFIER, nullable=False, index=True)
    cmrf_Name = Column(String(60, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    cmrf_Phone = Column(String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)


class CMRHRatesHeader(Base):
    __tablename__ = 'CMRH_RatesHeader'

    cmrh_id = Column(UNIQUEIDENTIFIER, primary_key=True, index=True, server_default=text("(newid())"))
    cmrh_descript = Column(String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    cmrh_printdescript = Column(String(10, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    sto_pk = Column(SmallInteger, nullable=False)
    cmrh_active = Column(BIT, nullable=False, server_default=text("(1)"))
    cmdba_id = Column(UNIQUEIDENTIFIER)


class CMRLRepolist(Base):
    __tablename__ = 'CMRL_Repolist'

    CMRL_ID = Column(UNIQUEIDENTIFIER, primary_key=True, unique=True, server_default=text("(newid())"))
    CMRL_ReportKey = Column(Integer, nullable=False, server_default=text("(1)"))
    CMRL_CustKey = Column(CHAR(10, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("('DA0000')"))
    CMRL_cType = Column(CHAR(25, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, index=True,
                        server_default=text("('')"))
    CMRL_defmenuacc = Column(Integer, nullable=False, server_default=text("(6)"))
    CMRL_cFullname = Column(CHAR(50, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("('')"))
    CMRL_cFilename = Column(CHAR(25, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("('')"))
    CMRL_HasTotals = Column(BIT, nullable=False, server_default=text("(1)"))
    CMRL_prt_prev = Column(BIT, nullable=False, server_default=text("(1)"))
    CMRL_Start = Column(Text(2147483647, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("('')"))
    CMRL_CompStart = Column(Text(2147483647, 'SQL_Latin1_General_CP1_CI_AS'))
    CMRL_Status = Column(CHAR(1, 'SQL_Latin1_General_CP1_CI_AS'))


t_CMSC_SysColumn = Table(
    'CMSC_SysColumn', metadata,
    Column('CMSC_ID', UNIQUEIDENTIFIER, nullable=False, server_default=text("(newid())")),
    Column('CMSC_Sort', SmallInteger, nullable=False, server_default=text("(0)")),
    Column('CMSC_Name', String(50, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("('')")),
    Column('CMSC_Parent', UNIQUEIDENTIFIER),
    Column('CMSC_Page', SmallInteger, server_default=text("(1)"))
)


class CMSTStation(Base):
    __tablename__ = 'CMST_Station'

    cmst_id = Column(UNIQUEIDENTIFIER, primary_key=True, server_default=text("(newid())"))
    sto_pk = Column(SmallInteger, nullable=False)
    cmst_number = Column(SmallInteger, nullable=False)


class CMSYSysInfo(Base):
    __tablename__ = 'CMSY_SysInfo'

    cmsy_id = Column(UNIQUEIDENTIFIER, primary_key=True, unique=True, server_default=text("(newid())"))
    cmsy_name = Column(String(50, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, index=True)
    cmsy_value = Column(String(254, 'SQL_Latin1_General_CP1_CI_AS'))
    sto_pk = Column(SmallInteger)
    cmsy_encrypt = Column(BIT)


t_CMTCC_TenderCC = Table(
    'CMTCC_TenderCC', metadata,
    Column('CMTCC_ID', UNIQUEIDENTIFIER, nullable=False, server_default=text("(newid())")),
    Column('CMLC_ID', UNIQUEIDENTIFIER, nullable=False),
    Column('CMTCC_IsCC', BIT, nullable=False, server_default=text("(0)"))
)


class CMTDTeletrackDisplay(Base):
    __tablename__ = 'CMTD_TeletrackDisplay'

    cmtd_id = Column(UNIQUEIDENTIFIER, primary_key=True, server_default=text("(newid())"))
    sto_pk = Column(SmallInteger, nullable=False, index=True)
    cmtl_id = Column(UNIQUEIDENTIFIER, nullable=False)
    cmtd_order = Column(Integer, nullable=False)


class CMTHGLHTranHistoryGLHeader(Base):
    __tablename__ = 'CMTHGLH_TranHistoryGLHeader'

    CMTHGLH_ID = Column(UNIQUEIDENTIFIER, primary_key=True, server_default=text("(newid())"))
    GLH_ID = Column(UNIQUEIDENTIFIER, nullable=False, index=True)
    CMTH_ID = Column(UNIQUEIDENTIFIER, nullable=False, index=True)


class CMTHSTranHistorySale(Base):
    __tablename__ = 'CMTHS_TranHistorySale'

    cmths_id = Column(UNIQUEIDENTIFIER, primary_key=True, server_default=text("(newid())"))
    cmtr_id = Column(UNIQUEIDENTIFIER, nullable=False, index=True)
    sld_id = Column(UNIQUEIDENTIFIER, nullable=False, index=True)
    sto_pk = Column(SmallInteger, nullable=False)


class CMTLTeletrackLayout(Base):
    __tablename__ = 'CMTL_TeletrackLayout'

    cmtl_id = Column(UNIQUEIDENTIFIER, primary_key=True, server_default=text("(newid())"))
    cmtl_property = Column(String(254, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    cmtl_label = Column(String(254, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    cmtl_segment_name = Column(String(254, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, index=True)


class CMTNNote(Base):
    __tablename__ = 'CMTN_Note'

    CMTN_ID = Column(UNIQUEIDENTIFIER, primary_key=True, server_default=text("(newid())"))
    CMTR_ID = Column(UNIQUEIDENTIFIER, index=True)
    CMTH_ID = Column(UNIQUEIDENTIFIER, index=True)
    Sto_PK = Column(SmallInteger, nullable=False, server_default=text("(0)"))
    Usr_ID = Column(UNIQUEIDENTIFIER, nullable=False)
    cus_id = Column(UNIQUEIDENTIFIER, nullable=False, index=True)
    cmtn_type = Column(String(50, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    cmtn_date = Column(DateTime, nullable=False)
    cmtn_note = Column(String(250, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)


class CMTRTransaction(Base):
    __tablename__ = 'CMTR_Transaction'
    __table_args__ = (
        Index('IDX_CMTR_Transaction_K1_K7_K6_K4_K2_K5', 'cmtr_id', 'cmtr_status', 'cmtr_date', 'sto_pk', 'cus_id',
              'cmtr_Type'),
        Index('IX_CMTR_Transaction_Composite', 'cus_id', 'sto_pk', 'cmtr_date', 'cmtr_status'),
        Index('IDX_CMTR_Transaction_K4_K6_K7_K5_K2_K1', 'sto_pk', 'cmtr_date', 'cmtr_status', 'cmtr_Type', 'cus_id',
              'cmtr_id'),
        Index('IDX_CMTR_Transaction_K4_K5_K1_K2_K7_K6', 'sto_pk', 'cmtr_Type', 'cmtr_id', 'cus_id', 'cmtr_status',
              'cmtr_date'),
        Index('IDX_CMTR_Transaction_K4_K1', 'sto_pk', 'cmtr_id'),
        Index('IDX_CMTR_Transaction_K1_K6_K4_K2_K7_K3', 'cmtr_id', 'cmtr_date', 'sto_pk', 'cus_id', 'cmtr_status',
              'usr_ID'),
        Index('IDX_CMTR_Transaction_K1_K2', 'cmtr_id', 'cus_id'),
        Index('IX_CMTR_Transaction_CMTR_ID_CMTR_Status', 'cmtr_id', 'cmtr_status')
    )

    cmtr_id = Column(UNIQUEIDENTIFIER, primary_key=True, server_default=text("(newid())"))
    cus_id = Column(UNIQUEIDENTIFIER, nullable=False, index=True)
    usr_ID = Column(UNIQUEIDENTIFIER, nullable=False)
    sto_pk = Column(SmallInteger, nullable=False)
    cmtr_Type = Column(CHAR(10, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, index=True)
    cmtr_date = Column(DateTime, nullable=False)
    cmtr_status = Column(CHAR(2, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    cmlc_id = Column(UNIQUEIDENTIFIER)


class CMTSDLTransSaleDetailLot(Base):
    __tablename__ = 'CMTSDL_TransSaleDetailLot'

    CMTSDL_ID = Column(UNIQUEIDENTIFIER, primary_key=True)
    CMTSD_ID = Column(UNIQUEIDENTIFIER, index=True)
    STO_PK = Column(SmallInteger, nullable=False)
    CMIL_ID = Column(UNIQUEIDENTIFIER, index=True)
    CMTSDL_Quantity = Column(Integer, nullable=False)
    CMI_ID = Column(UNIQUEIDENTIFIER, nullable=False, index=True)
    CMTSDL_RetailPrice = Column(MONEY, server_default=text("(0)"))


class CMTSHTransSaleHeader(Base):
    __tablename__ = 'CMTSH_TransSaleHeader'

    CMTSH_ID = Column(UNIQUEIDENTIFIER, primary_key=True, index=True)
    CMTR_ID = Column(UNIQUEIDENTIFIER, nullable=False, index=True)
    STO_PK = Column(SmallInteger, nullable=False)
    CMTSH_Discount = Column(Numeric(9, 4), nullable=False,
                            server_default=text("CREATE DEFAULT dbo.UW_ZeroDefault AS 0"))
    CMTSH_Usr_ID = Column(UNIQUEIDENTIFIER)
    CMTSH_EatTax = Column(BIT)
    cmtsh_return = Column(BIT)


class CMUHUserHistory(Base):
    __tablename__ = 'CMUH_UserHistory'
    __table_args__ = (
        Index('IX_CMUH_UserHistory_cmuh_type', 'cmuh_type', 'sto_pk'),
    )

    cmuh_id = Column(UNIQUEIDENTIFIER, primary_key=True, server_default=text("(newid())"))
    usr_id = Column(UNIQUEIDENTIFIER, nullable=False, index=True)
    sto_pk = Column(SmallInteger, nullable=False)
    cmuh_tablename = Column(String(200, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    cmuh_tableid = Column(UNIQUEIDENTIFIER, nullable=False)
    cmuh_date = Column(DateTime, nullable=False)
    cmuh_comment = Column(String(200, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    cmuh_type = Column(String(50, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("('')"))


class CMVNVendor(Base):
    __tablename__ = 'CMVN_Vendor'

    CMVN_ID = Column(UNIQUEIDENTIFIER, primary_key=True, server_default=text("(newid())"))
    CMVN_Company = Column(String(50, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    CMVN_Address = Column(String(50, 'SQL_Latin1_General_CP1_CI_AS'))
    CMVN_City = Column(String(20, 'SQL_Latin1_General_CP1_CI_AS'))
    CMVN_State = Column(String(3, 'SQL_Latin1_General_CP1_CI_AS'))
    CMVN_Zip = Column(String(10, 'SQL_Latin1_General_CP1_CI_AS'))
    CMVN_Contact = Column(String(25, 'SQL_Latin1_General_CP1_CI_AS'))
    CMVN_AC1 = Column(String(3, 'SQL_Latin1_General_CP1_CI_AS'))
    CMVN_Phone = Column(String(8, 'SQL_Latin1_General_CP1_CI_AS'))
    CMVN_AC2 = Column(String(3, 'SQL_Latin1_General_CP1_CI_AS'))
    CMVN_Fax = Column(String(8, 'SQL_Latin1_General_CP1_CI_AS'))
    CMVN_Email = Column(String(50, 'SQL_Latin1_General_CP1_CI_AS'))
    CMVN_Active = Column(BIT, nullable=False, server_default=text("(1)"))


class CMVRVeritecResponse(Base):
    __tablename__ = 'CMVR_VeritecResponse'

    cmvr_id = Column(UNIQUEIDENTIFIER, primary_key=True, server_default=text("(newid())"))
    cmtr_id = Column(UNIQUEIDENTIFIER)
    sto_pk = Column(SmallInteger, nullable=False)
    usr_id = Column(UNIQUEIDENTIFIER, nullable=False)
    cmvr_date = Column(DateTime, nullable=False)
    cmvr_actioncode = Column(String(20, 'SQL_Latin1_General_CP1_CI_AS'))
    cmvr_responsecode = Column(String(20, 'SQL_Latin1_General_CP1_CI_AS'))
    cmvr_responseother = Column(String(20, 'SQL_Latin1_General_CP1_CI_AS'))
    cmvr_responsedescription = Column(String(250, 'SQL_Latin1_General_CP1_CI_AS'))


class CMVTVeritecTransaction(Base):
    __tablename__ = 'CMVT_VeritecTransaction'

    CMVT_ID = Column(UNIQUEIDENTIFIER, primary_key=True, unique=True, server_default=text("(newid())"))
    cus_id = Column(UNIQUEIDENTIFIER, nullable=False, index=True)
    cmvt_vrnumber = Column(String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    sto_pk = Column(SmallInteger, nullable=False)
    cmvt_rtcharges = Column(MONEY, nullable=False)
    cmvt_rtfees = Column(MONEY, nullable=False)
    cmvt_fee1 = Column(MONEY, nullable=False)
    cmvt_fee2 = Column(MONEY, nullable=False)
    cmvt_status = Column(CHAR(2, 'SQL_Latin1_General_CP1_CI_AS'))
    cmvt_send = Column(Text(2147483647, 'SQL_Latin1_General_CP1_CI_AS'))
    cmvt_date = Column(DateTime)


class CMVXVeritecXPayPlan(Base):
    __tablename__ = 'CMVX_VeritecXPayPlan'

    CMVX_ID = Column(UNIQUEIDENTIFIER, primary_key=True, index=True, server_default=text("(newid())"))
    CMVT_ID = Column(UNIQUEIDENTIFIER, nullable=False)
    CMVX_Term = Column(Integer, nullable=False, server_default=text("(0)"))
    CMVX_Payments = Column(Integer, nullable=False)
    CMVX_StartDate = Column(DateTime, nullable=False)
    CMVX_EndDate = Column(DateTime, nullable=False)
    CMVX_Total = Column(MONEY, nullable=False, server_default=text("(0)"))


t_CM_AdvanceView = Table(
    'CM_AdvanceView', metadata,
    Column('sto_pk', SmallInteger, nullable=False),
    Column('Type', CHAR(10, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('DATE', DateTime, nullable=False),
    Column('status', CHAR(2, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('ticketnumber', Integer, nullable=False),
    Column('numberofday', SmallInteger, nullable=False),
    Column('datein', DateTime, nullable=False),
    Column('dateout', DateTime, nullable=False),
    Column('amount', MONEY, nullable=False),
    Column('paidtodate', DateTime, nullable=False),
    Column('floatamount', MONEY, nullable=False),
    Column('additionalcharge', MONEY, nullable=False),
    Column('additionalfee', MONEY, nullable=False),
    Column('monthlycharge', BIT, nullable=False),
    Column('reminder', DateTime),
    Column('USR_ID', UNIQUEIDENTIFIER, nullable=False),
    Column('cmvr_number', String(20, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('ckdate', DateTime, nullable=False),
    Column('ckamount', MONEY, nullable=False),
    Column('cknumber', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('Account', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('account_type', CHAR(1, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('routing', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('bank_address1', String(50, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('bank_address2', String(25, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('bank_city', String(50, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('bank_state', CHAR(2, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('bank_zip', CHAR(10, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('bank_phone', CHAR(3, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('bank_name', String(50, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('Emp', String(8, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CMCU_maidenname', String(25, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('cmcu_badcust', BIT),
    Column('cmcu_paydate', DateTime),
    Column('cmcu_payrate', Numeric(18, 0)),
    Column('cmcu_payfreq', CHAR(1, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('cmtr_id', UNIQUEIDENTIFIER, nullable=False),
    Column('cmta_id', UNIQUEIDENTIFIER, nullable=False),
    Column('cmrh_id', UNIQUEIDENTIFIER, nullable=False),
    Column('cmck_id', UNIQUEIDENTIFIER, nullable=False),
    Column('cmbk_id', UNIQUEIDENTIFIER, nullable=False),
    Column('cmvt_id', UNIQUEIDENTIFIER),
    Column('payor_cus_id', UNIQUEIDENTIFIER),
    Column('Payor_Name', String(41, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('payor_address1', String(25, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('payor_address2', String(25, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('payor_city', String(50, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('payor_state', CHAR(2, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('payor_zip', CHAR(10, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('payor_ac', CHAR(3, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('payor_phone', String(20, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('payor_entered', DateTime),
    Column('payor_badpayor', BIT),
    Column('payor_min', MONEY),
    Column('payor_max', MONEY),
    Column('maidenname', String(25, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('badcust', BIT),
    Column('hair', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('eyes', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('race', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('ID1Type', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('ID2Type', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('Cus_Store', Integer, nullable=False),
    Column('Cus_PK', Integer, nullable=False),
    Column('CUS_FNAME', String(15, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_MNAME', String(15, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_LNAME', String(25, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_ADD1', String(25, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_ADD2', String(25, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_CITY', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_STATE', String(2, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_ZIP', String(10, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_COUNTRY', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_AC1', String(3, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_PHONE1', String(8, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_HEIGHT', String(6, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_WEIGHT', SmallInteger, nullable=False),
    Column('CUS_HAIRFK', Integer, nullable=False),
    Column('CUS_RACEFK', Integer, nullable=False),
    Column('CUS_EYESFK', Integer, nullable=False),
    Column('CUS_SEX', String(1, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_MARKS', String(40, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_BIRTHDate', SMALLDATETIME),
    Column('CUS_BIRTHCITY', String(15, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_BIRTHSTATE', String(2, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_BIRTH2', String(15, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_IDTYP1', Integer, nullable=False),
    Column('CUS_IDNUM1', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_ID1EXP', SMALLDATETIME),
    Column('CUS_ID1ISSUE', String(50, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_IDTYP2', Integer, nullable=False),
    Column('CUS_IDNUM2', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_ID2EXP', SMALLDATETIME),
    Column('CUS_ID2ISSUE', String(2, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_KNOWN', BIT, nullable=False),
    Column('CUS_SSNUM', String(11, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_VEHIC1', String(10, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_VEHIC2', String(8, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_VEHIC3', String(2, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_EMPLOYER', String(40, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_EMPAD2', String(35, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_EMPAD1', String(35, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_EMPCITY', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_EMPSTATE', String(2, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_EMPZIP', String(10, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_AC2', String(3, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_EMPPHONE', String(14, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_COMMENT', String(200, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_TOTALPAWNS', Integer, nullable=False),
    Column('CUS_ACTIVEPAWN', Integer, nullable=False),
    Column('CUS_REDEEMED', Integer, nullable=False),
    Column('CUS_BUYS', Integer, nullable=False),
    Column('CUS_SALES', MONEY, nullable=False),
    Column('CUS_AMT1', MONEY, nullable=False),
    Column('CUS_AMT2', MONEY, nullable=False),
    Column('CUS_FFLNUM', String(25, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_DELETE', BIT, nullable=False),
    Column('CUS_LOCKED', BIT, nullable=False),
    Column('CUS_PAWNER', BIT, nullable=False),
    Column('CUS_BUYER', BIT, nullable=False),
    Column('CUS_IDADD1', String(25, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_IDADD2', String(25, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_IDCITY', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_IDSTATE', String(2, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_IDZIP', String(10, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_CREDIT', MONEY, nullable=False),
    Column('CUS_SPECIAL', Integer, nullable=False),
    Column('CUS_PIC_FK', Integer, nullable=False),
    Column('cus_Thum_fk', Integer, nullable=False),
    Column('CUS_Action_Spec', CHAR(1, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('Cus_ID', UNIQUEIDENTIFIER),
    Column('Cus_PatriotAct', BIT),
    Column('Cus_PointsPawnBuy', Integer, nullable=False),
    Column('Cus_PointsSale', Integer, nullable=False),
    Column('Cus_PointsAvail', Integer, nullable=False),
    Column('Cus_PointsMailer', BIT, nullable=False),
    Column('Cus_TaxID', String(25, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('Cus_CellPhone', String(20, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('Cus_Email', String(254, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('Cus_Entered', DateTime),
    Column('cus_military', BIT)
)

t_CM_CMPY_PayorView = Table(
    'CM_CMPY_PayorView', metadata,
    Column('cmpy_id', UNIQUEIDENTIFIER, nullable=False),
    Column('sto_pk', SmallInteger, nullable=False),
    Column('cus_id', UNIQUEIDENTIFIER),
    Column('payor_name', String(41, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('payor_address1', String(25, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('payor_address2', String(25, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('payor_city', String(50, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('payor_state', CHAR(2, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('payor_zip', CHAR(10, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('payor_entered', DateTime),
    Column('payor_badpayor', BIT),
    Column('payor_min', MONEY),
    Column('payor_max', MONEY),
    Column('payor_ac', CHAR(3, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('payor_phone', String(20, 'SQL_Latin1_General_CP1_CI_AS'))
)

t_CM_CMTH_DrawerView = Table(
    'CM_CMTH_DrawerView', metadata,
    Column('receipt', Integer),
    Column('tran_type', CHAR(10, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('tran_date', DateTime, nullable=False),
    Column('Amount', MONEY, nullable=False),
    Column('OverRideAmount', MONEY, nullable=False),
    Column('sto_pk', SmallInteger, nullable=False),
    Column('emp', String(8, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('cus_id', UNIQUEIDENTIFIER),
    Column('Long_Description', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('Short_Description', CHAR(12, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('lookup', CHAR(10, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('cmcd_id', UNIQUEIDENTIFIER, nullable=False),
    Column('CMTH_ID', UNIQUEIDENTIFIER, nullable=False),
    Column('CMTR_ID', UNIQUEIDENTIFIER, nullable=False),
    Column('Profit_Usr_id', UNIQUEIDENTIFIER, nullable=False)
)

t_CM_CheckView = Table(
    'CM_CheckView', metadata,
    Column('sto_pk', SmallInteger, nullable=False),
    Column('Type', CHAR(10, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('DATE', DateTime, nullable=False),
    Column('status', CHAR(2, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('fee', MONEY),
    Column('calcfee', MONEY),
    Column('ckdate', DateTime, nullable=False),
    Column('ckamount', MONEY, nullable=False),
    Column('cknumber', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('Account', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('account_type', CHAR(1, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('routing', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('bank_address1', String(50, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('bank_address2', String(25, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('bank_city', String(50, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('bank_state', CHAR(2, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('bank_zip', CHAR(10, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('bank_phone', CHAR(3, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('bank_name', String(50, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('Emp', String(8, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('cmpy_id', UNIQUEIDENTIFIER, nullable=False),
    Column('payor_cus_id', UNIQUEIDENTIFIER),
    Column('payor_name', String(41, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('payor_address1', String(25, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('payor_address2', String(25, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('payor_city', String(50, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('payor_state', CHAR(2, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('payor_zip', CHAR(10, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('payor_entered', DateTime),
    Column('payor_badpayor', BIT),
    Column('payor_min', MONEY),
    Column('payor_max', MONEY),
    Column('payor_ac', CHAR(3, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('payor_phone', String(20, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('maidenname', String(25, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('badcust', BIT),
    Column('hair', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('eyes', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('race', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('ID1Type', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('ID2Type', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('Cus_Store', Integer, nullable=False),
    Column('Cus_PK', Integer, nullable=False),
    Column('CUS_FNAME', String(15, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_MNAME', String(15, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_LNAME', String(25, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_ADD1', String(25, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_ADD2', String(25, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_CITY', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_STATE', String(2, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_ZIP', String(10, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_COUNTRY', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_AC1', String(3, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_PHONE1', String(8, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_HEIGHT', String(6, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_WEIGHT', SmallInteger, nullable=False),
    Column('CUS_HAIRFK', Integer, nullable=False),
    Column('CUS_RACEFK', Integer, nullable=False),
    Column('CUS_EYESFK', Integer, nullable=False),
    Column('CUS_SEX', String(1, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_MARKS', String(40, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_BIRTHDate', SMALLDATETIME),
    Column('CUS_BIRTHCITY', String(15, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_BIRTHSTATE', String(2, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_BIRTH2', String(15, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_IDTYP1', Integer, nullable=False),
    Column('CUS_IDNUM1', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_ID1EXP', SMALLDATETIME),
    Column('CUS_ID1ISSUE', String(50, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_IDTYP2', Integer, nullable=False),
    Column('CUS_IDNUM2', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_ID2EXP', SMALLDATETIME),
    Column('CUS_ID2ISSUE', String(2, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_KNOWN', BIT, nullable=False),
    Column('CUS_SSNUM', String(11, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_VEHIC1', String(10, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_VEHIC2', String(8, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_VEHIC3', String(2, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_EMPLOYER', String(40, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_EMPAD2', String(35, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_EMPAD1', String(35, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_EMPCITY', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_EMPSTATE', String(2, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_EMPZIP', String(10, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_AC2', String(3, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_EMPPHONE', String(14, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_COMMENT', String(200, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_TOTALPAWNS', Integer, nullable=False),
    Column('CUS_ACTIVEPAWN', Integer, nullable=False),
    Column('CUS_REDEEMED', Integer, nullable=False),
    Column('CUS_BUYS', Integer, nullable=False),
    Column('CUS_SALES', MONEY, nullable=False),
    Column('CUS_AMT1', MONEY, nullable=False),
    Column('CUS_AMT2', MONEY, nullable=False),
    Column('CUS_FFLNUM', String(25, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_DELETE', BIT, nullable=False),
    Column('CUS_LOCKED', BIT, nullable=False),
    Column('CUS_PAWNER', BIT, nullable=False),
    Column('CUS_BUYER', BIT, nullable=False),
    Column('CUS_IDADD1', String(25, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_IDADD2', String(25, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_IDCITY', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_IDSTATE', String(2, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_IDZIP', String(10, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_CREDIT', MONEY, nullable=False),
    Column('CUS_SPECIAL', Integer, nullable=False),
    Column('CUS_PIC_FK', Integer, nullable=False),
    Column('cus_Thum_fk', Integer, nullable=False),
    Column('CUS_Action_Spec', CHAR(1, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('Cus_ID', UNIQUEIDENTIFIER),
    Column('Cus_PatriotAct', BIT),
    Column('Cus_PointsPawnBuy', Integer, nullable=False),
    Column('Cus_PointsSale', Integer, nullable=False),
    Column('Cus_PointsAvail', Integer, nullable=False),
    Column('Cus_PointsMailer', BIT, nullable=False),
    Column('Cus_TaxID', String(25, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('Cus_CellPhone', String(20, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('Cus_Email', String(254, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('Cus_Entered', DateTime),
    Column('cus_military', BIT),
    Column('cmtr_id', UNIQUEIDENTIFIER, nullable=False),
    Column('usr_ID', UNIQUEIDENTIFIER, nullable=False),
    Column('cmrh_id', UNIQUEIDENTIFIER),
    Column('cmck_id', UNIQUEIDENTIFIER, nullable=False),
    Column('cmbk_id', UNIQUEIDENTIFIER, nullable=False),
    Column('cmvr_reponseother', String(20, 'SQL_Latin1_General_CP1_CI_AS'))
)

t_CM_CustView = Table(
    'CM_CustView', metadata,
    Column('maidenname', String(25, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('badcust', BIT),
    Column('hair', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('eyes', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('race', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('ID1Type', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('ID2Type', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('Cus_Store', Integer, nullable=False),
    Column('Cus_PK', Integer, nullable=False),
    Column('CUS_FNAME', String(15, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_MNAME', String(15, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_LNAME', String(25, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_ADD1', String(25, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_ADD2', String(25, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_CITY', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_STATE', String(2, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_ZIP', String(10, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_COUNTRY', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_AC1', String(3, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_PHONE1', String(8, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_HEIGHT', String(6, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_WEIGHT', SmallInteger, nullable=False),
    Column('CUS_HAIRFK', Integer, nullable=False),
    Column('CUS_RACEFK', Integer, nullable=False),
    Column('CUS_EYESFK', Integer, nullable=False),
    Column('CUS_SEX', String(1, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_MARKS', String(40, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_BIRTHDate', SMALLDATETIME),
    Column('CUS_BIRTHCITY', String(15, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_BIRTHSTATE', String(2, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_BIRTH2', String(15, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_IDTYP1', Integer, nullable=False),
    Column('CUS_IDNUM1', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_ID1EXP', SMALLDATETIME),
    Column('CUS_ID1ISSUE', String(50, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_IDTYP2', Integer, nullable=False),
    Column('CUS_IDNUM2', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_ID2EXP', SMALLDATETIME),
    Column('CUS_ID2ISSUE', String(2, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_KNOWN', BIT, nullable=False),
    Column('CUS_SSNUM', String(11, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_VEHIC1', String(10, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_VEHIC2', String(8, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_VEHIC3', String(2, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_EMPLOYER', String(40, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_EMPAD2', String(35, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_EMPAD1', String(35, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_EMPCITY', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_EMPSTATE', String(2, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_EMPZIP', String(10, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_AC2', String(3, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_EMPPHONE', String(14, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_COMMENT', String(200, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_TOTALPAWNS', Integer, nullable=False),
    Column('CUS_ACTIVEPAWN', Integer, nullable=False),
    Column('CUS_REDEEMED', Integer, nullable=False),
    Column('CUS_BUYS', Integer, nullable=False),
    Column('CUS_SALES', MONEY, nullable=False),
    Column('CUS_AMT1', MONEY, nullable=False),
    Column('CUS_AMT2', MONEY, nullable=False),
    Column('CUS_FFLNUM', String(25, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_DELETE', BIT, nullable=False),
    Column('CUS_LOCKED', BIT, nullable=False),
    Column('CUS_PAWNER', BIT, nullable=False),
    Column('CUS_BUYER', BIT, nullable=False),
    Column('CUS_IDADD1', String(25, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_IDADD2', String(25, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_IDCITY', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_IDSTATE', String(2, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_IDZIP', String(10, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_CREDIT', MONEY, nullable=False),
    Column('CUS_SPECIAL', Integer, nullable=False),
    Column('CUS_PIC_FK', Integer, nullable=False),
    Column('cus_Thum_fk', Integer, nullable=False),
    Column('CUS_Action_Spec', CHAR(1, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('Cus_ID', UNIQUEIDENTIFIER),
    Column('Cus_PatriotAct', BIT),
    Column('Cus_PointsPawnBuy', Integer, nullable=False),
    Column('Cus_PointsSale', Integer, nullable=False),
    Column('Cus_PointsAvail', Integer, nullable=False),
    Column('Cus_PointsMailer', BIT, nullable=False),
    Column('Cus_TaxID', String(25, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('Cus_CellPhone', String(20, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('Cus_Email', String(254, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('Cus_Entered', DateTime),
    Column('cus_military', BIT)
)

t_CM_SigLoanView = Table(
    'CM_SigLoanView', metadata,
    Column('CMTSL_ID', UNIQUEIDENTIFIER, nullable=False),
    Column('CMTR_ID', UNIQUEIDENTIFIER, nullable=False),
    Column('CMRH_ID', UNIQUEIDENTIFIER, nullable=False),
    Column('STO_PK', SmallInteger, nullable=False),
    Column('CMTSL_TicketNumber', Integer, nullable=False),
    Column('CMTSL_DateIn', DateTime, nullable=False),
    Column('CMTSL_MaturityDate', DateTime, nullable=False),
    Column('CMTSL_LoanAmount', MONEY, nullable=False),
    Column('CMTSL_ServiceAPR', MONEY, nullable=False),
    Column('CMTSL_InterestAPR', MONEY, nullable=False),
    Column('CMTSL_OneTimeFee', MONEY, nullable=False),
    Column('CMTSL_AmortOneTime', BIT),
    Column('CMTSL_PeriodFee', MONEY, nullable=False),
    Column('CMTSL_AdminPrepaid', MONEY, nullable=False),
    Column('CMTSL_OrigPrepaid', MONEY, nullable=False),
    Column('CMTSL_MiscPrepaid', MONEY, nullable=False),
    Column('CMTSL_OriginalPrincipal', MONEY, nullable=False),
    Column('CMTSL_Duration', SmallInteger, nullable=False),
    Column('CMTSL_PaymentFreq', String(1, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CMTSL_FPIAmount', MONEY, nullable=False),
    Column('CMTSL_PIAmount', MONEY, nullable=False),
    Column('CMTSL_FirstPayment', DateTime, nullable=False),
    Column('CMTSL_DOM1', TINYINT, nullable=False),
    Column('CMTSL_DOM2', TINYINT, nullable=False),
    Column('CMTSL_Note', String(254, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CMTSL_LPIAmount', MONEY, nullable=False),
    Column('CUS_ID', UNIQUEIDENTIFIER, nullable=False),
    Column('USR_ID', UNIQUEIDENTIFIER, nullable=False),
    Column('CMTR_Type', CHAR(10, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CMTR_Date', DateTime, nullable=False),
    Column('CMTR_Status', CHAR(2, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CMLC_ID', UNIQUEIDENTIFIER),
    Column('Cus_PK', Integer, nullable=False),
    Column('CUS_FNAME', String(15, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_MNAME', String(15, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_LNAME', String(25, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_ADD1', String(25, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_ADD2', String(25, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_CITY', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_STATE', String(2, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_ZIP', String(10, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_COUNTRY', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_AC1', String(3, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_PHONE1', String(8, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_HEIGHT', String(6, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_WEIGHT', SmallInteger, nullable=False),
    Column('CUS_HAIRFK', Integer, nullable=False),
    Column('CUS_EYESFK', Integer, nullable=False),
    Column('CUS_RACEFK', Integer, nullable=False),
    Column('CUS_SEX', String(1, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_MARKS', String(40, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_BIRTHDate', SMALLDATETIME),
    Column('CUS_BIRTHCITY', String(15, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_BIRTHSTATE', String(2, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_BIRTH2', String(15, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_IDTYP1', Integer, nullable=False),
    Column('ID1TYPE', String(20, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('CUS_IDNUM1', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_ID1EXP', SMALLDATETIME),
    Column('CUS_ID1ISSUE', String(50, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_IDTYP2', Integer, nullable=False),
    Column('CUS_IDNUM2', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_ID2EXP', SMALLDATETIME),
    Column('CUS_ID2ISSUE', String(2, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_KNOWN', BIT, nullable=False),
    Column('CUS_SSNUM', String(11, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_VEHIC1', String(10, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_VEHIC2', String(8, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_VEHIC3', String(2, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_EMPLOYER', String(40, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_EMPAD1', String(35, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_EMPAD2', String(35, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_EMPCITY', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_EMPSTATE', String(2, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_EMPZIP', String(10, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_AC2', String(3, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_EMPPHONE', String(14, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_COMMENT', String(200, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_LOCKED', BIT, nullable=False),
    Column('CUS_IDADD1', String(25, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_IDADD2', String(25, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_IDCITY', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_IDSTATE', String(2, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_IDZIP', String(10, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_SPECIAL', Integer, nullable=False),
    Column('CUS_PIC_FK', Integer, nullable=False),
    Column('cus_Thum_fk', Integer, nullable=False),
    Column('Cus_PatriotAct', BIT),
    Column('Cus_CellPhone', String(20, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('Cus_Email', String(254, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('Cus_Search_SSNUM4', String(4, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('USR_LANID', String(8, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CMCU_ID', UNIQUEIDENTIFIER, nullable=False),
    Column('cmcu_maidenname', String(25, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('cmcu_badcust', BIT),
    Column('cmcu_paydate', DateTime),
    Column('cmcu_payfreq', CHAR(1, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('cmcu_payrate', Numeric(18, 0)),
    Column('cmcu_payratefreq', CHAR(1, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('cmcu_directdeposit', BIT),
    Column('cmcu_jobtitle', String(30, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('cmcu_bankruptcy', BIT),
    Column('cmcu_garnishment', BIT),
    Column('cmcu_ownhome', BIT)
)

t_CM_TranHistoryAdvanceView = Table(
    'CM_TranHistoryAdvanceView', metadata,
    Column('sto_pk', SmallInteger, nullable=False),
    Column('tranhist_date', DateTime, nullable=False),
    Column('tranhist_amount', MONEY, nullable=False),
    Column('tranhist_type', CHAR(10, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('emp', String(8, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('emp_profit', String(8, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('OverRideAmount', MONEY, nullable=False),
    Column('ticketnumber', Integer, nullable=False),
    Column('numberofday', Integer, nullable=False),
    Column('datein', DateTime, nullable=False),
    Column('cmtha_dateout', DateTime, nullable=False),
    Column('adv_amount', MONEY, nullable=False),
    Column('paidtodate', DateTime, nullable=False),
    Column('floatamount', MONEY, nullable=False),
    Column('additionalcharge', MONEY, nullable=False),
    Column('additionalfee', MONEY, nullable=False),
    Column('monthlycharge', BIT, nullable=False),
    Column('reminder', DateTime),
    Column('cmvr_number', String(20, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('tran_type', CHAR(10, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('tran_date', DateTime, nullable=False),
    Column('status', CHAR(2, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('Cus_Store', Integer, nullable=False),
    Column('Cus_PK', Integer, nullable=False),
    Column('CUS_FNAME', String(15, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_MNAME', String(15, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_LNAME', String(25, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_ADD1', String(25, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_ADD2', String(25, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_CITY', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_STATE', String(2, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_ZIP', String(10, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_COUNTRY', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_AC1', String(3, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_PHONE1', String(8, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_HEIGHT', String(6, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_WEIGHT', SmallInteger, nullable=False),
    Column('CUS_HAIRFK', Integer, nullable=False),
    Column('CUS_EYESFK', Integer, nullable=False),
    Column('CUS_RACEFK', Integer, nullable=False),
    Column('CUS_SEX', String(1, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_MARKS', String(40, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_BIRTHDate', SMALLDATETIME),
    Column('CUS_BIRTHCITY', String(15, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_BIRTHSTATE', String(2, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_BIRTH2', String(15, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_IDTYP1', Integer, nullable=False),
    Column('CUS_IDNUM1', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_ID1EXP', SMALLDATETIME),
    Column('CUS_ID1ISSUE', String(50, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_IDTYP2', Integer, nullable=False),
    Column('CUS_IDNUM2', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_ID2EXP', SMALLDATETIME),
    Column('CUS_ID2ISSUE', String(2, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_KNOWN', BIT, nullable=False),
    Column('CUS_SSNUM', String(11, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_VEHIC1', String(10, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_VEHIC2', String(8, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_VEHIC3', String(2, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_EMPLOYER', String(40, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_EMPAD1', String(35, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_EMPAD2', String(35, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_EMPCITY', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_EMPSTATE', String(2, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_EMPZIP', String(10, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_AC2', String(3, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_EMPPHONE', String(14, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_COMMENT', String(200, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_TOTALPAWNS', Integer, nullable=False),
    Column('CUS_ACTIVEPAWN', Integer, nullable=False),
    Column('CUS_REDEEMED', Integer, nullable=False),
    Column('CUS_BUYS', Integer, nullable=False),
    Column('CUS_SALES', MONEY, nullable=False),
    Column('CUS_AMT1', MONEY, nullable=False),
    Column('CUS_AMT2', MONEY, nullable=False),
    Column('CUS_FFLNUM', String(25, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_DELETE', BIT, nullable=False),
    Column('CUS_LOCKED', BIT, nullable=False),
    Column('CUS_PAWNER', BIT, nullable=False),
    Column('CUS_BUYER', BIT, nullable=False),
    Column('CUS_IDADD1', String(25, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_IDADD2', String(25, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_IDCITY', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_IDSTATE', String(2, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_IDZIP', String(10, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_CREDIT', MONEY, nullable=False),
    Column('CUS_SPECIAL', Integer, nullable=False),
    Column('CUS_PIC_FK', Integer, nullable=False),
    Column('cus_Thum_fk', Integer, nullable=False),
    Column('CUS_Action_Spec', CHAR(1, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('Cus_id', UNIQUEIDENTIFIER),
    Column('Cus_PatriotAct', BIT),
    Column('Cus_PointsPawnBuy', Integer, nullable=False),
    Column('Cus_PointsSale', Integer, nullable=False),
    Column('Cus_PointsAvail', Integer, nullable=False),
    Column('Cus_PointsMailer', BIT, nullable=False),
    Column('maidenname', String(25, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('entered', DateTime),
    Column('CMCU_usr_id', UNIQUEIDENTIFIER),
    Column('cellphone', String(20, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('Email', String(254, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('badcust', BIT),
    Column('hair', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('eyes', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('race', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('ID1Type', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('ID2Type', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CMTH_id', UNIQUEIDENTIFIER, nullable=False),
    Column('cmtr_id', UNIQUEIDENTIFIER, nullable=False),
    Column('usr_id', UNIQUEIDENTIFIER, nullable=False),
    Column('cmcd_id', UNIQUEIDENTIFIER),
    Column('cmlc_id', UNIQUEIDENTIFIER),
    Column('cmth_profit_usr_id', UNIQUEIDENTIFIER, nullable=False),
    Column('cmtha_id', UNIQUEIDENTIFIER, nullable=False)
)

t_CPL_CustomerPaymentLock = Table(
    'CPL_CustomerPaymentLock', metadata,
    Column('CPL_ID', UNIQUEIDENTIFIER, unique=True, server_default=text("(newid())")),
    Column('CPL_Cus_fk', Integer, nullable=False, index=True),
    Column('CPL_LockDate', DateTime, nullable=False, index=True),
    Column('CPL_Employee', CHAR(3, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CPL_Sto_Pk', SmallInteger, nullable=False)
)

t_CPT_CustPointsTables = Table(
    'CPT_CustPointsTables', metadata,
    Column('Sto_pk', SmallInteger, nullable=False),
    Column('CPT_Type', CHAR(1, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CPT_Amount', MONEY, nullable=False),
    Column('CPT_Points', SmallInteger, nullable=False),
    Column('CPT_ID', UNIQUEIDENTIFIER, nullable=False, unique=True, server_default=text("(newid())")),
    Index('IDX_CPT_CustPointsTables_Sto_PK_CPT_Type', 'CPT_Type', 'Sto_pk')
)


class CPChecksPrinted(Base):
    __tablename__ = 'CP_ChecksPrinted'

    CP_ID = Column(UNIQUEIDENTIFIER, primary_key=True, server_default=text("(newid())"))
    sto_pk = Column(SmallInteger, nullable=False, server_default=text("(1)"))
    usr_id = Column(UNIQUEIDENTIFIER, nullable=False)
    CP_Number = Column(Integer, nullable=False, index=True)
    CP_Date = Column(DateTime, nullable=False, index=True)
    CP_Amount = Column(MONEY, nullable=False)
    CP_Memo = Column(String(30, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("('')"))
    CP_ToWhom = Column(String(35, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("('')"))
    CP_Address1 = Column(String(25, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("('')"))
    CP_Address2 = Column(String(25, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("('')"))
    CP_City = Column(String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("('')"))
    CP_State = Column(CHAR(2, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("('')"))
    CP_Zip = Column(CHAR(10, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("('')"))

t_Cardscan = Table(
    'Cardscan', metadata,
    Column('crd_PK', Integer, nullable=False),
    Column('crd_Code', Text(2147483647, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('crd_Compiled', Text(2147483647, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('crd_state', CHAR(3, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('crd_date', DateTime),
    Column('crd_id', UNIQUEIDENTIFIER, server_default=text("(newid())"))
)

t_Contract = Table(
    'Contract', metadata,
    Column('cont_pk', SmallInteger, nullable=False),
    Column('sto_FK', SmallInteger, nullable=False, server_default=text("(1)")),
    Column('SalesMsg', String(254, 'SQL_Latin1_General_CP1_CI_AS'), server_default=text("('')")),
    Column('LayawayMsg', String(150, 'SQL_Latin1_General_CP1_CI_AS'), server_default=text("('')")),
    Column('CreditSaleMsg', String(150, 'SQL_Latin1_General_CP1_CI_AS'), server_default=text("('')")),
    Column('RepairMsg', String(150, 'SQL_Latin1_General_CP1_CI_AS'), server_default=text("('')")),
    Column('MemoMsg', String(800, 'SQL_Latin1_General_CP1_CI_AS'), server_default=text("('')")),
    Column('Con_id', UNIQUEIDENTIFIER, server_default=text("(newid())")),
    Column('LastUpdatedUSR_ID', UNIQUEIDENTIFIER)
)

t_CrSaleView = Table(
    'CrSaleView', metadata,
    Column('TICKETNUM', Integer),
    Column('STO_PK', SmallInteger),
    Column('CUS_FK', Integer),
    Column('DATEin', SMALLDATETIME),
    Column('DATEout', SMALLDATETIME),
    Column('TransDate', SMALLDATETIME),
    Column('SaleAmt', MONEY),
    Column('Taxable', MONEY),
    Column('TAX', MONEY),
    Column('ReturnedAmt', MONEY),
    Column('srvchgperc', Float(24)),
    Column('srvchggrac', SmallInteger),
    Column('srvchgAmt', MONEY),
    Column('deposit', MONEY),
    Column('period', SmallInteger),
    Column('type', CHAR(1, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('sstatus', CHAR(1, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('status2', String(25, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('istatus', CHAR(1, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('INVNUM', String(14, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('NUMBERSOLD', Numeric(9, 2), nullable=False),
    Column('RETURNSOLD', DateTime),
    Column('AMOUNT', MONEY, nullable=False),
    Column('DESCRIPT', String(254, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('COST', MONEY, nullable=False),
    Column('TAXEXEMPT', BIT, nullable=False),
    Column('NEWITEM', BIT),
    Column('items_pk', Integer, nullable=False),
    Column('cus_fname', String(15, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('cus_lname', String(25, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('cus_ac1', String(3, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('cus_phone1', String(8, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('usr_lanid', String(8, 'SQL_Latin1_General_CP1_CI_AS'))
)


class CustReq(Base):
    __tablename__ = 'CustReq'

    CUS_STORE = Column(SmallInteger, primary_key=True, server_default=text("(0)"))
    CUS_FNAME = Column(BIT, nullable=False, server_default=text("(0)"))
    CUS_MNAME = Column(BIT, nullable=False, server_default=text("(0)"))
    CUS_LNAME = Column(BIT, nullable=False, server_default=text("(1)"))
    CUS_ADD1 = Column(BIT, nullable=False, server_default=text("(0)"))
    CUS_ADD2 = Column(BIT, nullable=False, server_default=text("(0)"))
    CUS_CITY = Column(BIT, nullable=False, server_default=text("(0)"))
    CUS_STATE = Column(BIT, nullable=False, server_default=text("(0)"))
    CUS_ZIP = Column(BIT, nullable=False, server_default=text("(0)"))
    CUS_COUNTRY = Column(BIT, nullable=False, server_default=text("(0)"))
    CUS_AC1 = Column(BIT, nullable=False, server_default=text("(0)"))
    CUS_PHONE1 = Column(BIT, nullable=False, server_default=text("(0)"))
    CUS_HEIGHT = Column(BIT, nullable=False, server_default=text("(0)"))
    CUS_WEIGHT = Column(BIT, nullable=False, server_default=text("(0)"))
    CUS_HAIRFK = Column(BIT, nullable=False, server_default=text("(0)"))
    CUS_EYESFK = Column(BIT, nullable=False, server_default=text("(0)"))
    CUS_RACEFK = Column(BIT, nullable=False, server_default=text("(0)"))
    CUS_SEX = Column(BIT, nullable=False, server_default=text("(0)"))
    CUS_MARKS = Column(BIT, nullable=False, server_default=text("(0)"))
    CUS_BIRTHDate = Column(BIT, nullable=False, server_default=text("(0)"))
    CUS_BIRTHCITY = Column(BIT, nullable=False, server_default=text("(0)"))
    CUS_BIRTHSTATE = Column(BIT, nullable=False, server_default=text("(0)"))
    CUS_BIRTH2 = Column(BIT, nullable=False, server_default=text("(0)"))
    CUS_IDTYP1 = Column(BIT, nullable=False, server_default=text("(0)"))
    CUS_IDNUM1 = Column(BIT, nullable=False, server_default=text("(0)"))
    CUS_ID1EXP = Column(BIT, nullable=False, server_default=text("(0)"))
    CUS_ID1ISSUE = Column(BIT, nullable=False, server_default=text("(0)"))
    CUS_IDTYP2 = Column(BIT, nullable=False, server_default=text("(0)"))
    CUS_IDNUM2 = Column(BIT, nullable=False, server_default=text("(0)"))
    CUS_ID2EXP = Column(BIT, nullable=False, server_default=text("(0)"))
    CUS_ID2ISSUE = Column(BIT, nullable=False, server_default=text("(0)"))
    CUS_KNOWN = Column(BIT, nullable=False, server_default=text("(0)"))
    CUS_SSNUM = Column(BIT, nullable=False, server_default=text("(0)"))
    CUS_VEHIC1 = Column(BIT, nullable=False, server_default=text("(0)"))
    CUS_VEHIC2 = Column(BIT, nullable=False, server_default=text("(0)"))
    CUS_VEHIC3 = Column(BIT, nullable=False, server_default=text("(0)"))
    CUS_EMPLOYER = Column(BIT, nullable=False, server_default=text("(0)"))
    CUS_EMPAD1 = Column(BIT, nullable=False, server_default=text("(0)"))
    CUS_EMPAD2 = Column(BIT, nullable=False, server_default=text("(0)"))
    CUS_EMPCITY = Column(BIT, nullable=False, server_default=text("(0)"))
    CUS_EMPSTATE = Column(BIT, nullable=False, server_default=text("(0)"))
    CUS_EMPZIP = Column(BIT, nullable=False, server_default=text("(0)"))
    CUS_AC2 = Column(BIT, nullable=False, server_default=text("(0)"))
    CUS_EMPPHONE = Column(BIT, nullable=False, server_default=text("(0)"))
    CUS_FFLNUM = Column(BIT, nullable=False, server_default=text("(0)"))
    CUS_IDADD1 = Column(BIT, nullable=False, server_default=text("(0)"))
    CUS_IDADD2 = Column(BIT, nullable=False, server_default=text("(0)"))
    CUS_IDCITY = Column(BIT, nullable=False, server_default=text("(0)"))
    CUS_IDSTATE = Column(BIT, nullable=False, server_default=text("(0)"))
    CUS_IDZIP = Column(BIT, nullable=False, server_default=text("(0)"))
    CUS_SPECIAL = Column(BIT, nullable=False, server_default=text("(0)"))
    Cur_id = Column(UNIQUEIDENTIFIER, unique=True, server_default=text("(newid())"))
    LastUpdatedUSR_ID = Column(UNIQUEIDENTIFIER)
    CUS_CELLPHONE = Column(BIT, nullable=False, server_default=text("(0)"))
    CUS_EMAIL = Column(BIT, nullable=False, server_default=text("((0))"))
    Cus_ID1IssueDate = Column(BIT, nullable=False, server_default=text("((0))"))
    Cus_ID2IssueDate = Column(BIT, nullable=False, server_default=text("((0))"))


t_DAM_DataAgeModules = Table(
    'DAM_DataAgeModules', metadata,
    Column('DAM_ID', UNIQUEIDENTIFIER, nullable=False, unique=True, server_default=text("(newid())")),
    Column('DAM_Module', String(50, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("('')")),
    Column('DAM_Order', SmallInteger, nullable=False),
    Column('DAM_Info', String(254, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("('')")),
    Column('DAM_Number', SmallInteger, nullable=False, index=True)
)

t_DAP_DataAgePartners = Table(
    'DAP_DataAgePartners', metadata,
    Column('DAP_ID', UNIQUEIDENTIFIER, nullable=False, unique=True, server_default=text("(newid())")),
    Column('DAP_Partner', String(50, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("('')")),
    Column('DAP_Order', SmallInteger, nullable=False),
    Column('DAP_Header', String(200, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("('')")),
    Column('DAP_Info', String(200, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("('')")),
    Column('DAP_WebSite', String(50, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("('')")),
    Column('DAP_Contact', String(100, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("('')")),
    Column('DAP_Name', String(100, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("('')")),
    Column('DAP_Phone', String(100, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("('')")),
    Column('DAP_EMail', String(100, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("('')")),
    Column('DAP_EmailCC', String(100, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("('')")),
    Column('DAP_EMailBCC', String(100, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("('')")),
    Column('DAP_Subject', String(100, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("('')")),
    Column('DAP_Body', String(100, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("('')")),
    Column('DAP_Number', SmallInteger, nullable=False, index=True)
)


class DLPDebitLoadProduct(Base):
    __tablename__ = 'DLP_DebitLoadProduct'

    dlp_id = Column(UNIQUEIDENTIFIER, primary_key=True, server_default=text("(newid())"))
    dlp_productno = Column(String(10, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    dlp_description = Column(String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    sto_pk = Column(SmallInteger, nullable=False)


class DLUCLoadUnloadCard(Base):
    __tablename__ = 'DLUC_LoadUnloadCard'
    __table_args__ = (
        Index('IX_DLUC_datetype', 'dluc_date', 'dluc_type'),
    )

    dluc_id = Column(UNIQUEIDENTIFIER, primary_key=True, server_default=text("(newid())"))
    dluc_type = Column(CHAR(1, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    dluc_dlc_id = Column(UNIQUEIDENTIFIER, nullable=False, index=True)
    dluc_tranno = Column(Integer, nullable=False)
    sto_pk = Column(SmallInteger, nullable=False)
    dluc_date = Column(SMALLDATETIME, nullable=False)
    dluc_amount = Column(MONEY, nullable=False)
    dluc_fee = Column(MONEY, nullable=False)
    dluc_lc_pk = Column(Integer, nullable=False)
    usr_fk = Column(Integer, nullable=False)


t_DPCU_Customer = Table(
    'DPCU_Customer', metadata,
    Column('DPCU_ID', UNIQUEIDENTIFIER, nullable=False, unique=True),
    Column('Cus_ID', UNIQUEIDENTIFIER, nullable=False, index=True),
    Column('DPCU_Template', LargeBinary)
)

t_DPUS_User = Table(
    'DPUS_User', metadata,
    Column('DPUS_ID', UNIQUEIDENTIFIER, nullable=False, unique=True),
    Column('Usr_ID', UNIQUEIDENTIFIER, nullable=False, index=True),
    Column('DPUS_Template', LargeBinary)
)

t_DataAgeUpdate = Table(
    'DataAgeUpdate', metadata,
    Column('UpdateDate', DateTime, nullable=False),
    Column('Sto_Pk', SmallInteger, nullable=False, index=True),
    Column('Product', CHAR(2, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('ResultCode', CHAR(1, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
)


class EDDEndDayDetail(Base):
    __tablename__ = 'EDD_EndDayDetail'

    EDD_No = Column(Integer, primary_key=True)
    EDD_ID = Column(UNIQUEIDENTIFIER, nullable=False, unique=True, server_default=text("(newid())"))
    Sto_PK = Column(SmallInteger, nullable=False)
    EDH_ID = Column(UNIQUEIDENTIFIER, nullable=False)
    EDD_Type = Column(SmallInteger, nullable=False)
    EDD_Amount = Column(String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    EDD_Desc = Column(String(40, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)


class EDHEndDayHeader(Base):
    __tablename__ = 'EDH_EndDayHeader'
    __table_args__ = (
        Index('IDX_EDH_EndDayHeader_STO_PK_EDH_Date', 'EDH_Date', 'Sto_PK'),
    )

    EDH_No = Column(Integer, primary_key=True)
    EDH_ID = Column(UNIQUEIDENTIFIER, nullable=False, unique=True, server_default=text("(newid())"))
    Sto_PK = Column(SmallInteger, nullable=False)
    EDH_Date = Column(DateTime, nullable=False)
    EDH_Posted = Column(DateTime, nullable=False)
    USR_ID = Column(UNIQUEIDENTIFIER, nullable=False)


t_EmpHistTrans = Table(
    'EmpHistTrans', metadata,
    Column('trn_PK', Integer, nullable=False, server_default=text("(0)")),
    Column('trn_Type', String(50, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('trn_Filter', String(50, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('TRN_id', UNIQUEIDENTIFIER, unique=True, server_default=text("(newid())"))
)


class GLAAccount(Base):
    __tablename__ = 'GLA_Account'

    GLA_ID = Column(UNIQUEIDENTIFIER, nullable=False, unique=True, server_default=text("(newid())"))
    GLA_NO = Column(Integer, primary_key=True)
    GLA_Account = Column(String(255, 'SQL_Latin1_General_CP1_CI_AS'), server_default=text("('')"))
    GLT_ID = Column(UNIQUEIDENTIFIER, index=True)
    Level_ID = Column(UNIQUEIDENTIFIER)
    gla_Export_AcctType = Column(String(100, 'SQL_Latin1_General_CP1_CI_AS'))
    sto_pk = Column(SmallInteger, index=True, server_default=text("(1)"))
    LastUpdatedUSR_ID = Column(UNIQUEIDENTIFIER, server_default=text("('F79DBA72-7207-4CCE-A271-FC83D727F283')"))


class GLDDetail(Base):
    __tablename__ = 'GLD_Detail'
    __table_args__ = (
        Index('IDX_GLD_Detail_Lv2_ID', 'GLH_ID', 'lv2_ID', 'GLD_ID'),
        Index('IDX_GLD_Detail_Lv1_ID', 'GLH_ID', 'lv1_ID', 'GLD_ID'),
        Index('IDX_GLD_Detail', 'GLH_ID', 'GLD_Acct_Posted'),
        Index('IDX_GLD_Detail_Lv4_ID', 'GLH_ID', 'lv4_ID', 'GLD_ID'),
        Index('IDX_GLD_Detail_Lv3_ID', 'GLH_ID', 'lv3_ID', 'GLD_ID')
    )

    GLD_ID = Column(UNIQUEIDENTIFIER, primary_key=True, unique=True, server_default=text("(newid())"))
    GLD_No = Column(Integer, nullable=False)
    GLH_ID = Column(UNIQUEIDENTIFIER, nullable=False, index=True)
    GLT_ID = Column(UNIQUEIDENTIFIER, nullable=False)
    GLD_Acct_Posted = Column(String(200, 'SQL_Latin1_General_CP1_CI_AS'), server_default=text("(0)"))
    GLD_Amt = Column(MONEY, nullable=False, server_default=text("(0)"))
    lv1_ID = Column(UNIQUEIDENTIFIER)
    lv2_ID = Column(UNIQUEIDENTIFIER)
    lv3_ID = Column(UNIQUEIDENTIFIER)
    lv4_ID = Column(UNIQUEIDENTIFIER)
    gld_OrigAmt = Column(MONEY)
    gld_ModDate = Column(DateTime)
    gld_ModType = Column(CHAR(1, 'SQL_Latin1_General_CP1_CI_AS'))
    USR_ID = Column(UNIQUEIDENTIFIER)


t_GLH_Header = Table(
    'GLH_Header', metadata,
    Column('GLH_ID', UNIQUEIDENTIFIER, nullable=False, unique=True, server_default=text("(newid())")),
    Column('GLH_No', Integer, nullable=False),
    Column('STO_PK', SmallInteger, nullable=False),
    Column('BAT_ID', UNIQUEIDENTIFIER, index=True),
    Column('GLH_Date', DateTime, nullable=False, server_default=text("(getdate())")),
    Column('GLH_Reference', String(200, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('GLH_Product', CHAR(2, 'SQL_Latin1_General_CP1_CI_AS'), server_default=text("('PM')")),
    Index('IDX_GLH_Header_STO_PK_GLH_Date', 'STO_PK', 'GLH_Date'),
    Index('IDX_GLH_Header_Sto_PK_GLH_ID', 'STO_PK', 'GLH_ID'),
    Index('IDX_GLH_Header', 'BAT_ID', 'GLH_ID')
)

t_GLM_AccountMask = Table(
    'GLM_AccountMask', metadata,
    Column('GLM_ID', UNIQUEIDENTIFIER, nullable=False, unique=True, server_default=text("(newid())")),
    Column('GLM_NO', Integer, nullable=False),
    Column('GLM_Mask_NO', TINYINT, index=True),
    Column('GLM_Mask', String(255, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('GLM_ExpInd', BIT, server_default=text("(1)")),
    Column('GLM_Length', TINYINT, server_default=text("(0)")),
    Column('LastUpdatedUSR_ID', UNIQUEIDENTIFIER, server_default=text("('F79DBA72-7207-4CCE-A271-FC83D727F283')"))
)

t_GLT_Type = Table(
    'GLT_Type', metadata,
    Column('GLT_ID', UNIQUEIDENTIFIER, nullable=False, unique=True, server_default=text("(newid())")),
    Column('GLT_No', Integer, nullable=False),
    Column('GLT_Type', CHAR(25, 'SQL_Latin1_General_CP1_CI_AS'), index=True),
    Column('GLT_Prompt', String(200, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('GLT_Status', BIT, nullable=False, server_default=text("(1)")),
    Column('GLT_AcctType', CHAR(1, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('GLT_Group', CHAR(2, 'SQL_Latin1_General_CP1_CI_AS'), index=True),
    Column('GLT_SortOrder', Integer, server_default=text("(0)")),
    Column('glt_cash_sto_pk', SmallInteger),
    Column('glt_Product', CHAR(2, 'SQL_Latin1_General_CP1_CI_AS'), server_default=text("('PM')")),
    Index('IDX_GLT_Type_GLT_type_glt_cash_Sto_pk', 'GLT_Type', 'glt_cash_sto_pk')
)

t_HoldConItems = Table(
    'HoldConItems', metadata,
    Column('hci_pk', Integer, nullable=False),
    Column('hc_fk', Integer, nullable=False, server_default=text("((-1))")),
    Column('sto_fk', SmallInteger, nullable=False, server_default=text("((-1))")),
    Column('items_fk', Integer, nullable=False, server_default=text("((-1))")),
    Column('HCI_id', UNIQUEIDENTIFIER, unique=True, server_default=text("(newid())")),
    Index('IDX_HoldConItems_Sto_FK_HC_FK', 'hc_fk', 'sto_fk')
)


class ITRQItemReq(Base):
    __tablename__ = 'ITRQ_ItemReq'

    ITRQ_ID = Column(UNIQUEIDENTIFIER, server_default=text("(newid())"))
    ITRQ_Store = Column(SmallInteger, primary_key=True, server_default=text("(0)"))
    level1_fk = Column(BIT, nullable=False, server_default=text("(1)"))
    level2_fk = Column(BIT, nullable=False, server_default=text("(0)"))
    level3_fk = Column(BIT, nullable=False, server_default=text("(0)"))
    level4_fk = Column(BIT, nullable=False, server_default=text("(0)"))
    level5_fk = Column(BIT, nullable=False, server_default=text("(0)"))
    modelnum = Column(BIT, nullable=False, server_default=text("(0)"))
    serialnum = Column(BIT, nullable=False, server_default=text("(0)"))
    color = Column(BIT, nullable=False, server_default=text("(0)"))
    ownernum = Column(BIT, nullable=False, server_default=text("(0)"))
    bin = Column(BIT, nullable=False, server_default=text("(0)"))
    amount = Column(BIT, nullable=False, server_default=text("(0)"))
    resaleamt = Column(BIT, nullable=False, server_default=text("(0)"))
    insrepcost = Column(BIT, nullable=False, server_default=text("(0)"))
    onhand = Column(BIT, nullable=False, server_default=text("(0)"))
    descript = Column(BIT, nullable=False, server_default=text("(0)"))
    storagefee = Column(BIT, nullable=False, server_default=text("(0)"))
    action_fk = Column(BIT, nullable=False, server_default=text("(1)"))
    finish_fk = Column(BIT, nullable=False, server_default=text("(0)"))
    barrel_fk = Column(BIT, nullable=False, server_default=text("(0)"))
    length = Column(BIT, nullable=False, server_default=text("(0)"))
    caliber_fk = Column(BIT, nullable=False, server_default=text("(1)"))
    condition = Column(BIT, nullable=False, server_default=text("(0)"))
    importerfk = Column(BIT, nullable=False, server_default=text("(0)"))
    metal_fk = Column(BIT, nullable=False, server_default=text("(0)"))
    karat_fk = Column(BIT, nullable=False, server_default=text("(0)"))
    weight = Column(BIT, nullable=False, server_default=text("(0)"))
    gender_fk = Column(BIT, nullable=False, server_default=text("(0)"))
    style_fk = Column(BIT, nullable=False, server_default=text("(0)"))
    sizelen_fk = Column(BIT, nullable=False, server_default=text("(0)"))
    numstone = Column(BIT, nullable=False, server_default=text("(0)"))
    typstonefk = Column(BIT, nullable=False, server_default=text("(0)"))
    shape_fk = Column(BIT, nullable=False, server_default=text("(0)"))
    carat = Column(BIT, nullable=False, server_default=text("(0)"))
    color_fk = Column(BIT, nullable=False, server_default=text("(0)"))
    stone_weight = Column(BIT, nullable=False, server_default=text("(0)"))
    stone_length = Column(BIT, nullable=False, server_default=text("(0)"))
    stone_width = Column(BIT, nullable=False, server_default=text("(0)"))
    translucfk = Column(BIT, nullable=False, server_default=text("(0)"))
    title_style_fk = Column(BIT, nullable=False, server_default=text("(0)"))
    cyear = Column(BIT, nullable=False, server_default=text("(0)"))
    plate_state = Column(BIT, nullable=False, server_default=text("(0)"))
    plate_number = Column(BIT, nullable=False, server_default=text("(0)"))
    mileage = Column(BIT, nullable=False, server_default=text("(0)"))
    title_cert_num = Column(BIT, nullable=False, server_default=text("(0)"))
    validation_num = Column(BIT, nullable=False, server_default=text("(0)"))
    LastUpdatedUSR_ID = Column(UNIQUEIDENTIFIER, server_default=text("('F79DBA72-7207-4CCE-A271-FC83D727F283')"))
    Condition_item = Column(BIT, nullable=False, server_default=text("((0))"))


class ITRItemsRFID(Base):
    __tablename__ = 'ITR_ItemsRFID'

    ITR_ID = Column(UNIQUEIDENTIFIER, nullable=False)
    ITEMS_ID = Column(UNIQUEIDENTIFIER, primary_key=True)
    sto_pk = Column(SmallInteger, nullable=False)
    ITR_EID = Column(String(50, 'SQL_Latin1_General_CP1_CI_AS'), index=True)


t_ItemWatchList = Table(
    'ItemWatchList', metadata,
    Column('IWL_ID', UNIQUEIDENTIFIER, nullable=False, unique=True, server_default=text("(newid())")),
    Column('STO_PK', SmallInteger, nullable=False),
    Column('Imported', BIT),
    Column('LV1_FK', Integer),
    Column('LV5_FK', Integer),
    Column('Model', String(20, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('SerialNum', String(50, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('Notes', String(250, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('Status', String(1, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('LastUpdatedUsr_id', UNIQUEIDENTIFIER),
    Column('LastUpdatedDate', DateTime),
    Column('ExpireDate', DateTime)
)

t_Items_SKU = Table(
    'Items_SKU', metadata,
    Column('ISKU_PK', Integer, nullable=False),
    Column('Sto_FK', Integer, nullable=False),
    Column('InvNum', String(14, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('ven_fk', Integer),
    Column('sku_num', Integer, index=True),
    Column('ven_invnum', String(14, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('LastPrice', MONEY),
    Column('ITK_id', UNIQUEIDENTIFIER, unique=True, server_default=text("(newid())")),
    Index('IDX_Items_SKU_Sto_FK_InvNum', 'Sto_FK', 'InvNum')
)


class Level1(Base):
    __tablename__ = 'Level1'
    __table_args__ = (
        Index('IDX_Level1_Sto_PK_Lv1_PK', 'sto_pk', 'lv1_pk'),
    )

    sto_pk = Column(SmallInteger, nullable=False, server_default=text("(1)"))
    lv1_pk = Column(Integer, primary_key=True, server_default=text("(1)"))
    DESCRIPT = Column(String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("('')"))
    lv1_ID = Column(UNIQUEIDENTIFIER, unique=True, server_default=text("(newid())"))
    LastUpdatedUSR_ID = Column(UNIQUEIDENTIFIER)


class Level2(Base):
    __tablename__ = 'Level2'
    __table_args__ = (
        Index('IDX_Level2_Sto_PK_Lv1_PK', 'sto_pk', 'lv2_pk'),
        Index('IDX_Level2_Sto_PK_Lv1_Parent', 'sto_pk', 'lv1_Parent')
    )

    sto_pk = Column(SmallInteger, nullable=False, server_default=text("(1)"))
    lv2_pk = Column(Integer, primary_key=True, server_default=text("(1)"))
    lv1_Parent = Column(Integer, nullable=False, index=True, server_default=text("(0)"))
    Descript = Column(String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("('')"))
    lv2_ID = Column(UNIQUEIDENTIFIER, unique=True, server_default=text("(newid())"))
    lv1_ID = Column(UNIQUEIDENTIFIER)
    LastUpdatedUSR_ID = Column(UNIQUEIDENTIFIER)


class Level3(Base):
    __tablename__ = 'Level3'
    __table_args__ = (
        Index('IDX_Level3_Sto_PK_Lv2_Parent', 'sto_pk', 'lv2_Parent'),
        Index('IDX_Level3_Sto_PK_Lv1_PK', 'sto_pk', 'lv3_pk')
    )

    sto_pk = Column(SmallInteger, nullable=False, server_default=text("(1)"))
    lv3_pk = Column(Integer, primary_key=True, server_default=text("(1)"))
    lv2_Parent = Column(Integer, nullable=False, index=True, server_default=text("(0)"))
    DESCRIPT = Column(String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("('')"))
    lv3_ID = Column(UNIQUEIDENTIFIER, unique=True, server_default=text("(newid())"))
    lv2_ID = Column(UNIQUEIDENTIFIER)
    LastUpdatedUSR_ID = Column(UNIQUEIDENTIFIER)


class Level4(Base):
    __tablename__ = 'Level4'
    __table_args__ = (
        Index('IDX_Level4_Sto_PK_Lv1_PK', 'sto_pk', 'lv4_PK'),
        Index('IDX_Level4_Sto_PK_Lv3_Parent', 'sto_pk', 'lv3_Parent')
    )

    sto_pk = Column(SmallInteger, nullable=False, server_default=text("(1)"))
    lv4_PK = Column(Integer, primary_key=True, server_default=text("(1)"))
    lv3_Parent = Column(Integer, nullable=False, index=True, server_default=text("(0)"))
    DESCRIPT = Column(String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("('')"))
    lv4_ID = Column(UNIQUEIDENTIFIER, unique=True, server_default=text("(newid())"))
    lv3_ID = Column(UNIQUEIDENTIFIER)
    LastUpdatedUSR_ID = Column(UNIQUEIDENTIFIER)


class Level5(Base):
    __tablename__ = 'Level5'
    __table_args__ = (
        Index('IDX_Level5_Sto_PK_Lv1_Parent', 'sto_pk', 'LV1_PARENT'),
        Index('IDX_Level5_Sto_PK_Lv1_PK', 'sto_pk', 'lv5_PK')
    )

    sto_pk = Column(SmallInteger, nullable=False, server_default=text("(1)"))
    lv5_PK = Column(Integer, primary_key=True, server_default=text("(1)"))
    LV1_PARENT = Column(Integer, nullable=False, index=True, server_default=text("(1)"))
    DESCRIPT = Column(String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("('')"))
    lv5_ID = Column(UNIQUEIDENTIFIER, unique=True, server_default=text("(newid())"))
    lv1_ID = Column(UNIQUEIDENTIFIER)
    LastUpdatedUSR_ID = Column(UNIQUEIDENTIFIER)


class LevelN(Base):
    __tablename__ = 'Level_N'
    __table_args__ = (
        Index('IDX_Level_N_Sto_PK_Lv1_PK', 'sto_pk', 'Level_FK'),
    )

    sto_pk = Column(SmallInteger, primary_key=True, nullable=False, server_default=text("(1)"))
    Level_FK = Column(Integer, primary_key=True, nullable=False, server_default=text("(1)"))
    NCIC_code = Column(String(15, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("(' ')"))
    Local_Code = Column(String(15, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("(' ')"))
    HoldGunDays = Column(TINYINT, nullable=False, server_default=text("(0)"))
    Post2GunLog = Column(BIT, nullable=False, server_default=text("(0)"))
    Min_Age = Column(TINYINT, nullable=False, server_default=text("(0)"))
    HandGun = Column(BIT, nullable=False, server_default=text("(0)"))
    LVN_id = Column(UNIQUEIDENTIFIER, unique=True, server_default=text("(newid())"))
    Lv_ID = Column(UNIQUEIDENTIFIER)
    LastUpdatedUSR_ID = Column(UNIQUEIDENTIFIER)


class LookupB(Base):
    __tablename__ = 'Lookup_B'

    lb_pk = Column(Integer, primary_key=True)
    lb_descript = Column(String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("('')"))
    lb_type = Column(CHAR(1, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("('')"))
    LUB_id = Column(UNIQUEIDENTIFIER, unique=True, server_default=text("(newid())"))


class LookupN(Base):
    __tablename__ = 'Lookup_N'

    ln_pk = Column(Integer, nullable=False)
    sto_pk = Column(Integer, primary_key=True, nullable=False, server_default=text("(1)"))
    lc_FK = Column(Integer, primary_key=True, nullable=False, server_default=text("(1)"))
    NCIC_Code = Column(String(15, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("('')"))
    Local_Code = Column(String(15, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("('')"))
    LUN_id = Column(UNIQUEIDENTIFIER, unique=True, server_default=text("(newid())"))
    LastUpdatedUSR_ID = Column(UNIQUEIDENTIFIER)


class MRSTTemplate(Base):
    __tablename__ = 'MRST_Templates'

    MRST_ID = Column(UNIQUEIDENTIFIER, primary_key=True, server_default=text("(newid())"))
    STO_PK = Column(SmallInteger)
    MRST_TEMPLATE = Column(String(300, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    MRST_CODE = Column(String(4, 'SQL_Latin1_General_CP1_CI_AS'))
    MRST_TYPE = Column(String(25, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    USR_ID = Column(UNIQUEIDENTIFIER)
    MRST_DEFAULT = Column(BIT, nullable=False, server_default=text("((0))"))
    MRST_LEVEL = Column(SmallInteger)
    MRST_SUBSCRIBE = Column(BIT, nullable=False, server_default=text("((0))"))
    MRST_SORTORDER = Column(SmallInteger)
    MRST_THRESHOLD = Column(MONEY, server_default=text("((0.00))"))
    MRST_CELLPHONELIST = Column(String(200, 'SQL_Latin1_General_CP1_CI_AS'))


class MRSVVariable(Base):
    __tablename__ = 'MRSV_Variables'

    MRSV_ID = Column(UNIQUEIDENTIFIER, primary_key=True, server_default=text("(newid())"))
    STO_PK = Column(SmallInteger)
    MRSV_VARIABLE = Column(String(100, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    MRSV_TYPE = Column(String(25, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    MRSV_ORDER = Column(TINYINT, nullable=False, server_default=text("((0))"))


class MRSWWordList(Base):
    __tablename__ = 'MRSW_WordList'

    MRSW_ID = Column(UNIQUEIDENTIFIER, primary_key=True, server_default=text("(newid())"))
    MRSW_WORD = Column(String(35, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)


class MenuItem(Base):
    __tablename__ = 'MenuItems'

    mnu_PK = Column(Integer, primary_key=True)
    mnu_Parent = Column(Integer, nullable=False)
    mnu_Pad = Column(Integer, nullable=False)
    mnu_Level = Column(Integer, nullable=False)
    mnu_Bar = Column(Integer, nullable=False)
    mnu_Descript = Column(String(40, 'SQL_Latin1_General_CP1_CI_AS'))
    mnu_AllowChange = Column(BIT, nullable=False, server_default=text("(1)"))
    mnu_EditVisible = Column(BIT, nullable=False, server_default=text("(1)"))
    MNU_id = Column(UNIQUEIDENTIFIER, unique=True, server_default=text("(newid())"))
    mnu_Desc_BuySell = Column(String(40, 'SQL_Latin1_General_CP1_CI_AS'))


class MenuLevel(Base):
    __tablename__ = 'MenuLevels'

    sto_PK = Column(Integer, primary_key=True, nullable=False, server_default=text("(1)"))
    mnu_FK = Column(Integer, primary_key=True, nullable=False, server_default=text("(1)"))
    mnu_AccessLvl = Column(Integer, nullable=False, server_default=text("(1)"))
    MNL_id = Column(UNIQUEIDENTIFIER, unique=True, server_default=text("(newid())"))
    LastUpdatedUSR_ID = Column(UNIQUEIDENTIFIER, server_default=text("('F79DBA72-7207-4CCE-A271-FC83D727F283')"))


t_Message = Table(
    'Message', metadata,
    Column('msg_PK', Integer, nullable=False),
    Column('sto_pk', SmallInteger, nullable=False, server_default=text("(1)")),
    Column('from_fk', Integer, nullable=False, server_default=text("(0)")),
    Column('to_fk', Integer, nullable=False, server_default=text("(0)")),
    Column('created', SMALLDATETIME, server_default=text("(null)")),
    Column('dStart', SMALLDATETIME, server_default=text("(null)")),
    Column('dEnd', SMALLDATETIME, server_default=text("(null)")),
    Column('message', String(250, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("(' ')")),
    Column('MSG_id', UNIQUEIDENTIFIER, unique=True, server_default=text("(newid())")),
    Column('from_sto_pk', SmallInteger, nullable=False, server_default=text("(1)")),
    Index('IDX_Message_To_fk_Sto_pk', 'to_fk', 'sto_pk'),
    Index('IDX_Message_From_fk_From_Sto_pk', 'from_fk', 'from_sto_pk')
)


class MrsCode(Base):
    __tablename__ = 'Mrs_Codes'

    codes_pk = Column(Integer, primary_key=True)
    sto_pk = Column(SmallInteger, nullable=False)
    country = Column(String(200, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    code = Column(String(200, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    divcode = Column(String(200, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    inuse = Column(BIT)


t_Mrs_TextMsg = Table(
    'Mrs_TextMsg', metadata,
    Column('MRS_ID', UNIQUEIDENTIFIER, nullable=False),
    Column('CUS_ID', UNIQUEIDENTIFIER, index=True),
    Column('USR_ID', UNIQUEIDENTIFIER, nullable=False),
    Column('STO_PK', SmallInteger, nullable=False),
    Column('MRS_TYPE', String(1, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('MRS_SEND', Text(2147483647, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('MRS_RECEIVE', Text(2147483647, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('MRS_DATE', DateTime, index=True),
    Column('TICKETNUM', Integer, server_default=text("(null)"))
)

t_Mrsd_TextMsgDate = Table(
    'Mrsd_TextMsgDate', metadata,
    Column('MRSD_ID', UNIQUEIDENTIFIER, nullable=False),
    Column('STO_PK', SmallInteger, nullable=False),
    Column('MRSD_DATE', DateTime, nullable=False, index=True)
)


class Override(Base):
    __tablename__ = 'Override'
    __table_args__ = (
        Index('IX_Date_Sto_PK', 'Ovr_Date', 'Sto_PK'),
    )

    Ovr_ID = Column(UNIQUEIDENTIFIER, primary_key=True, server_default=text("(newid())"))
    Ovr_PK = Column(Integer, nullable=False)
    Sto_PK = Column(SmallInteger, nullable=False)
    Ovr_Date = Column(DateTime, nullable=False)
    User_ID = Column(UNIQUEIDENTIFIER, nullable=False, index=True)
    Ovr_UserID = Column(UNIQUEIDENTIFIER, nullable=False, index=True)
    Ovr_Desc = Column(String(200, 'SQL_Latin1_General_CP1_CI_AS'))
    Ticketnum = Column(Integer, index=True)


t_PAA_Patriot_Address = Table(
    'PAA_Patriot_Address', metadata,
    Column('PAA_ID', UNIQUEIDENTIFIER, unique=True, server_default=text("(newid())")),
    Column('PAH_ID', UNIQUEIDENTIFIER, nullable=False, index=True),
    Column('PAA_Address', String(125, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('PAA_City', String(30, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('PAA_Country', String(40, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('PAA_Remarks', String(254, 'SQL_Latin1_General_CP1_CI_AS'))
)

t_PAH_Patriot_Header = Table(
    'PAH_Patriot_Header', metadata,
    Column('PAH_ID', UNIQUEIDENTIFIER, unique=True, server_default=text("(newid())"))
)

t_PAN_Patriot_Names = Table(
    'PAN_Patriot_Names', metadata,
    Column('PAN_ID', UNIQUEIDENTIFIER, unique=True, server_default=text("(newid())")),
    Column('PAH_ID', UNIQUEIDENTIFIER, nullable=False, index=True),
    Column('PAN_Name', String(200, 'SQL_Latin1_General_CP1_CI_AS'), index=True),
    Column('PAN_MainName', BIT, nullable=False, server_default=text("(0)")),
    Column('PAN_Remarks', String(254, 'SQL_Latin1_General_CP1_CI_AS'))
)


class PMAC(Base):
    __tablename__ = 'PMACS'

    PMACS_ID = Column(UNIQUEIDENTIFIER, primary_key=True, server_default=text("(newid())"))
    STO_PK = Column(SmallInteger, nullable=False)
    ACS_URL = Column(String(75, 'SQL_Latin1_General_CP1_CI_AS'))
    ACS_CUSID = Column(String(25, 'SQL_Latin1_General_CP1_CI_AS'))
    ACS_PASS = Column(String(30, 'SQL_Latin1_General_CP1_CI_AS'))
    ACS_PONUMBER = Column(String(30, 'SQL_Latin1_General_CP1_CI_AS'))
    ACS_SHIPTOACCT = Column(String(30, 'SQL_Latin1_General_CP1_CI_AS'))
    ACS_SHIPTONAME = Column(String(35, 'SQL_Latin1_General_CP1_CI_AS'))
    ACS_SHIPTOADDR = Column(String(50, 'SQL_Latin1_General_CP1_CI_AS'))
    ACS_SHIPTOCITY = Column(String(20, 'SQL_Latin1_General_CP1_CI_AS'))
    ACS_SHIPTOSTATE = Column(String(3, 'SQL_Latin1_General_CP1_CI_AS'))
    ACS_SHIPTOZIP = Column(String(10, 'SQL_Latin1_General_CP1_CI_AS'))
    ACS_EMAIL = Column(String(50, 'SQL_Latin1_General_CP1_CI_AS'))
    ACS_SHIPTOATTN = Column(String(30, 'SQL_Latin1_General_CP1_CI_AS'))
    ACS_SHIPTOMETHOD = Column(String(10, 'SQL_Latin1_General_CP1_CI_AS'))
    ACS_XACCTTYPE = Column(String(12, 'SQL_Latin1_General_CP1_CI_AS'))
    ACS_SHIPTOPHONE = Column(String(10, 'SQL_Latin1_General_CP1_CI_AS'))
    ACS_VENDORNUMBER = Column(Integer)
    ACS_CLXPOSID = Column(String(15, 'SQL_Latin1_General_CP1_CI_AS'))
    ACS_FIELD1 = Column(String(15, 'SQL_Latin1_General_CP1_CI_AS'))
    ACS_FIELD2 = Column(String(15, 'SQL_Latin1_General_CP1_CI_AS'))
    ACS_CLXAUTOUPDATE = Column(BIT)
    ACS_CLXUPDATETIME = Column(String(4, 'SQL_Latin1_General_CP1_CI_AS'))
    ACS_CLXLASTUPDATE = Column(DateTime)
    ACS_CLXHISTORY = Column(BIT)
    ACS_USE = Column(BIT)


class PMACSDETAIL(Base):
    __tablename__ = 'PMACS_DETAIL'

    ACS_DETAIL_ID = Column(UNIQUEIDENTIFIER, primary_key=True, server_default=text("(newid())"))
    STO_PK = Column(SmallInteger, nullable=False)
    ACS_HEADER_ID = Column(UNIQUEIDENTIFIER, nullable=False)
    ACS_ID = Column(String(15, 'SQL_Latin1_General_CP1_CI_AS'))
    ITEMS_ID = Column(UNIQUEIDENTIFIER)
    ACS_ORDERQTY = Column(Integer)
    ACS_ONORDER = Column(Integer)
    ACS_FILLED = Column(Integer)
    ACS_UPC = Column(String(15, 'SQL_Latin1_General_CP1_CI_AS'))
    ACS_ITEMDESC = Column(String(25, 'SQL_Latin1_General_CP1_CI_AS'))


class PMACSFALEVEL(Base):
    __tablename__ = 'PMACS_FALEVELS'

    FALV_ID = Column(UNIQUEIDENTIFIER, primary_key=True, unique=True, server_default=text("(newid())"))
    STO_PK = Column(SmallInteger, nullable=False)
    UPC = Column(String(14, 'SQL_Latin1_General_CP1_CI_AS'))
    MODELNUM = Column(String(20, 'SQL_Latin1_General_CP1_CI_AS'))
    LEVEL5_FK = Column(Integer)
    LEVEL2_FK = Column(Integer)
    CALIBER_FK = Column(Integer)
    ACTION_FK = Column(Integer)
    MAXQUANT = Column(Integer)
    REORDER = Column(Integer)
    NOTES = Column(String(250, 'SQL_Latin1_General_CP1_CI_AS'))
    ACTIVE = Column(BIT)
    LASTUPDATEDDATE = Column(DateTime)


class PMACSHEADER(Base):
    __tablename__ = 'PMACS_HEADER'

    ACS_HEADER_ID = Column(UNIQUEIDENTIFIER, primary_key=True, server_default=text("(newid())"))
    STO_PK = Column(SmallInteger, nullable=False)
    ACS_PONUMBER = Column(String(20, 'SQL_Latin1_General_CP1_CI_AS'))
    ACS_SEND = Column(Text(2147483647, 'SQL_Latin1_General_CP1_CI_AS'))
    ACS_RECEIVE = Column(Text(2147483647, 'SQL_Latin1_General_CP1_CI_AS'))
    ACS_DATE = Column(DateTime)
    ACS_USR_ID = Column(UNIQUEIDENTIFIER)


class PMARTAssignRateTable(Base):
    __tablename__ = 'PMART_AssignRateTables'

    pk_rate = Column(UNIQUEIDENTIFIER, primary_key=True, server_default=text("(newid())"))
    level1_fk = Column(UNIQUEIDENTIFIER)
    level2_fk = Column(UNIQUEIDENTIFIER)
    rate_descript = Column(String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    sto_pk = Column(SmallInteger, nullable=False, server_default=text("((1))"))


t_PMLU_LastUpdated = Table(
    'PMLU_LastUpdated', metadata,
    Column('ID', Integer, nullable=False),
    Column('Sto_PK', Integer, index=True),
    Column('LastUpdLevel1', DateTime),
    Column('LastUpdLevel2', DateTime),
    Column('LastUpdLevel3', DateTime),
    Column('LastUpdLevel4', DateTime),
    Column('LastUpdLevel5', DateTime),
    Column('LastUpdLookup_C', DateTime),
    Column('LastUpdBin', DateTime),
    Column('LastUpdStatProv', DateTime),
    Column('LastUpdZipCity', DateTime),
    Column('LastUpdItemReq', DateTime),
    Column('LastUpdCustReq', DateTime),
    Column('LastUpdC_Rates', DateTime),
    Column('LastUpdUsers', DateTime)
)


class PMSGStoreGroup(Base):
    __tablename__ = 'PMSG_StoreGroup'

    PMSG_ID = Column(UNIQUEIDENTIFIER, primary_key=True, index=True, server_default=text("(newid())"))
    PMSG_Description = Column(NCHAR(50), nullable=False)


class PMTRDTransferDetail(Base):
    __tablename__ = 'PMTRD_TransferDetail'

    pmtrd_id = Column(UNIQUEIDENTIFIER, primary_key=True, server_default=text("(newid())"))
    items_id = Column(UNIQUEIDENTIFIER, index=True)
    inv_id = Column(UNIQUEIDENTIFIER, index=True)
    pmtrh_id = Column(UNIQUEIDENTIFIER, nullable=False)
    items_pk = Column(Integer)
    invnum = Column(String(14, 'SQL_Latin1_General_CP1_CI_AS'))
    sto_pk = Column(Integer)


class PMTRHTransferHeader(Base):
    __tablename__ = 'PMTRH_TransferHeader'

    pmtrh_id = Column(UNIQUEIDENTIFIER, primary_key=True, server_default=text("(newid())"))
    sto_name = Column(String(35, 'SQL_Latin1_General_CP1_CI_AS'))
    pmtrh_date = Column(DateTime, index=True)
    pmtrh_type = Column(String(1, 'SQL_Latin1_General_CP1_CI_AS'))
    pmtrh_emp = Column(String(8, 'SQL_Latin1_General_CP1_CI_AS'))
    sto_pk = Column(Integer)
    verifycode = Column(String(10, 'SQL_Latin1_General_CP1_CI_AS'), index=True)


t_POI_PawnOrigInvnum = Table(
    'POI_PawnOrigInvnum', metadata,
    Column('POI_ID', UNIQUEIDENTIFIER, nullable=False, unique=True, server_default=text("(newid())")),
    Column('Sto_pk', SmallInteger, nullable=False),
    Column('OrigInvNum', String(14, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('InvNum', String(14, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Index('IDX_POI_OrigInvNum_Sto_PK', 'Sto_pk', 'OrigInvNum'),
    Index('IDX_POI_InvNum_Sto_PK', 'InvNum', 'Sto_pk')
)


class PPRProtPlanRep(Base):
    __tablename__ = 'PPR_ProtPlanRep'

    ppr_id = Column(UNIQUEIDENTIFIER, primary_key=True, server_default=text("(newid())"))
    sit_id = Column(UNIQUEIDENTIFIER, nullable=False, index=True)
    pps_id = Column(UNIQUEIDENTIFIER, nullable=False, index=True)


class PSIPawnSimpleInterest(Base):
    __tablename__ = 'PSI_PawnSimpleInterest'
    __table_args__ = (
        Index('IX_PSI_TicketNum_Sto_pk', 'TicketNum', 'sto_pk', unique=True),
    )

    PSI_ID = Column(UNIQUEIDENTIFIER, primary_key=True, server_default=text("(newid())"))
    PWN_ID = Column(UNIQUEIDENTIFIER)
    sto_pk = Column(SmallInteger, nullable=False, server_default=text("(1)"))
    TicketNum = Column(Integer, nullable=False)
    PIAmount = Column(MONEY, nullable=False)
    MonthlyFee = Column(MONEY, nullable=False)
    OneTimeFee = Column(MONEY, nullable=False)
    StorageFee = Column(MONEY, nullable=False)
    IntRate = Column(MONEY, nullable=False)
    SCRate = Column(MONEY, nullable=False)
    SCDP = Column(CHAR(1, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("('%')"))
    MinAmt = Column(MONEY, nullable=False, server_default=text("(0.00)"))
    MaxAmt = Column(MONEY, nullable=False, server_default=text("(999999.99)"))
    RepoFeeAmt = Column(MONEY, nullable=False, server_default=text("(0.00)"))


t_PawnView = Table(
    'PawnView', metadata,
    Column('Store_No', SmallInteger, nullable=False),
    Column('Usr_LANID', String(8, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('TicketNum', Integer, nullable=False),
    Column('OrigTicket', Integer, nullable=False),
    Column('DateIn', SMALLDATETIME),
    Column('NumDays', SmallInteger, nullable=False),
    Column('DateOut', SMALLDATETIME),
    Column('PawnAmt', MONEY, nullable=False),
    Column('Trans', String(1, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('PaidAmt', MONEY, nullable=False),
    Column('Status', String(1, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('NumItems', SmallInteger, nullable=False),
    Column('RateTable', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('ChargeDate', SMALLDATETIME),
    Column('Comment', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('ServPeriod', SmallInteger, nullable=False),
    Column('GunChrg', MONEY, nullable=False),
    Column('TickChrg', MONEY),
    Column('MonthChrg', MONEY, nullable=False),
    Column('MonthChrg2', MONEY, nullable=False),
    Column('MonthlyChg', BIT, nullable=False),
    Column('PrepChrg', MONEY, nullable=False),
    Column('StorageChrg', MONEY, nullable=False),
    Column('PrevPawnAmt', MONEY, nullable=False),
    Column('DailyFee', MONEY, nullable=False),
    Column('PawnNote', String(200, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('StartDate', SMALLDATETIME),
    Column('FloatAmt', MONEY, nullable=False),
    Column('TitleLoan', BIT, nullable=False),
    Column('Reminder', SMALLDATETIME),
    Column('TransDate', SMALLDATETIME),
    Column('StartPawnAmt', MONEY, nullable=False),
    Column('unextenddate', SMALLDATETIME),
    Column('text_msg', BIT, nullable=False),
    Column('pddate', SMALLDATETIME),
    Column('MLARate', BIT, nullable=False),
    Column('Level1_FK', Integer, nullable=False),
    Column('Level2_FK', Integer, nullable=False),
    Column('Level3_FK', Integer, nullable=False),
    Column('Level4_FK', Integer, nullable=False),
    Column('Level5_FK', Integer, nullable=False),
    Column('Descript2', String(200, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('ModelNum', String(20, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('SerialNum', String(50, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('Bin', String(6, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('Amount', MONEY),
    Column('ResaleAmt', MONEY),
    Column('InsRepCost', MONEY),
    Column('OnHand', DECIMAL(10, 2)),
    Column('OrigOnHand', Integer),
    Column('iStatus', String(1, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('Items_PK', Integer, nullable=False),
    Column('Items_ID', UNIQUEIDENTIFIER),
    Column('composite', String(255, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('composit2', String(255, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('composit3', String(255, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('composit4', String(1000, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('cus_pk', Integer, nullable=False),
    Column('Cus_FName', String(15, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('Cus_MName', String(15, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('Cus_LName', String(25, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('Cus_Add1', String(25, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('Cus_Add2', String(25, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('Cus_City', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('Cus_State', String(2, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('Cus_Zip', String(10, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('Cus_AC1', String(3, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('Cus_Phone1', String(8, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('cus_id', UNIQUEIDENTIFIER),
    Column('Cus_TotalPawns', Integer, nullable=False),
    Column('Cus_ActivePawn', Integer, nullable=False),
    Column('Cus_Redeemed', Integer, nullable=False),
    Column('Cus_Buys', Integer, nullable=False),
    Column('Cus_Cellphone', String(20, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('Cus_Email', String(254, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('Cus_TxtMsg', BIT),
    Column('Cus_TxtMsgSent', DateTime)
)

t_PayOrder = Table(
    'PayOrder', metadata,
    Column('PayOrd_PK', Integer, nullable=False),
    Column('Sto_PK', SmallInteger, nullable=False, server_default=text("(1)")),
    Column('SortOrder', TINYINT),
    Column('Descript', String(20, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('arrayelement', TINYINT),
    Column('PAO_id', UNIQUEIDENTIFIER, unique=True, server_default=text("(newid())"))
)

t_PoliceView = Table(
    'PoliceView', metadata,
    Column('TICKETNUM', Integer, nullable=False),
    Column('DATEIN', SMALLDATETIME),
    Column('PawnAMT', MONEY, nullable=False),
    Column('TRANS', String(1, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('STATUS', String(1, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('STARTDATE', SMALLDATETIME),
    Column('SERIALNUM', String(20, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('MODELNUM', String(20, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('AMOUNT', MONEY),
    Column('OnHand', DECIMAL(10, 2)),
    Column('origonhand', Integer),
    Column('Composite', String(255, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('Composit2', String(255, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('Composit3', String(255, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('Composit4', String(1000, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('DESCRIPT', String(200, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('DESCRIPT2', String(200, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('fullname', String(58, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('CUS_LNAME', String(25, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('CUS_FNAME', String(15, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('CUS_MNAME', String(15, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('CUS_ADD1', String(25, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('CUS_ADD2', String(25, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('CUS_CITY', String(20, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('CUS_STATE', String(2, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('CUS_ZIP', String(10, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('race', String(20, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('CUS_HEIGHT', String(6, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('CUS_WEIGHT', SmallInteger),
    Column('CUS_PHONE1', String(8, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('CUS_HAIRFK', Integer),
    Column('CUS_EYESFK', Integer),
    Column('hair', String(20, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('eyes', String(20, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('CUS_SEX', String(1, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('CUS_BIRTHDate', SMALLDATETIME),
    Column('CUS_SSNUM', String(11, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('CUS_IDNUM1', String(20, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('CUS_ID1ISSUE', String(50, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('CUS_ID1', String(20, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('CUS_ID2', String(20, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('CUS_IDNUM2', String(20, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('CUS_ID2ISSUE', String(2, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('emp', String(8, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('STORE_NO', SmallInteger, nullable=False),
    Column('POLTICNUM', Integer, nullable=False),
    Column('DATEOUT', SMALLDATETIME),
    Column('TRANSDATE', SMALLDATETIME),
    Column('NUMITEMS', SmallInteger, nullable=False),
    Column('COMMENT', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('RePawned', BIT, nullable=False),
    Column('ORIGTICKET', Integer, nullable=False),
    Column('origdatein', SMALLDATETIME),
    Column('PAWNNOTE', String(200, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('LEVEL1_FK', Integer),
    Column('LEVEL2_FK', Integer),
    Column('LEVEL3_FK', Integer),
    Column('LEVEL4_FK', Integer),
    Column('LEVEL5_FK', Integer),
    Column('Color', Integer),
    Column('OWNERNUM', String(20, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('CUS_AC1', String(3, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('CUS_RACEFK', Integer),
    Column('CUS_MARKS', String(40, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('CUS_BIRTHCITY', String(15, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('CUS_BIRTHSTATE', String(2, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('CUS_BIRTH2', String(15, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('CUS_IDTYP1', Integer),
    Column('CUS_ID1EXP', SMALLDATETIME),
    Column('CUS_IDTYP2', Integer),
    Column('CUS_ID2EXP', SMALLDATETIME),
    Column('CUS_KNOWN', BIT),
    Column('CUS_COMMENT', String(200, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('CUS_IDADD1', String(25, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('CUS_IDADD2', String(25, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('CUS_IDCITY', String(20, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('CUS_IDSTATE', String(2, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('CUS_IDZIP', String(10, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('CUS_SPECIAL', Integer)
)

t_Printdata = Table(
    'Printdata', metadata,
    Column('reprint_id', UNIQUEIDENTIFIER, nullable=False, index=True, server_default=text("(newid())")),
    Column('sto_pk', SmallInteger, nullable=False),
    Column('ticketnum', Integer, nullable=False),
    Column('printdata', CHAR(1000, 'SQL_Latin1_General_CP1_CI_AS'))
)

t_PurgeHist = Table(
    'PurgeHist', metadata,
    Column('PurgeNum', SmallInteger, nullable=False),
    Column('Sto_PK', Integer),
    Column('PurgeDate', DateTime),
    Column('PurgeStarted', DateTime),
    Column('PurgeEnded', DateTime)
)

t_QuickQuoteHist = Table(
    'QuickQuoteHist', metadata,
    Column('QuickQuoteHist_id', UNIQUEIDENTIFIER, nullable=False, index=True),
    Column('QuickQuoteHeader_id', UNIQUEIDENTIFIER, nullable=False),
    Column('OutCome', String(1, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('QuoteDateTime', DateTime, nullable=False),
    Column('Sto_PK', SmallInteger, nullable=False),
    Column('Quantity', SmallInteger, nullable=False),
    Column('MetalDesc', String(30, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('KaratDesc', String(30, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('TotalWeight', DECIMAL(11, 2), nullable=False),
    Column('StoneWt', DECIMAL(11, 2), nullable=False),
    Column('NetWt', DECIMAL(11, 2), nullable=False),
    Column('LoanOffer', DECIMAL(11, 2), nullable=False),
    Column('BuyOffer', DECIMAL(11, 2), nullable=False),
    Column('LoanSpotRate', DECIMAL(7, 2), nullable=False),
    Column('BuySpotRate', DECIMAL(7, 2), nullable=False),
    Column('CurLoanSpotRate', DECIMAL(7, 3), nullable=False),
    Column('CurBuySpotRate', DECIMAL(7, 3), nullable=False),
    Column('MetalContent', DECIMAL(7, 2), nullable=False),
    Column('SpotPrice', DECIMAL(11, 2), nullable=False),
    Column('Buy_Percent', DECIMAL(7, 3), nullable=False),
    Column('Loan_Percent', DECIMAL(7, 3), nullable=False),
    Column('Wgt_Unit', DECIMAL(11, 2), nullable=False),
    Column('Metal_FK', Integer, nullable=False),
    Column('Karat_FK', Integer, nullable=False),
    Column('BuyLoan', String(1, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('LastUpdatedUsr_id', UNIQUEIDENTIFIER, nullable=False),
    Column('CUS_ID', UNIQUEIDENTIFIER)
)


class RPDRemotePaymentDetail(Base):
    __tablename__ = 'RPD_RemotePaymentDetail'

    rpd_id = Column(UNIQUEIDENTIFIER, primary_key=True, server_default=text("(newid())"))
    rph_id = Column(UNIQUEIDENTIFIER, nullable=False, index=True)
    ticketno = Column(Integer, nullable=False)
    amount = Column(MONEY, nullable=False)


class RPHRemotePaymentHeader(Base):
    __tablename__ = 'RPH_RemotePaymentHeader'

    rph_id = Column(UNIQUEIDENTIFIER, primary_key=True, server_default=text("(newid())"))
    vouchno = Column(CHAR(12, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    sto_pk = Column(SmallInteger, nullable=False)
    date = Column(SMALLDATETIME, nullable=False)
    ispaystore = Column(BIT, nullable=False)
    custno = Column(Integer, nullable=False)
    cus_id = Column(UNIQUEIDENTIFIER, nullable=False, index=True)
    usr_id = Column(UNIQUEIDENTIFIER, nullable=False, index=True)
    usr_lanid = Column(String(8, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, index=True)
    store_id = Column(UNIQUEIDENTIFIER, nullable=False, index=True)
    isrps_id = Column(BIT, nullable=False)


class RPLRepolistPasswordLevel(Base):
    __tablename__ = 'RPL_RepolistPasswordLevels'
    __table_args__ = (
        Index('IX_RPL_ReportKey_CustKey_Sto_PK', 'ReportKey', 'CustKey', 'Sto_PK'),
    )

    RPL_ID = Column(UNIQUEIDENTIFIER, primary_key=True, server_default=text("(newid())"))
    Sto_PK = Column(SmallInteger, nullable=False, server_default=text("(1)"))
    ReportKey = Column(Integer, nullable=False)
    CustKey = Column(CHAR(10, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    AccessLevel = Column(SmallInteger, nullable=False)
    ReportDescription = Column(String(5000, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False,
                               server_default=text("(' ')"))
    LastUpdatedUSR_ID = Column(UNIQUEIDENTIFIER, server_default=text("('F79DBA72-7207-4CCE-A271-FC83D727F283')"))


class RPPHRatesProtPlanHeader(Base):
    __tablename__ = 'RPPH_RatesProtPlanHeader'
    __table_args__ = (
        Index('IX_rpph_planname_sto_pk', 'planname', 'sto_pk'),
    )

    rpph_id = Column(UNIQUEIDENTIFIER, primary_key=True, server_default=text("(newid())"))
    sto_pk = Column(SmallInteger, nullable=False)
    planname = Column(String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    duration = Column(Integer, nullable=False)
    filetoprint = Column(String(250, 'SQL_Latin1_General_CP1_CI_AS'))
    LastUpdatedUSR_ID = Column(UNIQUEIDENTIFIER)


class RPSRemotePaymentStore(Base):
    __tablename__ = 'RPS_RemotePaymentStores'

    rps_id = Column(UNIQUEIDENTIFIER, primary_key=True, server_default=text("(newid())"))
    sto_pk = Column(SmallInteger, nullable=False, index=True)
    name = Column(String(35, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    address1 = Column(String(30, 'SQL_Latin1_General_CP1_CI_AS'))
    address2 = Column(String(30, 'SQL_Latin1_General_CP1_CI_AS'))
    city = Column(String(20, 'SQL_Latin1_General_CP1_CI_AS'))
    state = Column(String(2, 'SQL_Latin1_General_CP1_CI_AS'))
    zip = Column(String(10, 'SQL_Latin1_General_CP1_CI_AS'))
    phone = Column(String(14, 'SQL_Latin1_General_CP1_CI_AS'))


t_RemindLast = Table(
    'RemindLast', metadata,
    Column('rem_pk', Integer, nullable=False),
    Column('Sto_pk', SmallInteger, nullable=False),
    Column('TicketNum', Integer, nullable=False),
    Column('remindDate', DateTime),
    Column('AddAmt', MONEY, nullable=False),
    Column('AddDays', SmallInteger, nullable=False),
    Column('REM_id', UNIQUEIDENTIFIER, unique=True, server_default=text("(newid())")),
    Index('IDX_RemindLast_Sto_PK_RemindDate', 'Sto_pk', 'remindDate')
)


class SASScrapAllSetup(Base):
    __tablename__ = 'SAS_ScrapAllSetup'
    __table_args__ = (
        Index('IX_SAS_ScrapAllSetup_metalkarat', 'metal_id', 'karat_id'),
    )

    sas_id = Column(UNIQUEIDENTIFIER, primary_key=True, server_default=text("(newid())"))
    sto_pk = Column(Integer, nullable=False, index=True)
    metal_id = Column(UNIQUEIDENTIFIER)
    karat_id = Column(UNIQUEIDENTIFIER)
    stone_id = Column(UNIQUEIDENTIFIER)
    scrap_id = Column(UNIQUEIDENTIFIER, nullable=False)
    isstone = Column(BIT, nullable=False)


t_SI_SplitItems = Table(
    'SI_SplitItems', metadata,
    Column('SI_ID', UNIQUEIDENTIFIER, nullable=False, server_default=text("(newid())")),
    Column('SplitFromItems_ID', UNIQUEIDENTIFIER, nullable=False, index=True),
    Column('NewItems_ID', UNIQUEIDENTIFIER, nullable=False, index=True),
    Column('Active', BIT, nullable=False, server_default=text("(1)"))
)

t_SS_4473 = Table(
    'SS_4473', metadata,
    Column('SS_4473_ID', UNIQUEIDENTIFIER, nullable=False, server_default=text("(newid())")),
    Column('STO_PK', SmallInteger, nullable=False, server_default=text("(1)")),
    Column('ATF4473NUM', Integer, nullable=False, server_default=text("(0)")),
    Index('IDX_SS_4473', 'STO_PK', 'ATF4473NUM', unique=True)
)

t_SS_CheckNum = Table(
    'SS_CheckNum', metadata,
    Column('SS_CheckNum_PK_ID', UNIQUEIDENTIFIER, nullable=False, server_default=text("(newid())")),
    Column('STO_PK', SmallInteger, nullable=False, server_default=text("(1)")),
    Column('CheckNum', Integer, nullable=False, server_default=text("(0)")),
    Index('IDX_SS_CheckNum', 'STO_PK', 'CheckNum', unique=True)
)

t_SS_Cust = Table(
    'SS_Cust', metadata,
    Column('SS_Cust_ID', UNIQUEIDENTIFIER, nullable=False, server_default=text("(newid())")),
    Column('STO_PK', SmallInteger, nullable=False, server_default=text("(1)")),
    Column('Cus_PK', Integer, nullable=False, server_default=text("(0)")),
    Index('IDX_SS_Cust', 'STO_PK', 'Cus_PK', unique=True)
)

t_SS_CustPic_PK = Table(
    'SS_CustPic_PK', metadata,
    Column('SS_CustPic_PK_ID', UNIQUEIDENTIFIER, nullable=False, server_default=text("(newid())")),
    Column('STO_PK', SmallInteger, nullable=False, server_default=text("(1)")),
    Column('CustPic_Pk', Integer, nullable=False, server_default=text("(0)")),
    Index('IDX_SS_CustPic_PK', 'STO_PK', 'CustPic_Pk', unique=True)
)

t_SS_Detail_G = Table(
    'SS_Detail_G', metadata,
    Column('SS_Detail_G_ID', UNIQUEIDENTIFIER, nullable=False, server_default=text("(newid())")),
    Column('STO_PK', SmallInteger, nullable=False, server_default=text("(1)")),
    Column('Detail_G', Integer, nullable=False, server_default=text("(0)")),
    Index('IDX_SS_Detail_G', 'STO_PK', 'Detail_G', unique=True)
)

t_SS_Detail_J = Table(
    'SS_Detail_J', metadata,
    Column('SS_Detail_J_ID', UNIQUEIDENTIFIER, nullable=False, server_default=text("(newid())")),
    Column('STO_PK', SmallInteger, nullable=False, server_default=text("(1)")),
    Column('Detail_J', Integer, nullable=False, server_default=text("(0)")),
    Index('IDX_SS_Detail_J', 'STO_PK', 'Detail_J', unique=True)
)

t_SS_Gunlog = Table(
    'SS_Gunlog', metadata,
    Column('SS_Gunlog_ID', UNIQUEIDENTIFIER, nullable=False, server_default=text("(newid())")),
    Column('STO_PK', SmallInteger, nullable=False, server_default=text("(1)")),
    Column('GunLogNum', Integer, nullable=False, server_default=text("(0)")),
    Index('IDX_SS_Gunlog', 'STO_PK', 'GunLogNum', unique=True)
)

t_SS_Holdcon_PK = Table(
    'SS_Holdcon_PK', metadata,
    Column('SS_Holdcon_PK_ID', UNIQUEIDENTIFIER, nullable=False, server_default=text("(newid())")),
    Column('STO_PK', SmallInteger, nullable=False, server_default=text("(1)")),
    Column('HoldCon_PK', Integer, nullable=False, server_default=text("(0)")),
    Index('IDX_SS_Holdcon_PK', 'STO_PK', 'HoldCon_PK', unique=True)
)

t_SS_Invent = Table(
    'SS_Invent', metadata,
    Column('SS_Invent_ID', UNIQUEIDENTIFIER, nullable=False, server_default=text("(newid())")),
    Column('STO_PK', SmallInteger, nullable=False, server_default=text("(1)")),
    Column('InvNum', Integer, nullable=False, server_default=text("(0)")),
    Index('IDX_SS_Invent', 'STO_PK', 'InvNum', unique=True)
)

t_SS_InventNew = Table(
    'SS_InventNew', metadata,
    Column('SS_InventNew_ID', UNIQUEIDENTIFIER, nullable=False, server_default=text("(newid())")),
    Column('STO_PK', SmallInteger, nullable=False, server_default=text("(1)")),
    Column('InvNumNew', Integer, nullable=False, server_default=text("(0)")),
    Index('IDX_SS_InventNew', 'STO_PK', 'InvNumNew', unique=True)
)

t_SS_Item = Table(
    'SS_Item', metadata,
    Column('SS_Item_ID', UNIQUEIDENTIFIER, nullable=False, server_default=text("(newid())")),
    Column('STO_PK', SmallInteger, nullable=False, server_default=text("(1)")),
    Column('Item_PK', Integer, nullable=False, server_default=text("(0)")),
    Index('IDX_SS_Item', 'STO_PK', 'Item_PK', unique=True)
)

t_SS_ItemPic_PK = Table(
    'SS_ItemPic_PK', metadata,
    Column('SS_ItemPic_PK_ID', UNIQUEIDENTIFIER, nullable=False, server_default=text("(newid())")),
    Column('STO_PK', SmallInteger, nullable=False, server_default=text("(1)")),
    Column('ItemPic_PK', Integer, nullable=False, server_default=text("(0)")),
    Index('IDX_SS_ItemPic_PK', 'STO_PK', 'ItemPic_PK', unique=True)
)

t_SS_LC_PK = Table(
    'SS_LC_PK', metadata,
    Column('SS_LC_PK_ID', UNIQUEIDENTIFIER, nullable=False, server_default=text("(newid())")),
    Column('STO_PK', SmallInteger, nullable=False, server_default=text("(1)")),
    Column('LC_PK', Integer, nullable=False, server_default=text("(0)")),
    Index('IDX_SS_LC_PK', 'STO_PK', 'LC_PK', unique=True)
)

t_SS_Levels_PK = Table(
    'SS_Levels_PK', metadata,
    Column('SS_Levels_PK_ID', UNIQUEIDENTIFIER, nullable=False, server_default=text("(newid())")),
    Column('STO_PK', SmallInteger, nullable=False, server_default=text("(1)")),
    Column('Levels_PK', Integer, nullable=False, server_default=text("(0)")),
    Index('IDX_SS_Levels_PK', 'STO_PK', 'Levels_PK', unique=True)
)

t_SS_Pawn = Table(
    'SS_Pawn', metadata,
    Column('SS_Pawn_ID', UNIQUEIDENTIFIER, nullable=False, server_default=text("(newid())")),
    Column('STO_PK', SmallInteger, nullable=False, server_default=text("(1)")),
    Column('TicketNum', Integer, nullable=False, server_default=text("(0)")),
    Index('IDX_SS_Pawn', 'STO_PK', 'TicketNum', unique=True)
)

t_SS_Purchas = Table(
    'SS_Purchas', metadata,
    Column('SS_Purchas_ID', UNIQUEIDENTIFIER, nullable=False, server_default=text("(newid())")),
    Column('STO_PK', SmallInteger, nullable=False, server_default=text("(1)")),
    Column('PurchasNum', Integer, nullable=False, server_default=text("(0)")),
    Index('IDX_SS_Purchas', 'STO_PK', 'PurchasNum', unique=True)
)

t_SS_Sale = Table(
    'SS_Sale', metadata,
    Column('SS_Sale_ID', UNIQUEIDENTIFIER, nullable=False, server_default=text("(newid())")),
    Column('STO_PK', SmallInteger, nullable=False, server_default=text("(1)")),
    Column('ReceiptNum', Integer, nullable=False, server_default=text("(0)")),
    Index('IDX_SS_Sale', 'STO_PK', 'ReceiptNum', unique=True)
)

t_SS_Users = Table(
    'SS_Users', metadata,
    Column('SS_Users_ID', UNIQUEIDENTIFIER, nullable=False, server_default=text("(newid())")),
    Column('STO_PK', SmallInteger, nullable=False, server_default=text("(1)")),
    Column('EmpNum', Integer, nullable=False, server_default=text("(0)")),
    Index('IDX_SS_Users', 'STO_PK', 'EmpNum', unique=True)
)

t_SS_Vend = Table(
    'SS_Vend', metadata,
    Column('SS_Vend_ID', UNIQUEIDENTIFIER, nullable=False, server_default=text("(newid())")),
    Column('STO_PK', SmallInteger, nullable=False, server_default=text("(1)")),
    Column('VendNum', Integer, nullable=False, server_default=text("(0)")),
    Index('IDX_SS_Vend', 'STO_PK', 'VendNum', unique=True)
)


class SYCLSysColumn(Base):
    __tablename__ = 'SYCL_SysColumns'

    sycl_id = Column(UNIQUEIDENTIFIER, primary_key=True, server_default=text("(newid())"))
    sycl_table = Column(String(50, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    sycl_column = Column(String(50, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    sycl_prompt = Column(String(100, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)


class SoldAuction(Base):
    __tablename__ = 'SoldAuction'

    sa_id = Column(UNIQUEIDENTIFIER, primary_key=True, server_default=text("(newid())"))
    sld_id = Column(UNIQUEIDENTIFIER, nullable=False, index=True)
    aui_id = Column(UNIQUEIDENTIFIER, nullable=False, index=True)


t_Soldview = Table(
    'Soldview', metadata,
    Column('TICKETNUM', Integer),
    Column('STO_PK', SmallInteger),
    Column('CUS_FK', Integer),
    Column('DATEin', SMALLDATETIME),
    Column('DATEout', SMALLDATETIME),
    Column('usr_fk', Integer),
    Column('srvchgamt', MONEY),
    Column('deposit', MONEY),
    Column('TransDate', DateTime),
    Column('SaleAmt', MONEY),
    Column('Taxable', MONEY),
    Column('CountyTaxable', MONEY),
    Column('TAX', MONEY),
    Column('type', CHAR(1, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('sstatus', CHAR(1, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('status2', String(25, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('istatus', CHAR(1, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('INVNUM', String(14, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('NUMBERSOLD', Numeric(9, 2), nullable=False),
    Column('RETURNSOLD', DateTime),
    Column('AMOUNT', MONEY, nullable=False),
    Column('DESCRIPT', String(254, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('COST', MONEY, nullable=False),
    Column('CountyTaxExempt', BIT, nullable=False),
    Column('TAXEXEMPT', BIT, nullable=False),
    Column('NEWITEM', BIT),
    Column('on_consign', BIT),
    Column('consignor', Integer),
    Column('vendor', Integer),
    Column('LEVEL1_FK', Integer),
    Column('Lv1_ID', UNIQUEIDENTIFIER),
    Column('csource', String(35, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('LEVEL2_FK', Integer),
    Column('Lv2_ID', UNIQUEIDENTIFIER),
    Column('LEVEL5_FK', Integer),
    Column('Lv5_ID', UNIQUEIDENTIFIER),
    Column('modelnum', String(20, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('items_pk', Integer, nullable=False),
    Column('VEN_PK', Integer),
    Column('VEN_COMPANY', String(35, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('USR_LANID', String(8, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('ven_phone', String(13, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('AuctionEntry', BIT),
    Column('level3_fk', Integer),
    Column('lv3_id', UNIQUEIDENTIFIER),
    Column('level4_fk', Integer),
    Column('lv4_id', UNIQUEIDENTIFIER),
    Column('Items_ID', UNIQUEIDENTIFIER),
    Column('sld_id', UNIQUEIDENTIFIER),
    Column('sit_id', UNIQUEIDENTIFIER),
    Column('salesloc', String(1, 'SQL_Latin1_General_CP1_CI_AS'))
)


class SplitCom(Base):
    __tablename__ = 'SplitCom'
    __table_args__ = (
        Index('IX_sold_fk', 'ticketnum', 'sto_pk'),
    )

    spc_id = Column(UNIQUEIDENTIFIER, primary_key=True, server_default=text("(newid())"))
    spc_pk = Column(Integer, nullable=False)
    sto_pk = Column(SmallInteger, nullable=False)
    ticketnum = Column(Integer, nullable=False)
    usr_fk = Column(Integer, index=True)
    usr_percent = Column(Float(53))


t_SpotPrice = Table(
    'SpotPrice', metadata,
    Column('SpotPrice_PK', Integer, nullable=False, index=True),
    Column('Metal_FK', Integer, nullable=False),
    Column('Spot_Price', DECIMAL(11, 4), nullable=False),
    Column('Sto_PK', SmallInteger, nullable=False),
    Column('DefaultSpot', BIT, nullable=False),
    Column('LastUpdated', DateTime, nullable=False),
    Column('LastUpdatedUsr_id', UNIQUEIDENTIFIER, nullable=False)
)

t_SpotRates = Table(
    'SpotRates', metadata,
    Column('SpotRates_PK', Integer, nullable=False, index=True),
    Column('Metal_FK', Integer, nullable=False),
    Column('Karat_FK', Integer, nullable=False),
    Column('Sto_PK', SmallInteger, nullable=False),
    Column('Metal_Content', DECIMAL(7, 3)),
    Column('Buy_Percent', DECIMAL(7, 3)),
    Column('Loan_Percent', DECIMAL(7, 3)),
    Column('LastUpdatedUsr_id', UNIQUEIDENTIFIER, nullable=False)
)


class StatCode(Base):
    __tablename__ = 'StatCode'
    __table_args__ = (
        Index('IDX_StatCode_Trans_Status', 'trans', 'status'),
    )

    cType = Column(String(8, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("('')"))
    trans = Column(String(6, 'SQL_Latin1_General_CP1_CI_AS'), primary_key=True, nullable=False,
                   server_default=text("('')"))
    status = Column(String(1, 'SQL_Latin1_General_CP1_CI_AS'), primary_key=True, nullable=False,
                    server_default=text("('')"))
    DESCRIPT = Column(String(25, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("('')"))
    ReportDesc = Column(String(25, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("('')"))
    SAT_id = Column(UNIQUEIDENTIFIER, server_default=text("(newid())"))


t_StatusCodeGroups = Table(
    'StatusCodeGroups', metadata,
    Column('SCG_Num', Integer, nullable=False),
    Column('TableName', String(20, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('TranType', String(15, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('Trans', String(1, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('Status', String(1, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('Group1', Integer),
    Column('Group2', Integer),
    Column('Group3', Integer),
    Column('Group4', Integer),
    Index('IDX_StatusCodeGroups_1', 'Group1', 'Status'),
    Index('IDX_StatusCodeGroups_3', 'Status', 'Group1'),
    Index('IDX_StatusCodeGroups_2', 'Status', 'TranType')
)

t_SysInfo2 = Table(
    'SysInfo2', metadata,
    Column('STO_PK', SmallInteger, nullable=False, unique=True, server_default=text("(0)")),
    Column('ENCODECENT', BIT, nullable=False, server_default=text("(0)")),
    Column('FLCODES', BIT, nullable=False, server_default=text("(0)")),
    Column('EXTENDTRAN', BIT, nullable=False, server_default=text("(0)")),
    Column('POLICEOPTION', TINYINT, nullable=False, server_default=text("(1)")),
    Column('POLICETYPE', TINYINT, nullable=False, server_default=text("(1)")),
    Column('POLICETXT', TINYINT, nullable=False, server_default=text("(1)")),
    Column('POLICECHAR', String(1, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("('')")),
    Column('POLICEDATE', DateTime),
    Column('POLICESSNUM', BIT, nullable=False, server_default=text("(0)")),
    Column('POLICEAMT', BIT, nullable=False, server_default=text("(0)")),
    Column('POLICEEMPLOYER', BIT, nullable=False, server_default=text("(0)")),
    Column('POLICEDISK', String(254, 'SQL_Latin1_General_CP1_CI_AS'), server_default=text("('')")),
    Column('POLITEMAMT', BIT, nullable=False, server_default=text("(0)")),
    Column('POLTOTLAMT', BIT, nullable=False, server_default=text("(0)")),
    Column('POLREDCONT', BIT, nullable=False, server_default=text("(0)")),
    Column('POLREDDAYS', Float(53), nullable=False, server_default=text("(0)")),
    Column('POLREDWEND', BIT, nullable=False, server_default=text("(0)")),
    Column('USEBINNUMS', BIT, nullable=False, server_default=text("(0)")),
    Column('PRINTCHRGS', BIT, nullable=False, server_default=text("(0)")),
    Column('GUNPRICES', BIT, nullable=False, server_default=text("(0)")),
    Column('GOLDWEIGHT', String(1, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("('')")),
    Column('GOLDWTSale', String(1, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("('')")),
    Column('REPAIRORD', BIT, nullable=False, server_default=text("(0)")),
    Column('REPAIRLABL', BIT, nullable=False, server_default=text("(0)")),
    Column('PRINTDTOUT', BIT, nullable=False, server_default=text("(0)")),
    Column('VarStorageFee', BIT, nullable=False, server_default=text("(0)")),
    Column('CHECKCASH', BIT, nullable=False, server_default=text("(0)")),
    Column('GL', BIT, nullable=False, server_default=text("(0)")),
    Column('StorageFeePer', BIT, nullable=False, server_default=text("(0)")),
    Column('SHOWCUST', BIT, nullable=False, server_default=text("(0)")),
    Column('V1', Float(53), nullable=False, server_default=text("(0)")),
    Column('V2', Float(53), nullable=False, server_default=text("(0)")),
    Column('V3', Float(53), nullable=False, server_default=text("(0)")),
    Column('V4', Float(53), nullable=False, server_default=text("(0)")),
    Column('INITSTART', BIT, nullable=False, server_default=text("(0)")),
    Column('RECONCLCHK', BIT, nullable=False, server_default=text("(0)")),
    Column('RINGLABEL', BIT, nullable=False, server_default=text("(0)")),
    Column('MONTHCHRG', BIT, nullable=False, server_default=text("(0)")),
    Column('DEPOSITTAX', SmallInteger, nullable=False, server_default=text("(1)")),
    Column('ATFCUST', BIT, nullable=False, server_default=text("(0)")),
    Column('DEFAULTRAT', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("('')")),
    Column('FEEMONTH', Float(53), nullable=False, server_default=text("(0)")),
    Column('FEEMONTH2', Float(53), nullable=False, server_default=text("(0)")),
    Column('PRORATE', BIT, nullable=False, server_default=text("(0)")),
    Column('PROSTART', Float(53), nullable=False, server_default=text("(0)")),
    Column('PROUPTODAY', Float(53), nullable=False, server_default=text("(0)")),
    Column('PROMINIMUM', Float(53), nullable=False, server_default=text("(0)")),
    Column('PAWNDAYSG', Float(53), nullable=False, server_default=text("(0)")),
    Column('OPTIONDAYG', Float(53), nullable=False, server_default=text("(0)")),
    Column('PAWNDAYSJ', Float(53), nullable=False, server_default=text("(0)")),
    Column('OPTIONDAYJ', Float(53), nullable=False, server_default=text("(0)")),
    Column('PAYROLL', BIT, nullable=False, server_default=text("(0)")),
    Column('V5', Float(53), nullable=False, server_default=text("(0)")),
    Column('V6', Float(53), nullable=False, server_default=text("(0)")),
    Column('V9', Float(53), nullable=False, server_default=text("(0)")),
    Column('V10', Float(53), nullable=False, server_default=text("(0)")),
    Column('PRORATSCHG', BIT, nullable=False, server_default=text("(0)")),
    Column('ENCODEREPT', String(1, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("(0)")),
    Column('ENCODEDORP', BIT, nullable=False, server_default=text("(0)")),
    Column('SERVROUND', BIT, nullable=False, server_default=text("(0)")),
    Column('BUYHOLDG', SmallInteger, nullable=False, server_default=text("(0)")),
    Column('BUYHOLDJ', SmallInteger, nullable=False, server_default=text("(0)")),
    Column('HAWAIIDATE', BIT, nullable=False, server_default=text("(0)")),
    Column('HAWAIIAMT', BIT, nullable=False, server_default=text("(0)")),
    Column('POLTIKITMS', Float(53), nullable=False, server_default=text("(0)")),
    Column('ONEITMTIKP', BIT, nullable=False, server_default=text("(0)")),
    Column('ONEITMTIKB', BIT, nullable=False, server_default=text("(0)")),
    Column('PULLADDSRV', TINYINT, nullable=False, server_default=text("(0)")),
    Column('GLDUNCLACT', SmallInteger, nullable=False, server_default=text("(0)")),
    Column('PULLGRACE', Float(53), nullable=False, server_default=text("(0)")),
    Column('GUNBUYBACK', Float(53), nullable=False, server_default=text("(0)")),
    Column('PREFPAWN', String(4, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("('')")),
    Column('PREFPOL', String(4, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("('')")),
    Column('PREFBUY', String(4, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("('')")),
    Column('PREFREPAWN', String(4, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("('')")),
    Column('REMINDER', SMALLDATETIME),
    Column('EATTAX', BIT, nullable=False, server_default=text("(0)")),
    Column('PAWNPERIOD', BIT, nullable=False, server_default=text("(0)")),
    Column('MARKUPG', Float(53), nullable=False, server_default=text("(0)")),
    Column('MARKUPJ', Float(53), nullable=False, server_default=text("(0)")),
    Column('MARKUPO', Float(53), nullable=False, server_default=text("(0)")),
    Column('MINSALMRKG', Float(53), nullable=False, server_default=text("(0)")),
    Column('MINSALMRKJ', Float(53), nullable=False, server_default=text("(0)")),
    Column('MINSALMRKO', Float(53), nullable=False, server_default=text("(0)")),
    Column('PAWNBUYNUM', BIT, nullable=False, server_default=text("(0)")),
    Column('PAWNBUYDAT', BIT, nullable=False, server_default=text("(0)")),
    Column('PAWRECBLAN', BIT, nullable=False, server_default=text("(0)")),
    Column('PAWRECBLPG', BIT, nullable=False, server_default=text("(0)")),
    Column('LAYREMIND', SMALLDATETIME),
    Column('CASHDRAWER', BIT, nullable=False, server_default=text("(0)")),
    Column('uploadcom', TINYINT, nullable=False, server_default=text("(2)")),
    Column('CASHSTRING', String(40, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("('')")),
    Column('TRANSFREXT', BIT, nullable=False, server_default=text("(0)")),
    Column('TRANSFRDRV', String(1, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("('')")),
    Column('REPPAYOVER', String(1, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("('')")),
    Column('SCRAPOTHER', BIT, nullable=False, server_default=text("(0)")),
    Column('FULLSALCUS', BIT, nullable=False, server_default=text("(0)")),
    Column('GENERATEID', BIT, nullable=False, server_default=text("(0)")),
    Column('SERVFEEPER', BIT, nullable=False, server_default=text("(0)")),
    Column('SERVFEEPER2', BIT, nullable=False, server_default=text("(0)")),
    Column('SERVFEEPRO1', BIT, nullable=False, server_default=text("(0)")),
    Column('SERVFEEPRO2', BIT, nullable=False, server_default=text("(0)")),
    Column('RATEONEPER', BIT, nullable=False, server_default=text("(0)")),
    Column('RATEFEEPER', BIT, nullable=False, server_default=text("(0)")),
    Column('RATEONEPRO', BIT, nullable=False, server_default=text("(0)")),
    Column('RATEFEEPRO', BIT, nullable=False, server_default=text("(0)")),
    Column('TEXASMINPR', MONEY, nullable=False, server_default=text("(0)")),
    Column('UPDTWHAT', String(10, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("('')")),
    Column('UPDTDATE', SMALLDATETIME, nullable=False, server_default=text("(1 / 1 / 2000)")),
    Column('EMPDRWR', BIT, nullable=False, server_default=text("(0)")),
    Column('EMPDRWRDEV', BIT, nullable=False, server_default=text("(0)")),
    Column('PAYREPAWN', BIT, nullable=False, server_default=text("(0)")),
    Column('RESETONEFE', BIT, nullable=False, server_default=text("(0)")),
    Column('NEWTICKNUM', BIT, nullable=False, server_default=text("(0)")),
    Column('REPAWNTICK', BIT, nullable=False, server_default=text("(0)")),
    Column('HANDGUNPWN', BIT, nullable=False, server_default=text("(0)")),
    Column('HANDGUNDPW', BIT, nullable=False, server_default=text("(0)")),
    Column('ALLOWPWNOP', BIT, nullable=False, server_default=text("(0)")),
    Column('POLICENAME', String(8, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("('')")),
    Column('CALCCHANGE', BIT, nullable=False, server_default=text("(0)")),
    Column('SALEENCOST', BIT, nullable=False, server_default=text("(0)")),
    Column('CUSTCRED', BIT, nullable=False, server_default=text("(0)")),
    Column('PAWNDATPAS', SmallInteger, nullable=False, server_default=text("(1)")),
    Column('COMBLABEL', BIT, nullable=False, server_default=text("(0)")),
    Column('POLICEEXT', String(3, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("('')")),
    Column('SY2_id', UNIQUEIDENTIFIER, server_default=text("(newid())")),
    Column('RedeemServMinChg', MONEY, nullable=False, server_default=text("(3.0000)")),
    Column('OneTimeMinChg', MONEY, nullable=False, server_default=text("(2.0000)")),
    Column('OneTimeMaxChg', MONEY, nullable=False, server_default=text("(100.0000)")),
    Column('MonthlyMinChg', MONEY, nullable=False, server_default=text("(2.0000)")),
    Column('ProrateFirearmFee', BIT, nullable=False, server_default=text("(1)")),
    Column('FirearmFeeRedeemOnly', BIT, nullable=False, server_default=text("(0)")),
    Column('FLFirearm_Lvl', TINYINT, nullable=False, server_default=text("(6)")),
    Column('UndoPull_Lvl', TINYINT, nullable=False, server_default=text("(3)")),
    Column('LastUpdatedUSR_ID', UNIQUEIDENTIFIER),
    Column('PMSG_ID', UNIQUEIDENTIFIER),
    Column('ShareLookups', BIT)
)

t_SysInfo3_703 = Table(
    'SysInfo3_703', metadata,
    Column('STO_PK', SmallInteger, nullable=False),
    Column('TicketNum', Integer, nullable=False),
    Column('PolTicNum', Integer, nullable=False),
    Column('PurchasNum', Integer, nullable=False),
    Column('ReceiptNum', Integer, nullable=False),
    Column('InvNum', Integer, nullable=False),
    Column('Cus_PK', Integer, nullable=False),
    Column('EndPolNum', Integer, nullable=False),
    Column('PolTicNum2', Integer, nullable=False),
    Column('EndPolNum2', Integer, nullable=False),
    Column('GunLogNum', Integer, nullable=False),
    Column('CheckNum', Integer, nullable=False),
    Column('VendNum', Integer, nullable=False),
    Column('Item_PK', Integer, nullable=False),
    Column('Pawn_PK', Integer, nullable=False),
    Column('GLtrans', Integer, nullable=False),
    Column('Levels_PK', Integer, nullable=False),
    Column('LC_PK', Integer, nullable=False),
    Column('jTypes_PK', Integer, nullable=False),
    Column('MemoNum', Integer, nullable=False),
    Column('ATF4473NUM', Integer, nullable=False),
    Column('Detail_G', Integer, nullable=False),
    Column('Detail_J', Integer, nullable=False),
    Column('EmpNum', Integer, nullable=False),
    Column('CustPic_Pk', Integer, nullable=False),
    Column('CustThum_PK', Integer, nullable=False),
    Column('ItemPic_Pk', Integer, nullable=False),
    Column('HoldCon_PK', Integer, nullable=False),
    Column('SY3_id', UNIQUEIDENTIFIER)
)

t_SysInfo4 = Table(
    'SysInfo4', metadata,
    Column('sto_pk', SmallInteger, nullable=False, unique=True, server_default=text("(1)")),
    Column('DifDayFee', BIT, nullable=False, server_default=text("(0)")),
    Column('FeeDaily', Float(53), nullable=False, server_default=text("(0)")),
    Column('TrackInsCost', BIT, nullable=False, server_default=text("(0)")),
    Column('InsCostPawn', BIT, nullable=False, server_default=text("(0)")),
    Column('AutoTimeOut', Integer, nullable=False, server_default=text("(0)")),
    Column('LastRunDate', SMALLDATETIME),
    Column('LastRunPawn', Integer, nullable=False, server_default=text("(0)")),
    Column('LastRunPur', Integer, nullable=False, server_default=text("(0)")),
    Column('GunFeeEachPeriod', BIT, nullable=False, server_default=text("(0)")),
    Column('GunFeeAmt', MONEY, nullable=False, server_default=text("(0.0)")),
    Column('PrepFeeAmt', MONEY, nullable=False, server_default=text("(0.0)")),
    Column('TicketFeeAmt', MONEY, nullable=False, server_default=text("(0.0)")),
    Column('LayDayExtn', SmallInteger, nullable=False, server_default=text("(0)")),
    Column('LayTotTaxD', BIT, nullable=False, server_default=text("(0)")),
    Column('LayBin', BIT, nullable=False, server_default=text("(0)")),
    Column('LayCred', SmallInteger, nullable=False, server_default=text("(50)")),
    Column('MDays', SmallInteger, nullable=False, server_default=text("(0)")),
    Column('MChgx', BIT, nullable=False, server_default=text("(0)")),
    Column('MMrkG', Float(24), nullable=False, server_default=text("(0)")),
    Column('MMrkJ', Float(24), nullable=False, server_default=text("(0)")),
    Column('MMrkO', Float(24), nullable=False, server_default=text("(0)")),
    Column('CrdRct', BIT, nullable=False, server_default=text("(0)")),
    Column('CSPerc', Float(24), nullable=False, server_default=text("(0)")),
    Column('SamePerc', BIT, nullable=False, server_default=text("(0)")),
    Column('CSDays', SmallInteger, nullable=False, server_default=text("(0)")),
    Column('SameDays', BIT, nullable=False, server_default=text("(0)")),
    Column('CTType', BIT, nullable=False, server_default=text("(0)")),
    Column('GunHoldLbl', BIT, nullable=False, server_default=text("(0)")),
    Column('NonInvPass', SmallInteger, nullable=False, server_default=text("(0)")),
    Column('ExemptPass', SmallInteger, nullable=False, server_default=text("(0)")),
    Column('ILblCstSal', BIT, nullable=False, server_default=text("(0)")),
    Column('UseTimeClock', BIT, nullable=False, server_default=text("(0)")),
    Column('PrtTimeSlip', BIT, nullable=False, server_default=text("(0)")),
    Column('Ovr_NonInvItem', TINYINT, nullable=False, server_default=text("(0)")),
    Column('Ovr_TaxExempt', TINYINT, nullable=False, server_default=text("(0)")),
    Column('Ovr_MinSalePrice', TINYINT, nullable=False, server_default=text("(0)")),
    Column('Ovr_SvcChg', TINYINT, nullable=False, server_default=text("(0)")),
    Column('Ovr_Redeem', TINYINT, nullable=False, server_default=text("(0)")),
    Column('Ovr_PrinLower', TINYINT, nullable=False, server_default=text("(0)")),
    Column('Ovr_ChgRate', TINYINT, nullable=False, server_default=text("(0)")),
    Column('Auto_4473', BIT, nullable=False, server_default=text("(0)")),
    Column('ShowRptCode', BIT, nullable=False, server_default=text("(0)")),
    Column('Ovr_Cus_Credit', SmallInteger, nullable=False, server_default=text("(5)")),
    Column('PrtBlankLbl', BIT, nullable=False, server_default=text("(0)")),
    Column('EncCostPawnBuyLbl', BIT, nullable=False, server_default=text("(1)")),
    Column('EncCostMinInvLbl', SmallInteger, nullable=False, server_default=text("(1)")),
    Column('ProRt', BIT, nullable=False, server_default=text("(1)")),
    Column('NewProrate', BIT, nullable=False, server_default=text("(1)")),
    Column('StratorAmt', BIT, nullable=False, server_default=text("(1)")),
    Column('ProPercent', Float(24), nullable=False, server_default=text("(0)")),
    Column('NewProStrt', SmallInteger, nullable=False, server_default=text("(0)")),
    Column('NewProEnd', SmallInteger, nullable=False, server_default=text("(0)")),
    Column('NewProDays', SmallInteger, nullable=False, server_default=text("(0)")),
    Column('NewProRedm', BIT, nullable=False, server_default=text("(1)")),
    Column('NewProServ', BIT, nullable=False, server_default=text("(1)")),
    Column('NewProOne', BIT, nullable=False, server_default=text("(1)")),
    Column('NewProFee1', BIT, nullable=False, server_default=text("(1)")),
    Column('NewProFee2', BIT, nullable=False, server_default=text("(1)")),
    Column('ProMinPeriod', Float(53), nullable=False, server_default=text("(0.00)")),
    Column('ServiceTax', BIT, nullable=False, server_default=text("(0)")),
    Column('UsePrevPrin', BIT, nullable=False, server_default=text("(0)")),
    Column('Ovr_ChgNote', TINYINT, nullable=False, server_default=text("(1)")),
    Column('Ovr_ChgDatO', TINYINT, nullable=False, server_default=text("(1)")),
    Column('PLblDateIO', SmallInteger, nullable=False, server_default=text("(1)")),
    Column('PullToInv', BIT, nullable=False, server_default=text("(1)")),
    Column('OnlyTitle', BIT, nullable=False, server_default=text("(0)")),
    Column('ReqLateChrg', BIT, nullable=False, server_default=text("(0)")),
    Column('LatePeriods', TINYINT, nullable=False, server_default=text("(0)")),
    Column('LateGraceDays', TINYINT, nullable=False, server_default=text("(0)")),
    Column('LateSingleDaily', TINYINT, nullable=False, server_default=text("(1)")),
    Column('LateDollarPercent', TINYINT, nullable=False, server_default=text("(1)")),
    Column('LateAmount', MONEY, nullable=False, server_default=text("(0.00)")),
    Column('Report_Lvl', SmallInteger, nullable=False, server_default=text("(6)")),
    Column('RetSvcChg_FL', BIT, nullable=False, server_default=text("(0)")),
    Column('NewTicBackPay', BIT, nullable=False, server_default=text("(0)")),
    Column('LostTickRcpt', BIT, nullable=False, server_default=text("(0)")),
    Column('txMemorandum', BIT, nullable=False, server_default=text("(0)")),
    Column('AskPawnRcpt', BIT, nullable=False, server_default=text("(0)")),
    Column('PawnPayBlank', BIT, nullable=False, server_default=text("(0)")),
    Column('PawnPayTag', BIT, nullable=False, server_default=text("(0)")),
    Column('NoResetPeriods', TINYINT, nullable=False, server_default=text("(0)")),
    Column('ResetBackPay', BIT, nullable=False, server_default=text("(0)")),
    Column('ResetPartialPay', BIT, nullable=False, server_default=text("(0)")),
    Column('ChgCustonPay', BIT, nullable=False, server_default=text("(0)")),
    Column('PrtPawnChks', BIT, nullable=False, server_default=text("(0)")),
    Column('PrtBuyChks', BIT, nullable=False, server_default=text("(0)")),
    Column('PrtSeparateChks', BIT, nullable=False, server_default=text("(0)")),
    Column('PrtAmountChks', MONEY, nullable=False, server_default=text("(0.00)")),
    Column('AskPrtChks', BIT, nullable=False, server_default=text("(0)")),
    Column('PrtChkName', String(15, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("('')")),
    Column('NumPawnTic', TINYINT, nullable=False, server_default=text("(1)")),
    Column('NumBuyTic', TINYINT, nullable=False, server_default=text("(1)")),
    Column('NumReceipts', TINYINT, nullable=False, server_default=text("(1)")),
    Column('NumPawnReceipts', TINYINT, nullable=False, server_default=text("(1)")),
    Column('Bin_Lvl', TINYINT, nullable=False, server_default=text("(0)")),
    Column('Buy_Lvl', TINYINT, nullable=False, server_default=text("(0)")),
    Column('DateOut_Lvl', TINYINT, nullable=False, server_default=text("(0)")),
    Column('ChgNote_Lvl', TINYINT, nullable=False, server_default=text("(0)")),
    Column('Void_Lvl', TINYINT, nullable=False, server_default=text("(0)")),
    Column('ChgFees_Lvl', TINYINT, nullable=False, server_default=text("(0)")),
    Column('Increase_Lvl', TINYINT, nullable=False, server_default=text("(0)")),
    Column('UndoPay_Lvl', TINYINT, nullable=False, server_default=text("(0)")),
    Column('ScrapJewelry', BIT, nullable=False, server_default=text("(0)")),
    Column('SplitJewelry', BIT, nullable=False, server_default=text("(0)")),
    Column('SplitOther', BIT, nullable=False, server_default=text("(0)")),
    Column('InvPhys_Lvl', TINYINT, nullable=False, server_default=text("(0)")),
    Column('InvCost_Lvl', TINYINT, nullable=False, server_default=text("(0)")),
    Column('PawnEdit_Lvl', TINYINT, nullable=False, server_default=text("(0)")),
    Column('InvDelete_Lvl', TINYINT, nullable=False, server_default=text("(0)")),
    Column('GoldPrice', MONEY, nullable=False, server_default=text("(0.00)")),
    Column('LastGoldDate', SMALLDATETIME),
    Column('PctSpot', Float(53), nullable=False, server_default=text("(0.00)")),
    Column('GoldKarat1', SmallInteger, nullable=False, server_default=text("(0)")),
    Column('GoldKarat2', SmallInteger, nullable=False, server_default=text("(0)")),
    Column('GoldKarat3', SmallInteger, nullable=False, server_default=text("(0)")),
    Column('GoldKarat4', SmallInteger, nullable=False, server_default=text("(0)")),
    Column('GoldKarat5', SmallInteger, nullable=False, server_default=text("(0)")),
    Column('GoldKarat6', SmallInteger, nullable=False, server_default=text("(0)")),
    Column('GoldKarat7', SmallInteger, nullable=False, server_default=text("(0)")),
    Column('GoldKarat8', SmallInteger, nullable=False, server_default=text("(0)")),
    Column('PctGold1', Float(53), nullable=False, server_default=text("(0.00)")),
    Column('PctGold2', Float(53), nullable=False, server_default=text("(0.00)")),
    Column('PctGold3', Float(53), nullable=False, server_default=text("(0.00)")),
    Column('PctGold4', Float(53), nullable=False, server_default=text("(0.00)")),
    Column('PctGold5', Float(53), nullable=False, server_default=text("(0.00)")),
    Column('PctGold6', Float(53), nullable=False, server_default=text("(0.00)")),
    Column('PctGold7', Float(53), nullable=False, server_default=text("(0.00)")),
    Column('PctGold8', Float(53), nullable=False, server_default=text("(0.00)")),
    Column('POLICEFILENAME', TINYINT, nullable=False, server_default=text("(1)")),
    Column('PoliceOldDBF', BIT, nullable=False, server_default=text("(1)")),
    Column('RepRemind', SMALLDATETIME),
    Column('Dir4BUdata', String(50, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("(' ')")),
    Column('Dir4BUpict', String(50, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("(' ')")),
    Column('JewLabelType', TINYINT, nullable=False, server_default=text("(1)")),
    Column('PrtPettyCashReceipt', BIT, nullable=False, server_default=text("(0)")),
    Column('PrtLgTicketnum', BIT, nullable=False, server_default=text("(0)")),
    Column('PrtPolTiconReset', BIT, nullable=False, server_default=text("(1)")),
    Column('ResetOTFonNewTic', BIT, nullable=False, server_default=text("(1)")),
    Column('ExportPic_Lvl', SmallInteger, nullable=False, server_default=text("(3)")),
    Column('ReqRemindPull', BIT, nullable=False, server_default=text("(0)")),
    Column('Allon1Remind', BIT, nullable=False, server_default=text("(0)")),
    Column('Chrg1Remind', BIT, nullable=False, server_default=text("(0)")),
    Column('duplicateinv_lvl', TINYINT, nullable=False, server_default=text("(1)")),
    Column('SaleSummary', BIT, nullable=False, server_default=text("(0)")),
    Column('LateNumPeriods', SmallInteger, nullable=False, server_default=text("(999)")),
    Column('ClearRemindPay', BIT, nullable=False, server_default=text("(0)")),
    Column('PrtPol1PG', BIT, nullable=False, server_default=text("(1)")),
    Column('PrtPol1PJ', BIT, nullable=False, server_default=text("(1)")),
    Column('PrtPol1PT', BIT, nullable=False, server_default=text("(1)")),
    Column('PrtPol1PO', BIT, nullable=False, server_default=text("(1)")),
    Column('PrtPol1OG', BIT, nullable=False, server_default=text("(1)")),
    Column('PrtPol1OJ', BIT, nullable=False, server_default=text("(1)")),
    Column('PrtPol1OT', BIT, nullable=False, server_default=text("(1)")),
    Column('PrtPol1OO', BIT, nullable=False, server_default=text("(1)")),
    Column('PrtPol1BG', BIT, nullable=False, server_default=text("(1)")),
    Column('PrtPol1BJ', BIT, nullable=False, server_default=text("(1)")),
    Column('PrtPol1BT', BIT, nullable=False, server_default=text("(1)")),
    Column('PrtPol1BO', BIT, nullable=False, server_default=text("(1)")),
    Column('PrtPol2PG', BIT, nullable=False, server_default=text("(1)")),
    Column('PrtPol2PJ', BIT, nullable=False, server_default=text("(1)")),
    Column('PrtPol2PT', BIT, nullable=False, server_default=text("(1)")),
    Column('PrtPol2PO', BIT, nullable=False, server_default=text("(1)")),
    Column('PrtPol2OG', BIT, nullable=False, server_default=text("(1)")),
    Column('PrtPol2OJ', BIT, nullable=False, server_default=text("(1)")),
    Column('PrtPol2OT', BIT, nullable=False, server_default=text("(1)")),
    Column('PrtPol2OO', BIT, nullable=False, server_default=text("(1)")),
    Column('PrtPol2BG', BIT, nullable=False, server_default=text("(1)")),
    Column('PrtPol2BJ', BIT, nullable=False, server_default=text("(1)")),
    Column('PrtPol2BT', BIT, nullable=False, server_default=text("(1)")),
    Column('PrtPol2BO', BIT, nullable=False, server_default=text("(1)")),
    Column('PatriotDate', DateTime),
    Column('ShowPawnDueDate', BIT, nullable=False, server_default=text("(0)")),
    Column('ResetTickChrg', BIT, nullable=False, server_default=text("(0)")),
    Column('ResetPrepChrg', BIT, nullable=False, server_default=text("(0)")),
    Column('ResetGunChrg', BIT, nullable=False, server_default=text("(0)")),
    Column('ResetTickonNewTick', BIT, nullable=False, server_default=text("(0)")),
    Column('ResetPreponNewTick', BIT, nullable=False, server_default=text("(0)")),
    Column('ResetGunonNewTick', BIT, nullable=False, server_default=text("(0)")),
    Column('PrintOnePawnPol1', BIT, nullable=False, server_default=text("(0)")),
    Column('PrintOnePawnPol2', BIT, nullable=False, server_default=text("(0)")),
    Column('PrintOneBuyPol1', BIT, nullable=False, server_default=text("(0)")),
    Column('PrintOneBuyPol2', BIT, nullable=False, server_default=text("(0)")),
    Column('NumPawnItemsOnPol', Integer, nullable=False, server_default=text("(1)")),
    Column('HideGraphicName', BIT, nullable=False, server_default=text("(0)")),
    Column('EditInv_Lvl', TINYINT, nullable=False, server_default=text("(3)")),
    Column('VoidTrans_Lvl', TINYINT, nullable=False, server_default=text("(3)")),
    Column('UndoLayPay_Lvl', TINYINT, nullable=False, server_default=text("(3)")),
    Column('UndoCSChrg_Lvl', TINYINT, nullable=False, server_default=text("(3)")),
    Column('EditRepAmt_Lvl', TINYINT, nullable=False, server_default=text("(3)")),
    Column('PawnRedeemDays', SmallInteger, nullable=False, server_default=text("(0)")),
    Column('SY4_id', UNIQUEIDENTIFIER, server_default=text("(newid())")),
    Column('LostTickPaymentRcpt', BIT, nullable=False, server_default=text("(0)")),
    Column('APRPeriodOne', BIT, nullable=False, server_default=text("(1)")),
    Column('APRPeriodTwo', BIT, nullable=False, server_default=text("(1)")),
    Column('APROneTime', BIT, nullable=False, server_default=text("(1)")),
    Column('APRTicket', BIT, nullable=False, server_default=text("(1)")),
    Column('APRPrep', BIT, nullable=False, server_default=text("(1)")),
    Column('APRFirearm', BIT, nullable=False, server_default=text("(1)")),
    Column('APRDaily', BIT, nullable=False, server_default=text("(1)")),
    Column('APRRTPeriod', BIT, nullable=False, server_default=text("(1)")),
    Column('APRRTOneTime', BIT, nullable=False, server_default=text("(1)")),
    Column('APRLate', BIT, nullable=False, server_default=text("(1)")),
    Column('APRTaxes', BIT, nullable=False, server_default=text("(1)")),
    Column('MultiStoreSave', BIT, nullable=False, server_default=text("(0)")),
    Column('TexasDailyProrate', BIT, nullable=False, server_default=text("(0)")),
    Column('SerialNumberCheck', BIT, nullable=False, server_default=text("(1)")),
    Column('PawnPayDays', BIT, nullable=False, server_default=text("(0)")),
    Column('PullCentralJew', TINYINT, nullable=False, server_default=text("(1)")),
    Column('PullCentralGun', TINYINT, nullable=False, server_default=text("(1)")),
    Column('PullCentralTitle', TINYINT, nullable=False, server_default=text("(1)")),
    Column('PullCentralOther', TINYINT, nullable=False, server_default=text("(1)")),
    Column('OvrUserTranLimit_Lvl', TINYINT, nullable=False, server_default=text("(3)")),
    Column('PawnOptionDateOutDays', SmallInteger, nullable=False, server_default=text("(0)")),
    Column('StatementForReceipt', BIT, nullable=False, server_default=text("(0)")),
    Column('PointsPawnDays1', TINYINT, nullable=False, server_default=text("(1)")),
    Column('PointsPawnDays2', TINYINT, nullable=False, server_default=text("(1)")),
    Column('PointsPawnDays3', TINYINT, nullable=False, server_default=text("(1)")),
    Column('PointsPawnDays4', TINYINT, nullable=False, server_default=text("(1)")),
    Column('PointsPawnDays5', TINYINT, nullable=False, server_default=text("(1)")),
    Column('PointsPawnDays6', TINYINT, nullable=False, server_default=text("(1)")),
    Column('PointsPawnDays7', TINYINT, nullable=False, server_default=text("(1)")),
    Column('PointsBuyDays1', TINYINT, nullable=False, server_default=text("(1)")),
    Column('PointsBuyDays2', TINYINT, nullable=False, server_default=text("(1)")),
    Column('PointsBuyDays3', TINYINT, nullable=False, server_default=text("(1)")),
    Column('PointsBuyDays4', TINYINT, nullable=False, server_default=text("(1)")),
    Column('PointsBuyDays5', TINYINT, nullable=False, server_default=text("(1)")),
    Column('PointsBuyDays6', TINYINT, nullable=False, server_default=text("(1)")),
    Column('PointsBuyDays7', TINYINT, nullable=False, server_default=text("(1)")),
    Column('PointsSaleDays1', TINYINT, nullable=False, server_default=text("(1)")),
    Column('PointsSaleDays2', TINYINT, nullable=False, server_default=text("(1)")),
    Column('PointsSaleDays3', TINYINT, nullable=False, server_default=text("(1)")),
    Column('PointsSaleDays4', TINYINT, nullable=False, server_default=text("(1)")),
    Column('PointsSaleDays5', TINYINT, nullable=False, server_default=text("(1)")),
    Column('PointsSaleDays6', TINYINT, nullable=False, server_default=text("(1)")),
    Column('PointsSaleDays7', TINYINT, nullable=False, server_default=text("(1)")),
    Column('PointsChargeDays1', TINYINT, nullable=False, server_default=text("(1)")),
    Column('PointsChargeDays2', TINYINT, nullable=False, server_default=text("(1)")),
    Column('PointsChargeDays3', TINYINT, nullable=False, server_default=text("(1)")),
    Column('PointsChargeDays4', TINYINT, nullable=False, server_default=text("(1)")),
    Column('PointsChargeDays5', TINYINT, nullable=False, server_default=text("(1)")),
    Column('PointsChargeDays6', TINYINT, nullable=False, server_default=text("(1)")),
    Column('PointsChargeDays7', TINYINT, nullable=False, server_default=text("(1)")),
    Column('PointsLooseDefault', BIT, nullable=False, server_default=text("(1)")),
    Column('PointsRepawn', SmallInteger, nullable=False, server_default=text("(0)")),
    Column('PointsPerDollar', Integer, nullable=False, server_default=text("(0)")),
    Column('Form8300Amount', MONEY, nullable=False, server_default=text("(10000.00)")),
    Column('InvLabelDate', TINYINT, nullable=False, server_default=text("(1)")),
    Column('InvLabelYear2', BIT, nullable=False, server_default=text("(0)")),
    Column('PoliceTicket1Ask', BIT, nullable=False, server_default=text("(0)")),
    Column('PoliceTicket2Ask', BIT, nullable=False, server_default=text("(0)")),
    Column('PrtNewTickDisclaim', BIT, nullable=False, server_default=text("(0)")),
    Column('PrtNewTickDisclaimBlank', BIT, nullable=False, server_default=text("(0)")),
    Column('LastUpdatedUSR_ID', UNIQUEIDENTIFIER)
)

t_Sysinfo3 = Table(
    'Sysinfo3', metadata,
    Column('STO_PK', SmallInteger, nullable=False, unique=True, server_default=text("(1)")),
    Column('PolTicNum', Integer, nullable=False, server_default=text("(0)")),
    Column('EndPolNum', Integer, nullable=False, server_default=text("(0)")),
    Column('PolTicNum2', Integer, nullable=False, server_default=text("(0)")),
    Column('EndPolNum2', Integer, nullable=False, server_default=text("(0)")),
    Column('SY3_id', UNIQUEIDENTIFIER, server_default=text("(newid())"))
)

t_TCC_TenderCC = Table(
    'TCC_TenderCC', metadata,
    Column('TCC_ID', UNIQUEIDENTIFIER, nullable=False, index=True, server_default=text("(newid())")),
    Column('LUC_ID', UNIQUEIDENTIFIER, nullable=False, index=True),
    Column('TCC_IsCC', BIT, nullable=False, server_default=text("(0)"))
)

t_Transfer = Table(
    'Transfer', metadata,
    Column('trans_pk', Integer, nullable=False),
    Column('Sto_fk', SmallInteger, nullable=False),
    Column('Suffix', CHAR(10, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('Items_FK', Integer, nullable=False),
    Column('tranqty', DECIMAL(10, 2), nullable=False, server_default=text("(0)")),
    Column('TRN_id', UNIQUEIDENTIFIER, unique=True, server_default=text("(newid())")),
    Index('IDX_Transfer_Sto_FK_Suffix', 'Suffix', 'Sto_fk')
)


class UPCFirearm(Base):
    __tablename__ = 'UPC_Firearm'
    __table_args__ = (
        Index('IX_UPC_Firearm_makemodel', 'make', 'modelnum'),
    )

    upc_id = Column(UNIQUEIDENTIFIER, primary_key=True, server_default=text("(newid())"))
    upc = Column(String(32, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, index=True)
    descript = Column(String(200, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    modelnum = Column(String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    level1 = Column(String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    level2 = Column(String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    make = Column(String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    caliber = Column(String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    action = Column(String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    finish = Column(String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    barrel = Column(String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    importer = Column(String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    length = Column(String(10, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)


class UPCOther(Base):
    __tablename__ = 'UPC_Other'
    __table_args__ = (
        Index('IX_UPC_Other_makemodel', 'make', 'modelnum'),
    )

    upc_id = Column(UNIQUEIDENTIFIER, primary_key=True, server_default=text("(newid())"))
    upc = Column(String(32, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, index=True)
    descript = Column(String(200, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    make = Column(String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    modelnum = Column(String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    level1 = Column(String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    level2 = Column(String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)


t_Version = Table(
    'Version', metadata,
    Column('ver_pk', Integer, nullable=False),
    Column('sto_pk', SmallInteger, nullable=False, server_default=text("(1)")),
    Column('Descript', String(30, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('Version', String(20, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('lastupdate', DateTime),
    Column('VER_id', UNIQUEIDENTIFIER, server_default=text("(newid())"))
)

t_WEB_WebSales = Table(
    'WEB_WebSales', metadata,
    Column('WEB_ID', UNIQUEIDENTIFIER, nullable=False, unique=True, server_default=text("(newid())")),
    Column('WEB_ItemNum', String(40, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('Web_Status', CHAR(10, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('WEB_Cost', MONEY, nullable=False),
    Column('WEB_SalePrice', MONEY, nullable=False),
    Column('Web_MinSale', MONEY, nullable=False),
    Column('WEB_Date', DateTime, nullable=False),
    Column('WEB_Sto_pk', SmallInteger, nullable=False),
    Column('WEB_Items_pk', Integer, nullable=False),
    Column('WEB_Items_id', UNIQUEIDENTIFIER, index=True),
    Column('WEB_Usr_id', UNIQUEIDENTIFIER, nullable=False),
    Index('IDX_WEB_Sto_pk_Items_PK', 'WEB_Sto_pk', 'WEB_Items_pk')
)


class Acctcode(Base):
    __tablename__ = 'acctcode'

    TYPE = Column(String(4, 'SQL_Latin1_General_CP1_CI_AS'), primary_key=True)
    DESCRIPT = Column(String(26, 'SQL_Latin1_General_CP1_CI_AS'))
    Acc_id = Column(UNIQUEIDENTIFIER, server_default=text("(newid())"))


class CeCustomerEmail(Base):
    __tablename__ = 'ce_CustomerEmail'

    ce_ID = Column(UNIQUEIDENTIFIER, primary_key=True, server_default=text("(newid())"))
    ce_SortOrder = Column(Integer, nullable=False)
    ce_DisplayName = Column(String(50, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    ce_Command1 = Column(Text(2147483647, 'SQL_Latin1_General_CP1_CI_AS'))
    ce_Command2 = Column(Text(2147483647, 'SQL_Latin1_General_CP1_CI_AS'))
    ce_Variables = Column(String(200, 'SQL_Latin1_General_CP1_CI_AS'))
    ce_From = Column(String(200, 'SQL_Latin1_General_CP1_CI_AS'))
    ce_CloseTables = Column(String(200, 'SQL_Latin1_General_CP1_CI_AS'))
    ce_If = Column(String(200, 'SQL_Latin1_General_CP1_CI_AS'))
    ce_CommandElse = Column(Text(2147483647, 'SQL_Latin1_General_CP1_CI_AS'))
    ce_Command1_2 = Column(Text(2147483647, 'SQL_Latin1_General_CP1_CI_AS'))
    ce_Proc = Column(Text(2147483647, 'SQL_Latin1_General_CP1_CI_AS'))


class CmluLoggedinuser(Base):
    __tablename__ = 'cmlu_loggedinuser'

    cmlu_id = Column(UNIQUEIDENTIFIER, primary_key=True, server_default=text("(newid())"))
    sto_pk = Column(SmallInteger, nullable=False, server_default=text("(1)"))
    cmlu_cpu_name = Column(String(200, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("(' ')"))
    cmlu_LoginTime = Column(DateTime, server_default=text("(getdate())"))


t_custview = Table(
    'custview', metadata,
    Column('Cus_Store', Integer, nullable=False),
    Column('Cus_PK', Integer, nullable=False),
    Column('CUS_FNAME', String(15, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_MNAME', String(15, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_LNAME', String(25, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_ADD1', String(25, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_ADD2', String(25, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_CITY', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_STATE', String(2, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_ZIP', String(10, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_COUNTRY', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_AC1', String(3, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_PHONE1', String(8, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_HEIGHT', String(6, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_WEIGHT', SmallInteger, nullable=False),
    Column('hair', String(20, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('eyes', String(20, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('race', String(20, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('CUS_SEX', String(1, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_MARKS', String(40, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_BIRTHDate', SMALLDATETIME),
    Column('CUS_BIRTHCITY', String(15, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_BIRTHSTATE', String(2, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_BIRTH2', String(15, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_ID1', String(20, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('CUS_IDNUM1', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_ID1EXP', SMALLDATETIME),
    Column('CUS_ID1ISSUE', String(50, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_ID2', String(20, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('CUS_IDNUM2', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_ID2EXP', SMALLDATETIME),
    Column('CUS_ID2ISSUE', String(2, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_KNOWN', BIT, nullable=False),
    Column('CUS_SSNUM', String(11, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_VEHIC1', String(10, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_VEHIC2', String(8, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_VEHIC3', String(2, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_EMPLOYER', String(40, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_EMPAD1', String(35, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_EMPAD2', String(35, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_EMPCITY', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_EMPSTATE', String(2, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_EMPZIP', String(10, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_AC2', String(3, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_EMPPHONE', String(14, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_COMMENT', String(200, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_TOTALPAWNS', Integer, nullable=False),
    Column('CUS_ACTIVEPAWN', Integer, nullable=False),
    Column('CUS_REDEEMED', Integer, nullable=False),
    Column('CUS_BUYS', Integer, nullable=False),
    Column('CUS_SALES', MONEY, nullable=False),
    Column('CUS_AMT1', MONEY, nullable=False),
    Column('CUS_AMT2', MONEY, nullable=False),
    Column('CUS_FFLNUM', String(25, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_DELETE', BIT, nullable=False),
    Column('CUS_LOCKED', BIT, nullable=False),
    Column('CUS_PAWNER', BIT, nullable=False),
    Column('CUS_BUYER', BIT, nullable=False),
    Column('CUS_IDADD1', String(25, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_IDADD2', String(25, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_IDCITY', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_IDSTATE', String(2, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_IDZIP', String(10, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_CREDIT', MONEY, nullable=False),
    Column('Special', String(20, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('CUS_PIC_FK', Integer, nullable=False)
)


class Custxtinfo(Base):
    __tablename__ = 'custxtinfo'

    Cus_id = Column(UNIQUEIDENTIFIER, primary_key=True)
    Cus_TxtMsg = Column(BIT)
    Cus_TxtMsgDeclined = Column(BIT)
    Cus_TxtMsgSent = Column(DateTime)
    Cus_TxtMsgsendsales = Column(BIT)
    Cus_TxtMsgsendfinancials = Column(BIT)
    LastUpdatedUsr_id = Column(UNIQUEIDENTIFIER)
    Cus_TxtMsgPin = Column(String(10, 'SQL_Latin1_General_CP1_CI_AS'), server_default=text("(space((10)))"))


t_dtproperties = Table(
    'dtproperties', metadata,
    Column('id', Integer, nullable=False),
    Column('objectid', Integer),
    Column('property', String(64, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('value', String(255, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('lvalue', LargeBinary),
    Column('version', Integer, nullable=False, server_default=text("(0)")),
    Column('uvalue', Unicode(255))
)


class Errorlog(Base):
    __tablename__ = 'errorlog'

    Err_PK = Column(Integer, primary_key=True)
    errdate = Column(DateTime, nullable=False)
    Descrip = Column(String(500, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    userlanid = Column(CHAR(10, 'SQL_Latin1_General_CP1_CI_AS'))
    err_store = Column(SmallInteger)
    program = Column(String(50, 'SQL_Latin1_General_CP1_CI_AS'))
    errorno = Column(String(50, 'SQL_Latin1_General_CP1_CI_AS'))
    linenumber = Column(String(50, 'SQL_Latin1_General_CP1_CI_AS'))
    callstack = Column(String(500, 'SQL_Latin1_General_CP1_CI_AS'))
    source = Column(String(255, 'SQL_Latin1_General_CP1_CI_AS'))
    page3var = Column(String(50, 'SQL_Latin1_General_CP1_CI_AS'))
    version = Column(String(50, 'SQL_Latin1_General_CP1_CI_AS'))
    ERR_id = Column(UNIQUEIDENTIFIER, server_default=text("(newid())"))
    product = Column(CHAR(2, 'SQL_Latin1_General_CP1_CI_AS'))


class Guninvnum(Base):
    __tablename__ = 'guninvnum'
    __table_args__ = (
        Index('IDX_guninvnum_sto_pk_oldinvnum', 'sto_pk', 'oldinvnum'),
        Index('IDX_guninvnum_sto_pk_invnum', 'sto_pk', 'invnum')
    )

    guninv_id = Column(UNIQUEIDENTIFIER, primary_key=True, server_default=text("(newid())"))
    sto_pk = Column(SmallInteger, nullable=False)
    invnum = Column(String(14, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    oldinvnum = Column(String(14, 'SQL_Latin1_General_CP1_CI_AS'))
    items_pk = Column(Integer, nullable=False)
    olditems_pk = Column(Integer)
    undone = Column(BIT, nullable=False)


t_gunlog = Table(
    'gunlog', metadata,
    Column('GunLog_PK', Integer, nullable=False),
    Column('GunLogNum', Integer, nullable=False, server_default=text("(0)")),
    Column('Prev_GunLogRec', Integer, nullable=False, server_default=text("(0)")),
    Column('Next_GunLogRec', Integer, nullable=False, server_default=text("(0)")),
    Column('STO_PK', SmallInteger, nullable=False, server_default=text("(1)")),
    Column('INVNUM', String(14, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("('')")),
    Column('MANUFACTUR', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("('')")),
    Column('MODEL', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("('')")),
    Column('SERIAL', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("('')")),
    Column('CALIBER', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("('')")),
    Column('ACTION', String(15, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("('')")),
    Column('CONDITION', String(5, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("('')")),
    Column('BUYAMT', MONEY, nullable=False, server_default=text("(0.00)")),
    Column('BUYDATE', DateTime),
    Column('BUYFNAME', String(15, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("('')")),
    Column('BUYMNAME', String(15, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("('')")),
    Column('BUYLNAME', String(30, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("('')")),
    Column('BUYADD1', String(25, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("('')")),
    Column('BuyAdd2', String(25, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("('')")),
    Column('BUYCITY', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("('')")),
    Column('BUYSTATE', String(2, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("('')")),
    Column('BUYZIP', String(10, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("('')")),
    Column('BUYIDTYPE', String(10, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("('')")),
    Column('BUYIDNUM', String(25, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("('')")),
    Column('SOLDDATE', DateTime),
    Column('SOLDFNAME', String(15, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("('')")),
    Column('SOLDMNAME', String(15, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("('')")),
    Column('SOLDLNAME', String(25, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("('')")),
    Column('SOLDADD1', String(25, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("('')")),
    Column('SoldAdd2', String(25, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("('')")),
    Column('SOLDCITY', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("('')")),
    Column('SOLDSTATE', String(2, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("('')")),
    Column('SOLDZIP', String(10, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("('')")),
    Column('SOLDAMT', MONEY, nullable=False, server_default=text("(0.00)")),
    Column('SOLDIDTYPE', String(10, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("('')")),
    Column('SOLDIDNUM', String(25, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("('')")),
    Column('TRANSNUM', String(25, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("('')")),
    Column('COMMENT1', String(40, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("('')")),
    Column('COMMENT2', String(40, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("('')")),
    Column('VOIDED', BIT, server_default=text("(0)")),
    Column('CHANGED', BIT, server_default=text("(0)")),
    Column('GUNTYPE', String(10, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("('')")),
    Column('IMPORTER', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("('')")),
    Column('PICKDATE', DateTime),
    Column('NICSTN', String(12, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("('')")),
    Column('GUN_id', UNIQUEIDENTIFIER, unique=True, server_default=text("(newid())")),
    Column('LastUpdatedUSR_ID', UNIQUEIDENTIFIER),
    Column('OrigManufacturer', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("('')")),
    Column('OrigModel', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("('')")),
    Column('OrigSerial', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("('')")),
    Column('OrigCaliber', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("('')")),
    Column('OrigAction', String(15, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("('')")),
    Column('OrigBuyDate', DateTime),
    Column('OrigBuyFName', String(15, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("('')")),
    Column('OrigBuyMName', String(15, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("('')")),
    Column('OrigBuyLName', String(30, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("('')")),
    Column('OrigBuyAdd1', String(25, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("('')")),
    Column('OrigBuyAdd2', String(25, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("('')")),
    Column('OrigBuyCity', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("('')")),
    Column('OrigBuyState', String(2, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("('')")),
    Column('OrigBuyZip', String(10, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("('')")),
    Column('OrigBuyIDType', String(10, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("('')")),
    Column('OrigBuyIDNum', String(25, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("('')")),
    Column('OrigSoldDate', DateTime),
    Column('OrigSoldFName', String(15, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("('')")),
    Column('OrigSoldMName', String(15, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("('')")),
    Column('OrigSoldLName', String(25, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("('')")),
    Column('OrigSoldAdd1', String(25, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("('')")),
    Column('OrigSoldAdd2', String(25, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("('')")),
    Column('OrigSoldCity', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("('')")),
    Column('OrigSoldState', String(2, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("('')")),
    Column('OrigSoldZip', String(10, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("('')")),
    Column('OrigSoldIDType', String(10, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("('')")),
    Column('OrigSoldIDNum', String(25, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("('')")),
    Column('OrigTransNum', String(25, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("('')")),
    Column('OrigGunType', String(10, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("('')")),
    Column('OrigImporter', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("('')")),
    Column('OrigNICSTN', String(12, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("('')")),
    Index('IDX_gunlog_Sto_PK_Type', 'GUNTYPE', 'STO_PK'),
    Index('IDX_gunlog_Sto_PK_Manu', 'MANUFACTUR', 'STO_PK'),
    Index('IDX_gunlog_Sto_PK_InvNum', 'STO_PK', 'INVNUM'),
    Index('IDX_gunlog_Sto_PK_Action', 'ACTION', 'STO_PK'),
    Index('IDX_gunlog_Sto_PK_Caliber', 'CALIBER', 'STO_PK'),
    Index('IDX_gunlog_Sto_PK_GunLogNum', 'GunLogNum', 'STO_PK')
)

t_guntrans = Table(
    'guntrans', metadata,
    Column('gt_Pk', Integer, nullable=False),
    Column('sto_pk', SmallInteger, nullable=False, server_default=text("(1)")),
    Column('invnum', String(14, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("('')")),
    Column('items_pk', Integer, nullable=False, server_default=text("(0)")),
    Column('gt_date', DateTime),
    Column('gt_type', String(10, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("('')")),
    Column('usr_fk', Integer, nullable=False, server_default=text("(1)")),
    Column('comment1', Text(2147483647, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("('')")),
    Column('GNT_id', UNIQUEIDENTIFIER, unique=True, server_default=text("(newid())")),
    Index('IDX_guntrans_Sto_PK_InvNum', 'sto_pk', 'invnum')
)

t_holdcon = Table(
    'holdcon', metadata,
    Column('hc_pk', Integer, nullable=False),
    Column('sto_pk', SmallInteger, nullable=False, server_default=text("((-1))")),
    Column('LookupKey', String(13, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("('-1')")),
    Column('emp_fk', Integer, nullable=False, server_default=text("((-1))")),
    Column('date', SMALLDATETIME),
    Column('agency', String(30, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("(' ')")),
    Column('casenum', String(15, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("(' ')")),
    Column('dateout', SMALLDATETIME),
    Column('ishold', TINYINT, nullable=False, server_default=text("(0)")),
    Column('isinv', TINYINT, nullable=False, server_default=text("(0)")),
    Column('itemlist', String(200, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("(' ')")),
    Column('comment', String(200, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("(' ')")),
    Column('agentln', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("(' ')")),
    Column('agentfn', String(15, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("(' ')")),
    Column('agentmi', String(1, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("(' ')")),
    Column('badge', String(10, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("(' ')")),
    Column('ac1', String(3, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("(' ')")),
    Column('phone1', String(8, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("(' ')")),
    Column('ext1', String(4, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("('')")),
    Column('jurisdict', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("(' ')")),
    Column('HCN_id', UNIQUEIDENTIFIER, unique=True, server_default=text("(newid())")),
    Column('LastUpdatedUSR_ID', UNIQUEIDENTIFIER),
    Index('IDX_HoldCon_hc_PK_Sto_PK', 'hc_pk', 'sto_pk')
)


class Inv(Base):
    __tablename__ = 'inv'
    __table_args__ = (
        Index('IDX_inv_Sto_PK_Scrapnum', 'SCRAPNUM', 'Sto_PK'),
        Index('IDX_inv_Sto_PK_InvNum', 'INVNUM', 'Sto_PK'),
        Index('IDX_inv_Sto_PK_DateIN', 'Sto_PK', 'DATEin')
    )

    Inv_PK = Column(Integer, primary_key=True)
    Sto_PK = Column(SmallInteger, nullable=False, server_default=text("(1)"))
    INVNUM = Column(String(14, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("('')"))
    DATEin = Column(DateTime)
    QUANTITY = Column(Numeric(9, 2), nullable=False, server_default=text("(0)"))
    SCRAPNUM = Column(String(14, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("('')"))
    STATUS = Column(String(1, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("('')"))
    COST = Column(MONEY, nullable=False, server_default=text("(0.00)"))
    USR_fk = Column(Integer, nullable=False, server_default=text("(0)"))
    OrigQty = Column(Numeric(9, 2), nullable=False, server_default=text("(0)"))
    OrigCost = Column(MONEY, nullable=False, server_default=text("(0.00)"))
    INV_id = Column(UNIQUEIDENTIFIER, unique=True, server_default=text("(newid())"))
    Items_ID = Column(UNIQUEIDENTIFIER, index=True)


t_invphys = Table(
    'invphys', metadata,
    Column('phy_pk', Integer, nullable=False),
    Column('sto_pk', SmallInteger, nullable=False, server_default=text("(1)")),
    Column('cNumber', String(13, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("('')")),
    Column('type', CHAR(1, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("('')")),
    Column('quantity', DECIMAL(9, 2), nullable=False, server_default=text("(0.00)")),
    Column('PHY_id', UNIQUEIDENTIFIER, unique=True, server_default=text("(newid())"))
)

t_itemsinholdperiod = Table(
    'itemsinholdperiod', metadata,
    Column('invnum', String(14, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('guntype', String(10, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('manufactur', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('serial', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('caliber', String(10, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('action', String(15, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('model', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('gunlognum', Integer, nullable=False),
    Column('bin', String(6, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('status', String(1, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('status2', String(11, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('sto_pk', SmallInteger),
    Column('Comment2', String(40, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('ticketnum', Integer),
    Column('cus_fname', String(15, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('cus_mname', String(15, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('cus_lname', String(25, 'SQL_Latin1_General_CP1_CI_AS'))
)

t_itemspost2gunview = Table(
    'itemspost2gunview', metadata,
    Column('invnum', String(14, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('guntype', String(10, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('manufactur', String(20, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('serial', String(20, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('caliber', String(10, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('action', String(15, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('model', String(20, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('gunlognum', Integer),
    Column('bin', String(6, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('status', String(1, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('status2', String(25, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('sto_pk', SmallInteger, nullable=False),
    Column('Comment2', String(40, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('ticketnum', Integer, nullable=False),
    Column('cus_fname', String(15, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('cus_mname', String(15, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('cus_lname', String(25, 'SQL_Latin1_General_CP1_CI_AS'))
)

t_jv_CMHistory = Table(
    'jv_CMHistory', metadata,
    Column('CMCD_ID', UNIQUEIDENTIFIER),
    Column('CMLC_ID', UNIQUEIDENTIFIER),
    Column('CMTH_AMOUNT', MONEY, nullable=False),
    Column('CMTH_DATE', DateTime, nullable=False),
    Column('CMTH_ID', UNIQUEIDENTIFIER, nullable=False),
    Column('CMTH_OVERRIDEAMOUNT', MONEY, nullable=False),
    Column('CMTH_PROFIT_USR_ID', UNIQUEIDENTIFIER, nullable=False),
    Column('CMTH_TYPE', CHAR(10, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('USR_ID', UNIQUEIDENTIFIER, nullable=False),
    Column('cmtn_note', String(250, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('usr_lanid', String(8, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('TicketNumber', Integer),
    Column('cmtr_id', UNIQUEIDENTIFIER, nullable=False),
    Column('cus_id', UNIQUEIDENTIFIER, nullable=False),
    Column('sto_pk', SmallInteger, nullable=False),
    Column('cmtr_type', CHAR(10, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('cmtr_date', DateTime, nullable=False),
    Column('cmtr_status', CHAR(2, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('Status', String(10, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('TypeDescription', String(20, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('CMTHTypeDescription', String(25, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('cmcd_receipt', Integer)
)

t_jv_CMITLevels = Table(
    'jv_CMITLevels', metadata,
    Column('CMIT_ID', UNIQUEIDENTIFIER, nullable=False),
    Column('LV1_ID', UNIQUEIDENTIFIER, nullable=False),
    Column('LV1_description', String(50, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('LV2_ID', UNIQUEIDENTIFIER),
    Column('LV2_description', String(50, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('LV3_ID', UNIQUEIDENTIFIER),
    Column('LV3_description', String(50, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('LV4_ID', UNIQUEIDENTIFIER),
    Column('LV4_description', String(50, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('sto_pk', SmallInteger, nullable=False),
    Column('CMITS_ID', UNIQUEIDENTIFIER, nullable=False),
    Column('lv_number', Integer, nullable=False),
    Column('lv_Parent', UNIQUEIDENTIFIER),
    Column('Description1', String(206, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('Description2', String(203, 'SQL_Latin1_General_CP1_CI_AS'))
)

t_jv_CMMain = Table(
    'jv_CMMain', metadata,
    Column('RowChangeInd', String(1, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('cmtr_id', UNIQUEIDENTIFIER, nullable=False),
    Column('cmtr_type', CHAR(10, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('cmtr_status', CHAR(2, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('cmtr_date', DateTime, nullable=False),
    Column('usr_id', UNIQUEIDENTIFIER, nullable=False),
    Column('sto_pk', SmallInteger, nullable=False),
    Column('cus_id', UNIQUEIDENTIFIER),
    Column('Status', String(10, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('cmck_id', UNIQUEIDENTIFIER),
    Column('cmrh_id', UNIQUEIDENTIFIER),
    Column('cmta_amount', Numeric(9, 2)),
    Column('Fee', MONEY),
    Column('CalcFee', MONEY),
    Column('CKNumber', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CKAmount', Numeric(9, 2)),
    Column('CKDate', DateTime, nullable=False),
    Column('CKAccount', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CKTransit', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('cmca_id', UNIQUEIDENTIFIER, nullable=False),
    Column('TicketNumber', Integer),
    Column('Charge', Numeric(9, 2)),
    Column('AllowCharge', BIT),
    Column('Redemption', Numeric(9, 2)),
    Column('AllowRedemption', BIT),
    Column('OtherPayment', Numeric(9, 2)),
    Column('AllowOtherPayment', BIT),
    Column('ChargeSelect', BIT),
    Column('RedemptionSelect', BIT),
    Column('OtherPaymentSelect', BIT),
    Column('DATEOUT', DateTime),
    Column('Maker', CHAR(35, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('TypeDescription', String(20, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('cmpy_cus_id', UNIQUEIDENTIFIER),
    Column('cmpy_name', String(35, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('cmpy_id', UNIQUEIDENTIFIER, nullable=False),
    Column('BankName', String(50, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('cmbk_id', UNIQUEIDENTIFIER),
    Column('OKtoVoid', BIT),
    Column('OkToUnvoid', BIT),
    Column('cBounceComment', String(256, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('nVoid', Numeric(9, 2)),
    Column('nPaySvcChg', Numeric(9, 2)),
    Column('nPayRedeem', Numeric(9, 2)),
    Column('nPayLate', Numeric(9, 2)),
    Column('nPayLost', Numeric(9, 2)),
    Column('nPayPartial', Numeric(9, 2)),
    Column('nPayLower', Numeric(9, 2)),
    Column('nPayOverRideAmt', Numeric(9, 2)),
    Column('nPayChargePeriods', Integer),
    Column('nPayOtherPeriods', Integer),
    Column('NewCMCK_ID', UNIQUEIDENTIFIER),
    Column('DateOutChange', BIT),
    Column('Remit', Numeric(9, 2)),
    Column('cmvt_vrnumber', String(20, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('nRTCharges', Numeric(9, 2)),
    Column('nRTFees', Numeric(9, 2)),
    Column('nFee1', Numeric(9, 2)),
    Column('nFee2', Numeric(9, 2)),
    Column('ReceiptNumber', Integer)
)

t_jv_CMMain2 = Table(
    'jv_CMMain2', metadata,
    Column('RowChangeInd', String(1, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('cmtr_id', UNIQUEIDENTIFIER, nullable=False),
    Column('cmtr_type', CHAR(10, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('cmtr_status', CHAR(2, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('cmtr_date', DateTime, nullable=False),
    Column('usr_id', UNIQUEIDENTIFIER, nullable=False),
    Column('sto_pk', SmallInteger, nullable=False),
    Column('cus_id', UNIQUEIDENTIFIER),
    Column('Status', String(10, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('cmck_id', UNIQUEIDENTIFIER),
    Column('cmrh_id', UNIQUEIDENTIFIER),
    Column('cmta_amount', Numeric(9, 2)),
    Column('Fee', Numeric(19, 4)),
    Column('CalcFee', Numeric(9, 2)),
    Column('CKNumber', CHAR(20, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('CKAmount', Numeric(9, 2)),
    Column('CKDate', DateTime),
    Column('CKAccount', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CKTransit', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('cmca_id', UNIQUEIDENTIFIER),
    Column('TicketNumber', Integer),
    Column('Charge', Numeric(9, 2)),
    Column('AllowCharge', BIT),
    Column('Redemption', Numeric(9, 2)),
    Column('AllowRedemption', BIT),
    Column('OtherPayment', Numeric(9, 2)),
    Column('AllowOtherPayment', BIT),
    Column('ChargeSelect', BIT),
    Column('RedemptionSelect', BIT),
    Column('OtherPaymentSelect', BIT),
    Column('DATEOUT', DateTime),
    Column('Maker', CHAR(50, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('TypeDescription', String(20, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('cmpy_cus_id', UNIQUEIDENTIFIER),
    Column('cmpy_name', String(35, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('cmpy_id', UNIQUEIDENTIFIER),
    Column('BankName', String(50, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('cmbk_id', UNIQUEIDENTIFIER),
    Column('OKtoVoid', BIT),
    Column('OkToUnvoid', BIT),
    Column('cBounceComment', String(256, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('nVoid', Numeric(9, 2)),
    Column('nPaySvcChg', Numeric(9, 2)),
    Column('nPayRedeem', Numeric(9, 2)),
    Column('nPayLate', Numeric(9, 2)),
    Column('nPayLost', Numeric(9, 2)),
    Column('nPayPartial', Numeric(9, 2)),
    Column('nPayLower', Numeric(9, 2)),
    Column('nPayOverRideAmt', Numeric(9, 2)),
    Column('nPayChargePeriods', Integer),
    Column('nPayOtherPeriods', Integer),
    Column('NewCMCK_ID', UNIQUEIDENTIFIER),
    Column('DateOutChange', BIT),
    Column('Remit', Numeric(9, 2)),
    Column('cmvt_vrnumber', String(20, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('nRTCharges', Numeric(9, 2)),
    Column('nRTFees', Numeric(9, 2)),
    Column('nFee1', Numeric(9, 2)),
    Column('nFee2', Numeric(9, 2)),
    Column('ReceiptNumber', Integer),
    Column('cmth_date', DateTime, nullable=False)
)

t_jv_CMMain3 = Table(
    'jv_CMMain3', metadata,
    Column('RowChangeInd', String(1, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('cmtr_id', UNIQUEIDENTIFIER, nullable=False),
    Column('cus_id', UNIQUEIDENTIFIER, nullable=False),
    Column('usr_ID', UNIQUEIDENTIFIER, nullable=False),
    Column('sto_pk', SmallInteger, nullable=False),
    Column('cmtr_Type', CHAR(10, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('cmtr_date', DateTime, nullable=False),
    Column('cmtr_status', CHAR(2, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('Status', String(10, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('cmck_id', UNIQUEIDENTIFIER),
    Column('cmrh_id', UNIQUEIDENTIFIER),
    Column('cmta_amount', Numeric(9, 2)),
    Column('Fee', MONEY),
    Column('CalcFee', MONEY),
    Column('CKNumber', CHAR(20, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('CKAmount', Numeric(9, 2)),
    Column('CKDate', DateTime),
    Column('CKAccount', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CKTransit', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('cmca_id', UNIQUEIDENTIFIER),
    Column('TicketNumber', Integer),
    Column('Charge', Numeric(9, 2)),
    Column('AllowCharge', BIT),
    Column('Redemption', Numeric(9, 2)),
    Column('AllowRedemption', BIT),
    Column('OtherPayment', Numeric(9, 2)),
    Column('AllowOtherPayment', BIT),
    Column('ChargeSelect', BIT),
    Column('RedemptionSelect', BIT),
    Column('OtherPaymentSelect', BIT),
    Column('DATEOUT', DateTime),
    Column('Maker', String(50, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('TypeDescription', String(20, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('cmpy_cus_id', UNIQUEIDENTIFIER),
    Column('cmpy_name', String(35, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('cmpy_id', UNIQUEIDENTIFIER),
    Column('BankName', String(50, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('cmbk_id', UNIQUEIDENTIFIER),
    Column('OKtoVoid', BIT),
    Column('OkToUnvoid', BIT),
    Column('cBounceComment', String(256, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('nVoid', Numeric(9, 2)),
    Column('nPaySvcChg', Numeric(9, 2)),
    Column('nPayRedeem', Numeric(9, 2)),
    Column('nPayLate', Numeric(9, 2)),
    Column('nPayLost', Numeric(9, 2)),
    Column('nPayPartial', Numeric(9, 2)),
    Column('nPayLower', Numeric(9, 2)),
    Column('nPayOverRideAmt', Numeric(9, 2)),
    Column('nPayChargePeriods', Integer),
    Column('nPayOtherPeriods', Integer),
    Column('NewCMCK_ID', UNIQUEIDENTIFIER),
    Column('DateOutChange', BIT),
    Column('Remit', Numeric(9, 2)),
    Column('cmvt_vrnumber', String(20, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('nRTCharges', Numeric(9, 2)),
    Column('nRTFees', Numeric(9, 2)),
    Column('nFee1', Numeric(9, 2)),
    Column('nFee2', Numeric(9, 2)),
    Column('ReceiptNumber', Integer),
    Column('cmth_date', DateTime, nullable=False)
)

t_jv_CMMultDepoAdd = Table(
    'jv_CMMultDepoAdd', metadata,
    Column('cmtr_ID', UNIQUEIDENTIFIER, nullable=False),
    Column('cmck_cknumber', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('cmck_id', UNIQUEIDENTIFIER, nullable=False),
    Column('cmtr_type', CHAR(10, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('usr_id', UNIQUEIDENTIFIER, nullable=False),
    Column('cus_id', UNIQUEIDENTIFIER, nullable=False),
    Column('sto_pk', SmallInteger, nullable=False),
    Column('cmck_ckamount', Numeric(9, 2)),
    Column('DepositDate', DateTime, nullable=False),
    Column('cmta_dateout', DateTime),
    Column('Name', String(58, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('Type', CHAR(14, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('TypeDesc', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('cmtr_date', DateTime, nullable=False),
    Column('status', String(10, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('cmtr_status', CHAR(2, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('Maker', String(50, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('TicketNumber', Integer),
    Column('cmpy_cus_id', UNIQUEIDENTIFIER),
    Column('cmpy_id', UNIQUEIDENTIFIER, nullable=False),
    Column('cus_fname', String(15, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('cus_mname', String(15, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('cus_lname', String(25, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('cmpy_name', String(35, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('CKAccount', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('cmca_id', UNIQUEIDENTIFIER, nullable=False),
    Column('CKTransit', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('BankName', String(50, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('cmbk_id', UNIQUEIDENTIFIER, nullable=False),
    Column('TypeDescription', String(20, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('Remit', Numeric(9, 2)),
    Column('cmvt_vrnumber', String(20, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('nRTCharges', Numeric(9, 2)),
    Column('nRTFees', Numeric(9, 2)),
    Column('Amount', Numeric(19, 4)),
    Column('ReceiptNumber', Integer),
    Column('AdditionalCharge', Numeric(19, 4)),
    Column('AdditionalFee', Numeric(19, 4)),
    Column('cmdba_id', UNIQUEIDENTIFIER),
    Column('cmck_Altered_CKAmount', Numeric(9, 2)),
    Column('orig_CKAmount', Numeric(9, 2)),
    Column('cmck_directdebit', BIT),
    Column('cmca_account_type', CHAR(1, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('From_cmcbs_id', UNIQUEIDENTIFIER),
    Column('From_usr_id', UNIQUEIDENTIFIER),
    Column('From_cmcbs_type', CHAR(2, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('cmcbs_description', String(50, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('cmdba_description', String(50, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('cmrh_id', UNIQUEIDENTIFIER),
    Column('cmcd_id', UNIQUEIDENTIFIER, nullable=False),
    Column('cmck_endorsed', BIT)
)

t_jv_CMMultDepoView = Table(
    'jv_CMMultDepoView', metadata,
    Column('cmtr_id', UNIQUEIDENTIFIER, nullable=False),
    Column('cmck_cknumber', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('cmck_id', UNIQUEIDENTIFIER, nullable=False),
    Column('cmtr_type', CHAR(10, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('usr_id', UNIQUEIDENTIFIER, nullable=False),
    Column('cus_id', UNIQUEIDENTIFIER, nullable=False),
    Column('cmck_ckamount', Numeric(9, 2)),
    Column('DepositDate', DateTime, nullable=False),
    Column('Name', String(58, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('Type', CHAR(14, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('TypeDesc', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('cmtr_date', DateTime, nullable=False),
    Column('status', String(10, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('cmtr_status', CHAR(2, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('Maker', String(50, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('TicketNumber', Integer),
    Column('cmpy_cus_id', UNIQUEIDENTIFIER),
    Column('cmpy_id', UNIQUEIDENTIFIER, nullable=False),
    Column('cus_fname', String(15, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('cus_mname', String(15, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('cus_lname', String(25, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('cmpy_name', String(35, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('CKAccount', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('cmca_id', UNIQUEIDENTIFIER, nullable=False),
    Column('CKTransit', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('BankName', String(50, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('cmbk_id', UNIQUEIDENTIFIER, nullable=False),
    Column('cmbh_id', UNIQUEIDENTIFIER, nullable=False),
    Column('TypeDescription', String(20, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('Remit', Numeric(9, 2)),
    Column('cmvt_vrnumber', String(20, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('nRTCharges', Numeric(9, 2)),
    Column('nRTFees', Numeric(9, 2)),
    Column('cmdba_id', UNIQUEIDENTIFIER),
    Column('cmck_Altered_CKAmount', Numeric(9, 2)),
    Column('ReceiptNumber', Integer),
    Column('cmrh_id', UNIQUEIDENTIFIER),
    Column('cmbh_check21', BIT),
    Column('cmbh_ck21proc', CHAR(2, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('cmck_endorsed', BIT),
    Column('cmbd_id', UNIQUEIDENTIFIER, nullable=False)
)

t_jv_CMPY = Table(
    'jv_CMPY', metadata,
    Column('CMPY_ADDRESS1', String(25, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('CMPY_ADDRESS2', String(25, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('CMPY_CITY', String(50, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('CMPY_ID', UNIQUEIDENTIFIER, nullable=False),
    Column('CMPY_NAME', String(35, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('CMPY_PHONE', String(20, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('CMPY_STATE', CHAR(2, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('CMPY_ZIP', CHAR(10, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('CUS_ID', UNIQUEIDENTIFIER),
    Column('cus_FName', String(15, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('cus_MName', String(15, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('cus_LName', String(25, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('cus_Add1', String(25, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('cus_Add2', String(25, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('cus_city', String(20, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('cus_state', String(2, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('cus_zip', String(10, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('cus_ac1', String(3, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('cus_phone1', String(8, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('CMTR_Cus_id', UNIQUEIDENTIFIER, nullable=False)
)

t_jv_CMPrintSelect = Table(
    'jv_CMPrintSelect', metadata,
    Column('CMCD_ID', UNIQUEIDENTIFIER),
    Column('CMLC_ID', UNIQUEIDENTIFIER),
    Column('CMTH_AMOUNT', MONEY, nullable=False),
    Column('CMTH_DATE', DateTime, nullable=False),
    Column('CMTH_ID', UNIQUEIDENTIFIER, nullable=False),
    Column('CMTH_OVERRIDEAMOUNT', MONEY, nullable=False),
    Column('CMTH_PROFIT_USR_ID', UNIQUEIDENTIFIER, nullable=False),
    Column('CMTH_TYPE', CHAR(10, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('cmtr_id', UNIQUEIDENTIFIER, nullable=False),
    Column('cus_id', UNIQUEIDENTIFIER, nullable=False),
    Column('usr_ID', UNIQUEIDENTIFIER, nullable=False),
    Column('sto_pk', SmallInteger, nullable=False),
    Column('cmtr_Type', CHAR(10, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('cmtr_date', DateTime, nullable=False),
    Column('cmtr_status', CHAR(2, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('Status', String(10, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('CMTRTypeDescription', String(20, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('CMTHTypeDescription', String(25, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('cmcd_receipt', Integer),
    Column('TicketNumber', Integer)
)

t_jv_CMReceiptview = Table(
    'jv_CMReceiptview', metadata,
    Column('ticketnumber', Integer),
    Column('currentticketnumber', Integer, nullable=False),
    Column('descript', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('printdescript', String(10, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('ckdate', DateTime, nullable=False),
    Column('ckamount', MONEY, nullable=False),
    Column('cknumber', String(20, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('fees', MONEY),
    Column('receipt', Integer),
    Column('tran_type', CHAR(10, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('tran_date', DateTime, nullable=False),
    Column('Amount', MONEY, nullable=False),
    Column('OverRideAmount', MONEY, nullable=False),
    Column('sto_pk', SmallInteger, nullable=False),
    Column('emp', String(8, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('cus_id', UNIQUEIDENTIFIER),
    Column('Long_Description', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('Short_Description', CHAR(12, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('lookup', CHAR(10, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('cmcd_id', UNIQUEIDENTIFIER, nullable=False),
    Column('CMTH_ID', UNIQUEIDENTIFIER, nullable=False),
    Column('CMTR_ID', UNIQUEIDENTIFIER, nullable=False),
    Column('Profit_Usr_id', UNIQUEIDENTIFIER, nullable=False)
)

t_jv_CMSoldInvItems = Table(
    'jv_CMSoldInvItems', metadata,
    Column('TICKETNUM', Integer),
    Column('STO_PK', SmallInteger, nullable=False),
    Column('DATEin', DateTime, nullable=False),
    Column('SaleAmt', MONEY, nullable=False),
    Column('Taxable', Numeric(9, 2)),
    Column('Tax', Numeric(9, 2)),
    Column('ReturnedAmt', Numeric(9, 2)),
    Column('COMMENT', CHAR(10, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('Trans', CHAR(1, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('SLD_Status', CHAR(1, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('DateOut', DateTime, nullable=False),
    Column('Note', CHAR(1, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('sld_id', UNIQUEIDENTIFIER),
    Column('Invnum', CHAR(14, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('NumberSold', Integer, nullable=False),
    Column('Amount', MONEY, nullable=False),
    Column('Descript', String(50, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('TaxExempt', BIT, nullable=False),
    Column('Cost', Numeric(9, 2)),
    Column('Returnsold', Numeric(9, 2)),
    Column('Bin', CHAR(6, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('SIT_Status', CHAR(1, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('Items_pk', Integer),
    Column('ven_pk', Integer),
    Column('from_cusPK', Integer),
    Column('cFlag', CHAR(1, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('sit_id', UNIQUEIDENTIFIER),
    Column('cmths_id', UNIQUEIDENTIFIER),
    Column('cmtr_id', UNIQUEIDENTIFIER, nullable=False),
    Column('cmth_id', UNIQUEIDENTIFIER, nullable=False),
    Column('cmts_id', UNIQUEIDENTIFIER),
    Column('Items_id', UNIQUEIDENTIFIER)
)

t_jv_CMSoldItems = Table(
    'jv_CMSoldItems', metadata,
    Column('TICKETNUM', Integer, nullable=False),
    Column('STO_PK', SmallInteger, nullable=False),
    Column('DATEin', SMALLDATETIME),
    Column('SaleAmt', MONEY, nullable=False),
    Column('Taxable', MONEY, nullable=False),
    Column('Tax', MONEY, nullable=False),
    Column('ReturnedAmt', MONEY, nullable=False),
    Column('COMMENT', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('Trans', CHAR(1, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('SLD_Status', CHAR(1, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('DateOut', SMALLDATETIME),
    Column('Note', String(40, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('sld_id', UNIQUEIDENTIFIER),
    Column('Invnum', String(14, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('NumberSold', Numeric(9, 2), nullable=False),
    Column('Amount', MONEY, nullable=False),
    Column('Descript', String(254, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('TaxExempt', BIT, nullable=False),
    Column('Cost', MONEY, nullable=False),
    Column('Returnsold', DateTime),
    Column('Bin', CHAR(6, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('SIT_Status', CHAR(1, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('Items_pk', Integer, nullable=False),
    Column('ven_pk', Integer, nullable=False),
    Column('from_cusPK', Integer, nullable=False),
    Column('cFlag', CHAR(2, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('sit_id', UNIQUEIDENTIFIER),
    Column('cmths_id', UNIQUEIDENTIFIER, nullable=False),
    Column('cmtr_id', UNIQUEIDENTIFIER, nullable=False),
    Column('cmth_id', UNIQUEIDENTIFIER, nullable=False),
    Column('cmts_id', UNIQUEIDENTIFIER, nullable=False),
    Column('Items_id', UNIQUEIDENTIFIER)
)

t_jv_CMTH_CMTSD = Table(
    'jv_CMTH_CMTSD', metadata,
    Column('CMTR_Type', CHAR(10, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CMTR_Date', DateTime, nullable=False),
    Column('CMTR_Status', CHAR(2, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CMTH_Date', DateTime, nullable=False),
    Column('CMTH_Amount', MONEY, nullable=False),
    Column('CMTH_Type', CHAR(10, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CMTH_OverRideAmount', MONEY, nullable=False),
    Column('CMTH_SalesTax', Numeric(8, 2)),
    Column('Emp', String(8, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('Cus_PK', Integer, nullable=False),
    Column('Cus_FName', String(15, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('Cus_MName', String(15, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('Cus_LName', String(25, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CMTHT_StateTax', MONEY, nullable=False),
    Column('CMTHT_CountyTax', MONEY, nullable=False),
    Column('CMTHT_LocalTax', MONEY, nullable=False),
    Column('CMTSH_Discount', Numeric(9, 4), nullable=False),
    Column('CMTSD_Quantity', Integer, nullable=False),
    Column('CMTSD_Discount', Numeric(9, 4), nullable=False),
    Column('CMTSD_SaleAmount', MONEY, nullable=False),
    Column('CMTSD_Exempt', BIT, nullable=False),
    Column('Sto_PK', SmallInteger, nullable=False),
    Column('CMTR_ID', UNIQUEIDENTIFIER, nullable=False),
    Column('CMTH_ID', UNIQUEIDENTIFIER, nullable=False),
    Column('CMTHT_ID', UNIQUEIDENTIFIER, nullable=False),
    Column('CMTSH_ID', UNIQUEIDENTIFIER, nullable=False),
    Column('CMTSD_ID', UNIQUEIDENTIFIER, nullable=False),
    Column('Cus_ID', UNIQUEIDENTIFIER, nullable=False),
    Column('CMLC_ID', UNIQUEIDENTIFIER),
    Column('CMTH_Profit_Usr_ID', UNIQUEIDENTIFIER, nullable=False),
    Column('CMCD_ID', UNIQUEIDENTIFIER),
    Column('CMIPH_ID', UNIQUEIDENTIFIER, nullable=False),
    Column('cmtsd_fee', MONEY, nullable=False)
)

t_jv_CMTSDL_Cost = Table(
    'jv_CMTSDL_Cost', metadata,
    Column('CMTSD_ID', UNIQUEIDENTIFIER, nullable=False),
    Column('TotalQuantity', Integer),
    Column('TotalCost', Numeric(38, 4))
)

t_jv_CMVoidedTransactions = Table(
    'jv_CMVoidedTransactions', metadata,
    Column('CMTH_ID', UNIQUEIDENTIFIER, nullable=False),
    Column('CMTR_ID', UNIQUEIDENTIFIER, nullable=False),
    Column('cus_id', UNIQUEIDENTIFIER, nullable=False),
    Column('cmtr_type', CHAR(10, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('cmtr_date', DateTime, nullable=False),
    Column('cmtr_status', CHAR(2, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('Sto_PK', SmallInteger, nullable=False),
    Column('Usr_ID', UNIQUEIDENTIFIER, nullable=False),
    Column('CMCD_ID', UNIQUEIDENTIFIER),
    Column('cmlc_id', UNIQUEIDENTIFIER),
    Column('cmth_date', DateTime, nullable=False),
    Column('cmth_amount', MONEY, nullable=False),
    Column('cmth_type', CHAR(10, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CMTH_Profit_Usr_id', UNIQUEIDENTIFIER, nullable=False),
    Column('CMTH_OverRideAmount', MONEY, nullable=False),
    Column('cmth_salestax', Numeric(8, 2)),
    Column('cmcd_receipt', Integer),
    Column('cmcd_amount', MONEY, nullable=False),
    Column('cmst_id', UNIQUEIDENTIFIER),
    Column('cmlc_Long_Description', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('cmlc_Short_Description', CHAR(12, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('cmlc_lookup', CHAR(10, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('usr_lanid', String(8, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('usr_fname', String(15, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('usr_mname', String(15, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('usr_lname', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('Note', String(250, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('Station', Integer)
)

t_jv_CMWriteOff = Table(
    'jv_CMWriteOff', metadata,
    Column('cmtr_ID', UNIQUEIDENTIFIER, nullable=False),
    Column('cmck_cknumber', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('cmck_id', UNIQUEIDENTIFIER, nullable=False),
    Column('cmtr_type', CHAR(10, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('usr_id', UNIQUEIDENTIFIER, nullable=False),
    Column('cus_id', UNIQUEIDENTIFIER, nullable=False),
    Column('sto_pk', SmallInteger, nullable=False),
    Column('cmck_ckamount', Numeric(9, 2)),
    Column('DepositDate', DateTime, nullable=False),
    Column('cmta_dateout', DateTime),
    Column('Name', String(58, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('Type', CHAR(20, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('TypeDesc', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('cmtr_date', DateTime, nullable=False),
    Column('status', String(10, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('cmtr_status', CHAR(2, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('Maker', String(50, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('TicketNumber', Integer),
    Column('cmpy_cus_id', UNIQUEIDENTIFIER),
    Column('cmpy_id', UNIQUEIDENTIFIER, nullable=False),
    Column('cus_fname', String(15, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('cus_mname', String(15, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('cus_lname', String(25, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('cmpy_name', String(35, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('CKAccount', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('cmca_id', UNIQUEIDENTIFIER, nullable=False),
    Column('CKTransit', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('BankName', String(50, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('cmbk_id', UNIQUEIDENTIFIER, nullable=False),
    Column('TypeDescription', String(20, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('Remit', Numeric(19, 4)),
    Column('cmvt_vrnumber', String(20, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('nRTCharges', Numeric(9, 2)),
    Column('nRTFees', Numeric(9, 2)),
    Column('Amount', Numeric(19, 4)),
    Column('ReceiptNumber', Integer),
    Column('AdditionalCharge', Numeric(19, 4)),
    Column('AdditionalFee', Numeric(19, 4)),
    Column('cmdba_id', UNIQUEIDENTIFIER),
    Column('cmck_Altered_CKAmount', Numeric(9, 2)),
    Column('orig_CKAmount', Numeric(9, 2)),
    Column('cmck_directdebit', BIT),
    Column('cmca_account_type', CHAR(1, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('From_cmcbs_id', Integer),
    Column('From_usr_id', Integer),
    Column('From_cmcbs_type', String(1, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('cmcbs_description', String(1, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('cmdba_description', String(50, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('cmrh_id', UNIQUEIDENTIFIER),
    Column('cmcd_id', UNIQUEIDENTIFIER),
    Column('cmck_endorsed', BIT)
)

t_jv_CMWriteOff2 = Table(
    'jv_CMWriteOff2', metadata,
    Column('cmtr_id', UNIQUEIDENTIFIER, nullable=False),
    Column('cmck_cknumber', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('cmck_id', UNIQUEIDENTIFIER, nullable=False),
    Column('cmtr_type', CHAR(10, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('usr_id', UNIQUEIDENTIFIER, nullable=False),
    Column('cus_id', UNIQUEIDENTIFIER, nullable=False),
    Column('cmck_ckamount', Numeric(9, 2)),
    Column('DepositDate', DateTime, nullable=False),
    Column('Name', String(58, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('Type', CHAR(13, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('TypeDesc', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('cmtr_date', DateTime, nullable=False),
    Column('status', String(10, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('cmtr_status', CHAR(2, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('Maker', String(50, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('TicketNumber', Integer),
    Column('cmpy_cus_id', UNIQUEIDENTIFIER),
    Column('cmpy_id', UNIQUEIDENTIFIER, nullable=False),
    Column('cus_fname', String(15, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('cus_mname', String(15, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('cus_lname', String(25, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('cmpy_name', String(35, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('CKAccount', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('cmca_id', UNIQUEIDENTIFIER, nullable=False),
    Column('CKTransit', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('BankName', String(50, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('cmbk_id', UNIQUEIDENTIFIER, nullable=False),
    Column('cmbh_id', UNIQUEIDENTIFIER, nullable=False),
    Column('TypeDescription', String(20, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('Remit', Numeric(9, 2)),
    Column('cmvt_vrnumber', String(20, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('nRTCharges', Numeric(9, 2)),
    Column('nRTFees', Numeric(9, 2)),
    Column('cmdba_id', UNIQUEIDENTIFIER),
    Column('cmck_Altered_CKAmount', Numeric(9, 2)),
    Column('ReceiptNumber', String(1, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('cmrh_id', UNIQUEIDENTIFIER),
    Column('cmbh_check21', BIT),
    Column('cmbh_ck21proc', CHAR(2, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('cmck_endorsed', BIT),
    Column('cmbd_id', UNIQUEIDENTIFIER, nullable=False)
)

t_jv_CMWriteOff3 = Table(
    'jv_CMWriteOff3', metadata,
    Column('cmtr_id', UNIQUEIDENTIFIER, nullable=False),
    Column('cmck_cknumber', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('cmck_id', UNIQUEIDENTIFIER, nullable=False),
    Column('cmtr_type', CHAR(10, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('usr_id', UNIQUEIDENTIFIER, nullable=False),
    Column('cus_id', UNIQUEIDENTIFIER, nullable=False),
    Column('cmck_ckamount', Numeric(9, 2)),
    Column('DepositDate', DateTime, nullable=False),
    Column('Name', String(58, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('Type', CHAR(13, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('TypeDesc', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('cmtr_date', DateTime, nullable=False),
    Column('status', String(10, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('cmtr_status', CHAR(2, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('Maker', String(50, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('TicketNumber', Integer),
    Column('cmpy_cus_id', UNIQUEIDENTIFIER),
    Column('cmpy_id', UNIQUEIDENTIFIER, nullable=False),
    Column('cus_fname', String(15, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('cus_mname', String(15, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('cus_lname', String(25, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('cmpy_name', String(35, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('CKAccount', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('cmca_id', UNIQUEIDENTIFIER, nullable=False),
    Column('CKTransit', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('BankName', String(50, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('cmbk_id', UNIQUEIDENTIFIER, nullable=False),
    Column('cmbh_id', UNIQUEIDENTIFIER, nullable=False),
    Column('TypeDescription', String(20, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('Remit', Numeric(9, 2)),
    Column('cmvt_vrnumber', String(20, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('nRTCharges', Numeric(9, 2)),
    Column('nRTFees', Numeric(9, 2)),
    Column('cmrh_id', UNIQUEIDENTIFIER)
)

t_jv_CM_TenderAmounts = Table(
    'jv_CM_TenderAmounts', metadata,
    Column('cmcd_id', UNIQUEIDENTIFIER, nullable=False),
    Column('Tender1Amount', Numeric(19, 4), nullable=False),
    Column('Tender2Amount', Numeric(19, 4), nullable=False),
    Column('ChangeAmount', Numeric(19, 4), nullable=False),
    Column('Tender1ShortDesc', CHAR(12, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('Tender1Lookup', CHAR(10, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('Tender2ShortDesc', CHAR(12, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('Tender2Lookup', CHAR(10, 'SQL_Latin1_General_CP1_CI_AS'))
)

t_jv_CheckView = Table(
    'jv_CheckView', metadata,
    Column('Sto_PK', SmallInteger, nullable=False),
    Column('Type', CHAR(10, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('DateIn', DateTime, nullable=False),
    Column('Status', CHAR(2, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('Fee', MONEY),
    Column('CalcFee', MONEY),
    Column('CkDate', DateTime, nullable=False),
    Column('CkAmount', MONEY, nullable=False),
    Column('CkNumber', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('Account', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('Account_Type', CHAR(1, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('Routing', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('Bank_Address1', String(50, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('Bank_Address2', String(25, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('Bank_City', String(50, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('Bank_State', CHAR(2, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('Bank_Zip', CHAR(10, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('Bank_Phone', CHAR(3, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('Bank_Name', String(50, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('Emp', String(8, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CMPY_ID', UNIQUEIDENTIFIER, nullable=False),
    Column('Payor_Cus_ID', UNIQUEIDENTIFIER),
    Column('Payor_Name', String(41, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('Payor_Address1', String(25, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('Payor_Address2', String(25, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('Payor_City', String(50, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('Payor_State', CHAR(2, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('Payor_Zip', CHAR(10, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('Payor_Entered', DateTime),
    Column('Payor_BadPayor', BIT),
    Column('Payor_Min', MONEY),
    Column('Payor_Max', MONEY),
    Column('Payor_AC', CHAR(3, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('Payor_Phone', String(20, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('Cus_Store', Integer, nullable=False),
    Column('Cus_PK', Integer, nullable=False),
    Column('Cus_FName', String(15, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('Cus_MName', String(15, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('Cus_LName', String(25, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('Cus_Add1', String(25, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('Cus_Add2', String(25, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('Cus_City', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('Cus_State', String(2, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('Cus_Zip', String(10, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('Cus_Country', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('Cus_AC1', String(3, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('Cus_Phone1', String(8, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('Cus_Height', String(6, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('Cus_Weight', SmallInteger, nullable=False),
    Column('Hair', String(20, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('Eyes', String(20, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('Race', String(20, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('Cus_Sex', String(1, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('Cus_Marks', String(40, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('Cus_BirthDate', SMALLDATETIME),
    Column('Cus_BirthCity', String(15, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('Cus_BirthState', String(2, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('Cus_Birth2', String(15, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('Cus_ID1', String(20, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('Cus_IDNum1', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('Cus_ID1Exp', SMALLDATETIME),
    Column('Cus_ID1Issue', String(50, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('Cus_ID2', String(20, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('Cus_IDNum2', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('Cus_ID2Exp', SMALLDATETIME),
    Column('Cus_ID2Issue', String(2, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('Cus_Known', BIT, nullable=False),
    Column('Cus_SSNum', String(11, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('Cus_Vehic1', String(10, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('Cus_Vehic2', String(8, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('Cus_Vehic3', String(2, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('Cus_Employer', String(40, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('Cus_EmpAd1', String(35, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('Cus_EmpAd2', String(35, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('Cus_EmpCity', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('Cus_EmpState', String(2, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('Cus_EmpZip', String(10, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('Cus_AC2', String(3, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('Cus_EmpPhone', String(14, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('Cus_Comment', String(200, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('Cus_TotalPawns', Integer, nullable=False),
    Column('Cus_ActivePawn', Integer, nullable=False),
    Column('Cus_Redeemed', Integer, nullable=False),
    Column('Cus_Buys', Integer, nullable=False),
    Column('Cus_Sales', MONEY, nullable=False),
    Column('Cus_Amt1', MONEY, nullable=False),
    Column('Cus_Amt2', MONEY, nullable=False),
    Column('Cus_FFLNum', String(25, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('Cus_Delete', BIT, nullable=False),
    Column('Cus_Locked', BIT, nullable=False),
    Column('Cus_Pawner', BIT, nullable=False),
    Column('Cus_Buyer', BIT, nullable=False),
    Column('Cus_IDAdd1', String(25, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('Cus_IDAdd2', String(25, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('Cus_IDCity', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('Cus_IDState', String(2, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('Cus_IDZip', String(10, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('Cus_Credit', MONEY, nullable=False),
    Column('Special', String(20, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('Cus_Pic_FK', Integer, nullable=False),
    Column('Cus_ID', UNIQUEIDENTIFIER),
    Column('CMTR_ID', UNIQUEIDENTIFIER, nullable=False),
    Column('Usr_ID', UNIQUEIDENTIFIER, nullable=False),
    Column('CMRH_ID', UNIQUEIDENTIFIER),
    Column('CMCK_ID', UNIQUEIDENTIFIER, nullable=False),
    Column('CMBK_ID', UNIQUEIDENTIFIER, nullable=False)
)

t_jv_CustView = Table(
    'jv_CustView', metadata,
    Column('Cus_Store', Integer, nullable=False),
    Column('Cus_PK', Integer, nullable=False),
    Column('Cus_FName', String(15, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('Cus_MName', String(15, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('Cus_LName', String(25, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('Cus_Add1', String(25, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('Cus_Add2', String(25, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('Cus_City', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('Cus_State', String(2, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('Cus_Zip', String(10, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('Cus_Country', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('Cus_AC1', String(3, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('Cus_Phone1', String(8, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('Cus_Height', String(6, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('Cus_Weight', SmallInteger, nullable=False),
    Column('Hair', String(20, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('Eyes', String(20, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('Race', String(20, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('Cus_Sex', String(1, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('Cus_Marks', String(40, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('Cus_BirthDate', SMALLDATETIME),
    Column('Cus_BirthCity', String(15, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('Cus_BirthState', String(2, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('Cus_Birth2', String(15, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('Cus_ID1', String(20, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('Cus_IDNum1', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('Cus_ID1Exp', SMALLDATETIME),
    Column('Cus_ID1Issue', String(50, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('Cus_ID2', String(20, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('Cus_IDNum2', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('Cus_ID2Exp', SMALLDATETIME),
    Column('Cus_ID2Issue', String(2, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('Cus_Known', BIT, nullable=False),
    Column('Cus_SSNum', String(11, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('Cus_Vehic1', String(10, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('Cus_Vehic2', String(8, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('Cus_Vehic3', String(2, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('Cus_Employer', String(40, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('Cus_EmpAd1', String(35, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('Cus_EmpAd2', String(35, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('Cus_EmpCity', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('Cus_EmpState', String(2, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('Cus_EmpZip', String(10, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('Cus_AC2', String(3, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('Cus_EmpPhone', String(14, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('Cus_Comment', String(200, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('Cus_TotalPawns', Integer, nullable=False),
    Column('Cus_ActivePawn', Integer, nullable=False),
    Column('Cus_Redeemed', Integer, nullable=False),
    Column('Cus_Buys', Integer, nullable=False),
    Column('Cus_Sales', MONEY, nullable=False),
    Column('Cus_Amt1', MONEY, nullable=False),
    Column('Cus_Amt2', MONEY, nullable=False),
    Column('Cus_FFLNum', String(25, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('Cus_Delete', BIT, nullable=False),
    Column('Cus_Locked', BIT, nullable=False),
    Column('Cus_Pawner', BIT, nullable=False),
    Column('Cus_Buyer', BIT, nullable=False),
    Column('Cus_IDAdd1', String(25, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('Cus_IDAdd2', String(25, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('Cus_IDCity', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('Cus_IDState', String(2, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('Cus_IDZip', String(10, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('Cus_Credit', MONEY, nullable=False),
    Column('Special', String(20, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('Cus_Pic_FK', Integer, nullable=False),
    Column('Cus_ID', UNIQUEIDENTIFIER)
)

t_jv_PayorView = Table(
    'jv_PayorView', metadata,
    Column('CMPY_ID', UNIQUEIDENTIFIER, nullable=False),
    Column('Sto_PK', SmallInteger, nullable=False),
    Column('Cus_ID', UNIQUEIDENTIFIER),
    Column('Payor_Name', String(41, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('Payor_Address1', String(25, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('Payor_Address2', String(25, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('Payor_City', String(50, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('Payor_State', CHAR(2, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('Payor_Zip', CHAR(10, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('Payor_Entered', DateTime),
    Column('Payor_BadPayor', BIT),
    Column('Payor_Min', MONEY),
    Column('Payor_Max', MONEY),
    Column('Payor_AC', CHAR(3, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('Payor_Phone', String(20, 'SQL_Latin1_General_CP1_CI_AS'))
)

t_languageinput_cm = Table(
    'languageinput_cm', metadata,
    Column('LangID', Integer, nullable=False),
    Column('Edited', DateTime, nullable=False),
    Column('NetID', CHAR(33, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('Llang', CHAR(2, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('Slibr', CHAR(64, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('Sproc', CHAR(64, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('Sline', Integer, nullable=False),
    Column('En', CHAR(254, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('EsFont', CHAR(48, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('Es', CHAR(254, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('PtFont', CHAR(48, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('Pt', CHAR(254, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('RuFont', CHAR(48, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('Ru', CHAR(254, 'SQL_Latin1_General_CP1_CI_AS'))
)

t_languageinput_pm = Table(
    'languageinput_pm', metadata,
    Column('LangID', Integer, nullable=False),
    Column('Edited', DateTime, nullable=False),
    Column('NetID', CHAR(33, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('Llang', CHAR(2, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('Slibr', CHAR(64, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('Sproc', CHAR(64, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('Sline', Integer, nullable=False),
    Column('En', CHAR(254, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('EsFont', CHAR(48, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('Es', CHAR(254, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('PtFont', CHAR(48, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('Pt', CHAR(254, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('GrFont', CHAR(48, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('Gr', CHAR(254, 'SQL_Latin1_General_CP1_CI_AS'))
)

t_laysview = Table(
    'laysview', metadata,
    Column('TICKETNUM', Integer, nullable=False),
    Column('DATEin', SMALLDATETIME),
    Column('DATEout', SMALLDATETIME),
    Column('saletotal', MONEY),
    Column('DEPOSIT', MONEY, nullable=False),
    Column('STATUS', CHAR(1, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('status2', String(25, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('NOTE', String(40, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_ID', UNIQUEIDENTIFIER),
    Column('CUS_FNAME', String(15, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('CUS_LNAME', String(25, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('CUS_TXTMSG', BIT),
    Column('CUS_CELLPHONE', String(20, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('CUS_TXTMSGSENT', DateTime),
    Column('INVNUM', String(14, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('DESCRIPT', String(254, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('NUMBERSOLD', Numeric(9, 2)),
    Column('AMOUNT', MONEY),
    Column('TAXEXEMPT', BIT),
    Column('COST', MONEY),
    Column('STO_PK', SmallInteger, nullable=False),
    Column('USR_fk', Integer, nullable=False),
    Column('BIN', CHAR(6, 'SQL_Latin1_General_CP1_CI_AS'))
)

t_loggedinusers = Table(
    'loggedinusers', metadata,
    Column('LIU_PK', Integer, nullable=False),
    Column('STO_PK', SmallInteger, nullable=False, index=True, server_default=text("(1)")),
    Column('CPU_NAME', String(200, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("('')")),
    Column('LoginTime', DateTime),
    Column('LIU_id', UNIQUEIDENTIFIER, server_default=text("(newid())"))
)


class MccModCustCredit(Base):
    __tablename__ = 'mcc_ModCustCredit'

    MCC_ID = Column(UNIQUEIDENTIFIER, primary_key=True, server_default=text("(newid())"))
    Cus_PK = Column(Integer, nullable=False, index=True)
    Cus_ID = Column(UNIQUEIDENTIFIER, index=True)
    Usr_ID = Column(UNIQUEIDENTIFIER, nullable=False)
    Sto_pk = Column(SmallInteger, nullable=False, server_default=text("(1)"))
    CreditDate = Column(DateTime, nullable=False, index=True)
    CreditAmount = Column(MONEY, nullable=False)


t_memoview = Table(
    'memoview', metadata,
    Column('TICKETNUM', Integer),
    Column('STO_PK', SmallInteger),
    Column('CUS_FK', Integer),
    Column('DATEin', SMALLDATETIME),
    Column('DATEout', SMALLDATETIME),
    Column('SaleAmt', MONEY),
    Column('Taxable', MONEY),
    Column('TAX', MONEY),
    Column('type', CHAR(1, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('sstatus', CHAR(1, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('status2', String(25, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('istatus', CHAR(1, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('INVNUM', String(14, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('NUMBERSOLD', Numeric(9, 2), nullable=False),
    Column('RETURNSOLD', DateTime),
    Column('AMOUNT', MONEY, nullable=False),
    Column('DESCRIPT', String(254, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('COST', MONEY, nullable=False),
    Column('TAXEXEMPT', BIT, nullable=False),
    Column('items_pk', Integer, nullable=False),
    Column('USR_LANID', String(8, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('Cus_fname', String(15, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('cus_lname', String(25, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('status3', String(25, 'SQL_Latin1_General_CP1_CI_AS'))
)

t_pd_physdetail = Table(
    'pd_physdetail', metadata,
    Column('pd_id', UNIQUEIDENTIFIER, nullable=False, unique=True, server_default=text("(newid())")),
    Column('ph_id', UNIQUEIDENTIFIER, nullable=False, index=True),
    Column('sto_pk', SmallInteger, nullable=False),
    Column('emp_id', UNIQUEIDENTIFIER, nullable=False),
    Column('pd_physdate', DateTime, nullable=False),
    Column('invnum', String(14, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('ticketnum', Integer),
    Column('pd_oldbin', String(6, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('pd_scansqty', DECIMAL(9, 2), nullable=False, server_default=text("(0.00)")),
    Column('pd_scanlocation', String(50, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('pd_status', CHAR(2, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
)

t_plhours = Table(
    'plhours', metadata,
    Column('Hrs_PK', Integer, nullable=False),
    Column('STO_PK', SmallInteger, server_default=text("CREATE DEFAULT dbo.UW_ZeroDefault AS 0")),
    Column('USR_FK', Integer, server_default=text("CREATE DEFAULT dbo.UW_ZeroDefault AS 0")),
    Column('TimeIN', DateTime),
    Column('TimeOUT', DateTime),
    Column('HRS_id', UNIQUEIDENTIFIER, unique=True, server_default=text("(newid())")),
    Column('LastUpdatedUSR_ID', UNIQUEIDENTIFIER),
    Index('IDX_plhours_Sto_PK_Usr_FK_TimeOut', 'USR_FK', 'TimeOUT', 'STO_PK')
)

t_repair = Table(
    'repair', metadata,
    Column('repair_pk', Integer, nullable=False),
    Column('TicketNum', Integer, nullable=False, server_default=text("((-1))")),
    Column('STO_PK', SmallInteger, nullable=False, server_default=text("(1)")),
    Column('PROMISEDATE', SMALLDATETIME),
    Column('SUBOUT', SMALLDATETIME),
    Column('SUBIN', SMALLDATETIME),
    Column('SUBTO', String(35, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("(' ')")),
    Column('vend_fk', Integer, nullable=False, server_default=text("((-1))")),
    Column('WORK1', String(254, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("(' ')")),
    Column('Items_PK', Integer, nullable=False, server_default=text("(0)")),
    Column('subStatus', String(15, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("(' ')")),
    Column('Quantity', DECIMAL(9, 2), nullable=False, server_default=text("(0.00)")),
    Column('invDateIN', SMALLDATETIME),
    Column('invDateOUT', SMALLDATETIME),
    Column('AddedCost', MONEY, nullable=False, server_default=text("(0.00)")),
    Column('REP_id', UNIQUEIDENTIFIER, unique=True, server_default=text("(newid())")),
    Column('LastUpdatedUSR_ID', UNIQUEIDENTIFIER),
    Index('IDX_repair_Sto_PK_TicketNum', 'TicketNum', 'STO_PK'),
    Index('IDX_repair_Sto_PK_Items_PK', 'Items_PK', 'STO_PK')
)


class Repomain(Base):
    __tablename__ = 'repomain'

    sto_pk = Column(Integer, primary_key=True, nullable=False)
    xt_pk = Column(Integer, primary_key=True, nullable=False)
    rep_name = Column(String(25, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    password = Column(String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    x_frx = Column(Text(2147483647, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    x_frt = Column(Text(2147483647, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    src_name = Column(String(30, 'SQL_Latin1_General_CP1_CI_AS'))
    fileTime = Column(String(30, 'SQL_Latin1_General_CP1_CI_AS'))
    RPM_id = Column(UNIQUEIDENTIFIER, unique=True, server_default=text("(newid())"))
    LastUpdatedUSR_ID = Column(UNIQUEIDENTIFIER)


class Sitem(Base):
    __tablename__ = 'sitems'
    __table_args__ = (
        Index('IDX_Sitems_Items_ID_Items_PK', 'Items_ID', 'items_pk'),
        Index('IDX_sitems_Sto_PK_TicketNum', 'Sto_PK', 'TICKETNUM'),
        Index('IDX_sitems_Sto_PK_InvNum', 'INVNUM', 'Sto_PK'),
        Index('IDX_Sitems_Status_CFlag', 'Status', 'cFlag')
    )

    sItem_PK = Column(Integer, primary_key=True)
    Sto_PK = Column(SmallInteger, nullable=False, server_default=text("(1)"))
    TICKETNUM = Column(Integer, nullable=False, server_default=text("(0)"))
    INVNUM = Column(String(14, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("('')"))
    NUMBERSOLD = Column(Numeric(9, 2), nullable=False, server_default=text("(0.00)"))
    AMOUNT = Column(MONEY, nullable=False, server_default=text("(0.00)"))
    DESCRIPT = Column(String(254, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("('')"))
    TAXEXEMPT = Column(BIT, nullable=False, server_default=text("(0)"))
    COST = Column(MONEY, nullable=False, server_default=text("(0.0)"))
    RETURNSOLD = Column(DateTime)
    BIN = Column(CHAR(6, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("('')"))
    Status = Column(CHAR(1, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("('')"))
    items_pk = Column(Integer, nullable=False, server_default=text("(0)"))
    ven_pk = Column(Integer, nullable=False, index=True, server_default=text("(0)"))
    from_cusPK = Column(Integer, nullable=False, index=True, server_default=text("(0)"))
    cFlag = Column(CHAR(2, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("(' ')"))
    SIT_id = Column(UNIQUEIDENTIFIER, unique=True, server_default=text("(newid())"))
    CountyTaxExempt = Column(BIT, nullable=False, server_default=text("(0)"))
    LastUpdatedUSR_ID = Column(UNIQUEIDENTIFIER)
    Items_ID = Column(UNIQUEIDENTIFIER, index=True)
    SalesLoc = Column(String(1, 'SQL_Latin1_General_CP1_CI_AS'))


t_sold = Table(
    'sold', metadata,
    Column('Sold_pk', Integer, nullable=False),
    Column('TICKETNUM', Integer, nullable=False, server_default=text("(1)")),
    Column('STO_PK', SmallInteger, nullable=False, index=True, server_default=text("(1)")),
    Column('USR_fk', Integer, nullable=False, server_default=text("(1)")),
    Column('DATEin', SMALLDATETIME),
    Column('PrevDate', SMALLDATETIME),
    Column('SaleAmt', MONEY, nullable=False, server_default=text("(0.00)")),
    Column('Taxable', MONEY, nullable=False, server_default=text("(0.00)")),
    Column('TAX', MONEY, nullable=False, server_default=text("(0.00)")),
    Column('ReturnedAmt', MONEY, nullable=False, server_default=text("(0.00)")),
    Column('CUS_FK', Integer, nullable=False, index=True, server_default=text("(1)")),
    Column('COMMENT', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("('')")),
    Column('TRANS', CHAR(1, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("('')")),
    Column('STATUS', CHAR(1, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("('')")),
    Column('DATEout', SMALLDATETIME),
    Column('SRVCHGPERC', Float(24), nullable=False, server_default=text("(0.0)")),
    Column('SRVCHGGRAC', SmallInteger, nullable=False, server_default=text("(0)")),
    Column('SRVCHGAMT', MONEY, nullable=False, server_default=text("(0.00)")),
    Column('DEPOSIT', MONEY, nullable=False, server_default=text("(0.00)")),
    Column('PERIOD', SmallInteger, nullable=False, server_default=text("(0)")),
    Column('NOTE', String(40, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("('')")),
    Column('GunProcFee', MONEY, nullable=False, server_default=text("(0.00)")),
    Column('AuctionEntry', BIT, nullable=False, server_default=text("(0)")),
    Column('SLD_id', UNIQUEIDENTIFIER, unique=True, server_default=text("(newid())")),
    Column('CountyTaxable', MONEY, nullable=False, server_default=text("(0)")),
    Column('Reminder', SMALLDATETIME),
    Column('sld_Message', String(254, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('LastUpdatedUSR_ID', UNIQUEIDENTIFIER),
    Index('IDX_Sold_Sto_PK_Sld_ID_Ticketnum', 'STO_PK', 'SLD_id', 'TICKETNUM'),
    Index('IDX_SOLD_MultiKey1', 'TRANS', 'STATUS', 'TICKETNUM', 'STO_PK', 'CUS_FK', 'DATEin', 'DATEout', 'USR_fk'),
    Index('IDX_SOLD_MultiKey2', 'TICKETNUM', 'STO_PK', 'CUS_FK', 'DATEin', 'TRANS'),
    Index('IDX_sold_Sto_PK_TicketNum', 'TICKETNUM', 'STO_PK')
)


class Statprov(Base):
    __tablename__ = 'statprov'
    __table_args__ = (
        Index('IDX_statprov_SPR_CRYFK_SPR_Abbrev', 'SPR_CRYFK', 'SPR_ABBREV'),
    )

    SPR_PK = Column(Integer, primary_key=True)
    SPR_CRYFK = Column(String(5, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, index=True,
                       server_default=text("('')"))
    SPR_ABBREV = Column(String(5, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, index=True,
                        server_default=text("('')"))
    SPR_NAME = Column(String(40, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("('')"))
    SPR_id = Column(UNIQUEIDENTIFIER, unique=True, server_default=text("(newid())"))
    LastUpdatedUSR_ID = Column(UNIQUEIDENTIFIER)


t_sy5_SysInfo5 = Table(
    'sy5_SysInfo5', metadata,
    Column('sy5_ID', UNIQUEIDENTIFIER, nullable=False, unique=True, server_default=text("(newid())")),
    Column('sy5_NO', Integer, nullable=False),
    Column('sto_pk', SmallInteger, nullable=False),
    Column('sy5_Lookup', CHAR(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('sy5_value', String(2000, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('sy5_datatype', CHAR(1, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('LastUpdatedUSR_ID', UNIQUEIDENTIFIER, server_default=text("('F79DBA72-7207-4CCE-A271-FC83D727F283')")),
    Index('IDX_sy5_SysInfo5_Sto_PK_Sy5_Lookukp', 'sy5_Lookup', 'sto_pk')
)

t_tv_CMBD = Table(
    'tv_CMBD', metadata,
    Column('cmbd_id', UNIQUEIDENTIFIER, nullable=False),
    Column('cmbh_id', UNIQUEIDENTIFIER, nullable=False),
    Column('sto_pk', SmallInteger, nullable=False),
    Column('cmth_id', UNIQUEIDENTIFIER, nullable=False),
    Column('cmck_id', UNIQUEIDENTIFIER)
)

t_tv_CMBH = Table(
    'tv_CMBH', metadata,
    Column('cmbh_id', UNIQUEIDENTIFIER, nullable=False),
    Column('cmbh_no', Integer, nullable=False),
    Column('sto_pk', SmallInteger, nullable=False),
    Column('cmbh_type', CHAR(2, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('cmbh_date', DateTime, nullable=False),
    Column('cmbh_status', CHAR(1, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('usr_id', UNIQUEIDENTIFIER, nullable=False),
    Column('cmbh_check21', BIT),
    Column('cmbh_ck21proc', CHAR(2, 'SQL_Latin1_General_CP1_CI_AS'))
)

t_tv_CMBK = Table(
    'tv_CMBK', metadata,
    Column('cmbk_id', UNIQUEIDENTIFIER, nullable=False),
    Column('cmbk_transit', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('cmbk_address1', String(50, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('cmbk_address2', String(25, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('cmbk_city', String(50, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('cmbk_state', CHAR(2, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('cmbk_zip', CHAR(10, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('cmbk_ac', CHAR(3, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('cmbk_phone', String(20, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('cmbk_name', String(50, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
)

t_tv_CMCA = Table(
    'tv_CMCA', metadata,
    Column('cmca_ID', UNIQUEIDENTIFIER, nullable=False),
    Column('cmbk_id', UNIQUEIDENTIFIER, nullable=False),
    Column('sto_pk', SmallInteger, nullable=False),
    Column('cmca_Account', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('cmpy_id', UNIQUEIDENTIFIER, nullable=False),
    Column('cmca_account_type', CHAR(1, 'SQL_Latin1_General_CP1_CI_AS'))
)

t_tv_CMCD = Table(
    'tv_CMCD', metadata,
    Column('cmcd_id', UNIQUEIDENTIFIER, nullable=False),
    Column('cmcd_receipt', Integer),
    Column('cmcd_amount', MONEY, nullable=False),
    Column('sto_pk', SmallInteger, nullable=False),
    Column('cmcd_print_cknumber', Integer),
    Column('cmcd_date', DateTime, nullable=False),
    Column('usr_id', UNIQUEIDENTIFIER, nullable=False),
    Column('cmcd_print_ckreturned', BIT),
    Column('cmst_id', UNIQUEIDENTIFIER),
    Column('cmck_id', UNIQUEIDENTIFIER),
    Column('cmcbs_id', UNIQUEIDENTIFIER),
    Column('cmcd_credit', MONEY),
    Column('cus_id', UNIQUEIDENTIFIER, nullable=False)
)

t_tv_CMCK = Table(
    'tv_CMCK', metadata,
    Column('cmck_id', UNIQUEIDENTIFIER, nullable=False),
    Column('sto_pk', SmallInteger, nullable=False),
    Column('cmca_id', UNIQUEIDENTIFIER, nullable=False),
    Column('cmck_ckdate', DateTime, nullable=False),
    Column('cmck_ckamount', MONEY, nullable=False),
    Column('cmck_cknumber', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('cmck_directdebit', BIT),
    Column('cmdba_id', UNIQUEIDENTIFIER),
    Column('cmck_Altered_CKAmount', MONEY),
    Column('cmck_endorsed', BIT),
    Column('cus_id', UNIQUEIDENTIFIER, nullable=False)
)

t_tv_CMCLVT = Table(
    'tv_CMCLVT', metadata,
    Column('cmclvt_ID', UNIQUEIDENTIFIER, nullable=False),
    Column('cmtr_id', UNIQUEIDENTIFIER),
    Column('cus_id', UNIQUEIDENTIFIER, nullable=False),
    Column('cmclvt_tran_id', String(8, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('cmclvt_clv_id', String(8, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('cmclvt_loannumber', String(24, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('cmclvt_transaction', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('sto_pk', SmallInteger, nullable=False),
    Column('cmclvt_rtcharges', MONEY, nullable=False),
    Column('cmclvt_rtfees', MONEY, nullable=False),
    Column('cmclvt_fee1', MONEY, nullable=False),
    Column('cmclvt_fee2', MONEY, nullable=False),
    Column('cmclvt_status', CHAR(2, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('cmclvt_orig_amount', MONEY),
    Column('cmclvt_loanrpt', Text(2147483647, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('cmclvt_upload', BIT)
)

t_tv_CMCT = Table(
    'tv_CMCT', metadata,
    Column('cmct_id', UNIQUEIDENTIFIER, nullable=False),
    Column('cmcd_id', UNIQUEIDENTIFIER, nullable=False),
    Column('sto_pk', SmallInteger, nullable=False),
    Column('luc_id', UNIQUEIDENTIFIER),
    Column('cmct_amount', MONEY, nullable=False),
    Column('cmct_Change_Ind', BIT, nullable=False),
    Column('CMLC_ID', UNIQUEIDENTIFIER),
    Column('cmct_order', SmallInteger)
)

t_tv_CMCU = Table(
    'tv_CMCU', metadata,
    Column('cmcu_id', UNIQUEIDENTIFIER, nullable=False),
    Column('cus_ID', UNIQUEIDENTIFIER, nullable=False),
    Column('sto_pk', SmallInteger, nullable=False),
    Column('cmcu_maidenname', String(25, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('cmcu_badcust', BIT),
    Column('cmcu_paydate', DateTime),
    Column('cmcu_payfreq', CHAR(1, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('cmcu_payrate', Numeric(18, 0)),
    Column('cmcu_payratefreq', CHAR(1, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('cmcu_directdeposit', BIT),
    Column('cmcu_dba', String(40, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('cmcu_jobtitle', String(30, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('cmcu_bankruptcy', BIT),
    Column('cmcu_garnishment', BIT),
    Column('cmcu_ownhome', BIT),
    Column('cmcu_points', Integer),
    Column('cmcu_pointsavailable', Integer),
    Column('cmcu_credit', MONEY),
    Column('cmcu_pointsmailer', BIT),
    Column('cmcu_pointtrans', Integer),
    Column('cmcu_pointslast', DateTime),
    Column('cmcu_taxexempt', BIT)
)

t_tv_CMDV = Table(
    'tv_CMDV', metadata,
    Column('CMDV_ID', UNIQUEIDENTIFIER, nullable=False),
    Column('CMDV_Manufacturer', CHAR(64, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('CMDV_ManufSupport', CHAR(16, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('CMDV_ManufURL', CHAR(128, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('CMDV_Model', CHAR(64, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('CMDV_Type', CHAR(32, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('CMDV_ExternalFile', CHAR(32, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('CMDV_ExternalClass', CHAR(32, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('CMDV_ExternalModule', CHAR(32, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('CMDV_Timestamp', BINARY(8))
)

t_tv_CMLB = Table(
    'tv_CMLB', metadata,
    Column('cmlb_id', UNIQUEIDENTIFIER, nullable=False),
    Column('cmlb_descript', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('cmlb_update', BIT, nullable=False),
    Column('cmlb_replace', BIT, nullable=False),
    Column('cmlb_add', BIT, nullable=False),
    Column('cmlb_delete', BIT, nullable=False)
)

t_tv_CMLC = Table(
    'tv_CMLC', metadata,
    Column('cmlc_id', UNIQUEIDENTIFIER, nullable=False),
    Column('cmlb_id', UNIQUEIDENTIFIER, nullable=False),
    Column('cmlc_Long_Description', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('cmlc_active', BIT),
    Column('cmlc_Short_Description', CHAR(12, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('cmlc_lookup', CHAR(10, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('cmlc_locked', BIT, nullable=False)
)

t_tv_CMPY = Table(
    'tv_CMPY', metadata,
    Column('cmpy_id', UNIQUEIDENTIFIER, nullable=False),
    Column('sto_pk', SmallInteger, nullable=False),
    Column('cus_id', UNIQUEIDENTIFIER),
    Column('cmpy_name', String(35, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('cmpy_address1', String(25, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('cmpy_address2', String(25, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('cmpy_city', String(50, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('cmpy_state', CHAR(2, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('cmpy_zip', CHAR(10, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('cmpy_entered', DateTime),
    Column('cmpy_badpayor', BIT),
    Column('cmpy_min', MONEY),
    Column('cmpy_max', MONEY),
    Column('cmpy_ac', CHAR(3, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('cmpy_phone', String(20, 'SQL_Latin1_General_CP1_CI_AS'))
)

t_tv_CMRA = Table(
    'tv_CMRA', metadata,
    Column('cmra_id', UNIQUEIDENTIFIER, nullable=False),
    Column('cmrh_id', UNIQUEIDENTIFIER, nullable=False),
    Column('sto_pk', SmallInteger, nullable=False),
    Column('cmra_hd', MONEY, nullable=False),
    Column('cmra_dp', CHAR(1, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('cmra_ap', MONEY, nullable=False),
    Column('CMRA_FeeDP', CHAR(1, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CMRA_Fee', MONEY, nullable=False),
    Column('CMRA_Minimum', MONEY, nullable=False),
    Column('CMRA_ISMonthPR', BIT, nullable=False),
    Column('CMRA_NumDays', SmallInteger, nullable=False)
)

t_tv_CMRC = Table(
    'tv_CMRC', metadata,
    Column('cmrc_id', UNIQUEIDENTIFIER, nullable=False),
    Column('cmrh_id', UNIQUEIDENTIFIER, nullable=False),
    Column('sto_pk', SmallInteger, nullable=False),
    Column('cmrc_hd', MONEY, nullable=False),
    Column('cmrc_dp', CHAR(1, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('cmrc_ap', MONEY, nullable=False),
    Column('cmrc_dp2', CHAR(1, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('cmrc_ap2', MONEY, nullable=False)
)

t_tv_CMRF = Table(
    'tv_CMRF', metadata,
    Column('cmrf_id', UNIQUEIDENTIFIER, nullable=False),
    Column('cus_id', UNIQUEIDENTIFIER, nullable=False),
    Column('cmrf_Name', String(60, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('cmrf_Phone', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
)

t_tv_CMRH = Table(
    'tv_CMRH', metadata,
    Column('cmrh_id', UNIQUEIDENTIFIER, nullable=False),
    Column('cmrh_descript', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('cmrh_printdescript', String(10, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('sto_pk', SmallInteger, nullable=False),
    Column('cmrh_active', BIT, nullable=False),
    Column('cmdba_id', UNIQUEIDENTIFIER)
)

t_tv_CMRL = Table(
    'tv_CMRL', metadata,
    Column('CMRL_ID', UNIQUEIDENTIFIER, nullable=False),
    Column('CMRL_ReportKey', Integer, nullable=False),
    Column('CMRL_CustKey', CHAR(10, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CMRL_cType', CHAR(25, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CMRL_defmenuacc', Integer, nullable=False),
    Column('CMRL_cFullname', CHAR(50, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CMRL_cFilename', CHAR(25, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CMRL_HasTotals', BIT, nullable=False),
    Column('CMRL_prt_prev', BIT, nullable=False),
    Column('CMRL_Start', Text(2147483647, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CMRL_CompStart', Text(2147483647, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('CMRL_Status', CHAR(1, 'SQL_Latin1_General_CP1_CI_AS'))
)

t_tv_CMRM = Table(
    'tv_CMRM', metadata,
    Column('cmrm_id', UNIQUEIDENTIFIER, nullable=False),
    Column('cmrh_id', UNIQUEIDENTIFIER, nullable=False),
    Column('sto_pk', SmallInteger, nullable=False),
    Column('cmrm_hd', MONEY, nullable=False),
    Column('cmrm_dp', CHAR(1, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('cmrm_ap', MONEY, nullable=False),
    Column('cmrm_costdp', CHAR(1, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('cmrm_cost', MONEY, nullable=False)
)

t_tv_CMRQ = Table(
    'tv_CMRQ', metadata,
    Column('cmrq_id', UNIQUEIDENTIFIER, nullable=False),
    Column('sto_pk', Integer, nullable=False),
    Column('sycl_id', UNIQUEIDENTIFIER, nullable=False),
    Column('cmrq_required', BIT, nullable=False),
    Column('cmrq_sort', Integer, nullable=False),
    Column('cmrq_locked', BIT, nullable=False)
)

t_tv_CMRS = Table(
    'tv_CMRS', metadata,
    Column('CMRS_ID', UNIQUEIDENTIFIER, nullable=False),
    Column('CMRL_ID', UNIQUEIDENTIFIER, nullable=False),
    Column('Sto_pk', Integer, nullable=False),
    Column('CMRS_MenuAccess', SmallInteger, nullable=False),
    Column('CMRS_Comment', Text(2147483647, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
)

t_tv_CMSC = Table(
    'tv_CMSC', metadata,
    Column('CMSC_ID', UNIQUEIDENTIFIER, nullable=False),
    Column('CMSC_Sort', SmallInteger, nullable=False),
    Column('CMSC_Name', String(50, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CMSC_Parent', UNIQUEIDENTIFIER),
    Column('CMSC_Page', SmallInteger)
)

t_tv_CMSY = Table(
    'tv_CMSY', metadata,
    Column('cmsy_id', UNIQUEIDENTIFIER, nullable=False),
    Column('cmsy_name', String(50, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('cmsy_value', String(254, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('sto_pk', SmallInteger)
)

t_tv_CMTA = Table(
    'tv_CMTA', metadata,
    Column('cmta_id', UNIQUEIDENTIFIER, nullable=False),
    Column('cmtr_id', UNIQUEIDENTIFIER, nullable=False),
    Column('cmrh_id', UNIQUEIDENTIFIER, nullable=False),
    Column('cmck_id', UNIQUEIDENTIFIER, nullable=False),
    Column('sto_pk', SmallInteger, nullable=False),
    Column('cmta_ticketnumber', Integer, nullable=False),
    Column('cmta_numberofday', SmallInteger, nullable=False),
    Column('cmta_datein', DateTime, nullable=False),
    Column('cmta_dateout', DateTime, nullable=False),
    Column('cmta_amount', MONEY, nullable=False),
    Column('cmta_paidtodate', DateTime, nullable=False),
    Column('cmta_floatamount', MONEY, nullable=False),
    Column('cmta_additionalcharge', MONEY, nullable=False),
    Column('cmta_additionalfee', MONEY, nullable=False),
    Column('cmta_monthlycharge', BIT, nullable=False),
    Column('cmta_reminder', DateTime),
    Column('cmvt_id', UNIQUEIDENTIFIER),
    Column('CMLT_ID', UNIQUEIDENTIFIER),
    Column('cmclvt_id', UNIQUEIDENTIFIER),
    Column('CUS_ID', UNIQUEIDENTIFIER, nullable=False)
)

t_tv_CMTC = Table(
    'tv_CMTC', metadata,
    Column('cmtc_id', UNIQUEIDENTIFIER, nullable=False),
    Column('cmtr_id', UNIQUEIDENTIFIER, nullable=False),
    Column('cmck_id', UNIQUEIDENTIFIER, nullable=False),
    Column('sto_pk', SmallInteger),
    Column('cmtc_fee', MONEY),
    Column('cmtc_calcfee', MONEY),
    Column('cmrh_id', UNIQUEIDENTIFIER),
    Column('cmcaa_agentcus_id', UNIQUEIDENTIFIER),
    Column('cus_id', UNIQUEIDENTIFIER, nullable=False)
)

t_tv_CMTH = Table(
    'tv_CMTH', metadata,
    Column('CMTH_ID', UNIQUEIDENTIFIER, nullable=False),
    Column('CMTR_ID', UNIQUEIDENTIFIER, nullable=False),
    Column('Sto_PK', SmallInteger, nullable=False),
    Column('Usr_ID', UNIQUEIDENTIFIER, nullable=False),
    Column('CMCD_ID', UNIQUEIDENTIFIER),
    Column('CMLC_ID', UNIQUEIDENTIFIER),
    Column('CMTH_Date', DateTime, nullable=False),
    Column('CMTH_Amount', MONEY, nullable=False),
    Column('CMTH_Type', CHAR(10, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CMTH_Profit_Usr_id', UNIQUEIDENTIFIER, nullable=False),
    Column('CMTH_OverRideAmount', MONEY, nullable=False),
    Column('cmth_salestax', Numeric(8, 2)),
    Column('cus_id', UNIQUEIDENTIFIER, nullable=False)
)

t_tv_CMTHA = Table(
    'tv_CMTHA', metadata,
    Column('cmtha_id', UNIQUEIDENTIFIER, nullable=False),
    Column('cmth_id', UNIQUEIDENTIFIER, nullable=False),
    Column('sto_pk', SmallInteger, nullable=False),
    Column('cmrh_id', UNIQUEIDENTIFIER, nullable=False),
    Column('cmck_id', UNIQUEIDENTIFIER, nullable=False),
    Column('cmtha_ticketnumber', Integer, nullable=False),
    Column('cmtha_numberofday', Integer, nullable=False),
    Column('cmtha_datein', DateTime, nullable=False),
    Column('cmtha_dateout', DateTime, nullable=False),
    Column('cmtha_amount', MONEY, nullable=False),
    Column('cmtha_paidtodate', DateTime, nullable=False),
    Column('cmtha_floatamount', MONEY, nullable=False),
    Column('cmtha_additionalcharge', MONEY, nullable=False),
    Column('cmtha_additionalfee', MONEY, nullable=False),
    Column('cmtha_monthlycharge', BIT, nullable=False),
    Column('cmtha_reminder', DateTime),
    Column('cmvt_id', UNIQUEIDENTIFIER),
    Column('CMLT_ID', UNIQUEIDENTIFIER),
    Column('cmclvt_id', UNIQUEIDENTIFIER),
    Column('cus_id', UNIQUEIDENTIFIER, nullable=False)
)

t_tv_CMTHC = Table(
    'tv_CMTHC', metadata,
    Column('cmthc_id', UNIQUEIDENTIFIER, nullable=False),
    Column('cmth_id', UNIQUEIDENTIFIER, nullable=False),
    Column('sto_pk', SmallInteger, nullable=False),
    Column('cmthc_newvalue', String(50, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('cmthc_priorvalue', String(50, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
)

t_tv_CMTHM = Table(
    'tv_CMTHM', metadata,
    Column('cmthm_id', UNIQUEIDENTIFIER, nullable=False),
    Column('cmth_id', UNIQUEIDENTIFIER, nullable=False),
    Column('sto_pk', SmallInteger, nullable=False),
    Column('cmtm_id', UNIQUEIDENTIFIER, nullable=False)
)

t_tv_CMTM = Table(
    'tv_CMTM', metadata,
    Column('cmtm_id', UNIQUEIDENTIFIER, nullable=False),
    Column('cmtr_id', UNIQUEIDENTIFIER, nullable=False),
    Column('sto_pk', SmallInteger, nullable=False),
    Column('cmrh_id', UNIQUEIDENTIFIER, nullable=False),
    Column('cmtm_name', String(50, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('cmtm_amount', MONEY, nullable=False),
    Column('cmtm_calcfee', MONEY, nullable=False),
    Column('cmtm_fee', MONEY, nullable=False),
    Column('cmtm_cost', MONEY, nullable=False),
    Column('cmtm_serialno', String(50, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('cmtm_mgprinted', Integer)
)

t_tv_CMTN = Table(
    'tv_CMTN', metadata,
    Column('CMTN_ID', UNIQUEIDENTIFIER, nullable=False),
    Column('CMTR_ID', UNIQUEIDENTIFIER),
    Column('CMTH_ID', UNIQUEIDENTIFIER),
    Column('Sto_PK', SmallInteger, nullable=False),
    Column('Usr_ID', UNIQUEIDENTIFIER, nullable=False),
    Column('cus_id', UNIQUEIDENTIFIER, nullable=False),
    Column('cmtn_type', String(50, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('cmtn_date', DateTime, nullable=False),
    Column('cmtn_note', String(250, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
)

t_tv_CMTR = Table(
    'tv_CMTR', metadata,
    Column('cmtr_id', UNIQUEIDENTIFIER, nullable=False),
    Column('cus_id', UNIQUEIDENTIFIER, nullable=False),
    Column('usr_ID', UNIQUEIDENTIFIER, nullable=False),
    Column('sto_pk', SmallInteger, nullable=False),
    Column('cmtr_Type', CHAR(10, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('cmtr_date', DateTime, nullable=False),
    Column('cmtr_status', CHAR(2, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('cmlc_id', UNIQUEIDENTIFIER)
)

t_tv_CMTSL = Table(
    'tv_CMTSL', metadata,
    Column('CMTSL_id', UNIQUEIDENTIFIER, nullable=False),
    Column('CMTR_id', UNIQUEIDENTIFIER, nullable=False),
    Column('CMRH_id', UNIQUEIDENTIFIER, nullable=False),
    Column('sto_pk', SmallInteger, nullable=False),
    Column('CMTSL_ticketnumber', Integer, nullable=False),
    Column('CMTSL_DateIn', DateTime, nullable=False),
    Column('CMTSL_MaturityDate', DateTime, nullable=False),
    Column('CMTSL_LoanAmount', MONEY, nullable=False),
    Column('CMTSL_ServiceAPR', MONEY, nullable=False),
    Column('CMTSL_InterestAPR', MONEY, nullable=False),
    Column('CMTSL_OneTimeFee', MONEY, nullable=False),
    Column('CMTSL_PeriodFee', MONEY, nullable=False),
    Column('CMTSL_AdminPrepaid', MONEY, nullable=False),
    Column('CMTSL_OrigPrepaid', MONEY, nullable=False),
    Column('CMTSL_MiscPrepaid', MONEY, nullable=False),
    Column('CMTSL_OriginalPrincipal', MONEY, nullable=False),
    Column('CMTSL_Duration', SmallInteger, nullable=False),
    Column('CMTSL_PaymentFreq', String(1, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CMTSL_FPIAmount', MONEY, nullable=False),
    Column('CMTSL_PIAmount', MONEY, nullable=False),
    Column('CMTSL_FirstPayment', DateTime, nullable=False),
    Column('CMTSL_DOM1', TINYINT, nullable=False),
    Column('CMTSL_DOM2', TINYINT, nullable=False),
    Column('CMTSL_Note', String(254, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('cus_id', UNIQUEIDENTIFIER, nullable=False)
)

t_tv_CMVR = Table(
    'tv_CMVR', metadata,
    Column('cmvr_id', UNIQUEIDENTIFIER, nullable=False),
    Column('cmtr_id', UNIQUEIDENTIFIER),
    Column('sto_pk', SmallInteger, nullable=False),
    Column('usr_id', UNIQUEIDENTIFIER, nullable=False),
    Column('cmvr_date', DateTime, nullable=False),
    Column('cmvr_actioncode', String(20, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('cmvr_responsecode', String(20, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('cmvr_responseother', String(20, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('cmvr_responsedescription', String(250, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('cus_id', UNIQUEIDENTIFIER, nullable=False)
)

t_tv_CMVT = Table(
    'tv_CMVT', metadata,
    Column('CMVT_ID', UNIQUEIDENTIFIER, nullable=False),
    Column('cus_id', UNIQUEIDENTIFIER, nullable=False),
    Column('cmvt_vrnumber', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('sto_pk', SmallInteger, nullable=False),
    Column('cmvt_rtcharges', MONEY, nullable=False),
    Column('cmvt_rtfees', MONEY, nullable=False),
    Column('cmvt_fee1', MONEY, nullable=False),
    Column('cmvt_fee2', MONEY, nullable=False),
    Column('cmvt_status', CHAR(2, 'SQL_Latin1_General_CP1_CI_AS'))
)

t_tv_CUS = Table(
    'tv_CUS', metadata,
    Column('Cus_Store', Integer, nullable=False),
    Column('Cus_PK', Integer, nullable=False),
    Column('CUS_FNAME', String(15, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_MNAME', String(15, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_LNAME', String(25, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_ADD1', String(25, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_ADD2', String(25, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_CITY', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_STATE', String(2, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_ZIP', String(10, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_COUNTRY', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_AC1', String(3, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_PHONE1', String(8, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_HEIGHT', String(6, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_WEIGHT', SmallInteger, nullable=False),
    Column('CUS_HAIRFK', Integer, nullable=False),
    Column('CUS_EYESFK', Integer, nullable=False),
    Column('CUS_RACEFK', Integer, nullable=False),
    Column('CUS_SEX', String(1, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_MARKS', String(40, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_BIRTHDate', SMALLDATETIME),
    Column('CUS_BIRTHCITY', String(15, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_BIRTHSTATE', String(2, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_BIRTH2', String(15, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_IDTYP1', Integer, nullable=False),
    Column('CUS_IDNUM1', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_ID1EXP', SMALLDATETIME),
    Column('CUS_ID1ISSUE', String(50, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_IDTYP2', Integer, nullable=False),
    Column('CUS_IDNUM2', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_ID2EXP', SMALLDATETIME),
    Column('CUS_ID2ISSUE', String(2, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_KNOWN', BIT, nullable=False),
    Column('CUS_SSNUM', String(11, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_VEHIC1', String(10, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_VEHIC2', String(8, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_VEHIC3', String(2, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_EMPLOYER', String(40, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_EMPAD1', String(35, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_EMPAD2', String(35, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_EMPCITY', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_EMPSTATE', String(2, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_EMPZIP', String(10, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_AC2', String(3, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_EMPPHONE', String(14, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_COMMENT', String(200, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_TOTALPAWNS', Integer, nullable=False),
    Column('CUS_ACTIVEPAWN', Integer, nullable=False),
    Column('CUS_REDEEMED', Integer, nullable=False),
    Column('CUS_BUYS', Integer, nullable=False),
    Column('CUS_SALES', MONEY, nullable=False),
    Column('CUS_AMT1', MONEY, nullable=False),
    Column('CUS_AMT2', MONEY, nullable=False),
    Column('CUS_FFLNUM', String(25, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_DELETE', BIT, nullable=False),
    Column('CUS_LOCKED', BIT, nullable=False),
    Column('CUS_PAWNER', BIT, nullable=False),
    Column('CUS_BUYER', BIT, nullable=False),
    Column('CUS_IDADD1', String(25, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_IDADD2', String(25, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_IDCITY', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_IDSTATE', String(2, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_IDZIP', String(10, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('CUS_CREDIT', MONEY, nullable=False),
    Column('CUS_SPECIAL', Integer, nullable=False),
    Column('CUS_PIC_FK', Integer, nullable=False),
    Column('cus_Thum_fk', Integer, nullable=False),
    Column('CUS_Action_Spec', CHAR(1, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('Cus_id', UNIQUEIDENTIFIER),
    Column('Cus_PatriotAct', BIT),
    Column('Cus_PointsPawnBuy', Integer, nullable=False),
    Column('Cus_PointsSale', Integer, nullable=False),
    Column('Cus_PointsAvail', Integer, nullable=False),
    Column('Cus_PointsMailer', BIT, nullable=False),
    Column('Cus_TaxID', String(25, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('Cus_CellPhone', String(20, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('Cus_Email', String(254, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('Cus_Entered', DateTime),
    Column('Usr_ID', UNIQUEIDENTIFIER)
)

t_tv_DPCU = Table(
    'tv_DPCU', metadata,
    Column('DPCU_ID', UNIQUEIDENTIFIER, nullable=False),
    Column('Cus_ID', UNIQUEIDENTIFIER, nullable=False),
    Column('DPCU_Template', LargeBinary)
)

t_tv_DPUS = Table(
    'tv_DPUS', metadata,
    Column('DPUS_ID', UNIQUEIDENTIFIER, nullable=False),
    Column('Usr_ID', UNIQUEIDENTIFIER, nullable=False),
    Column('DPUS_Template', LargeBinary)
)

t_tv_ERR = Table(
    'tv_ERR', metadata,
    Column('Err_PK', Integer, nullable=False),
    Column('errdate', DateTime, nullable=False),
    Column('Descrip', String(500, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('userlanid', CHAR(10, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('err_store', SmallInteger),
    Column('program', String(50, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('errorno', String(50, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('linenumber', String(50, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('callstack', String(500, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('source', String(255, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('page3var', String(50, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('version', String(50, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('ERR_id', UNIQUEIDENTIFIER)
)

t_tv_GLA = Table(
    'tv_GLA', metadata,
    Column('GLA_ID', UNIQUEIDENTIFIER, nullable=False),
    Column('GLA_NO', Integer, nullable=False),
    Column('GLA_Account', String(255, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('GLT_ID', UNIQUEIDENTIFIER),
    Column('Level_ID', UNIQUEIDENTIFIER),
    Column('gla_Export_AcctType', String(100, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('sto_pk', SmallInteger)
)

t_tv_GLD = Table(
    'tv_GLD', metadata,
    Column('GLD_ID', UNIQUEIDENTIFIER, nullable=False),
    Column('GLD_No', Integer, nullable=False),
    Column('GLH_ID', UNIQUEIDENTIFIER, nullable=False),
    Column('GLT_ID', UNIQUEIDENTIFIER, nullable=False),
    Column('GLD_Acct_Posted', String(200, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('GLD_Amt', MONEY, nullable=False),
    Column('lv1_ID', UNIQUEIDENTIFIER),
    Column('lv2_ID', UNIQUEIDENTIFIER),
    Column('lv3_ID', UNIQUEIDENTIFIER),
    Column('lv4_ID', UNIQUEIDENTIFIER),
    Column('gld_OrigAmt', MONEY),
    Column('gld_ModDate', DateTime),
    Column('gld_ModType', CHAR(1, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('USR_ID', UNIQUEIDENTIFIER)
)

t_tv_GLH = Table(
    'tv_GLH', metadata,
    Column('GLH_ID', UNIQUEIDENTIFIER, nullable=False),
    Column('GLH_No', Integer, nullable=False),
    Column('STO_PK', SmallInteger, nullable=False),
    Column('BAT_ID', UNIQUEIDENTIFIER),
    Column('GLH_Date', DateTime, nullable=False),
    Column('GLH_Reference', String(200, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('GLH_Product', CHAR(2, 'SQL_Latin1_General_CP1_CI_AS'))
)

t_tv_GLT = Table(
    'tv_GLT', metadata,
    Column('GLT_ID', UNIQUEIDENTIFIER, nullable=False),
    Column('GLT_No', Integer, nullable=False),
    Column('GLT_Type', CHAR(10, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('GLT_Prompt', String(200, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('GLT_Status', BIT, nullable=False),
    Column('GLT_AcctType', CHAR(1, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('glt_group', CHAR(2, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('GLT_SortOrder', Integer),
    Column('glt_cash_sto_pk', SmallInteger),
    Column('glt_product', CHAR(2, 'SQL_Latin1_General_CP1_CI_AS'))
)

t_tv_INV = Table(
    'tv_INV', metadata,
    Column('Inv_PK', Integer, nullable=False),
    Column('Sto_PK', SmallInteger, nullable=False),
    Column('INVNUM', String(14, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('DATEin', DateTime),
    Column('QUANTITY', Numeric(9, 2), nullable=False),
    Column('SCRAPNUM', String(14, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('STATUS', String(1, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('COST', MONEY, nullable=False),
    Column('USR_fk', Integer, nullable=False),
    Column('OrigQty', Numeric(9, 2), nullable=False),
    Column('OrigCost', MONEY, nullable=False),
    Column('INV_id', UNIQUEIDENTIFIER)
)

t_tv_LB = Table(
    'tv_LB', metadata,
    Column('lb_pk', Integer, nullable=False),
    Column('lb_descript', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('lb_type', CHAR(1, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('LUB_id', UNIQUEIDENTIFIER)
)

t_tv_LC = Table(
    'tv_LC', metadata,
    Column('Sto_PK', SmallInteger, nullable=False),
    Column('lc_pk', Integer, nullable=False),
    Column('lc_Descript', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('LB_FK', Integer, nullable=False),
    Column('LUC_id', UNIQUEIDENTIFIER)
)

t_tv_MNL = Table(
    'tv_MNL', metadata,
    Column('sto_PK', Integer, nullable=False),
    Column('mnu_FK', Integer, nullable=False),
    Column('mnu_AccessLvl', Integer, nullable=False),
    Column('MNL_id', UNIQUEIDENTIFIER)
)

t_tv_MNU = Table(
    'tv_MNU', metadata,
    Column('mnu_PK', Integer, nullable=False),
    Column('mnu_Parent', Integer, nullable=False),
    Column('mnu_Pad', Integer, nullable=False),
    Column('mnu_Level', Integer, nullable=False),
    Column('mnu_Bar', Integer, nullable=False),
    Column('mnu_Descript', String(40, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('mnu_AllowChange', BIT, nullable=False),
    Column('mnu_EditVisible', BIT, nullable=False),
    Column('MNU_id', UNIQUEIDENTIFIER)
)

t_tv_SYCL = Table(
    'tv_SYCL', metadata,
    Column('sycl_id', UNIQUEIDENTIFIER, nullable=False),
    Column('sycl_table', String(50, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('sycl_column', String(50, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('sycl_prompt', String(100, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
)

t_tv_USR = Table(
    'tv_USR', metadata,
    Column('USR_PK', Integer, nullable=False),
    Column('USR_STORE', SmallInteger, nullable=False),
    Column('USR_LANID', String(8, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('USR_PASSWORD', String(8, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('USR_MENUACCESS', SmallInteger, nullable=False),
    Column('USR_RWACCESS', SmallInteger, nullable=False),
    Column('USR_ACTIVE', BIT, nullable=False),
    Column('USR_LASTLOGIN', DateTime),
    Column('USR_FNAME', String(15, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('USR_MNAME', String(15, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('USR_LNAME', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('USR_ADD1', String(35, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('USR_ADD2', String(35, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('USR_CITY', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('USR_STATE', String(3, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('USR_ZIP', String(11, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('USR_AC1', String(4, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('USR_PHONE1', String(9, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('USR_PHONEEXT', String(4, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('USR_AC2', String(4, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('USR_PHONE2', String(9, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('USR_ENABLEPREFS', String(1, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('USR_STARTDATE', DateTime),
    Column('USR_TERMINATE', DateTime),
    Column('USR_BIRTHDATE', DateTime),
    Column('CASHDRDATE', DateTime),
    Column('CASHDRSTAT', String(1, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('USR_KLOKIN', DateTime),
    Column('USR_SSNUM', String(12, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('USR_ID', UNIQUEIDENTIFIER, nullable=False),
    Column('PawnLimit', MONEY, nullable=False),
    Column('BuyLimit', MONEY, nullable=False),
    Column('OptionLimit', MONEY, nullable=False),
    Column('Usr_Clock', BIT, nullable=False),
    Column('LastUpdatedUSR_ID', UNIQUEIDENTIFIER),
    Column('USR_NOTES', Unicode(3000))
)

t_users = Table(
    'users', metadata,
    Column('USR_PK', Integer, nullable=False, server_default=text("(1)")),
    Column('USR_STORE', SmallInteger, nullable=False, server_default=text("(1)")),
    Column('USR_LANID', String(8, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("('   ')")),
    Column('USR_PASSWORD', String(8, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False,
           server_default=text("('#u*,2,1%')")),
    Column('USR_MENUACCESS', SmallInteger, nullable=False, server_default=text("(6)")),
    Column('USR_RWACCESS', SmallInteger, nullable=False, server_default=text("(6)")),
    Column('USR_ACTIVE', BIT, nullable=False, server_default=text("(0)")),
    Column('USR_LASTLOGIN', DateTime),
    Column('USR_FNAME', String(15, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("(' ')")),
    Column('USR_MNAME', String(15, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("(' ')")),
    Column('USR_LNAME', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("(' ')")),
    Column('USR_ADD1', String(35, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("(' ')")),
    Column('USR_ADD2', String(35, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("(' ')")),
    Column('USR_CITY', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("(' ')")),
    Column('USR_STATE', String(3, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("(' ')")),
    Column('USR_ZIP', String(11, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("(' ')")),
    Column('USR_AC1', String(4, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("(' ')")),
    Column('USR_PHONE1', String(9, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("(' ')")),
    Column('USR_PHONEEXT', String(4, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("(' ')")),
    Column('USR_AC2', String(4, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("(' ')")),
    Column('USR_PHONE2', String(9, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("(' ')")),
    Column('USR_ENABLEPREFS', String(1, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("(' ')")),
    Column('USR_STARTDATE', DateTime),
    Column('USR_TERMINATE', DateTime),
    Column('USR_BIRTHDATE', DateTime),
    Column('CASHDRDATE', DateTime),
    Column('CASHDRSTAT', String(1, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("(' ')")),
    Column('USR_KLOKIN', DateTime),
    Column('USR_SSNUM', String(12, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("(' ')")),
    Column('USR_ID', UNIQUEIDENTIFIER, nullable=False, unique=True, server_default=text("(newid())")),
    Column('PawnLimit', MONEY, nullable=False, server_default=text("(999999.99)")),
    Column('BuyLimit', MONEY, nullable=False, server_default=text("(999999.99)")),
    Column('OptionLimit', MONEY, nullable=False, server_default=text("(999999.99)")),
    Column('Usr_Clock', BIT, nullable=False, server_default=text("(1)")),
    Column('LastUpdatedUSR_ID', UNIQUEIDENTIFIER),
    Column('USR_NOTES', Unicode(3000)),
    Column('USR_DISCOUNT', DECIMAL(5, 2), nullable=False, server_default=text("(100.00)")),
    Index('IDX_users_Usr_store_usr_pk', 'USR_PK', 'USR_STORE'),
    Index('IDX_users_USR_LANID_USR_PASSWORD_USR_STORE', 'USR_LANID', 'USR_PASSWORD', 'USR_STORE'),
    Index('IDX_users_Usr_Store_LanID', 'USR_STORE', 'USR_LANID')
)


class Vend(Base):
    __tablename__ = 'vend'

    VEN_STORE = Column(SmallInteger, nullable=False, server_default=text("(1)"))
    VEN_PK = Column(Integer, primary_key=True, server_default=text("(0)"))
    VEN_COMPANY = Column(String(35, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, index=True,
                         server_default=text("(' ')"))
    VEN_ADD1 = Column(String(25, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("(' ')"))
    VEN_ADD2 = Column(String(25, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("(' ')"))
    VEN_CITY = Column(String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("(' ')"))
    VEN_STATE = Column(String(3, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("(' ')"))
    VEN_ZIP = Column(String(10, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("(' ')"))
    VEN_CONTACT = Column(String(25, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("(' ')"))
    VEN_AC1 = Column(String(3, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("(' ')"))
    VEN_PHONE = Column(String(8, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("(' ')"))
    VEN_COMMENT1 = Column(String(60, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("(' ')"))
    VEN_COMMENT2 = Column(String(60, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("(' ')"))
    VEN_FFLNUM = Column(String(25, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, index=True,
                        server_default=text("(' ')"))
    VEN_STATUS = Column(String(1, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("(' ')"))
    VEN_DELETE = Column(BIT, nullable=False, server_default=text("(0)"))
    VEN_AC2 = Column(String(3, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("(' ')"))
    VEN_FAX = Column(String(8, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("(' ')"))
    VEN_ACTIVE = Column(BIT, nullable=False, server_default=text("(0)"))
    Sells_FireArms = Column(BIT, nullable=False, server_default=text("(0)"))
    ConsignDate = Column(DateTime)
    VEN_id = Column(UNIQUEIDENTIFIER, unique=True, server_default=text("(newid())"))
    LastUpdatedUSR_ID = Column(UNIQUEIDENTIFIER)
    Comments = Column(Unicode(3000))
    VEN_FFLEXPIREDATE = Column(DateTime)


t_vt_CMVR = Table(
    'vt_CMVR', metadata,
    Column('cmvr_id', UNIQUEIDENTIFIER, nullable=False),
    Column('cmtr_id', UNIQUEIDENTIFIER),
    Column('sto_pk', SmallInteger, nullable=False),
    Column('usr_id', UNIQUEIDENTIFIER, nullable=False),
    Column('cmvr_date', DateTime, nullable=False),
    Column('cmvr_actioncode', String(20, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('cmvr_responsecode', String(20, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('cmvr_responseother', String(20, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('cmvr_responsedescription', String(250, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('cus_id', UNIQUEIDENTIFIER, nullable=False)
)

t_vwLayCost = Table(
    'vwLayCost', metadata,
    Column('NUMBERSOLD', Numeric(9, 2), nullable=False),
    Column('COST', MONEY, nullable=False),
    Column('Sto_PK', SmallInteger, nullable=False),
    Column('Items_pk', Integer, nullable=False)
)

t_vwLaysCR = Table(
    'vwLaysCR', metadata,
    Column('datein', DateTime),
    Column('SaleAmt', MONEY, nullable=False),
    Column('Tax', MONEY, nullable=False),
    Column('Deposit', MONEY, nullable=False),
    Column('Trans', CHAR(1, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('Status', CHAR(1, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('Srvchgamt', MONEY, nullable=False),
    Column('Sto_PK', SmallInteger, nullable=False),
    Column('Type', CHAR(3, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
)

t_zipcity = Table(
    'zipcity', metadata,
    Column('ZIP_PK', Integer, nullable=False),
    Column('ZIP_CITY', String(20, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('ZIP_STATE', String(2, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('ZIP_CODE', String(10, 'SQL_Latin1_General_CP1_CI_AS'), index=True),
    Column('ZIP_STORE', SmallInteger, server_default=text("(1)")),
    Column('ZIP_id', UNIQUEIDENTIFIER, unique=True, server_default=text("(newid())")),
    Column('LastUpdatedUSR_ID', UNIQUEIDENTIFIER),
    Index('IDX_zipcity_Zip_City_State', 'ZIP_CITY', 'ZIP_STATE')
)


class CMABDACHBatchDetail(Base):
    __tablename__ = 'CMABD_ACHBatchDetail'

    cmabd_id = Column(UNIQUEIDENTIFIER, primary_key=True, server_default=text("(newid())"))
    cmabh_id = Column(ForeignKey('CMABH_ACHBatchHeader.cmabh_id'), nullable=False)
    sto_pk = Column(SmallInteger, nullable=False)
    cmck_id = Column(UNIQUEIDENTIFIER, nullable=False)
    cmabd_status = Column(CHAR(1, 'SQL_Latin1_General_CP1_CI_AS'))
    cmabd_indivno = Column(String(15, 'SQL_Latin1_General_CP1_CI_AS'))
    cmabd_resubamt = Column(MONEY)

    cmabh = relationship('CMABHACHBatchHeader')


class CMABRACHBatchResponse(Base):
    __tablename__ = 'CMABR_ACHBatchResponse'

    cmabr_id = Column(UNIQUEIDENTIFIER, primary_key=True, server_default=text("(newid())"))
    cmabh_id = Column(ForeignKey('CMABH_ACHBatchHeader.cmabh_id'), nullable=False)
    usr_id = Column(UNIQUEIDENTIFIER, nullable=False)
    cmabr_senddate = Column(DateTime, nullable=False)
    cmabr_response = Column(String(100, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)

    cmabh = relationship('CMABHACHBatchHeader')


class CMARAccountsReceivable(Base):
    __tablename__ = 'CMAR_AccountsReceivable'

    CMAR_ID = Column(UNIQUEIDENTIFIER, primary_key=True, server_default=text("(newid())"))
    CMTR_ID = Column(ForeignKey('CMTR_Transaction.cmtr_id'), nullable=False, index=True)
    CMAR_CMTH_ID = Column(UNIQUEIDENTIFIER)
    CMCK_ID = Column(UNIQUEIDENTIFIER, index=True)
    CMAR_TYPE = Column(CHAR(2, 'SQL_Latin1_General_CP1_CI_AS'), index=True)
    CMAR_ASSIGNEMP_ID = Column(UNIQUEIDENTIFIER, server_default=text("(null)"))

    CMTR_Transaction = relationship('CMTRTransaction')


class CMBDPHBatchDishonorPayHead(Base):
    __tablename__ = 'CMBDPH_BatchDishonorPayHead'

    cmbdph_id = Column(UNIQUEIDENTIFIER, primary_key=True, server_default=text("(newid())"))
    cmbdph_no = Column(Integer, nullable=False)
    sto_pk = Column(SmallInteger, nullable=False)
    cmbdph_date = Column(DateTime, nullable=False)
    usr_id = Column(UNIQUEIDENTIFIER, nullable=False, index=True)
    cmpy_id = Column(ForeignKey('CMPY_Payor.cmpy_id'), nullable=False, index=True)

    cmpy = relationship('CMPYPayor')


class CMBDBatchDetail(Base):
    __tablename__ = 'CMBD_BatchDetail'
    __table_args__ = (
        Index('IDX_CMBD_BatchDetail_8_958274819_K2_K4_K5', 'cmbh_id', 'cmth_id', 'cmck_id'),
    )

    cmbd_id = Column(UNIQUEIDENTIFIER, primary_key=True, server_default=text("(newid())"))
    cmbh_id = Column(ForeignKey('CMBH_BatchHeader.cmbh_id'), nullable=False, index=True)
    sto_pk = Column(SmallInteger, nullable=False)
    cmth_id = Column(UNIQUEIDENTIFIER, nullable=False, index=True)
    cmck_id = Column(UNIQUEIDENTIFIER, index=True)
    cmcd_id = Column(UNIQUEIDENTIFIER, index=True)

    cmbh = relationship('CMBHBatchHeader')


class CMCACheckAccount(Base):
    __tablename__ = 'CMCA_CheckAccount'
    __table_args__ = (
        Index('IX_CMCA_CheckAccount_cmpy_id', 'cmca_ID', 'cmpy_id'),
    )

    cmca_ID = Column(UNIQUEIDENTIFIER, primary_key=True, server_default=text("(newid())"))
    cmbk_id = Column(ForeignKey('CMBK_Bank.cmbk_id'), nullable=False, index=True)
    sto_pk = Column(SmallInteger, nullable=False)
    cmca_Account = Column(String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    cmpy_id = Column(ForeignKey('CMPY_Payor.cmpy_id'), nullable=False)
    cmca_account_type = Column(CHAR(1, 'SQL_Latin1_General_CP1_CI_AS'), server_default=text("('C')"))

    cmbk = relationship('CMBKBank')
    cmpy = relationship('CMPYPayor')


class CMCBBCashBoxBalance(Base):
    __tablename__ = 'CMCBB_CashBoxBalance'
    __table_args__ = (
        Index('IX_CMCBB_cmcbs_status', 'CMCBS_ID', 'CMCBB_Status', 'CMCBCH_ID', 'CMCBB_ID'),
        Index('IDX_CMCBB_CashBoxBalance_K4_K2_K3', 'CMCBB_Date', 'CMCBS_ID', 'CMCBCH_ID'),
        Index('IDX_CMCBB_CashBoxBalance_K2_K4_K1_K3', 'CMCBS_ID', 'CMCBB_Date', 'CMCBB_ID', 'CMCBCH_ID')
    )

    CMCBB_ID = Column(UNIQUEIDENTIFIER, primary_key=True, server_default=text("(newid())"))
    CMCBS_ID = Column(ForeignKey('CMCBS_CashBoxSlot.CMCBS_ID'), nullable=False, index=True)
    CMCBCH_ID = Column(ForeignKey('CMCBCH_CashBoxCountHeader.CMCBCH_ID'), nullable=False, index=True)
    CMCBB_Date = Column(DateTime, nullable=False)
    CMCBB_Status = Column(CHAR(2, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    USR_ID = Column(UNIQUEIDENTIFIER, nullable=False)
    CMST_ID = Column(UNIQUEIDENTIFIER)
    STO_PK = Column(SmallInteger, nullable=False)
    CMCBB_Manager_Usr_ID = Column(UNIQUEIDENTIFIER)

    CMCBCH_CashBoxCountHeader = relationship('CMCBCHCashBoxCountHeader')
    CMCBS_CashBoxSlot = relationship('CMCBSCashBoxSlot')


class CMCBCCCashBoxCountCheck(Base):
    __tablename__ = 'CMCBCC_CashBoxCountCheck'
    __table_args__ = (
        Index('IX_CMCBCC_cmck_cmcbch_active', 'CMCK_ID', 'CMCBCH_ID', 'CMCBCC_Active'),
        Index('IDX_CMCBCC_CashBoxCountCheck_K2_K1_K3', 'CMCBCH_ID', 'CMCBCC_ID', 'CMCK_ID')
    )

    CMCBCC_ID = Column(UNIQUEIDENTIFIER, primary_key=True, server_default=text("(newid())"))
    CMCBCH_ID = Column(ForeignKey('CMCBCH_CashBoxCountHeader.CMCBCH_ID'), nullable=False, index=True)
    CMCK_ID = Column(UNIQUEIDENTIFIER, nullable=False, index=True)
    CMCBBCD_ID = Column(UNIQUEIDENTIFIER)
    CMCBCC_Active = Column(BIT, nullable=False, server_default=text("(1)"))

    CMCBCH_CashBoxCountHeader = relationship('CMCBCHCashBoxCountHeader')


class CMCBCDCashBoxCountDetail(Base):
    __tablename__ = 'CMCBCD_CashBoxCountDetail'

    CMCBCD_ID = Column(UNIQUEIDENTIFIER, primary_key=True, server_default=text("(newid())"))
    CMCBCH_ID = Column(ForeignKey('CMCBCH_CashBoxCountHeader.CMCBCH_ID'), nullable=False)
    CMCBLU_ID = Column(ForeignKey('CMCBLU_CashBoxLookupUnit.CMCBLU_ID'), nullable=False)
    CMLC_ID = Column(UNIQUEIDENTIFIER, nullable=False)
    CMCBCD_Count = Column(MONEY, nullable=False)

    CMCBCH_CashBoxCountHeader = relationship('CMCBCHCashBoxCountHeader')
    CMCBLU_CashBoxLookupUnit = relationship('CMCBLUCashBoxLookupUnit')


class CMCBHCashBoxHeader(Base):
    __tablename__ = 'CMCBH_CashBoxHeader'

    CMCBH_ID = Column(UNIQUEIDENTIFIER, primary_key=True, index=True, server_default=text("(newid())"))
    CMCBH_Type = Column(CHAR(2, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    USR_ID = Column(UNIQUEIDENTIFIER, nullable=False)
    STO_PK = Column(SmallInteger, nullable=False)
    CMCBCH_ID = Column(ForeignKey('CMCBCH_CashBoxCountHeader.CMCBCH_ID'), nullable=False)
    CMST_ID = Column(UNIQUEIDENTIFIER)

    CMCBCH_CashBoxCountHeader = relationship('CMCBCHCashBoxCountHeader')


class CMCTCashType(Base):
    __tablename__ = 'CMCT_CashType'
    __table_args__ = (
        Index('IDX_CMCT_CashType_K2_K7_5', 'cmcd_id', 'CMLC_ID'),
        Index('IDX_CMCT_CashType_K7_K1_K2_5_6', 'CMLC_ID', 'cmct_id', 'cmcd_id'),
        Index('IX_CMCT_cmcd_order', 'cmcd_id', 'cmct_order'),
        Index('IDX_CMCT_CashType_K1_K7_K2_5_6', 'cmct_id', 'CMLC_ID', 'cmcd_id')
    )

    cmct_id = Column(UNIQUEIDENTIFIER, primary_key=True, server_default=text("(newid())"))
    cmcd_id = Column(ForeignKey('CMCD_CashDrawer.cmcd_id'), nullable=False)
    sto_pk = Column(SmallInteger, nullable=False)
    luc_id = Column(UNIQUEIDENTIFIER)
    cmct_amount = Column(MONEY, nullable=False)
    cmct_Change_Ind = Column(BIT, nullable=False, server_default=text("(0)"))
    CMLC_ID = Column(UNIQUEIDENTIFIER)
    cmct_order = Column(SmallInteger)

    cmcd = relationship('CMCDCashDrawer')


class CMDBGTDepositBankGLType(Base):
    __tablename__ = 'CMDBGT_DepositBankGLType'

    CMDBGT_ID = Column(UNIQUEIDENTIFIER, primary_key=True, server_default=text("(newid())"))
    CMDBA_ID = Column(ForeignKey('CMDBA_DepositBankAccount.CMDBA_ID'), nullable=False)
    GLT_ID = Column(ForeignKey('CMGLT_Type.GLT_ID'), nullable=False)
    STO_PK = Column(SmallInteger, nullable=False)
    CMDBGT_Type = Column(CHAR(1, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)

    CMDBA_DepositBankAccount = relationship('CMDBADepositBankAccount')
    CMGLT_Type = relationship('CMGLTType')


class CMDLCDebitLoadCard(Base):
    __tablename__ = 'CMDLC_DebitLoadCard'

    cmdlc_id = Column(UNIQUEIDENTIFIER, primary_key=True, server_default=text("(newid())"))
    cus_id = Column(UNIQUEIDENTIFIER, nullable=False)
    cmdlp_id = Column(ForeignKey('CMDLP_DebitLoadProduct.cmdlp_id'))
    sto_pk = Column(SmallInteger, nullable=False)
    cmdlc_cardno = Column(BINARY(50), nullable=False)

    cmdlp = relationship('CMDLPDebitLoadProduct')


class CMGLAAccount(Base):
    __tablename__ = 'CMGLA_Account'

    GLA_ID = Column(UNIQUEIDENTIFIER, primary_key=True, server_default=text("(newid())"))
    GLA_NO = Column(Integer, nullable=False)
    GLA_Account = Column(String(255, 'SQL_Latin1_General_CP1_CI_AS'), server_default=text("('')"))
    GLT_ID = Column(ForeignKey('CMGLT_Type.GLT_ID'))
    Level_ID = Column(UNIQUEIDENTIFIER)
    gla_Export_AcctType = Column(String(100, 'SQL_Latin1_General_CP1_CI_AS'))
    sto_pk = Column(SmallInteger, server_default=text("(1)"))

    CMGLT_Type = relationship('CMGLTType')


class CMGLDDetail(Base):
    __tablename__ = 'CMGLD_Detail'

    GLD_ID = Column(UNIQUEIDENTIFIER, primary_key=True, server_default=text("(newid())"))
    GLD_No = Column(Integer, nullable=False)
    GLH_ID = Column(ForeignKey('CMGLH_Header.GLH_ID'), nullable=False)
    GLT_ID = Column(UNIQUEIDENTIFIER, nullable=False)
    GLD_Acct_Posted = Column(String(200, 'SQL_Latin1_General_CP1_CI_AS'), server_default=text("(0)"))
    GLD_Amt = Column(MONEY, nullable=False, server_default=text("(0)"))
    lv1_ID = Column(UNIQUEIDENTIFIER)
    lv2_ID = Column(UNIQUEIDENTIFIER)
    lv3_ID = Column(UNIQUEIDENTIFIER)
    lv4_ID = Column(UNIQUEIDENTIFIER)
    gld_OrigAmt = Column(MONEY)
    gld_ModDate = Column(DateTime)
    gld_ModType = Column(CHAR(1, 'SQL_Latin1_General_CP1_CI_AS'))
    USR_ID = Column(UNIQUEIDENTIFIER)

    CMGLH_Header = relationship('CMGLHHeader')


class CMILDItemLotDamaged(Base):
    __tablename__ = 'CMILD_ItemLotDamaged'

    CMILD_ID = Column(UNIQUEIDENTIFIER, primary_key=True)
    STO_PK = Column(SmallInteger, nullable=False)
    USR_ID = Column(UNIQUEIDENTIFIER, nullable=False)
    CMTSDL_ID = Column(ForeignKey('CMTSDL_TransSaleDetailLot.CMTSDL_ID'), nullable=False, index=True)
    CMILD_Date = Column(DateTime, nullable=False)
    CMILDN_ID = Column(UNIQUEIDENTIFIER)

    CMTSDL_TransSaleDetailLot = relationship('CMTSDLTransSaleDetailLot')


class CMILHItemLotHeader(Base):
    __tablename__ = 'CMILH_ItemLotHeader'

    CMILH_ID = Column(UNIQUEIDENTIFIER, primary_key=True)
    CMVN_ID = Column(ForeignKey('CMVN_Vendor.CMVN_ID'), nullable=False)
    CMILH_ORDERNUMBER = Column(String(50, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    STO_PK = Column(SmallInteger, nullable=False)
    CMILH_Date = Column(DateTime, nullable=False, index=True)

    CMVN_Vendor = relationship('CMVNVendor')


class CMINIItemNonInventory(Base):
    __tablename__ = 'CMINI_ItemNonInventory'

    CMINI_ID = Column(UNIQUEIDENTIFIER, primary_key=True, server_default=text("(newid())"))
    CMIPH_ID = Column(ForeignKey('CMIPH_InvPackageHeader.CMIPH_ID'), nullable=False)
    CMINI_HD = Column(MONEY, nullable=False)
    CMINI_DP = Column(CHAR(1, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    CMINI_AP = Column(MONEY, nullable=False)
    CMINI_CostDP = Column(CHAR(1, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    CMINI_Cost = Column(MONEY, nullable=False)

    CMIPH_InvPackageHeader = relationship('CMIPHInvPackageHeader')


class CMIOHInvOrderHeader(Base):
    __tablename__ = 'CMIOH_InvOrderHeader'

    CMIOH_ID = Column(UNIQUEIDENTIFIER, primary_key=True)
    STO_PK = Column(SmallInteger, nullable=False)
    CMIOH_OrderNumber = Column(String(50, 'SQL_Latin1_General_CP1_CI_AS'))
    CMVN_ID = Column(ForeignKey('CMVN_Vendor.CMVN_ID'), nullable=False)
    CMIOH_Date = Column(DateTime, nullable=False)
    USR_ID = Column(UNIQUEIDENTIFIER, nullable=False)
    CMIOH_EstimatedShippingCost = Column(MONEY, nullable=False)
    CUS_ID = Column(UNIQUEIDENTIFIER)

    CMVN_Vendor = relationship('CMVNVendor')


class CMIPRInvPackageRate(Base):
    __tablename__ = 'CMIPR_InvPackageRate'

    CMIPR_ID = Column(UNIQUEIDENTIFIER, primary_key=True)
    CMIPH_ID = Column(ForeignKey('CMIPH_InvPackageHeader.CMIPH_ID'), nullable=False)
    STO_PK = Column(SmallInteger, nullable=False)
    CMIPR_Begindate = Column(DateTime, nullable=False)
    CMIPR_EndDate = Column(DateTime)
    CMIPR_Price = Column(MONEY, nullable=False)
    CMIPR_Active = Column(BIT, nullable=False)

    CMIPH_InvPackageHeader = relationship('CMIPHInvPackageHeader')


class CMIPUInvPackageUPC(Base):
    __tablename__ = 'CMIPU_InvPackageUPC'

    CMIPU_ID = Column(UNIQUEIDENTIFIER, primary_key=True)
    CMIPH_ID = Column(ForeignKey('CMIPH_InvPackageHeader.CMIPH_ID'), nullable=False, index=True)
    STO_PK = Column(SmallInteger, nullable=False)
    CMIPU_UPC = Column(String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, index=True)
    CMIPU_HotKey = Column(String(20, 'SQL_Latin1_General_CP1_CI_AS'))
    CMIPU_isUPC = Column(BIT, nullable=False)
    CMIPU_Default = Column(BIT, server_default=text("(0)"))
    CMIPU_Active = Column(BIT, server_default=text("(1)"))

    CMIPH_InvPackageHeader = relationship('CMIPHInvPackageHeader')


class CMITInvType(Base):
    __tablename__ = 'CMIT_InvType'

    CMIT_ID = Column(UNIQUEIDENTIFIER, primary_key=True)
    CMITS_ID = Column(ForeignKey('CMITS_InvTypeSetup.CMITS_ID'), nullable=False)
    CMIT_Description = Column(String(50, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    CMIT_CMIT_ID = Column(ForeignKey('CMIT_InvType.CMIT_ID'))
    CMIT_Active = Column(BIT, server_default=text("(1)"))
    cmit_MinAge = Column(Integer)
    cmitt_id = Column(UNIQUEIDENTIFIER)

    CMITS_InvTypeSetup = relationship('CMITSInvTypeSetup')
    parent = relationship('CMITInvType', remote_side=[CMIT_ID])


class CMMUMenuLevel(Base):
    __tablename__ = 'CMMU_MenuLevel'

    cmmu_id = Column(UNIQUEIDENTIFIER, primary_key=True, server_default=text("(newid())"))
    cmmi_id = Column(ForeignKey('CMMI_MenuItems.cmmi_id'), nullable=False)
    cmmu_accesslvl = Column(TINYINT, nullable=False)
    sto_pk = Column(SmallInteger, nullable=False)

    cmmi = relationship('CMMIMenuItem')


class CMMMessage(Base):
    __tablename__ = 'CMM_Message'
    __table_args__ = (
        Index('IX_CMM_Message_CMMA_ID_CMM_Lookup', 'CMM_ID', 'CMM_Lookup', unique=True),
    )

    CMM_ID = Column(UNIQUEIDENTIFIER, primary_key=True, server_default=text("(newid())"))
    CMMA_ID = Column(ForeignKey('CMMA_MessageArea.CMMA_ID'), nullable=False)
    CMM_Description = Column(String(500, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    CMM_Lookup = Column(String(50, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)

    CMMA_MessageArea = relationship('CMMAMessageArea')


class CMRARatesAdvance(Base):
    __tablename__ = 'CMRA_RatesAdvance'

    cmra_id = Column(UNIQUEIDENTIFIER, primary_key=True, server_default=text("(newid())"))
    cmrh_id = Column(ForeignKey('CMRH_RatesHeader.cmrh_id'), nullable=False, index=True)
    sto_pk = Column(SmallInteger, nullable=False)
    cmra_hd = Column(MONEY, nullable=False, server_default=text("(0.00)"))
    cmra_dp = Column(CHAR(1, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("('%')"))
    cmra_ap = Column(MONEY, nullable=False, server_default=text("(0.00)"))
    CMRA_FeeDP = Column(CHAR(1, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("('%')"))
    CMRA_Fee = Column(MONEY, nullable=False, server_default=text("(0.00)"))
    CMRA_Minimum = Column(MONEY, nullable=False, server_default=text("(0.00)"))
    CMRA_ISMonthPR = Column(BIT, nullable=False, server_default=text("(0)"))
    CMRA_NumDays = Column(SmallInteger, nullable=False, server_default=text("(0)"))

    cmrh = relationship('CMRHRatesHeader')


class CMRCRatesCheck(Base):
    __tablename__ = 'CMRC_RatesCheck'

    cmrc_id = Column(UNIQUEIDENTIFIER, primary_key=True, server_default=text("(newid())"))
    cmrh_id = Column(ForeignKey('CMRH_RatesHeader.cmrh_id'), nullable=False, index=True)
    sto_pk = Column(SmallInteger, nullable=False)
    cmrc_hd = Column(MONEY, nullable=False)
    cmrc_dp = Column(CHAR(1, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    cmrc_ap = Column(MONEY, nullable=False)
    cmrc_dp2 = Column(CHAR(1, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("('$')"))
    cmrc_ap2 = Column(MONEY, nullable=False, server_default=text("(0.00)"))

    cmrh = relationship('CMRHRatesHeader')


class CMRGTRatesGLType(Base):
    __tablename__ = 'CMRGT_RatesGLType'

    CMRGT_ID = Column(UNIQUEIDENTIFIER, primary_key=True, server_default=text("(newid())"))
    CMRH_ID = Column(ForeignKey('CMRH_RatesHeader.cmrh_id'), nullable=False)
    GLT_ID = Column(ForeignKey('CMGLT_Type.GLT_ID'), nullable=False)
    STO_PK = Column(SmallInteger, nullable=False)
    CMRGT_Type = Column(String(2, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)

    CMRH_RatesHeader = relationship('CMRHRatesHeader')
    CMGLT_Type = relationship('CMGLTType')


class CMRMRatesMoneyOrder(Base):
    __tablename__ = 'CMRM_RatesMoneyOrder'

    cmrm_id = Column(UNIQUEIDENTIFIER, primary_key=True, server_default=text("(newid())"))
    cmrh_id = Column(ForeignKey('CMRH_RatesHeader.cmrh_id'), nullable=False)
    sto_pk = Column(SmallInteger, nullable=False)
    cmrm_hd = Column(MONEY, nullable=False)
    cmrm_dp = Column(CHAR(1, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    cmrm_ap = Column(MONEY, nullable=False)
    cmrm_costdp = Column(CHAR(1, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("('$')"))
    cmrm_cost = Column(MONEY, nullable=False, server_default=text("(0)"))

    cmrh = relationship('CMRHRatesHeader')


class CMRQRequired(Base):
    __tablename__ = 'CMRQ_Required'

    cmrq_id = Column(UNIQUEIDENTIFIER, primary_key=True, unique=True, server_default=text("(newid())"))
    sto_pk = Column(Integer, nullable=False, server_default=text("(1)"))
    sycl_id = Column(ForeignKey('SYCL_SysColumns.sycl_id'), nullable=False, index=True,
                     server_default=text("(newid())"))
    cmrq_required = Column(BIT, nullable=False, server_default=text("(0)"))
    cmrq_sort = Column(Integer, nullable=False, server_default=text("(0)"))
    cmrq_locked = Column(BIT, nullable=False, server_default=text("(0)"))

    sycl = relationship('SYCLSysColumn')


class CMRSLRatesSigLoan(Base):
    __tablename__ = 'CMRSL_RatesSigLoan'

    CMRSL_id = Column(UNIQUEIDENTIFIER, primary_key=True, server_default=text("(newid())"))
    CMRH_id = Column(ForeignKey('CMRH_RatesHeader.cmrh_id'), nullable=False, index=True)
    sto_pk = Column(SmallInteger, nullable=False)
    CMRSL_hd = Column(MONEY, nullable=False)
    CMRSL_ServiceAPR = Column(MONEY, nullable=False)
    CMRSL_InterestAPR = Column(MONEY, nullable=False)
    CMRSL_OneTimeFee = Column(MONEY, nullable=False)
    CMRSL_dpotf = Column(String(1, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    CMRSL_PeriodFee = Column(MONEY, nullable=False)
    CMRSL_dppf = Column(String(1, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    CMRSL_AdminPrepaid = Column(MONEY, nullable=False)
    CMRSL_dpap = Column(String(1, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    CMRSL_OrigPrepaid = Column(MONEY, nullable=False)
    CMRSL_dpop = Column(String(1, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    CMRSL_MiscPrepaid = Column(MONEY, nullable=False)
    CMRSL_dpmp = Column(String(1, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)

    CMRH = relationship('CMRHRatesHeader')


class CMRSReportSecurity(Base):
    __tablename__ = 'CMRS_ReportSecurity'

    CMRS_ID = Column(UNIQUEIDENTIFIER, primary_key=True, unique=True, server_default=text("(newid())"))
    CMRL_ID = Column(ForeignKey('CMRL_Repolist.CMRL_ID'), nullable=False)
    Sto_pk = Column(Integer, nullable=False, server_default=text("(1)"))
    CMRS_MenuAccess = Column(SmallInteger, nullable=False, server_default=text("(6)"))
    CMRS_Comment = Column(Text(2147483647, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("('')"))

    CMRL_Repolist = relationship('CMRLRepolist')


class CMTATranAdvance(Base):
    __tablename__ = 'CMTA_TranAdvance'

    cmta_id = Column(UNIQUEIDENTIFIER, primary_key=True, server_default=text("(newid())"))
    cmtr_id = Column(ForeignKey('CMTR_Transaction.cmtr_id'), nullable=False, index=True)
    cmrh_id = Column(UNIQUEIDENTIFIER, nullable=False)
    cmck_id = Column(UNIQUEIDENTIFIER, nullable=False, index=True)
    sto_pk = Column(SmallInteger, nullable=False)
    cmta_ticketnumber = Column(Integer, nullable=False)
    cmta_numberofday = Column(SmallInteger, nullable=False)
    cmta_datein = Column(DateTime, nullable=False)
    cmta_dateout = Column(DateTime, nullable=False)
    cmta_amount = Column(MONEY, nullable=False)
    cmta_paidtodate = Column(DateTime, nullable=False)
    cmta_floatamount = Column(MONEY, nullable=False)
    cmta_additionalcharge = Column(MONEY, nullable=False)
    cmta_additionalfee = Column(MONEY, nullable=False)
    cmta_monthlycharge = Column(BIT, nullable=False)
    cmta_reminder = Column(DateTime)
    cmvt_id = Column(UNIQUEIDENTIFIER, index=True)
    CMLT_ID = Column(UNIQUEIDENTIFIER)
    cmclvt_id = Column(UNIQUEIDENTIFIER, server_default=text("(null)"))

    cmtr = relationship('CMTRTransaction')


class CMTBPTranBillPay(Base):
    __tablename__ = 'CMTBP_TranBillPay'

    cmtbp_id = Column(UNIQUEIDENTIFIER, primary_key=True, server_default=text("(newid())"))
    cmtr_id = Column(ForeignKey('CMTR_Transaction.cmtr_id'), nullable=False, index=True)
    sto_pk = Column(SmallInteger, nullable=False, index=True)
    cmtbp_tranno = Column(Integer, nullable=False)
    cmtbp_date = Column(String(10, 'SQL_Latin1_General_CP1_CI_AS'))
    cmtbp_time = Column(String(10, 'SQL_Latin1_General_CP1_CI_AS'))
    cmtbp_billerid = Column(String(10, 'SQL_Latin1_General_CP1_CI_AS'))
    cmtbp_billername = Column(String(30, 'SQL_Latin1_General_CP1_CI_AS'))
    cmtbp_consacct = Column(String(35, 'SQL_Latin1_General_CP1_CI_AS'))
    cmtbp_consname = Column(String(30, 'SQL_Latin1_General_CP1_CI_AS'))
    cmtbp_duedate = Column(String(10, 'SQL_Latin1_General_CP1_CI_AS'))
    cmtbp_amtdue = Column(MONEY)
    cmtbp_latedate = Column(String(10, 'SQL_Latin1_General_CP1_CI_AS'))
    cmtbp_latedue = Column(MONEY)
    cmtbp_amtpaid = Column(MONEY)
    cmtbp_tranfeedesc = Column(String(30, 'SQL_Latin1_General_CP1_CI_AS'))
    cmtbp_tranfee = Column(MONEY)

    cmtr = relationship('CMTRTransaction')


class CMTCTranCheck(Base):
    __tablename__ = 'CMTC_TranCheck'
    __table_args__ = (
        Index('IDX_CMTC_TranCheck_K2_K4_K8_6_7', 'cmtr_id', 'cmck_id', 'cmrh_id'),
        Index('IDX_CMTC_TranCheck_K2_K4_6_7', 'cmtr_id', 'cmck_id')
    )

    cmtc_id = Column(UNIQUEIDENTIFIER, primary_key=True, server_default=text("(newid())"))
    cmtr_id = Column(ForeignKey('CMTR_Transaction.cmtr_id'), nullable=False, index=True)
    cmck_id = Column(UNIQUEIDENTIFIER, nullable=False, index=True)
    sto_pk = Column(SmallInteger)
    cmtc_fee = Column(MONEY, server_default=text("(0)"))
    cmtc_calcfee = Column(MONEY)
    cmrh_id = Column(UNIQUEIDENTIFIER)
    cmcaa_agentcus_id = Column(UNIQUEIDENTIFIER, server_default=text("(null)"))

    cmtr = relationship('CMTRTransaction')


class CMTDLRTranDebitLoader(Base):
    __tablename__ = 'CMTDLR_TranDebitLoader'

    cmtdlr_id = Column(UNIQUEIDENTIFIER, primary_key=True, server_default=text("(newid())"))
    cmtr_id = Column(ForeignKey('CMTR_Transaction.cmtr_id'), nullable=False, index=True)
    sto_pk = Column(SmallInteger, nullable=False)
    cmtdlr_cmdlc_id = Column(UNIQUEIDENTIFIER, nullable=False, index=True)
    cmtdlr_tranno = Column(Integer, nullable=False)
    cmtdlr_amount = Column(MONEY, nullable=False)
    cmtdlr_fee = Column(MONEY, nullable=False)

    cmtr = relationship('CMTRTransaction')


class CMTHTranHistory(Base):
    __tablename__ = 'CMTH_TranHistory'
    __table_args__ = (
        Index('IDX_CMTH_TranHistory_K10_K8_K2_K1_K6_9_13', 'CMTH_Type', 'CMTH_Date', 'CMTR_ID', 'CMTH_ID', 'CMCD_ID'),
        Index('IDX_CMTH_TranHistory_K3_K8_K2_9_10', 'Sto_PK', 'CMTH_Date', 'CMTR_ID'),
        Index('IDX_CMTH_TranHistory_K10_K3_K8_K1_K6_K2', 'CMTH_Type', 'Sto_PK', 'CMTH_Date', 'CMTH_ID', 'CMCD_ID',
              'CMTR_ID'),
        Index('IDX_CMTH_TranHistory_K2_K10_K8_9', 'CMTR_ID', 'CMTH_Type', 'CMTH_Date'),
        Index('IX_CMTH_type_cmcd_cmtr', 'CMTH_Type', 'CMCD_ID', 'CMTR_ID'),
        Index('IDX_CMTH_TranHistory_K10_K8_K1_K2_9', 'CMTH_Type', 'CMTH_Date', 'CMTH_ID', 'CMTR_ID'),
        Index('IDX_CMTH_TranHistory_K1_K6_K2_K3_K10_K8_9_13', 'CMTH_ID', 'CMCD_ID', 'CMTR_ID', 'Sto_PK', 'CMTH_Type',
              'CMTH_Date'),
        Index('IDX_CMTH_TranHistory_K10_K8_2', 'CMTH_Type', 'CMTH_Date'),
        Index('IDX_CMTH_TranHistory_K2_K8_K10_K6', 'CMTR_ID', 'CMTH_Date', 'CMTH_Type', 'CMCD_ID'),
        Index('IDX_CMTH_TranHistory_K1_K8_K10_K6_K3_K2_9_13', 'CMTH_ID', 'CMTH_Date', 'CMTH_Type', 'CMCD_ID', 'Sto_PK',
              'CMTR_ID')
    )

    CMTH_ID = Column(UNIQUEIDENTIFIER, primary_key=True, server_default=text("(newid())"))
    CMTR_ID = Column(ForeignKey('CMTR_Transaction.cmtr_id'), nullable=False, index=True)
    Sto_PK = Column(SmallInteger, nullable=False)
    Usr_ID = Column(UNIQUEIDENTIFIER, nullable=False)
    CMCD_ID = Column(UNIQUEIDENTIFIER, index=True)
    CMLC_ID = Column(ForeignKey('CMLC_Lookup_C.cmlc_id'))
    CMTH_Date = Column(DateTime, nullable=False)
    CMTH_Amount = Column(MONEY, nullable=False)
    CMTH_Type = Column(CHAR(10, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, index=True)
    CMTH_Profit_Usr_id = Column(UNIQUEIDENTIFIER, nullable=False)
    CMTH_OverRideAmount = Column(MONEY, nullable=False, server_default=text("(0)"))
    cmth_salestax = Column(Numeric(8, 2))

    CMLC_Lookup_C = relationship('CMLCLookupC')
    CMTR_Transaction = relationship('CMTRTransaction')


class CMTMTranMoney(Base):
    __tablename__ = 'CMTM_TranMoney'

    cmtm_id = Column(UNIQUEIDENTIFIER, primary_key=True, server_default=text("(newid())"))
    cmtr_id = Column(ForeignKey('CMTR_Transaction.cmtr_id'), nullable=False, index=True)
    sto_pk = Column(SmallInteger, nullable=False)
    cmrh_id = Column(UNIQUEIDENTIFIER, nullable=False)
    cmtm_name = Column(String(50, 'SQL_Latin1_General_CP1_CI_AS'))
    cmtm_amount = Column(MONEY, nullable=False)
    cmtm_fee = Column(MONEY, nullable=False)
    cmtm_calcfee = Column(MONEY, nullable=False)
    cmtm_cost = Column(MONEY, nullable=False, server_default=text("(0)"))
    cmtm_serialno = Column(String(50, 'SQL_Latin1_General_CP1_CI_AS'))
    cmtm_mgprinted = Column(Integer, server_default=text("(null)"))

    cmtr = relationship('CMTRTransaction')


class CMTNCNoteCollection(Base):
    __tablename__ = 'CMTNC_NoteCollection'

    CMTNC_ID = Column(UNIQUEIDENTIFIER, primary_key=True, server_default=text("(newid())"))
    CMTN_ID = Column(ForeignKey('CMTN_Note.CMTN_ID'), nullable=False, index=True)
    CMTNC_Date = Column(DateTime, nullable=False)
    CMTNC_Amount = Column(MONEY)
    CMTNC_Description = Column(String(20, 'SQL_Latin1_General_CP1_CI_AS'))

    CMTN_Note = relationship('CMTNNote')


class CMTSDTransSaleDetail(Base):
    __tablename__ = 'CMTSD_TransSaleDetail'
    __table_args__ = (
        Index('IDX_CMTSD_TransSaleDetail_K5_K2_6_8', 'CMIPH_ID', 'CMTSH_ID'),
        Index('IDX_CMTSD_TransSaleDetail_K2_K5_6_8', 'CMTSH_ID', 'CMIPH_ID')
    )

    CMTSD_ID = Column(UNIQUEIDENTIFIER, primary_key=True)
    CMTSH_ID = Column(ForeignKey('CMTSH_TransSaleHeader.CMTSH_ID'), nullable=False, index=True)
    CMTH_ID = Column(UNIQUEIDENTIFIER, nullable=False)
    STO_PK = Column(SmallInteger, nullable=False)
    CMIPH_ID = Column(ForeignKey('CMIPH_InvPackageHeader.CMIPH_ID'), nullable=False)
    CMTSD_Quantity = Column(Integer, nullable=False, server_default=text("(1)"))
    CMTSD_Discount = Column(Numeric(9, 4), nullable=False, server_default=text("(0)"))
    CMTSD_SaleAmount = Column(MONEY, nullable=False)
    CMTSD_Exempt = Column(BIT, nullable=False)
    CMIPU_ID = Column(UNIQUEIDENTIFIER)
    CMIPR_ID = Column(UNIQUEIDENTIFIER)
    cmtsd_fee = Column(MONEY, nullable=False, server_default=text("(0)"))
    cmtsd_cost = Column(MONEY, nullable=False, server_default=text("(0)"))

    CMIPH_InvPackageHeader = relationship('CMIPHInvPackageHeader')
    CMTSH_TransSaleHeader = relationship('CMTSHTransSaleHeader')


class CMTSLTranSigLoan(Base):
    __tablename__ = 'CMTSL_TranSigLoan'

    CMTSL_id = Column(UNIQUEIDENTIFIER, primary_key=True, server_default=text("(newid())"))
    CMTR_id = Column(ForeignKey('CMTR_Transaction.cmtr_id'), nullable=False, index=True)
    CMRH_id = Column(ForeignKey('CMRH_RatesHeader.cmrh_id'), nullable=False, index=True)
    sto_pk = Column(SmallInteger, nullable=False)
    CMTSL_ticketnumber = Column(Integer, nullable=False)
    CMTSL_DateIn = Column(DateTime, nullable=False)
    CMTSL_MaturityDate = Column(DateTime, nullable=False)
    CMTSL_LoanAmount = Column(MONEY, nullable=False)
    CMTSL_ServiceAPR = Column(MONEY, nullable=False)
    CMTSL_InterestAPR = Column(MONEY, nullable=False)
    CMTSL_OneTimeFee = Column(MONEY, nullable=False)
    CMTSL_PeriodFee = Column(MONEY, nullable=False)
    CMTSL_AdminPrepaid = Column(MONEY, nullable=False)
    CMTSL_OrigPrepaid = Column(MONEY, nullable=False)
    CMTSL_MiscPrepaid = Column(MONEY, nullable=False)
    CMTSL_OriginalPrincipal = Column(MONEY, nullable=False)
    CMTSL_Duration = Column(SmallInteger, nullable=False)
    CMTSL_PaymentFreq = Column(String(1, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    CMTSL_FPIAmount = Column(MONEY, nullable=False)
    CMTSL_PIAmount = Column(MONEY, nullable=False)
    CMTSL_FirstPayment = Column(DateTime, nullable=False)
    CMTSL_DOM1 = Column(TINYINT, nullable=False)
    CMTSL_DOM2 = Column(TINYINT, nullable=False)
    CMTSL_Note = Column(String(254, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    cmtsl_LPIAmount = Column(MONEY, nullable=False, server_default=text("(0)"))
    cmtsl_AmortOneTime = Column(BIT)

    CMRH = relationship('CMRHRatesHeader')
    CMTR = relationship('CMTRTransaction')


class CMTSTranSale(Base):
    __tablename__ = 'CMTS_TranSale'

    cmts_id = Column(UNIQUEIDENTIFIER, primary_key=True, server_default=text("(newid())"))
    sto_pk = Column(SmallInteger, nullable=False)
    cmths_id = Column(ForeignKey('CMTHS_TranHistorySale.cmths_id'), nullable=False)
    cmth_id = Column(UNIQUEIDENTIFIER, nullable=False, index=True)
    sit_id = Column(UNIQUEIDENTIFIER, nullable=False, index=True)
    cmts_void_sit_id = Column(UNIQUEIDENTIFIER)

    cmths = relationship('CMTHSTranHistorySale')


class DLCDebitLoadCard(Base):
    __tablename__ = 'DLC_DebitLoadCard'

    dlc_id = Column(UNIQUEIDENTIFIER, primary_key=True, server_default=text("(newid())"))
    cus_pk = Column(Integer, nullable=False)
    dlp_id = Column(ForeignKey('DLP_DebitLoadProduct.dlp_id'))
    sto_pk = Column(SmallInteger, nullable=False)
    dlc_cardno = Column(BINARY(50), nullable=False)

    dlp = relationship('DLPDebitLoadProduct')


class DetailG(Base):
    __tablename__ = 'Detail_G'

    Sto_FK = Column(Integer, primary_key=True, nullable=False, server_default=text("(1)"))
    GDT_PK = Column(Integer, nullable=False, server_default=text("(1)"))
    Items_FK = Column(Integer, primary_key=True, nullable=False, server_default=text("(1)"))
    Caliber_FK = Column(ForeignKey('Lookup_C.lc_pk'), nullable=False, server_default=text("(1)"))
    Action_FK = Column(ForeignKey('Lookup_C.lc_pk'), nullable=False, server_default=text("(1)"))
    Finish_FK = Column(ForeignKey('Lookup_C.lc_pk'), nullable=False, server_default=text("(1)"))
    Barrel_FK = Column(ForeignKey('Lookup_C.lc_pk'), nullable=False, server_default=text("(1)"))
    ImporterFK = Column(ForeignKey('Lookup_C.lc_pk'), nullable=False, server_default=text("(1)"))
    Length = Column(String(10, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("(' ')"))
    Condition = Column(String(15, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("(' ')"))
    GDT_id = Column(UNIQUEIDENTIFIER, unique=True, server_default=text("(newid())"))
    LastUpdatedUSR_ID = Column(UNIQUEIDENTIFIER)

    Lookup_C = relationship('LookupC', primaryjoin='DetailG.Action_FK == LookupC.lc_pk')
    Lookup_C1 = relationship('LookupC', primaryjoin='DetailG.Barrel_FK == LookupC.lc_pk')
    Lookup_C2 = relationship('LookupC', primaryjoin='DetailG.Caliber_FK == LookupC.lc_pk')
    Lookup_C3 = relationship('LookupC', primaryjoin='DetailG.Finish_FK == LookupC.lc_pk')
    Lookup_C4 = relationship('LookupC', primaryjoin='DetailG.ImporterFK == LookupC.lc_pk')


class DetailJ(Base):
    __tablename__ = 'Detail_J'

    Sto_FK = Column(Integer, primary_key=True, nullable=False, server_default=text("(0)"))
    JDT_PK = Column(Integer, nullable=False, server_default=text("(1)"))
    Items_FK = Column(Integer, primary_key=True, nullable=False, server_default=text("(1)"))
    Gender_FK = Column(ForeignKey('Lookup_C.lc_pk'), nullable=False, server_default=text("(1)"))
    Style_FK = Column(ForeignKey('Lookup_C.lc_pk'), nullable=False, server_default=text("(1)"))
    Metal_FK = Column(ForeignKey('Lookup_C.lc_pk'), nullable=False, server_default=text("(1)"))
    Sizelen_FK = Column(ForeignKey('Lookup_C.lc_pk'), nullable=False, server_default=text("(1)"))
    Karat_FK = Column(ForeignKey('Lookup_C.lc_pk'), nullable=False, server_default=text("(1)"))
    Weight = Column(DECIMAL(9, 2), nullable=False, server_default=text("(0)"))
    WgtUnit = Column(String(1, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("('O')"))
    JDT_id = Column(UNIQUEIDENTIFIER, unique=True, server_default=text("(newid())"))
    LastUpdatedUSR_ID = Column(UNIQUEIDENTIFIER)

    Lookup_C = relationship('LookupC', primaryjoin='DetailJ.Gender_FK == LookupC.lc_pk')
    Lookup_C1 = relationship('LookupC', primaryjoin='DetailJ.Karat_FK == LookupC.lc_pk')
    Lookup_C2 = relationship('LookupC', primaryjoin='DetailJ.Metal_FK == LookupC.lc_pk')
    Lookup_C3 = relationship('LookupC', primaryjoin='DetailJ.Sizelen_FK == LookupC.lc_pk')
    Lookup_C4 = relationship('LookupC', primaryjoin='DetailJ.Style_FK == LookupC.lc_pk')


class DetailT(Base):
    __tablename__ = 'Detail_T'

    TDT_PK = Column(Integer, nullable=False)
    Sto_FK = Column(SmallInteger, primary_key=True, nullable=False, server_default=text("(1)"))
    Items_FK = Column(Integer, primary_key=True, nullable=False, server_default=text("(1)"))
    Style_FK = Column(ForeignKey('Lookup_C.lc_pk'), nullable=False, server_default=text("(1)"))
    cYEAR = Column(CHAR(4, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("(' ')"))
    Plate_State = Column(CHAR(2, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("(' ')"))
    Plate_number = Column(CHAR(10, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("(' ')"))
    Mileage = Column(CHAR(10, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("(' ')"))
    Title_Cert_Num = Column(CHAR(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("(' ')"))
    Validation_Num = Column(CHAR(15, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("(' ')"))
    TDT_id = Column(UNIQUEIDENTIFIER, unique=True, server_default=text("(newid())"))
    LastUpdatedUSR_ID = Column(UNIQUEIDENTIFIER)

    Lookup_C = relationship('LookupC')


class PPL1ProtPlanLevel1(Base):
    __tablename__ = 'PPL1_ProtPlanLevel1'

    ppl_id = Column(UNIQUEIDENTIFIER, primary_key=True, server_default=text("(newid())"))
    level_id = Column(UNIQUEIDENTIFIER, nullable=False, index=True)
    rpph_id = Column(ForeignKey('RPPH_RatesProtPlanHeader.rpph_id'), nullable=False, index=True)

    rpph = relationship('RPPHRatesProtPlanHeader')


class PPL2ProtPlanLevel2(Base):
    __tablename__ = 'PPL2_ProtPlanLevel2'

    ppl_id = Column(UNIQUEIDENTIFIER, primary_key=True, server_default=text("(newid())"))
    level_id = Column(UNIQUEIDENTIFIER, nullable=False, index=True)
    rpph_id = Column(ForeignKey('RPPH_RatesProtPlanHeader.rpph_id'), nullable=False, index=True)

    rpph = relationship('RPPHRatesProtPlanHeader')


class PPSProtPlanSale(Base):
    __tablename__ = 'PPS_ProtPlanSales'

    pps_id = Column(UNIQUEIDENTIFIER, primary_key=True, server_default=text("(newid())"))
    protected_id = Column(UNIQUEIDENTIFIER, nullable=False, index=True)
    protection_id = Column(UNIQUEIDENTIFIER, nullable=False, index=True)
    rpph_id = Column(ForeignKey('RPPH_RatesProtPlanHeader.rpph_id'), nullable=False, index=True)
    duration = Column(Integer, nullable=False)
    returntype = Column(TINYINT, nullable=False, server_default=text("((0))"))

    rpph = relationship('RPPHRatesProtPlanHeader')


class RPPDRatesProtPlanDetail(Base):
    __tablename__ = 'RPPD_RatesProtPlanDetail'

    rppd_id = Column(UNIQUEIDENTIFIER, primary_key=True, index=True, server_default=text("(newid())"))
    rpph_id = Column(ForeignKey('RPPH_RatesProtPlanHeader.rpph_id'), nullable=False)
    range = Column(MONEY)
    dp = Column(CHAR(1, 'SQL_Latin1_General_CP1_CI_AS'))
    ap = Column(MONEY)

    rpph = relationship('RPPHRatesProtPlanHeader')


t_WANT = Table(
    'WANT', metadata,
    Column('want_pk', Integer, nullable=False),
    Column('cus_fk', Integer, nullable=False, server_default=text("(0)")),
    Column('STO_PK', SmallInteger, nullable=False, server_default=text("(1)")),
    Column('Level1_fk', ForeignKey('Level1.lv1_pk'), nullable=False, server_default=text("(1)")),
    Column('level2_fk', ForeignKey('Level2.lv2_pk'), nullable=False, server_default=text("(1)")),
    Column('level3_fk', ForeignKey('Level3.lv3_pk'), nullable=False, server_default=text("(1)")),
    Column('level4_fk', ForeignKey('Level4.lv4_PK'), nullable=False, server_default=text("(1)")),
    Column('level5_fk', ForeignKey('Level5.lv5_PK'), nullable=False, server_default=text("(1)")),
    Column('MODEL', String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("('')")),
    Column('want_date', DateTime),
    Column('Offer', MONEY, nullable=False, server_default=text("(0.00)")),
    Column('WNT_DELETE', BIT, nullable=False, server_default=text("(0)")),
    Column('DESCRIPT', String(80, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("('')")),
    Column('DESCRIPT2', String(80, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("('')")),
    Column('COMMENT', String(80, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("('')")),
    Column('lv1_id', UNIQUEIDENTIFIER),
    Column('lv2_id', UNIQUEIDENTIFIER),
    Column('lv3_id', UNIQUEIDENTIFIER),
    Column('lv4_id', UNIQUEIDENTIFIER),
    Column('lv5_id', UNIQUEIDENTIFIER),
    Column('WNT_id', UNIQUEIDENTIFIER, unique=True, server_default=text("(newid())")),
    Column('LastUpdatedUSR_ID', UNIQUEIDENTIFIER),
    Index('IDX_Want_Level5_fk_sto_pk', 'level5_fk', 'STO_PK'),
    Index('IDX_Want_level1_fk_sto_pk', 'Level1_fk', 'STO_PK'),
    Index('IDX_Want_Level2_fk_sto_pk', 'level2_fk', 'STO_PK'),
    Index('IDX_Want_cus_fk_Sto_pk', 'cus_fk', 'STO_PK')
)


class Item(Base):
    __tablename__ = 'items'
    __table_args__ = (
        Index('IDX_Items_Sto_PK_Lv3_ID', 'Sto_Pk', 'lv3_ID'),
        Index('IDX_items_Sto_PK_Status', 'STATUS', 'Sto_Pk'),
        Index('IDX_items_Sto_PK_IsBulkItem', 'IsBulkItem', 'Sto_Pk'),
        Index('IDX_Items_Status_Sto_PK_TicketNum_Items_ID', 'STATUS', 'Sto_Pk', 'TICKETNUM', 'Items_ID'),
        Index('IDX_Items_Sto_PK_Lv1_ID', 'Sto_Pk', 'lv1_ID'),
        Index('IDX_Items_Sto_PK_Level5_FK', 'Sto_Pk', 'LEVEL5_FK'),
        Index('IDX_Items_Sto_PK_Level1_FK_Lv1_ID', 'Sto_Pk', 'LEVEL1_FK', 'lv1_ID'),
        Index('IDX_Items_Sto_PK_Level1_FK', 'Sto_Pk', 'LEVEL1_FK'),
        Index('IDX_Items_Sto_PK_Lv5_ID', 'Sto_Pk', 'lv5_ID'),
        Index('IDX_Items_Sto_PK_Ticketnum', 'TICKETNUM', 'Sto_Pk'),
        Index('IDX_Items_Sto_PK_Level3_FK', 'Sto_Pk', 'LEVEL3_FK'),
        Index('IDX_Items_Sto_PK_UPC', 'UPC', 'Sto_Pk'),
        Index('IDX_Items_Sto_PK_Level2_FK', 'Sto_Pk', 'LEVEL2_FK'),
        Index('IDX_Items_Sto_PK_Level4_FK', 'Sto_Pk', 'LEVEL4_FK'),
        Index('IDX_Items_Sto_PK_Status_NewItem', 'Sto_Pk', 'STATUS', 'NEWITEM'),
        Index('IDX_Items_Sto_PK_SERIALNUM', 'SERIALNUM', 'Sto_Pk'),
        Index('IDX_Items_Sto_PK_Level4_FK_Lv4_ID', 'Sto_Pk', 'LEVEL4_FK', 'lv4_ID'),
        Index('IDX_items_STO_PK_BIN', 'BIN', 'Sto_Pk'),
        Index('IDX_Items_Sto_PK_Level5_FK_Lv5_ID', 'Sto_Pk', 'LEVEL5_FK', 'lv5_ID'),
        Index('IDX_Items_Sto_PK_Lv2_ID', 'Sto_Pk', 'lv2_ID'),
        Index('IDX_Items_Sto_PK_Lv4_ID', 'Sto_Pk', 'lv4_ID'),
        Index('IDX_Items_Sto_PK_Level2_FK_Lv2_ID', 'Sto_Pk', 'LEVEL2_FK', 'lv2_ID'),
        Index('IDX_items_Sto_PK_Invnum', 'INVNUM', 'Sto_Pk'),
        Index('IDX_Items_Sto_PK_Level3_FK_Lv3_ID', 'Sto_Pk', 'LEVEL3_FK', 'lv3_ID')
    )

    Sto_Pk = Column(SmallInteger, primary_key=True, nullable=False, server_default=text("(0)"))
    ITEMS_PK = Column(Integer, primary_key=True, nullable=False, server_default=text("(0)"))
    CUS_FK = Column(Integer, nullable=False, index=True, server_default=text("(0)"))
    TICKETNUM = Column(Integer, nullable=False, server_default=text("(0)"))
    PolTicNum = Column(Integer, nullable=False, server_default=text("(0)"))
    usr_fk = Column(Integer, nullable=False, server_default=text("(0)"))
    LEVEL1_FK = Column(ForeignKey('Level1.lv1_pk'), nullable=False, index=True, server_default=text("(1)"))
    LEVEL2_FK = Column(ForeignKey('Level2.lv2_pk'), nullable=False, index=True, server_default=text("(1)"))
    LEVEL3_FK = Column(ForeignKey('Level3.lv3_pk'), nullable=False, index=True, server_default=text("(1)"))
    LEVEL4_FK = Column(ForeignKey('Level4.lv4_PK'), nullable=False, index=True, server_default=text("(1)"))
    LEVEL5_FK = Column(ForeignKey('Level5.lv5_PK'), nullable=False, index=True, server_default=text("(1)"))
    Color = Column(ForeignKey('Lookup_C.lc_pk'), nullable=False, server_default=text("(1)"))
    DESCRIPT = Column(String(200, 'SQL_Latin1_General_CP1_CI_AS'), server_default=text("('')"))
    DESCRIPT2 = Column(String(200, 'SQL_Latin1_General_CP1_CI_AS'), server_default=text("('')"))
    SERIALNUM = Column(String(50, 'SQL_Latin1_General_CP1_CI_AS'), server_default=text("('')"))
    MODELNUM = Column(String(20, 'SQL_Latin1_General_CP1_CI_AS'), server_default=text("('')"))
    BIN = Column(String(6, 'SQL_Latin1_General_CP1_CI_AS'), server_default=text("('')"))
    AMOUNT = Column(MONEY, server_default=text("(0.0)"))
    RESALEAMT = Column(MONEY, server_default=text("(0.0)"))
    INVNUM = Column(String(14, 'SQL_Latin1_General_CP1_CI_AS'), server_default=text("('')"))
    OnHand = Column(DECIMAL(10, 2), server_default=text("(0)"))
    STATUS = Column(String(1, 'SQL_Latin1_General_CP1_CI_AS'), server_default=text("('')"))
    OWNERNUM = Column(String(20, 'SQL_Latin1_General_CP1_CI_AS'), server_default=text("('')"))
    NEWITEM = Column(BIT, server_default=text("(0)"))
    DELETECOM = Column(String(20, 'SQL_Latin1_General_CP1_CI_AS'), server_default=text("('')"))
    DELETEDATE = Column(DateTime)
    REPAWNED = Column(BIT, server_default=text("(0)"))
    VENDOR = Column(Integer, server_default=text("(0)"))
    MAXQUANT = Column(DECIMAL(10, 2), server_default=text("(0)"))
    REORDER = Column(DECIMAL(10, 2), server_default=text("(0)"))
    UPC = Column(String(14, 'SQL_Latin1_General_CP1_CI_AS'), server_default=text("('')"))
    ORIGAMT = Column(MONEY, server_default=text("(0)"))
    CONSIGNOR = Column(Integer, index=True, server_default=text("(0)"))
    INSREPCOST = Column(MONEY, server_default=text("(0)"))
    SPLITNUMS = Column(String(7, 'SQL_Latin1_General_CP1_CI_AS'), server_default=text("('')"))
    LOWSLPRICE = Column(MONEY, server_default=text("(0)"))
    CSOURCE = Column(String(35, 'SQL_Latin1_General_CP1_CI_AS'), server_default=text("('')"))
    Composite = Column(String(255, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("('')"))
    Composit2 = Column(String(255, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("('')"))
    Composit3 = Column(String(255, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text("('')"))
    Composit4 = Column(String(1000, 'SQL_Latin1_General_CP1_CI_AS'), server_default=text("('')"))
    IsBulkItem = Column(BIT, server_default=text("(0)"))
    on_consign = Column(BIT, nullable=False, server_default=text("(0)"))
    itemPic_FK = Column(Integer, server_default=text("((-1))"))
    PawnedBefore = Column(BIT, nullable=False, server_default=text("(0)"))
    OrigOnHand = Column(Integer, server_default=text("(0)"))
    timestamp = Column(TIMESTAMP)
    storagefee = Column(MONEY, nullable=False, server_default=text("(0.00)"))
    lv1_ID = Column(UNIQUEIDENTIFIER, index=True)
    lv2_ID = Column(UNIQUEIDENTIFIER, index=True)
    lv3_ID = Column(UNIQUEIDENTIFIER, index=True)
    lv4_ID = Column(UNIQUEIDENTIFIER, index=True)
    lv5_ID = Column(UNIQUEIDENTIFIER, index=True)
    Items_ID = Column(UNIQUEIDENTIFIER, unique=True, server_default=text("(newid())"))
    DateItemEntered = Column(SMALLDATETIME)
    LastUpdatedUSR_ID = Column(UNIQUEIDENTIFIER)
    SalesTaxEx = Column(BIT, nullable=False, server_default=text("(0)"))
    PWN_id = Column(UNIQUEIDENTIFIER, index=True)
    WithProtectionPlan = Column(BIT, nullable=False, server_default=text("((1))"))
    Condition = Column(Integer, nullable=False, server_default=text("((1))"))
    ACS_ID = Column(String(15, 'SQL_Latin1_General_CP1_CI_AS'))
    ONORDER = Column(Integer)

    Lookup_C = relationship('LookupC')
    Level1 = relationship('Level1')
    Level2 = relationship('Level2')
    Level3 = relationship('Level3')
    Level4 = relationship('Level4')
    Level5 = relationship('Level5')


t_ph_physheader = Table(
    'ph_physheader', metadata,
    Column('ph_id', UNIQUEIDENTIFIER, nullable=False, unique=True, server_default=text("(newid())")),
    Column('sto_pk', SmallInteger, nullable=False),
    Column('emp_id', UNIQUEIDENTIFIER, nullable=False),
    Column('ph_batchdate', DateTime, nullable=False),
    Column('ph_batchtitle', String(100, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('ph_batchclosedate', DateTime),
    Column('ph_status', CHAR(2, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('ph_type', CHAR(1, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('level1_fk', ForeignKey('Level1.lv1_pk')),
    Column('level2_fk', ForeignKey('Level2.lv2_pk')),
    Column('level3_fk', ForeignKey('Level3.lv3_pk')),
    Column('level4_fk', ForeignKey('Level4.lv4_PK')),
    Column('bin', String(6, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('ph_excl_jew_firearm', BIT, server_default=text("(0)"))
)

t_stones = Table(
    'stones', metadata,
    Column('STONE_PK', Integer, nullable=False),
    Column('Sto_FK', SmallInteger, nullable=False, server_default=text("(1)")),
    Column('JDT_FK', Integer, nullable=False, server_default=text("(1)")),
    Column('TYPSTONEFK', ForeignKey('Lookup_C.lc_pk'), nullable=False, index=True, server_default=text("(1)")),
    Column('NUMSTONE', SmallInteger, nullable=False, index=True, server_default=text("(0)")),
    Column('SHAPE_FK', ForeignKey('Lookup_C.lc_pk'), nullable=False, index=True, server_default=text("(1)")),
    Column('COLOR_FK', ForeignKey('Lookup_C.lc_pk'), nullable=False, index=True, server_default=text("(1)")),
    Column('TRANSLUCFK', ForeignKey('Lookup_C.lc_pk'), nullable=False, index=True, server_default=text("(1)")),
    Column('WEIGHT', DECIMAL(9, 2), nullable=False, server_default=text("(0)")),
    Column('CARAT', DECIMAL(9, 2), nullable=False, server_default=text("(0)")),
    Column('LENGTH', DECIMAL(9, 2), nullable=False, server_default=text("(0)")),
    Column('WIDTH', DECIMAL(9, 2), nullable=False, server_default=text("(0)")),
    Column('STO_id', UNIQUEIDENTIFIER, unique=True, server_default=text("(newid())")),
    Column('LastUpdatedUSR_ID', UNIQUEIDENTIFIER),
    Index('IDX_stones_Sto_FK_JDT_FK', 'Sto_FK', 'JDT_FK')
)


class CMAVRATMVerifyResponse(Base):
    __tablename__ = 'CMAVR_ATMVerifyResponse'

    CMAVR_ID = Column(UNIQUEIDENTIFIER, primary_key=True, server_default=text("(newid())"))
    CMCA_ID = Column(ForeignKey('CMCA_CheckAccount.cmca_ID'), nullable=False)
    CMLC_ID = Column(ForeignKey('CMLC_Lookup_C.cmlc_id'), nullable=False)
    CMAVR_Date = Column(DateTime, nullable=False)
    CMAVR_TraceNo = Column(CHAR(36, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    CMAVR_Result = Column(CHAR(3, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)

    CMCA_CheckAccount = relationship('CMCACheckAccount')
    CMLC_Lookup_C = relationship('CMLCLookupC')


class CMBDPDBatchDishonorPayDet(Base):
    __tablename__ = 'CMBDPD_BatchDishonorPayDet'

    cmbdpd_id = Column(UNIQUEIDENTIFIER, primary_key=True, server_default=text("(newid())"))
    cmbdph_id = Column(ForeignKey('CMBDPH_BatchDishonorPayHead.cmbdph_id'), nullable=False, index=True)
    sto_pk = Column(SmallInteger, nullable=False)
    cmth_id = Column(UNIQUEIDENTIFIER, nullable=False, index=True)
    cmck_id = Column(UNIQUEIDENTIFIER, nullable=False, index=True)

    cmbdph = relationship('CMBDPHBatchDishonorPayHead')


class CMCBACashBoxAdjustment(Base):
    __tablename__ = 'CMCBA_CashBoxAdjustment'

    CMCBA_ID = Column(UNIQUEIDENTIFIER, primary_key=True, server_default=text("(newid())"))
    CMCBB_ID = Column(ForeignKey('CMCBB_CashBoxBalance.CMCBB_ID'), nullable=False)
    CMCD_ID = Column(UNIQUEIDENTIFIER, nullable=False)
    cmcba_comment = Column(String(254, 'SQL_Latin1_General_CP1_CI_AS'))

    CMCBB_CashBoxBalance = relationship('CMCBBCashBoxBalance')


class CMCBBCDCashBoxBalanceCashDrawer(Base):
    __tablename__ = 'CMCBBCD_CashBoxBalanceCashDrawer'
    __table_args__ = (
        Index('IX_CMCBBCD_cmcd_cmcbb_id', 'CMCD_ID', 'CMCBB_ID', 'CMCBBCD_ID'),
    )

    CMCBBCD_ID = Column(UNIQUEIDENTIFIER, primary_key=True, server_default=text("(newid())"))
    CMCBB_ID = Column(ForeignKey('CMCBB_CashBoxBalance.CMCBB_ID'), nullable=False, index=True)
    CMCD_ID = Column(ForeignKey('CMCD_CashDrawer.cmcd_id'), nullable=False, index=True)

    CMCBB_CashBoxBalance = relationship('CMCBBCashBoxBalance')
    CMCD_CashDrawer = relationship('CMCDCashDrawer')


class CMCBCCCCashBoxCountCheckColumn(Base):
    __tablename__ = 'CMCBCCC_CashBoxCountCheckColumn'
    __table_args__ = (
        Index('IDX_CMCBCCC_CashBoxCountCheckColumn_K2_K1_K3_K4', 'CMCBCC_ID', 'CMCBCCC_ID', 'CMCBCCC_Active',
              'CMCBCCC_Date'),
        Index('IDX_CMCBCCC_CashBoxCountCheckColumn_K3_K2_K1_K4', 'CMCBCCC_Active', 'CMCBCC_ID', 'CMCBCCC_ID',
              'CMCBCCC_Date')
    )

    CMCBCCC_ID = Column(UNIQUEIDENTIFIER, primary_key=True, server_default=text("(newid())"))
    CMCBCC_ID = Column(ForeignKey('CMCBCC_CashBoxCountCheck.CMCBCC_ID'), nullable=False, index=True)
    CMCBCCC_Active = Column(BIT, nullable=False)
    CMCBCCC_Date = Column(DateTime, nullable=False)

    CMCBCC_CashBoxCountCheck = relationship('CMCBCCCashBoxCountCheck')


class CMCBCCashBoxComment(Base):
    __tablename__ = 'CMCBC_CashBoxComment'

    CMCBC_ID = Column(UNIQUEIDENTIFIER, primary_key=True, server_default=text("(newid())"))
    CMCBH_ID = Column(ForeignKey('CMCBH_CashBoxHeader.CMCBH_ID'), nullable=False, index=True)
    CMCBC_Comment = Column(String(254, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)

    CMCBH_CashBoxHeader = relationship('CMCBHCashBoxHeader')


class CMCBTCashBoxDetail(Base):
    __tablename__ = 'CMCBT_CashBoxDetail'
    __table_args__ = (
        Index('IDX_CMCBT_CashBoxDetail_K4_K2', 'CMCD_ID', 'CMCBH_ID'),
    )

    CMCBT_ID = Column(UNIQUEIDENTIFIER, primary_key=True, server_default=text("(newid())"))
    CMCBH_ID = Column(ForeignKey('CMCBH_CashBoxHeader.CMCBH_ID'), nullable=False)
    CMCBS_ID = Column(ForeignKey('CMCBS_CashBoxSlot.CMCBS_ID'), nullable=False)
    CMCD_ID = Column(UNIQUEIDENTIFIER, nullable=False)

    CMCBH_CashBoxHeader = relationship('CMCBHCashBoxHeader')
    CMCBS_CashBoxSlot = relationship('CMCBSCashBoxSlot')


class CMCKCheck(Base):
    __tablename__ = 'CMCK_Check'
    __table_args__ = (
        Index('IDX_CMCK_Check_K1_K9_K4_K7_5_6_10', 'cmck_id', 'cmdba_id', 'cmca_id', 'cmck_cknumber'),
        Index('IDX_CMCK_Check_K1_K6_5_7', 'cmck_id', 'cmck_ckamount')
    )

    cmck_id = Column(UNIQUEIDENTIFIER, primary_key=True, index=True, server_default=text("(newid())"))
    sto_pk = Column(SmallInteger, nullable=False)
    cmca_id = Column(ForeignKey('CMCA_CheckAccount.cmca_ID'), nullable=False, index=True)
    cmck_ckdate = Column(DateTime, nullable=False)
    cmck_ckamount = Column(MONEY, nullable=False)
    cmck_cknumber = Column(String(20, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    cmck_directdebit = Column(BIT, server_default=text("(0)"))
    cmdba_id = Column(UNIQUEIDENTIFIER, index=True)
    cmck_Altered_CKAmount = Column(MONEY)
    cmck_endorsed = Column(BIT, server_default=text("(0)"))

    cmca = relationship('CMCACheckAccount')


class CMDLRDebitLoadResponse(Base):
    __tablename__ = 'CMDLR_DebitLoadResponse'

    cmdlr_id = Column(UNIQUEIDENTIFIER, primary_key=True, server_default=text("(newid())"))
    cmdlc_id = Column(ForeignKey('CMDLC_DebitLoadCard.cmdlc_id'), nullable=False)
    cmdlr_cmtr_id = Column(UNIQUEIDENTIFIER)
    sto_pk = Column(SmallInteger, nullable=False)
    cmdlr_cmtdl_tranno = Column(Integer, nullable=False)

    cmdlc = relationship('CMDLCDebitLoadCard')


class CMIODInvOrderDetail(Base):
    __tablename__ = 'CMIOD_InvOrderDetail'

    CMIOD_ID = Column(UNIQUEIDENTIFIER, primary_key=True)
    CMIOH_ID = Column(ForeignKey('CMIOH_InvOrderHeader.CMIOH_ID'), nullable=False)
    STO_PK = Column(SmallInteger, nullable=False)
    CMIOD_Quantity = Column(Integer, nullable=False)
    CMILU_ID = Column(UNIQUEIDENTIFIER, nullable=False)
    CMIOD_Cost = Column(MONEY, nullable=False)
    CMI_ID = Column(UNIQUEIDENTIFIER, nullable=False)

    CMIOH_InvOrderHeader = relationship('CMIOHInvOrderHeader')


class CMIItem(Base):
    __tablename__ = 'CMI_Item'
    __table_args__ = (
        Index('IDX_CMI_Item_K6_K2_1', 'CMI_Type', 'CMIT_ID'),
    )

    CMI_ID = Column(UNIQUEIDENTIFIER, primary_key=True)
    CMIT_ID = Column(ForeignKey('CMIT_InvType.CMIT_ID'))
    CMIB_ID = Column(ForeignKey('CMIB_InvBrand.CMIB_ID'))
    STO_PK = Column(SmallInteger, nullable=False, index=True)
    CMI_Active = Column(BIT, nullable=False, server_default=text("(1)"))
    CMI_Type = Column(CHAR(2, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    CMI_Description = Column(String(50, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    CMI_MaximumOnHand = Column(Integer)
    CMI_MinimumOnHand = Column(Integer)
    CMILU_ID = Column(UNIQUEIDENTIFIER)

    CMIB_InvBrand = relationship('CMIBInvBrand')
    CMIT_InvType = relationship('CMITInvType')


class CMTDLTranDebitLoad(Base):
    __tablename__ = 'CMTDL_TranDebitLoad'

    cmtdl_id = Column(UNIQUEIDENTIFIER, primary_key=True)
    cmtr_id = Column(ForeignKey('CMTR_Transaction.cmtr_id'), nullable=False)
    cmdlc_id = Column(ForeignKey('CMDLC_DebitLoadCard.cmdlc_id'), nullable=False)
    cmck_id = Column(UNIQUEIDENTIFIER)
    sto_pk = Column(SmallInteger, nullable=False)
    cmtdl_tranno = Column(Integer, nullable=False)

    cmdlc = relationship('CMDLCDebitLoadCard')
    cmtr = relationship('CMTRTransaction')


class CMTHATranHistoryAdvance(Base):
    __tablename__ = 'CMTHA_TranHistoryAdvance'

    cmtha_id = Column(UNIQUEIDENTIFIER, primary_key=True, server_default=text("(newid())"))
    cmth_id = Column(ForeignKey('CMTH_TranHistory.CMTH_ID'), nullable=False, index=True)
    sto_pk = Column(SmallInteger, nullable=False)
    cmrh_id = Column(UNIQUEIDENTIFIER, nullable=False)
    cmck_id = Column(UNIQUEIDENTIFIER, nullable=False)
    cmtha_ticketnumber = Column(Integer, nullable=False)
    cmtha_numberofday = Column(Integer, nullable=False)
    cmtha_datein = Column(DateTime, nullable=False)
    cmtha_dateout = Column(DateTime, nullable=False)
    cmtha_amount = Column(MONEY, nullable=False)
    cmtha_paidtodate = Column(DateTime, nullable=False)
    cmtha_floatamount = Column(MONEY, nullable=False)
    cmtha_additionalcharge = Column(MONEY, nullable=False)
    cmtha_additionalfee = Column(MONEY, nullable=False)
    cmtha_monthlycharge = Column(BIT, nullable=False)
    cmtha_reminder = Column(DateTime)
    cmvt_id = Column(UNIQUEIDENTIFIER)
    CMLT_ID = Column(UNIQUEIDENTIFIER)
    cmclvt_id = Column(UNIQUEIDENTIFIER, server_default=text("(null)"))

    cmth = relationship('CMTHTranHistory')


class CMTHBPTranHistoryBillPay(Base):
    __tablename__ = 'CMTHBP_TranHistoryBillPay'

    cmthbp_id = Column(UNIQUEIDENTIFIER, primary_key=True, server_default=text("(newid())"))
    cmth_id = Column(ForeignKey('CMTH_TranHistory.CMTH_ID'), nullable=False)
    sto_pk = Column(SmallInteger, nullable=False)
    cmtbp_id = Column(ForeignKey('CMTBP_TranBillPay.cmtbp_id'), nullable=False)

    cmtbp = relationship('CMTBPTranBillPay')
    cmth = relationship('CMTHTranHistory')


class CMTHCTranHistoryColumn(Base):
    __tablename__ = 'CMTHC_TranHistoryColumn'

    cmthc_id = Column(UNIQUEIDENTIFIER, primary_key=True, server_default=text("(newid())"))
    cmth_id = Column(ForeignKey('CMTH_TranHistory.CMTH_ID'), nullable=False)
    sto_pk = Column(SmallInteger, nullable=False)
    cmthc_newvalue = Column(String(50, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    cmthc_priorvalue = Column(String(50, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)

    cmth = relationship('CMTHTranHistory')


class CMTHDLRTranHistoryDebitLoader(Base):
    __tablename__ = 'CMTHDLR_TranHistoryDebitLoader'

    cmthdlr_id = Column(UNIQUEIDENTIFIER, primary_key=True, server_default=text("(newid())"))
    cmth_id = Column(ForeignKey('CMTH_TranHistory.CMTH_ID'), nullable=False, index=True)
    cmtdlr_id = Column(ForeignKey('CMTDLR_TranDebitLoader.cmtdlr_id'), nullable=False, index=True)
    sto_pk = Column(SmallInteger, nullable=False)

    cmtdlr = relationship('CMTDLRTranDebitLoader')
    cmth = relationship('CMTHTranHistory')


class CMTHGLDTranHistoryGLDetail(Base):
    __tablename__ = 'CMTHGLD_TranHistoryGLDetail'

    CMTHGLD_ID = Column(UNIQUEIDENTIFIER, primary_key=True, server_default=text("(newid())"))
    GLD_ID = Column(ForeignKey('GLD_Detail.GLD_ID'), nullable=False, index=True)
    CMTH_ID = Column(ForeignKey('CMTH_TranHistory.CMTH_ID'), nullable=False, index=True)

    CMTH_TranHistory = relationship('CMTHTranHistory')
    GLD_Detail = relationship('GLDDetail')


class CMTHMTranHistoryMoney(Base):
    __tablename__ = 'CMTHM_TranHistoryMoney'

    cmthm_id = Column(UNIQUEIDENTIFIER, primary_key=True, server_default=text("(newid())"))
    cmth_id = Column(ForeignKey('CMTH_TranHistory.CMTH_ID'), nullable=False, index=True)
    sto_pk = Column(SmallInteger, nullable=False)
    cmtm_id = Column(ForeignKey('CMTM_TranMoney.cmtm_id'), nullable=False)

    cmth = relationship('CMTHTranHistory')
    cmtm = relationship('CMTMTranMoney')


class CMTHSLTranHistorySigLoan(Base):
    __tablename__ = 'CMTHSL_TranHistorySigLoan'

    CMTHSL_id = Column(UNIQUEIDENTIFIER, primary_key=True, server_default=text("(newid())"))
    CMTSL_id = Column(ForeignKey('CMTSL_TranSigLoan.CMTSL_id'), nullable=False, index=True)
    CMTH_id = Column(ForeignKey('CMTH_TranHistory.CMTH_ID'), nullable=False, index=True)
    sto_pk = Column(SmallInteger, nullable=False)
    CMTHSL_DueDate = Column(DateTime, nullable=False)
    CMTHSL_Principal = Column(MONEY, nullable=False)
    CMTHSL_FloatAmount = Column(MONEY, nullable=False)
    CMTHSL_PromiseDate = Column(DateTime, nullable=False)

    CMTH = relationship('CMTHTranHistory')
    CMTSL = relationship('CMTSLTranSigLoan')


class CMTHTTranHistoryTax(Base):
    __tablename__ = 'CMTHT_TranHistoryTax'

    CMTHT_ID = Column(UNIQUEIDENTIFIER, primary_key=True)
    CMTH_ID = Column(ForeignKey('CMTH_TranHistory.CMTH_ID'), nullable=False)
    STO_PK = Column(SmallInteger, nullable=False)
    CMTHT_StateTax = Column(MONEY, nullable=False)
    CMTHT_CountyTax = Column(MONEY, nullable=False)
    CMTHT_LocalTax = Column(MONEY, nullable=False)
    CMTHT_Taxable = Column(MONEY, nullable=False, server_default=text("(0.0000)"))
    CMTHT_Nontaxable = Column(MONEY, nullable=False, server_default=text("(0.0000)"))

    CMTH_TranHistory = relationship('CMTHTranHistory')


class DLTDebitLoadTran(Base):
    __tablename__ = 'DLT_DebitLoadTran'
    __table_args__ = (
        Index('IX_DLT_TicketNum', 'ticketnum', 'sto_pk'),
    )

    dlt_id = Column(UNIQUEIDENTIFIER, primary_key=True, server_default=text("(newid())"))
    dlc_id = Column(ForeignKey('DLC_DebitLoadCard.dlc_id'), nullable=False)
    ticketnum = Column(Integer, nullable=False)
    dlt_tranno = Column(Integer, nullable=False)
    sto_pk = Column(SmallInteger, nullable=False)

    dlc = relationship('DLCDebitLoadCard')


class CMCBBCTCashBoxBalanceCashType(Base):
    __tablename__ = 'CMCBBCT_CashBoxBalanceCashType'
    __table_args__ = (
        Index('IX_CMCBBCT_cmcbbcd_cmct', 'CMCBBCD_ID', 'CMCT_ID'),
    )

    CMCBBCT_ID = Column(UNIQUEIDENTIFIER, primary_key=True, server_default=text("(newid())"))
    CMCBBCD_ID = Column(ForeignKey('CMCBBCD_CashBoxBalanceCashDrawer.CMCBBCD_ID'), nullable=False)
    CMCT_ID = Column(UNIQUEIDENTIFIER, nullable=False)

    CMCBBCD_CashBoxBalanceCashDrawer = relationship('CMCBBCDCashBoxBalanceCashDrawer')


class CMIGTItemGLType(Base):
    __tablename__ = 'CMIGT_ItemGLType'

    CMIGT_ID = Column(UNIQUEIDENTIFIER, primary_key=True, server_default=text("(newid())"))
    CMI_ID = Column(ForeignKey('CMI_Item.CMI_ID'), nullable=False)
    GLT_ID = Column(ForeignKey('CMGLT_Type.GLT_ID'), nullable=False)
    STO_PK = Column(SmallInteger, nullable=False)

    CMI_Item = relationship('CMIItem')
    CMGLT_Type = relationship('CMGLTType')


class CMILItemLot(Base):
    __tablename__ = 'CMIL_ItemLot'

    CMIL_ID = Column(UNIQUEIDENTIFIER, primary_key=True, server_default=text("(newid())"))
    CMI_ID = Column(ForeignKey('CMI_Item.CMI_ID'), nullable=False, index=True)
    STO_PK = Column(SmallInteger, nullable=False)
    CMIOD_ID = Column(UNIQUEIDENTIFIER)
    CMILH_ID = Column(ForeignKey('CMILH_ItemLotHeader.CMILH_ID'), index=True)
    CMIL_Quantity = Column(Integer, nullable=False)
    CMILU_ID = Column(UNIQUEIDENTIFIER, nullable=False, index=True)
    CMIL_Cost = Column(Numeric(18, 4), nullable=False)
    CMIL_Status = Column(CHAR(2, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, index=True,
                         server_default=text("('O')"))
    CMIL_Allowance = Column(Numeric(18, 4), nullable=False, server_default=text("(0)"))
    CMIL_Discount = Column(Numeric(18, 4), nullable=False, server_default=text("(0)"))

    CMILH_ItemLotHeader = relationship('CMILHItemLotHeader')
    CMI_Item = relationship('CMIItem')


class CMIPIInvPackageItem(Base):
    __tablename__ = 'CMIPI_InvPackageItem'
    __table_args__ = (
        Index('IDX_CMIPI_InvPackageItem_K2_K3', 'CMIPH_ID', 'CMI_ID'),
    )

    CMIPI_ID = Column(UNIQUEIDENTIFIER, primary_key=True)
    CMIPH_ID = Column(ForeignKey('CMIPH_InvPackageHeader.CMIPH_ID'), nullable=False)
    CMI_ID = Column(ForeignKey('CMI_Item.CMI_ID'), nullable=False, index=True)
    STO_PK = Column(SmallInteger, nullable=False)
    CMIPI_Quantity = Column(Integer, nullable=False)
    CMILU_ID = Column(ForeignKey('CMILU_InvLookupUnit.CMILU_ID'), nullable=False)
    CMIPI_Price = Column(MONEY, server_default=text("(0)"))

    CMILU_InvLookupUnit = relationship('CMILUInvLookupUnit')
    CMIPH_InvPackageHeader = relationship('CMIPHInvPackageHeader')
    CMI_Item = relationship('CMIItem')
