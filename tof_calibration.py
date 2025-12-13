from fileReader import compassReader
import numpy as np
import matplotlib.pyplot as plt
import os
from Functions import *
from scipy.optimize import curve_fit

minimum_energy_time = 67.06 # ns
maximum_energy_time = 23.4257 # ns


distance = 0.804 # meters
mass_neutron = 1.675e-27 # kg
J_to_eV = 1 / 1.602e-19

plotting_directory = "Final_Analysis_Plots"

def gaussian(x, amp, mean, stddev):
    return amp * np.exp(-((x - mean) ** 2) / (2 * stddev ** 2))

tof_calibration_data_directory = "TOF_calibration_Na22"

tof_bare_data = "PuBe_ToF_12_4_25_Bare/Filtered/CH1@DT5730S_2263_TOFspectrumF_New_PuBe_ToF_12_4_25_Bare_20251206_143249.txt"
tof_bare_data = compassReader(tof_bare_data)
tof_shadowbar_data = "PuBe_ToF_12_8_25_Shadowbar\CH1@DT5730S_2263_TOFspectrumF_New_PuBe_TOF_12_8_25_Shadowbar_20251210_143515.txt"
tof_shadowbar_data = compassReader(tof_shadowbar_data)

for file in sorted(os.listdir(tof_calibration_data_directory)):
    spectrum_type = file.split("_")[2]
    channel = file.split("@")[0]
    if spectrum_type == "TOFspectrumF":
        tof_spectrum_file = os.path.join(tof_calibration_data_directory, file)

tof_data = compassReader(tof_spectrum_file)
peak_channel_calibration = np.argmax(tof_data)
peak_channel_bare = np.argmax(tof_bare_data)

tof_data = boxcar_average_numpy(tof_data, window_size=5)
tof_bare_data = boxcar_average_numpy(tof_bare_data, window_size=5)
tof_shadowbar_data = boxcar_average_numpy(tof_shadowbar_data, window_size=5)

print(f"Na22 Peak Channel: {peak_channel_calibration}")
print(f"PuBe Peak Channel: {peak_channel_bare}")
print(peak_channel_bare - peak_channel_calibration)
print(4000 - peak_channel_calibration)
print(67.06 / (4000 - peak_channel_calibration))
calibration_factor = 67.06 / (4050 - peak_channel_calibration)
print((3855 - peak_channel_bare) * calibration_factor)


channels = np.arange(len(tof_data))
channels -= peak_channel_calibration
time_ns = channels * calibration_factor


net_data = tof_bare_data - tof_shadowbar_data
where_not_0 = np.where(net_data != 0)
net_data = net_data[where_not_0]
time_ns = time_ns[where_not_0]
#net_data = boxcar_average_numpy(net_data, window_size=10)

max_time = time_ns[np.argmax(net_data)]

popt, pcov = curve_fit(gaussian, time_ns, net_data, p0=[max(net_data), max_time, 5])

gaussian_fit = gaussian(time_ns, *popt)


# plt.plot(time_ns, abs(net_data- gaussian_fit), label='Net TOF Data (Bare - Shadowbar)', color='blue')
plt.plot(time_ns, net_data, label = "Net TOF Data (Bare - Shadowbar)", color='blue')
# plt.plot(time_ns, gaussian_fit, label='Gaussian Fit', color='orange')
plt.axvline(x = 23.4257, color='r', linestyle='--', label='Maximum Neutron Energy')
plt.axvline(x = 67.06, color='g', linestyle='--', label='Minimum Neutron Energy')
plt.xlim(0, 70)
plt.ylim(0, 300)

plt.xlabel("Time of Flight (ns)")
plt.ylabel("Counts")
plt.legend()
# plt.show()
plt.savefig(os.path.join(plotting_directory, "net_tof_spectrum_calibrated.png"))
plt.clf()

def piecewise_modification(x_array, data_array, x_value_cut, scalar):
    cut_index = np.argmin(np.abs(x_array - x_value_cut))
    unmodified_part = data_array[:cut_index] * scalar
    modified_part = data_array[cut_index:] #* scalar
    return np.concatenate((unmodified_part, modified_part))


time_ns = time_ns[np.argmax(net_data):]
net_data = net_data[np.argmax(net_data):]
energy_joules = time_of_flight(distance, time_ns * 1e-9, mass_neutron, d_unit="m", t_unit="s")[1] * J_to_eV / 1e6  # convert to MeV

relativistic_energy_joules = (1 / np.sqrt(1 - (distance / (time_ns * 1e-9))**2 / (3e8)**2) -1) * mass_neutron * (3e8)**2 * J_to_eV / 1e6  # convert to MeV

min_neutron_energy = 0.75 # MeV
max_neutron_energy = 6.2 # MeV

modded_energy_data =  piecewise_modification(energy_joules, net_data, x_value_cut=4, scalar= 0.5)

print(type(energy_joules))
plt.plot(relativistic_energy_joules, net_data, label = "Net TOF Data (Bare - Shadowbar)", color='blue')
plt.plot(relativistic_energy_joules, modded_energy_data, label = "Modified Net TOF Data (Bare - Shadowbar)", color='orange')
plt.axvline(x = max_neutron_energy, color='r', linestyle='--', label='Maximum Neutron Energy')
plt.axvline(x = min_neutron_energy, color='g', linestyle='--', label='Minimum Neutron Energy')
plt.xlim(0, 12)
plt.ylim(0, 300)
plt.xlabel("Neutron Energy (MeV)")
plt.ylabel("Counts")
plt.legend()
plt.show()
# plt.savefig(os.path.join(plotting_directory, "net_tof_spectrum_energy_calibrated.png"))

