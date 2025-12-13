import numpy as np
import pandas as pd 
import matplotlib.pyplot as plt
from Functions import *
from fileReader import compassReader
import os

#data directories
shadowbar_data_directory = "PuBe_ToF_12_8_25_Shadowbar"
bare_data_directory = "PuBe_ToF_12_4_25_Bare/Filtered"

#creating necessary directories
final_plottting_directory = "Final_Analysis_Plots"
if not os.path.exists(final_plottting_directory):
    os.makedirs(final_plottting_directory)


#constants used for data
distance = 0.804 # meters
time_conversion_factor = 1
joule_to_ev = 1 / 1.602e-19
mass_neutron = 1.675e-27 # kg
bare_measurement_time = 47 * 3600 + 7 * 60 + 29
shadowbar_measurement_time = 48 * 3600 + 1



#expected highest peak energy and time
expected_highest_peak_time = 23.4257 # ns

#retrieving TOF spectra from both datasets
tof_spectra = []
for data_directory in [shadowbar_data_directory, bare_data_directory]:
    filtered_files = sorted(os.listdir(data_directory))
    for file in filtered_files:
        spectrum_type = file.split("_")[2]
        channel = file.split("@")[0]
        if spectrum_type == "TOFspectrumF":
            tof_spectrum_file = os.path.join(data_directory, file)
    tof_data = compassReader(tof_spectrum_file)
    tof_spectra.append(tof_data)

shadowbar_tof_data = tof_spectra[0]
bare_tof_data = tof_spectra[1]

#normalizing data by measurement time
shadowbar_tof_data = shadowbar_tof_data / shadowbar_measurement_time
bare_tof_data = bare_tof_data / bare_measurement_time


#applying boxcar moving average filter to data to smooth out fluctuations
shadowbar_tof_data = boxcar_average_numpy(shadowbar_tof_data, window_size=5)
bare_tof_data = boxcar_average_numpy(bare_tof_data, window_size=5)

net_data = bare_tof_data - shadowbar_tof_data
channels = np.arange(len(net_data))
time = channels * time_conversion_factor

#finding where net data is not zero
where_not_0 = np.where(net_data != 0)
net_data = net_data[where_not_0]
time = time[where_not_0]

#large peak index & finding baseline average
large_peak_index = np.argmax(net_data)
baseline_average = np.mean(net_data[0:large_peak_index-20])

large_peak_channel = where_not_0[0][large_peak_index]
# time = time * expected_highest_peak_time / large_peak_channel

#remvoing baseline average from net data
net_data = net_data - baseline_average
net_data = np.where(net_data < 0, 0, net_data) * 48 * 3600  # converting to counts per 48 hours

net_data2 = boxcar_average_numpy(net_data, window_size=1000)




plt.plot(time, net_data,  label="Net Spectrum (Bare - Shadowbar)")
# plt.plot(time, net_data2, label="Smoothed Net Spectrum")
plt.legend()
plt.xlabel("Time of Flight (ns)")
plt.ylabel("Counts per Second")
# plt.axhline(y=baseline_average, color='r', linestyle='--', label="Baseline Average")
# plt.yscale("log")
plt.show()


