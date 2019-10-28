
"""

- Universal representation of particle decays and decay chains.
- Easy visualisation of decay chains with DOT graphs.
- Storage in particular via the dictionary-like representation.

Set of classes to provide a universal representation of decay chains
and particle decays.

The representation is easily stored on file, in particular via the
dictionary-like representation.


import yaml
def to_yaml(dc_as_dict):
    return yaml.dump(dc_as_dict)


1) decays of a given particle:
  Decays = mother + list of DecayMode's

--> Decay = Decays instance where len(DecayMode's)=1

2) DecayChain A -> B C, C -> D E
   --> chain = list of Decay instances
   --> Decay list elm # 0 is A -> B C, elm # 1 is C -> D E, etc.

--> a "Decay" statement in a .dec file becomes a Decays instance

3) given a top-level (mother) particle, "flatten" the decay chains possible
(give list if particles to consider stable)
mother -> get daughters -> for each daughter with decays defined,
add daughters to dict of daughters


AllowedDecays.decay_of = particle
             .decays = list of DecayMode instances

DecayChain - list of DecayMode instances

Decays - all allowed / described decay modes of a given particle

DecayMode: my dict as given by parser.build_decay_chain for a single decay in the chain

DaughterList          DaughtersDict
AllowedDecays         Decays
Decay                 DecayMode

DecayMode.charge_conjugate('B0 -> K+ pi-')

D*+ -> D0 pi+
       |-> K- pi+   (visible BF = ...)
"""

"""
class Decays(object):
    def __init__(self, particle):
        self.decays_of = particle
        self.decay_modes = []


def Tree_to_Decays(decay_tree):
    if not isinstance(decay_tree, Tree) or decay_tree.data != 'decay':
        raise RuntimeError("Input not an instance of a 'decay' Tree!")

    mother_name = decay_tree.children[0].children[0].value

    decays = Decays(mother_name)
    decays.decays = []

    decay_modes = tuple(decay_tree.find_data('decayline'))
    for decay_mode in decay_modes:
        bf = float(decay_mode.children[0].children[0].value)
        fsps = list(decay_mode.find_data('particle'))
        fsp_names = [fsp.children[0].value for fsp in fsps]
        lm = list(decay_mode.find_data('model'))
        model = lm[0].children[0].value
        lmo = list(decay_mode.find_data('model_options'))
        model_params = [float(tree.children[0].value) for tree in lmo[0].children] if len(lmo) == 1 else ''

        decays.decays.append(DecayMode(bf, fsp_names))

    return decays

t = Tree('decay', [Tree('particle', [Token('LABEL', 'D0')]), Tree('decayline', [Tree('value', [Token('SIGNED_NUMBER', '1.0')]), Tree('particle', [Token('LABEL', 'K-')]), Tree('particle', [Token('LABEL', 'pi+')]), Tree('model', [Token('MODEL_NAME', 'PHSP')])])])
d = Tree_to_Decays(t)

In [46]: d.decay_of
Out[46]: 'D0'

In [47]: d.decays
Out[47]: [<DecayMode: daughters=K- pi+, BF=1.0>]
"""


class DecayModeList():
    """
    Output from parsing a decay file. The class holds a list of decay modes
    of a given mother particle.
    """
    def __init__(self, mother, decay_modes):
        self.mother = mother
        self.decay_modes = decay_modes

    def flatten(self):
        """
        A flatten dictionary of decay modes, where the single key
        is the mother particle.
        """
        m = self.mother
        d = {m:[]}
        for dm in self.decay_modes:
            d[m].append(dm.to_dict())

        return d
