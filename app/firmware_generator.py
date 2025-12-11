"""
firmware_generator.py - Gera código Arduino customizado a partir de presets
"""
import os


class FirmwareGenerator:
    """
    Gera código Arduino (.ino) customizado baseado em configuração e presets.
    """
    
    FIRMWARE_TEMPLATE = '''
#include <FastLED.h>

#define NUM_LEDS {total_leds}
#define NUM_PORTS {num_ports}

// Portas de dados para cada saída de LEDs (referência)
const uint8_t DATA_PINS[NUM_PORTS] = {{{data_pins_array}}};

// Array de arrays para armazenar LEDs de cada porta
CRGB leds[NUM_PORTS][NUM_LEDS];

// Struct para definir cada efeito
struct Effect {{
    const char* name;
    uint8_t type;        // 0=Solid, 1=Gradient, 2=Wave
    uint8_t r1, g1, b1;
    uint8_t r2, g2, b2;
    uint16_t speed_ms;
    uint16_t wave_width;
}} effects[] = {{
{effect_definitions}
}};

#define NUM_EFFECTS (sizeof(effects) / sizeof(effects[0]))

uint8_t current_effect = 0;
uint32_t last_update = 0;
uint16_t wave_index = 0;

void setup() {{
    // Configura FastLED para todas as portas (chamadas geradas com pinos constantes)
{add_leds_calls}
    FastLED.setBrightness(255);
    Serial.begin(9600);
}}

void loop() {{
    apply_effect(effects[current_effect]);
    
    // Mostra efeito (FastLED.show atualiza todos os controladores registrados)
    FastLED.show();
    
    // Recebe comando serial se disponível
    if (Serial.available()) {{
        int effect_num = Serial.parseInt();
        if (effect_num >= 0 && effect_num < NUM_EFFECTS) {{
            current_effect = effect_num;
            wave_index = 0;
        }}
    }}
}}

void apply_effect(Effect& effect) {{
    uint32_t now = millis();
    if (now - last_update < effect.speed_ms) return;
    last_update = now;
    
    switch (effect.type) {{
        case 0:  // Cor Sólida
            apply_solid(effect);
            break;
        case 1:  // Gradiente
            apply_gradient(effect);
            break;
        case 2:  // Onda
            apply_wave(effect);
            break;
    }}
}}

void apply_solid(Effect& effect) {{
    CRGB color(effect.r1, effect.g1, effect.b1);
    for (int port = 0; port < NUM_PORTS; port++) {{
        fill_solid(leds[port], NUM_LEDS, color);
    }}
}}

void apply_gradient(Effect& effect) {{
    for (int port = 0; port < NUM_PORTS; port++) {{
        for (int i = 0; i < NUM_LEDS; i++) {{
            float t = (float)i / (float)(NUM_LEDS - 1);
            uint8_t r = (uint8_t)(effect.r1 * (1.0 - t) + effect.r2 * t);
            uint8_t g = (uint8_t)(effect.g1 * (1.0 - t) + effect.g2 * t);
            uint8_t b = (uint8_t)(effect.b1 * (1.0 - t) + effect.b2 * t);
            leds[port][i] = CRGB(r, g, b);
        }}
    }}
}}

void apply_wave(Effect& effect) {{
    uint16_t wave_width = effect.wave_width;
    
    for (int port = 0; port < NUM_PORTS; port++) {{
        for (int i = 0; i < NUM_LEDS; i++) {{
            int relative_pos = (i - wave_index + NUM_LEDS) % NUM_LEDS;
            float blend = 0.0;
            
            if (relative_pos < wave_width) {{
                blend = 1.0 - ((float)relative_pos / (float)wave_width);
            }}
            
            uint8_t r = (uint8_t)(effect.r1 * blend + effect.r2 * (1.0 - blend));
            uint8_t g = (uint8_t)(effect.g1 * blend + effect.g2 * (1.0 - blend));
            uint8_t b = (uint8_t)(effect.b1 * blend + effect.b2 * (1.0 - blend));
            
            leds[port][i] = CRGB(r, g, b);
        }}
    }}
    
    wave_index = (wave_index + 1) % NUM_LEDS;
}}
'''
    
    def __init__(self, total_leds, config):
        self.total_leds = total_leds
        self.config = config
    
    def generate_firmware(self, presets):
        """
        Gera código Arduino a partir de uma lista de presets.
        Retorna string com o código .ino pronto para upload.
        """
        # Gera definições dos efeitos
        effect_defs = self._generate_effect_definitions(presets)
        
        # Determina pinos usados (padrão: 2..7). Pode ser substituído via config['data_pins']
        default_pins = [2, 3, 4, 5, 6, 7]
        pins = self.config.get("data_pins", default_pins)
        # Limpa e garante inteiros
        pins = [int(p) for p in pins]
        num_ports = len(pins)
        data_pins_array = ", ".join(str(p) for p in pins)

        # Gera chamadas FastLED.addLeds com pinos constantes (necessário para o template do FastLED)
        add_calls_lines = []
        for idx, pin in enumerate(pins):
            add_calls_lines.append(f"    FastLED.addLeds<WS2812B, {pin}, GRB>(leds[{idx}], NUM_LEDS);")
        add_leds_calls = "\n".join(add_calls_lines)

        # Substitui no template
        firmware_code = self.FIRMWARE_TEMPLATE.format(
            total_leds=self.total_leds,
            num_ports=num_ports,
            data_pins_array=data_pins_array,
            add_leds_calls=add_leds_calls,
            effect_definitions=effect_defs
        )
        
        return firmware_code
    
    def _generate_effect_definitions(self, presets):
        """Gera as definições das structs dos efeitos"""
        definitions = []
        
        for i, preset in enumerate(presets):
            if not preset.get("ativo"):
                continue
            
            effect_type = self._get_effect_type_code(preset.get("tipo"))
            r1, g1, b1 = self._hex_to_rgb(preset.get("color1", "#FF0000"))
            r2, g2, b2 = self._hex_to_rgb(preset.get("color2", "#0000FF"))
            speed_ms = self._get_speed_ms(preset.get("velocidade", "Médio"))
            wave_width = preset.get("wave_width", 10)
            
            definition = (
                f'    {{"{preset.get("nome_mes", f"Preset {i}")}", {effect_type}, '
                f'{r1}, {g1}, {b1}, {r2}, {g2}, {b2}, {speed_ms}, {wave_width}}}'
            )
            definitions.append(definition)
        
        return ",\n".join(definitions) if definitions else '    {"Default", 0, 255, 0, 0, 0, 0, 0, 300, 0}'
    
    def _get_effect_type_code(self, effect_type):
        """Mapeia tipo de efeito para código numérico"""
        mapping = {
            "Cor sólida": 0,
            "Gradiente": 1,
            "Onda": 2
        }
        return mapping.get(effect_type, 0)
    
    def _hex_to_rgb(self, hex_color):
        """Converte cor hex (#RRGGBB) para RGB tuple"""
        hex_color = hex_color.lstrip("#")
        if len(hex_color) == 6:
            return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        return (255, 0, 0)  # Padrão: vermelho
    
    def _get_speed_ms(self, speed_label):
        """Mapeia label de velocidade para milissegundos"""
        mapping = {
            "Lento": 300,
            "Médio": 150,
            "Rápido": 70,
            "Turbo": 30
        }
        return mapping.get(speed_label, 150)
    
    def save_firmware(self, presets, output_file=None):
        """Salva firmware em arquivo .ino"""
        if output_file is None:
            output_file = os.path.join(
                os.path.dirname(__file__), "firmware", "firmware.ino"
            )
        
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        firmware_code = self.generate_firmware(presets)
        
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(firmware_code)
        
        return output_file
