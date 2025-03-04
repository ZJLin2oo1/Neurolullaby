import os, platform, abc, sys
from enum import IntEnum  # Enum declarations

from cffi import FFI

ffi = FFI()

# Defining SDK constants
_ENABLE_SOCIAL_ENGAGEMENT = True

def load_library():
    lib_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), "..", "libcmsn")

    # 1. load header
    with open(os.path.join(lib_dir, "crimson_sdk.h"), encoding='utf-8') as sdk_header:
        sdk_header = sdk_header.read()                                      \
            .split("//CFFI_DEF_START")[1]                           \
            .split("//CFFI_DEF_END")[0]                             \
            .replace("SDK_EXTERN ", "")                             \
            .replace("#if defined(_WIN32) || TARGET_OS_OSX", "")    \
            .replace("#endif", "")
        ffi.cdef(sdk_header)

    # 2. find library path and load
    arch = platform.architecture()[0]
    if platform.system() == "Darwin":
        return ffi.dlopen(os.path.join(lib_dir, "mac", "libcmsn.dylib"))

    elif platform.system() == "Windows" and arch == "64bit":
        # add path 'python/libcmsn/' to environment variable 'PATH' to load the dependent DLLs.
        os.environ["PATH"] += os.pathsep + os.path.join(lib_dir, "win")
        return ffi.dlopen(os.path.join(lib_dir, "win", "cmsn.dll"))
    else:
        raise Exception("Unsupported platform: " + platform.system() + ", arch: " + arch)


# load CrimsonSDK library
libcmsn = load_library()


def get_sdk_version():
    return ffi.string(libcmsn.cmsn_get_sdk_version()).decode("utf-8")

def set_log_level(level):
    return libcmsn.zl_set_log_level(level)

class CMSNDeviceListener(abc.ABC):
    def on_device_info_ready(self, device_info):
        pass  # print("on_device_info_ready not implemented")

    def on_raw_eeg_data(self, eeg_data):
        pass  # print("on_raw_eeg_data not implemented")

    def on_eeg_data(self, eeg_data):
        pass  # print("on_eeg_data not implemented")

    def on_imu_data(self, imu_data):
        pass  # print("on_imu_data not implemented")

    def on_brain_wave(self, brain_wave):
        pass  # print("on_brain_wave not implemented")

    def on_attention(self, attention):
        pass  # print("on_attention not implemented %f" % attention)

    def on_error(self, error):
        pass  # print("on_error not implemented: %i" % error.code)

    def on_connectivity_change(self, connectivity):
        # print("on_connection_change not implemented: %s" % connection_state.name)
        pass

    def on_contact_state_change(self, contact_state):
        # print("on_contact_state_change not implemented: %s" % contact_state.name)
        pass

    def on_orientation_change(self, orientation):
        # print("on_orientation_change not implemented: %s" % orientation.name)
        pass

    def on_meditation(self, meditation):
        pass  # print("on_meditation not implemented")

    # Experimental features
    def on_social_engagement(self, engagement):
        pass  # print("on_social_engagement not implemented %f" % engagement)

    def on_blink(self):
        pass  # print("on_blink not implemented")


def fatal_error(msg):
    print("FATAL_ERROR:" + msg)
    sys.exit(1)

class LogLevel(IntEnum):
    debug = 0
    info = 1
    warning = 2
    error = 3
    none = 4

class ContactState(IntEnum):
    unknown = 0
    contact = 1
    no_contact = 2


class Orientation(IntEnum):
    unknown = 0
    upward = 1
    downward = 2


class Connectivity(IntEnum):
    connecting = 0
    connected = 1
    disconnecting = 2
    disconnected = 3


class AFEDataSampleRate(IntEnum):
    sr125 = 0
    sr250 = 1
    sr500 = 2
    sr1000 = 3


class AFEDataChannel(IntEnum):
    none = 0
    ch1 = 1
    ch2 = 2
    both = 3


class AFEDataLeadOffOption(IntEnum):
    disabled = 0
    ac = 1
    dc_6na = 2
    dc_22na = 3
    dc_6ua = 4
    dc_22ua = 5


class AFEDataSignalType(IntEnum):
    eeg = 0
    lead_off_detection = 1


class IMUDataSampleRate(IntEnum):
    off = 0
    sr12_5 = 0x10
    sr26 = 0x20
    sr52 = 0x30
    sr104 = 0x40
    sr208 = 0x50
    sr416 = 0x60
    sr833 = 0x70


class CMSNCommand(IntEnum):
    afe_config = -1
    imu_config = -2
    unused = 0
    pair = 1
    check_pairing_status = 2
    start_data_stream = 3
    stop_data_stream = 4
    shutdown = 5
    enter_ota = 6
    enter_factory_mode = 7
    restore_factory_settings = 8
    set_led_color = 9
    set_device_name = 10
    set_sleep_idle_time = 11
    set_vibration_intensity = 12
    get_system_info = 13
    get_lead_off_status = 14


class AFEConfigError(IntEnum):
    none = 0
    unknown = 1
    afe_config_error = 2


class AFEConfigResponse:
    error = AFEConfigError.none

    def __init__(self, error):
        self.error = error

    def success(self):
        return self.error == AFEConfigError.none


class IMUConfigError(IntEnum):
    none = 0
    unknown = 1
    acc_config_error = 2
    gyro_config_error = 3


class IMUConfigResponse:
    error = IMUConfigError.none

    def __init__(self, error):
        self.error = error

    def success(self):
        return self.error == IMUConfigError.none


class SysConfigError(IntEnum):
    none = 0
    unknown = 1
    ota_failed_low_power = 2
    # Pairing related errors
    pair_error = 3
    validate_pair_info = 4
    internal_storage_error = 5


class SysConfigResponse:
    command = CMSNCommand.unused
    error = SysConfigError.none

    def __init__(self, command, error):
        self.command = command
        self.error = error

    def success(self):
        return self.error == SysConfigError.none


class HardwareError(IntEnum):
    none = 0
    unknown = 1
    eeg_err = 2
    imu_err = 3
    mag_err = 4
    abnormal_battery_voltage = 5


class CMSNErrorCode(IntEnum):
    none = 0
    unknown = -1
    invalid_params = -2
    invalid_data = -3
    bleDeviceUnreachable = -128
    bleDisabled = -129
    bleUnavailable = -130
    bleDataWriteFailure = -131
    device_not_connected = -160
    device_uuid_unavailable = -196


# Wrapper objects
class CMSNError:
    code = None
    message = None

    def __init__(self, code):
        self.code = code
        c_msg = libcmsn.cmsn_err_code_to_msg(code)
        self.message = ffi.string(c_msg).decode("utf-8")


class DeviceInfo:
    manufacturer_name = None
    model_number = None
    serial_number = None
    hardware_revision = None
    firmware_revision = None

    def __init__(self, c_info):
        self.manufacturer_name = ffi.string(c_info.manufacturer, 16).decode("utf-8")
        self.model_number = ffi.string(c_info.model, 16).decode("utf-8")
        self.serial_number = ffi.string(c_info.serial, 17).decode("utf-8")
        self.hardware_revision = ffi.string(c_info.hardware, 16).decode("utf-8")
        self.firmware_revision = ffi.string(c_info.firmware, 16).decode("utf-8")


class EEGData:
    sequence_num = None
    sample_rate = None
    eeg_data = None

    def __init__(self, c_data):
        self.sequence_num = c_data.sequence_num
        self.sample_rate = c_data.sample_rate
        self.eeg_data = ffi.unpack(c_data.eeg_data, c_data.eeg_size)
        self.signal_type = AFEDataSignalType(c_data.signal_type)


class ACCData:
    sequence_num = None
    x = None
    y = None
    z = None

    def __init__(self, c_data):
        self.sequence_num = c_data.sequence_num
        points = ffi.unpack(c_data.data, c_data.size)
        self.x = [0.0] * c_data.size
        self.y = [0.0] * c_data.size
        self.z = [0.0] * c_data.size
        for i in range(0, c_data.size):
            self.x[i] = points[i].x
            self.y[i] = points[i].y
            self.z[i] = points[i].z


class GyroData:
    sequence_num = None
    x = None
    y = None
    z = None

    def __init__(self, c_data):
        self.sequence_num = c_data.sequence_num
        points = ffi.unpack(c_data.data, c_data.size)

        self.x = [0.0] * c_data.size
        self.y = [0.0] * c_data.size
        self.z = [0.0] * c_data.size
        for i in range(0, c_data.size):
            self.x[i] = points[i].x
            self.y[i] = points[i].y
            self.z[i] = points[i].z


class EulerAngleData:
    yaw = None
    pitch = None
    roll = None

    def __init__(self, c_data):
        self.yaw = ffi.unpack(c_data.yaw, c_data.size)
        self.pitch = ffi.unpack(c_data.pitch, c_data.size)
        self.roll = ffi.unpack(c_data.roll, c_data.size)


class IMUData:
    acc_data = None
    gyro_data = None
    euler_angle_data = None
    sample_rate = None

    def __init__(self, c_data):
        self.sample_rate = c_data.sample_rate
        self.acc_data = ACCData(c_data.acc_data)
        self.gyrp_data = GyroData(c_data.gyro_data)
        self.euler_angle_data = EulerAngleData(c_data.euler_angle_data)


class SysInfoData:
    firmware_info = None
    hardware_errors = None

    def __init__(self, firmware_info, hardware_errs):
        self.firmware_info = firmware_info
        self.hardware_errors = hardware_errs


class BrainWave:
    delta = 0
    theta = 0
    alpha = 0
    low_beta = 0
    high_beta = 0
    gamma = 0

    def __init__(self, c_stats):
        self.delta = c_stats.delta
        self.theta = c_stats.theta
        self.alpha = c_stats.alpha
        self.low_beta = c_stats.low_beta
        self.high_beta = c_stats.high_beta
        self.gamma = c_stats.gamma


class CMSNDevice(CMSNDeviceListener):

    _device_pointer_map = {}
    _device_map = {}
    _config_response_callbacks = {}
    _sys_info_cb = None
    _lead_off_status_cb = None

    __address = 0
    __uuid = None
    __name = None
    __broadcast_battery_level = 0
    rssi = 0.0
    __is_in_pairing_mode = False

    __listener = None

    def __init__(self, uuid, name, address, broadcast_battery_level):
        self.__uuid = uuid
        self.__name = name
        self.__address = address
        self.__broadcast_battery_level = broadcast_battery_level

    @property
    def uuid(self):
        return self.__uuid

    @property
    def name(self):
        return self.__name

    @property
    def connectivity(self):
        if self.__uuid in CMSNDevice._device_pointer_map:
            return Connectivity(libcmsn.cmsn_get_ble_connectivity(CMSNDevice._device_pointer_map[self.__uuid]))
        return Connectivity.disconnected

    @property
    def contact_state(self):
        if self.__uuid in CMSNDevice._device_pointer_map:
            return ContactState(libcmsn.cmsn_get_contact_state(CMSNDevice._device_pointer_map[self.__uuid]))
        return ContactState.unknown

    @property
    def battery_level(self):
        if self.__uuid in CMSNDevice._device_pointer_map:
            return libcmsn.cmsn_get_battery_level(CMSNDevice._device_pointer_map[self.__uuid])
        return self.__broadcast_battery_level

    @property
    def hardware_revision(self):
        if self.__uuid in CMSNDevice._device_pointer_map:
            hardware_rev = libcmsn.cmsn_get_hardware_revision(CMSNDevice._device_pointer_map[self.__uuid])
            return ffi.string(hardware_rev, 64).decode("utf-8")
        print("Never connected to the device; hardware revision is not available")
        return None

    @property
    def firmware_revision(self):
        if self.__uuid in CMSNDevice._device_pointer_map:
            firmware_rev = libcmsn.cmsn_get_firmware_revision(CMSNDevice._device_pointer_map[self.__uuid])
            return ffi.string(firmware_rev, 64).decode("utf-8")
        print("Never connected to the device; firmware revision is not available")
        return None

    @property
    def is_in_pairing_mode(self):
        return self.__is_in_pairing_mode

    def __pair(self, cb):
        if self.__uuid in CMSNDevice._device_pointer_map:
            res = libcmsn.cmsn_pair(CMSNDevice._device_pointer_map[self.__uuid], CMSNDevice.__on_sys_config_response_internal)
            if res > 0:  # res is now msg_id
                CMSNDevice._config_response_callbacks[res] = cb
                return CMSNError(CMSNErrorCode.none)
            else:
                return CMSNError(res)
        else:
            fatal_error("Calling pair before connecting to device")

    def __check_pairing_status(self, cb):
        if self.__uuid in CMSNDevice._device_pointer_map:
            res = libcmsn.cmsn_check_pairing_status(CMSNDevice._device_pointer_map[self.__uuid], CMSNDevice.__on_sys_config_response_internal)
            if res > 0:  # res is now msg_id
                CMSNDevice._config_response_callbacks[res] = cb
                return CMSNError(CMSNErrorCode.none)
            else:
                return CMSNError(res)
        else:
            fatal_error("Calling pair before connecting to device")

    def pair(self, cb):
        if self.is_in_pairing_mode:
            self.__pair(cb)
        else:
            self.__check_pairing_status(cb)

    # Default is working mode
    # const dataChannel = AFE.CHANNEL.enum(ImpedanceMode ? 'both' : 'ch1');
    # const leadOffOption = AFE.LEAD_OFF_OPTION.enum(ImpedanceMode ? 'ac' : 'dc_6na')
    # const leadOffChannel = AFE.CHANNEL.enum(ImpedanceMode ? 'both' : 'ch2');
    def config_afe(self, sample_rate=AFEDataSampleRate.sr250, data_channel=AFEDataChannel.ch1, lead_off_option=AFEDataLeadOffOption.dc_6na, lead_off_channel=AFEDataChannel.ch2, rld_channel=AFEDataChannel.both, cb=None):
        if self.__uuid in CMSNDevice._device_pointer_map:
            res = libcmsn.cmsn_config_afe(CMSNDevice._device_pointer_map[self.__uuid], sample_rate.value, data_channel.value, lead_off_option.value, lead_off_channel.value, rld_channel.value,
                                          CMSNDevice.__on_afe_config_response_internal)
            if res > 0:  
                # res is now msg_id
                if cb is not None:  
                    CMSNDevice._config_response_callbacks[res] = cb
                return CMSNError(CMSNErrorCode.none)
            else:
                return CMSNError(res)
        else:
            fatal_error("Calling config_afe before connecting to device")

    def start_eeg_stream(self, cb=None):
        if self.__uuid in CMSNDevice._device_pointer_map:
            res = libcmsn.cmsn_start_eeg_stream(CMSNDevice._device_pointer_map[self.__uuid], CMSNDevice.__on_sys_config_response_internal)
            if res > 0:  # res is now msg_id
                if cb is not None:
                    CMSNDevice._config_response_callbacks[res] = cb
                return CMSNError(CMSNErrorCode.none)
            else:
                return CMSNError(res)
        else:
            fatal_error("Calling start_eeg_stream before connecting to device")

    def stop_eeg_stream(self, cb=None):
        if self.__uuid in CMSNDevice._device_pointer_map:
            res = libcmsn.cmsn_stop_eeg_stream(CMSNDevice._device_pointer_map[self.__uuid], CMSNDevice.__on_sys_config_response_internal)
            if res > 0:  # res is now msg_id
                if cb is not None:
                    CMSNDevice._config_response_callbacks[res] = cb
                return CMSNError(CMSNErrorCode.none)
            else:
                return CMSNError(res)
        else:
            fatal_error("Calling stop_data_stream before connecting to device")

    def start_imu_stream(self, sample_rate=IMUDataSampleRate.sr12_5, cb=None):
        if self.__uuid in CMSNDevice._device_pointer_map:
            print("Starting IMU stream with sample rate:" + str(sample_rate.value))
            res = libcmsn.cmsn_start_imu_stream(CMSNDevice._device_pointer_map[self.__uuid], sample_rate.value, CMSNDevice.__on_imu_config_response_internal)
            if res > 0:  # res is now msg_id
                if cb is not None:
                    CMSNDevice._config_response_callbacks[res] = cb
                return CMSNError(CMSNErrorCode.none)
            else:
                return CMSNError(res)
        else:
            fatal_error("Calling start_imu_stream before connecting to device")

    def stop_imu_stream(self, cb=None):
        if self.__uuid in CMSNDevice._device_pointer_map:
            print("Stop IMU stream")
            res = libcmsn.cmsn_stop_imu_stream(CMSNDevice._device_pointer_map[self.__uuid], CMSNDevice.__on_imu_config_response_internal)
            if res > 0:  # res is now msg_id
                if cb is not None:
                    CMSNDevice._config_response_callbacks[res] = cb
                return CMSNError(CMSNErrorCode.none)
            else:
                return CMSNError(res)
        else:
            fatal_error("Calling stop_imu_stream before connecting to device")

    def set_device_name(self, name, cb=None):
        if isinstance(name, str) and len(name) > 3:
            if self.__uuid in CMSNDevice._device_pointer_map:
                c_name = ffi.new("char[]", name.encode('utf-8'))
                res = libcmsn.cmsn_set_device_name(CMSNDevice._device_pointer_map[self.__uuid], c_name, CMSNDevice.__on_sys_config_response_internal)
                if res > 0:  # res is now msg_id
                    if cb is not None:
                        CMSNDevice._config_response_callbacks[res] = cb
                    return CMSNError(CMSNErrorCode.none)
                else:
                    return CMSNError(res)
            else:
                fatal_error("Calling set_device_name before connecting to device")
        else:
            fatal_error("Input name has to be an string with more than 3 characters")

    # Example: device.set_forehead_led_color((255,255,255))
    def set_led_color(self, rgb_color, cb=None):
        if len(rgb_color) != 3:
            fatal_error("Invalid color input, length is not 3")
            return
        if isinstance(rgb_color[0], int) and isinstance(rgb_color[1], int) and isinstance(rgb_color[2], int):
            if self.__uuid in CMSNDevice._device_pointer_map:
                res = libcmsn.cmsn_set_led_color(CMSNDevice._device_pointer_map[self.__uuid], rgb_color[0], rgb_color[1], rgb_color[2], CMSNDevice.__on_sys_config_response_internal)
                if res > 0:  # res is now msg_id
                    if cb is not None:
                        CMSNDevice._config_response_callbacks[res] = cb
                    return CMSNError(CMSNErrorCode.none)
                else:
                    return CMSNError(res)
            else:
                fatal_error("Calling set_forehead_led_color before connecting to device")
        else:
            fatal_error("Input color values must be integer from [0,255]")

    def set_vibration_intensity(self, intensity, cb=None):  # intensity
        if intensity < 0 or intensity > 100:
            fatal_error("Invalid intensity input, intensity should be a int value with in (0-100)")
        if self.__uuid in CMSNDevice._device_pointer_map:
            res = libcmsn.cmsn_set_vibration_intensity(CMSNDevice._device_pointer_map[self.__uuid], int(intensity), CMSNDevice.__on_sys_config_response_internal)
            if res > 0:  # res is now msg_id
                if cb is not None:
                    CMSNDevice._config_response_callbacks[res] = cb
                return CMSNError(CMSNErrorCode.none)
            else:
                return CMSNError(res)
        else:
            fatal_error("Calling set_vibration_intensity before connecting to device")

    def set_sleep_idle_time(self, secs, cb=None):  # intensity
        if secs < 0 or secs > 1000:
            fatal_error("Invalid idle time input, idle time should be a int value with in (0-1000)")
        if self.__uuid in CMSNDevice._device_pointer_map:
            res = libcmsn.cmsn_set_sleep_idle_time(CMSNDevice._device_pointer_map[self.__uuid], int(secs), CMSNDevice.__on_sys_config_response_internal)
            if res > 0:  # res is now msg_id
                if cb is not None:
                    CMSNDevice._config_response_callbacks[res] = cb
                return CMSNError(CMSNErrorCode.none)
            else:
                return CMSNError(res)
        else:
            fatal_error("Calling set_sleep_idle_time before connecting to device")

    def shutdown(self, cb=None):
        if self.__uuid in CMSNDevice._device_pointer_map:
            res = libcmsn.cmsn_device_shutdown(CMSNDevice._device_pointer_map[self.__uuid], CMSNDevice.__on_sys_config_response_internal)
            if res > 0:  # res is now msg_id
                if cb is not None:
                    CMSNDevice._config_response_callbacks[res] = cb
                return CMSNError(CMSNErrorCode.none)
            else:
                return CMSNError(res)
        else:
            fatal_error("Calling shutdown before connecting to device")

    def enter_ota(self, cb=None):
        if self.__uuid in CMSNDevice._device_pointer_map:
            res = libcmsn.cmsn_device_enter_ota(CMSNDevice._device_pointer_map[self.__uuid], CMSNDevice.__on_sys_config_response_internal)
            if res > 0:  # res is now msg_id
                if cb is not None:
                    CMSNDevice._config_response_callbacks[res] = cb
                return CMSNError(CMSNErrorCode.none)
            else:
                return CMSNError(res)
        else:
            fatal_error("Calling enter_ota before connecting to device")

    def get_sys_info(self, sys_info_cb, cb=None):
        if self.__uuid in CMSNDevice._device_pointer_map:
            self._sys_info_cb = sys_info_cb
            res = libcmsn.cmsn_get_sys_info(CMSNDevice._device_pointer_map[self.__uuid], CMSNDevice.__on_sys_info_internal, CMSNDevice.__on_sys_config_response_internal)
            if res > 0:  # res is now msg_id
                if cb is not None:
                    CMSNDevice._config_response_callbacks[res] = cb
                return CMSNError(CMSNErrorCode.none)
            else:
                return CMSNError(res)
        else:
            fatal_error("Calling get_sys_info before connecting to device")

    def get_lead_off_status(self, lead_off_status_cb, cb=None):
        if self.__uuid in CMSNDevice._device_pointer_map:
            self._lead_off_status_cb = lead_off_status_cb
            res = libcmsn.cmsn_get_lead_off_status(CMSNDevice._device_pointer_map[self.__uuid], CMSNDevice.__on_lead_off_status_internal, CMSNDevice.__on_sys_config_response_internal)
            if res > 0:  # res is now msg_id
                if cb is not None:
                    CMSNDevice._config_response_callbacks[res] = cb
                return CMSNError(CMSNErrorCode.none)
            else:
                return CMSNError(res)
        else:
            fatal_error("Calling get_lead_off_status_info before connecting to device")

    def set_listener(self, listener):
        if isinstance(listener, CMSNDeviceListener):
            self.__listener = listener
            if self.__uuid in CMSNDevice._device_pointer_map:
                device_ptr = CMSNDevice._device_pointer_map[self.__uuid]
                libcmsn.cmsn_set_signal_quality_warning_callback(device_ptr, CMSNDevice.__on_signal_quality_warning_internal)

                if listener is not None:
                    libcmsn.cmsn_set_error_callback(device_ptr, CMSNDevice.__on_error_internal)
                    libcmsn.cmsn_set_connectivity_change_callback(device_ptr, CMSNDevice.__on_connectivity_change_internal)
                    libcmsn.cmsn_set_device_info_callback(device_ptr, CMSNDevice.__on_device_info_internal)
                    libcmsn.cmsn_set_contact_state_change_callback(device_ptr, CMSNDevice.__on_contact_state_change_internal)
                    libcmsn.cmsn_set_orientation_change_callback(device_ptr, CMSNDevice.__on_orientation_change_internal)

                    libcmsn.cmsn_set_raw_eeg_data_callback(device_ptr, CMSNDevice.__on_raw_eeg_data_internal)
                    libcmsn.cmsn_set_eeg_data_callback(device_ptr, CMSNDevice.__on_eeg_data_internal)
                    libcmsn.cmsn_set_eeg_stats_callback(device_ptr, CMSNDevice.__on_eeg_stats_internal)
                    libcmsn.cmsn_set_imu_data_callback(device_ptr, CMSNDevice.__on_imu_data_internal)
                    libcmsn.cmsn_set_blink_callback(device_ptr, CMSNDevice.__on_blink_internal)
                    libcmsn.cmsn_set_attention_callback(device_ptr, CMSNDevice.__on_attention_internal)
                    libcmsn.cmsn_set_meditation_callback(device_ptr, CMSNDevice.__on_meditation_internal)
                    if _ENABLE_SOCIAL_ENGAGEMENT:
                        libcmsn.cmsn_set_social_engagement_callback(device_ptr, CMSNDevice.__on_social_engagement_internal)
                    
                else:
                    libcmsn.cmsn_set_error_callback(device_ptr, ffi.NULL)
                    libcmsn.cmsn_set_connectivity_change_callback(device_ptr, ffi.NULL)
                    libcmsn.cmsn_set_device_info_callback(device_ptr, ffi.NULL)
                    libcmsn.cmsn_set_contact_state_change_callback(device_ptr, ffi.NULL)
                    libcmsn.cmsn_set_orientation_change_callback(device_ptr, ffi.NULL)
                    
                    libcmsn.cmsn_set_raw_eeg_data_callback(device_ptr, ffi.NULL)
                    libcmsn.cmsn_set_eeg_data_callback(device_ptr, ffi.NULL)
                    libcmsn.cmsn_set_eeg_stats_callback(device_ptr, ffi.NULL)
                    libcmsn.cmsn_set_imu_data_callback(device_ptr, ffi.NULL)
                    libcmsn.cmsn_set_blink_callback(device_ptr, ffi.NULL)
                    libcmsn.cmsn_set_attention_callback(device_ptr, ffi.NULL)
                    libcmsn.cmsn_set_meditation_callback(device_ptr, ffi.NULL)
                    libcmsn.cmsn_set_social_engagement_callback(device_ptr, ffi.NULL)
        else:
            fatal_error("Listener does not conform to CMSNDeviceListener interface")

    def __get_c_ble_info(self):
        uuid_fld = ffi.new("char[40]", self.__uuid.encode('utf-8'))
        name_fld = ffi.new("char[40]", self.__name.encode('utf-8'))
        c_info = ffi.new("CMSNBLEInfo *", (uuid_fld, name_fld, float(self.rssi), self.__address, self.__is_in_pairing_mode, chr(self.__broadcast_battery_level).encode()))
        return c_info[0]

    def connect(self):
        libcmsn.cmsn_stop_scan_ble_devices()

        if self.connectivity == Connectivity.disconnected:
            print("CMSNDevice:connecting...")
            device_ptr = libcmsn.cmsn_connect_ble(self.__get_c_ble_info())
            if device_ptr is not ffi.NULL:
                CMSNDevice._device_pointer_map[self.__uuid] = device_ptr
        # Make sure listeners are set to the C core
        if self.__listener is not None:
            self.set_listener(self.__listener)

    def disconnect(self):
        if self.connectivity is not Connectivity.disconnected or self.connectivity is not Connectivity.disconnecting:
            print("CMSNDevice:disconnecting...")
            if self.__uuid in self._device_pointer_map:
                device_ptr = CMSNDevice._device_pointer_map[self.__uuid]
                libcmsn.cmsn_disconnect_ble(device_ptr)
            else:
                fatal_error("CMSNDevice: Device map already cleared this device")

        else:
            print("CMSNDevice:Device is already disconnected...")

    @classmethod
    def create_cmsn_device_with_c_ble_info(cls, c_device_ble_info):
        uuid = ffi.string(c_device_ble_info.uuid, 40).decode("utf-8")
        name = ffi.string(c_device_ble_info.name, 16).decode("utf-8")
        rssi = c_device_ble_info.rssi
        address = c_device_ble_info.address
        is_in_pairing_mode = c_device_ble_info.is_in_pairing_mode
        broadcast_battery_level = c_device_ble_info.battery_level[0]
        return cls.create_cmsn_device(address, uuid, name, rssi, is_in_pairing_mode, broadcast_battery_level)

    @classmethod
    def create_cmsn_device(cls, address, uuid, name, rssi, is_in_pairing_mode, broadcast_battery_level):
        if uuid in cls._device_map:
            device = cls._device_map.get(uuid)
            device.__name = name
            device.__is_in_pairing_mode = is_in_pairing_mode
            device.__broadcast_battery_level = broadcast_battery_level
            device.__rssi = rssi
            if device.connectivity == Connectivity.connected or device.connectivity == Connectivity.connecting:
                device.connect()
            return device
        device = CMSNDevice(uuid, name, address, broadcast_battery_level)
        device.__rssi = rssi
        device.__is_in_pairing_mode = is_in_pairing_mode
        cls._device_map[uuid] = device
        return device

    # Callback internal methods implementation
    @staticmethod
    @ffi.callback("void(char*, unsigned int, ConfigResp*)")
    def __on_afe_config_response_internal(uuid_ptr, msg_id, c_resp):
        uuid = ffi.string(uuid_ptr, 40).decode("utf-8")
        if msg_id in CMSNDevice._config_response_callbacks:
            if uuid in CMSNDevice._device_map:
                device = CMSNDevice._device_map[uuid]
                err = AFEConfigError.none
                if c_resp.n_errors > 0:
                    err = AFEConfigError(ffi.unpack(c_resp.errors, c_resp.n_errors)[0])

                cb = CMSNDevice._config_response_callbacks[msg_id]
                if cb is not None:
                    cb(device, AFEConfigResponse(err))
                del CMSNDevice._config_response_callbacks[msg_id]

    @staticmethod
    @ffi.callback("void(char*, unsigned int, ConfigResp*)")
    def __on_imu_config_response_internal(uuid_ptr, msg_id, c_resp):
        uuid = ffi.string(uuid_ptr, 40).decode("utf-8")
        if msg_id in CMSNDevice._config_response_callbacks:
            if uuid in CMSNDevice._device_map:
                device = CMSNDevice._device_map[uuid]
                err = IMUConfigError.none
                if c_resp.n_errors > 0:
                    err = IMUConfigError(ffi.unpack(c_resp.errors, c_resp.n_errors)[0])

                cb = CMSNDevice._config_response_callbacks[msg_id]
                if cb is not None:
                    cb(device, IMUConfigResponse(err))
                del CMSNDevice._config_response_callbacks[msg_id]

    @staticmethod
    @ffi.callback("void(char*, unsigned int, ConfigResp*)")
    def __on_sys_config_response_internal(uuid_ptr, msg_id, c_resp):
        uuid = ffi.string(uuid_ptr, 40).decode("utf-8")
        if msg_id in CMSNDevice._config_response_callbacks:
            if uuid in CMSNDevice._device_map:
                device = CMSNDevice._device_map[uuid]
                cmd = ffi.unpack(c_resp.cmds, c_resp.n_errors)[0]
                err = ffi.unpack(c_resp.errors, c_resp.n_errors)[0]
                cb = CMSNDevice._config_response_callbacks[msg_id]
                if cb is not None:
                    cb(device, SysConfigResponse(CMSNCommand(cmd), SysConfigError(err)))

                del CMSNDevice._config_response_callbacks[msg_id]

    @staticmethod
    @ffi.callback("void(char*, unsigned int, SysInfoData*)")
    def __on_sys_info_internal(uuid_ptr, msg_id, c_data):
        uuid = ffi.string(uuid_ptr, 40).decode("utf-8")
        if uuid in CMSNDevice._device_map:
            device = CMSNDevice._device_map[uuid]
            if device._sys_info_cb is not None:
                firmware_info = ffi.string(c_data.firmware_info).decode("utf-8")  # TODO: Validate firmware info is properly unpacked
                c_errors = ffi.unpack(c_data.hardware_errors, c_data.n_errors)
                hardware_errors = []
                for err in c_errors:
                    hardware_errors.append(HardwareError(err))
                device._sys_info_cb(device, SysInfoData(firmware_info, hardware_errors))
                device._sys_info_cb = None

    @staticmethod
    @ffi.callback("void(char*, unsigned int, DeviceContactState, DeviceContactState)")
    def __on_lead_off_status_internal(uuid_ptr, msg_id, center_rld, side_channels):
        uuid = ffi.string(uuid_ptr, 40).decode("utf-8")
        if uuid in CMSNDevice._device_map:
            device = CMSNDevice._device_map[uuid]
            center_rld_state = ContactState(center_rld)
            side_channels_state = ContactState(side_channels)
            print("Lead off status:center:" + center_rld_state.name + ",sides:" + side_channels_state.name)
            if device._lead_off_status_cb is not None:
                device._lead_off_status_cb(device, center_rld_state, side_channels_state)
                device._lead_off_status_cb = None

    @staticmethod
    @ffi.callback("void(char*, int)")
    def __on_signal_quality_warning_internal(uuid_ptr, signal_quality):
        print("Signal quality warning:%i, starting lead off detection" % signal_quality)
        # uuid = ffi.string(uuid_ptr, 40).decode("utf-8")
        # if uuid in CMSNDevice._device_map:
        #     device = CMSNDevice._device_map[uuid]
        #     device.get_lead_off_status(None, None)
        # else:
        #     fatal_error("__on_connection_change_internal:device unavailable for:" + uuid)

    @staticmethod
    @ffi.callback("void(char*, BLEConnectivity)")
    def __on_connectivity_change_internal(uuid_ptr, connecvitity):
        uuid = ffi.string(uuid_ptr, 40).decode("utf-8")
        if uuid in CMSNDevice._device_map:
            device = CMSNDevice._device_map[uuid]
            connecvitity_enum = Connectivity(connecvitity)
            if device.__listener is not None:
                device.__listener.on_connectivity_change(connecvitity_enum)
            if connecvitity_enum == Connectivity.disconnected:
                if device.__uuid in CMSNDevice._device_pointer_map:
                    del CMSNDevice._device_pointer_map[device.__uuid]
        else:
            fatal_error("__on_connection_change_internal:device unavailable for:" + uuid)

    @staticmethod
    @ffi.callback("void(char*, EEGData*)")
    def __on_raw_eeg_data_internal(uuid_ptr, eeg_data_ptr):
        uuid = ffi.string(uuid_ptr, 40).decode("utf-8")
        if uuid in CMSNDevice._device_map:
            device = CMSNDevice._device_map[uuid]
            if device.__listener is not None:
                device.__listener.on_raw_eeg_data(EEGData(eeg_data_ptr[0]))
        else:
            fatal_error("__on_raw_eeg_data_internal:device unavailable for:" + uuid)

    @staticmethod
    @ffi.callback("void(char*, EEGData*)")     
    def __on_eeg_data_internal(uuid_ptr, eeg_data_ptr):
        uuid = ffi.string(uuid_ptr, 40).decode("utf-8")
        if uuid in CMSNDevice._device_map:
            device = CMSNDevice._device_map[uuid]
            if device.__listener is not None:
                device.__listener.on_eeg_data(EEGData(eeg_data_ptr[0]))
        else:
            fatal_error("__on_eeg_data_internal:device unavailable for:" + uuid)

    @staticmethod
    @ffi.callback("void(char*, IMUData*)")
    def __on_imu_data_internal(uuid_ptr, imu_data_ptr):
        uuid = ffi.string(uuid_ptr, 40).decode("utf-8")
        if uuid in CMSNDevice._device_map:
            device = CMSNDevice._device_map[uuid]
            if device.__listener is not None:
                device.__listener.on_imu_data(IMUData(imu_data_ptr[0]))
        else:
            fatal_error("__on_imu_data_internal:device unavailable for:" + uuid)

    @staticmethod
    @ffi.callback("void(char*, float)")
    def __on_attention_internal(uuid_ptr, attention):
        uuid = ffi.string(uuid_ptr, 40).decode("utf-8")
        if uuid in CMSNDevice._device_map:
            device = CMSNDevice._device_map[uuid]
            if device.__listener is not None:
                device.__listener.on_attention(attention)
        else:
            fatal_error("__attention_internal:device unavailable for:" + uuid)

    @staticmethod
    @ffi.callback("void(char*, float)")
    def __on_social_engagement_internal(uuid_ptr, social):
        uuid = ffi.string(uuid_ptr, 40).decode("utf-8")
        if uuid in CMSNDevice._device_map:
            device = CMSNDevice._device_map[uuid]
            if device.__listener is not None:
                device.__listener.on_social_engagement(social)
        else:
            fatal_error("__on_social_engagement_internal:device unavailable for:" + uuid)

    @staticmethod
    @ffi.callback("void(char*, float)")
    def __on_meditation_internal(uuid_ptr, meditation):
        uuid = ffi.string(uuid_ptr, 40).decode("utf-8")
        if uuid in CMSNDevice._device_map:
            device = CMSNDevice._device_map[uuid]
            if device.__listener is not None:
                device.__listener.on_meditation(meditation)
        else:
            fatal_error("__meditation_internal:device unavailable for:" + uuid)

    @staticmethod
    @ffi.callback("void(char*, EEGStats*)")
    def __on_eeg_stats_internal(uuid_ptr, eeg_stats_ptr):
        uuid = ffi.string(uuid_ptr, 40).decode("utf-8")
        if uuid in CMSNDevice._device_map:
            device = CMSNDevice._device_map[uuid]
            if device.__listener is not None:
                device.__listener.on_brain_wave(BrainWave(eeg_stats_ptr[0]))
        else:
            fatal_error("__eeg_stats_internal:device unavailable for:" + uuid)

    @staticmethod
    @ffi.callback("void(char*, int)")
    def __on_error_internal(uuid_ptr, error_code):
        uuid = ffi.string(uuid_ptr, 40).decode("utf-8")
        if uuid in CMSNDevice._device_map:
            device = CMSNDevice._device_map[uuid]
            if device.__listener is not None:
                device.__listener.on_error(CMSNError(error_code))
        else:
            fatal_error("__on_error_internal:device unavailable for:" + uuid)

    @staticmethod
    @ffi.callback("void(char*, DeviceContactState)")
    def __on_contact_state_change_internal(uuid_ptr, contact_state):
        uuid = ffi.string(uuid_ptr, 40).decode("utf-8")
        if uuid in CMSNDevice._device_map:
            device = CMSNDevice._device_map[uuid]
            if device.__listener is not None:
                device.__listener.on_contact_state_change(ContactState(contact_state))
        else:
            fatal_error("__on_contact_state_change_internal:device unavailable for:" + uuid)

    @staticmethod
    @ffi.callback("void(char*, DeviceOrientation)")
    def __on_orientation_change_internal(uuid_ptr, orientation):
        uuid = ffi.string(uuid_ptr, 40).decode("utf-8")
        if uuid in CMSNDevice._device_map:
            device = CMSNDevice._device_map[uuid]
            if device.__listener is not None:
                device.__listener.on_orientation_change(Orientation(orientation))
        else:
            fatal_error("__on_orientation_change_internal:device unavailable for:" + uuid)

    @staticmethod
    @ffi.callback("void(char*)")
    def __on_blink_internal(uuid_ptr):
        uuid = ffi.string(uuid_ptr, 40).decode("utf-8")
        if uuid in CMSNDevice._device_map:
            device = CMSNDevice._device_map[uuid]
            if device.__listener is not None:
                device.__listener.on_blink()
        else:
            fatal_error("__on_blink_internal:device unavailable for:" + uuid_ptr)

    @staticmethod
    @ffi.callback("void(char*, CMSNDeviceInfo*)")
    def __on_device_info_internal(uuid_ptr, c_info):
        uuid = ffi.string(uuid_ptr, 40).decode("utf-8")
        if uuid in CMSNDevice._device_map:
            device = CMSNDevice._device_map[uuid]
            if device.__listener is not None:
                device.__listener.on_device_info_ready(DeviceInfo(c_info))
        else:
            fatal_error("__on_device_info_ready_internal:device unavailable for:" + uuid_ptr)


class CMSNSDK:

    _on_found_device = None
    _on_scan_error = None

    @staticmethod
    def dispose():
        ffi.dlclose(libcmsn)
        # os.kill(os.getpid(), signal.SIGKILL)

    @staticmethod
    @ffi.callback("void(CMSNBLEInfo*)")
    def _on_found_device_internal(device):
        if CMSNSDK._on_found_device is not None:
            if device is not None:
                CMSNSDK._on_found_device(CMSNDevice.create_cmsn_device_with_c_ble_info(device))
            else:
                fatal_error("Devide found but is None")

    @classmethod
    def start_device_scan(cls, on_finish):
        cls._on_found_device = on_finish
        # cls._on_search_error = on_error
        print("crimson_sdk.py:start_device_scan:scanning ...")
        libcmsn.cmsn_scan_ble_devices(CMSNSDK._on_found_device_internal)

    @classmethod
    def stop_device_scan(cls):
        print("crimson_sdk.py:stop_device_scan:stop")
        cls._on_found_device = None
        libcmsn.cmsn_stop_scan_ble_devices()

    @classmethod
    def create_sdk_filter(cls):
        return libcmsn.dev_create_sdk_filter()

    @classmethod
    def filter(cls, sdk_filter, signal):
        return libcmsn.dev_filter(sdk_filter, signal)
    
    @classmethod
    def dev_analyze_eeg(cls, device, eeg_data):
        libcmsn.dev_analyze_eeg(device, ffi.cast("float(*)", eeg_data.ctypes.data), len(eeg_data))

    @classmethod
    def dev_set_social_session(cls, mu_enabled):
        libcmsn.dev_set_social_session(mu_enabled)      

    # TEST Methods
    # @classmethod
    # def cmsn_create_device(cls, uuid):
    #     uuid_str = ffi.new("char[]", uuid.encode('utf-8'))
    #     return libcmsn.cmsn_create_device(uuid_str)

    # @classmethod
    # def did_receive_data(cls, device, data):
    #     res = libcmsn.cmsn_did_receive_data(device, ffi.from_buffer(bytes(data)), len(data))
    #     # print(f'did_receive_data, res:{res}')
