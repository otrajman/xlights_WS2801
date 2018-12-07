# Simple demo of of the WS2801/SPI-like addressable RGB LED lights.
import time
import math
import RPi.GPIO as GPIO
 
# Import the WS2801 module.
import Adafruit_WS2801
import Adafruit_GPIO.SPI as SPI
 
 
# Configure the count of pixels:
PIXEL_COUNT = 125
 
# Alternatively specify a hardware SPI connection on /dev/spidev0.0:
SPI_PORT   = 0
SPI_DEVICE = 0

WHITE = (0xd0,0xd0,0xd0)
BLACK = (0,0,0)
RED = (0xff,0,0)
ORANGE = (0xff, 0x20, 0x00)
YELLOW = (0xff,0xff,0)
GREEN = (0,0xff,0)
BLUE = (0,0,0xff)
VIOLET = (0xff,0,0xff)

class Pixels():
    def __init__(self):
        self.pixels = Adafruit_WS2801.WS2801Pixels(PIXEL_COUNT, spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE), gpio=GPIO)

    # Define the wheel function to interpolate between different hues.
    def wheel(self, pos):
        if pos < 85:
            return Adafruit_WS2801.RGB_to_color(pos * 3, 255 - pos * 3, 0)
        elif pos < 170:
            pos -= 85
            return Adafruit_WS2801.RGB_to_color(255 - pos * 3, 0, pos * 3)
        else:
            pos -= 170
            return Adafruit_WS2801.RGB_to_color(0, pos * 3, 255 - pos * 3)

    def color_step(self, color1, color2, pct):
        """Return a color that is pct from color1 to color2"""
        r = int(color1[0] - (color1[0] - color2[0]) * pct)
        g = int(color1[1] - (color1[1] - color2[1]) * pct)
        b = int(color1[2] - (color1[2] - color2[2]) * pct)
        return (r,g,b)
 
    # Define rainbow cycle function to do a cycle of all hues.
    def rainbow_cycle_successive(self, wait=0.1):
        for i in range(self.pixels.count()):
            # tricky math! we use each pixel as a fraction of the full 96-color wheel
            # (thats the i / strip.numPixels() part)
            # Then add in j which makes the colors go around per pixel
            # the % 96 is to make the wheel cycle around
            self.pixels.set_pixel(i, self.wheel(((i * 256 // self.pixels.count())) % 256) )
            self.pixels.show()
            if wait > 0: time.sleep(wait)
 
    def rainbow_cycle_wheel(self, wait=0.005):
        for j in range(256): # one cycle of all 256 colors in the wheel
            for i in range(self.pixels.count()):
                self.pixels.set_pixel(i, self.wheel(((i * 256 // self.pixels.count()) + j) % 256) )
            self.pixels.show()
            if wait > 0: time.sleep(wait)
 
    def rainbow_colors_wheel(self, wait=0.05):
        for j in range(256): # one cycle of all 256 colors in the wheel
            for i in range(self.pixels.count()):
                self.pixels.set_pixel(i, self.wheel(((256 // self.pixels.count() + j)) % 256) )
            self.pixels.show()
            if wait > 0: time.sleep(wait)

    def rainbow_cycle(self, colors=[RED, ORANGE, YELLOW, GREEN, BLUE, VIOLET], wait=0.05):
        """Rainbow of colors along the string doing one full loop"""
        rcolors = colors + [colors[0]]
        rainbow = []
        transitions = int(math.ceil(float(self.pixels.count()) / (len(rcolors) - 1)))
        for i in range(len(rcolors) - 1):
            for j in range(transitions):
                r,g,b = self.color_step(rcolors[i], rcolors[i+1], float(j)/transitions)
                rainbow.append(Adafruit_WS2801.RGB_to_color(r,g,b))

        for i in range(self.pixels.count()):
            for j in range(self.pixels.count()):
                self.pixels.set_pixel(j, rainbow[(j + i) % self.pixels.count()])
            self.pixels.show()
            if wait > 0: time.sleep(wait)

    def solid_cycle(self, colors=[RED, ORANGE, YELLOW, GREEN, BLUE, VIOLET], transitions = 10, wait=0.05):
        for i in range(len(colors) - 1):
            for j in range(transitions + 1):
              r,g,b = self.color_step(colors[i], colors[i+1], float(j)/transitions)
              self.solid((r,g,b))
              if wait > 0:
                  time.sleep(wait)

    def brightness_decrease(self, wait=0.01, step=1):
        for j in range(int(256 // step)):
            for i in range(self.pixels.count()):
                r, g, b = self.pixels.get_pixel_rgb(i)
                r = int(max(0, r - step))
                g = int(max(0, g - step))
                b = int(max(0, b - step))
                self.pixels.set_pixel(i, Adafruit_WS2801.RGB_to_color( r, g, b ))
            self.pixels.show()
            if wait > 0:
                time.sleep(wait)
        self.off()

    def brightness_increase(self, wait=0.01, step=1):
        for j in range(int(256 // step)):
            for i in range(self.pixels.count()):
                r, g, b = self.pixels.get_pixel_rgb(i)
                r = int(max(0, r + step))
                g = int(max(0, g + step))
                b = int(max(0, b + step))
                self.pixels.set_pixel(i, Adafruit_WS2801.RGB_to_color( r, g, b ))
            self.pixels.show()
            if wait > 0:
                time.sleep(wait)
 
    def blink_color(self, blinks = 2, blink_times=5, wait=0.5, color=(255,0,0)):
        for i in range(blink_times):
            # blink two times, then wait
            self.pixels.clear()
            for j in range(blinks):
                for k in range(self.pixels.count()):
                    self.pixels.set_pixel(k, Adafruit_WS2801.RGB_to_color( color[0], color[1], color[2] ))
                self.pixels.show()
                time.sleep(0.08)
                self.off()
                time.sleep(0.08)
            time.sleep(wait)

    def appear_from_back(self, color=(255, 0, 0)):
        for i in range(self.pixels.count()):
            for j in reversed(range(i, pixels.count())):
                self.pixels.clear()
                # first set all pixels at the begin
                for k in range(i):
                    self.pixels.set_pixel(k, Adafruit_WS2801.RGB_to_color( color[0], color[1], color[2] ))
                # set then the pixel at position j
                self.pixels.set_pixel(i, Adafruit_WS2801.RGB_to_color( color[0], color[1], color[2] ))
                self.pixels.show()
                time.sleep(0.02)

    def trace(self, tail=1, direction = 0, color=(255,255,255), speed = 1):
        pos = 0
        start = 0
        order = range(self.pixels.count())
        if direction: 
          order = reversed(order)
          start = self.pixels.count()
        for i in order:
            self.pixels.clear()

            pos = max(0, i - tail)
            if direction: pos = min(self.pixels.count(), i + tail)

            step = 1
            stride = int(255 / tail) 
            bias = 255 * (1 - math.log(stride, 255)) / 2

            r, g, b = color
            self.pixels.set_pixel(i, Adafruit_WS2801.RGB_to_color( r, g, b ))

            otail = range(pos, i)
            if direction: otail = range(i, pos)
            if not direction: otail = reversed(otail)

            for j in otail:
                r, g, b = color
                r = int(max(0, r - bias - step * stride))
                g = int(max(0, g - bias - step * stride))
                b = int(max(0, b - bias - step * stride))
                self.pixels.set_pixel(j, Adafruit_WS2801.RGB_to_color( r, g, b ))
                step += 1

            self.pixels.show()
            time.sleep(0.1 / speed)
        self.off()

    def bounce(self, tail=1, start_dir = 0, color=(255,255,255), speed = 1):
        self.trace(tail, start_dir, color = color, speed = speed)
        self.trace(tail, (start_dir + 1) % 2, color = color, speed = speed)

    def alternating(self, color_set=[(255,255,255)]):
        self.pixels.clear()
        set_count = len(color_set)
        for i in range(self.pixels.count()):
            color = color_set[i % set_count]
            self.pixels.set_pixel(i, Adafruit_WS2801.RGB_to_color( color[0], color[1], color[2] ))
        self.pixels.show()

    def solid(self, color=(255,255,255)):
        self.pixels.clear()
        for i in range(self.pixels.count()):
            self.pixels.set_pixel(i, Adafruit_WS2801.RGB_to_color( color[0], color[1], color[2] ))
        self.pixels.show()

    def off(self):
        self.pixels.clear()
        self.pixels.show()
 
if __name__ == "__main__":
    pixels = Pixels()

    # Clear all the pixels to turn them off.
    pixels.off() # Make sure to call show() after changing any pixels!
 
    pixels.rainbow_cycle_successive(wait=0.1)
    
    pixels.rainbow_cycle(wait=0.01)
 
    pixels.off()
    pixels.brightness_increase()
    
    #pixels.appear_from_back()
    
    pixels.blink_color(blink_times = 1, color=(200, 200, 200))
    
    pixels.rainbow_colors()
    
    pixels.brightness_decrease()
