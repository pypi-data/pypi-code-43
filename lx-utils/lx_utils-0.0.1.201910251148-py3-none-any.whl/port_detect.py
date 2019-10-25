import telnetlib


async def is_port_open(ip, port) -> bool:
    is_open = False
    try:
        tn = telnetlib.Telnet(ip, port, timeout=2)
        is_open = True
        tn.close()
    except:
        pass

    return is_open
