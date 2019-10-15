# -*- coding: utf-8 -*-
"""
Created 2019/08/21

"""

FTP_HOST = '141.24.24.121'

dataset_info = {
    1: {'patchsizes': [64, 'images'],
        'issues': ['NORMvsDISTRESS'],
        'subsets': ['train', 'valid', 'test']},

    2: {'patchsizes': [64, 96, 128, 160, 192, 224, 256, 'segmentation', 'images'],
        'issues': ['NORMvsDISTRESS', 'NORMvsDISTRESS_50k', 'ZEB_50k'],
        'subsets': ['train', 'valid', 'valid-test', 'test']}
}

ftp_version_prefix = {
    1: '/GAPs/v1/',
    2: '/GAPs2/'
}

INFO_FILE_TEMPLATE = 'chunks_{patchsize}x{patchsize}_{issue}_{subset}_info.pkl'
CHUNK_TEMPLATE = 'chunks_{patchsize}x{patchsize}_{issue}_{subset}_chunk_{part_nr}_{data}.npy'
NP_FILE_TEMPLATE = 'patch_references_{subset}.npz'

dataset_checksums = {
    1: {
        64: {
            'NORMvsDISTRESS': {
                'train': '8ff1685346ee4809836e2173e17ab006',
                'valid': 'a04203dd87cf3387c9c3831ef930c1e4',
                'test': '0aca7893c6fcef41afdfa819c01dcef5'
            }
        },
        'images': {
            'train': '7b3ed8c771848fb3e57f7806fd4dec00',
            'valid': '08503b47b25851728c32f0e05356f306',
            'test': '9214f64f4e9b2a97903577bf061135cd',
            'images': '8df7a86b6c5c04776a539001d893e047'
        }
    },
    2: {
        64: {
            'NORMvsDISTRESS': {
                'train': None,
                'valid': None,
                'valid-test': None,
                'test': None
            },
            'NORMvsDISTRESS_50k': {
                'train': '3396fb613eff8a9f3f19312648aff148',
                'valid': '3c9da15d00dabba64c8c6a6462fe86c5',
                'valid-test': 'a083b258d8a5bf6d80188aa19098843a',
                'test': '1ee0c06e353b1244ea3e9a8ed2e16c19'
            },
            'ZEB_50k': {
                'patch_issue': 'NORMvsDISTRESS_50k',
                'train': 'ec477d92cf195e2671bf731cccb986d6',
                'valid': '2cb5bacdabd60ef1db0c2f8764503681',
                'valid-test': '286c31c7c92874eb38a5ba3a75dbd883',
                'test': 'c6be0d8db9c10352d8241df163f98139'
            }
        },
        96: {
            'NORMvsDISTRESS': {
                'train': None,
                'valid': None,
                'valid-test': None,
                'test': None
            },
            'NORMvsDISTRESS_50k': {
                'train': 'a0778d6e7851f825991cbc18b8d1f125',
                'valid': '8799e9d69dd4e55c08e97821e25e77e0',
                'valid-test': 'ec8b268fb32ff624469c744c8338bc13',
                'test': '33f5d4f26537799278a6d76c5bd83d80'
            },
            'ZEB_50k': {
                'patch_issue': 'NORMvsDISTRESS_50k',
                'train': '09cbe11e8437c4eb779afcd350b7ebb1',
                'valid': '1b3ef7ef61a4e2cff1a11c02432be5fe',
                'valid-test': '1d4851403554318e6c7bf2bf9c4718bb',
                'test': 'cbb065a3590c759483b0bd0ee5315a96'
            }
        },
        128: {
            'NORMvsDISTRESS': {
                'train': None,
                'valid': None,
                'valid-test': None,
                'test': None
            },
            'NORMvsDISTRESS_50k': {
                'train': '804efd2969015eaa7042d66384d82d59',
                'valid': '447cd00cedd95bf52e6d9425f1840341',
                'valid-test': 'a8573ebd8fb143b398e8d5fb4e784298',
                'test': 'b95418da39e4a262a28da20389a101c6'
            },
            'ZEB_50k': {
                'patch_issue': 'NORMvsDISTRESS_50k',
                'train': '63025cf9b4b798764c3e774c9a87d923',
                'valid': '9e159a9658493996455386ddc1e701aa',
                'valid-test': 'ca53c470945a06d4b7fba222164ec6ce',
                'test': 'c5d18511ed7ede20cbaf6186f40e3728'
            }
        },
        160: {
            'NORMvsDISTRESS': {
                'train': None,
                'valid': None,
                'valid-test': None,
                'test': None
            },
            'NORMvsDISTRESS_50k': {
                'train': '3ce74ae6b55c06cca3d5bf3402122543',
                'valid': 'c96e88e51586e42ff7828d5e096d2169',
                'valid-test': 'd88dca6572fb0dc23c0e95d90d5f2c3a',
                'test': '452d7a13a57e7e614949bb2b0be3ada4'
            },
            'ZEB_50k': {
                'patch_issue': 'NORMvsDISTRESS_50k',
                'train': 'bba7a6feab43caea55a4eedad4aea15b',
                'valid': '44bd90b392559c633ab58180a2c28a39',
                'valid-test': 'f7376501ffe8a310d69b71244351f11a',
                'test': '6c6215208522fd03d791243ee05d772f'
            }
        },
        192: {
            'NORMvsDISTRESS': {
                'train': None,
                'valid': None,
                'valid-test': None,
                'test': None
            },
            'NORMvsDISTRESS_50k': {
                'train': 'dcc9aa1283abe977f9e69a48eba31fa5',
                'valid': '062cf7d3cf73a54150e584debe069abf',
                'valid-test': '4f600d32ead8c2ecf02320ba7a00dbb1',
                'test': '9b76923660258650fe2be09fef41540f'
            },
            'ZEB_50k': {
                'patch_issue': 'NORMvsDISTRESS_50k',
                'train': '4354ddfce9aef8f2c0810d31ef3d09a5',
                'valid': '6ae89117b8e6b6eac2ce0be230fb9ea7',
                'valid-test': '1e9d73c8bdf9b30cb88aac1c1168410e',
                'test': 'd5f2f1ebd57790d888c902a76cc603d3'
            }
        },
        224: {
            'NORMvsDISTRESS': {
                'train': None,
                'valid': None,
                'valid-test': None,
                'test': None
            },
            'NORMvsDISTRESS_50k': {
                'train': '6ff4637c7dad8a7bc489e50c1661f0f7',
                'valid': '8a06cf0faf585978a8aca3ae1438d252',
                'valid-test': 'f32e1e214dad47b2953e9be4b0eba969',
                'test': '4b0c98620ed039bb319ecf0eb3aaa39b'
            },
            'ZEB_50k': {
                'patch_issue': 'NORMvsDISTRESS_50k',
                'train': '9133eea9a0549bebd60dfbb657286cb2',
                'valid': '110c34e80babf6f5e7022bbc7ca3006e',
                'valid-test': 'e1ba0f668d4ad6cdf6d18a60cc82ecfc',
                'test': 'e97eac4496f203f61b89d2286d8e2c89'
            }
        },
        256: {
            'NORMvsDISTRESS': {
                'train': None,
                'valid': None,
                'valid-test': None,
                'test': None
            },
            'NORMvsDISTRESS_50k': {
                'train': '7d1cbdc73e8b69eebab9f27609fe55a2',
                'valid': 'd42ab3d11234f9666d95ca055f5e8205',
                'valid-test': '01cfee712bf2198761af33a20cb0e4e3',
                'test': 'edb031333d750a57207511731dcf9dbf'
            },
            'ZEB_50k': {
                'patch_issue': 'NORMvsDISTRESS_50k',
                'train': 'd848b85e0f08603c812356d124b8075d',
                'valid': '17e3086fb8763cd567e2fdb88efbf3fd',
                'valid-test': '6ca7cfb7fc89d763b61d49ea242886ce',
                'test': '0abd75e75b497703fa0b5a1639ccad81'
            }
        },
        'segmentation': {
            'train': '25dba4aa37166adba8e615bb10a2e7f2',
            'valid': '5b17054016d609a94bbaeb1964bfc97a',
            'valid-test': '12ea33a93b91a760049083398d8d0725',
            'test': 'b1575bff982df1810e42916898be033f',
            'images': '9a0a2cd547839a3591b88231ae96ec71'
        },
        'images': {
            'train': '6a0967d6c6e8a790a67ce0bab84fc24d',
            'valid': 'bffcd268805a93c117ef224c30419497',
            'valid-test': '20e9d57b3b8b52c386737ac43f02ddea',
            'test': '903f24bee45f3cdedecd0c9222c0d852',
            'images': '4dc24e4bf88cec16cb155c4f01b0bb31'
        }
    }
}
