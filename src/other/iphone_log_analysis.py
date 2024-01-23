import libimobiledevice
# import libimobiledevice.util.ide as idevice


def log_analysis_ios():
    print('iPhone 13.3 iOS device .')
    # 连接到iPhone
    # libimobiledevice.
    device = libimobiledevice.Device.find_device_by_udid()
    libimobiledevice.Connection.register(device)

    # 获取日志
    log_path = '/private/var/log/system.log'  # 这是系统日志的路径，您可以根据需要更改
    log_data = device.read_data_from_file(log_path)
    print(log_data)


if __name__ == '__main__':
    log_analysis_ios()
