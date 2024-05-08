# Import necessary libraries
import time
import math
from ssd1306 import SSD1306_I2C
from machine import UART, Pin, I2C, ADC
from filefifo import Filefifo
from fifo import Fifo
from led import Led
from piotimer import Piotimer
import micropython
from kubios import Kubios
from mqtt_publish import Mqtt
import ujson
from machine import Pin

# Define OLED display parameters
oled_width = 128
oled_height = 64
character_width = 8
text_height = 8

# Initialize OLED display
i2c = I2C(1, scl=Pin(15), sda=Pin(14), freq=400000)
oled = SSD1306_I2C(oled_width, oled_height, i2c)

# Initialize ADC for sensor
sensor = ADC(Pin(26))

# Initialize FIFO buffer for samples
samples = Fifo(2000)

# Define gap in milliseconds
gap_ms = 4

# Define FIFO buffer for button presses
press = Fifo(10)

# Define minimum and maximum heart rate
minhr = 30
maxhr = 240
LED = Pin(20,Pin.OUT)
LED.off()
# Function to measure heart rate
def measure_hr():
    # Initialize sample_list
    sample_list = []
    
    def get_signal(tid):
        samples.put(sensor.read_u16())

    timer = Piotimer(period=4, mode=Piotimer.PERIODIC, callback=get_signal)

    global ppis, heartrates, max_sample, peakcounts, pts, ts
    ppis = []
    heartrates = []
    peakcounts = []
    max_sample = 0
    pts = 0
    ts = 0

    while True:
        if samples.has_data():
            sample = samples.get()
            sample_list.append(sample)

            if len(sample_list) >= 750:
                max_value = max(sample_list)
                min_value = min(sample_list)
                threshold = (4 * max_value + min_value) / 5

                for i in sample_list:
                    if i >= threshold and i > max_sample:
                        max_sample = i
                    elif i < threshold and max_sample != 0:
                        try:
                            index = sample_list.index(max_sample)
                            peakcounts.append(index)
                            max_sample = 0
                        except ValueError:
                            print("Please put the sensor back on your pulse and wait for recalibration (10 seconds)")
                            oled.fill(0)
                            oled.text("Pulse not detected", 0, 30, 1)
                            oled.show()
                            LED.on()
                            if press.has_data():
                                value = press.get()
                                if ts - pts < 250:
                                    pts = ts
                                    continue
                                else:
                                    pts = ts
                                    peakcounts = []
                                    sample_list = []
                                    timer.deinit()
                                    return

                for i in range(len(peakcounts)):
                    delta = peakcounts[i] - peakcounts[i - 1]
                    ppi = delta * gap_ms
                    if press.has_data():
                        value = press.get()
                        if ts - pts < 250:
                            pts = ts
                            continue
                        else:
                            pts = ts
                            timer.deinit()
                            return

                    if ppi > 300 and ppi < 1200:
                        LED.off()
                        heartrate = 60000 / ppi
                        heartrate = round(heartrate)
                        print(f"HR: {heartrate} BPM")  # Print heart rate
                        if len(heartrates) > 1:
                            if heartrates[-1] - heartrates[-2] > 20 or heartrates[-2] - heartrates[-1] > 20:
                                oled.text("Noise detected", 0, 1)
                                oled.show()

                        if heartrate > minhr and heartrate < maxhr:
                            oled.fill(0)
                            oled.rect(oled_width - (character_width * 4), oled_height - (text_height + 1),
                                      character_width * 4, text_height, 1, 1)
                            oled.text("STOP", oled_width - (character_width * 4), oled_height - text_height, 0)
                            oled.text(f"HR: {heartrate} BPM", 0, oled_height - text_height, 1)
                            oled.show()
                            ppis.append(ppi)
                            prev_hr = heartrate

                sample_list = []
                peakcounts = []

# Call the measure_hr function to measure heart rate
measure_hr()

