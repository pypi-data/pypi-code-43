"""
    Copyright (c) 2019 Contributors as noted in the AUTHORS file
    This file is part of ggm, the GILGAMESH core engine in Python.
    ggm is free software; you can redistribute it and/or modify it under
    the terms of the GNU Lesser General Public License (GPL) as published
    by the Free Software Foundation; either version 3 of the License, or
    (at your option) any later version.
    As a special exception, the Contributors give you permission to link
    this library with independent modules to produce an executable,
    regardless of the license terms of these independent modules, and to
    copy and distribute the resulting executable under terms of your choice,
    provided that you also meet, for each linked independent module, the
    terms and conditions of the license of that module. An independent
    module is a module which is not derived from or based on this library.
    If you modify this library, you must extend this exception to your
    version of the library.
    ggm is distributed in the hope that it will be useful, but WITHOUT
    ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
    FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public
    License for more details.
    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""


def update_nested_dict(d, u):
    """doc
    """
    for k, v in u.items():
        dv = d.get(k, {})
        if not isinstance(dv, dict):
            d[k] = v
        elif isinstance(v, dict):
            d[k] = update_nested_dict(dv, v)
        else:
            d[k] = v
    return d

class Kmap(object):
    """FIXME
    there has to be a better way
    """
    def __init__(self, base_cfg, *args, **kwargs):
        self.base_cfg = base_cfg
        self.kmap = list()

    def append_spec(self, what, kname, config, xname=None, path=None):
        """doc
        """
        funcname = kname+'_process'
        modname = f'ggm.{what}.{kname}'

        if path:
            import importlib.util as iutil
            filename = kname+f'.py'
            f = path / filename
            spec = iutil.spec_from_file_location(modname, f)
            module = iutil.module_from_spec(spec)
            spec.loader.exec_module(module)
        else:
            from importlib import import_module
            module = import_module(modname)

        func = getattr(module, funcname)

        # use xname if available
        if 'config' not in config:
            config['config'] = dict()
        kname = xname or kname
        config['config']['name'] = kname
        config['config'].update(self.base_cfg)
        #update_nested_dict(config, self.base_cfg)
        kspec = {
            'name': kname,
            'function': func,
            'config': config['config']
        }
        self.kmap.append(kspec)
        return True

def generate_certificate(path, name):
    """FIXME
    there has to be a better way
    """
    import os, shutil, errno
    import zmq.auth
    from pathlib import Path

    if zmq.zmq_version_info() < (4,0):
        raise RuntimeError(f'Security is not supported in libzmq version < 4.0. libzmq version {zmq.zmq_version()}')

    # Generate client and server CURVE certificate files
    #base_dir = Path.cwd()
    base_dir = Path(path)
    tmp_dir = base_dir / 'certificates'

    if not base_dir.exists():
        os.mkdir(base_dir)
    if not tmp_dir.exists():
        os.mkdir(tmp_dir)

    # Check for existing certificates
    knames = [f'{name}.key', f'{name}.key_secret']
    for key in knames:
        f =  tmp_dir / key
        if f.exists():
            raise FileExistsError(f'{f} already exists.')

    # create new keys in certificate dir
    public_file, secret_file = zmq.auth.create_certificates(tmp_dir, name)

    pubk = f'{name}.key'
    pub_dir = path / Path(f'public_keys')
    seck = f'{name}.key_secret'
    sec_dir = path / Path(f'private_keys')
    if not pub_dir.exists():
        os.mkdir(pub_dir)
    if not sec_dir.exists():
        os.mkdir(sec_dir)

    dest = pub_dir / pubk
    if not dest.exists():
        shutil.move(public_file, dest)
    else:
        raise FileExistsError(f'{dest} already exists. trouble ahead...')

    dest = sec_dir / seck
    if not dest.exists():
        shutil.move(secret_file, dest)
    else:
        raise FileExistsError(f'{dest} already exists. trouble ahead...')

    try:
        os.rmdir(tmp_dir)
    except Exception as e:
        print(e)
