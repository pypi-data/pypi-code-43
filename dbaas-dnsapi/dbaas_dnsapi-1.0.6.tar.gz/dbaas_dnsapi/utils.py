# -*- coding: utf-8 -*-

from models import PlanAttr
from .models import HOST
from .models import DatabaseInfraDNSList


def add_dns_record(databaseinfra, name, ip, type, is_database):
        name, domain = get_dns_name_domain(
            databaseinfra, name, type, is_database)

        records = DatabaseInfraDNSList.objects.filter(
            databaseinfra=databaseinfra.id,
            name=name,
            domain=domain,
            ip=ip,
            type=type).count()

        if records == 0:
            databaseinfradnslist = DatabaseInfraDNSList(
                databaseinfra=databaseinfra.id,
                name=name,
                domain=domain,
                ip=ip,
                type=type)
            databaseinfradnslist.save()

        dnsname = '%s.%s' % (name, domain)
        return dnsname


def get_dns_name_domain(databaseinfra, name, type, is_database):
    planattr = PlanAttr.objects.get(dbaas_plan=databaseinfra.plan)
    database_domain = planattr.dnsapi_database_domain
    database_sufix = planattr.dnsapi_database_sufix
    if not is_database:
        database_domain = planattr.dnsapi_secondary_database_domain or database_domain
        database_sufix = planattr.dnsapi_secondary_database_sufix or database_sufix
    sufix = ''
    if database_sufix:
        sufix = '.' + database_sufix
    if type == HOST:
        domain = planattr.dnsapi_vm_domain
    else:
        domain = database_domain
        name += sufix
    return name, domain
