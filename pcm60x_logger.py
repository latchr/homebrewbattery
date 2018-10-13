# -*- coding: utf-8 -*-
"""
This file contains a script to log status data from the PCM 60x solar charge controller

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

import serial
import time
import datetime
import numpy as np
import gspread
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from oauth2client.service_account import ServiceAccountCredentials


QPIGS = b"\x51\x50\x49\x47\x53\xB7\xA9\x0D"


def open_gsheet(worksheet_idx=0):
    """ Authenticate with GDocs and open the spreadsheet for editing"""
    scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name(
        'pythontest-425f92ff2f94.json',
        scope
    )
    client = gspread.authorize(creds)

    sheet = client.open("pcm60x_charging_log").get_worksheet(worksheet_idx)

    return sheet


def read_pcm60x(ser):
    """Serial communication with PCM 60x charge controller"""
    ser.write(QPIGS)
    result = ser.read(70)
    ser.read()
    ser.read()

    return result


def read_pcm60x_dummy(ser):
    """ Simulate serial communication for debugging and testing
    """
    return '032.3 24.02 00.10 00.00 00.10 0045 +023'.encode()


def save_log(data, times):
    """Save the data to a log file and save a thumbnail plot"""

    nptimes = np.zeros(len(times), dtype='datetime64[ms]')

    for i, entry in enumerate(data):
        nptimes[i] = np.datetime64(times[i])

    numdata = np.array(data)

    datestring = datetime.datetime.now().strftime("%Y%m%d")
    np.savetxt(datestring + '_solar_charge_log.csv', numdata)
    np.savetxt(datestring + '_solar_charge_log_times.csv', nptimes, fmt='%s')

    # Draw figure
    fig, ax = plt.subplots(3, figsize=[8, 8])

    hours = mdates.HourLocator()   # every year
    hoursFmt = mdates.DateFormatter('%H')

    # format the ticks
    for axis in ax:
        axis.xaxis.set_major_locator(hours)
        axis.xaxis.set_major_formatter(hoursFmt)

    ax[0].plot(nptimes, numdata[:, 2])
    ax[1].plot(nptimes, numdata[:, 3])
    ax[2].plot(nptimes, numdata[:, 6])

    ax[2].set_xlabel('Time (clock hour)')
    ax[0].set_ylabel('Battery Voltage (V)')
    ax[1].set_ylabel('Charging current (A)')
    ax[2].set_ylabel('Charging power (W)')

    fig.savefig(datestring + '_solar_charge_log.png')


def write_daily_energy(starttime, energy):
    """Write daily energy harvested figure to another sheet."""
    energy_sheet = open_gsheet(worksheet_idx=2)
    datestring = '{}/{}/{}'.format(starttime.day, starttime.month, starttime.year)
    energy_sheet.insert_row([datestring, energy], 2, value_input_option='USER_ENTERED')


def reset_gsheet(spreadsheet):
    """ Reset the spreadsheet for a new day of data"""
    for i in range(700):
        spreadsheet.delete_row(2)
        time.sleep(2)


def main():
    """Logging loop, querying PCM 60x status and logging to GSheet"""

    # Connect serial
    ser = serial.Serial(port='/dev/ttyACM0', baudrate=2400, timeout=2)

    # Open Google spreadsheet
    sheet = open_gsheet()

    # Clear previous day's data
    reset_gsheet(sheet)

    # Initialise data arrays
    data = []
    times = []
    energy = 0.0

    # Serial queries take a while, so the loop is referenced to clock time rather
    # than counting the number of loops.
    start = datetime.datetime.now()

    logtime = datetime.datetime.now()
    while (logtime - start).seconds < 13.5 * 60 * 60:
        result = read_pcm60x(ser)
        thistime = datetime.datetime.now()

        try:
            row = [logtime.hour + (logtime.minute / 60) + (logtime.second / 3600),
                   float(result[1:6].decode()),
                   float(result[7:12].decode()),
                   float(result[13:18].decode()),
                   float(result[19:24].decode()),
                   float(result[25:30].decode()),
                   float(result[31:35].decode()),
                   float(result[36:40].decode()),
                   ]

            times.append(logtime)
            data.append(row)
            energy += row[6] * (thistime - logtime).seconds / 3600

            try:
                sheet.insert_row(row, 2)
                sheet.update_acell('I1', energy)

            except:
                # Re-open Google spreadsheet
                sheet = open_gsheet()
                try:
                    sheet.insert_row(row, 2)
                except:
                    print('Google docs upload failed at {}'.format(logtime))

        except:
            print('Serial read returned useless data at {}'.format(logtime))

        time.sleep(60)
        logtime = thistime

    write_daily_energy(start, energy)

    save_log(data, times)


main()
