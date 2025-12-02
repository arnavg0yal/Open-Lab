import os
import numpy as np




def compassReader(file_path):

    with open(file_path, 'r') as file:
        lines = file.readlines()
    new_lines = []
    for line in lines:
        l = line.replace("\n", "")
        new_lines.append(int(l))
    data = np.array(new_lines)
    return data