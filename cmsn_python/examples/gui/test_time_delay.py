#!/usr/bin/env python
import os
import sys
import time
import numpy as np
import pandas as pd
import mainwindow
from PyQt5.QtWidgets import QMainWindow, QApplication, QInputDialog, QMessageBox
from PyQt5 import QtCore

current_dir = os.path.dirname(os.path.abspath(__file__))
lib_path = os.path.join(current_dir, '..', '..', 'lib')
sys.path.append(lib_path)
from crimson_sdk import *

_WINDOW_SIZE = 1250
_SAMPLE_RATE = 250 # buffer length (s) = window_size * sample_rate = 5s. Therefore, fft result is based on 5s window
_HISTORY_LENGTH = 20 # history length = 20s?
main_window = None
_src_dir = os.path.abspath(os.path.dirname(__file__))
if not os.path.isdir(_src_dir + '/data'):
    os.mkdir(_src_dir + '/data')

print(f"CrimsonSDK version: {get_sdk_version()}")    
class MyDeviceListener(CMSNDeviceListener):
    def on_raw_eeg_data(self, eeg_data):
        # without pre-processing
        pass
        # print("Raw EEG data:" + str(eeg_data.eeg_data))
        
    # 主要是这个 eeg_data。它的时延迟是什么样的？
    def on_eeg_data(self, eeg_data):
        if main_window is not None:
            main_window._eeg_graph_signal.emit(eeg_data)
            # main_window.update_eeg_and_fft(eeg_data) 表示是不是要实时更新 eeg and fft
            if main_window._collect_data:
                main_window._eeg_history.append([time.time(), eeg_data.eeg_data, main_window._attention_history[-1]])
            elif not main_window._collect_data and len(main_window._eeg_history) != 0:
                _data_dir = os.path.join(_src_dir, "data", main_window._data_file_name + ".csv")
                df = pd.DataFrame(main_window._eeg_history, columns=['time_stamp', 'raw_eeg', 'attention'])
                df.to_csv(_data_dir, index=None)
                main_window._eeg_history = []
                print('Successfully Saved Data')

    def on_attention(self, attention):
        if main_window is not None:
            main_window._attention_graph_signal.emit(attention)

    def on_brain_wave(self, brain_wave):
        if main_window is not None:
            main_window.label_delta_value.setText(str(round(brain_wave.delta, 2)))
            main_window.label_theta_value.setText(str(round(brain_wave.theta, 2)))
            main_window.label_alpha_value.setText(str(round(brain_wave.alpha, 2)))
            main_window.label_low_beta_value.setText(str(round(brain_wave.low_beta, 2)))
            main_window.label_high_beta_value.setText(str(round(brain_wave.high_beta, 2)))
            main_window.label_gamma_value.setText(str(round(brain_wave.gamma, 2)))

    def on_connectivity_change(self, connectivity):
        print("Connectivity:" + connectivity.name)
        if main_window is not None:
            main_window.label_connectivity_value.setText(connectivity.name.upper())
            if connectivity == Connectivity.disconnected:
                main_window.button_connect.setText("Connect")
            elif connectivity == Connectivity.connected:
                main_window.pair()

    def on_contact_state_change(self, contact_state):
        if main_window is not None:
            main_window.label_contact_value.setText(contact_state.name.upper())

    def on_meditation(self, meditation):
        if main_window is not None:
            main_window._meditation_graph_signal.emit(meditation)

    def on_device_info_ready(self, device_info):
        if main_window is not None:
            print(f"serial_number:{device_info.serial_number}")
            main_window.label_manufacturer_value.setText(device_info.manufacturer_name)
            main_window.label_model_number_value.setText(device_info.model_number)
            main_window.label_serial_number_value.setText(device_info.serial_number)
            main_window.label_hardware_revision_value.setText(device_info.hardware_revision)
            main_window.label_firmware_revision_value.setText(device_info.firmware_revision)


def config_response_callback(device, error):
    print("DEBUG:response error:" + str(error))
    if error != 0 and main_window is not None:
        main_window.show_message("Config error", "For device" + device.name, "Error code:" + str(error))


def on_pair_response(device, response):
    print(f"Paring result", response.success())

class MainWindow(QMainWindow, mainwindow.Ui_MainWindow):
    _selected_device = None
    _data_file_name = None
    _collect_data = False
    _device_list = []
    _eeg_history = []
    _brain_wave = {}
    _eeg_data = [0] * _WINDOW_SIZE
    _attention_history = [0] * _HISTORY_LENGTH
    _meditation_history = [0] * _HISTORY_LENGTH
    _attention_range = [0, 100]
    _meditation_range = [0, 100]

    _eeg_graph_signal = QtCore.pyqtSignal(object)
    _attention_graph_signal = QtCore.pyqtSignal(float)
    _meditation_graph_signal = QtCore.pyqtSignal(float)

    def __init__(self):
        global main_window
        super(MainWindow, self).__init__()
        self.setupUi(self)
        self.init_ui()
        self.eeg_raw_data_plot = self.plot_raw_data.plot()
        self.fft_plot = self.plot_fft.plot()
        self.plot_fft.setRange(xRange=[0,60], yRange=[0, 2])
        self.attention_curve_plot = self.plot_attention.plot()
        self.meditation_curve_plot = self.plot_meditation.plot()
        self.plot_attention.setRange(yRange=self._attention_range)
        self.plot_meditation.setRange(yRange=self._meditation_range)
        main_window = self
        # Signal connections
        self._eeg_graph_signal.connect(self.update_eeg_and_fft)
        self._attention_graph_signal.connect(self.update_attention)
        self._meditation_graph_signal.connect(self.update_meditation)

    def init_ui(self):
        self.button_scan.clicked.connect(self.clicked_scan_button)
        self.button_connect.clicked.connect(self.clicked_connect_button)
        self.button_send_afe.clicked.connect(self.clicked_send_afe_button)
        self.button_send_acc.clicked.connect(self.clicked_send_acc_button)
        self.button_start.clicked.connect(self.clicked_start_button)
        self.button_collect_data.clicked.connect(self.clicked_collect_data_button)
        self.button_red.clicked.connect(self.clicked_red_button)
        self.button_green.clicked.connect(self.clicked_green_button)
        self.button_blue.clicked.connect(self.clicked_blue_button)
        self.button_rename.clicked.connect(self.clicked_rename_button)

        # IMU sample rate
        self.combo_box_acc_sample_rate.addItems(list(map(lambda x: x.name.upper(), list(IMUDataSampleRate))))
        self.combo_box_acc_sample_rate.setCurrentIndex(1)

        # AFE sample rate, 250Hz        
        self.combo_box_afe_sample_rate.addItems(list(map(lambda x: x.name.upper(), list(AFEDataSampleRate))))
        self.combo_box_afe_sample_rate.setCurrentIndex(1) 

    def show_message(self, title, msg, detail):
        msgbox = QMessageBox()
        msgbox.setIcon(QMessageBox.Information)
        msgbox.setWindowTitle(title)
        msgbox.setText(msg)
        if detail is not None:
            msgbox.setInformativeText(detail)
        # msg.setDetailedText("")
        msgbox.setStandardButtons(QMessageBox.Ok)

    # here, provide how to update the buffer and culculate the fft
    def update_eeg_and_fft(self, eeg_data):
        
        del self._eeg_data[:len(eeg_data.eeg_data)]
        self._eeg_data.extend(eeg_data.eeg_data)
        # update eeg plot
        main_window.eeg_raw_data_plot.setData(self._eeg_data)
        # fft
        l = len(self._eeg_data)  # Length of signal
        y_rfft = np.fft.rfft(self._eeg_data)
        s2 = np.abs(y_rfft / l)  # normalized two-sided spectrum s2
        f2 = np.linspace(0.0, _SAMPLE_RATE / 2, l // 2 + 1)
        # update fft plot
        main_window.fft_plot.setData(f2, s2)
        
        """ DEBUG:Alpha band power
        alpha = 0
        for i in range(len(s2)):
            f = f2[i]
            if f > 8 and f < 12:
                alpha += s2[i]
        print("DEBUG:Alpha band power:" + str(alpha))
        """

        alpha = 0
        for i in range(len(s2)):
            f = f2[i]
            if f > 8 and f < 12:
                alpha += s2[i]
        print("DEBUG:Alpha band power:" + str(alpha))

    def update_attention(self, attention):
        self.label_attention_level_value.setText(str(int(attention)))

        del self._attention_history[0]
        self._attention_history.append(attention)
        main_window.attention_curve_plot.setData(self._attention_history)

    def update_meditation(self, meditation):
        self.label_meditation_level_value.setText(str(int(meditation)))

        del self._meditation_history[0]
        self._meditation_history.append(meditation)
        main_window.meditation_curve_plot.setData(self._meditation_history)

    def __on_found_device(self, device):
        if device not in self._device_list:
            print("Found device:", device.name)
            self.combo_box_device_list.addItem(device.name)
            self._device_list.append(device)

    def clicked_scan_button(self):
        if self.button_scan.text() == "Scan":
            try:
                self._device_list.clear()
                self.combo_box_device_list.clear()
                CMSNSDK.start_device_scan(self.__on_found_device)
                self.button_scan.setText("Stop scan")
            except KeyboardInterrupt:
                print("Early termination from keyboard")
        else:
            CMSNSDK.stop_device_scan()
            self.button_scan.setText("Scan")

    def clicked_connect_button(self):
        # choose device
        device_name = self.combo_box_device_list.currentText()
        for device in self._device_list:
            if device.name == device_name:
                self._selected_device = device
                self._selected_device.set_listener(MyDeviceListener())
        # connect device
        if self.button_connect.text() == "Connect":
            QApplication.processEvents()
            self.button_connect.setText("Disconnect")
            self._selected_device.connect()
            if self.button_scan.text() == "Stop scan":
                self.button_scan.click()
        else:
            QApplication.processEvents()
            self.button_connect.setText("Connect")
            self.button_start.setText("Start")
            self.button_collect_data.setText("Collect Data")
            self._selected_device.disconnect()
            self.label_manufacturer_value.clear()
            self.label_model_number_value.clear()
            self.label_serial_number_value.clear()
            self.label_hardware_revision_value.clear()
            self.label_firmware_revision_value.clear()
            self.label_connectivity_value.clear()
            self.label_contact_value.clear()
            self.label_attention_level_value.setText("0")
            self.label_meditation_level_value.setText("0")
            self.eeg_raw_data_plot.clear()
            self.fft_plot.clear()
            self.attention_curve_plot.clear()
            self.meditation_curve_plot.clear()

    def clicked_start_button(self):
        if self.button_start.text() == "Start":
            if self._selected_device is not None and self._selected_device.connectivity == Connectivity.connected:
                self._selected_device.start_eeg_stream(config_response_callback)
                QApplication.processEvents()
                self.button_start.setText("Stop")
        else:
            self._selected_device.stop_eeg_stream(config_response_callback)
            QApplication.processEvents()
            self.button_start.setText("Start")

    def pair(self):
        self._selected_device.pair(on_pair_response)

    def clicked_rename_button(self):
        text, ok = QInputDialog.getText(self, 'Input Dialog', 'Enter new device name:')
        if ok:
            self._selected_device.set_device_name(str(text), config_response_callback)

    def clicked_collect_data_button(self, eeg_data):
        if self.button_collect_data.text() == "Collect Data":
            QApplication.processEvents()
            text, ok = QInputDialog.getText(self, 'Event Name', 'Set Data File Name:')
            if ok:
                self.button_collect_data.setText("Stop")
                self._collect_data = True
                self._data_file_name = str(text) + "_filtered"

        elif self.button_collect_data.text() == "Stop":
            self._collect_data = False
            QApplication.processEvents()
            self.button_collect_data.setText("Collect Data")

    def clicked_send_acc_button(self):
        sample_rate = list(IMUDataSampleRate)[self.combo_box_acc_sample_rate.currentIndex()]
        if sample_rate == IMUDataSampleRate.off: 
            self._selected_device.stop_imu_stream()
        else:
            self._selected_device.start_imu_stream(sample_rate)

    def clicked_send_afe_button(self):
        sample_rate = list(AFEDataSampleRate)[self.combo_box_afe_sample_rate.currentIndex()]
        self._selected_device.config_afe(sample_rate)

    def clicked_red_button(self):
        self._selected_device.set_led_color((255, 0, 0), config_response_callback)

    def clicked_green_button(self):
        self._selected_device.set_led_color((0, 255, 0), config_response_callback)

    def clicked_blue_button(self):
        self._selected_device.set_led_color((0, 0, 255), config_response_callback)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
