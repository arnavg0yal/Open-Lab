import numpy as np
import os
from fileReader import compassReader
import matplotlib.pyplot as plt
from Functions import *

current_dir = os.getcwd()
data_dir = os.path.join(current_dir,"PuBe_ToF_12_4_25_Bare" )
filtered_dir = os.path.join(data_dir, "Filtered")
unfiltered_dir = os.path.join(data_dir, "Unfiltered")
raw_dir = os.path.join(data_dir, "Raw")

plotting_dir = os.path.join(data_dir, "Plotting")
if not os.path.exists(plotting_dir):
    os.makedirs(plotting_dir)

distance = 0.804 # meters
time_conversion_factor = 1
joule_to_ev = 1 / 1.602e-19

detector_channels = []
spectrum_types = []

filtered_files = sorted(os.listdir(filtered_dir))
for file in filtered_files:
    spectrum_type = file.split("_")[2]
    channel = file.split("@")[0]
    if spectrum_type == "TOFspectrumF":
        tof_spectrum_file = os.path.join(filtered_dir, file)

tof_data = compassReader(tof_spectrum_file)
tof_channels = np.arange(len(tof_data))

where_not_0 = np.where(tof_data != 0)
tof_data = tof_data[where_not_0]
tof_channels = tof_channels[where_not_0]

tof_time = tof_channels * time_conversion_factor

tof_velocity, tof_energy = time_of_flight(distance, tof_time, d_unit="m", t_unit="ns", mass=1.675e-27)

plt.plot(tof_energy * joule_to_ev, tof_data, drawstyle='steps-mid')
plt.xlabel("Neutron Energy (eV)")
plt.ylabel("Counts")
plt.savefig(os.path.join(plotting_dir, "tof_energy_spectrum.png"))
# plt.show()

