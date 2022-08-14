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
import clima3_gui

# Constants
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
  if response.status_code != 200:
    print('Got ' + str(response.status_code) + ' from AEMET while getting station list')
    # TODO error_msg('Got ' + str(response.status_code) + ' from AEMET while getting station list')
    response = [];
  else:
    response = response.json()
    url = response['datos']
    response = requests.get(url)
    response = response.json()

  return response

def compile_station_list(stations):
  compiled_stations = {}
  for s in stations:
    if s['provincia'] not in compiled_stations:
      compiled_stations[s['provincia']] = {}

    compiled_stations[s['provincia']][s['nombre']] = s['indicativo']
  
  return compiled_stations
