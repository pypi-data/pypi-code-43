import logging

logger = logging.getLogger(__name__)

ORGANIZATION_KEYS = ["org.name", "org-name", "orgname", "organization name", "organization name", "organisation",
                     "organization", "owner.name", "owner-name", "owner name", "owner",
                     "registrant organization",
                     "maintainer", "mnt-by", "name",
                     "registrant name", "registrar name", "registrar", "registrant"]

NETRANGE_KEYS = ["netrange", "inetnum", "inet6num"]
TLD_CHARSET = 'arpbthovieclgdumynsfkzxqwj-1432907865'


def whois(query):
    from easilyb.commands import run_command_ex1
    from easilyb.validators import validate_ip, validate_domain, validate_charset
    if not validate_ip(query) and not validate_domain(query) and not validate_charset(query, TLD_CHARSET):
        raise ValueError("Query is not an IP address nor a domain")
    ret_code, output = run_command_ex1(["whois", query])
    output = output.decode(errors="replace")
    output_parsed = _parse_whois_output(output)
    org = _find_organization(output_parsed)
    if org == '': org = None
    netrange = _find_netrange(output_parsed)
    if netrange == '': netrange = None
    emails = _find_emails(output)
    return org, netrange, emails, output


def cymru_whois(ip):
    from easilyb.commands import run_command_ex1
    from easilyb.validators import validate_ip
    if not validate_ip(ip):
        raise ValueError("Param is not an IP address")
    ret_code, output = run_command_ex1(["whois", "-h", "whois.cymru.com", "-v " + ip])
    keys = list()
    for l in output.decode(errors="replace").splitlines():
        if ip in l:
            values = [v.strip() for v in l.split('|')]
            ret = {keys[i]:values[i] for i in range(min(len(keys), len(values)))}
            for k in ['AS', 'BGP Prefix', 'AS Name']:
                if ret[k] == 'NA':
                    ret[k] = None
            if ret['CC'] == '':
                ret['CC'] = None
            return ret
        elif "BGP Prefix" in l:
            keys = [k.strip() for k in l.split('|')]
    return None


def _find_organization(output_parsed):
    return _find_keys_value(output_parsed, ORGANIZATION_KEYS)


def _find_netrange(output_parsed):
    return _find_keys_value(output_parsed, NETRANGE_KEYS)


def _find_emails(output):
    import re
    finds = []
    for line in output.splitlines():
        match = re.findall(r'[\w\.-]+@[\w\.-]+', line)
        if isinstance(match, list):
            finds.extend(match)
    return finds


def _parse_whois_output(output):
    ret = list()
    for l in output.splitlines():
        if ':' in l:
            splits = l.split(':')
            key, value = splits[0].strip(), (':'.join(splits[1:])).strip()
            ret.append((key, value))
    return ret


def _find_keys_value(output_parsed, keys):
    for key in keys:
        for k, v in output_parsed:
            if k.lower() == key and len(v) > 0:
                return v
    return None
