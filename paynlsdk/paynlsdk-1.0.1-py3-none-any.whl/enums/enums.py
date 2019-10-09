from enum import Enum


class Gender(Enum):
    male = 'm'
    female = 'f'


class TaxClassCategory(Enum):
    none = 'N'
    low = 'L'
    high = 'H'


class TaxClass(Enum):
    none = 0
    low = 6
    high = 21


class PaymentMethodId(Enum):
    sms = 1
    payfixedprice = 2
    paypercall = 3
    paypertransaction = 4
    payperminute = 5


class ExchangeState(Enum):
    failed = -1
    notcalled = 0
    success = 1


class ActiveState(Enum):
    inactive = 0
    active = 1


class Secure(Enum):
    notsecure = 0
    secure3d = 1


class Availability(Enum):
    unavailable = 0
    available = 1


class Blacklist(Enum):
    notblacklisted = 0
    blacklisted = 1
    blacklistedbyothers = 2


class ProductType(Enum):
    ARTICLE = 'ARTICLE'
    SHIPPING = 'SHIPPING'
    HANDLING = 'HANDLING'
    DISCOUNT = 'DISCOUNT'


class PaymentStatus(Enum):
    CANCEL = -90
    CANCEL_2 = -60
    DENIED = -63
    PARTIAL_REFUND = -82
    REFUND = -81
    EXPIRED = -80
    REFUND_IN_PROGRESS = -72
    CHARGEBACK_1 = -71
    CHARGEBACK_2 = -70
    PAID_CHECKAMOUNT = -51
    WAIT = 0
    PENDING_1 = 20
    PENDING_2 = 25
    PENDING_3 = 50
    PENDING_4 = 90
    OPEN = 60
    CONFIRMED_1 = 75
    CONFIRMED_2 = 76
    PARTIAL_PAYMENT = 80
    VERIFY = 85
    AUTHORIZE = 95
    PAID = 100
