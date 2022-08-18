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

import pandas
from statsmodels.tsa.seasonal import STL

import datetime
import os

MAX_TOLERABLE_DATA_GAP = 62

def stl(data, key):
  # Prepare the dataset
  # Constrain the dataset to regions where enough contiguous data is available
  data = clean_holes(data, key, MAX_TOLERABLE_DATA_GAP)
  
  # Constrain the dataset to year boundaries and crop the extra day from leap
  # years
  data = constrain_series_to_year(data)
  data = crop_leap_years(data)

  # Interpolate missing values
  data.interpolate(method='pchip', inplace=True)

  # Apply STL
  result = STL(data[key], period = 365).fit()
  data[key + '_trend'] = result.trend
  data[key + '_seasonal'] = result.seasonal
  data[key + '_resid'] = result.resid

  # FIXME Debug feature: dump data to csv for analysis
  data.to_csv(os.getcwd() + '/stl_dump.csv')

  return data

def clean_holes(data, key, hole):
  hole_size = 0
  for d in data.index:
    if pandas.isna(data.loc[d, key]):
      hole_size = hole_size + 1
    
    if not pandas.isna(data.loc[d, key]):
      if hole_size > hole:
        data = data.loc[d:, :]
        print('[clean holes]: Cleaned ' + str(hole_size) + ' days until ' + str(d))

      hole_size = 0 

  return data
      
def crop_leap_years(data):
  for d in data.index:
    if d.month == 2 and d.day == 29:
      data = data.drop(d)

  return data

def constrain_series_to_year(data):
  for d in data.index:
    if d.month == 1 and d.day == 1:
      break
    else:
      data = data.drop(d)

  for d in reversed(data.index):
    if d.month == 12 and d.day == 31:
      break
    else:
      data = data.drop(d)

  return data

def constrain_series_to_observed(data, key):
  for d in data.index:
    if pandas.isna(data.loc[d, key]):
      data = data.drop(d)
    else:
      break

  for d in reversed(data.index):
    if pandas.isna(data.loc[d, key]):
      data = data.drop(d)
    else:
      break
  
  return data

def interpolate_missing(data, key):

  return data 
