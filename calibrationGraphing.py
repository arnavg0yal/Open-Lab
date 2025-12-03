import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pulseParser import WaveBinFile
import os
from fileReader import compassReader
from Functions import *
from scipy.signal import find_peaks

window_size = 10
calibration_folder = "11_20_2025_calibration"
calibration_plot_save = os.path.join(calibration_folder,"detector_calibration_plots")
if not os.path.exists(calibration_plot_save):
    os.makedirs(calibration_plot_save)


Cs137_CLYC_CH0 = os.path.join(calibration_folder,r"data\CH0@DT5730S_2263_Espectrum_Cs137_CLYC_11_20_2025_test_20251120_175941.txt")
Cs137_CLYC_CH1 = os.path.join(calibration_folder,r"data\CH1@DT5730S_2263_Espectrum_Cs137_CLYC_11_20_2025_test_20251120_175941.txt")

Na22_CLYC_CH0 = os.path.join(calibration_folder,r"data\CH0@DT5730S_2263_Espectrum_Na22_CLYC_11_20_2025_test_20251120_180528.txt")
Na22_CLYC_CH1 = os.path.join(calibration_folder,r"data\CH1@DT5730S_2263_Espectrum_Na22_CLYC_11_20_2025_test_20251120_180528.txt")

Cs137_OG_CH0 = os.path.join(calibration_folder,r"data\CH0@DT5730S_2263_Espectrum_Cs137_OG_11_20_2025_test_20251120_174405.txt")
Cs137_OG_CH1 = os.path.join(calibration_folder,r"data\CH1@DT5730S_2263_Espectrum_Cs137_OG_11_20_2025_test_20251120_174405.txt")

Na22_OG_CH0 = os.path.join(calibration_folder, r"data\CH0@DT5730S_2263_Espectrum_Na22_OG_11_20_2025_test_20251120_174621.txt")
Na22_OG_CH1 = os.path.join(calibration_folder,r"data\CH1@DT5730S_2263_Espectrum_Na22_OG_11_20_2025_test_20251120_174621.txt")

CH0_files = [Cs137_CLYC_CH0, Na22_CLYC_CH0, Cs137_OG_CH0, Na22_OG_CH0]
CH1_files = [Cs137_CLYC_CH1, Na22_CLYC_CH1, Cs137_OG_CH1, Na22_OG_CH1]

isotopes = ["Cs-137", "Na-22", "Cs-137", "Na-22"]
detectors = ["CLYC", "CLYC", "Organic Glass", "Organic Glass"]

calibration_factors = []

N = len(CH0_files)

for i in range(N):
    if i != 0:
        pass
    CH0_file = CH0_files[i]
    CH1_file = CH1_files[i]
    isotope = isotopes[i]
    detector = detectors[i]



    CH0_data = compassReader(CH0_file)
    CH1_data = compassReader(CH1_file)
    CH0_data = boxcar_average_numpy(CH0_data, window_size)
    CH1_data = boxcar_average_numpy(CH1_data, window_size)

    if isotope == "Cs-137":
        photopeak = 662
    if isotope == "Na-22":
        photopeak = 1275
        anhillation_peak = 511
    if detector == "CLYC":
        data = CH1_data
    if detector == "Organic Glass":
        data = CH0_data

   
    channels = np.arange(len(CH0_data))


    fig, ax = plt.subplots(1, 1, figsize=(8, 6))
    if detector== "CLYC":
        peak_indices, _ = find_peaks(data, distance=100)
        peak_channels = channels[peak_indices]
        plt.scatter(peak_channels, data[peak_indices], color='red', label='Detected Peaks')
        if isotope == "Na-22":
            plt.axvline(x = peak_channels[14], color='green', linestyle='--', label='1275 keV Peak')
            plt.axvline(x = peak_channels[7], color='orange', linestyle='--', label='511 keV Peak')

            calibration_factor = 1275 / peak_channels[14]
            print(f"Calibration factor for {isotope} with {detector}: {calibration_factor:.4f} keV/channel")
        if isotope == "Cs-137":
            plt.axvline(x = peak_channels[19], color='green', linestyle='--', label='662 keV Peak')
            calibration_factor = 662 / peak_channels[19]
            print(f"Calibration factor for {isotope} with {detector}: {calibration_factor:.4f} keV/channel")
            pass
    
    if detector == "Organic Glass":
        peak_indices, _ = find_peaks(data, distance=50)
        peak_channels = channels[peak_indices]
        plt.scatter(peak_channels, data[peak_indices], color='red', label='Detected Peaks')

        counts_at_top_of_edge = data[peak_indices[1]]
        counts_at_bottom_of_edge = data[peak_indices[2]]

        half_max_counts = (counts_at_top_of_edge + counts_at_bottom_of_edge) / 2
        center_of_edge_index = np.argmin(np.abs(data - half_max_counts))
        center_of_edge_channel = channels[center_of_edge_index]
        plt.axvline(x = center_of_edge_channel, color='purple', linestyle='--', label='Compton Edge')

        if isotope == "Cs-137":
            compton_edge_energy = comptonGamma(photopeak, 180)
            calibration_factor = compton_edge_energy / center_of_edge_channel
            print(f"Calibration factor for {isotope} with {detector}: {calibration_factor:.4f} keV/channel")
        if isotope == "Na-22":
            compton_edge_energy = comptonGamma(anhillation_peak, 180)
            calibration_factor = compton_edge_energy / center_of_edge_channel
            print(f"Calibration factor for {isotope} with {detector}: {calibration_factor:.4f} keV/channel")
        


    calibration_factors.append(calibration_factor)
    ax.plot(channels, data)
    ax.set_xlabel('Channel number')
    ax.set_ylabel('Counts')
    ax.legend()
    ax.set_title(f"{isotope} spectrum with {detector} detector")
    if detector == "Organic Glass":
        ax.set_xlim(0, 500)
    plt.savefig(os.path.join(calibration_plot_save, f"{isotope}_{detector}_spectrum.png"))
    # plt.show()

calibration_dict = {
    "Isotope": isotopes,
    "Detector": detectors,
    "Calibration Factor (keV/channel)": calibration_factors
}

calibration_df = pd.DataFrame(calibration_dict)
calibration_df.to_csv(os.path.join(calibration_plot_save, "calibration_factors.csv"), index=False)