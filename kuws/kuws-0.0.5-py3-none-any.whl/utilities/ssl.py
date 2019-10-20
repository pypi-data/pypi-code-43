"""A library of useful SSL lookup tools, including expiry checking etc.

Functions
---------
check_ssl_expiry : str|None
    Allows you to check the SSL expiry for a FQDN;
    More specifically it will return the notAfter 
    for the SSL cert associated with the FQDN.

Examples
--------
```
>> from kuws.utilities.ssl import check_ssl_expiry

>> print(check_ssl_expiry('kieranwood.ca')) # prints: 'Host: kieranwood.ca will expire on 2020-09-26 22:40:51'
```

"""

# Internal Dependencies
import ssl, socket
from datetime import datetime

# External Dependencies
import OpenSSL

def check_ssl_expiry(hostname, print_result=False):
    """Allows you to check the SSL expiry for a FQDN;
    More specifically it will return the notAfter for the SSL cert associated with the FQDN.

    Arguments
    ---------
    hostname : str
        A string of a FQDN (root URL with no protocol) for example 'kieranwood.ca'.
    
    print_result : bool
        If true then the value will be printed in a human readable format.

    Returns
    -------
    str:
        A the expiry of the domain name in YYYY-MM-DD HH:MM:SS format
        
    Example
    -------
    ```
    >> from kuws.utilities.ssl import check_ssl_expiry

    >> print(check_ssl_expiry('kieranwood.ca')) # prints: 'Host: kieranwood.ca will expire on 2020-09-26 22:40:51'
    ```

    """
    try:
        cert=ssl.get_server_certificate((hostname, 443))
        x509 = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, cert)
        expiry_date = str(datetime.strptime(x509.get_notAfter().decode('ascii'), '%Y%m%d%H%M%SZ'))
    except Exception as error:
        print(f"While checking ssl expiry on {hostname} \nScript encountered an error: {error}")
        return # Bail out of function
    
    if print_result:
        print(f"Host: {hostname} will expire on {expiry_date}")

    return expiry_date
