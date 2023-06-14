import platform
import pyudev
import subprocess

def get_disk_serial_number():
    system = platform.system()
    if system == 'Windows':
        return get_disk_serial_number_windows()
    elif system == 'Linux':
        return get_disk_serial_number_linux()
    elif system == 'Darwin':
        return get_disk_serial_number_mac()
    else:
        return None

def get_disk_serial_number_windows():
    command = 'wmic diskdrive get serialnumber'
    output = subprocess.check_output(command, shell=True, text=True)
    serial_numbers = [line.strip() for line in output.split('\n') if line.strip()]
    return serial_numbers[1] if len(serial_numbers) > 1 else None

def get_disk_serial_number_linux():
    context = pyudev.Context()
    for device in context.list_devices(subsystem='block'):
        if device.device_type == 'disk':
            try:
                serial_number = device.get('ID_SERIAL_SHORT')
                if serial_number:
                    return serial_number
            except (KeyError, OSError):
                pass
    return None

def get_disk_serial_number_mac():
    # Add macOS-specific method to retrieve disk serial number here
    return None

# Example usage
serial_number = get_disk_serial_number()
if serial_number:
    print("Disk Serial Number:", serial_number)
else:
    print("Failed to retrieve the disk serial number.")