'''
Description: CoMPASS binary data parser
Author: Ming Fang
Date: 2022-08-22 19:00:26
LastEditors: Ming Fang
LastEditTime: 2022-08-23 17:55:59
'''
from pathlib import Path
import numpy as np


class WaveBinFile:
    """Paser for CoMPASS binary file.
    """
    def __init__(self, p, version=2) -> None:
        """Initialize with input file path and version number.

        Args:
            p (str | Path): Path to the binary data file saved by CoMPASS.
            version (int): Version of the CoMPASS software. Must be 1 or 2. Default is 2.

        Raises:
            ValueError: If input file is not accessible, or the version is incorrect.
        """
        self._filePath = Path(p)  # file path
        if not self._filePath.is_file():
            raise ValueError(f"{str(p)} is not accessible.")
        if version != 1 and version != 2:
            raise ValueError(f"Version number must be either 1 or 2, but got {version}.")
        self._headersize = 24  # header size in bytes
        if version == 2:
            self._headersize += 1
        self._version = version  # CoMPASS version number
        self._numberOfSamples = 0  # number of samples per pulse
        self._boardNumber = -1  # board number
        self._channelNumber = -1  # channel number
        self._getCommonHeader()
        self._fileObject = open(self._filePath, 'rb')  # data file object
        if version == 2:
            # skip first 2 bytes
            self._fileObject.read(2)
        self._pulseSize = self._headersize + 2 * self._numberOfSamples  # pulse size in bytes
        self._numberOfPulses = int(self._filePath.stat().st_size / self._pulseSize)  # total number of pulses in the file
        if version == 1:
            self._pulseType = np.dtype([('Board', np.int16),
                                       ('Channel', np.int16),
                                       ('Time Stamp', np.int64),
                                       ('Energy', np.int16),
                                       ('Energy Short', np.int16),
                                       ('Flags', np.int32),
                                       ('Number of Samples', np.int32),
                                       ('Samples', np.uint16, (self._numberOfSamples, ))])  # custom data type for one pulse
        else:
            self._pulseType = np.dtype([('Board', np.int16),
                                       ('Channel', np.int16),
                                       ('Time Stamp', np.int64),
                                       ('Energy', np.int16),
                                       ('Energy Short', np.int16),
                                       ('Flags', np.int32),
                                       ('Waveform Code', np.int8),
                                       ('Number of Samples', np.int32),
                                       ('Samples', np.uint16, (self._numberOfSamples, ))])
            # print(self.pulseType['Samples'])
        self._numberOfPulseUnread = self._numberOfPulses  # number of pulses that have not been read

    def skipNextPulse(self):
        """Skip the next pulse.
        """
        if self._numberOfPulseUnread > 0:
            self._fileObject.seek(self._pulseSize, 1)
            self._numberOfPulseUnread -= 1

    def skipNextNPulses(self, num: int):
        """Skip the next N pulses.

        Args:
            num (int): number of pulses to skip.
        """
        if self._numberOfPulseUnread > num:
            self._fileObject.seek(self._pulseSize*num, 1)
            self._numberOfPulseUnread -= num
        else:
            self._fileObject.seek(0, 2)
            self._numberOfPulseUnread = 0

    def readNextPulse(self):
        """Read the next pulse.

        Returns:
            self.pulseType: Custom data type for pulse object.
            
            None: If all pulses have been read
            
            The data members of self.PulseType can be accessed with the following string keys:
            
                "Board": np.int16, board number
                "Channel": np.int16, channel number
                "Time Stamp": np.int64, unit: ps
                "Energy": np.int16
                "Energy short": np.int16
                "Flags": np.int32
                "Waveform Code": np.int8, version 2 only
                "Number of Samples" np.int32
                "Samples": numpy array of np.uint16
        """
        if self._numberOfPulseUnread > 0:
            self._numberOfPulseUnread -= 1
            buffer = self._fileObject.read(self._pulseSize)
            return (np.frombuffer(buffer, dtype=self._pulseType))[0]
        else:
            return None

    def readNextNPulses(self, num: int):
        """Read the next N pulses.
        Note:
            Be carefule about the memory when reading a large file. 
            If the user read the whole file and there is not enough memory, program will crash.
            If that's the case, read the pulses in smaller chunks.

        Args:
            num (int): number of pulses to read.

        Returns:
            np.ndarray: Array of pulses. Number of pulses is at most `num`.
                        If reached EOF, less than `num` pulses will be returned.
            
            None: If all pulses have been read
        """
        if self._numberOfPulseUnread <= 0:
            return None
        elif self._numberOfPulseUnread > num:
            self._numberOfPulseUnread -= num
        else:
            num = self._numberOfPulseUnread
            self._numberOfPulseUnread = 0
        buffer = self._fileObject.read(self._pulseSize*num)
        return np.frombuffer(buffer, dtype=self._pulseType)
        
    def rewind(self):
        """Go to the begnning of the file.
        """
       
        self._fileObject.seek(0)
        if self._version == 2:
            # skip first 2 bytes
            self._fileObject.read(2)
        self._numberOfPulseUnread = self._numberOfPulses

    @property
    def versionNumber(self):
        """The CoMPASS version number.

        Returns:
            int
        """
        return self._version
    
    @property
    def numberOfSamplesPerPulse(self):
        """The number of samples per pulse.

        Returns:
            int
        """
        return self._numberOfSamples

    @property
    def boardNumber(self):
        """Board number.

        Returns:
            int
        """
        return self._boardNumber

    @property
    def channelNumber(self):
        """Channel number.

        Returns:
            int
        """
        return self._channelNumber

    @property
    def totalNumberOfPulses(self):
        """The total number of pulses recorded on file.

        Returns:
            int
        """
        return self._numberOfPulses

    @property
    def numberOfPulsesUnread(self):
        """The number of pulses that haven't been read.

        Returns:
            int
        """
        return self._numberOfPulseUnread
    
    
    def _getCommonHeader(self):
        """Read common headers of all pulses.
        """
        with open(self._filePath, 'rb') as f:
            if self._version == 2:
                f.read(2)
            # read first header
            self._boardNumber = int.from_bytes(f.read(2), 'little')
            self._channelNumber = int.from_bytes(f.read(2), 'little')
            if self._version == 1:
                f.read(16)
            else:
                f.read(17)
            self._numberOfSamples = int.from_bytes(f.read(4), 'little')

    def __del__(self):
        self._fileObject.close()
