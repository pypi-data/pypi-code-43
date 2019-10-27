'''
Ocarina targets
'''

__all__ = 'LOCATIONS',


LOCATIONS = {
    'Ocarina': {
        'type': 'area',
        'link': {
            'West Lower Mount Hebra': [('nosettings', 'inverted')],
            'East Light World': [('nosettings', 'inverted')],
            'Kakariko': [('nosettings', 'inverted')],
            'South Light World': [('nosettings', 'inverted')],
            'East Light World': [('nosettings', 'inverted')],
            'Desert Portal (LW)': [('nosettings', 'inverted')],
            'Southern Shores': [('nosettings', 'inverted')],

            'West Lower Death Mountain': [('settings', 'inverted')],
            'River Shop Area': [('settings', 'inverted')],
            "Thieves' Town Surface": [('settings', 'inverted')],
            'South Dark World': [('settings', 'inverted')],
            'East Dark World': [('settings', 'inverted')],
            'Desert Portal (DW)': [('settings', 'inverted')],
            'Eastern Shores': [('settings', 'inverted')],
        }
    },

    'Light Bottle Ocarina': {
        'type': 'area',
        'link': {
            'West Lower Mount Hebra': [('and', [
                ('glitch', 'major'), ('item', 'bottle')])],
            'East Light World': [('and', [
                ('glitch', 'major'), ('item', 'bottle')])],
            'Kakariko': [('and', [
                ('glitch', 'major'), ('item', 'bottle')])],
            'South Light World': [('and', [
                ('glitch', 'major'), ('item', 'bottle')])],
            'East Light World': [('and', [
                ('glitch', 'major'), ('item', 'bottle')])],
            'Desert Portal (LW)': [('and', [
                ('glitch', 'major'), ('item', 'bottle')])],
            'Southern Shores': [('and', [
                ('glitch', 'major'), ('item', 'bottle')])]}
    },

    'Dark Bottle Ocarina': {
        'type': 'area',
        'link': {
            'West Lower Death Mountain': [('and', [
                ('glitch', 'major'), ('item', 'bottle')])],
            'River Shop Area': [('and', [
                ('glitch', 'major'), ('item', 'bottle')])],
            "Thieves' Town Surface": [('and', [
                ('glitch', 'major'), ('item', 'bottle')])],
            'South Dark World': [('and', [
                ('glitch', 'major'), ('item', 'bottle')])],
            'East Dark World': [('and', [
                ('glitch', 'major'), ('item', 'bottle')])],
            'Desert Portal (DW)': [('and', [
                ('glitch', 'major'), ('item', 'bottle')])],
            'Eastern Shores': [('and', [
                ('glitch', 'major'), ('item', 'bottle')])]}
    },
}
