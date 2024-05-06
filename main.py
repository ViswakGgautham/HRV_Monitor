from machine import ADC, Pin
import network
import time
from time import sleep
from ssd1306 import SSD1306_I2C
from piotimer import Piotimer
from fifo import Fifo
from filefifo import Filefifo
import urequests as requests
import ujson

# Display configuration
width = 128
height = 64
i2c = machine.I2C(1,sda=machine.Pin(14), scl=machine.Pin(15), freq=400000)
oled = SSD1306_I2C(width, height, i2c)




counter_1 = 0
max_limits = 5



# Taking ADC values and calculating Peak-to-Peak intervals (PPIs) and Heart rate.                    
sample_list = Fifo (1500)
adc = ADC(26)

samples = [] 
peaks = [] 
min_hr = 30
max_hr = 240
ppi_list = []
ppi_list_processed = []
interval_gap_ms = 4
counter = 0

def get_signal(dummy_variable_01): 
    sample_list.put(adc.read_u16()) #Sensor reads ADC values here which are then put in a fifo buffer.
    
    
timer = Piotimer(period = 4, mode = Piotimer.PERIODIC, callback = get_signal)
#sample_list = Filefifo('capture03_250Hz.txt')

# While true loop that checks for PPIs from the samples collected.
while True: 
    if not sample_list.empty():
            measured = sample_list.get()
            samples.append(measured)
            if measured < 0:
                break
            if len(samples) >= 750:
                max_sample = max(samples)
                min_sample = min(samples)
                threshold = (3*max_sample + 2*min_sample)/5 
                
                prev = samples[0]
                counter = 0
                for s in samples:
                    if s >= threshold and prev < threshold:
                        peaks.append(counter)
                    counter += 1
                    prev = s
            
                for i in range(1, len(peaks)):
                    delta_gap = peaks[i] - peaks[i-1]
                    ppi = delta_gap * interval_gap_ms

                    if ppi > 0:
                         heart_rate = 60000/ppi
                         if heart_rate > min_hr and heart_rate < max_hr:
                             print(f'Heart Rate: {round(heart_rate)}')
                             oled.fill(0)
                             oled.text(f'HR:{round(heart_rate)} BPM',32 ,30, 1)
                             oled.show()
                             ppi_list.append(ppi)
                             ppi_list_processed = ppi_list[30:] #Samples recoreded after first 30 samples to enchance stability in measurement.
                    if len(ppi_list_processed) >= 25:
                            
                       break
                samples = [] 
                peaks = [] 
                
                    


    if len(ppi_list_processed) >= 25:
        break

oled.fill(0)
print('Processing...')
oled.show()

# Calculating HRV data locally using measured PPIs
def calculate_hrv(ppi_list_processed):
   
    mean_ppi = sum(ppi_list_processed) / len(ppi_list_processed)
    
    
    mean_hr = 60000 / mean_ppi
    
    
    sdnn_sum = sum([(ppi - mean_ppi)**2 for ppi in ppi_list_processed])
    sdnn = (sdnn_sum / (len(ppi_list_processed)-1))**0.5
    
    
    rmssd_sum = sum([(ppi_list_processed[i+1] - ppi_list_processed[i])**2 for i in range(len(ppi_list_processed)-1)])
    rmssd = (rmssd_sum / (len(ppi_list_processed) - 1))**0.5
    
    return (mean_ppi, mean_hr, sdnn, rmssd)





current_page = 0

# Printings the Pages on the display.
while True:
    oled.fill(0)
    page = pages[current_page]
    oled.text(page['title'], 0, 0)
    oled.text(page['subtitle'], 0, 10)
    for i, line in enumerate(page['lines']):
        oled.text(line, 0, 20 + i * 10)
    oled.show()
    time.sleep(5)
    current_page = (current_page + 1) % len(pages)

