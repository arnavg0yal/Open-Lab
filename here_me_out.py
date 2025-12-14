import numpy as np
import matplotlib.pyplot as plt
import os
from fileReader import compassReader
import pandas as pd

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

net_data = bare_tof_data - shadowbar_tof_data
where_not_zero = np.where(net_data > 0)
net_data = net_data[where_not_zero]

pd.DataFrame(net_data).to_csv("net_tof_data.csv")



big_peak_index = np.argmax(net_data)
mini_peak_index = big_peak_index + 163

# plt.plot(net_data)
# plt.axvline(x=big_peak_index, color='r', linestyle='--', label='Big Peak')
# plt.axvline(x=mini_peak_index, color='g', linestyle='--', label='Mini Peak')

justin_factor = (minimum_energy_time - maximum_energy_time) / (mini_peak_index - big_peak_index)

channel_of_0 = round(big_peak_index - (maximum_energy_time / justin_factor))
channels = np.arange(len(net_data))
channels -= channel_of_0
time_ns = channels * justin_factor

# plt.axvline(x=channel_of_0, color='b', linestyle='--', label='0 ns Point')
# plt.show()
# plt.clf()

plt.plot(time_ns, net_data)
plt.plot(time_ns, calibration_tof_data[where_not_zero], label = "Calibration Spectrum")
plt.show()

print(.8 / 3e8)

