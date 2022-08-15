# clima3 - AEMET OpenData analyzer and viewer
# Jorge Fabregat López (jfabregat@protonmail.com)

# This file is part of clima3

# clima3 is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import requests
import datetime
import math
import time
import clima3_gui

# Constants

# AEMET only allows requests of a max of 5 years. Any timespan longer than that
# must be split in periods smaller than 5 years. (That is 5 years minus 1 day).
# The 5 year period here is represented in milliseconds taking into account that
# every 5 year period has a leap year. (So an extra day).
MAX_TIMEFRAME = 157680000000
DAY_IN_US = 86400000

# TODO Temporary solution. Should be loaded from a config file.
HOSTNAME = 'https://opendata.aemet.es/opendata'
API_KEY = 'eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJqZmFicmVnYXRAcHJvdG9ubWFpbC5jb20iLCJqdGkiOiJhYThhYTI4Zi00MjViLTQzNmYtODJiMC1hMjNlYWVkNWU1MWQiLCJpc3MiOiJBRU1FVCIsImlhdCI6MTY0NTExMDIyMCwidXNlcklkIjoiYWE4YWEyOGYtNDI1Yi00MzZmLTgyYjAtYTIzZWFlZDVlNTFkIiwicm9sZSI6IiJ9.STKW2NwMlRC-HhWFpZOOE5fUZvub_kON0eLGNHPmKdI'

def get_list_url():
  ep = '/api/valores/climatologicos/inventarioestaciones/todasestaciones'
  return HOSTNAME + ep + '/?api_key=' + API_KEY

def get_station_list():
  url = get_list_url()
  response = requests.get(url)

  # Parse response and get data from URL
  if response.status_code == 200:
    response = response.json()
    if response['estado'] != 200:
      print('Got ' + str(response['estado']) + ' from AEMET: ' + response['descripcion'])
      response = [];
    else:
      url = response['datos']
      response = requests.get(url)
      response = response.json()
  else:
    print('[get_data]: Got ' + str(response.status_code) + ' while trying to reach AEMET')

  return response

def compile_station_list(stations):
  compiled_stations = {}
  for s in stations:
    if s['provincia'] not in compiled_stations:
      compiled_stations[s['provincia']] = {}

    compiled_stations[s['provincia']][s['nombre']] = s['indicativo']
  
  return compiled_stations

def get_station_data(indicative, date_from, date_to):
  dates = generate_dates(date_from, date_to)
  urls = get_data_urls(indicative, dates)
  data = get_data(urls)

  return data

def generate_dates(date_from, date_to):
  # date_from and date_to are in milliseconds
  timeframes = math.ceil((date_to - date_from) / MAX_TIMEFRAME)
  last_timeframe = (date_to - date_from) % MAX_TIMEFRAME

  s_from = date_from;
  # If only 1 iteration add the remaining time unless the division is exact by less than 1 day
  if timeframes <= 1 and last_timeframe >= DAY_IN_US:
    s_to = s_from + last_timeframe
  else:
    s_to = s_from + MAX_TIMEFRAME
  
  print('[generate_dates]: Splitting request in ' + str(timeframes) + ' independent requests') 
  
  dates = []
  for i in range(timeframes):
    dates.append({'ini': timestamp_to_datetime(s_from).strftime('%Y-%m-%dT00:00:00UTC'),
                'fin': timestamp_to_datetime(s_to).strftime('%Y-%m-%dT23:59:59UTC')})

    print('[generate_dates]: Split ' + str(i) + ': ' + dates[i]['ini'] + ' to ' + dates[i]['fin'])

    if i == 0:
      s_from = s_from + MAX_TIMEFRAME + DAY_IN_US
    else:
      s_from = s_from + MAX_TIMEFRAME

    # When preparing for the last iteration only add the remaining time unless the division is exact by less than 1 day
    if i == timeframes - 2 and last_timeframe >= DAY_IN_US:
      s_to = s_to + last_timeframe
    else:
      s_to = s_to + MAX_TIMEFRAME

  return dates

def timestamp_to_datetime(timestamp):
  return datetime.datetime(1970, 1, 1) + datetime.timedelta(milliseconds=timestamp)
 
def get_data_urls(indicative, dates):
  urls = []
  for i in range(len(dates)):
    ep = '/api/valores/climatologicos/diarios/datos/fechaini/' + dates[i]['ini'] + '/fechafin/' + dates[i]['fin'] + '/estacion/' + indicative
    urls.append(HOSTNAME + '/' + ep + '/?api_key=' + API_KEY)

  return urls

def get_data(urls):
  data = []
  for i in range(len(urls)):
    if i % 10 == 0 and i != 0:
      print('[get_data]: Waiting 5 seconds to avoid AEMET request restrictions')
      time.sleep(5)

    print('[get_station_data]: Requesting split ' + str(i + 1) + ' of ' + str(len(urls)) + ': ' + urls[i])
    
    response = requests.get(urls[i])
    if response.status_code == 200:
      response = response.json()
      if response['estado'] != 200:
        print('[get_data]: Got ' + str(response['estado']) + ' from AEMET: ' + response['descripcion'])
        s_data = []
      else:
        data_url = response['datos']
        response = requests.get(data_url)
        s_data = response.json()
    else:
      print('[get_data]: Got ' + str(response.status_code) + ' while trying to reach AEMET')
      s_data = []

    data = data + s_data

  return data
