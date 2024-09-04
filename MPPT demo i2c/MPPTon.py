import smbus

# Create an instance of the I2C bus
bus = smbus.SMBus(1)  

# Device I2C address (replace with your device's address)
device_address = 0x6B  

# Register address to write to (replace with your register's address)
## watchdog registe
register_address = 0x10
## ICO register
register_address2 = 0x0F
## Enable MPPT address
register_address3 = 0x15
## Enable ADC control
register_address4 = 0x2E
# Set the bit at bit_position
## Watchdog OFF
new_value = 0b10000000
## ICO enable
new_value2 = 0b10110010
## EN MPPT
new_value3 = 0b10101011
## EN ADC control
new_value4 = 0b10110000




# Read the current value of the register
bus.write_byte_data(device_address, register_address, new_value)
bus.write_byte_data(device_address, register_address2, new_value2)
bus.write_byte_data(device_address, register_address3, new_value3)
bus.write_byte_data(device_address, register_address4, new_value4)
         
