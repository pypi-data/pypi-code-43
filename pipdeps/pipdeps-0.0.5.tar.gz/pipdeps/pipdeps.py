# pylint: disable=too-many-lines
"""
pipdeps
"""
import argparse
import collections
import itertools
import json
import os
import platform
import pprint
import re
import subprocess
import sys
import tarfile
import tempfile
import urllib2
import zipfile
import wheel.metadata

import tabulate
import packaging.specifiers
import packaging.version
import pip._internal.utils.misc

# https://www.python.org/dev/peps/pep-0508/#environment-markers
PY_VER = ".".join(map(str, sys.version_info[:2]))
SYS_PLAT = sys.platform
PLAT_PY_IMPL = platform.python_implementation()

SBoarder = collections.namedtuple("SBoarder", ["boarders", "extrem", "extrem_op"])


def arg_parse():
    """
    argument parser
    """
    parser = argparse.ArgumentParser(
        description="Pipdeps shows/upgrades outdated packages with respect to existing \
                     dependencies."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-l', '--list',
                       action='store_true',
                       help="show upgradeable packages and versions")
    group.add_argument('-u', '--upgrade',
                       action='store_true',
                       help="upgrade upgradeable packages")
    group.add_argument('-s', '--show',
                       nargs='*',
                       help="show detailed info about upgradeable packages")
    return parser.parse_args()

def upgrade_package(data):
    """
    pip install --upgrade "<package>==<versions>"
    """
    if not data:
        return
    to_upgrade = []
    for package, version in data:
        to_upgrade.append("%s==%s" % (package, version))
    subprocess.check_call(
        ["pip", "install", "--upgrade"] + to_upgrade,
        stderr=subprocess.STDOUT
    )

def get_json(url):
    """
    Return url json
    """
    return json.load(urllib2.urlopen(urllib2.Request(url)))

def file_download(url):
    """
    Download file from url as temporary file
    It returns file object
    """
    tmp_file = tempfile.NamedTemporaryFile(delete=False)
    rfile = urllib2.urlopen(url)
    with tmp_file as output:
        output.write(rfile.read())
    return tmp_file

def merge_two_dicts(in_x, in_y):
    """
    Return merge of two dictionaries
    """
    out = in_x.copy()
    out.update(in_y)
    return out

def is_version(version):
    """
    Return true if version satisfy regex, otherwise return false
    """
    if re.compile(r'^(\d+) \. (\d+) (\. (\d+))? (\. (\d+))?$', re.VERBOSE).search(version) or \
       re.compile(r'^(\d+) \. (\d+) (\. (\d+))? (rc(\d+))?$', re.VERBOSE).search(version):
        return True
    return False

def is_in_specifiers(version, specifiers):
    """
    Return true if version satisfy specifiers, otherwise return false
    """
    if not specifiers:
        return True
    elif version is None:
        return True
    else:
        # https://github.com/pypa/packaging/pull/92
        ver = packaging.version.LegacyVersion(version)
        specifiers = [
            packaging.specifiers.LegacySpecifier(s.strip()) for s in specifiers if s.strip()]
    return all(s.contains(ver) for s in specifiers)

def is_in_conditions(condition):
    """
    Return true if condition satisfy sys_platform and python_version and
    platform_python_implementation, otherwise return false
    """
    if not condition:
        return True
    # pylint: disable=eval-used
    return eval(
        condition.replace("sys_platform", '"%s"' % SYS_PLAT) \
                 .replace("python_version", '"%s"' % PY_VER) \
                 .replace("platform_python_implementation", '"%s"' % PLAT_PY_IMPL))

def is_in_extra(extra, req_extra):
    """
    Return true if extra satisfy, otherwise return false
    """
    if extra is None or extra in req_extra:
        return True
    return False

# pylint: disable=too-many-branches
def specifier_boarders(specifiers):
    """
    Return specifier boarders, equals and notequals
    """
    left = SBoarder([s for s in specifiers if s.operator in ['>', '>=']], None, None)
    right = SBoarder([s for s in specifiers if s.operator in ['<', '<=']], None, None)
    if left.boarders:
        left = left._replace(extrem=sorted([s.version for s in left.boarders],
                                           key=packaging.specifiers.LegacyVersion,
                                           reverse=True)[0])
        left = left._replace(extrem_op=[s.operator for s in left.boarders \
                                        if s.version == left.extrem])
        if '>' in left.extrem_op:
            left = left._replace(extrem_op='>')
        else:
            left = left._replace(extrem_op='>=')
    if right.boarders:
        right = right._replace(extrem=sorted([s.version for s in right.boarders],
                                             key=packaging.specifiers.LegacyVersion)[0])
        right = right._replace(extrem_op=[s.operator for s in right.boarders \
                                          if s.version == right.extrem])
        if '<' in right.extrem_op:
            right = right._replace(extrem_op='<')
        else:
            right = right._replace(extrem_op='<=')
    if left.boarders and right.boarders:
        if packaging.version.LegacyVersion(left.extrem) > \
           packaging.version.LegacyVersion(right.extrem):
            left, right = None, None
        elif packaging.version.LegacyVersion(left.extrem) == \
             packaging.version.LegacyVersion(right.extrem):
            if left.extrem_op in ['>='] and right.extrem_op in ['<=']:
                left = left._replace(extrem_op='==')
                right = right._replace(boarders=None)
            else:
                left, right = None, None
    equals = [s for s in specifiers if s.operator in ['==']]
    if equals:
        cmp_v = list(set([s.version for s in equals]))[0]
        if all([packaging.version.LegacyVersion(cmp_v) == packaging.version.LegacyVersion(item) \
               for item in list(set([s.version for s in equals]))]):
            equals = cmp_v
        else:
            equals = None
    notequals = [s for s in specifiers if s.operator in ['!=']]
    notequals = list(set([s.version for s in notequals]))
    return left, right, equals, notequals

def specifiers_intersection(specifiers):
    """
    Return intersection of specifiers, otherwise return None
    """
    if not specifiers:
        return []
    specifiers = [packaging.specifiers.LegacySpecifier(s.strip()) for s in specifiers if s.strip()]
    left, right, equals, notequals = specifier_boarders(specifiers)
    if (left is None and right is None) or equals is None:
        return None
    boarders = []
    for item in [left, right]:
        if item.boarders:
            boarders.append("%s%s" % (item.extrem_op, item.extrem))
    if boarders and notequals:
        for item in notequals:
            if is_in_specifiers(item, boarders):
                boarders.append("!=%s" % item)
    elif not boarders and notequals:
        for item in notequals:
            boarders.append("!=%s" % item)
    if boarders and equals:
        if not is_in_specifiers(equals, boarders):
            return None
        boarders = ["==%s" % equals]
    elif not boarders and equals:
        boarders = ["==%s" % equals]
    return boarders

def select_upkgs(data, rkey):
    """
    Return data packages having requested key
    """
    result = []
    for pkg, pkg_data in data.iteritems():
        if rkey in pkg_data.keys():
            result.append(pkg)
    return result

def print_list(data):
    """
    Print upgradeable versions
    """
    upkgs = select_upkgs(data, 'upgradeable_version')
    if not upkgs:
        print "There is nothing to upgrade."
        return 0
    tab_data = []
    for pkg in sorted(upkgs):
        tab_data.append([pkg, data[pkg]['installed_version'], data[pkg]['upgradeable_version']])
    print tabulate.tabulate(
        tab_data,
        ['package', 'installed_version', 'upgradeable_version']
    )
    return 1

def write_metadata(tmp_file):
    """
    Write package metadata
    """
    try:
        tar_file = tarfile.open(tmp_file.name, 'r')
        for member in tar_file.getmembers():
            if 'requires.txt' in member.name:
                with open('/tmp/requires.txt', 'w') as tmpf:
                    tmpf.write(tar_file.extractfile(member).read())
            if 'PKG-INFO' in member.name:
                with open('/tmp/PKG-INFO', 'w') as tmpf:
                    tmpf.write(tar_file.extractfile(member).read())
    except tarfile.ReadError:
        zip_file = zipfile.ZipFile(tmp_file.name, 'r')
        for member in zip_file.namelist():
            if 'requires.txt' in member:
                with open('/tmp/requires.txt', 'w') as tmpf:
                    tmpf.write(zip_file.read(member))
            if 'PKG-INFO' in member:
                with open('/tmp/PKG-INFO', 'w') as tmpf:
                    tmpf.write(zip_file.read(member))

def get_metadata(package, version):
    """
    Return package metadata
    """
    metadata = None
    for item in get_json("https://pypi.python.org/pypi/%s/%s/json" % (package, version,)) \
        ['releases'][version]:
        if item['packagetype'] == 'sdist':
            tmp_file = file_download(item['url'])
            write_metadata(tmp_file)
            if os.path.isfile('/tmp/PKG-INFO'):
                metadata = [
                    line.decode('utf-8') \
                    for line in wheel.metadata.pkginfo_to_metadata('/tmp', '/tmp/PKG-INFO') \
                    .as_string().splitlines()]
            try:
                os.unlink('/tmp/requires.txt')
            except OSError:
                pass
            try:
                os.unlink('/tmp/PKG-INFO')
            except OSError:
                pass
            os.unlink(tmp_file.name)
            if metadata:
                break
        elif item['packagetype'] == 'bdist_wheel':
            tmp_file = file_download(item['url'])
            zip_file = zipfile.ZipFile(tmp_file.name, 'r')
            for member in zip_file.namelist():
                if 'METADATA' in member:
                    metadata = [line.decode('utf-8') for line in zip_file.read(member).splitlines()]
            os.unlink(tmp_file.name)
            break
    return metadata

def parse_metadata(metadata, extra):
    """
    Return dependencies parsed from metadata
    """
    if metadata is None:
        return None
    for line in metadata:
        if 'Metadata-Version' in line.decode('utf-8'):
            metadata_version = line.replace('Metadata-Version:', '').strip()
            break
    arr = []
    if metadata_version and \
       packaging.version.Version(metadata_version) >= packaging.version.Version('2.0'):
        arr = []
        lines = [line.replace('Requires-Dist:', '').strip() \
                 for line in metadata if re.search(r'^Requires-Dist:', line)]
        for line in lines:
            data = pkginfo(str(line), req_extra=extra, repair=True)
            if data:
                arr.append(pkginfo(str(line), req_extra=extra, repair=True))
    return arr

def get_pkg_data():
    """
    Return package data
    """
    packages_data = {}
    # pylint: disable=protected-access
    for pkg in pip._internal.utils.misc.get_installed_distributions():
        pkg_name, pkg_ver, _pkg_extra = pkginfo(str(pkg))
        rev = {'installed_version': pkg_ver,
               'requires': [pkginfo(str(dep), repair=True) for dep in pkg.requires()]}
        packages_data[pkg_name] = rev
    packages_data = insert_extras(packages_data)
    packages_data = insert_availables(packages_data)
    packages_data = insert_news(packages_data)

    while True:
        new_packages_data = new_packages(packages_data)
        if not new_packages_data:
            break
        new_packages_data = insert_availables(new_packages_data)
        new_packages_data = insert_news(new_packages_data)
        packages_data = merge_two_dicts(packages_data, new_packages_data)
    check_new_extras(packages_data)
    return packages_data

def pkginfo(data, req_extra=None, repair=False):
    """
    Return parsed pkginfo
    """
    extra_match = re.compile(
        r"""^(?P<package>.*?)(;\s*(?P<condition>.*?)(extra == '(?P<extra>.*?)')?)$""").search(data)
    if extra_match:
        groupdict = extra_match.groupdict()
        condition = groupdict['condition']
        extra = groupdict['extra']
        package = groupdict['package']
        if condition.endswith(' and '):
            condition = condition[:-5]
        mysearch = re.compile(r'(extra == .*)').search(condition)
        if mysearch:
            extra = mysearch.group(1)
            condition = condition.replace(extra, '')
            if not condition:
                condition = None
            extra = re.compile(r'extra == (.*)').search(extra).group(1).replace('"', "")
    else:
        condition, extra = None, None
        package = data
    if not is_in_conditions(condition):
        return None
    pkg_name, pkg_extra, pkg_ver = re.compile(
        r'([\w\.\-]*)(\[\w*\])?(.*)').search(package).groups()
    if pkg_extra:
        pkg_extra = pkg_extra.replace("[", "").replace("]", "").lower()
    pkg_ver = pkg_ver.replace("(", "").replace(")", "").strip()
    if not pkg_ver:
        pkg_ver = []
    else:
        if repair:
            try:
                pkg_ver = re.compile(r'^(\d.*)$').search(pkg_ver).group(1)
            except AttributeError:
                pass
            pkg_ver = pkg_ver.split(",")
    if not is_in_extra(extra, req_extra):
        return None
    return (pkg_name.lower(), pkg_ver, pkg_extra)

def insert_extras(data):
    """
    Insert extras
    """
    for key in data.keys():
        extra = []
        for pkg, pkg_data in data.iteritems():
            for dep in pkg_data['requires']:
                if dep[0] == key:
                    if dep[2]:
                        extra.append(dep[2])
        data[key]['extras'] = extra
        if extra:
            # pylint: disable=protected-access
            for pkg in pip._internal.utils.misc.get_installed_distributions():
                pkg_name, _pkg_ver, _pkg_extra = pkginfo(str(pkg))
                if pkg_name == key:
                    data[key]['requires'] += [pkginfo(str(dep), repair=True, req_extra=extra) \
                                              for dep in pkg.requires(extras=extra)]
    return data

def insert_availables(data):
    """
    Insert available versions
    """
    for pkg, pkg_data in data.iteritems():
        if 'available_version' in pkg_data.keys():
            continue
        try:
            data[pkg]['available_version'] = get_available_vers(pkg)
        except urllib2.HTTPError:
            data[pkg]['available_version'] = []
    return data

def get_available_vers(package):
    """
    Return descending list of public available strict version
    """
    versions = []
    try:
        data = get_json("https://pypi.python.org/pypi/%s/json" % (package))
    except urllib2.HTTPError, err:
        print "%s %s" % (err, err.url)
        raise urllib2.HTTPError(err.url, err.code, None, err.hdrs, err.fp)
    releases = data["releases"].keys()
    for release in releases:
        requires_python = []
        for item in data["releases"][release]:
            if item['requires_python'] is not None:
                for reqpyt in item['requires_python'].split(","):
                    requires_python.append(reqpyt.strip())
        if requires_python:
            requires_python = list(set(requires_python))
        if is_version(release) and is_in_specifiers(PY_VER, requires_python):
            versions.append(release)
    return sorted(versions, key=packaging.specifiers.LegacyVersion, reverse=True)

def select_news(available_version, installed_version=None):
    """
    Select versions newer than installed version, if it is known
    """
    if installed_version is None:
        return sorted(available_version, key=packaging.specifiers.LegacyVersion, reverse=True)
    iver = packaging.version.Version(installed_version)
    return sorted([aver for aver in available_version if packaging.version.Version(aver) > iver],
                  key=packaging.specifiers.LegacyVersion, reverse=True)

def insert_news(data):
    """
    Insert new versions
    """
    for pkg, pkg_data in data.iteritems():
        if 'new_version' in pkg_data.keys():
            continue
        try:
            new_version = select_news(pkg_data['available_version'], pkg_data['installed_version'])
        except KeyError:
            new_version = select_news(pkg_data['available_version'])
        if new_version:
            res = {}
            for version in new_version:
                content = parse_metadata(get_metadata(pkg, version), pkg_data['extras'])
                if content is not None:
                    res[version] = content
            if res:
                pkg_data['new_version'] = res
    return data

def new_packages(data):
    """
    Return new packages as dictionary
    """
    out = {}
    arr = []
    pkg_list = data.keys()
    for pkg, pkg_data in data.iteritems():
        try:
            for dep in pkg_data['requires']:
                if dep[0] not in pkg_list:
                    arr.append(dep)
            for _ver, ver_data in pkg_data['new_version'].iteritems():
                for dep in ver_data:
                    if dep[0] not in pkg_list:
                        arr.append(dep)
        except KeyError:
            pass
    for item in list(set([i[0] for i in arr])):
        extras = []
        for pkg, _req, extra in arr:
            if pkg == item and extra is not None:
                extras.append(extra)
        out[item] = {'extras': extras}
    return out

def check_new_extras(data):
    """
    Check if there are new extras
    """
    extra_pkgs = []
    pkg_list = data.keys()
    for pkg, pkg_data in data.iteritems():
        try:
            for _ver, ver_data in pkg_data['new_version'].iteritems():
                for dep in ver_data:
                    if dep[0] in pkg_list and dep[2] is not None:
                        extra_pkgs.append(dep)
        except KeyError:
            pass
    for pkg, _req, extra in extra_pkgs:
        if extra not in data[pkg]['extras']:
            raise Exception('There are new extras!')

def check_extras(data):
    """
    Check if there are extras in upgradeable packages
    """
    for package in select_upkgs(data, 'upgradeable_version'):
        if data[package]['extras']:
            raise Exception('There are extras in upgradeable packages!')

def check_co_branches(data):
    """
    Check if there branches with intersection of packages
    """
    branches = get_branches(data)
    co_branches = get_co_branches(branches)
    if co_branches:
        raise Exception('There are branches with intersection of packages!')

def pvector(package, data):
    """
    Return vector of package versions
    """
    out = []
    if 'new_version' not in data[package].keys():
        out.append((package, data[package]['installed_version']))
    else:
        if 'upgradeable_version' in data[package].keys():
            out.append((package, data[package]['upgradeable_version']))
        else:
            if 'installed_version' in data[package].keys():
                out.append((package, data[package]['installed_version']))
        for ver in sorted(data[package]['new_version'].keys(),
                          key=packaging.specifiers.LegacyVersion):
            if 'upgradeable_version' in data[package].keys():
                if packaging.specifiers.LegacyVersion(ver) > \
                   packaging.specifiers.LegacyVersion(data[package]['upgradeable_version']):
                    out.append((package, ver))
            else:
                out.append((package, ver))
    return out

def single_multi(data):
    """
    Return list of packages with new versions and list of packages without new versions
    """
    pkg_list, single, multi = [], [], []
    for pkg, pkg_data in data.iteritems():
        if 'requires' in pkg_data.keys():
            pkg_list.append(pkg)
    for pkg in pkg_list:
        vec = pvector(pkg, data)
        if len(vec) == 1:
            single.append(*vec)
        elif len(vec) > 1:
            multi.append(vec)
    single = list(set([item[0] for item in single]))
    multi = list(set([item[0] for pkg_data in multi for item in pkg_data]))
    return single, multi

def move_incompatible(data, to_delete):
    """
    Move new version to incompatible
    """
    if not to_delete:
        return data
    for package, version in to_delete:
        if 'incompatible_version' not in data[package].keys():
            data[package]['incompatible_version'] = {}
        data[package]['incompatible_version'][version] = data[package]['new_version'][version]
        del data[package]['new_version'][version]
        if not data[package]['new_version']:
            del data[package]['new_version']
    return data

def get_compatible(versions, reqs, inverse=False):
    """
    Return compatible versions
    """
    specifiers = specifiers_intersection([i for i in itertools.chain(*[req[1] for req in reqs])])
    if inverse:
        v_versions = [version for version in versions if not is_in_specifiers(version, specifiers)]
    else:
        v_versions = [version for version in versions if is_in_specifiers(version, specifiers)]
    return sorted(v_versions, key=packaging.specifiers.LegacyVersion, reverse=True)

def get_hards(data, package_no_news):
    """
    Return requirements
    """
    out = {}
    deps = get_simple_reqs(data, None, package_no_news)
    for item in list(set([pkg[0] for pkg in deps])):
        reqs, extras = [], []
        for pkg, req, extra in deps:
            if pkg == item:
                reqs += req
                if extra:
                    extras += extra
        if 'installed_version' in data[item].keys():
            out[item] = {'installed_version': data[item]['installed_version'],
                         'requirements': list(set(reqs)),
                         'extras': list(set(extras))}
    return out

def del_hards(data):
    """
    Return list of packages and their versions that does not satisfy
    requirements of packages without new version
    """
    to_delete = []
    package_no_news, package_with_news = single_multi(data)
    hard_requirements = get_hards(data, package_no_news)
    for pkg in package_with_news+not_installed(data):
        for ver, ver_data in data[pkg]['new_version'].iteritems():
            for dep, req, _extra in ver_data:
                if dep in hard_requirements.keys():
                    if specifiers_intersection(req+hard_requirements[dep]['requirements']) is None:
                        to_delete.append((pkg, ver))
    return to_delete

def del_no_news(data):
    """
    Return list of packages and their versions that does not satisfy packages without new version
    """
    to_delete = []
    package_no_news, package_with_news = single_multi(data)
    hard_requirements = get_hards(data, package_no_news)
    for package in package_with_news+not_installed(data):
        if package in hard_requirements.keys():
            versions = [pkg[1] for pkg in pvector(package, data)]
            specifiers = specifiers_intersection(hard_requirements[package]['requirements'])
            for version in versions:
                if not is_in_specifiers(version, specifiers):
                    to_delete.append((package, version))
    return to_delete

def del_one_ver(data):
    """
    If all packages requirements lead to one specific version, return list of that packages
    """
    to_delete = []
    _package_no_news, package_with_news = single_multi(data)
    for package in package_with_news+not_installed(data):
        reqs = get_reqs(data, package)
        specifiers = specifiers_intersection(
            [i for i in itertools.chain(*[req[1] for req in reqs])])
        if specifiers:
            if len(specifiers) == 1 and '==' in specifiers[0]:
                versions = [pkg[1] for pkg in pvector(package, data)]
                versions.remove(specifiers[0].replace('==', ''))
                for version in versions:
                    to_delete.append((package, version))
    return to_delete

def del_notinstalled(data):
    """
    If no package requires notinstalled packages, return list of that packages
    """
    to_delete = []
    for package in not_installed(data):
        reqs = get_reqs(data, package)
        if not reqs:
            for pkg, version in pvector(package, data):
                to_delete.append((pkg, version))
    return to_delete

def get_deps(data, package):
    """
    Return package deep requirements
    """
    try:
        content = data[package]
    except KeyError:
        content = []
    for pkg in content:
        yield pkg
        for child in get_deps(data, pkg):
            yield child

def not_installed(data):
    """
    Return not installed packages
    """
    not_i = []
    for pkg, pkg_data in data.iteritems():
        if 'requires' not in pkg_data.keys() and 'new_version' in pkg_data.keys():
            not_i.append(pkg)
    return not_i

def get_no_news_req(data):
    """
    Return requirements of packages without new versions
    """
    reqs = {}
    package_no_news, _package_with_news = single_multi(data)
    for package in package_no_news:
        version = pvector(package, data)[0][1]
        reqs = save_version(reqs, data, package, version)
    return reqs

def save_version(r_data, p_data, pkg, ver):
    """
    Save the highest package version
    """
    if 'installed_version' in p_data[pkg].keys() and p_data[pkg]['installed_version'] == ver:
        r_data[pkg] = p_data[pkg]['requires']
    else:
        r_data[pkg] = p_data[pkg]['new_version'][ver]
    return r_data

def add_reqs(reqs, data, pkg=None, addpkg=None):
    """
    Append requirements
    """
    for dep, req, extra in data:
        if pkg and dep != pkg:
            continue
        if addpkg:
            reqs.append(addpkg)
        else:
            reqs.append((dep, req, extra))

def save_ic(out, package, incompatible=None, compatible=None):
    """
    Save compatible/incompatible version
    """
    if package not in out.keys():
        out[package] = {'incompatible': [], 'compatible': None}
    if incompatible:
        out[package]['incompatible'].append(incompatible)
    if compatible:
        out[package]['compatible'] = compatible
    return out

def get_reqs(data, package, data2=None, addpkg=False):
    """
    Get requirements
    """
    reqs = []
    if data2:
        for pkg in data2:
            if 'upgradeable_version' in data[pkg].keys():
                uver = data[pkg]['upgradeable_version']
                add_reqs(reqs, data[pkg]['new_version'][uver], pkg=package)
            else:
                add_reqs(reqs, data[pkg]['requires'], pkg=package)
        return reqs
    for pkg, pkg_data in data.iteritems():
        uver = None
        if pkg == package:
            continue
        if 'upgradeable_version' in pkg_data.keys():
            uver = pkg_data['upgradeable_version']
            if addpkg:
                add_reqs(reqs, pkg_data['new_version'][uver], pkg=package, addpkg=pkg)
            else:
                add_reqs(reqs, pkg_data['new_version'][uver], pkg=package)
        elif 'requires' in pkg_data.keys():
            if addpkg:
                add_reqs(reqs, pkg_data['requires'], pkg=package, addpkg=pkg)
            else:
                add_reqs(reqs, pkg_data['requires'], pkg=package)
        if 'new_version' in pkg_data.keys():
            for ver, ver_data in pkg_data['new_version'].iteritems():
                if uver:
                    if packaging.specifiers.LegacyVersion(ver) <= \
                       packaging.specifiers.LegacyVersion(uver):
                        continue
                if addpkg:
                    add_reqs(reqs, ver_data, pkg=package, addpkg=pkg)
                else:
                    add_reqs(reqs, ver_data, pkg=package)
    return reqs

def get_reqs_dict(data):
    """
    Get requirements
    """
    out = {}
    for pkg, pkg_data in data.iteritems():
        reqs = []
        uver = None
        if 'upgradeable_version' in pkg_data.keys():
            uver = pkg_data['upgradeable_version']
            add_reqs(reqs, pkg_data['new_version'][uver])
        elif 'requires' in pkg_data.keys():
            add_reqs(reqs, pkg_data['requires'])
        if 'new_version' in pkg_data.keys():
            for ver, ver_data in pkg_data['new_version'].iteritems():
                if uver:
                    if packaging.specifiers.LegacyVersion(ver) <= \
                       packaging.specifiers.LegacyVersion(uver):
                        continue
                add_reqs(reqs, ver_data)
        out[pkg] = list(set([req[0] for req in reqs]))
    return out

def get_simple_reqs(data, package_with_news, package_no_news):
    """
    Return no_requires, only_no_news_requires or requirements
    """
    if package_with_news is None:
        reqs = []
        for pkg in package_no_news:
            if 'requires' in data[pkg].keys():
                if 'upgradeable_version' in data[pkg].keys():
                    uver = data[pkg]['upgradeable_version']
                    reqs += [req for req in data[pkg]['new_version'][uver] if req[1] or req[2]]
                else:
                    reqs += [req for req in data[pkg]['requires'] if req[1] or req[2]]
        return reqs
    no_requires, only_no_news_requires, = {}, {}
    for pkg in package_with_news:
        dep_in_no_news_vers = []
        dep_vers = []
        uver = None
        if 'upgradeable_version' in data[pkg].keys():
            uver = data[pkg]['upgradeable_version']
        if 'new_version' in data[pkg].keys():
            for ver, ver_data in data[pkg]['new_version'].iteritems():
                if uver:
                    if packaging.specifiers.LegacyVersion(ver) <= \
                       packaging.specifiers.LegacyVersion(uver):
                        continue
                if ver_data:
                    reqs = [req[0] for req in ver_data]
                    reqs_not_in_no_news = [req for req in reqs if req not in package_no_news]
                    if not reqs_not_in_no_news:
                        dep_in_no_news_vers.append(ver)
                else:
                    dep_vers.append(ver)
        if dep_vers:
            no_requires[pkg] = dep_vers
        if dep_in_no_news_vers:
            only_no_news_requires[pkg] = dep_in_no_news_vers
    return no_requires, only_no_news_requires

def phase_one(data):
    """
    Partial resolve upgrades
    """
    out, no_requires_deps = {}, {}
    package_no_news, package_with_news = single_multi(data)
    no_requires, only_no_news_requires = get_simple_reqs(data, package_with_news, package_no_news)
    for package, version in no_requires.iteritems():
        reqs = get_reqs(data, package, addpkg=True)
        if reqs:
            no_requires_deps[package] = list(set(reqs))
        else:
            out = save_ic(out, package,
                          compatible=sorted(no_requires[package],
                                            key=packaging.specifiers.LegacyVersion,
                                            reverse=True)[0])

    for package, dep in no_requires_deps.iteritems():
        if all([pkg in package_no_news for pkg in dep]):
            reqs = get_reqs(data, package, data2=dep)
            compatible = get_compatible(no_requires[package], reqs)
            for version in no_requires[package]:
                if version not in compatible:
                    out = save_ic(out, package, incompatible=version)
            if compatible:
                out = save_ic(out, package, compatible=compatible[0])

    for package, versions in only_no_news_requires.iteritems():
        reqs = get_reqs(data, package, addpkg=True)
        if all([item in package_no_news for item in list(set(reqs))]):
            out = save_ic(out, package,
                          compatible=sorted(versions,
                                            key=packaging.specifiers.LegacyVersion,
                                            reverse=True)[0])
    return out

def get_branches(data):
    """
    Return branches
    """
    branches = []
    package_reqs = {}
    _package_no_news, package_with_news = single_multi(data)
    package_with_news = package_with_news+not_installed(data)
    package_info = get_reqs_dict(data)
    for package in package_with_news:
        package_reqs[package] = list(set([i for i in get_deps(package_info, package)]))
    for package in package_with_news:
        res = []
        for pkg, deps in package_reqs.iteritems():
            if pkg == package:
                continue
            if package in deps:
                res.append(pkg)
        if not res:
            branches.append(package)
    package_info = {}
    for branch in branches:
        package_info[branch] = [i for i in package_reqs[branch] if i in package_with_news]
    return package_info

def get_co_branches(branches):
    """
    Return corelated branches
    """
    co_branches = []
    for branch in branches:
        for pkg, reqs in branches.iteritems():
            if pkg == branch:
                continue
            if len(branches[branch]+reqs) != len(list(set(branches[branch]+reqs))):
                co_branches.append(branch)
    return list(set(co_branches))

def cross_packages(data):
    """
    Return cross packages
    """
    cross_branches = []
    out, pkg_reqs = {}, {}
    package_branches = get_branches(data)
    _package_no_news, package_with_news = single_multi(data)
    package_with_news = package_with_news+not_installed(data)
    for package in package_with_news:
        res = []
        for pkg, reqs in package_branches.iteritems():
            if package in reqs:
                res.append(pkg)
        if len(res) > 1:
            cross_branches.append(package)
    for package in package_with_news:
        if package not in cross_branches:
            version = pvector(package, data)[0][1]
            pkg_reqs = save_version(pkg_reqs, data, package, version)
    merged_reqs = merge_two_dicts(pkg_reqs, get_no_news_req(data))
    for package in cross_branches:
        reqs = []
        for pkg, pkg_data in merged_reqs.iteritems():
            add_reqs(reqs, pkg_data, pkg=package)
        compatible = get_compatible([pkg[1] for pkg in pvector(package, data)], reqs)
        if compatible:
            out = save_ic(out, package, compatible=compatible[0])
    return out

def get_comb_summary(data, packages, common_reqs):
    """
    Return combination summary
    """
    out = {}
    for comb in list(itertools.product(*packages)):
        pkg_reqs = {}
        for package, version in comb:
            pkg_reqs = save_version(pkg_reqs, data, package, version)
        pkg_reqs = merge_two_dicts(common_reqs, pkg_reqs)
        sumary = []
        for package, version in comb:
            reqs = []
            for _pkg, pkg_data in pkg_reqs.iteritems():
                add_reqs(reqs, pkg_data, pkg=package)
            specifiers = specifiers_intersection(
                [i for i in itertools.chain(*[req[1] for req in reqs])])
            sumary.append(is_in_specifiers(version, specifiers))
        if all(sumary):
            sumary = 0
            for package, version in comb:
                sumary += pvector(package, data).index((package, version))
            out[comb] = sumary
    return out

def u_comb(data, packages, common_reqs):
    """
    Return combination upgrade
    """
    out = []
    high = 0
    comb_summary = get_comb_summary(data, packages, common_reqs)
    for comb, summary in comb_summary.iteritems():
        if summary > high:
            high = summary
    if high > 0:
        reqs = []
        for comb, summary in comb_summary.iteritems():
            if summary == high:
                reqs.append(comb)
        for pkg, version in reqs[0]:
            if 'installed_version' in data[pkg].keys() and \
               data[pkg]['installed_version'] != version:
                out.append((pkg, version))
        return out
    return None

def ibranch(data, fix=False):
    """
    Return upgradeable versions of independent branch
    """
    out = {}
    no_news_req = get_no_news_req(data)
    branches = get_branches(data)
    _package_no_news, package_with_news = single_multi(data)
    co_branches = get_co_branches(branches)
    for branch in branches:
        if branch in co_branches:
            continue
        if fix:
            version = pvector(branch, data)[0][1]
            pkg_reqs = save_version({}, data, branch, version)
            common_reqs = merge_two_dicts(pkg_reqs, no_news_req)
            packages = [pvector(pkg, data)[:2] \
                        for pkg in branches[branch] if pkg in package_with_news]
        else:
            common_reqs = no_news_req.copy()
            packages = [pvector(branch, data)]+[pvector(pkg, data) \
                        for pkg in branches[branch] if pkg in package_with_news]
        compatible = u_comb(data, packages, common_reqs)
        if compatible:
            for pkg, version in compatible:
                out = save_ic(out, pkg, compatible=version)
    return out

def p_upgrade(data, pkg, compatible=None, incompatible=None):
    """
    Partial upgrade
    """
    if compatible:
        data[pkg]['upgradeable_version'] = compatible
    if incompatible:
        for version in incompatible:
            if compatible and version not in compatible:
                data = move_incompatible(data, [(pkg, version)])
            elif not compatible:
                data = move_incompatible(data, [(pkg, version)])
    return data

def first_loop(data):
    """
    Upgrade loop
    """
    while True:
        to_delete_hards = del_hards(data)
        data = move_incompatible(data, to_delete_hards)
        to_delete_no_news = del_no_news(data)
        data = move_incompatible(data, to_delete_no_news)
        to_delete_one_ver = del_one_ver(data)
        data = move_incompatible(data, to_delete_one_ver)

        phase_one_packages = phase_one(data)
        for pkg, pkg_data in phase_one_packages.iteritems():
            data = p_upgrade(data, pkg, compatible=pkg_data['compatible'],
                             incompatible=pkg_data['incompatible'])

        cross_pkgs = cross_packages(data)
        for pkg, pkg_data in cross_pkgs.iteritems():
            data = p_upgrade(data, pkg, compatible=pkg_data['compatible'],
                             incompatible=pkg_data['incompatible'])

        to_delete_noti = del_notinstalled(data)
        data = move_incompatible(data, to_delete_noti)

        i_branch = ibranch(data, fix=True)
        for pkg, pkg_data in i_branch.iteritems():
            data = p_upgrade(data, pkg, compatible=pkg_data['compatible'])
        if all([not to_delete_hards, not to_delete_no_news, not to_delete_one_ver,
                not phase_one_packages, not cross_pkgs, not to_delete_noti, not i_branch]):
            break
    return data

def main():
    """
    main function
    """
    os.environ["PYTHONWARNINGS"] = "ignore:DEPRECATION"
    arguments = arg_parse()
    packages_data = get_pkg_data()
    packages_data = first_loop(packages_data)

    i_branch = ibranch(packages_data)
    for package, data in i_branch.iteritems():
        if data['compatible']:
            packages_data[package]['upgradeable_version'] = data['compatible']

    check_co_branches(packages_data)
    check_extras(packages_data)

    if arguments.list:
        sys.exit(print_list(packages_data))
    if arguments.show is not None:
        if arguments.show:
            pkgs = arguments.show
        else:
            pkgs = packages_data
        for pkg in pkgs:
            pprint.pprint({pkg: packages_data[pkg]})
        sys.exit(0)
    if arguments.upgrade:
        to_upgrade = []
        for pkg in sorted(select_upkgs(packages_data, 'upgradeable_version')):
            to_upgrade.append((pkg, packages_data[pkg]['upgradeable_version']))
        upgrade_package(to_upgrade)
        print "Done."

if __name__ == "__main__":
    main()
