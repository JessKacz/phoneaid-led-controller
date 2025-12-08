from PyQt5.QtWidgets import QApplication
from app.config_manager import load_config
from app.ui.effects_tab import EffectsTab
import sys

app = QApplication([])
cfg = load_config()
win = EffectsTab()
# Apply config mapping and total
win.total_leds = cfg.get('total_leds', win.total_leds)
win.letter_mapping = {k.upper(): v for k, v in cfg.get('letters', {}).items()}

print('LETTER_KEYS:', list(win.letter_mapping.keys()))
print('TOTAL_LEDS:', win.total_leds)
print('LAST_LED_INDEX:', win.total_leds - 1)

# Ensure effect dropdown set to Onda
idx = win.effect_dropdown.findText('Onda')
if idx >= 0:
    win.effect_dropdown.setCurrentIndex(idx)
else:
    win.effect_dropdown.setCurrentIndex(2)

# Test several wave_index values
test_indices = [0, 1, max(0, win.total_leds - 1)]
for w in test_indices:
    win.wave_index = w
    win._generate_led_colors()
    arr = [c.name() for c in win.virtual_leds]
    print(f'wave_index={w} first5={arr[:5]} last5={arr[-5:]}')

# Continuity check: compare color at position 0 for wave_index 0 and wave_index total_leds
win.wave_index = 0
win._generate_led_colors()
c0 = win.virtual_leds[0].name()
win.wave_index = win.total_leds
win._generate_led_colors()
c1 = win.virtual_leds[0].name()
print('continuity_equal:', c0 == c1, c0, c1)

print('TEST_DONE')
sys.exit(0)
