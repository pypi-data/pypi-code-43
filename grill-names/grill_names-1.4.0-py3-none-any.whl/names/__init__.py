from __future__ import annotations
import naming
from grill.tokens import ids


def _table_from_id(id_mapping):
    headers = [
        'Token',
        'Pattern',
        'Default',
        'Description',
    ]
    table_sep = tuple([''] * len(headers))
    sorter = lambda m: (
        # cleanup backslashes formatting
        m["pattern"].replace('\\', '\\\\'),
        m['default'],
        # replace new lines with empty strings to avoid malformed tables.
        m['description'].replace('\n', ' '),
    )
    rows = [table_sep, headers, table_sep]
    rows.extend([token, *sorter(values)] for token, values in id_mapping.items())
    rows.append(table_sep)
    max_sizes = [(max(len(i) for i in r)) for r in zip(*rows)]

    format_rows = []
    for r in rows:
        filler = '=<' if r == table_sep else ''
        format_rows.append(' '.join(
            f"{{:{f'{filler}'}{f'{size}'}}}".format(i)
            for size, i in zip(max_sizes, r))
        )
    return '\n'.join(format_rows)


class Project(naming.Name):
    """Inherited by: :class:`grill.names.Environment`

    Project Name objects.

    ==========  ==========
    **Config:**
    ----------------------
    *project*   Any amount of characters in the class [a-zA-Z0-9]
    *workarea*  Any amount of word characters
    ==========  ==========

    Basic use::

        >>> from grill.names import Project
        >>> p = Project()
        >>> p.get_name()
        '[project]_[workarea]'
        >>> f.get_name(workarea='foo')
        '[project]_foo'
        >>> p.name = 'test_concept_art'
        >>> p.values
        {'project': 'test', 'workarea': 'concept_art'}
        >>> p.workarea = 'rigging'
        >>> p.name
        'test_rigging'
    """
    config = dict(project='[a-zA-Z0-9]+', workarea='\w+')

    def __init__(self, *args, sep='_', **kwargs):
        super().__init__(*args, sep=sep, **kwargs)


class Environment(Project):
    """Inherited by: :class:`grill.names.Primitive`

    Environment splits the project field to know more about where it belongs.

    ============= ==========
    **Config:**
    ------------------------
    *environment* Composed of 3 lowercase letters
    *code*        Any amount of characters in the class [a-zA-Z0-9]
    ============= ==========

    ========= ====
    **Compounds:**
    --------------
    *project* environment, code
    ========= ====

    Basic use::

        >>> from grill.names import Environment
        >>> e = Environment('flmmultimedia_concept_art')
        >>> e.values
        {'project': 'flmmultimedia',
        'environment': 'flm',
        'code': 'multimedia',
        'workarea': 'concept_art'}
        >>> e.get_name(environment='gme')
        'gmemultimedia_concept_art'
    """
    config = dict(environment='[a-z]{3}', code='[a-z0-9]+')
    compounds = dict(project=('environment', 'code'))


class Primitive(Environment):
    """
    For primitive names with multiple stages of development.

    ======= ================
    **Config:**
    ------------------------
    *prim*  Any amount of characters in the class [a-zA-Z0-9]
    *stage* Any amount of characters in the class [a-zA-Z0-9]
    ======= ================

    Basic use::

        >>> from grill.names import Primitive
        >>> a = Primitive('prmtest_concept_art_hero_color')
        >>> a.values
        {'project': 'prmtest',
        'environment': 'prm',
        'code': 'test',
        'workarea': 'concept_art',
        'prim': 'hero',
        'stage': 'color',
        'version': '1',
        'suffix': 'psd'}
    """
    config = dict(prim='[a-zA-Z0-9]+', stage='[a-z0-9]+')


class CGAsset(naming.Name):
    """Inherited by: :class:`grill.names.CGAssetFile`

    Elemental resources that, when composed, generate the entities that bring an idea to a tangible product
    through their life cycles (e.g. a character, a film, a videogame).

    """
    config = {k: v['pattern'] for k, v in ids.CGAsset.items()}
    __doc__ += '\n' + _table_from_id(ids.CGAsset) + '\n'

    def __init__(self, *args, sep='-', **kwargs):
        super().__init__(*args, sep=sep, **kwargs)

    @property
    def _defaults(self):
        return {k: v['default'] for k, v in ids.CGAsset.items()}

    @classmethod
    def get_default(cls, **kwargs) -> CGAsset:
        """Get a new Name object with default values and overrides from **kwargs."""
        name = cls()
        defaults = dict(name._defaults, **kwargs)
        name.name = name.get_name(**defaults)
        return name


class CGAssetFile(CGAsset, naming.PipeFile):
    """Versioned files in the pipeline for a CGAsset.

    Basic use::

        >>> from grill.names import CGAssetFile
        >>> name = CGAssetFile.get_default(version=7)
        >>> name.suffix
        'ext'
        >>> name.suffix = 'abc'
        >>> name.path
        WindowsPath('demo/3d/abc/entity/rnd/master/atom/main/all/whole/7/demo-3d-abc-entity-rnd-master-atom-main-all-whole.7.abc')
    """

    @property
    def _defaults(self):
        result = super()._defaults
        result.update(version=1, suffix='ext')
        return result

    def get_path_pattern_list(self):
        pattern = super().get_pattern_list()
        pattern.append('version')
        return pattern


class LifeTR(naming.Name):
    """Taxonomic Rank used for biological classification.

    """
    config = {k: v['pattern'] for k, v in ids.LifeTR.items()}
    __doc__ += '\n' + _table_from_id(ids.LifeTR) + '\n'

    def __init__(self, *args, sep=':', **kwargs):
        super().__init__(*args, sep=sep, **kwargs)
