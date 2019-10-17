#  Copyright (c) 2019 | Advancing Technology Systems, LLC
#  See LICENSE for any grants of usage, distribution, or modification

from collections import namedtuple
from datetime import datetime, timedelta

from fuzzywuzzy import process
from sqlalchemy import create_engine, and_, or_
from sqlalchemy.engine.url import URL
from sqlalchemy.exc import *
from sqlalchemy.orm import sessionmaker

from pawn_pay import Customer, Ticket, Payment, CustomerList, TicketList
from pawn_pay.Exceptions import *
from .models import Cust, Pawn, LookupC, C_Rates, SysInfo1, Acct, CSSCustStatsStore

Store = namedtuple(
    typename="Store",
    field_names=["pk", "name", "address", "phone", "service_period", "pawn_days"],
    defaults=[0, "", "", "", 30, 30],
    module="PawnMaster",
)

Rate = namedtuple(
    typename="Rate",
    field_names=[
        "store_pk",
        "description",
        "multiplier",
        "period_based",
        "ap",
        "interest",
        "onetime",
        "per_month",
        "dp",
        "is_simple",
        "in_period",
        "min_amount",
        "max_amount",
    ],
    defaults=[1, "", 0.1, False, 0.0, 0.0, 0.0, 0.0, "", False, 0, 0.0, 0.0],
    module="PawnMaster",
)


class IsolinearNanoProbe(object):
    """Creates a connection to the PawnMaster DB

    NOTE:
    """

    def __init__(self, sql_driver=None, sql_user=None, sql_pass=None, sql_host=None, sql_port=None, store_pk=None):
        """Initializes and tests the connection to the SQL server

        Args:
            sql_driver (str): SQL Alchemy-supported driver to access the SQL DB
                with
            sql_user (str): Username to access SQL DB with
            sql_pass (str): Password to access SQL DB with
            sql_host (str): IP address || FQDN || DSN of SQL DB
            sql_port (str): Port SQL DB listens on
            store_pk (int): Restrict returned values to specified store

        Raises:
            CatastrophicPhaseVariance: Raised if the SQL DB cannot be accessed
                using the supplied information
        """
        self.store_pk = store_pk

        # The SQL server instance is a bit finicky about connections
        # Initialize our connection indicator to False until we can actually check that our connection is good
        self.sql_connection = False

        # Build a connection string that SQL Alchemy will recognize and use
        conn_string = URL(
            **{
                key: value
                for key, value in list(
                    filter(
                        lambda x: all([x[1] is not None, x[1] != ""]),
                        {
                            "drivername": sql_driver,
                            "username": sql_user,
                            "password": sql_pass,
                            "host": sql_host,
                            "port": sql_port,
                        }.items(),
                    )
                )
            }
        )

        self.__db = create_engine(conn_string, encoding="utf8", echo=False)
        self.__super_session = sessionmaker(bind=self.__db)
        self.__super_session.configure(autoflush=False, autocommit=False, expire_on_commit=False)
        self.__session = self.__super_session()

        try:
            self.__db.connect()
            self.sql_connection = True
        except OperationalError as err:
            raise CatastrophicPhaseVariance(err)

        # Initialize a list to hold any errors we encounter during the
        # session, to be checked before committing changes to the DB

        self.session_errors = list()

    @property
    def pending_changes(self):
        return {
            "to be created": self.__session.new,
            "to be updated": self.__session.dirty,
            "to be deleted": self.__session.deleted,
        }

    def save_changes(self):
        if len(self.session_errors) < 1:
            changes = {
                "new": list(self.__session.new),
                "updated": list(self.__session.dirty),
                "deleted": list(self.__session.deleted),
            }
            self.__session.flush()
            self.__session.commit()
            return True, changes
        else:
            return False, self.session_errors

    def rollback_changes(self):
        changes = {
            "not added": list(self.__session.new),
            "not updated": list(self.__session.dirty),
            "not deleted": list(self.__session.deleted),
        }
        try:
            self.__session.rollback()
            return True, changes
        except Exception as err:
            return False, err

    @property
    def store_info(self):
        info = [shop for shop in self.__session.query(SysInfo1).all()]
        return info if info.__len__() > 1 else info[0]

    def get_customers(self):
        """Get all complete customer records from PawnMaster

        Get a list of all customer records in a PawnMaster database that have
        a valid email address and phone number

        Returns:
            list: [ Customer(name (str), email (str), phone (str)), ...]
        """
        return CustomerList(
            [
                Customer(name=customer.name, email=customer.email, phone=customer.phone)
                for customer in list(
                filter(
                    lambda x: all([x.email is not None, x.phone is not None, x.name is not None]),
                    self.__session.query(Cust)
                        .filter(
                        and_(
                            Cust.Cus_Email != "",
                            Cust.Cus_CellPhone != "",
                            (
                                (Cust.Cus_Store == self.store_pk)
                                if self.store_pk is not None
                                else (Cust.Cus_Store > 0)
                            ),
                        )
                    )
                        .all(),
                )
            )
            ]
        )

    def get_tickets(self, with_customers=True):
        """Get a store's currently active ticket records from PawnMaster

        Get a list of all currently active ticket records in
        a PawnMaster database, pre-formatted for upload to Pawn-Pay.
        If no store identifier is supplied, the default store_pk (1) is used.

        Args:
            with_customers (bool): Return tickets with customer emails attached

        Returns:
            list: [ Ticket(
                        number (str),
                        amount (int),
                        due_date (datetime),
                        customer_email (str),
                        status (str),
                        renewal_period (int),
                        renew_from_payment (str),
                        layaway (bool),
                        layaway_total (int),
                        layaway_payment (int),
                    ),
                    ...
                ]
        """
        # The rate "filter" parts of the list comprehension will
        # likely need to be checked for accuracy against any
        # given PawnMaster instance before actual use

        return TicketList(
            [
                Ticket(
                    data=(
                        (
                            {
                                "number": str(t.TICKETNUM).strip(),
                                "amount": t.payment_amount,
                                "due_date": t.CHARGEDATE,
                                "customer_email": t.customer.email,
                                "renewal_period": t.store.PAWNDAYS,
                            }
                        )
                        if with_customers and t.customer is not None
                        else (
                            {
                                "number": str(t.TICKETNUM).strip(),
                                "amount": t.payment_amount,
                                "due_date": t.CHARGEDATE,
                                "renewal_period": t.store.PAWNDAYS,
                            }
                        )
                    )
                )
                for t in self.__session.query(Pawn)
                .filter(
                Pawn.STATUS == "P",
                Pawn.TRANS == "P",
                ((Pawn.STORE_NO == self.store_pk) if self.store_pk is not None else (Pawn.STORE_NO > 0)),
            )
                .all()
            ]
        )

    def update_customer(self, customer: any([dict, Customer]), id_by: str, key: any([str, int]), certainty=85):
        """Update an existing PawnMaster customer record

        Due to PawnMaster's support for multiple stores in a single DB and
        lack of enforced uniqueness for customer information, the id_by
        parameter is used to supply a strategy for ensuring the correct customer
        record is updated. Supported strategies are:

        ticket (most reliable): update the customer record associated with the supplied ticket
        email (ill advised): update any customer record(s) whose on file email address matches
        phone (ill advised): update any customer record(s) whose on file cellphone number matches
        name (don't ever do this): update any customer record(s)
                                   whose full name matches meets the minimum match certainty

        Args:
            customer (dict || pawn_pay.helpers.Customer): the new customer information
            id_by (str): the strategy used to identify the correct customer to update
            key (str): the key value used by the selected strategy to identify the correct customer to update
            certainty (int): the minimum match certainty to a customer's name required to allow an update

        Returns:
            tuple: (success (bool), customer name if successful else errors (str))
        """
        if id_by == "ticket":
            # This -should- select all tickets matching the supplied key
            # if more than one ticket is found, use fuzzywuzzy's [process.extractOne] function
            # to go through the ticket's owners to find (hopefully only) one that matches the supplied customer record

            if len("".join(str(x) if str(x).isnumeric() else "" for x in str(key))) > 1:
                lookup = [
                    x.customer
                    for x in self.__session.query(Pawn).filter(Pawn.TRANS == "P", Pawn.TICKETNUM == key).all()
                ]
                lookup = process.extractOne(customer.name, lookup) if lookup.__len__() > 0 else None
                lookup = lookup[0] if lookup is not None and lookup[1] >= certainty else None
            else:
                return False, "PawnMaster ticket numbers must be integers or numeric-only strings"

        elif id_by in ["email", "phone", "name"]:
            lookup = key.split(" ")
            lookup = (
                (self.__session.query(Cust).filter(Cust.Cus_Email == key).all())
                if id_by == "email"
                else (
                    self.__session.query(Cust)
                        .filter(
                        or_(Cust.Cus_CellPhone == key, and_(Cust.CUS_AC1 == key[:3], Cust.CUS_PHONE1 == key[3:])))
                        .all()
                )
                if id_by == "phone"
                else (
                    self.__session.query(Cust)
                        .filter(
                        Cust.CUS_FNAME.ilike("%" + lookup[0] + "%"),
                        (
                            (
                                Cust.CUS_LNAME.ilike(
                                    "%" + ((lookup[2]) if lookup.__len__() == 3 else (lookup[1])) + "%"
                                )
                            )
                            if lookup.__len__() >= 2
                            else (Cust.Cus_PK > 0)
                        ),
                    )
                        .all()
                )
            )
            lookup = process.extractOne(customer.name, lookup) if lookup.__len__() > 0 else None
            lookup = lookup[0] if lookup is not None and lookup[1] >= certainty else None

        else:
            lookup = None
            raise ValueError("Supported 'id_by' strategies are:  [ticket, email, phone, name]")

        if lookup is None:
            return False, "Could not find matching customer to update"

        try:
            up_count = 0
            if lookup.Cus_Email != customer.email:
                lookup.Cus_Email = customer.email
                up_count += 1
            if len(lookup.CUS_AC1.strip()) < 3 and len(lookup.CUS_PHONE1.strip()) < 7:
                lookup.CUS_AC1 = customer.phone[:3]
                lookup.CUS_PHONE1 = customer.phone[3:]
                up_count += 1
            if lookup.CusCellPhone != customer.phone:
                lookup.CusCellPhone = customer.phone
                up_count += 1
            if up_count > 0:
                self.__session.add(lookup)
            return True, lookup, up_count
        except Exception as err:
            self.session_errors.append(err)
            return False, err, 0

    def input_payment(self, payment: type(Payment)):
        """Input a payment made via Pawn-Pay to the PawnMaster DB

        Args:
            payment (pawn_pay.Payment): The payment to input
            store_pk (int): The primary key of the store that wrote the ticket being paid against
        """
        if len("".join(x if not x.isnumeric() else "" for x in str(payment.ticket_number))) > 0:
            return False, "Ticket numbers must be of type [int]"
        if self.store_pk is None:
            raise CatastrophicPhaseVariance(
                "Payments cannot be input without specifying a store_pk "
                + "during initialization of the PawnMaster connection"
            )

        ticket_lookup = (
            self.__session.query(Pawn)
                .filter(
                Pawn.TICKETNUM == payment.ticket_number,
                Pawn.TRANS == "P",
                Pawn.STATUS == "P",
                Pawn.STORE_NO == self.store_pk,
            )
                .all()
        )

        if len(ticket_lookup) > 1:
            raise RuinousMicroFluctuation(
                "More than one ticket match found! Aborting attempt to process payment " + str(payment.number)
            )
        if len(ticket_lookup) < 1:
            raise RuinousMicroFluctuation(
                "No matching ticket found! Aborting attempt to process payment " + str(payment.number)
            )
        else:
            ticket_lookup = ticket_lookup[0]

        rate_total = (
                ticket_lookup.rate.AP
                + ticket_lookup.rate.Interest
                + ticket_lookup.rate.MONCHRG
                + ticket_lookup.rate.ONECHRG
        )

        int_paid = round((float(payment.amount / 100) * round(float(ticket_lookup.rate.Interest / rate_total), 5)), 2)
        svc_paid = float(payment.amount / 100) - int_paid

        payment_record = Acct(
            sto_pk=self.store_pk,
            DATEin=datetime.now(),
            TICKETNUM=payment.ticket_number,
            CUS_FK=ticket_lookup.customer.Cus_PK,
            TYPE="PPP",
            AMOUNT=float(payment.amount / 100),
            Usr_FK=161619,
            Enter_UsrFK=161619,
            TENDERTYP1=161619,
            TENDERAMT1=float(payment.amount / 100),
            OneTime=0,
            Ticket=0,
            Prep=0,
            Gun=0,
            Daily=0,
            RTint=int_paid,
            RTsvc=svc_paid,
            RTper=0,
            RTonetime=0,
            Station=ticket_lookup.original_station,
        )

        pawn_update = ticket_lookup
        pawn_update.DATEOUT = ticket_lookup.DATEOUT + timedelta(days=ticket_lookup.store.PAWNDAYS)
        pawn_update.TRANSDATE = datetime.now()
        pawn_update.CHARGEDATE = ticket_lookup.CHARGEDATE + timedelta(days=ticket_lookup.store.PAWNDAYS)
        pawn_update.PAIDAMT = float(ticket_lookup.PAIDAMT) + float(payment.amount / 100)

        customer_update = ticket_lookup.customer
        customer_update.CUS_AMT1 = float(ticket_lookup.customer.CUS_AMT1) + float(payment.amount / 100)

        customer_update.stats.CSS_Amt1 = float(customer_update.stats.CSS_Amt1) + float(payment.amount / 100)

        try:
            [self.__session.add(q) for q in [payment_record, pawn_update, customer_update]]

            return (True, payment.number) if len(self.session_errors) < 1 else (False, self.session_errors)
        except Exception as err:
            self.session_errors.append(err)
            return False, err


# Copyright (c) 2019 | Advancing Technology Systems, LLC
# See LICENSE for any grants of usage, distribution, or modification
