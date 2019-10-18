#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
"""
***
Module: postsignum
***
"""
# Copyright (C) Smart Arcs Ltd registered in the United Kingdom.
# Unauthorized copying of this file, via any medium is strictly prohibited
#
# This file is provided under a license as specified in the "LICENSE" file, which is part
# of this software package.
#
# Written by Smart Arcs <support@smartarchitects.co.uk>, August 2018
import base64
import binascii
import logging

from cryptography import x509
from cryptography.hazmat.backends import default_backend
# noinspection PyProtectedMember
from cryptography.x509 import ExtensionOID

from foxyproxy.constant import Constant
from foxyproxy.csp import TokenRecord
from foxyproxy.csp import CertificateRecord
from foxyproxy.csp import ReaderRecord
from foxyproxy.csp import BaseCryptoService
from foxyproxy.upstream import RegisterUpstream

__author__ = "Smart Arcs"
__copyright__ = 'Smart Arcs Ltd'
__email__ = 'support@smartarchitects.co.uk'
__status__ = 'Development'

logger = logging.getLogger(__name__)


# logger.setLevel(logging.INFO)
# ch = logging.StreamHandler()
# ch.setLevel(logging.INFO)
# logger.addHandler(ch)


class CryptoPostSignum(BaseCryptoService):
    """
    This class implements signing with eIDAS smart cards of a Czech trust provider I.CA.
    """

    ca_certs = [
        "MIIEijCCA3KgAwIBAgIBZzANBgkqhkiG9w0BAQsFADBgMQswCQYDVQQGEwJDWjEs"
        "MCoGA1UECgwjxIxlc2vDoSBwb8WhdGEsIHMucC4gW0nEjCA0NzExNDk4M10xIzAh"
        "BgNVBAMTGkRFTU8gUG9zdFNpZ251bSBSb290IFFDQSAyMB4XDTA5MTIxMTA3NTY0"
        "N1oXDTE5MTIxMTA3NTYxMVowZDELMAkGA1UEBhMCQ1oxLDAqBgNVBAoMI8SMZXNr"
        "w6EgcG/FoXRhLCBzLnAuIFtJxIwgNDcxMTQ5ODNdMScwJQYDVQQDEx5ERU1PIFBv"
        "c3RTaWdudW0gUXVhbGlmaWVkIENBIDIwggEiMA0GCSqGSIb3DQEBAQUAA4IBDwAw"
        "ggEKAoIBAQDdjq5EmbFtevax6oC5h15xE7VYvTBDjzA+zAZb446p5OfQuKlU/EOt"
        "zV9rKksBUWWi/CCO0xQyfO4i/iiTlDLGCh6wqZlynNlyV1D0mnEQDSQg5piMxbdP"
        "sn6H4KNffvqhqlBokzo2ETrV0dH4Q/EKprVxcL90CJFXSb58d2PyxFW2j1E8DE03"
        "NluqxaZvF5VPrZuaLnw+c6w25OXtcN11YUHBnfDxIG622dN6x9oPYOTMUGuihYmZ"
        "hwcbHddIqdEPLEgkhV6KFogoPeUiJjUbLWmUEYAfa22675Csq3sgvjxzRiMrfJxP"
        "rOy5U3LP1xdmAbKVIvUpSlqvGHpqOGQ9AgMBAAGjggFJMIIBRTAyBgNVHSAEKzAp"
        "MCcGBFUdIAAwHzAdBggrBgEFBQcCAjARGg9ERU1PIGNlcnRpZmlrYXQwEgYDVR0T"
        "AQH/BAgwBgEB/wIBADAOBgNVHQ8BAf8EBAMCAQYwgYkGA1UdIwSBgTB/gBRLhZON"
        "6pqUvNad3vrpKJJIbD4KAqFkpGIwYDELMAkGA1UEBhMCQ1oxLDAqBgNVBAoMI8SM"
        "ZXNrw6EgcG/FoXRhLCBzLnAuIFtJxIwgNDcxMTQ5ODNdMSMwIQYDVQQDExpERU1P"
        "IFBvc3RTaWdudW0gUm9vdCBRQ0EgMoIBZDBABgNVHR8EOTA3MDWgM6Axhi9odHRw"
        "Oi8vd3d3LnBvc3RzaWdudW0uY3ovY3JsL2RlbW9wc3Jvb3RxY2EyLmNybDAdBgNV"
        "HQ4EFgQUmP/z94uLm61k5tQ+pgmkgDfPbLQwDQYJKoZIhvcNAQELBQADggEBABO2"
        "ckhqCyP4kqlyhDAhkni9UzhiOU/p/dkMoPFT70ti46Y4bXuGFXJHeZu2FkPnGa6d"
        "aVGZYNh3HTopW9XM/BkxrMzzFFm+BDnRH+iUr+0JGBM8ChLfjDIu3cCQJlEmHtW+"
        "ikQwNN4RXPLffxXrJUyFDWG6LGQCv2vESsYWfwW5Rik2MF0Z5OvGhs7P5hD7E6B/"
        "iH8Tyir/5Kc4oSi+Gh/tl/eKWXdXH06G3ZHRL7tD07DAY0Cloc7EkSe2BgcIF40+"
        "XeFnX4SNmB0cpgHYqIFZ2tNT84Alw0t/bny0TCQqc5HOSQ7T7e28HFVPOyo9x25t"
        "fA5f2X3G6/O0oHz0Nk4=",
        "MIIEojCCA4qgAwIBAgIDCC5NMA0GCSqGSIb3DQEBCwUAMGQxCzAJBgNVBAYTAkNa"
        "MSwwKgYDVQQKDCPEjGVza8OhIHBvxaF0YSwgcy5wLiBbScSMIDQ3MTE0OTgzXTEn"
        "MCUGA1UEAxMeREVNTyBQb3N0U2lnbnVtIFF1YWxpZmllZCBDQSAyMB4XDTE2MDEx"
        "ODA3MjgwNVoXDTE5MTIxMTA3NTYxMVowXTELMAkGA1UEBhMCQ1oxHTAbBgNVBAoM"
        "FMSMZXNrw6EgcG/FoXRhLCBzLnAuMREwDwYDVQQLEwhUU0EgREVNTzEcMBoGA1UE"
        "AxMTVFNBIERFTU8gUG9zdFNpZ251bTCCASIwDQYJKoZIhvcNAQEBBQADggEPADCC"
        "AQoCggEBAMy4/JrB0OgtxHsCkIjPEIeBfabbYYS3RUC2HMYHaBn29OMsRg2e7LSo"
        "CrCyR4yuNalR1HsA/2YhEWut6TVW+I8DsT44Yjc+9fMZ1Bctr5j/bqsBpSBN8qWZ"
        "JwQzYUe/H1V4rxK9bpnZ0VZfTnXUI1JUzdcr8HgkIFZ4UonKNa5WRFoMkjbFB7Ue"
        "2FZzhhHZNdhGmQY/FWrUZ1GsVoeP6prG+TrD+iJuMjoEvdnc8O5ZhC+x2oA0J2cj"
        "pQ95AGvS9Pz8seobW/c9Cy7bKAxcCcgJ50EIoOHiaNgzR4LBlUIMDU3unmLhpjX4"
        "wwS/wLhYomGxMigNDxz8lo0Z7rm/qsUCAwEAAaOCAWIwggFeMAkGA1UdEwQCMAAw"
        "NgYDVR0gBC8wLTArBghngQYBBAEBczAfMB0GCCsGAQUFBwICMBEaD0RFTU8gY2Vy"
        "dGlmaWthdDAaBggrBgEFBQcBAwQOMAwwCgYIKwYBBQUHCwIwTwYIKwYBBQUHAQEE"
        "QzBBMD8GCCsGAQUFBzAChjNodHRwOi8vd3d3LnBvc3RzaWdudW0uY3ovY3J0L2Rl"
        "bW9wc3F1YWxpZmllZGNhMi5jcnQwDgYDVR0PAQH/BAQDAgbAMBYGA1UdJQEB/wQM"
        "MAoGCCsGAQUFBwMIMB8GA1UdIwQYMBaAFJj/8/eLi5utZObUPqYJpIA3z2y0MEQG"
        "A1UdHwQ9MDswOaA3oDWGM2h0dHA6Ly93d3cucG9zdHNpZ251bS5jei9jcmwvZGVt"
        "b3BzcXVhbGlmaWVkY2EyLmNybDAdBgNVHQ4EFgQU6hL49eT0Xd2kMcygTDQWZ+0p"
        "bH4wDQYJKoZIhvcNAQELBQADggEBANLweK7XOal9817eAxpX4ccgMfycb76z54O4"
        "veynLkOTvrx0e2AvvSwOuFGNBmJ9WNWa1xJMObWXNkOrXeYtjIMc7+WXUmz/lJqJ"
        "VyMVGjodrq+A3kLC0vWR1tEcxoEDRz3Z8KJOqtB8NKL4cimen2kqU/DCSe5GfYKs"
        "G0euEisVq/ITVHWobCo/T5Q1XRvlyhmvKruoIUUn90H+gpNk7aGuaA640Yi7yOpB"
        "NzHXNnl/k39qV+qZtm15kbHP6eEg/8LbvdYDgNIRBrm+wAzYaNjWrnoBg0gpR+os"
        "rr1zD7WwXi1gtxp+VGURvn0pjb/Qc9xXkOz5h4D0bjv+L1dcEpA=",
        "MIIGXzCCBUegAwIBAgIBcTANBgkqhkiG9w0BAQsFADBbMQswCQYDVQQGEwJDWjEs"
        "MCoGA1UECgwjxIxlc2vDoSBwb8WhdGEsIHMucC4gW0nEjCA0NzExNDk4M10xHjAc"
        "BgNVBAMTFVBvc3RTaWdudW0gUm9vdCBRQ0EgMjAeFw0xMDAxMTkxMTMxMjBaFw0y"
        "MDAxMTkxMTMwMjBaMF8xCzAJBgNVBAYTAkNaMSwwKgYDVQQKDCPEjGVza8OhIHBv"
        "xaF0YSwgcy5wLiBbScSMIDQ3MTE0OTgzXTEiMCAGA1UEAxMZUG9zdFNpZ251bSBR"
        "dWFsaWZpZWQgQ0EgMjCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBAKbR"
        "ReVFlmMooQD/ZzJA9M793LcZivHRvWEG8jsEpp2xTayR17ovs8OMeoYKjvGo6PDf"
        "kCJs+sBYS0q5WQFApdWkyl/tUOw1oZ2SPSq6uYLJUyOYSKPMOgKz4u3XuB4Ki1Z+"
        "i8Fb7zeRye6eqahK+tql3ZAJnrJKgC4X2Ta1RKkxK+Hu1bdhWJA3gwL+WkIZbL/P"
        "YIzjet++T8ssWK1PWdBXsSfKOTikNzZt2VPETAQDBpOYxqAgLfCRbcb9KU2WIMT3"
        "NNxILu3sNl+OM9gV/GWO943JHsOMAVyJSQREaZksG5KDzzNzQS/LsbYkFtnJAmmh"
        "7g9p9Ci6cEJ+pfBTtMECAwEAAaOCAygwggMkMIHxBgNVHSAEgekwgeYwgeMGBFUd"
        "IAAwgdowgdcGCCsGAQUFBwICMIHKGoHHVGVudG8ga3ZhbGlmaWtvdmFueSBzeXN0"
        "ZW1vdnkgY2VydGlmaWthdCBieWwgdnlkYW4gcG9kbGUgemFrb25hIDIyNy8yMDAw"
        "U2IuIGEgbmF2YXpueWNoIHByZWRwaXN1L1RoaXMgcXVhbGlmaWVkIHN5c3RlbSBj"
        "ZXJ0aWZpY2F0ZSB3YXMgaXNzdWVkIGFjY29yZGluZyB0byBMYXcgTm8gMjI3LzIw"
        "MDBDb2xsLiBhbmQgcmVsYXRlZCByZWd1bGF0aW9uczASBgNVHRMBAf8ECDAGAQH/"
        "AgEAMIG8BggrBgEFBQcBAQSBrzCBrDA3BggrBgEFBQcwAoYraHR0cDovL3d3dy5w"
        "b3N0c2lnbnVtLmN6L2NydC9wc3Jvb3RxY2EyLmNydDA4BggrBgEFBQcwAoYsaHR0"
        "cDovL3d3dzIucG9zdHNpZ251bS5jei9jcnQvcHNyb290cWNhMi5jcnQwNwYIKwYB"
        "BQUHMAKGK2h0dHA6Ly9wb3N0c2lnbnVtLnR0Yy5jei9jcnQvcHNyb290cWNhMi5j"
        "cnQwDgYDVR0PAQH/BAQDAgEGMIGDBgNVHSMEfDB6gBQVKYzFRWmruLPD6v5LuDHY"
        "3PDndqFfpF0wWzELMAkGA1UEBhMCQ1oxLDAqBgNVBAoMI8SMZXNrw6EgcG/FoXRh"
        "LCBzLnAuIFtJxIwgNDcxMTQ5ODNdMR4wHAYDVQQDExVQb3N0U2lnbnVtIFJvb3Qg"
        "UUNBIDKCAWQwgaUGA1UdHwSBnTCBmjAxoC+gLYYraHR0cDovL3d3dy5wb3N0c2ln"
        "bnVtLmN6L2NybC9wc3Jvb3RxY2EyLmNybDAyoDCgLoYsaHR0cDovL3d3dzIucG9z"
        "dHNpZ251bS5jei9jcmwvcHNyb290cWNhMi5jcmwwMaAvoC2GK2h0dHA6Ly9wb3N0"
        "c2lnbnVtLnR0Yy5jei9jcmwvcHNyb290cWNhMi5jcmwwHQYDVR0OBBYEFInoTN+L"
        "Jjk+1yQuEg565+Yn5daXMA0GCSqGSIb3DQEBCwUAA4IBAQB17M2VB48AXCVfVeeO"
        "Lo0LIJZcg5EyHUKurbnff6tQOmyT7gzpkJNY3I3ijW2ErBfUM/6HefMxYKKWSs4j"
        "XqGSK5QfxG0B0O3uGfHPS4WFftaPSAnWk1tiJZ4c43+zSJCcH33n9pDmvt8n0j+6"
        "cQAZIWh4PPpmkvUg3uN4E0bzZHnH2uKzMvpVnE6wKml6oV+PUfPASPIYQw9gFEAN"
        "cMzp10hXJHrnOo0alPklymZdTVssBXwdzhSBsFel1eVBSvVOx6+y8zdbrkRLOvTV"
        "nSMb6zH+fsygU40mimdo30rY/6N+tdQhbM/sTCxgdWAy2g0elAN1zi9Jx6aQ76wo"
        "Dcn+",
        "MIIGYDCCBUigAwIBAgICAKQwDQYJKoZIhvcNAQELBQAwWzELMAkGA1UEBhMCQ1ox"
        "LDAqBgNVBAoMI8SMZXNrw6EgcG/FoXRhLCBzLnAuIFtJxIwgNDcxMTQ5ODNdMR4w"
        "HAYDVQQDExVQb3N0U2lnbnVtIFJvb3QgUUNBIDIwHhcNMTQwMzI2MDgwMTMyWhcN"
        "MjQwMzI2MDcwMDM2WjBfMQswCQYDVQQGEwJDWjEsMCoGA1UECgwjxIxlc2vDoSBw"
        "b8WhdGEsIHMucC4gW0nEjCA0NzExNDk4M10xIjAgBgNVBAMTGVBvc3RTaWdudW0g"
        "UXVhbGlmaWVkIENBIDMwggEiMA0GCSqGSIb3DQEBAQUAA4IBDwAwggEKAoIBAQCX"
        "Ou7d2frODVCZuo7IEWxoF5f1KE9aelb8FUyoZCL6iyvBe7YaL1pH4FJ5DPFbf3mz"
        "6rLnSiDY/YSpipstdNUHM2BZkhiEulb7ltvMC+v4gf+H9ApVkmNspEWcO8+Thj4b"
        "m0anXJ8oFKRCkPQYAPQQyRq0erqlXTkXS4NePI0TU4mvtaokZCqBBqzP6GnXOvZA"
        "zxo/KkK7nvgEwibZEXnrI3ZN20dzmvT/m+igHsPfBuTJsRXO1ytqxD+xz8L9eoAX"
        "yOWbQTLJI9FXE3utZ9fr0mhEUc0xcaQfVwdGahJ6/ex1asZH7XFD2VyHaTSqXomD"
        "iyo71Zp0EnGjdLACkUtdAgMBAAGjggMoMIIDJDCB8QYDVR0gBIHpMIHmMIHjBgRV"
        "HSAAMIHaMIHXBggrBgEFBQcCAjCByhqBx1RlbnRvIGt2YWxpZmlrb3Zhbnkgc3lz"
        "dGVtb3Z5IGNlcnRpZmlrYXQgYnlsIHZ5ZGFuIHBvZGxlIHpha29uYSAyMjcvMjAw"
        "MFNiLiBhIG5hdmF6bnljaCBwcmVkcGlzdS9UaGlzIHF1YWxpZmllZCBzeXN0ZW0g"
        "Y2VydGlmaWNhdGUgd2FzIGlzc3VlZCBhY2NvcmRpbmcgdG8gTGF3IE5vIDIyNy8y"
        "MDAwQ29sbC4gYW5kIHJlbGF0ZWQgcmVndWxhdGlvbnMwEgYDVR0TAQH/BAgwBgEB"
        "/wIBADCBvAYIKwYBBQUHAQEEga8wgawwNwYIKwYBBQUHMAKGK2h0dHA6Ly93d3cu"
        "cG9zdHNpZ251bS5jei9jcnQvcHNyb290cWNhMi5jcnQwOAYIKwYBBQUHMAKGLGh0"
        "dHA6Ly93d3cyLnBvc3RzaWdudW0uY3ovY3J0L3Bzcm9vdHFjYTIuY3J0MDcGCCsG"
        "AQUFBzAChitodHRwOi8vcG9zdHNpZ251bS50dGMuY3ovY3J0L3Bzcm9vdHFjYTIu"
        "Y3J0MA4GA1UdDwEB/wQEAwIBBjCBgwYDVR0jBHwweoAUFSmMxUVpq7izw+r+S7gx"
        "2Nzw53ahX6RdMFsxCzAJBgNVBAYTAkNaMSwwKgYDVQQKDCPEjGVza8OhIHBvxaF0"
        "YSwgcy5wLiBbScSMIDQ3MTE0OTgzXTEeMBwGA1UEAxMVUG9zdFNpZ251bSBSb290"
        "IFFDQSAyggFkMIGlBgNVHR8EgZ0wgZowMaAvoC2GK2h0dHA6Ly93d3cucG9zdHNp"
        "Z251bS5jei9jcmwvcHNyb290cWNhMi5jcmwwMqAwoC6GLGh0dHA6Ly93d3cyLnBv"
        "c3RzaWdudW0uY3ovY3JsL3Bzcm9vdHFjYTIuY3JsMDGgL6AthitodHRwOi8vcG9z"
        "dHNpZ251bS50dGMuY3ovY3JsL3Bzcm9vdHFjYTIuY3JsMB0GA1UdDgQWBBTy+Mwq"
        "V2HaKxczWeWCLewGHIpPSjANBgkqhkiG9w0BAQsFAAOCAQEAVHG9oYU7dATQI/yV"
        "gwhboNVX9Iat8Ji6PvVnoM6TQ8WjUQ5nErZG1fV5QQgN7slMBWnXKNjUSxMDpfht"
        "N2RbJHniaw/+vDqKtlmoKAnmIRzRaIqBLwGZs6RGHFrMPiol3La55fBoa4JPliRT"
        "Fw5xVOK5FdJh/5Pbfg+XNZ0RzO0/tk/oKRXfgRNb9ZBL2pe8sr9g9QywpsGKt2gP"
        "9t0q/+dhKAGc0+eimChM8Bmq4WNUxK4qdo4ARH6344uIVlIu+9Gq3H54noyZd/Oh"
        "RTnuoXuQOdx9DooTp6SPpPfZXj/djsseT22QVpYBP7v8AVK/paqphINL2XmQdiw6"
        "5KhDYA==",
        "MIIGSDCCBTCgAwIBAgICANUwDQYJKoZIhvcNAQELBQAwWzELMAkGA1UEBhMCQ1ox"
        "LDAqBgNVBAoMI8SMZXNrw6EgcG/FoXRhLCBzLnAuIFtJxIwgNDcxMTQ5ODNdMR4w"
        "HAYDVQQDExVQb3N0U2lnbnVtIFJvb3QgUUNBIDIwHhcNMTgxMDI1MDcyOTE3WhcN"
        "MjUwMTE5MDgwNDMxWjBjMQswCQYDVQQGEwJDWjEsMCoGA1UECgwjxIxlc2vDoSBw"
        "b8WhdGEsIHMucC4gW0nEjCA0NzExNDk4M10xJjAkBgNVBAMTHVBvc3RTaWdudW0g"
        "UXVhbGlmaWVkIENBIDMtVFNBMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKC"
        "AQEAwc2QqDKrJgrtmoTt5FOx8YZjDA7cFzDPCpdbugwnenXg0ZZg96Emvmq/Y8X+"
        "oYumOkBwr6jDmwj5EajqYvm5Wi+SqROdDdaWBfTaWnklgypXrHLXVKn1znsAZBuK"
        "5MhOKy4CQOeg7Jgg7DvgvrEUCgbmLTEXigpsbBJx0An6QW9cHzSWGWG9CGlTdUUW"
        "BB6SFlBSXgvw5HourO/ggnBxwTIXWVCOmYlOnZqooMJREQgv+9RZdnZ9esztRIgM"
        "AhSE4RGxZg3WqiClCwMSYrurH3ORLdX4B1ctCF8Kct85wONQSCu0vtSmEZMhzdcS"
        "V4n2vSBH+N84OHYcjgepjSjCMQIDAQABo4IDDDCCAwgwgdUGA1UdIASBzTCByjCB"
        "xwYEVR0gADCBvjCBuwYIKwYBBQUHAgIwga4agatUZW50byBjZXJ0aWZpa2F0IHBy"
        "byBlbGVrdHJvbmlja291IHBlY2V0IGJ5bCB2eWRhbiB2IHNvdWxhZHUgcyBuYXJp"
        "emVuaW0gRVUgYy4gOTEwLzIwMTQuVGhpcyBpcyBhIGNlcnRpZmljYXRlIGZvciBl"
        "bGVjdHJvbmljIHNlYWwgYWNjb3JkaW5nIHRvIFJlZ3VsYXRpb24gKEVVKSBObyA5"
        "MTAvMjAxNC4wEgYDVR0TAQH/BAgwBgEB/wIBADCBvAYIKwYBBQUHAQEEga8wgaww"
        "NwYIKwYBBQUHMAKGK2h0dHA6Ly93d3cucG9zdHNpZ251bS5jei9jcnQvcHNyb290"
        "cWNhMi5jcnQwOAYIKwYBBQUHMAKGLGh0dHA6Ly93d3cyLnBvc3RzaWdudW0uY3ov"
        "Y3J0L3Bzcm9vdHFjYTIuY3J0MDcGCCsGAQUFBzAChitodHRwOi8vcG9zdHNpZ251"
        "bS50dGMuY3ovY3J0L3Bzcm9vdHFjYTIuY3J0MA4GA1UdDwEB/wQEAwIBBjCBgwYD"
        "VR0jBHwweoAUFSmMxUVpq7izw+r+S7gx2Nzw53ahX6RdMFsxCzAJBgNVBAYTAkNa"
        "MSwwKgYDVQQKDCPEjGVza8OhIHBvxaF0YSwgcy5wLiBbScSMIDQ3MTE0OTgzXTEe"
        "MBwGA1UEAxMVUG9zdFNpZ251bSBSb290IFFDQSAyggFkMIGlBgNVHR8EgZ0wgZow"
        "MaAvoC2GK2h0dHA6Ly93d3cucG9zdHNpZ251bS5jei9jcmwvcHNyb290cWNhMi5j"
        "cmwwMqAwoC6GLGh0dHA6Ly93d3cyLnBvc3RzaWdudW0uY3ovY3JsL3Bzcm9vdHFj"
        "YTIuY3JsMDGgL6AthitodHRwOi8vcG9zdHNpZ251bS50dGMuY3ovY3JsL3Bzcm9v"
        "dHFjYTIuY3JsMB0GA1UdDgQWBBRsw+aHUj0hN36Xs2TOEa127kSy1jANBgkqhkiG"
        "9w0BAQsFAAOCAQEAU0UkMCe/3FpM0jW1akSEuZ1VSfqJtQ/k6GFXBPbUi3pmpHkc"
        "NJsE9PlNC/e819Gz0xCiCpfYMJFAuh+VoPVD0S1MpSpBw9iXbUKn/BQGRc9nNvRy"
        "aHSA90wwSyh5+/4Bm7/MySyiN7nk1dlWo8/Kn4lMF/wvh41+dPTrv4mgOgqJel04"
        "Dd31v990D+LvxwLB5hVK6YjkUXivBPjIx6CI9tcMcM/9mKEouc2HjlaMjSbWNMO7"
        "srRPPnYvvzcOKg75wPE0TWhhEK+JR4oTf0YHmTXPbG4z6X+lbmDZ49ikWuCKzP1l"
        "bA2jlU5wkBh6F0/Of8cFyxgOMWyfgCMzxiBWow==",
        "MIIGXDCCBUSgAwIBAgIBcjANBgkqhkiG9w0BAQsFADBbMQswCQYDVQQGEwJDWjEs"
        "MCoGA1UECgwjxIxlc2vDoSBwb8WhdGEsIHMucC4gW0nEjCA0NzExNDk4M10xHjAc"
        "BgNVBAMTFVBvc3RTaWdudW0gUm9vdCBRQ0EgMjAeFw0xMDAxMTkxMzM2MTFaFw0y"
        "MDAxMTkxMzM1NDJaMFwxCzAJBgNVBAYTAkNaMSwwKgYDVQQKDCPEjGVza8OhIHBv"
        "xaF0YSwgcy5wLiBbScSMIDQ3MTE0OTgzXTEfMB0GA1UEAxMWUG9zdFNpZ251bSBQ"
        "dWJsaWMgQ0EgMjCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBALFqPb09"
        "F3sXxYtm8k64ePhIeQKY17MVm6sFb8bcdcEqnM5YXskZ9nvohRAwfMBN9Msgd70B"
        "tTJB+bctteMnXuV/ANfGl2aYG2/7r/GdnRwZO/Eu67zzIBgAVQWK7wNTYHoNHoXK"
        "CuMPs4QoXu+/oyUd/f4cTm5DPGTz/n1JyMEmQeXoFhxheDUt4lHPFEBA9Qjdqlk2"
        "u3jhoJpgNbUX5SvgLKeC3udpZNpJajc/MYcf97R4l2K+iIl/fbvB+RDcQPqQZNWz"
        "6nBs1+efFlxIg545Cz3Y1WL/DkP78gr55S/Jh+Fvk5fP8FDQIhnbVpndd6tAjfmn"
        "R+Vvd3ONQd0Q4vcCAwEAAaOCAygwggMkMIHxBgNVHSAEgekwgeYwgeMGBFUdIAAw"
        "gdowgdcGCCsGAQUFBwICMIHKGoHHVGVudG8ga3ZhbGlmaWtvdmFueSBzeXN0ZW1v"
        "dnkgY2VydGlmaWthdCBieWwgdnlkYW4gcG9kbGUgemFrb25hIDIyNy8yMDAwU2Iu"
        "IGEgbmF2YXpueWNoIHByZWRwaXN1L1RoaXMgcXVhbGlmaWVkIHN5c3RlbSBjZXJ0"
        "aWZpY2F0ZSB3YXMgaXNzdWVkIGFjY29yZGluZyB0byBMYXcgTm8gMjI3LzIwMDBD"
        "b2xsLiBhbmQgcmVsYXRlZCByZWd1bGF0aW9uczASBgNVHRMBAf8ECDAGAQH/AgEA"
        "MIG8BggrBgEFBQcBAQSBrzCBrDA3BggrBgEFBQcwAoYraHR0cDovL3d3dy5wb3N0"
        "c2lnbnVtLmN6L2NydC9wc3Jvb3RxY2EyLmNydDA4BggrBgEFBQcwAoYsaHR0cDov"
        "L3d3dzIucG9zdHNpZ251bS5jei9jcnQvcHNyb290cWNhMi5jcnQwNwYIKwYBBQUH"
        "MAKGK2h0dHA6Ly9wb3N0c2lnbnVtLnR0Yy5jei9jcnQvcHNyb290cWNhMi5jcnQw"
        "DgYDVR0PAQH/BAQDAgEGMIGDBgNVHSMEfDB6gBQVKYzFRWmruLPD6v5LuDHY3PDn"
        "dqFfpF0wWzELMAkGA1UEBhMCQ1oxLDAqBgNVBAoMI8SMZXNrw6EgcG/FoXRhLCBz"
        "LnAuIFtJxIwgNDcxMTQ5ODNdMR4wHAYDVQQDExVQb3N0U2lnbnVtIFJvb3QgUUNB"
        "IDKCAWQwgaUGA1UdHwSBnTCBmjAxoC+gLYYraHR0cDovL3d3dy5wb3N0c2lnbnVt"
        "LmN6L2NybC9wc3Jvb3RxY2EyLmNybDAyoDCgLoYsaHR0cDovL3d3dzIucG9zdHNp"
        "Z251bS5jei9jcmwvcHNyb290cWNhMi5jcmwwMaAvoC2GK2h0dHA6Ly9wb3N0c2ln"
        "bnVtLnR0Yy5jei9jcmwvcHNyb290cWNhMi5jcmwwHQYDVR0OBBYEFEjvPtTqiYmj"
        "6eI/2++MQrEK+MjRMA0GCSqGSIb3DQEBCwUAA4IBAQBAWREYnlE2Tl0xt1q/MSjh"
        "9cCNd41kSonCP+xD3meT7hwW75dgS2pYWQd814Y7HAbrQ0CT34pc4jX76YxPyXOQ"
        "pCl7A/Cwpgu6wdFPPV9ExyHWqvzjP0zfyIgk9WzTJTik6fdl2heaINgUX5Uh+xXk"
        "NsddYMi8vXEh1129vcwSmkQep8RPF02PGX4OQ/Lj4em7Gdhx/sWDQDyTuJ4LRPkX"
        "Ek6YO76Zm4vidiNXloK0Ni/npm6pt/WN4SDCa2ERNnwcPnGou74zKLWD8YSdvZYF"
        "KSr050Cjjg2n3TSl9GllFCtTO2BLWnj2+eDdMWvaAVWL5+fRH7MH7wc1e5XtWdmz",
        "MIIGSDCCBTCgAwIBAgICAMMwDQYJKoZIhvcNAQELBQAwWzELMAkGA1UEBhMCQ1ox"
        "LDAqBgNVBAoMI8SMZXNrw6EgcG/FoXRhLCBzLnAuIFtJxIwgNDcxMTQ5ODNdMR4w"
        "HAYDVQQDExVQb3N0U2lnbnVtIFJvb3QgUUNBIDIwHhcNMTcwMzIwMDgyODM4WhcN"
        "MjUwMTE5MDgwNDMxWjBcMQswCQYDVQQGEwJDWjEsMCoGA1UECgwjxIxlc2vDoSBw"
        "b8WhdGEsIHMucC4gW0nEjCA0NzExNDk4M10xHzAdBgNVBAMTFlBvc3RTaWdudW0g"
        "UHVibGljIENBIDMwggEiMA0GCSqGSIb3DQEBAQUAA4IBDwAwggEKAoIBAQDIiUSr"
        "XZqgX+ZK1F+bxRw957rh1FklTEyONCxDdeid8POSALF3RAwg3uFkhU8o63v6I5mY"
        "wxSXFaxc8jkQ1ViYt9aVl4zAQ+4ZVhbChIwwKB4zllspT418Yq4oJfE+KP04XR8u"
        "0Thqm0t/9BD7Wz4DkkQ6Qq7Pk9uDlHwC7G/f7sf0zwVe+SKM6X/0Gen9G9/f0lcE"
        "H/FhnvZbn9I3gkIHS1to8BvcQouUXAVvdTz0Ej50Iw0Nfo9/KRHI8mhm2LkdPhG2"
        "IxBSyP9LWr2vC+HAbx4CbRL/4feQOfW7QtksX4QI816neU5OA/ebic+C4Rbj8w3w"
        "K8M4pgMXit/xKJTPAgMBAAGjggMTMIIDDzCB3AYDVR0gBIHUMIHRMIHOBgRVHSAA"
        "MIHFMIHCBggrBgEFBQcCAjCBtRqBslRlbnRvIHN5c3RlbW92eSBjZXJ0aWZpa2F0"
        "IGJ5bCB2eWRhbiBwb2RsZSB6YWtvbmEgMjk3LzIwMTYgU2IuIGEgbmF2YXpueWNo"
        "IHByZWRwaXN1L1RoaXMgc3lzdGVtIGNlcnRpZmljYXRlIHdhcyBpc3N1ZWQgYWNj"
        "b3JkaW5nIHRvIExhdyBOby4gMjk3LzIwMTYgQ29sbC4gYW5kIHJlbGF0ZWQgcmVn"
        "dWxhdGlvbnMwEgYDVR0TAQH/BAgwBgEB/wIBADCBvAYIKwYBBQUHAQEEga8wgaww"
        "NwYIKwYBBQUHMAKGK2h0dHA6Ly93d3cucG9zdHNpZ251bS5jei9jcnQvcHNyb290"
        "cWNhMi5jcnQwOAYIKwYBBQUHMAKGLGh0dHA6Ly93d3cyLnBvc3RzaWdudW0uY3ov"
        "Y3J0L3Bzcm9vdHFjYTIuY3J0MDcGCCsGAQUFBzAChitodHRwOi8vcG9zdHNpZ251"
        "bS50dGMuY3ovY3J0L3Bzcm9vdHFjYTIuY3J0MA4GA1UdDwEB/wQEAwIBBjCBgwYD"
        "VR0jBHwweoAUFSmMxUVpq7izw+r+S7gx2Nzw53ahX6RdMFsxCzAJBgNVBAYTAkNa"
        "MSwwKgYDVQQKDCPEjGVza8OhIHBvxaF0YSwgcy5wLiBbScSMIDQ3MTE0OTgzXTEe"
        "MBwGA1UEAxMVUG9zdFNpZ251bSBSb290IFFDQSAyggFkMIGlBgNVHR8EgZ0wgZow"
        "MaAvoC2GK2h0dHA6Ly93d3cucG9zdHNpZ251bS5jei9jcmwvcHNyb290cWNhMi5j"
        "cmwwMqAwoC6GLGh0dHA6Ly93d3cyLnBvc3RzaWdudW0uY3ovY3JsL3Bzcm9vdHFj"
        "YTIuY3JsMDGgL6AthitodHRwOi8vcG9zdHNpZ251bS50dGMuY3ovY3JsL3Bzcm9v"
        "dHFjYTIuY3JsMB0GA1UdDgQWBBQV74k+utu5muc2rBdmW+P4DDXcNTANBgkqhkiG"
        "9w0BAQsFAAOCAQEAWeC6ksdN2XymYTDEsHwSf7H0/aXornB5BKiBrK3AnKOLAK2m"
        "sZ2EFYP2bxXpqfvoxoEuksTPLdRdE0P2KELvcmwQqeECfZJ9rC/c1OLWg56Klzml"
        "W4MVlbE2ZxzOwa1itX7jikkSD8I7dppzKl2N+74a6vZhvgig+si+38/RsPLR4kSU"
        "YGGLNTGyb+tlZNKOysXvTQkqznIjK8oGd+sOcquyLALVcQtC4of0XK6GfEZe8Mkl"
        "bKRXZu1WPA6y5er2AX380XI+z/9LPerSN2d3cvqyM/KbTNBxnEMTaq2ywIVNnOpU"
        "2z4f0JqV4kE7aQhoxYy2gIIdq9wcbbBOvn1/Vg==",
        "MIIHsDCCBZigAwIBAgICEBEwDQYJKoZIhvcNAQENBQAwZTELMAkGA1UEBhMCQ1ox"
        "FzAVBgNVBGETDk5UUkNaLTQ3MTE0OTgzMR0wGwYDVQQKDBTEjGVza8OhIHBvxaF0"
        "YSwgcy5wLjEeMBwGA1UEAxMVUG9zdFNpZ251bSBSb290IFFDQSA0MB4XDTE4MDky"
        "NzA3MzkyM1oXDTMzMDkyNzA3MzkyM1owaTELMAkGA1UEBhMCQ1oxFzAVBgNVBGET"
        "Dk5UUkNaLTQ3MTE0OTgzMR0wGwYDVQQKDBTEjGVza8OhIHBvxaF0YSwgcy5wLjEi"
        "MCAGA1UEAxMZUG9zdFNpZ251bSBRdWFsaWZpZWQgQ0EgNDCCAiIwDQYJKoZIhvcN"
        "AQEBBQADggIPADCCAgoCggIBALn4cm0aMs92PJ1iwAnlTVIu2WBzRcPSHgU0C7O3"
        "+uxKlKVXpRVOlvo3jiQUPh72sF14DZ0EaeSDihdPf2BSOgPP2O/VNKJ1wqbRW0Rj"
        "6KBhnRGzs0i5ASgw3OQGaBgstnI7lFx41r3jKgtV2ka7VwhuHlYnoITDQ9Ss26lg"
        "oANS/y2PACXZB/ojdi6u7v2GEgXTLgwvhO2L7Xy427QD/VsvXsyH/swz/tpqC/Wd"
        "Ref/Rden0xGbky6qNYL70eBfqgvrGVFEodFGa543oDunEFg6SVv4L+kdlxqeoSZ6"
        "j9iQamhOqgYe1gM9vkhGlA/1QXLQ8xhpDQP8OMVofxhxnWlJwMLzxadsW7xOmaJJ"
        "nbPok0b5RmKQ+Mw2+OMwF7sm6zZTEzGGb66dHh5Z37a2F+8/CuPNJLA6Lpjsn+9m"
        "LmZaOi8XVYmsgbAkGqIDo3fnEBYgLUpycUVHSC+pRK1v5IOBXwIXGVTLjw3SP6Cf"
        "Qw+2HJZyJscUwAxQL7acA6mJna5mkk0nh15InSou5F+9HKypm7p3iY6S+7r1XIyB"
        "ZASRZqJen5DnKQXe9I5p6BXVebAsw+Ja8HAXMVR3rdDj6iDUknzMztfvE8kymZ6D"
        "BZ2XFqDJuHudRDtyIaMpsnD3ddyO6hr9+WA/0iO86HWbiwU/yFJkFbjcB94+reDW"
        "RLSVAgMBAAGjggJkMIICYDCB1QYDVR0gBIHNMIHKMIHHBgRVHSAAMIG+MIG7Bggr"
        "BgEFBQcCAjCBrhqBq1RlbnRvIGNlcnRpZmlrYXQgcHJvIGVsZWt0cm9uaWNrb3Ug"
        "cGVjZXQgYnlsIHZ5ZGFuIHYgc291bGFkdSBzIG5hcml6ZW5pbSBFVSBjLiA5MTAv"
        "MjAxNC5UaGlzIGlzIGEgY2VydGlmaWNhdGUgZm9yIGVsZWN0cm9uaWMgc2VhbCBh"
        "Y2NvcmRpbmcgdG8gUmVndWxhdGlvbiAoRVUpIE5vIDkxMC8yMDE0LjASBgNVHRMB"
        "Af8ECDAGAQH/AgEAMHoGCCsGAQUFBwEBBG4wbDA3BggrBgEFBQcwAoYraHR0cDov"
        "L2NydC5wb3N0c2lnbnVtLmN6L2NydC9wc3Jvb3RxY2E0LmNydDAxBggrBgEFBQcw"
        "AYYlaHR0cDovL29jc3AucG9zdHNpZ251bS5jei9PQ1NQL1JRQ0E0LzAOBgNVHQ8B"
        "Af8EBAMCAQYwHwYDVR0jBBgwFoAUkxg2H6lpcFE1qk8/rI1QfiYFKQowgaUGA1Ud"
        "HwSBnTCBmjAxoC+gLYYraHR0cDovL2NybC5wb3N0c2lnbnVtLmN6L2NybC9wc3Jv"
        "b3RxY2E0LmNybDAyoDCgLoYsaHR0cDovL2NybDIucG9zdHNpZ251bS5jei9jcmwv"
        "cHNyb290cWNhNC5jcmwwMaAvoC2GK2h0dHA6Ly9jcmwucG9zdHNpZ251bS5ldS9j"
        "cmwvcHNyb290cWNhNC5jcmwwHQYDVR0OBBYEFA8ofD42ADgQUK49uCGXi/dgXGF4"
        "MA0GCSqGSIb3DQEBDQUAA4ICAQAbhhYsYpF0Fzj3iisDvJa2cWrwl846MIlgQ5sg"
        "c6b4nStKcomDZ6mmCidpPffy19JfJ/ExdLe1zNEw82Tdrje6WDww6C7Xt6DoCE+t"
        "MsrwJSg0W9irFrQDImySUQQhlFJsoAfA8PJsrHxNPkzKSWtFht+SKlSoLD+2eGUt"
        "68FNJtU03BPm+a2eTX5+aPKmaM+4u6th95ac0shlwW2T197xuVmv6Wd6pVA0vWzS"
        "7WXTGbu+zFotfYoGex6uF6f/DhP8xSRD2O3MVvlo/g3bQmUbIbdHutN8NhcRRXn3"
        "r3oYnBWAX+oOPE81Mbq0bwfteSDJzWczRV7ROdNqMm9jxq3DspHoVtXwDj1R4H0D"
        "RcYscg9kuvC74vyHyretV++pSATrd0Z4JTB73iMVxozCKancH+vbpWzgDLnrZj0P"
        "ILb8vOFOkzBkyUaMnnyQb9q6kJvdWQ4KCzALNYK1Izjo6GXXlY77rXSQ//s0ez9M"
        "3RjWfzZ/bEZTprsHZVNWf7na73KPT7Sk/KjeX0H6WGPcGJ3rm0T1OCwsIsfBZ6oc"
        "SnEe5rW1VXRI6wwow/rRFG9u0R0pJU8kF1FKtRDWtBaZTDbOJZ3oOcDK2iKuURxt"
        "4qgKhPU4eRPrPicqAGQeeKfsvKc3YJRHV2P/PrK/FT1I8Las5ktxIKxqp24jdYmH"
        "gHdaNA==",
        "MIIHsDCCBZigAwIBAgICEGswDQYJKoZIhvcNAQENBQAwZTELMAkGA1UEBhMCQ1ox"
        "FzAVBgNVBGETDk5UUkNaLTQ3MTE0OTgzMR0wGwYDVQQKDBTEjGVza8OhIHBvxaF0"
        "YSwgcy5wLjEeMBwGA1UEAxMVUG9zdFNpZ251bSBSb290IFFDQSA0MB4XDTE4MTAw"
        "MzA1MDY1M1oXDTMzMTAwMzA1MDY1M1owaTELMAkGA1UEBhMCQ1oxFzAVBgNVBGET"
        "Dk5UUkNaLTQ3MTE0OTgzMR0wGwYDVQQKDBTEjGVza8OhIHBvxaF0YSwgcy5wLjEi"
        "MCAGA1UEAxMZUG9zdFNpZ251bSBRdWFsaWZpZWQgQ0EgNTCCAiIwDQYJKoZIhvcN"
        "AQEBBQADggIPADCCAgoCggIBALdJvaq+u7OWP72i1DBwGwmEne0bxHOhavnNh1bu"
        "A9rR5L0+NOcm5dbwWH9eMgmDftAq72U/YBYNcvGL7ppNJzA6qSC794TNfoiyT5Rc"
        "jID7oFy5K6mJSCvqssuUvpfOE0Ri7jKRw71PlDeunmHIvvsXq1YmJoPK0s5AMIOJ"
        "pmTeVxHUkUn9sNazpN3KkbJFL0HZ6QoXMDBWE+3+hrU+uxm/9lDuvS5g9DFNFlwO"
        "JQNuCftZw/+DwKripJnzStAkZXmYu5j3Bb3E+uka47+EEJ9f2xPQ6zrbF0i1jW9L"
        "yxXFBfufknEqOSXZIZduLKapg+LOZprO9TzEHGaBsyLDrTJfRVc3PlDxqEZvTgdZ"
        "oqWzlXxPbMQYNF5bqCXr/b/Ykpzek3qEv9JLQ1xIcv8OhAzo2i3f4Nl1CsHVVpoe"
        "QT9WelXy+g/gj0lgsy6NU5X7PNrCTxoX4tG7Lk13YzmEOCvbwpqPaOXdpo5aoQZw"
        "rHjzmjM8F6vHYX//wrRtnPVjBLaxmBF3yvZiVMNsjCeNiR24Hmo852prVjeZB6Fa"
        "xn9mbwyWGlPs8MkD63iRz4n+infE42VvnsSusJe0tkmulEFsj/DJ+tG+OlN8gt8M"
        "afTe6Ub9mJNFt9iD/VrjGeHhdJLZKiJyDmGlQCAzQE425oQwLKH37N8pBWx/7xgS"
        "doCzAgMBAAGjggJkMIICYDCB1QYDVR0gBIHNMIHKMIHHBgRVHSAAMIG+MIG7Bggr"
        "BgEFBQcCAjCBrhqBq1RlbnRvIGNlcnRpZmlrYXQgcHJvIGVsZWt0cm9uaWNrb3Ug"
        "cGVjZXQgYnlsIHZ5ZGFuIHYgc291bGFkdSBzIG5hcml6ZW5pbSBFVSBjLiA5MTAv"
        "MjAxNC5UaGlzIGlzIGEgY2VydGlmaWNhdGUgZm9yIGVsZWN0cm9uaWMgc2VhbCBh"
        "Y2NvcmRpbmcgdG8gUmVndWxhdGlvbiAoRVUpIE5vIDkxMC8yMDE0LjASBgNVHRMB"
        "Af8ECDAGAQH/AgEAMHoGCCsGAQUFBwEBBG4wbDA3BggrBgEFBQcwAoYraHR0cDov"
        "L2NydC5wb3N0c2lnbnVtLmN6L2NydC9wc3Jvb3RxY2E0LmNydDAxBggrBgEFBQcw"
        "AYYlaHR0cDovL29jc3AucG9zdHNpZ251bS5jei9PQ1NQL1JRQ0E0LzAOBgNVHQ8B"
        "Af8EBAMCAQYwHwYDVR0jBBgwFoAUkxg2H6lpcFE1qk8/rI1QfiYFKQowgaUGA1Ud"
        "HwSBnTCBmjAxoC+gLYYraHR0cDovL2NybC5wb3N0c2lnbnVtLmN6L2NybC9wc3Jv"
        "b3RxY2E0LmNybDAyoDCgLoYsaHR0cDovL2NybDIucG9zdHNpZ251bS5jei9jcmwv"
        "cHNyb290cWNhNC5jcmwwMaAvoC2GK2h0dHA6Ly9jcmwucG9zdHNpZ251bS5ldS9j"
        "cmwvcHNyb290cWNhNC5jcmwwHQYDVR0OBBYEFDubIFJ1I6uE5L1o7GDcdEQnVpUG"
        "MA0GCSqGSIb3DQEBDQUAA4ICAQAsFo4nyLa3tmwlqvi+qWEyANr+RGPTzjMYUNOh"
        "0pV9aAwVLJbFqSNuznckWfSCai6Ch5wE7CGKe0+8ZVlomoGwbK2zXBjQ5EaWYR9r"
        "kr4LRY0AotBI14lTACgmmNq2ntI8LSa0ScQO5zoqy6D8z1eDY3WlJNM/x+W5wf3T"
        "QRE9Zu/JnKqpcp9oOIcs9RrUpiXhwYu7e92c/9Dj3fOlVeIK8BJgiKWzL83uNQ5I"
        "zdpYz/Ridu5SEf12PhOgOaCSQ63JAnpivRQo0a43kLxAq27ctynBgzSc1IJjDhI8"
        "buqlt+sA+OPpYZ3KPm8ywYv/pP1nXSa8cG4x1hz4xREGzFm+0kCaup+naKLWZzsT"
        "hyAEzlSXK90JEIf0FaYzkwUzyMVASFjiIQ2A7048aN7lbf8ZHqbLg8e8cknUM5G1"
        "d0U7twKtIckiDfolQwUmee59+ueb+iT2Z7ATcT8p9a538r4djazpN0pH406u7a7q"
        "AKiiIHl3esjEWnhEHoT+i1t1D2smaN0h7ME8Ia2ZGQx5JpGsnpZmHSbEl+ZSOOiz"
        "gu0Ii/M4Ggj1L1ykeYt+qHy7u9151PPaQXpZOzVDjtYQa37pXCNqTwA4I5JNifXS"
        "dHPOsxYZNkbcgofLnt9DWWTfmyRoq8YFQfp7RwUupbupDJrRhHlf1KMUVgRAYv5v"
        "Y5ybWQ==",
        "MIIHrTCCBZWgAwIBAgICEBMwDQYJKoZIhvcNAQENBQAwZTELMAkGA1UEBhMCQ1ox"
        "FzAVBgNVBGETDk5UUkNaLTQ3MTE0OTgzMR0wGwYDVQQKDBTEjGVza8OhIHBvxaF0"
        "YSwgcy5wLjEeMBwGA1UEAxMVUG9zdFNpZ251bSBSb290IFFDQSA0MB4XDTE4MDky"
        "NzEwMTkzNVoXDTMzMDkyNzEwMTkzNVowZjELMAkGA1UEBhMCQ1oxFzAVBgNVBGET"
        "Dk5UUkNaLTQ3MTE0OTgzMR0wGwYDVQQKDBTEjGVza8OhIHBvxaF0YSwgcy5wLjEf"
        "MB0GA1UEAxMWUG9zdFNpZ251bSBQdWJsaWMgQ0EgNDCCAiIwDQYJKoZIhvcNAQEB"
        "BQADggIPADCCAgoCggIBANJroh6wuy+PYGyVAgdlaVL3B3Vto0L22/7pobi7B6dh"
        "eZHyCsyuc+XGqzJZACZ7805iANOgahOL27yhw1KCUYH70iHAqA37iSROvxg0Tjth"
        "PejnLoDH8KF8/XGAwklOdBpNLlubJ3xvEeuBne/0TJsjc+8NfPkth+Cw4PIlZt5S"
        "q3MoXm8UwZ0dIM1W6oahrIuA2847UQAnI3+nrkCp4bMq6ygMzXFgsJtc+N/KAcDl"
        "wHXJlW02cgiPz3hl0buBuZd6seXT8iEpH1dwK9NGtYjE41NOM5wMGj86VPAvaNCr"
        "bl08g4SWOjY1wPuUTDCtzFf2b76nrj0D2ngbZ564Tiz5WQUyMfEtO3ZKYgo/sLy4"
        "MFZIwfwPRZBZQBndeu7eJYgxdPvLxkRKMpVH+E5NY7gWiVt+ZDwq8jybQWl1d+2B"
        "sEH1ongoM2DGM9ocasK7saHlfIH0cyjy3T/DKCUWa/MkwyLfp35obaRsZU6bVaep"
        "GTThzP91JTqvQ5IVDuQFV0KuM3PuBhx1bi+zOsBL8emOAZoPZu4+qw/J7fc2mftt"
        "Sb3SiiOlYnZj89h1w4HsthtCnaBA1QvOcn3XyVLOMzjVEDl0yGQukN0UyQDAhUpo"
        "s75mT9ntlJyb45v+UFzqbm4Ed/t94QsiGllMS+L1Ex6KpM7pTyDmg22174z7MvGf"
        "AgMBAAGjggJkMIICYDCB1QYDVR0gBIHNMIHKMIHHBgRVHSAAMIG+MIG7BggrBgEF"
        "BQcCAjCBrhqBq1RlbnRvIGNlcnRpZmlrYXQgcHJvIGVsZWt0cm9uaWNrb3UgcGVj"
        "ZXQgYnlsIHZ5ZGFuIHYgc291bGFkdSBzIG5hcml6ZW5pbSBFVSBjLiA5MTAvMjAx"
        "NC5UaGlzIGlzIGEgY2VydGlmaWNhdGUgZm9yIGVsZWN0cm9uaWMgc2VhbCBhY2Nv"
        "cmRpbmcgdG8gUmVndWxhdGlvbiAoRVUpIE5vIDkxMC8yMDE0LjASBgNVHRMBAf8E"
        "CDAGAQH/AgEAMHoGCCsGAQUFBwEBBG4wbDA3BggrBgEFBQcwAoYraHR0cDovL2Ny"
        "dC5wb3N0c2lnbnVtLmN6L2NydC9wc3Jvb3RxY2E0LmNydDAxBggrBgEFBQcwAYYl"
        "aHR0cDovL29jc3AucG9zdHNpZ251bS5jei9PQ1NQL1JRQ0E0LzAOBgNVHQ8BAf8E"
        "BAMCAQYwHwYDVR0jBBgwFoAUkxg2H6lpcFE1qk8/rI1QfiYFKQowgaUGA1UdHwSB"
        "nTCBmjAxoC+gLYYraHR0cDovL2NybC5wb3N0c2lnbnVtLmN6L2NybC9wc3Jvb3Rx"
        "Y2E0LmNybDAyoDCgLoYsaHR0cDovL2NybDIucG9zdHNpZ251bS5jei9jcmwvcHNy"
        "b290cWNhNC5jcmwwMaAvoC2GK2h0dHA6Ly9jcmwucG9zdHNpZ251bS5ldS9jcmwv"
        "cHNyb290cWNhNC5jcmwwHQYDVR0OBBYEFFBJWsSKYUL+uP8rOlGi8GEd4PMiMA0G"
        "CSqGSIb3DQEBDQUAA4ICAQCXgDeAMWB+gdA3Lt8ZCH5b4mCcN1/hndJy8qlYiNjn"
        "IYdGXcflXiITztrqus5usM+m3H3GUHbsvmOYPdrFkdvNf+FSsLC+z8DMbvnS0ni9"
        "cUv7zNJdFRtByZMr95Yy3k5Mu8s5STdQvfw3+j5NFnyEYuMtstavj4JQp6NI6aeo"
        "QFySWmVnxVR48g2UYZW/97oblGzFlYpWIgmm3NC+l+BRJaDuyS1zCOv3dh9sgyPL"
        "/MKeoxBnrWORAyPRAekjNu2lC6VBEGmAefBObE3KDgzQHCC2q2dMxyZKZy6YMLkQ"
        "U9LO1QURcgUQFoflBXN3+dS9UftHfB7ZJpHlpir7hNFEMbemGIpruzMS64Vyzqw1"
        "AyYNPQJ8ioMdaCsug3bxpxxv65ZLhC73HTyDMAgPB7tLoawGHycplUk+HrYg4GUx"
        "nc0RVRsD2mYSHc6Au/RT5TmqOY4cGNqDITsvn3vKp/OdJw3HLLs9lcvB9EGU0uZ2"
        "PiIJGD417apzMUy4M7Vk0MKNMkGeZipZj9kWc/OaHMLiwsZgF/RyNscwrKplSXgQ"
        "1EujcjisMCiGT/EPeRfi1TcfYZMsPySQBoKH3I2+LYrpgwRMDLCwqITFaCvCJDBH"
        "E70vZ7UAgNvvHNQatzN8EhMrZbY2N55arKD02KoeSUZhCUyuvdREKoJ5goqoyMAf"
        "+A==",
        "MIIHrTCCBZWgAwIBAgICEGwwDQYJKoZIhvcNAQENBQAwZTELMAkGA1UEBhMCQ1ox"
        "FzAVBgNVBGETDk5UUkNaLTQ3MTE0OTgzMR0wGwYDVQQKDBTEjGVza8OhIHBvxaF0"
        "YSwgcy5wLjEeMBwGA1UEAxMVUG9zdFNpZ251bSBSb290IFFDQSA0MB4XDTE4MTAw"
        "MzA2NDgwMVoXDTMzMTAwMzA2NDgwMVowZjELMAkGA1UEBhMCQ1oxFzAVBgNVBGET"
        "Dk5UUkNaLTQ3MTE0OTgzMR0wGwYDVQQKDBTEjGVza8OhIHBvxaF0YSwgcy5wLjEf"
        "MB0GA1UEAxMWUG9zdFNpZ251bSBQdWJsaWMgQ0EgNTCCAiIwDQYJKoZIhvcNAQEB"
        "BQADggIPADCCAgoCggIBAL6ElsP42nPy+ArZgdEs/vRt1eCQ5Dgp7prFynrxGjQF"
        "Il2/XKmMtNnDRDHVnJPlx6ehMO4CkSiYLmVX3x2hWsgG8FTsC5cGogk6uCrhqDso"
        "cfaRajLU22S7yf7GnsGbHsu5suYT03JlTzlsZamspj1zqmMAxERFoKKrdy7ZL9Uy"
        "N5oQ/pKO5ez/EeytkhqmnJVj0v25vq+pvL4WWOfji+LgHHOMKJOGXVJnyiCqs6kx"
        "dMKoit42DQPeD5V6j26y+myQg4T9d0VvtnVVCPhfigp1yMkuHLkOHMFwHI4WkxQz"
        "QIB1L3L93iRvuKZ2X8BTKNxA9F9K53C/GQ/pH7VObsJcp9BF9Zwfo5z4eNaQ0wta"
        "sIKo+P/aQg5lqZyPIK/ih0zp5A+bZEVWgVxEt6BAn5mXF0kbDjQkfBxMaKbZsXKu"
        "AUFKuCmOrshEZazgHRlIwqyXjEZ9iRyrs0ohf90R5mlFIZklbtjGsa2TgKnaV1Lh"
        "Zy7wH37K7t69hj6wqq12zHMIHUdns0lTwYOGrPI8yjv8bdUG/Qb7DzQ9CWpJu5QE"
        "en+EEQAnztb9l42D0cj3aYu9Vy+Ok7y5qSOoqaJqLBEdp8EQPDzVo2L/XMv17BbH"
        "tGd654bDPAoucCtCZbbspoYBUNIjN2L/fjn7JJMVO9Ojh3wohnuEuZazCfyKCWMB"
        "AgMBAAGjggJkMIICYDCB1QYDVR0gBIHNMIHKMIHHBgRVHSAAMIG+MIG7BggrBgEF"
        "BQcCAjCBrhqBq1RlbnRvIGNlcnRpZmlrYXQgcHJvIGVsZWt0cm9uaWNrb3UgcGVj"
        "ZXQgYnlsIHZ5ZGFuIHYgc291bGFkdSBzIG5hcml6ZW5pbSBFVSBjLiA5MTAvMjAx"
        "NC5UaGlzIGlzIGEgY2VydGlmaWNhdGUgZm9yIGVsZWN0cm9uaWMgc2VhbCBhY2Nv"
        "cmRpbmcgdG8gUmVndWxhdGlvbiAoRVUpIE5vIDkxMC8yMDE0LjASBgNVHRMBAf8E"
        "CDAGAQH/AgEAMHoGCCsGAQUFBwEBBG4wbDA3BggrBgEFBQcwAoYraHR0cDovL2Ny"
        "dC5wb3N0c2lnbnVtLmN6L2NydC9wc3Jvb3RxY2E0LmNydDAxBggrBgEFBQcwAYYl"
        "aHR0cDovL29jc3AucG9zdHNpZ251bS5jei9PQ1NQL1JRQ0E0LzAOBgNVHQ8BAf8E"
        "BAMCAQYwHwYDVR0jBBgwFoAUkxg2H6lpcFE1qk8/rI1QfiYFKQowgaUGA1UdHwSB"
        "nTCBmjAxoC+gLYYraHR0cDovL2NybC5wb3N0c2lnbnVtLmN6L2NybC9wc3Jvb3Rx"
        "Y2E0LmNybDAyoDCgLoYsaHR0cDovL2NybDIucG9zdHNpZ251bS5jei9jcmwvcHNy"
        "b290cWNhNC5jcmwwMaAvoC2GK2h0dHA6Ly9jcmwucG9zdHNpZ251bS5ldS9jcmwv"
        "cHNyb290cWNhNC5jcmwwHQYDVR0OBBYEFOPOMVHzTJH1fbcFibF40KMKxkOZMA0G"
        "CSqGSIb3DQEBDQUAA4ICAQAmFNtdTcBzqe+IFWNXvKldM+SWsXDLIOo2gUTBbVgi"
        "cipgjlcuFSUKXBhNMW2vdVrfKZG0AXzR3SBt72KtoF8khafwHhoww8Bkwo5CKqMf"
        "8A0zcJ5dqav49MG/ioKgVoeC4TvO++AKjQMrKfJz9xPFNktG5t7ongWmUppupDSf"
        "a4tnKV/6nqTrOpZOyXJgJCy4dNkv/Aplu+EfFw2/mOEVqtxtogbN7nQ+ZjsNpWX1"
        "/RZNlwB0JvkqW/yCNsnwjxzbbNZZGj47cUS8Zz9RVdoUyMWY8JyHTPtHX/fA15vc"
        "MbbV9qaXymcnGgVXWSHNKLT42dkLMnuEHeCSJoFxfTgC3iyRsBGSE04deZb9sWxa"
        "vQqhI23NR4RB4N1TKBBMjApIB7r6oj+XphAWC+M1AorOtv49/dtJCAIRJzdPUfxh"
        "NHwGIgGqiW6GNq/HuYGF53CX9RVA38azY8kYoPrAFs6RgjjzH7wtIEMlJsMskiMA"
        "JBH+Hc5K41eGDedXFiRdJ+yQEmM8Bk3kqpXke+Crnr8IVLK+I1M8/jcYKanmInvf"
        "GJQKPScUk5aipwf17eeh/uG1+rJ7C6sqqiPlIWVSjtTiaBBpyZOuWeZXeKBSHHZG"
        "1VmBf4sAyzWoxlUsHsqpQ0YUieBYPsFuxz+v4sqVJH+ScS3pCBcgE/2DxrqYBVo3"
        "Cg=="
    ]

    def __init__(self, cmd_params):

        server = RegisterUpstream.get_service(cmd_params['upstream'], token=cmd_params['token'],
                                              signer=cmd_params['signer'])
        if server is None:
            logging.error("No upstream server configuration created")
            exit(-1)

        if cmd_params['register']:
            self.create_csr = True
        else:
            self.create_csr = False

        self.general_cas = []

        # we call the super() constructor to initialize the 'self.signer' object
        super(CryptoPostSignum, self).__init__(server)

    def _read_static_certs(self):
        # first we read ca_certs from the array
        for new_cert in CryptoPostSignum.ca_certs:
            # we got a cert
            cert = x509.load_der_x509_certificate(base64.b64decode(new_cert), default_backend())
            subject_list = []
            subject_cn = ""
            for attribute in cert.subject:
                oid_in = attribute.oid
                # dot = oid_in.dotted_string
                # noinspection PyProtectedMember
                oid_name = oid_in._name
                val = attribute.value
                subject_list.append('%s: %s' % (oid_name, val))
                if oid_name.lower() == "commonname":
                    subject_cn = val
            subject_list.sort()
            subject = ', '.join(subject_list)
            issuer_list = []
            for attribute in cert.issuer:
                oid_in = attribute.oid
                # dot = oid_in.dotted_string
                # noinspection PyProtectedMember
                oid_name = oid_in._name
                val = attribute.value
                issuer_list.append('%s: %s' % (oid_name, val))
            issuer_list.sort()
            issuer = ', '.join(issuer_list)
            ext = cert.extensions.get_extension_for_oid(ExtensionOID.BASIC_CONSTRAINTS)
            if ext and ext.value and ext.value.ca:
                logging.info("New CA certificate from pre-defined list: %s" % subject_cn)
                # this is a CA, we store it in card CA list
                self.general_cas.append({
                    'name': subject,
                    'issuer': issuer,
                    'cert': base64.standard_b64encode(base64.b64decode(new_cert))
                })
            else:
                logging.info("New user certificate from pre-defined list: %s" % subject_cn)

    def init(self, session, config=None):
        """
        As in the abstract class
        :param session:
        :param config:
        """
        was_down = self.server.downtime(session)

        if was_down:
            # we refresh the crypto storage
            self.storage.initialize()
            self._read_static_certs()
            self._read_certificates(session)
            self.server.set_uptime()
        pass

    def aliases(self):
        """
        As in the abstract class
        """
        pass

    def chain(self, alias, sign_alg=0):
        """
        As in the abstract class

        :param alias:
        :param sign_alg:
        :return:
        """
        reader = self.get_token(alias)
        if len(reader) != 1:
            if len(reader) == 0:
                # we haven't found the name
                response_data = Constant.CMD_READER_NOT_FOUND
            else:
                # the name is not unique
                response_data = Constant.CMD_VAGUE_NAME
        else:
            # and we need to get the certificate chain
            response_data = self.get_certs(reader.reader)
        return response_data

    def sign(self, session, alias, fingerprint, password=None, hash_alg=None, sign_alg=None):
        """
        # signing consists of the following APDUs
        # apdu=00A4000C023F00\\&reset=1  - card reset
        # apdu=00A4010C020604           - select of the PIN file
        # apdu=002000810733323837313935  - PIN check  - 3287295
        # apdu=00 22 41 AA 04 89 02 14 30   . 41 - MSE:SET, AA - hash,
        #                      89021430 = sha-256, 89021410 = sha-1
        # apdu=00 22 41 B6 0A 84(SDO ref) 03 800400 8903 13 23 30 -
        #                      8903132330 - rsa-sha-256, 8903132310 = rsa-sha1
        # apdu=00 2A 90 A0 22 90 20 D0 6C EF 8B 4A DA 05 75 9E 1A 2C 75 23 64 15 08 DC BA 5C B6 E7 C3
        # 3F E8 A2 C6 43 C0 1B C4 CE 34

        :param session:
        :param alias:
        :param fingerprint:
        :param password:
        :param hash_alg:
        :param sign_alg:
        :return:
        """

        readers = self.get_token(alias)
        if len(readers) != 1:
            if len(readers) == 0:
                # we haven't found the name
                response_data = Constant.CMD_READER_NOT_FOUND
            else:
                # the name is not unique
                response_data = Constant.CMD_VAGUE_NAME
            return response_data

        reader = readers[0]  # type: TokenRecord

        # we have a reader, let's do the signing
        if len(fingerprint) == 40:
            sha_id = "3021300906052B0E03021A05000414"  # sha1
        elif len(fingerprint) == 64:
            sha_id = "3031300D060960864801650304020105000420"  # sha256
        elif len(fingerprint) == 96:
            sha_id = "3041300D060960864801650304020205000430"  # sha384
        elif len(fingerprint) == 128:
            sha_id = "3041300D060960864801650304020205000440"  # sha512
        else:
            response_data = Constant.CMD_READER_WRONG_DATA
            return response_data

        # PIN
        # if the password is set
        pin_ok = True
        if password is not None:
            encoded_password = binascii.b2a_hex(password.encode('ascii')).decode('ascii')  # 3287195
            if (reader.pin is not None) and (reader.pin == encoded_password):
                logging.error("Blocked repeated use of incorrect PIN to reader %s"
                             % reader.reader)
                pin_ok = False
            else:
                # select FILE
                self.server.cmd(session, '00A408000614009001200200', reader.reader)
                # enter PIN  e.g. 8 digit 12345678: 00200010083132333435363738
                response_all = self.server.cmd(session,
                                               '00200010%02X%s' % (len(password), encoded_password),
                                               reader.reader)
                if (response_all is not None) and (len(response_all) > 0) \
                        and response_all[0][-4:-1] == "63C":
                    # there is a problem with PIN - the counter was decreased
                    logging.error("Incorrect PIN to reader %s, remaining tries %s" %
                                 (reader.reader, response_all[0][-1:]))
                    reader.pin = encoded_password
                elif (response_all is not None) and (len(response_all) > 0) \
                        and response_all[0][-4:] == "9000":
                    reader.pin = None
                elif (response_all is None) or len(response_all) < 1:
                    logging.error("Error with PIN verification at reader %s - no details available" %
                                 reader.reader)
                    pin_ok = False
                else:
                    logging.error("Error with PIN verification at reader %s, the error code is %s" %
                                 (reader.reader, response_all[0]))
                    pin_ok = False
        if not pin_ok:
            response_data = Constant.CMD_READER_WRONG_PIN
        else:
            # let's do signing

            # restore security context
            self.server.cmd(session, '0022F303', reader.reader)
            # set security context
            response_all = self.server.cmd(session, '0022F1B80383010E', reader.reader)

            if response_all[0][-4:] == "9000":
                # context set up - do the signature

                # we got 512 characters
                data_in = '0001' + '{:F>{width}}'.format(sha_id + fingerprint, width=(256 + 252))
                data_in_1 = data_in[:256]
                data_in_2 = data_in[256:]

                # we need to create a complete blob with padding for the hash value
                padding1 = "8100" + data_in_1
                padding2 = "80" + data_in_2

                # first half of the data
                self.server.cmd(session, '102A8086%s00' % padding1, reader.reader)
                # second half of the data
                response_all = self.server.cmd(session, '102A8086%s00' % padding2, reader.reader)

                if response_all[0][-4:] != "9000":
                    logging.error("Signing unsuccessful reader %s, error code %s" %
                                  (reader.reader, response_all[0][-4:]))
                    response_data = response_all[0][-4:]
                else:
                    response_data = response_all[0][0:-4]
            else:
                response_data = response_all[0][-4:]
        return response_data

    def apdu(self, session, token, command):
        """
        A native command provided by the cryptographic token
        :param session: upstream connection TCP/HTTP or None
        :param token: identification of the cryptographic token, e.g., smartcard
        :type token: str
        :param command: the actual command - hex encoded
        :type command: str
        :return:
        """

        response_all = self.server.cmd(session, command, token)
        if len(response_all) > 0:
            response_data = response_all[0]
        else:
            response_data = Constant.CMD_INTERNAL_ERROR
        return response_data

    def reset(self, session, token):
        """
        As in the abstract class
        :param session:
        :param token:
        :return:
        """
        response_all = self.server.cmd(session, None, token, 1)
        if len(response_all) > 0:
            response_data = response_all[0]
        else:
            response_data = Constant.CMD_INTERNAL_ERROR

        return response_data

    # #########################################################################
    #  Internal methods
    # #########################################################################

    def _read_certificates(self, session):

        # let's now get a list of card readers and ATRs
        response_data = self.server.inventory(session)

        for each_line in response_data:
            logging.info("Found a new chip '%s'" % each_line)
            items = [each_line]  # .split()  # TODO this doesn't sound good
            # we found a smart-card
            self.storage.certificates[items[0]] = ReaderRecord()
            self.storage.certificates[items[0]].subject = ""
            #     # we need to get the certificates

        for reader in self.storage.certificates.keys():

            ##########################
            # a new approach to derive the file ID for the private key
            ##########################
            error = False
            response_all = self.server.cmd(session, '00A4040010A0000000770103000610000000000002', reader)
            if len(response_all) < 1 or response_all[0][-4:] != "9000":
                error = True
            response_all = self.server.cmd(session, '00A408000410001003', reader)
            if len(response_all) < 1 or response_all[0][-4:] != "9000":
                error = True
            response_all = self.server.cmd(session, '00B0000010', reader)  # some kind of card ID
            if len(response_all) < 1 or response_all[0][-4:] != "9000":
                error = True

            # select certificate store
            response_all = self.server.cmd(session, '00A408000614009001200200', reader)
            if len(response_all) < 1 or response_all[0][-4:] != "9000":
                error = True

            # the response defines the store's content
            # 6F35 - wrapper
            # 8002 - 0525 - user certificate
            # 8203 - 010000
            # 8302 - 2002
            # 8501 - 01
            # 8609 - 001010FFFF10FFFFFF

            # cert_file_id = 1
            # not_found = True

            # first let's get the certificate length
            response_all = self.server.cmd(session, '00B0000004', reader)
            if len(response_all) < 1 or response_all[0][-4:] != "9000":
                # error = True
                logging.error("Terminated processing of card %s due to an error" % reader['name'])
                continue

            prefix = int(response_all[0][2])
            if prefix < 8:
                length = int(response_all[0][2:4], 16)
            elif response_all[0][3] == '1':
                length = int(response_all[0][4:6], 16)
            else:
                length = int(response_all[0][4:8], 16)

            certificate = response_all[0][:-4]
            length_read = 4
            length += 4
            while length_read < length and not error:
                to_read = length - length_read
                if to_read > 100:
                    to_read = 100
                response_all = self.server.cmd(session, '00B0%04X%02X' % (length_read, to_read), reader)  # a folder
                # print(response_all[0])
                if len(response_all) < 1 or response_all[0][-4:] != "9000":
                    error = True
                else:
                    certificate += response_all[0][:-4]
                    length_read += (len(response_all[0]) - 4) / 2

            # we have a user certificate
            new_item = True
            new_cert = certificate
            ##########################
            ##########################

            latest_cert_time = 0
            self.storage.card_cas[reader] = []
            self.server.cmd(session, '00A40004023F0000', reader)

            # certificate_id = 1
            end_subject = ""
            end_issuer = ""

            subject_cn = None
            while new_item:
                new_item = False
                # we got a cert
                cert = x509.load_der_x509_certificate(binascii.a2b_hex(new_cert), default_backend())
                subject_list = []
                subject_cn = ""
                for attribute in cert.subject:
                    oid_in = attribute.oid
                    # dot = oid_in.dotted_string
                    # noinspection PyProtectedMember
                    oid_name = oid_in._name
                    val = attribute.value
                    subject_list.append('%s: %s' % (oid_name, val))
                    if oid_name.lower() == "commonname":
                        subject_cn = val
                subject_list.sort()
                subject = ', '.join(subject_list)
                issuer_list = []
                for attribute in cert.issuer:
                    oid_in = attribute.oid
                    # dot = oid_in.dotted_string
                    # noinspection PyProtectedMember
                    oid_name = oid_in._name
                    val = attribute.value
                    issuer_list.append('%s: %s' % (oid_name, val))
                issuer_list.sort()
                issuer = ', '.join(issuer_list)
                ext = None
                # noinspection PyBroadException
                try:
                    ext = cert.extensions.get_extension_for_oid(ExtensionOID.BASIC_CONSTRAINTS)
                except Exception:
                    pass
                if ext and ext.value and ext.value.ca:
                    logging.debug("New CA certificate from reader %s: %s" % (reader, subject_cn))
                    # this is a CA, we store it in card CA list
                    _cas = CertificateRecord()
                    _cas.name = subject
                    _cas.issuer = issuer
                    _cas.cert = base64.standard_b64encode(binascii.a2b_hex(new_cert))
                    self.storage.card_cas[reader].append(_cas)
                else:
                    logging.info("New user certificate from reader %s: %s" % (reader, subject_cn))
                    # it's an end-user certificate
                    issued_at = Constant.unix_time(cert.not_valid_before)
                    if issued_at > latest_cert_time:
                        self.storage.certificates[reader].cert = \
                            base64.standard_b64encode(binascii.a2b_hex(new_cert))
                        end_issuer = issuer
                        end_subject = subject
                    else:
                        # we will only take the latest certificate - if there are more end-user certs
                        pass

            # this is the end of reading certificates from smart card - we now need to create a chain
            # and extract the subject from the end-user cert
            if end_subject == "" or end_issuer == "":
                logging.warning("No end-user certificate found on this smart card %s" % reader)
            else:
                # create a link from name to smart card
                _token = TokenRecord()
                _token.name = end_subject
                _token.short_name = subject_cn
                _token.reader = reader
                self.storage.cert_names.append(_token)
                # we will try to find it with the first signature ...  end_cert_id})
                # let's create a chain
                root = False
                chain = []
                while not root:
                    next_found = False
                    for ca_cert in self.general_cas:
                        if ca_cert['name'] == end_issuer:
                            next_found = True
                            chain.append(ca_cert)
                            end_issuer = ca_cert['issuer']
                            if ca_cert['name'] == ca_cert['issuer']:
                                root = True
                            break
                    if not next_found:
                        break
                if len(chain) < 1:
                    logging.error("No certificate found for %s" % end_subject)
                else:
                    self.storage.certificates[reader].chain = chain

        pass

    def _update_file_id(self, reader, file_id):
        """
        If we find a correct file_id for the user's private key, we set it in the cert_names list
        :param reader: a copy of one of the items retrieved from cert_names
        :type reader: TokenRecord
        :param file_id: an integer - the new file_id
        :return: None
        """
        new_cert_names = []
        for one_name in self.storage.cert_names:  # type: TokenRecord
            if reader.name == one_name.name:
                one_name.file_id = file_id
            new_cert_names.append(one_name)
        self.storage.cert_names = new_cert_names
