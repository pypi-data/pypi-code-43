# -*- coding: utf-8 -*-
from distutils.core import setup

modules = \
['resubname']
entry_points = \
{'console_scripts': ['resubname = resubname:cli']}

setup_kwargs = {
    'name': 'resubname',
    'version': '0.2.0',
    'description': 'Rename subtitle filenames to match videos.',
    'long_description': '# resubname\n\nRename subtitle filenames to match videos.\n\n## Install with `pipx`\n\nUsing [pipx](https://pipxproject.github.io/pipx/) to install `resubname` is recommended.\n\n```bash\npipx install resubname\n```\n\n## Example\n\n```bash\n> ls\n 03.ass    \'[VCB-Studio] GIRLS und PANZER [03][Ma10p_1080p][x265_flac].mkv\'\n 05.5.ass  \'[VCB-Studio] GIRLS und PANZER [05.5][Ma10p_1080p][x265_flac].mkv\'\n 05.ass    \'[VCB-Studio] GIRLS und PANZER [05][Ma10p_1080p][x265_flac].mkv\'\n\n> resubname *.ass *.mkv\n03.ass -> [VCB-Studio] GIRLS und PANZER [03][Ma10p_1080p][x265_flac].ass\n05.5.ass -> [VCB-Studio] GIRLS und PANZER [05.5][Ma10p_1080p][x265_flac].ass\n05.ass -> [VCB-Studio] GIRLS und PANZER [05][Ma10p_1080p][x265_flac].ass\n> ls\n\'[VCB-Studio] GIRLS und PANZER [03][Ma10p_1080p][x265_flac].ass\'\n\'[VCB-Studio] GIRLS und PANZER [03][Ma10p_1080p][x265_flac].mkv\'\n\'[VCB-Studio] GIRLS und PANZER [05.5][Ma10p_1080p][x265_flac].ass\'\n\'[VCB-Studio] GIRLS und PANZER [05.5][Ma10p_1080p][x265_flac].mkv\'\n\'[VCB-Studio] GIRLS und PANZER [05][Ma10p_1080p][x265_flac].ass\'\n\'[VCB-Studio] GIRLS und PANZER [05][Ma10p_1080p][x265_flac].mkv\'\n```\n\nAnd you can exclude certain files:\n\n```bash\n> ls\n\'[ANE] Soredemo Machi wa Mawatte Iru - EP01 [BD 1920x1080 H.264 FLAC].CASO-SC.ass\'\n\'[ANE] Soredemo Machi wa Mawatte Iru - EP02 [BD 1920x1080 H.264 FLAC].CASO-SC.ass\'\n\'[ANK-Raws] それでも町は廻っている (Ep_05 Creditless ED) (BDrip 1920x1080 HEVC-YUV420P10 FLAC).mkv\'\n\'[ANK-Raws] それでも町は廻っている 01 (BDrip 1920x1080 HEVC-YUV420P10 FLAC).mkv\'\n\'[ANK-Raws] それでも町は廻っている 02 (BDrip 1920x1080 HEVC-YUV420P10 FLAC).mkv\'\n> resubname *.ass *.mkv -e creditless --dryrun\n[ANE] Soredemo Machi wa Mawatte Iru - EP01 [BD 1920x1080 H.264 FLAC].CASO-SC.ass -> [ANK-Raws] それでも町は廻っている 01 (BDrip 1920x1080 HEVC-YUV420P10 FLAC).ass\n[ANE] Soredemo Machi wa Mawatte Iru - EP02 [BD 1920x1080 H.264 FLAC].CASO-SC.ass -> [ANK-Raws] それでも町は廻っている 02 (BDrip 1920x1080 HEVC-YUV420P10 FLAC).ass\n```\n\n## Help\n\n```\nresubname -h\n```\n\n## Changelog\n\n### v0.2.0\n\n- Show videos and subtitiles file list when their number dismatch.\n- Stop complain about "Unknown suffix" for folders. Will just ignore them.\n\n### v0.1.0\n\n- Initial Release\n',
    'author': 'Wu Haotian',
    'author_email': 'whtsky@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/whtsky/resubname',
    'py_modules': modules,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
