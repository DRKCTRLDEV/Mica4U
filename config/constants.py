DEFAULT_CONFIG = {
    'config': {
        'effect': '1',
        'clearAddress': 'true',
        'clearBarBg': 'true',
        'clearWinUIBg': 'true',
        'showLine': 'false'
    },
    'light': {'r': '255', 'g': '255', 'b': '255', 'a': '200'},
    'dark': {'r': '0', 'g': '0', 'b': '0', 'a': '120'},
    'gui': {
        'windowwidth': '400',
        'windowheight': '550',
        'windowbaseheight': '550',
        'showUnsupportedEffects': 'false'
    },
    'presets': {
        'Light Mode': {
            'r': '220', 'g': '220', 'b': '220', 'a': '160'
        },
        'Dark Mode': {
            'r': '0', 'g': '0', 'b': '0', 'a': '120'
        }
    }
}

DEFAULT_PRESETS = ['Light Mode', 'Dark Mode']

REQUIRED_FILES = {
    'ExplorerBlurMica.dll': 'DLL for transparency effects',
    'Initialise.cmd': 'Initialization script'
}

STYLE_EFFECTS = [
    ("Acrylic", "1", "Win10/11 • Blur with noise • Color customizable",
     lambda v: True, None),
    ("Blur", "0", "Win11 22H2 or earlier • Classic blur • Color customizable", 
     lambda v: v['is_win11_22h2_or_earlier'], "Requires Win11 22H2 or earlier"),
    ("Blur (Clear)", "3", "Win10/11 • Clean blur • Color customizable",
     lambda v: True, None),
    ("Mica", "2", "Win11 only • System colors • No customization",
     lambda v: v['is_win11'], "Requires Win11"),
    ("Mica Alt", "4", "Win11 only • Alt. system colors • No customization",
     lambda v: v['is_win11'], "Requires Win11")
] 