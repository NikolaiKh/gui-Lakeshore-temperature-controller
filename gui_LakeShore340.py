import sys
import time
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
import numpy as np
# import instruments as ik
# import instruments.units as u
from PyQt6 import QtWidgets
import Lakeshore_class as TempControl_class
# import OxfordInst_ITC5023S_class as TempControl_class
import ctypes


class TemperatureControl(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Temperature Control")
        self.setWindowIcon(QtGui.QIcon('term_icon.png'))

        # create the elements

        self.address_label = QtWidgets.QLabel("Lakeshore GPIB address")
        self.address_input = QtWidgets.QLineEdit('12')

        self.connect_button = QtWidgets.QPushButton("Connect")
        self.connect_button.clicked.connect(self.lakeshore_init)

        self.status_label = QtWidgets.QLabel("Status: NOT connected")

        self.sensor_label = QtWidgets.QLabel("Sensor (A/B)")
        self.sensor_input = QtWidgets.QLineEdit('A')

        self.rate_label = QtWidgets.QLabel("Temp Ramp [K/min]")
        self.rate_curr_label = QtWidgets.QLabel("Current Temp Ramp: ----- [K/min]")
        self.rate_input = QtWidgets.QLineEdit('10')
        self.rate_button = QtWidgets.QPushButton("Set Ramp")
        self.rate_button.clicked.connect(self.set_rate)

        self.heater_range_label = QtWidgets.QLabel("Heater range ('0'=off; '1'=1.4mW; '2'=14mW; '3'=140mW; '4'=1.4W; '5'=14W)")
        self.heater_range_curr_label = QtWidgets.QLabel("Current heater range: ---- ")
        self.heater_range_input = QtWidgets.QLineEdit('4')
        self.heater_range_button = QtWidgets.QPushButton("Set heater range")
        self.heater_range_button.clicked.connect(self.set_heater_range)

        self.current_temp_label = QtWidgets.QLabel("Current temperature [K]")
        self.current_temp_input = QtWidgets.QLineEdit('---')

        self.set_point_label = QtWidgets.QLabel("Set point [K]")
        self.set_point_curr_label = QtWidgets.QLabel("Current set point: ---- K")
        self.set_point_input = QtWidgets.QLineEdit('---')

        self.set_temp_button = QtWidgets.QPushButton("Set temperature (K)")
        self.set_temp_button.clicked.connect(self.set_point)

        # combine widgets into layout
        self.main_vertical_layout = QtWidgets.QVBoxLayout(self)   # main vertical layout

        # layout for GPIB section
        self.layout_GPIB = QtWidgets.QHBoxLayout()
        self.layout_GPIB.addWidget(self.address_label)
        self.layout_GPIB.addWidget(self.address_input)
        self.layout_GPIB.addWidget(self.connect_button)
        self.main_vertical_layout.addLayout(self.layout_GPIB)

        self.main_vertical_layout.addWidget(self.status_label)

        # Create a horizontal line
        line = QtWidgets.QFrame(self)
        line.setFrameShape(QtWidgets.QFrame.Shape.HLine)  # Set shape to horizontal line
        line.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)  # Optional: for styling
        self.main_vertical_layout.addWidget(line)  # Adding the line to the layout

        # layout for Sensor section
        self.layout_sensor = QtWidgets.QHBoxLayout()
        self.layout_sensor.addWidget(self.sensor_label)
        self.layout_sensor.addWidget(self.sensor_input)
        self.main_vertical_layout.addLayout(self.layout_sensor)
        # Create a horizontal line
        line = QtWidgets.QFrame(self)
        line.setFrameShape(QtWidgets.QFrame.Shape.HLine)  # Set shape to horizontal line
        line.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)  # Optional: for styling
        self.main_vertical_layout.addWidget(line)  # Adding the line to the layout

        # Temperature Rate section
        # self.main_vertical_layout.addWidget(self.rate_label)
        self.layout_rate = QtWidgets.QHBoxLayout()
        self.layout_rate.addWidget(self.rate_curr_label)
        self.layout_rate.addWidget(self.rate_input)
        self.layout_rate.addWidget(self.rate_button)
        self.main_vertical_layout.addLayout(self.layout_rate)
        # Create a horizontal line
        line = QtWidgets.QFrame(self)
        line.setFrameShape(QtWidgets.QFrame.Shape.HLine)  # Set shape to horizontal line
        line.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)  # Optional: for styling
        self.main_vertical_layout.addWidget(line)  # Adding the line to the layout

        #  heater range section
        self.main_vertical_layout.addWidget(self.heater_range_label)
        self.layout_heater_range = QtWidgets.QHBoxLayout()
        self.layout_heater_range.addWidget(self.heater_range_curr_label)
        self.layout_heater_range.addWidget(self.heater_range_input)
        self.layout_heater_range.addWidget(self.heater_range_button)
        self.main_vertical_layout.addLayout(self.layout_heater_range)
        # Create a horizontal line
        line = QtWidgets.QFrame(self)
        line.setFrameShape(QtWidgets.QFrame.Shape.HLine)  # Set shape to horizontal line
        line.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)  # Optional: for styling
        self.main_vertical_layout.addWidget(line)  # Adding the line to the layout

        # current temperature section
        self.layout_curr_temp = QtWidgets.QHBoxLayout()
        self.layout_curr_temp.addWidget(self.current_temp_label)
        self.layout_curr_temp.addWidget(self.current_temp_input)
        self.main_vertical_layout.addLayout(self.layout_curr_temp)

        # set point section
        # self.main_vertical_layout.addWidget(self.set_point_curr_label)
        self.layout_set_point = QtWidgets.QHBoxLayout()
        self.layout_set_point.addWidget(self.set_point_label)
        self.layout_set_point.addWidget(self.set_point_input)
        self.layout_set_point.addWidget(self.set_temp_button)
        self.main_vertical_layout.addLayout(self.layout_set_point)
        # Create a horizontal line
        line = QtWidgets.QFrame(self)
        line.setFrameShape(QtWidgets.QFrame.Shape.HLine)  # Set shape to horizontal line
        line.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)  # Optional: for styling
        self.main_vertical_layout.addWidget(line)  # Adding the line to the layout

        # plot widget
        self.canvas = pg.GraphicsLayoutWidget()
        # self.canvas.setBackground((255, 255, 255))
        self.main_vertical_layout.addWidget(self.canvas)
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
        self.temp_controller = TempControl_class.TemControlDevice(self.address_input.text())
        self.status_label.setText(self.temp_controller.state)
        self.set_point_input.setText(self.temp_controller.query_setpoint())
        sensor = self.sensor_input.text()
        self.current_temp_input.setText(self.temp_controller.query_temp(sensor))
        ### start updating the window and data ###
        self._update()

    def set_point(self):
        setpoint = self.set_point_input.text()
        self.temp_controller.set_setpoint(setpoint)

    def set_rate(self):
        rate = self.rate_input.text()
        self.temp_controller.set_ramp(rate=rate)

    def set_heater_range(self):
        range = self.heater_range_input.text()
        self.temp_controller.set_heater_range(value_range=range)

    def _update(self):
        sensor = self.sensor_input.text()
        curr_temp = float(self.temp_controller.query_temp(sensor))
        self.current_temp_input.setText(str(curr_temp))
        set_temp = float(self.temp_controller.query_setpoint())
        self.set_point_curr_label.setText(f'Current set point: {set_temp} [K]')
        get_heater_range = int(self.temp_controller.query_heater_range())
        self.heater_range_curr_label.setText(f'Current heater range: {get_heater_range}')
        get_curr_rate = float(self.temp_controller.query_ramp())
        self.rate_curr_label.setText(f'Current Temp Ramp: {get_curr_rate} [K/min]')
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
