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

import sys
from PyQt6 import QtWidgets, uic
from pyqtgraph import PlotWidget
import pyqtgraph
import pandas
import clima3_aemet
import clima3_stat

class Window(object):
  def __init__(self):
    self.app = QtWidgets.QApplication(sys.argv)
    self.window = uic.loadUi('../ui/main.ui')

    self.window.button_get.clicked.connect(self.get_aemet_data)
    self.window.button_get.setEnabled(False)

    self.window.graph_data.setAxisItems({'bottom': pyqtgraph.DateAxisItem()})
    self.window.graph_tsd_trend.setAxisItems({'bottom': pyqtgraph.DateAxisItem()})
    self.window.graph_tsd_seasonal.setAxisItems({'bottom': pyqtgraph.DateAxisItem()})
    self.window.graph_tsd_remainder.setAxisItems({'bottom': pyqtgraph.DateAxisItem()})
    
    self.window.list_decomps.addItem('STL')
    self.window.list_decomps.addItem('Classical')
    self.window.list_interps.addItem('Pchip')
    self.window.list_interps.addItem('Akima')
    self.window.list_interps.addItem('Cubic Spline')
    self.window.list_interps.addItem('Cubic')
    self.window.list_interps.addItem('Quadratic')
    self.window.list_interps.addItem('Linear')

    self.window.statusbar.showMessage('Source: AEMET')

    self.window.show()

  def enter_exec_loop(self):
    self.app.exec()

  def msg(self, text):
    self.window.statusbar.showMessage(text)

  def generate_province_sel_menu(self):
    self.stations = clima3_aemet.get_station_list()
    self.stations = clima3_aemet.compile_station_list(self.stations)

    self.window.list_provinces.clear()
    for s in self.stations.keys():
      self.window.list_provinces.addItem(s)

    self.update_station_sel_menu()
    self.window.list_provinces.currentTextChanged.connect(self.update_station_sel_menu)

    self.window.button_get.setEnabled(True)

  def update_station_sel_menu(self):
    self.window.list_stations.clear()
    for s in self.stations[str(self.window.list_provinces.currentText())].keys():
      self.window.list_stations.addItem(s)

  def generate_variable_sel_menu(self):
    self.window.list_variables.clear()
    for v in self.data.columns:
      self.window.list_variables.addItem(v)

    self.window.list_variables.currentTextChanged.connect(self.process_data)
    self.window.list_decomps.currentTextChanged.connect(self.process_data)
    self.window.list_interps.currentTextChanged.connect(self.process_data)

  def get_aemet_data(self):
    # Get data from AEMET API
    indicative = self.stations[str(self.window.list_provinces.currentText())][str(self.window.list_stations.currentText())]
    date_from = self.window.date_from.dateTime().toMSecsSinceEpoch()
    date_to = self.window.date_to.dateTime().toMSecsSinceEpoch()
    self.data = clima3_aemet.get_station_data(indicative, date_from, date_to)
    self.generate_variable_sel_menu()
    self.process_data()

  def process_data(self):
    if self.window.list_decomps.currentText() == 'STL':
      if self.window.list_variables.currentText() == 'prec':
        self.process_data_stl(self.data, seasonal=7, inner_iter=2, outer_iter=10)
      elif self.window.list_variables.currentText() == 'sol':
        self.process_data_stl(self.data, seasonal=35)
      else:
        self.process_data_stl(self.data, seasonal=35, inner_iter=2, outer_iter=10)

    else:
      self.process_data_classical(self.data)

  def process_data_classical(self, data):
    # Clean up received data and process it
    variable = self.window.list_variables.currentText()
    interp = self.window.list_interps.currentText()
    data = clima3_stat.constrain_series_to_observed(data, variable)
    data = clima3_stat.clean_dataset(data, variable)
    data = clima3_stat.interpolate(data, variable, interp)
    data = clima3_stat.classical(data, variable)
    self.update_graphs(data, variable)

  def process_data_stl(self, data, seasonal=None, trend=None, inner_iter=5, outer_iter=0):
    # Clean up received data and process it
    variable = self.window.list_variables.currentText()
    interp = self.window.list_interps.currentText()
    data = clima3_stat.constrain_series_to_observed(data, variable)
    data = clima3_stat.clean_dataset(data, variable)
    data = clima3_stat.interpolate(data, variable, interp)
    data = clima3_stat.stl(data, variable, 
                           seasonal=seasonal,
                           trend=trend, 
                           inner_iter=inner_iter, 
                           outer_iter=outer_iter)
    self.update_graphs(data, variable)


  def update_graphs(self, data, key):
    self.plot(self.window.graph_data, data, key)
    self.plot(self.window.graph_tsd_trend, data, key + '_trend')
    self.plot(self.window.graph_tsd_seasonal, data, key + '_seasonal')
    self.plot(self.window.graph_tsd_remainder, data, key + '_resid')
    
    
  def plot(self, graph, data, key):
    graph.clear()
    x = [d.timestamp() for d in data.index]
    y = [d for d in data.loc[:,key]]
    graph.plot(x, y)
