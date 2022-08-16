# libclima3 - Climate data analysis library
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

def stl(data, key):
  result = STL(data.loc[:,key], period=365).fit()
  data[key + '_trend'] = result.trend
  data[key + '_seasonal'] = result.seasonal
  data[key + '_resid'] = result.resid

  return data
