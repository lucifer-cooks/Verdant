"""Central runtime configuration for the VERDANT extension layer."""

VERDANT_CONFIG = {
    'project_name': 'VERDANT',
    'foundation': 'minecraft-python-indev-20100223',
    'foundation_tag': 'baseline-original-working-indev-20100223',
    'enabled': True,
    'safe_mode': True,
    'extension_layer': 'minimal-noop-bridge',
    'simulation': {
        'enabled': True,
        'speed': 1,
        'seed': 0,
        'deterministic': True,
        'debug': False,
    },
    'compatibility': {
        'legacy_game': 'Minecraft Indev 20100223',
        'must_not_rewrite': [
            'rendering',
            'world generation',
            'player physics',
            'inventory',
            'crafting',
            'entity systems',
        ],
    },
}
