# randomname.py - topic extension
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
"""random topic generator utils
"""

import random

animals = [
    b'aardvark',
    b'albatross',
    b'alligator',
    b'alpaca',
    b'ant',
    b'anteater',
    b'antelope',
    b'ape',
    b'armadillo',
    b'baboon',
    b'badger',
    b'barracuda',
    b'bat',
    b'bear',
    b'beaver',
    b'bee',
    b'beetle',
    b'bison',
    b'boar',
    b'buffalo',
    b'bushbaby',
    b'bustard',
    b'butterfly',
    b'camel',
    b'capuchin',
    b'carabao',
    b'caribou',
    b'cat',
    b'caterpillar',
    b'cattle',
    b'chameleon',
    b'chamois',
    b'cheetah',
    b'chicken',
    b'chimpanzee',
    b'chinchilla',
    b'chipmunk',
    b'chough',
    b'cicada',
    b'clam',
    b'cobra',
    b'cockroach',
    b'cod',
    b'cormorant',
    b'coyote',
    b'crab',
    b'crane',
    b'cricket',
    b'crocodile',
    b'crow',
    b'curlew',
    b'deer',
    b'dinosaur',
    b'dog',
    b'dogfish',
    b'dolphin',
    b'donkey',
    b'dotterel',
    b'dove',
    b'dragon',
    b'dragonfly',
    b'duck',
    b'dugong',
    b'dunlin',
    b'eagle',
    b'echidna',
    b'eel',
    b'eland',
    b'elephant',
    b'elk',
    b'emu',
    b'falcon',
    b'ferret',
    b'finch',
    b'fish',
    b'flamingo',
    b'fly',
    b'fox',
    b'frog',
    b'gaur',
    b'gazelle',
    b'gecko',
    b'gerbil',
    b'giraffe',
    b'gnat',
    b'gnu',
    b'goat',
    b'goldfish',
    b'goose',
    b'gorilla',
    b'goshawk',
    b'grasshopper',
    b'grouse',
    b'guanaco',
    b'guinea',
    b'gull',
    b'hamster',
    b'hare',
    b'hawk',
    b'hedgehog',
    b'heron',
    b'herring',
    b'hippopotamus',
    b'hornet',
    b'horse',
    b'horsecrab',
    b'hound',
    b'hummingbird',
    b'hyena',
    b'hyrax',
    b'ibex',
    b'ibis',
    b'iguana',
    b'impala',
    b'insect',
    b'jackal',
    b'jaguar',
    b'jay',
    b'jellyfish',
    b'kangaroo',
    b'koala',
    b'kouprey',
    b'kudu',
    b'lapwing',
    b'lark',
    b'lemming',
    b'lemur',
    b'leopard',
    b'lion',
    b'lizard',
    b'llama',
    b'lobster',
    b'locust',
    b'loris',
    b'louse',
    b'lynx',
    b'lyrebird',
    b'magpie',
    b'mallard',
    b'mammoth',
    b'manatee',
    b'marten',
    b'meerkat',
    b'mink',
    b'minnow',
    b'mole',
    b'mongoose',
    b'monkey',
    b'moose',
    b'mosquito',
    b'mouse',
    b'mule',
    b'muskrat',
    b'narwhal',
    b'newt',
    b'nightingale',
    b'numbat',
    b'octopus',
    b'okapi',
    b'opossum',
    b'oryx',
    b'ostrich',
    b'otter',
    b'owl',
    b'ox',
    b'oyster',
    b'panda',
    b'panther',
    b'parrot',
    b'partridge',
    b'peacock',
    b'peafowl',
    b'pelican',
    b'penguin',
    b'pheasant',
    b'pig',
    b'pigeon',
    b'platypus',
    b'pony',
    b'porcupine',
    b'porpoise',
    b'puffin',
    b'pug',
    b'quagga',
    b'quail',
    b'quelea',
    b'rabbit',
    b'raccoon',
    b'ram',
    b'rat',
    b'raven',
    b'reindeer',
    b'rhea',
    b'rhinoceros',
    b'rook',
    b'ruff',
    b'salamander',
    b'salmon',
    b'sambar',
    b'sandpiper',
    b'sardine',
    b'scorpion',
    b'seahorse',
    b'seal',
    b'serval',
    b'shark',
    b'sheep',
    b'shrew',
    b'shrimp',
    b'skink',
    b'skunk',
    b'snail',
    b'snake',
    b'spider',
    b'squid',
    b'squirrel',
    b'starling',
    b'stinkbug',
    b'stork',
    b'swan',
    b'tapir',
    b'tarsier',
    b'termite',
    b'tern',
    b'tiger',
    b'toad',
    b'trout',
    b'turkey',
    b'turtle',
    b'unicorn',
    b'viper',
    b'vulture',
    b'wallaby',
    b'walrus',
    b'wasp',
    b'weasel',
    b'whale',
    b'wolf',
    b'wolverine',
    b'wombat',
    b'woodchuck',
    b'woodcock',
    b'woodpecker',
    b'worm',
    b'wren',
    b'yak',
    b'zebra',
    b'zorilla'
]

adjectives = [
    b'abiding',
    b'abject',
    b'ablaze',
    b'able',
    b'aboard',
    b'abounding',
    b'absorbed',
    b'absorbing',
    b'abstracted',
    b'abundant',
    b'acceptable',
    b'accessible',
    b'accurate',
    b'acoustic',
    b'adamant',
    b'adaptable',
    b'adhesive',
    b'adjoining',
    b'adorable',
    b'adventurous',
    b'affable',
    b'affectionate',
    b'agreeable',
    b'alert',
    b'alive',
    b'alluring',
    b'amazing',
    b'ambiguous',
    b'ambitious',
    b'amiable',
    b'amicable',
    b'amused',
    b'amusing',
    b'ancient',
    b'animated',
    b'apricot',
    b'appropriate',
    b'aquatic',
    b'arctic',
    b'arenaceous',
    b'aromatic',
    b'aspiring',
    b'assiduous',
    b'assorted',
    b'astonishing',
    b'attractive',
    b'auspicious',
    b'automatic',
    b'available',
    b'average',
    b'awake',
    b'aware',
    b'awesome',
    b'axiomatic',
    b'bashful',
    b'bawdy',
    b'beautiful',
    b'beefy',
    b'befitting',
    b'beneficial',
    b'benevolent',
    b'bent',
    b'best',
    b'better',
    b'bewildered',
    b'bewitching',
    b'big',
    b'billowy',
    b'bizarre',
    b'black',
    b'blithe',
    b'blue',
    b'blushing',
    b'bouncy',
    b'boundless',
    b'brainy',
    b'brash',
    b'brave',
    b'brawny',
    b'brazen',
    b'breezy',
    b'brief',
    b'bright',
    b'brilliant',
    b'broad',
    b'brown',
    b'bucolic',
    b'bulky',
    b'bumpy',
    b'burgundy',
    b'burly',
    b'bustling',
    b'busy',
    b'calm',
    b'capable',
    b'capricious',
    b'captivating',
    b'carefree',
    b'careful',
    b'caring',
    b'carrot',
    b'ceaseless',
    b'cerise',
    b'certain',
    b'challenging',
    b'changeable',
    b'charming',
    b'cheerful',
    b'chief',
    b'chilly',
    b'chipper',
    b'classy',
    b'clean',
    b'clear',
    b'clever',
    b'cloudy',
    b'coherent',
    b'colorful',
    b'colossal',
    b'comfortable',
    b'common',
    b'communicative',
    b'compassionate',
    b'complete',
    b'complex',
    b'compulsive',
    b'confused',
    b'conscientious',
    b'conscious',
    b'conservative',
    b'considerate',
    b'convivial',
    b'cooing',
    b'cool',
    b'cooperative',
    b'coordinated',
    b'courageous',
    b'courteous',
    b'crazy',
    b'creative',
    b'crispy',
    b'crooked',
    b'crowded',
    b'cuddly',
    b'cultured',
    b'cunning',
    b'curious',
    b'curly',
    b'curved',
    b'curvy',
    b'cut',
    b'cute',
    b'daily',
    b'damp',
    b'dapper',
    b'dashing',
    b'dazzling',
    b'dear',
    b'debonair',
    b'decisive',
    b'decorous',
    b'deep',
    b'defiant',
    b'delicate',
    b'delicious',
    b'delighted',
    b'delightful',
    b'delirious',
    b'descriptive',
    b'detached',
    b'detailed',
    b'determined',
    b'different',
    b'diligent',
    b'diminutive',
    b'diplomatic',
    b'discreet',
    b'distinct',
    b'distinctive',
    b'dramatic',
    b'dry',
    b'dynamic',
    b'dynamite',
    b'eager',
    b'early',
    b'earthy',
    b'easy',
    b'easygoing',
    b'eatable',
    b'economic',
    b'ecstatic',
    b'educated',
    b'efficacious',
    b'efficient',
    b'effortless',
    b'eight',
    b'elastic',
    b'elated',
    b'electric',
    b'elegant',
    b'elfin',
    b'elite',
    b'eminent',
    b'emotional',
    b'enchanted',
    b'enchanting',
    b'encouraging',
    b'endless',
    b'energetic',
    b'enormous',
    b'entertaining',
    b'enthusiastic',
    b'envious',
    b'epicurean',
    b'equable',
    b'equal',
    b'eternal',
    b'ethereal',
    b'evanescent',
    b'even',
    b'excellent',
    b'excited',
    b'exciting',
    b'exclusive',
    b'exotic',
    b'expensive',
    b'exquisite',
    b'extroverted',
    b'exuberant',
    b'exultant',
    b'fabulous',
    b'fair',
    b'faithful',
    b'familiar',
    b'famous',
    b'fancy',
    b'fantastic',
    b'far',
    b'fascinated',
    b'fast',
    b'fearless',
    b'female',
    b'fertile',
    b'festive',
    b'few',
    b'fine',
    b'first',
    b'five',
    b'fixed',
    b'flamboyant',
    b'flashy',
    b'flat',
    b'flawless',
    b'flirtatious',
    b'florid',
    b'flowery',
    b'fluffy',
    b'fluttering',
    b'foamy',
    b'foolish',
    b'foregoing',
    b'fortunate',
    b'four',
    b'frank',
    b'free',
    b'frequent',
    b'fresh',
    b'friendly',
    b'full',
    b'functional',
    b'funny',
    b'furry',
    b'future',
    b'futuristic',
    b'fuzzy',
    b'gabby',
    b'gainful',
    b'garrulous',
    b'general',
    b'generous',
    b'gentle',
    b'giant',
    b'giddy',
    b'gifted',
    b'gigantic',
    b'gilded',
    b'glamorous',
    b'gleaming',
    b'glorious',
    b'glossy',
    b'glowing',
    b'godly',
    b'good',
    b'goofy',
    b'gorgeous',
    b'graceful',
    b'grandiose',
    b'grateful',
    b'gratis',
    b'gray',
    b'great',
    b'green',
    b'gregarious',
    b'grey',
    b'groovy',
    b'guiltless',
    b'gusty',
    b'guttural',
    b'habitual',
    b'half',
    b'hallowed',
    b'halting',
    b'handsome',
    b'happy',
    b'hard',
    b'hardworking',
    b'harmonious',
    b'heady',
    b'healthy',
    b'heavenly',
    b'helpful',
    b'hilarious',
    b'historical',
    b'holistic',
    b'hollow',
    b'honest',
    b'honorable',
    b'hopeful',
    b'hospitable',
    b'hot',
    b'huge',
    b'humorous',
    b'hungry',
    b'hushed',
    b'hypnotic',
    b'illustrious',
    b'imaginary',
    b'imaginative',
    b'immense',
    b'imminent',
    b'impartial',
    b'important',
    b'imported',
    b'impossible',
    b'incandescent',
    b'inconclusive',
    b'incredible',
    b'independent',
    b'industrious',
    b'inexpensive',
    b'innate',
    b'innocent',
    b'inquisitive',
    b'instinctive',
    b'intellectual',
    b'intelligent',
    b'intense',
    b'interesting',
    b'internal',
    b'intuitive',
    b'inventive',
    b'invincible',
    b'jazzy',
    b'jolly',
    b'joyful',
    b'joyous',
    b'judicious',
    b'juicy',
    b'jumpy',
    b'keen',
    b'kind',
    b'kindhearted',
    b'kindly',
    b'knotty',
    b'knowing',
    b'knowledgeable',
    b'known',
    b'laconic',
    b'large',
    b'lavish',
    b'lean',
    b'learned',
    b'left',
    b'legal',
    b'level',
    b'light',
    b'likeable',
    b'literate',
    b'little',
    b'lively',
    b'living',
    b'long',
    b'longing',
    b'loud',
    b'lovely',
    b'loving',
    b'loyal',
    b'lucky',
    b'luminous',
    b'lush',
    b'luxuriant',
    b'luxurious',
    b'lyrical',
    b'magenta',
    b'magical',
    b'magnificent',
    b'majestic',
    b'male',
    b'mammoth',
    b'many',
    b'marvelous',
    b'massive',
    b'material',
    b'mature',
    b'meandering',
    b'meaty',
    b'medical',
    b'mellow',
    b'melodic',
    b'melted',
    b'merciful',
    b'mighty',
    b'miniature',
    b'miniscule',
    b'minor',
    b'minute',
    b'misty',
    b'modern',
    b'modest',
    b'momentous',
    b'motionless',
    b'mountainous',
    b'mute',
    b'mysterious',
    b'narrow',
    b'natural',
    b'near',
    b'neat',
    b'nebulous',
    b'necessary',
    b'neighborly',
    b'new',
    b'next',
    b'nice',
    b'nifty',
    b'nimble',
    b'nine',
    b'nippy',
    b'noiseless',
    b'noisy',
    b'nonchalant',
    b'normal',
    b'numberless',
    b'numerous',
    b'nutritious',
    b'obedient',
    b'observant',
    b'obtainable',
    b'oceanic',
    b'omniscient',
    b'one',
    b'open',
    b'opposite',
    b'optimal',
    b'optimistic',
    b'opulent',
    b'orange',
    b'ordinary',
    b'organic',
    b'outgoing',
    b'outrageous',
    b'outstanding',
    b'oval',
    b'overjoyed',
    b'overt',
    b'palatial',
    b'panoramic',
    b'parallel',
    b'passionate',
    b'past',
    b'pastoral',
    b'patient',
    b'peaceful',
    b'perfect',
    b'periodic',
    b'permissible',
    b'perpetual',
    b'persistent',
    b'petite',
    b'philosophical',
    b'physical',
    b'picturesque',
    b'pink',
    b'pioneering',
    b'piquant',
    b'plausible',
    b'pleasant',
    b'plucky',
    b'poised',
    b'polite',
    b'possible',
    b'powerful',
    b'practical',
    b'precious',
    b'premium',
    b'present',
    b'pretty',
    b'previous',
    b'private',
    b'probable',
    b'productive',
    b'profound',
    b'profuse',
    b'protective',
    b'proud',
    b'psychedelic',
    b'public',
    b'pumped',
    b'purple',
    b'purring',
    b'puzzled',
    b'puzzling',
    b'quaint',
    b'quick',
    b'quicker',
    b'quickest',
    b'quiet',
    b'quirky',
    b'quixotic',
    b'quizzical',
    b'rainy',
    b'rapid',
    b'rare',
    b'rational',
    b'ready',
    b'real',
    b'rebel',
    b'receptive',
    b'red',
    b'reflective',
    b'regular',
    b'relaxed',
    b'reliable',
    b'relieved',
    b'remarkable',
    b'reminiscent',
    b'reserved',
    b'resolute',
    b'resonant',
    b'resourceful',
    b'responsible',
    b'rich',
    b'ridiculous',
    b'right',
    b'rightful',
    b'ripe',
    b'ritzy',
    b'roasted',
    b'robust',
    b'romantic',
    b'roomy',
    b'round',
    b'royal',
    b'ruddy',
    b'rural',
    b'rustic',
    b'sable',
    b'safe',
    b'salty',
    b'same',
    b'satisfying',
    b'savory',
    b'scientific',
    b'scintillating',
    b'scrumptious',
    b'second',
    b'secret',
    b'secretive',
    b'seemly',
    b'selective',
    b'sensible',
    b'separate',
    b'shaggy',
    b'shaky',
    b'shining',
    b'shiny',
    b'short',
    b'shy',
    b'silent',
    b'silky',
    b'silly',
    b'simple',
    b'simplistic',
    b'sincere',
    b'six',
    b'sizzling',
    b'skillful',
    b'sleepy',
    b'slick',
    b'slim',
    b'smart',
    b'smiling',
    b'smooth',
    b'soaring',
    b'sociable',
    b'soft',
    b'solid',
    b'sophisticated',
    b'sparkling',
    b'special',
    b'spectacular',
    b'speedy',
    b'spicy',
    b'spiffy',
    b'spiritual',
    b'splendid',
    b'spooky',
    b'spotless',
    b'spotted',
    b'square',
    b'standing',
    b'statuesque',
    b'steadfast',
    b'steady',
    b'steep',
    b'stimulating',
    b'straight',
    b'straightforward',
    b'striking',
    b'striped',
    b'strong',
    b'stunning',
    b'stupendous',
    b'sturdy',
    b'subsequent',
    b'substantial',
    b'subtle',
    b'successful',
    b'succinct',
    b'sudden',
    b'super',
    b'superb',
    b'supreme',
    b'swanky',
    b'sweet',
    b'swift',
    b'sympathetic',
    b'synonymous',
    b'talented',
    b'tall',
    b'tame',
    b'tan',
    b'tangible',
    b'tangy',
    b'tasteful',
    b'tasty',
    b'telling',
    b'temporary',
    b'tempting',
    b'ten',
    b'tender',
    b'terrific',
    b'tested',
    b'thankful',
    b'therapeutic',
    b'thin',
    b'thinkable',
    b'third',
    b'thoughtful',
    b'three',
    b'thrifty',
    b'tidy',
    b'tiny',
    b'toothsome',
    b'towering',
    b'tranquil',
    b'tremendous',
    b'tricky',
    b'true',
    b'truthful',
    b'two',
    b'typical',
    b'ubiquitous',
    b'ultra',
    b'unassuming',
    b'unbiased',
    b'uncovered',
    b'understanding',
    b'understood',
    b'unequaled',
    b'unique',
    b'unusual',
    b'unwritten',
    b'upbeat',
    b'useful',
    b'utopian',
    b'utter',
    b'uttermost',
    b'valuable',
    b'various',
    b'vast',
    b'verdant',
    b'vermilion',
    b'versatile',
    b'versed',
    b'victorious',
    b'vigorous',
    b'violet',
    b'vivacious',
    b'voiceless',
    b'voluptuous',
    b'wacky',
    b'waiting',
    b'wakeful',
    b'wandering',
    b'warm',
    b'warmhearted',
    b'wealthy',
    b'whimsical',
    b'whispering',
    b'white',
    b'whole',
    b'wholesale',
    b'whopping',
    b'wide',
    b'wiggly',
    b'wild',
    b'willing',
    b'windy',
    b'winsome',
    b'wiry',
    b'wise',
    b'wistful',
    b'witty',
    b'womanly',
    b'wonderful',
    b'workable',
    b'young',
    b'youthful',
    b'yummy',
    b'zany',
    b'zealous',
    b'zesty',
    b'zippy'
]

def randomtopicname(ui):
    # Re-implement random.choice() in the way it was written in Python 2.
    def choice(things):
        return things[int(len(things) * random.random())]
    if ui.configint(b"devel", b"randomseed"):
        random.seed(ui.configint(b"devel", b"randomseed"))
    return choice(adjectives) + b"-" + choice(animals)
