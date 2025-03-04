#!/usr/bin/env python
import os
import sys
import time

current_dir = os.path.dirname(os.path.abspath(__file__))
lib_path = os.path.join(current_dir, '..', '..', 'lib')
sys.path.append(lib_path)
from crimson_sdk import *

_TOTAL_RUN_TIME = 6 * 60  # seconds

_TARGET_DEVICE_NAME = "BY11-1388A"

_target_device = None

print("CrimsonSDK version:" + get_sdk_version())

def on_eeg_stream_started(device, res):
    print(f"EEG Data stream started result:{res.success()}")

def on_imu_stream_started(device, res):
    print(f"IMU Data stream started result: {res.success()}")

def on_pair_response(device, res):
    print(f"Paring result: {res.success()}")
    if res.success():
        device.start_eeg_stream(on_eeg_stream_started)

# A Listerner example. 
class DeviceListener(CMSNDeviceListener):
    def on_connectivity_change(self, connectivity):
        print(f"Connectivity: {connectivity.name}")
        if connectivity == Connectivity.connected:
            _target_device.pair(on_pair_response)

    def on_contact_state_change(self, contact_state):
        print(f"Contact state: {contact_state.name}")

    def on_orientation_change(self, orientation):
        print(f"Orientation: {orientation.name}")

    def on_eeg_data(self, eeg):
        if eeg.signal_type == AFEDataSignalType.lead_off_detection:
            print("Received lead off detection signal, skipping the packet.")
            return
        print(f"EEG SN: {eeg.sequence_num}, signal type: {eeg.signal_type.name}, data len: {len(eeg.eeg_data)}")

    # it has provided alpha, low_beta .... 
    def on_brain_wave(self, brain_wave):
        print(f"Brain wave, alpha: {brain_wave.alpha}, low_beta: {brain_wave.low_beta}, high_beta: {brain_wave.high_beta}, gamma: {brain_wave.gamma}, theta: {brain_wave.theta}, delta: {brain_wave.delta}")    

    def on_attention(self, attention):
        print(f"Attention: {attention}")

    # To Sariha: in this project, we don't need meditation index. 
    def on_meditation(self, meditation):
        print(f"Meditation: {meditation}")

    def on_imu_data(self, imu):
        print(f"IMU Data: SN: {imu.acc_data.sequence_num}")

def on_found_device(device):
    print('Found device:' + device.name)
    if device.name == _TARGET_DEVICE_NAME:
        global _target_device
        # print("Found %d devices" % len(devices))
        print("Stop scanning for more devices")
        CMSNSDK.stop_device_scan()
        _target_device = device
        _target_device.set_listener(DeviceListener())
        _target_device.connect()

try:
    CMSNSDK.start_device_scan(on_found_device)
    time.sleep(_TOTAL_RUN_TIME)
    print("Timeout, disposing")
except KeyboardInterrupt:
    print("Early termination from keyboard")
