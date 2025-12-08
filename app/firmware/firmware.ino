
#include <FastLED.h>
#define NUM_LEDS 270
#define DATA_PINS {2,3,4,5,6,7,8,9,10,11,12,13}
CRGB leds[NUM_LEDS];

void setup() {
  FastLED.addLeds<WS2812, 6, GRB>(leds, NUM_LEDS);
}

void loop() {
  fill_solid(leds, NUM_LEDS, CRGB::Blue);
  FastLED.show();
  delay(100);
}
