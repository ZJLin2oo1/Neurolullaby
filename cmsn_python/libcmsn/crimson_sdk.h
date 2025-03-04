#ifndef CRIMSON_SDK_H
#define CRIMSON_SDK_H

#ifdef __cplusplus
extern "C" {
#endif

#ifdef _WIN32
#ifdef BUILDING_CMSN_SHARED
#define SDK_EXTERN __declspec(dllexport)
#elif USING_CMSN_SHARED
#define SDK_EXTERN __declspec(dllimport)
#else
#define SDK_EXTERN
#endif
#else
#define SDK_EXTERN
#endif

#if __APPLE__
#include <TargetConditionals.h>
#endif

#include <stdbool.h>

//CFFI_DEF_START

// 1. CMSNDevice and related struct definitions
// ==============================================================================
typedef struct CMSNDevice CMSNDevice;

typedef enum {
    LOG_LEVEL_DEBUG = 0,
    LOG_LEVEL_INFO,
    LOG_LEVEL_WARNING,
    LOG_LEVEL_ERROR,
    LOG_LEVEL_NONE,
} LogLevel;

typedef enum {
    CONTACT_STATE_UNKNOWN = 0,
    CONTACT_STATE_CONTACT = 1,
    CONTACT_STATE_NO_CONTACT = 2
} DeviceContactState;

typedef enum {
    SIGNAL_TYPE_EEG = 0,
    SIGNAL_TYPE_LEAD_OFF_DETECTION = 1
} AFESignalType;

typedef struct {
    int sequence_num;
    float sample_rate;
    float* eeg_data;
    int eeg_size;
    AFESignalType signal_type;
    DeviceContactState side_channel_contact_state;
} EEGData;

typedef enum {
    ORIENTATION_UNKNOWN = 0,
    ORIENTATION_UPWARD = 1,
    ORIENTATION_DOWNWARD = 2 //UPSIDEDOWN
} DeviceOrientation;

typedef struct {
    float x;
    float y;
    float z;
} Point3D;

typedef struct {
    int     sequence_num;
    Point3D *  data;
    int     size;
} ACCData;

typedef struct {
    int     sequence_num;
    Point3D*  data;
    int     size;
} GyroData;

typedef struct {
    float*    yaw; // (-180 ~ 180) int value
    float*    pitch;
    float*    roll;
    int     size;
} EulerAngleData;

typedef struct {
    ACCData*           acc_data;
    GyroData*          gyro_data;
    EulerAngleData*    euler_angle_data;
    float              sample_rate;
} IMUData;

typedef struct {
    char* firmware_info;      // Firmware information
    int * hardware_errors;    // Hardware errors
    int   n_errors;    // Number of hardware errors
    int   sleep_idle_time_sec; //最小不能小于30秒 0表示不休眠
    int   vibration_intensity; //0~100
} SysInfoData;

typedef struct {
    int success;
    int* cmds;
    int* errors;
    int n_errors;
} ConfigResp;

typedef struct {
    double delta;
    double theta;
    double alpha;
    double low_beta;
    double high_beta;
    double gamma;
} EEGStats;

typedef enum {
    CMSN_ERROR_NONE = 0,
    CMSN_ERROR_UNKNOWN = -1,
    CMSN_ERROR_INVALID_PARAMS = -2,
    CMSN_ERROR_INVALID_DATA = -3,

    CMSN_ERROR_SYSTEM_IS_BUSY = -11,

    CMSN_ERROR_SCAN_FAILED = -64,                   //Android
    CMSN_ERROR_SCAN_FEATURE_UNSUPPORTED = -65,      //Android
    CMSN_ERROR_MAIN_SERVICE_UNSUPPORTED = -66,      //Android

    // BLE device error codes
    CMSN_ERROR_BLE_DEVICE_UNREACHABLE = -128,       //Android,Desktop (iOS)
    CMSN_ERROR_BLE_DISABLED = -129,                 //Android,Desktop (iOS)
    CMSN_ERROR_BLE_UNAVAILABLE = -130,              //Android,Desktop (iOS)

    CMSN_ERROR_BLE_DATA_WRITE_FAILURE = -131,       //Desktop

    CMSN_ERROR_DEVICE_NOT_CONNECTED = -160,         //Android,iOS     (Desktop)
    CMSN_ERROR_DEVICE_UUID_UNAVAILABLE = -196       //Android,iOS,Desktop

} CMSNError;

SDK_EXTERN unsigned int cmsn_gen_msg_id();
// 1-1. cmsn_create_device
SDK_EXTERN CMSNDevice * cmsn_create_device(const char * device_id);

// 1-2. cmsn_release_device (DEPRECATED:We recommend singleton implementation) 
// SDK_EXTERN int cmsn_release_device(CMSNDevice * device);


// 2. Data Handler
// ==============================================================================
/* call this functions when received any byte data from the devices
 *
 * Note:
 *   This is not a thread safe function
 *
 * @param   device
 * @param   data          data would NOT be free in this function
 * @param   size
 * @return  remain_size   the size of the remaining fragment data
 *          -1            fail
 */
SDK_EXTERN int cmsn_did_receive_data(CMSNDevice * device, const char * data, int size);


// 3. Message Builder
// ==============================================================================
// 3-1. SYS Config Message Builder
/*
 * 3-1-1. sys_config_pack
 *
 * @param   buffer
 * @param   sys_config_cmd  SysConfigCmd
 * @return  n  buffer_size  (buffer need to be free)
 *         -1  failed
 */
SDK_EXTERN int sys_config_pack(char ** buffer, int sys_config_cmd, unsigned int msg_id);

/*
 * 3-1-2. sys_config_set_device_name_pack
 *
 * @param   buffer
 * @param   device_name     string length should be 4 ~ 18
 * @return  n  buffer_size  (buffer need to be free)
 *         -1  failed
 */
SDK_EXTERN int sys_config_set_device_name_pack(char ** buffer, const char * device_name, unsigned int msg_id);

/*
 * 3-1-3. sys_config_pair_pack
 *
 * @param   buffer
 * @param   pair_info     string length should be 4 ~ 18
 * @return  n  buffer_size  (buffer need to be free)
 *         -1  failed
 */
SDK_EXTERN int sys_config_pair_pack(char ** buffer, const char * pair_info, unsigned int msg_id);

/*
 * 3-1-4. sys_config_validate_pair_info_pack
 *
 * @param   buffer
 * @param   pair_info     string length should be 4 ~ 18
 * @return  n  buffer_size  (buffer need to be free)
 *         -1  failed
 */
SDK_EXTERN int sys_config_validate_pair_info_pack(char ** buffer, const char * pair_info, unsigned int msg_id);

/*
 * 3-1-5. sys_config_set_led_color_pack
 *
 * @param   buffer
 * @param   r     0-255 (red value)
 * @param   g     0-255 (gree value)
 * @param   b     0-255 (blue value)
 * @return  n  buffer_size  (buffer need to be free)
 *         -1  failed
 */
SDK_EXTERN int sys_config_set_led_color_pack(char ** buffer, int r, int g, int b, unsigned int msg_id);

/*
 * 3-1-6. sys_config_set_sleep_idle_time_pack
 *
 * @param   buffer
 * @param   time_sec     seconds to put device into sleep mode, 0 for no sleep. 
 * @return  n  buffer_size  (buffer need to be free)
 *         -1  failed
 */
SDK_EXTERN int sys_config_set_sleep_idle_time_pack(char ** buffer, int time_sec, unsigned int msg_id);

/*
 * 3-1-7. sys_config_set_vibration_intensity_pack
 *
 * @param   buffer
 * @param   intensity     vibration intensity, 0 ~ 100. 
 * @return  n  buffer_size  (buffer need to be free)
 *         -1  failed
 */
SDK_EXTERN int sys_config_set_vibration_intensity_pack(char ** buffer, int intensity, unsigned int msg_id);

// 3-2. AFE Config Message Builder
/*
 * 3-2-1. afe_config_pack
 *
 * @param   sample_rate      AfeSampleRate
 * @param   buffer
 * @param   data_channel     Channel:data channel
 * @param   lead_off_option  AfeConfigLeadOff AC/DC current option
 * @param   lead_off_channel Channel:LeadOff detection channel
 * @param   rld_channel      Channel:Rld detectionChannel
 * @return  n  buffer_size  (buffer need to be free)
 *         -1  failed
 */
SDK_EXTERN int afe_config_pack(char ** buffer, int sample_rate, int data_channel, int lead_off_option, int lead_off_channel, int rld_channel, unsigned int msg_id);

// 3-3. Acc Config Message Builder
/*
 * 3-3-1. imu_config_pack
 *
 * @param   buffer
 * @param   imu_sample_rate     IMUSampleRate
 * @return  n  buffer_size  (buffer need to be freed)
 *         -1  failed
 */
SDK_EXTERN int imu_config_pack(char ** buffer, int imu_sample_rate, unsigned int msg_id);


// Error code to message converters
SDK_EXTERN const char* afe_config_err_code_to_msg(int err_code);
SDK_EXTERN const char* imu_config_err_code_to_msg(int err_code);
SDK_EXTERN const char* sys_config_err_code_to_msg(int err_code);
SDK_EXTERN const char* cmsn_err_code_to_msg(int err_code);

// 4. Device state getters
SDK_EXTERN DeviceContactState cmsn_get_contact_state(CMSNDevice* device);
SDK_EXTERN DeviceOrientation cmsn_get_orientation(CMSNDevice* device);

// 5. Callbacks
// ==============================================================================
// 5-1. Global Callbacks
typedef void (*LogCB)(const char * msg);
SDK_EXTERN int cmsn_set_log_callback(LogCB cb);
SDK_EXTERN void cmsn_set_log_level(LogLevel logLevel);
SDK_EXTERN void cmsn_log(LogLevel logLevel, const char *format, ...);

typedef float* (*ModelPredictCB)(const char* device_id, const char* model_type, const float *data, const int len);
SDK_EXTERN void cmsn_set_model_predict_callback(ModelPredictCB cb);
SDK_EXTERN float* cmsn_model_predict(const char* device_id, const char* model_type, float* predictor_buff);

// 5-2. Device Callbacks
typedef void (*ContactStateChangeCB)(const char * device_id, DeviceContactState state);
SDK_EXTERN int cmsn_set_contact_state_change_callback(CMSNDevice * device, ContactStateChangeCB cb);

typedef void (*SignalQualityWarningCB)(const char * device_id, int quality);
SDK_EXTERN int cmsn_set_signal_quality_warning_callback(CMSNDevice * device, SignalQualityWarningCB cb);

typedef void (*ErrorCB)(const char * device_id, int error);
SDK_EXTERN int cmsn_set_error_callback(CMSNDevice * device, ErrorCB cb);

typedef void (*EEGDataCB)(const char * device_id, EEGData * data);
SDK_EXTERN int cmsn_set_eeg_data_callback(CMSNDevice * device, EEGDataCB cb);
SDK_EXTERN int cmsn_set_raw_eeg_data_callback(CMSNDevice * device, EEGDataCB cb);

typedef void (*EEGStatsCB)(const char* device_mac, EEGStats * stats);
SDK_EXTERN int cmsn_set_eeg_stats_callback(CMSNDevice * device, EEGStatsCB cb);

typedef void (*IMUDataCB)(const char * device_id, IMUData * data);
SDK_EXTERN int cmsn_set_imu_data_callback(CMSNDevice * device, IMUDataCB cb);

typedef void (*DeviceOrientationCB)(const char * device_id, DeviceOrientation orientation);
SDK_EXTERN int cmsn_set_orientation_change_callback(CMSNDevice * device, DeviceOrientationCB cb);

typedef void (*AttentionCB)(const char * device_id, float attention);
SDK_EXTERN int cmsn_set_attention_callback(CMSNDevice * device, AttentionCB cb);

typedef void (*MeditationCB)(const char * device_id, float meditation);
SDK_EXTERN int cmsn_set_meditation_callback(CMSNDevice * device, MeditationCB cb);

typedef void (*SocialEngagementCB)(const char * device_id, float social_engagement);
SDK_EXTERN int cmsn_set_social_engagement_callback(CMSNDevice * device, SocialEngagementCB cb);

typedef void (*BlinkCB)(const char * device_id);
SDK_EXTERN int cmsn_set_blink_callback(CMSNDevice * device, BlinkCB cb);

typedef void (*ConfigRespCB)(const char * device_id, unsigned int msg_id, ConfigResp* resp);
SDK_EXTERN int cmsn_set_afe_config_resp_callback(CMSNDevice * device, ConfigRespCB cb);
SDK_EXTERN int cmsn_set_imu_config_resp_callback(CMSNDevice * device, ConfigRespCB cb);
SDK_EXTERN int cmsn_set_sys_config_resp_callback(CMSNDevice * device, ConfigRespCB cb);

typedef void (*SysInfoCB)(const char * device_id, unsigned int msg_id, SysInfoData* sys_info);
SDK_EXTERN int cmsn_set_sys_info_callback(CMSNDevice * device, SysInfoCB cb);

typedef void (*LeadOffStatusCB)(const char * device_id, unsigned int msg_id, DeviceContactState center_rld, DeviceContactState side_channels);
SDK_EXTERN int cmsn_set_lead_off_status_callback(CMSNDevice * device, LeadOffStatusCB cb);

SDK_EXTERN const char* cmsn_get_sdk_version();

// 6. Desktop bluetooth APIs
// ==============================================================================
#if defined(_WIN32) || TARGET_OS_OSX
typedef struct {
    char uuid[40];
    char name[40];
    float rssi;
    unsigned long long address;
    bool is_in_pairing_mode;
    char battery_level;
} CMSNBLEInfo;

typedef struct {
    char manufacturer[16];
    char model[16];
    char serial[17]; // NOTE: crimson SN length is 17
    char hardware[16];
    char firmware[16];
} CMSNDeviceInfo;

typedef enum {
    BLE_CONNECTIVITY_CONNECTING    = 0,
    BLE_CONNECTIVITY_CONNECTED     = 1,
    BLE_CONNECTIVITY_DISCONNECTING = 2,
    BLE_CONNECTIVITY_DISCONNECTED  = 3,
} BLEConnectivity;

typedef enum {
    AFE_SAMPLE_RATE_125  = 0,
    AFE_SAMPLE_RATE_250  = 1,
    AFE_SAMPLE_RATE_500  = 2,
    AFE_SAMPLE_RATE_1000 = 3,
} AFESampleRate;

typedef enum {
    AFE_CHANNEL_NONE = 0,
    AFE_CHANNEL_CH1  = 1,
    AFE_CHANNEL_CH2  = 2,
    AFE_CHANNEL_BOTH = 3,
} AFEChannel;

typedef enum {
    AFE_LEAD_OFF_DISABLED = 0,
    AFE_LEAD_OFF_AC       = 1,
    AFE_LEAD_OFF_DC_6nA   = 2,
    AFE_LEAD_OFF_DC_22nA  = 3,
    AFE_LEAD_OFF_DC_6uA   = 4,
    AFE_LEAD_OFF_DC_22uA  = 5,
} AFELeadOffOption;

typedef enum {
    IMU_SAMPLE_RATE_UNUSED = 0,
    IMU_SAMPLE_RATE_12_5 = 0x10,
    IMU_SAMPLE_RATE_26 = 0x20,
    IMU_SAMPLE_RATE_52 = 0x30,
    IMU_SAMPLE_RATE_104 = 0x40,
    IMU_SAMPLE_RATE_208 = 0x50,
    IMU_SAMPLE_RATE_416= 0x60,
    IMU_SAMPLE_RATE_833= 0x70,
} IMUSampleRate;

typedef void (*FoundDeviceCB)(CMSNBLEInfo *bleInfo);
SDK_EXTERN void cmsn_scan_ble_devices(FoundDeviceCB cb);
SDK_EXTERN void cmsn_stop_scan_ble_devices();
SDK_EXTERN CMSNDevice* cmsn_connect_ble(CMSNBLEInfo device_ble_info);
SDK_EXTERN void cmsn_disconnect_ble(CMSNDevice* device);
SDK_EXTERN BLEConnectivity cmsn_get_ble_connectivity(CMSNDevice* device);
SDK_EXTERN const char * cmsn_get_device_name(CMSNDevice* device);
SDK_EXTERN const char * cmsn_get_manufacturer_name(CMSNDevice* device);
SDK_EXTERN const char * cmsn_get_serial_number(CMSNDevice* device);
SDK_EXTERN const char * cmsn_get_model_number(CMSNDevice* device);
SDK_EXTERN const char * cmsn_get_hardware_revision(CMSNDevice* device);
SDK_EXTERN const char * cmsn_get_firmware_revision(CMSNDevice* device);
SDK_EXTERN int cmsn_get_battery_level(CMSNDevice* device);
//TODO on_battery_level_callback

SDK_EXTERN int cmsn_pair(CMSNDevice * device, ConfigRespCB cb);
SDK_EXTERN int cmsn_check_pairing_status(CMSNDevice * device, ConfigRespCB cb);

SDK_EXTERN int cmsn_start_eeg_stream(CMSNDevice* device, ConfigRespCB cb);
SDK_EXTERN int cmsn_stop_eeg_stream(CMSNDevice* device, ConfigRespCB cb);

SDK_EXTERN int cmsn_config_afe(CMSNDevice * device, AFESampleRate sample_rate, AFEChannel data_channel, AFELeadOffOption lead_off_option, AFEChannel lead_off_channel, AFEChannel rld_channel, ConfigRespCB cb);
// SDK_EXTERN int cmsn_config_imu(CMSNDevice * device, IMUSampleRate imu_sample_rate, ConfigRespCB cb);
SDK_EXTERN int cmsn_start_imu_stream(CMSNDevice * device, IMUSampleRate imu_sample_rate, ConfigRespCB cb);
SDK_EXTERN int cmsn_stop_imu_stream(CMSNDevice * device, ConfigRespCB cb);

SDK_EXTERN int cmsn_set_device_name(CMSNDevice * device, const char * device_name, ConfigRespCB cb);
SDK_EXTERN int cmsn_set_led_color(CMSNDevice* device, int r, int g, int b, ConfigRespCB cb);
SDK_EXTERN int cmsn_set_vibration_intensity(CMSNDevice* device, int intensity, ConfigRespCB cb);
SDK_EXTERN int cmsn_set_sleep_idle_time(CMSNDevice* device, int secs, ConfigRespCB cb);

SDK_EXTERN int cmsn_device_shutdown(CMSNDevice * device, ConfigRespCB cb);
SDK_EXTERN int cmsn_device_enter_ota(CMSNDevice * device, ConfigRespCB cb);
SDK_EXTERN int cmsn_get_sys_info(CMSNDevice * device, SysInfoCB info_cb, ConfigRespCB cb);
SDK_EXTERN int cmsn_get_lead_off_status(CMSNDevice * device, LeadOffStatusCB status_cb, ConfigRespCB cb);


// set callback functions (implemented in crimson_ble.c)
typedef void (*DeviceInfoCB)(const char * device_id, CMSNDeviceInfo *info);
SDK_EXTERN int cmsn_set_device_info_callback(CMSNDevice * device, DeviceInfoCB cb);

typedef void (*ConnectivityChangeCB)(const char * device_id, BLEConnectivity connectivity);
SDK_EXTERN int cmsn_set_connectivity_change_callback(CMSNDevice * device, ConnectivityChangeCB cb);

SDK_EXTERN int cmsn_select_attention_model(CMSNDevice * device, int model_key);
#endif
// ==============================================================================


// 7. Test & experimental functions
// ==============================================================================

typedef enum {
    TASK_SESSION_UNADJUSTED = -1,
    TASK_SESSION_NORMAL = 0,
    TASK_SESSION_FOCUS = 1,
    TASK_SESSION_RELAX = 2
} DEVTaskSession;

SDK_EXTERN void dev_set_task_session(DEVTaskSession session);
SDK_EXTERN void dev_set_social_session(bool muEnabled);

SDK_EXTERN int hello(int num);
typedef struct {
    void * bs;
    void * bp;
    void * fft;
} CMSNFilter;

SDK_EXTERN CMSNFilter * dev_create_sdk_filter();
SDK_EXTERN float dev_filter(CMSNFilter* filter, float signal);
SDK_EXTERN float* dev_fft(CMSNFilter* filter, float* windowed_signal, int size);
SDK_EXTERN void debug_signal(float * signal);
SDK_EXTERN void dev_analyze_eeg(CMSNDevice* device, const float *eeg_data, int size);

//CFFI_DEF_END

#ifdef __cplusplus
}
#endif
#endif
