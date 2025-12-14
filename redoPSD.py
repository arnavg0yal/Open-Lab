import numpy as np
import matplotlib.pyplot as plt
from pulseParser import *
import os
from scipy.optimize import curve_fit
from Functions import *
from fileReader import compassReader
import pandas as pd

def linear_fit(x, m, b):
    return m * x + b

save_directory = "redo_PSD_analysis_plots"
if not os.path.exists(save_directory):
    os.makedirs(save_directory)

bare_spectrum_CH0_file = r"binary_files\DataF_CH0@DT5730S_2263_New_PuBe_ToF_12_4_25_Bare.BIN"
bare_spectrum_CH1_file = r"binary_files\DataF_CH1@DT5730S_2263_New_PuBe_ToF_12_4_25_Bare.BIN"

shadowbar_spectrum_CH0_file = r"binary_files\DataF_CH0@DT5730S_2263_New_PuBe_TOF_12_8_25_Shadowbar.BIN"
shadowbar_spectrum_CH1_file = r"binary_files\DataF_CH1@DT5730S_2263_New_PuBe_TOF_12_8_25_Shadowbar.BIN"

calibration_tof_spectrum = compassReader(r"TOF_calibration_Na22\CH1@DT5730S_2263_TOFspectrumF_Na22_1mCi_DeltaT_Calibration_12_8_25_20251208_143019.txt")


for file in [bare_spectrum_CH0_file, bare_spectrum_CH1_file]:
    if not os.path.isfile(file):
        raise FileNotFoundError(f"Required file '{file}' not found.")
    if os.path.isfile(file):
        print(f"File '{file}' found. Proceeding with analysis.")

net_spectrum = pd.read_csv("net_tof_data.csv", header=None)[1].to_numpy()



for collection in [(bare_spectrum_CH0_file, bare_spectrum_CH1_file, "Bare"),
                   (shadowbar_spectrum_CH0_file, shadowbar_spectrum_CH1_file, "Shadowbar")]:

    CH0_wave_bin = WaveBinFile(collection[0], version=2)
    CH1_wave_bin = WaveBinFile(collection[1], version=2)

    name = collection[2]

    CH0_pulses = CH0_wave_bin.readNextNPulses(CH0_wave_bin.totalNumberOfPulses)
    CH1_pulses = CH1_wave_bin.readNextNPulses(CH1_wave_bin.totalNumberOfPulses)

    print(f"Total pulses in CH0: {CH0_wave_bin.totalNumberOfPulses}")
    print(f"Total pulses in CH1: {CH1_wave_bin.totalNumberOfPulses}")


    time_stamps = []
    energy_clycs = []
    energy_ogs = []
    clyc_psd_energies = []
    psd_ratio_list = []

    for pulse_og, pulse_clyc in zip(CH0_pulses, CH1_pulses):

        energy_clycs.append(pulse_clyc['Energy'])
        energy_ogs.append(pulse_og['Energy'])



        clyc_samples = np.array(pulse_clyc['Samples'], dtype=np.float32) * -1

        baseline = np.mean(clyc_samples[:5])
        clyc_samples -= baseline

        clyc_samples = boxcar_average_numpy(clyc_samples, window_size=3)


        long_gate = len(clyc_samples)
        short_gate = 120

        # plt.plot(clyc_samples)
        # plt.axvline(x=short_gate, color='r', linestyle='--', label='Short Gate End')
        # plt.axvline(x=long_gate, color='g', linestyle='--', label='Long Gate End')
        # plt.show()

        numerator = np.trapezoid(clyc_samples[short_gate:long_gate])
        denominator = np.trapezoid(clyc_samples[:long_gate])

        psd_ratio = numerator / denominator
        # print(f"PSD Ratio: {psd_ratio}")
        psd_ratio_list.append(psd_ratio)
        if psd_ratio > 0.78:
            clyc_psd_energies.append(pulse_clyc['Energy'])

            tof = (pulse_clyc["Time Stamp"] - pulse_og["Time Stamp"]) * 1e-3
            time_stamps.append(tof)




    plt.hist(energy_clycs, bins=1000, alpha=1, label='CLYC Energy', color='r')
    plt.hist(clyc_psd_energies, bins=1000, alpha=0.25, label='CLYC PSD Selected Energy', color='b')
    plt.yscale('log')
    # plt.plot(time_stamps, energy_ogs, 'bo', markersize=1, label='OG Energy')
    # plt.show()
    plt.savefig(os.path.join(save_directory, f"{name}_CLYC_Energy_PSD_Selection.png"))
    plt.clf()

    plt.plot(energy_clycs, psd_ratio_list, 'ro', markersize=1)
    plt.ylim(0, 1)
    plt.axhline(y = 0.78)
    plt.savefig(os.path.join(save_directory, f"{name}_CLYC_PSD_Ratio_vs_Energy.png"))
    plt.clf()

    plt.hist(time_stamps, bins=1000, range=(-150, 150))
    x = np.linspace(-150, 150, len(calibration_tof_spectrum))
    plt.plot(x, calibration_tof_spectrum, 'b-')
    x2 = np.linspace(-150, 150, len(net_spectrum))
    plt.plot(x2, net_spectrum, 'r-')
    plt.xlabel("Time of Flight (ns)")
    plt.ylabel("Counts")
    plt.yscale('log')
    plt.title(f"{name} CLYC TOF Spectrum")
    plt.savefig(os.path.join(save_directory, f"{name}_CLYC_TOF_Spectrum.png"))
    # plt.show()
    plt.clf()