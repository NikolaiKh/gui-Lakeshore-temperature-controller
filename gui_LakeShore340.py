import sys
import time
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
import numpy as np
# import instruments as ik
# import instruments.units as u
from PyQt6 import QtWidgets
import Lakeshore_class
import ctypes


class TemperatureControl(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Temperature Control")
        self.setWindowIcon(QtGui.QIcon('term_icon.png'))

        self.layout = QtWidgets.QVBoxLayout(self)

        self.address_label = QtWidgets.QLabel("Lakeshore GPIB address")
        self.address_input = QtWidgets.QLineEdit('12')

        self.sensor_label = QtWidgets.QLabel("Sensor (A/B)")
        self.sensor_input = QtWidgets.QLineEdit('A')

        self.connect_button = QtWidgets.QPushButton("Connect")
        self.connect_button.clicked.connect(self.lakeshore_init)

        self.status_label = QtWidgets.QLabel("Status: NOT connected")

        self.current_temp_label = QtWidgets.QLabel("Current temperature (K)")
        self.current_temp_input = QtWidgets.QLineEdit('---')

        self.set_point_label = QtWidgets.QLabel("Set point temperature (K)")
        self.set_point_curr_label = QtWidgets.QLabel("Current set point: ---- K")
        self.set_point_input = QtWidgets.QLineEdit('---')

        self.set_temp_button = QtWidgets.QPushButton("Set temperature (K)")
        self.set_temp_button.clicked.connect(self.set_point)

        self.layout.addWidget(self.address_label)
        self.layout.addWidget(self.address_input)
        self.layout.addWidget(self.connect_button)
        self.layout.addWidget(self.status_label)
        self.layout.addWidget(self.sensor_label)
        self.layout.addWidget(self.sensor_input)
        self.layout.addWidget(self.current_temp_label)
        self.layout.addWidget(self.current_temp_input)
        self.layout.addWidget(self.set_point_curr_label)
        self.layout.addWidget(self.set_point_label)
        self.layout.addWidget(self.set_point_input)
        self.layout.addWidget(self.set_temp_button)

        # plot widget
        self.canvas = pg.GraphicsLayoutWidget()
        # self.canvas.setBackground((255, 255, 255))
        self.layout.addWidget(self.canvas)
        #  line plot
        # pen = pg.mkPen(color=(0, 0, 255), width=5)
        self.temperature_plot = self.canvas.addPlot()
        self.temperature_plot.addLegend()
        pen = pg.mkPen(color=(215, 48, 39), width=1)
        self.plot_set_temp = self.temperature_plot.plot(pen=pen, name="SetPoint")
        pen = pg.mkPen(color=(69, 117, 180), width=1)
        self.plot_curr_temp = self.temperature_plot.plot(pen=pen, name="Current temperature")
        self.temperature_plot.setTitle("Temperature vs Time")
        self.temperature_plot.setLabel("left", "Temperature (K)")
        self.temperature_plot.setLabel("bottom", "Time (arb.units)")

        self.x = np.linspace(0, 50., num=100)
        self.X, self.Y = np.meshgrid(self.x, self.x)
        self.counter = 0
        self.xdata = []
        self.ydata = []
        self.setpoint_data = []

    def lakeshore_init(self):
        self.temp_controller = Lakeshore_class.Lakeshore(self.address_input.text())
        self.status_label.setText(self.temp_controller.state)
        self.set_point_input.setText(self.temp_controller.query_setpoint())
        sensor = self.sensor_input.text()
        self.current_temp_input.setText(self.temp_controller.query_temp(sensor))
        ### start updating the window and data ###
        self._update()

    def set_point(self):
        setpoint = self.set_point_input.text()
        self.temp_controller.set_setpoint(setpoint)


    def _update(self):
        sensor = self.sensor_input.text()
        curr_temp = float(self.temp_controller.query_temp(sensor))
        self.current_temp_input.setText(str(curr_temp))
        set_temp = float(self.temp_controller.query_setpoint())
        self.set_point_curr_label.setText(f'Current set point: {set_temp}K')
        # plot current and set temperatures
        self.xdata.append(self.counter)
        self.ydata.append(curr_temp)
        self.setpoint_data.append(set_temp)
        if self.counter > 100:
            del self.xdata[0]
            del self.ydata[0]
            del self.setpoint_data[0]
        self.plot_set_temp.setData(self.xdata, self.setpoint_data)
        self.plot_curr_temp.setData(self.xdata, self.ydata)
        QtCore.QTimer.singleShot(100, self._update)
        self.counter += 1



if __name__ == "__main__":
    myappid = 'Nikolai.temperature.control.10'  # arbitrary string
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

    app = QtWidgets.QApplication([])
    app.setStyle('Fusion')
    window = TemperatureControl()
    window.show()
    app.exec()
