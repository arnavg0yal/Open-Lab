'''
Description: Example of using the paser
Author: Ming Fang and Angela Di Fulvio
Date: 2022-08-22 20:55:13
LastEditors: Angela Di Fulvio
LastEditTime: 2025-11-28 16:19:00
'''
import numpy as np
from matplotlib import pyplot as plt
# import the parser to use it
from pulseParser import WaveBinFile

# Example 1
# Plot the first, second and last pulse recorded
binFileV1 = WaveBinFile('Data_CH0@DT5730_1660_Cs137_group1.bin', version=1)
totalN = binFileV1.totalNumberOfPulses
print(
    "Version {0} test data. Board number {1}, Channel number {2}. There are {3} pulses in total."
    .format(binFileV1.versionNumber, binFileV1.boardNumber,
            binFileV1.channelNumber, totalN))

firstPulse = binFileV1.readNextPulse()
secondPulse = binFileV1.readNextPulse()
# skip the next N - 3 pulses
binFileV1.skipNextNPulses(totalN - 3)
lastPulse = binFileV1.readNextPulse()
fig, ax = plt.subplots(1, 1, figsize=(6, 6))
ax.plot(firstPulse['Samples'], label='First pulse')
ax.plot(secondPulse['Samples'], label='Second pulse')
ax.plot(lastPulse['Samples'], label='Last pulse')
ax.set_xlabel('Sample number')
ax.set_ylabel('ADC unit')
ax.legend()
# plt.show()

# Example 2
# Plot the pulse height distribution
binFileV2 = WaveBinFile('Data_CH0@DT5730_1660_Cs137_group1.bin', version=1)
totalN = binFileV2.totalNumberOfPulses
print(
    "Version {0} test data. Board number {1}, Channel number {2}. There are {3} pulses in total."
    .format(binFileV2.versionNumber, binFileV2.boardNumber,
            binFileV2.channelNumber, totalN))

BASELINENUM = 16
VMAX = 2
NBITS = 14
POLARITY = -1
coeff = VMAX / (2**NBITS - 1)
##### read pulses one after another
# pulseHeights = []
# while binFileV2.numberOfPulsesUnread > 0:
#     newPulse = binFileV2.readNextPulse()
#     baseLine = np.mean(newPulse['Samples'][:BASELINENUM])
#     voltagePulse = coeff * (newPulse['Samples'] - baseLine) * POLARITY
#     pulseHeights.append(np.max(voltagePulse))

##### read all pulses at the same time
pulses = binFileV2.readNextNPulses(binFileV2.totalNumberOfPulses)
samples = pulses['Samples']
baseLines = np.mean(samples[:, :BASELINENUM], axis=1)
voltagePulses = coeff * (samples - baseLines[:,None]) * POLARITY
pulseHeights = np.max(voltagePulses, axis=1)

fig, ax = plt.subplots(1, 1, figsize=(6, 6))
ax.hist(pulseHeights, bins=300, range=(0, 2))
ax.set_xlabel('Pulse height (V)')
ax.set_ylabel('Counts')
ax.set_title("DCR spectrum")
plt.show()


# Example 3
# Plot the time stamp of each pulse (ps units)
binFileV3 = WaveBinFile('Data_CH0@DT5730_1660_Cs137_group1.bin', version=1)
totalN = binFileV3.totalNumberOfPulses
print(
    "Version {0} test data. Board number {1}, Channel number {2}. There are {3} pulses in total."
    .format(binFileV3.versionNumber, binFileV1.boardNumber,
            binFileV3.channelNumber, totalN))

pulses = binFileV3.readNextNPulses(binFileV3.totalNumberOfPulses)
timeS = pulses['Time Stamp']
fig, ax = plt.subplots(1, 1, figsize=(6, 6))
ax.plot(timeS, label='First pulse')
ax.set_xlabel('Incremental number')
ax.set_ylabel('Time (ps)')

plt.show()
