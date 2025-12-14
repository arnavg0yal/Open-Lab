import numpy as np
import pandas as pd 
import matplotlib.pyplot as plt
from Functions import *
from fileReader import compassReader
import os

#data directories
shadowbar_data_directory = "PuBe_ToF_12_8_25_Shadowbar"
bare_data_directory = "PuBe_ToF_12_4_25_Bare/Filtered"
tof_calibration_data_directory = "TOF_calibration_Na22"

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

minimum_energy_time = 67.06 # ns
maximum_energy_time = 23.4257 # ns




#retrieving TOF spectra from both datasets
tof_spectra = []
for data_directory in [shadowbar_data_directory, bare_data_directory, tof_calibration_data_directory]:
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
calibration_tof_data = tof_spectra[2]

#normalizing data by measurement time
shadowbar_tof_data = shadowbar_tof_data #/ shadowbar_measurement_time
bare_tof_data = bare_tof_data #/ bare_measurement_time


#applying boxcar moving average filter to data to smooth out fluctuations
shadowbar_tof_data = boxcar_average_numpy(shadowbar_tof_data, window_size=5)
bare_tof_data = boxcar_average_numpy(bare_tof_data, window_size=5)



plt.plot(bare_tof_data, label = "Bare Spectrum")
plt.plot(shadowbar_tof_data, label = "Shadowbar Spectrum")
plt.plot(calibration_tof_data, label = "Calibration Spectrum")
plt.yscale('log')
plt.title("Raw TOF Spectra")
# plt.show()
plt.clf()
net_data = bare_tof_data - shadowbar_tof_data

peak_channel_calibration = np.argmax(calibration_tof_data)
peak_channel_bare = np.argmax(bare_tof_data)
peak_channel_shadowbar = np.argmax(shadowbar_tof_data)

print(f"Na22 Peak Channel: {peak_channel_calibration}")
print(f"Bare Peak Channel: {peak_channel_bare}")
print(f"Shadowbar Peak Channel: {peak_channel_shadowbar}")

channels = np.arange(len(calibration_tof_data))
channels -= peak_channel_calibration

# time_ns_calibration_factor = maximum_energy_time / (channels[peak_channel_bare] - channels[peak_channel_calibration])
time_ns_calibration_factor = maximum_energy_time / (channels[3850] - channels[peak_channel_calibration])

print(channels[peak_channel_bare] - channels[peak_channel_calibration])
print(f"Calibration Factor (ns/channel): {time_ns_calibration_factor}")

time_ns = channels * time_ns_calibration_factor

plt.plot(time_ns, bare_tof_data, label = "Bare Spectrum")
plt.plot(time_ns, shadowbar_tof_data, label = "Shadowbar Spectrum")
plt.axvline(x = time_ns[peak_channel_shadowbar], color='r', linestyle='--', label=f'Shadowbar Peak: {time_ns[peak_channel_shadowbar]:.2f} ns')
# plt.axvline(x = time_ns[3850])
plt.legend()
plt.yscale('log')
plt.ylim(bottom = 1e1)
plt.xlim(-1500, 2000)
plt.show()




















'''

where_not_0 = np.where(net_data>0)
net_data = net_data[where_not_0]
channels = np.arange(len(net_data))
big_peak_index = np.argmax(net_data)
end_of_left_contium_index = big_peak_index -50
start_of_left_contium_index = end_of_left_contium_index - 360
index_of_0 = round(np.average([start_of_left_contium_index, end_of_left_contium_index]))

baseline_average = np.average(net_data[start_of_left_contium_index:end_of_left_contium_index])
net_data = net_data - baseline_average
net_data = np.where(net_data <0, 0, net_data)

channels = channels - index_of_0

channel_to_ns = maximum_energy_time / channels[big_peak_index]
time_ns = channels * channel_to_ns

plt.plot(time_ns,net_data)
# plt.axvline(x=end_of_left_contium_index,color='r')
# plt.axvline(x=start_of_left_contium_index,color='r')
plt.axvline(x=time_ns[index_of_0],color='g', label = "zero point", linestyle='--')
plt.axvline(x=time_ns[big_peak_index],color='b', label = "6.4 MeV peak", linestyle='--')
plt.xlabel("Time-of-Flight (ns)")
plt.ylabel("Counts (Normalized)")
# plt.yscale('log')
# plt.show()
plt.clf()
where_time_positive = np.where(time_ns > 0)
time_ns = time_ns[where_time_positive]
net_data = net_data[where_time_positive]


energy_data = time_of_flight(distance, time_ns, mass_neutron, "m", "ns")[1] * joule_to_ev / 1e6
plt.plot(energy_data, net_data)
plt.xlim(0,12)
plt.xlabel("Neutron Energy (MeV)")
plt.ylabel("Counts (Normalized)")
# plt.show()


'''