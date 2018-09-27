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
from oauth2client.service_account import ServiceAccountCredentials


QPIGS = b"\x51\x50\x49\x47\x53\xB7\xA9\x0D"

ser = serial.Serial(port='/dev/ttyACM0',baudrate=2400,timeout=2)

ser.write(QPIGS)
result = ser.read(70)
ser.read()
ser.read()
print(result)

scope = ['https://spreadsheets.google.com/feeds',
        'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('pythontest-425f92ff2f94.json', scope)
client = gspread.authorize(creds)


sheet = client.open("pcm60x_charging_log").sheet1




data = []
times = []

start = datetime.datetime.now()

logtime = datetime.datetime.now()
while (logtime - start).seconds < 10*60*60:
    ser.write(QPIGS)
    result = ser.read(70)
    ser.read()
    ser.read()
    
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
    
        try:
            sheet.insert_row(row, 2)
            
        except:
            print('Google docs upload failed at {}'.format(logtime))
            
    except:
        print('Serial read returned useless data at {}'.format(logtime))
    
    logtime = datetime.datetime.now()
    time.sleep(60)





nptimes = np.zeros(len(times), dtype='datetime64[ms]')

for i, entry in enumerate(data):
    nptimes[i] = np.datetime64(times[i])

numdata = np.array(data)



np.savetxt('20180926_solar_charge_log.csv', data)
np.savetxt('20180926_solar_charge_log_times.csv', nptimes, fmt='%s')





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
