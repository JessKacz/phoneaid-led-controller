
#include <FastLED.h>
#define NUM_LEDS 92
#define DATA_PIN 6
CRGB leds[NUM_LEDS];

void setup() {
  FastLED.addLeds<WS2812, DATA_PIN, GRB>(leds, NUM_LEDS);
}

void loop() {

  static uint8_t waveIndex = 0;
  for (int i = 0; i < NUM_LEDS; i++) {
    int relativePos = (i - waveIndex + NUM_LEDS) % NUM_LEDS;
    float blend = (relativePos < 48) ? (1.0 - float(relativePos) / 48) : 0.0;
    uint8_t r = uint8_t(255 * blend + 0 * (1.0 - blend));
    uint8_t g = uint8_t(0 * blend + 0 * (1.0 - blend));
    uint8_t b = uint8_t(0 * blend + 255 * (1.0 - blend));
    leds[i] = CRGB(r, g, b);
  }
  FastLED.show();
  delay(300);
  waveIndex = (waveIndex + 1) % NUM_LEDS;
}
