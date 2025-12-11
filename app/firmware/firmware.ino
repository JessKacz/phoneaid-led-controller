
#include <FastLED.h>

#define NUM_LEDS 46
#define NUM_PORTS 6

// Portas de dados para cada saída de LEDs (referência)
const uint8_t DATA_PINS[NUM_PORTS] = {2, 3, 4, 5, 6, 7};

// Array de arrays para armazenar LEDs de cada porta
CRGB leds[NUM_PORTS][NUM_LEDS];

// Struct para definir cada efeito
struct Effect {
    const char* name;
    uint8_t type;        // 0=Solid, 1=Gradient, 2=Wave
    uint8_t r1, g1, b1;
    uint8_t r2, g2, b2;
    uint16_t speed_ms;
    uint16_t wave_width;
} effects[] = {
    {"Default", 0, 255, 0, 0, 0, 0, 0, 300, 0}
};

#define NUM_EFFECTS (sizeof(effects) / sizeof(effects[0]))

uint8_t current_effect = 0;
uint32_t last_update = 0;
uint16_t wave_index = 0;

void setup() {
    // Configura FastLED para todas as portas (chamadas geradas com pinos constantes)
    FastLED.addLeds<WS2812B, 2, GRB>(leds[0], NUM_LEDS);
    FastLED.addLeds<WS2812B, 3, GRB>(leds[1], NUM_LEDS);
    FastLED.addLeds<WS2812B, 4, GRB>(leds[2], NUM_LEDS);
    FastLED.addLeds<WS2812B, 5, GRB>(leds[3], NUM_LEDS);
    FastLED.addLeds<WS2812B, 6, GRB>(leds[4], NUM_LEDS);
    FastLED.addLeds<WS2812B, 7, GRB>(leds[5], NUM_LEDS);
    FastLED.setBrightness(255);
    Serial.begin(9600);
}

void loop() {
    apply_effect(effects[current_effect]);
    
    // Mostra efeito (FastLED.show atualiza todos os controladores registrados)
    FastLED.show();
    
    // Recebe comando serial se disponível
    if (Serial.available()) {
        int effect_num = Serial.parseInt();
        if (effect_num >= 0 && effect_num < NUM_EFFECTS) {
            current_effect = effect_num;
            wave_index = 0;
        }
    }
}

void apply_effect(Effect& effect) {
    uint32_t now = millis();
    if (now - last_update < effect.speed_ms) return;
    last_update = now;
    
    switch (effect.type) {
        case 0:  // Cor Sólida
            apply_solid(effect);
            break;
        case 1:  // Gradiente
            apply_gradient(effect);
            break;
        case 2:  // Onda
            apply_wave(effect);
            break;
    }
}

void apply_solid(Effect& effect) {
    CRGB color(effect.r1, effect.g1, effect.b1);
    for (int port = 0; port < NUM_PORTS; port++) {
        fill_solid(leds[port], NUM_LEDS, color);
    }
}

void apply_gradient(Effect& effect) {
    for (int port = 0; port < NUM_PORTS; port++) {
        for (int i = 0; i < NUM_LEDS; i++) {
            float t = (float)i / (float)(NUM_LEDS - 1);
            uint8_t r = (uint8_t)(effect.r1 * (1.0 - t) + effect.r2 * t);
            uint8_t g = (uint8_t)(effect.g1 * (1.0 - t) + effect.g2 * t);
            uint8_t b = (uint8_t)(effect.b1 * (1.0 - t) + effect.b2 * t);
            leds[port][i] = CRGB(r, g, b);
        }
    }
}

void apply_wave(Effect& effect) {
    uint16_t wave_width = effect.wave_width;
    
    for (int port = 0; port < NUM_PORTS; port++) {
        for (int i = 0; i < NUM_LEDS; i++) {
            int relative_pos = (i - wave_index + NUM_LEDS) % NUM_LEDS;
            float blend = 0.0;
            
            if (relative_pos < wave_width) {
                blend = 1.0 - ((float)relative_pos / (float)wave_width);
            }
            
            uint8_t r = (uint8_t)(effect.r1 * blend + effect.r2 * (1.0 - blend));
            uint8_t g = (uint8_t)(effect.g1 * blend + effect.g2 * (1.0 - blend));
            uint8_t b = (uint8_t)(effect.b1 * blend + effect.b2 * (1.0 - blend));
            
            leds[port][i] = CRGB(r, g, b);
        }
    }
    
    wave_index = (wave_index + 1) % NUM_LEDS;
}
