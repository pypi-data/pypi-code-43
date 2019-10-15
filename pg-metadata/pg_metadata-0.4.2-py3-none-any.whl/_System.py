#!/usr/bin/python
# -*- coding: utf-8 -*-

SEP = chr(10)

def ParseACL(acl_value, owner_name):
    acl_value = acl_value or []
    result = {}

    for acl in acl_value:
        spl = acl.split("=")
        if len(spl) != 2:
            continue

        role_name = spl[0].strip()
        if role_name == "":
            role_name = "public"

        result[role_name] = {
            "is_grant" : True,
            "types" : []
        }

        grants = spl[1].replace("/%s" % (owner_name), "").strip()
        if grants.strip() == "":
            result.get(role_name).get("types").append("ALL")
        elif grants == "U":
            result.get(role_name).get("types").append("USAGE")
        elif grants == "arwdDxt":
            result.get(role_name).get("types").append("ALL")
        elif grants == "rwU":
            result.get(role_name).get("types").append("ALL")
        elif grants == "X":
            result.get(role_name).get("types").append("EXECUTE")
        else:
            if grants.find("r") >= 0:
                result.get(role_name).get("types").append("SELECT")
            if grants.find("a") >= 0:
                result.get(role_name).get("types").append("INSERT")
            if grants.find("w") >= 0:
                result.get(role_name).get("types").append("UPDATE")
            if grants.find("d") >= 0:
                result.get(role_name).get("types").append("DELETE")
            if grants.find("D") >= 0:
                result.get(role_name).get("types").append("TRUNCATE")
            if grants.find("x") >= 0:
                result.get(role_name).get("types").append("REFERENCES")
            if grants.find("t") >= 0:
                result.get(role_name).get("types").append("TRIGGER")

    if "public" not in result.keys():
        result["public"] = {
            "is_grant" : False,
            "types" : ["ALL"]
        }

    if owner_name not in result.keys():
        result[owner_name] = {
            "is_grant" : True,
            "types" : ["ALL"]
        }

    return result
