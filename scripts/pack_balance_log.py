# -*- coding: utf-8 -*-
"""
This file contains a script to allow input of pack voltage readings.

pcm60x_to_gdocs is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

pcm60x_to_gdocs is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with pcm60x_to_gdocs. If not, see <http://www.gnu.org/licenses/>.

Copyright (c) Lachlan Rogers
"""

import time
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import plotly.plotly as py
import plotly.graph_objs as go
from datetime import datetime

PACKNAME = ['A', 'B', 'C', 'D', 'E', 'F', 'G']

def get_input_pack_voltage(packnum):
    """Do user input of pack voltage"""
    pack_v = input("Voltage reading for Pack {}: ".format(PACKNAME[packnum]))

    # TODO: sanity check input

    return float(pack_v)


def main():
    """Get pack voltages and update balance plot"""

    string_voltages = np.zeros(7)
    
    for i in range(7):
        string_voltages[i] = get_input_pack_voltage(i)

    mean_v = np.mean(string_voltages)

    top_v = max(string_voltages)
    bottom_v = min(string_voltages)

    out_of_balance_range = [100 * bottom_v / mean_v - 100, 100 * top_v / mean_v - 100]

    print(string_voltages, out_of_balance_range)

main()
