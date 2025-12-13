import numpy as np
import matplotlib.pyplot as plt
from Functions import boxcar_average_numpy
from fileReader import compassReader
import os
from pulseParser import WaveBinFile


CH0_bare_measurement_binary = "binary_files/DataF_CH0@DT5730S_2263_New_PuBe_ToF_12_4_25.BIN"
CH1_bare_measurement_binary = "binary_files/DataF_CH1@DT5730S_2263_New_PuBe_ToF_12_4_25.BIN"

pulse_list = []



for i , binary_file in enumerate([CH0_bare_measurement_binary, CH1_bare_measurement_binary]):
    binFile = WaveBinFile(binary_file, version=2)
    totalN = binFile.totalNumberOfPulses
    pulses = binFile.readNextNPulses(binFile.totalNumberOfPulses)
    pulse_list.append(pulses)

for i in range(len(pulse_list[0])):
    organic_glass_pulse = pulse_list[0][i]
    clyc_pulse = pulse_list[1][i]

    og_time = organic_glass_pulse['Time Stamp']
    clyc_time = clyc_pulse['Time Stamp']

    print(og_time - clyc_time)

