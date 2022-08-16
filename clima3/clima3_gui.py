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
import clima3_aemet
import libclima3

class Window(object):
  def __init__(self):
    self.app = QtWidgets.QApplication(sys.argv)

    self.window = uic.loadUi('../ui/main.ui')
    self.window.button_get.clicked.connect(self.get_and_process_data)
    self.window.button_get.setEnabled(False)
    self.window.graph_temperature.setAxisItems({'bottom': pyqtgraph.DateAxisItem()})
    self.window.show()

  def enter_exec_loop(self):
    self.app.exec()

  def msg(self, text):
    self.window.statusbar.showMessage(text)

  def generate_province_sel_menu(self):
    self.msg('Getting station info from AEMET')
    self.stations = clima3_aemet.get_station_list()
    self.stations = clima3_aemet.compile_station_list(self.stations)

    self.window.list_provinces.clear()
    for s in self.stations.keys():
      self.window.list_provinces.addItem(s)

    self.update_station_sel_menu()
    self.window.list_provinces.currentTextChanged.connect(self.update_station_sel_menu)

    self.window.button_get.setEnabled(True)
    self.msg('Idle')

  def update_station_sel_menu(self):
    self.window.list_stations.clear()
    for s in self.stations[str(self.window.list_provinces.currentText())].keys():
      self.window.list_stations.addItem(s)

  def get_and_process_data(self):
    self.msg('Getting data from AEMET')
    indicative = self.stations[str(self.window.list_provinces.currentText())][str(self.window.list_stations.currentText())]
    date_from = self.window.date_from.dateTime().toMSecsSinceEpoch()
    date_to = self.window.date_to.dateTime().toMSecsSinceEpoch()
    data = clima3_aemet.get_station_data(indicative, date_from, date_to)
    self.plot(self.window.graph_temperature, data, 'tmax')
    self.msg('Idle')
    
  def plot(self, graph, data, key):
    x = [d['fecha'].timestamp() for d in data]
    y = [d[key] for d in data]
    graph.plot(x, y)
