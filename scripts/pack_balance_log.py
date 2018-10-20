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

import numpy as np
import plotly.plotly as py
import plotly.graph_objs as go
from datetime import datetime

PACKNAME = ['A', 'B', 'C', 'D', 'E', 'F', 'G']


def get_input_pack_voltage(packnum):
    """Do user input of pack voltage"""
    pack_v = input("Voltage reading for Pack {}: ".format(PACKNAME[packnum]))

    # TODO: sanity check input

    return float(pack_v)


def add_data_to_chart(measure_time, string_percentages, mean_v):
    """Add data to the online plotly chart"""

    trace1 = go.Scatter(
        x = [measure_time], 
        y = [string_percentages[0]], 
        name = "pack A", 
        yaxis = "y2", 
    )
    
    trace2 = go.Scatter(
        x = [measure_time], 
        y = [string_percentages[1]], 
        name = "pack B", 
        yaxis = "y2", 
    )
    
    trace3 = go.Scatter(
        x = [measure_time], 
        y = [string_percentages[2]], 
        name = "pack C", 
        yaxis = "y2", 
    )
    
    trace4 = go.Scatter(
        x = [measure_time], 
        y = [string_percentages[3]], 
        name = "pack D", 
        yaxis = "y2", 
    )
    
    trace5 = go.Scatter(
        x = [measure_time], 
        y = [string_percentages[4]], 
        name = "pack E", 
        yaxis = "y2", 
    )
    
    trace6 = go.Scatter(
        x = [measure_time], 
        y = [string_percentages[5]], 
        name = "pack F", 
        yaxis = "y2", 
    )
    
    trace7 = go.Scatter(
        x = [measure_time], 
        y = [string_percentages[6]], 
        name = "pack G", 
        yaxis = "y2", 
    )
    
    trace8 = go.Scatter(
        x = [measure_time], 
        y = [mean_v], 
        name = "Average pack V", 
        yaxis = "y", 
    )
    
    newdata = [trace1, trace2, trace3, trace4, trace5, trace6, trace7, trace8]
    
    plot_url = py.plot(newdata, filename = 'pack_balance_string1', fileopt='extend')


def main():
    """Get pack voltages and update balance plot"""

    string_voltages = np.zeros(7)
    
    for i in range(7):
        string_voltages[i] = get_input_pack_voltage(i)

    measure_time = datetime.now()

    mean_v = np.mean(string_voltages)

    string_percentages = 100 * string_voltages / mean_v - 100

    add_data_to_chart(measure_time, string_percentages, mean_v)

    # Write raw data to text file
    datestring = str(np.datetime64(measure_time))
    
    # generate an array with strings
    data_arrstr = np.char.mod('%f', string_voltages)
    # combine to a string
    data_str = ",".join(data_arrstr)

    with open('string1_pack_v_log.dat', 'a') as fd:
        fd.write(datestring + ',' + data_str)

    # Print out some feedback upon completion
    top_v = max(string_voltages)
    bottom_v = min(string_voltages)
    out_of_balance_range = [100 * bottom_v / mean_v - 100, 100 * top_v / mean_v - 100]

    print(string_voltages, out_of_balance_range)

main()
