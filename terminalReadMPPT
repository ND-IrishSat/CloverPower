import curses
import smbus

# Initialize I2C bus
bus = smbus.SMBus(1)
device_address = 0x6B  # Example device address; replace with your actual devic>

# Define registers and their byte lengths
# This is a simplified map based on your description; add all necessary registe>
registers = {
    0x00: ("REG00_Minimal_System_Voltage", 1),
    0x01: ("REG01_Charge_Voltage_Limit", 2),
    0x03: ("REG03_Charge_Current_Limit", 2),
    0x05: ("REG05_Input_Voltage_Limit", 1),
    0x06: ("REG06_Input_Current_Limit", 2),
    0x08: ("REG08_Precharge_Control", 1),
    0x09: ("REG09_Termination_Control", 1),
    0x0A: ("REG0A_Re-charge_Control", 1),
    0x0B: ("REG0B_VOTG_regulation", 2),
    0x0D: ("REG0D_IOTG_regulation", 1),
    0x0E: ("REG0E_Timer_Control", 1),
    0x0F: ("REG0F_Charger_Control_0", 1),
    0x10: ("REG10_Charger_Control_1", 1),
    0x11: ("REG11_Charger_Control_2", 1),
    0x12: ("REG12_Charger_Control_3", 1),
    0x13: ("REG13_Charger_Control_4", 1),
    0x14: ("REG14_Charger_Control_5", 1),
    0x15: ("REG15_MPPT_Control", 1),
    0x16: ("REG16_Temperature_Control", 1),
    0x17: ("REG17_NTC_Control_0", 1),
    0x18: ("REG18_NTC_Control_1", 1),
    0x19: ("REG19_ICO_Current_Limit", 2),
    0x1B: ("REG1B_Charger_Status_0", 1),
    0x1C: ("REG1C_Charger_Status_1", 1),
    0x1D: ("REG1D_Charger_Status_2", 1),
    0x1E: ("REG1E_Charger_Status_3", 1),
    0x1F: ("REG1F_Charger_Status_4", 1),
    0x20: ("REG20_FAULT_Status_0", 1),
    0x21: ("REG21_FAULT_Status_1", 1),
    0x22: ("REG22_Charger_Flag_0", 1),
    0x23: ("REG23_Charger_Flag_1", 1),
    0x24: ("REG24_Charger_Flag_2", 1),
    0x25: ("REG25_Charger_Flag_3", 1),
    0x26: ("REG26_FAULT_Flag_0", 1),
    0x27: ("REG27_FAULT_Flag_1", 1),
    0x28: ("REG28_Charger_Mask_0", 1),
    0x29: ("REG29_Charger_Mask_1", 1),
    0x2A: ("REG2A_Charger_Mask_2", 1),
    0x2B: ("REG2B_Charger_Mask_3", 1),
    0x2C: ("REG2C_FAULT_Mask_0", 1),
    0x2D: ("REG2D_FAULT_Mask_1", 1),
    0x2E: ("REG2E_ADC_Control", 1),  
    0x2F: ("REG2F_ADC_Function_Disable_0", 1),
    0x30: ("REG30_ADC_Function_Disable_1", 1),
    0x31: ("REG31_IBUS_ADC", 2),
    0x33: ("REG33_IBAT_ADC", 2),
    0x35: ("REG35_VBUS_ADC", 2),
    0x37: ("REG37_VAC1_ADC", 2),
    0x39: ("REG39_VAC2_ADC", 2),
    0x3B: ("REG3B_VBAT_ADC", 2),
    0x3D: ("REG3D_VSYS_ADC", 2),
    0x3F: ("REG3F_TS_ADC", 2),
    0x41: ("REG41_TDIE_ADC", 2),
    0x43: ("REG43_D+_ADC", 2),
    0x45: ("REG45_D-_ADC", 2),
    0x47: ("REG47_DPDM_Driver", 1),
    0x48: ("REG48_Part_Information", 1),
}

def read_register_data(reg_addr, length):
    """Read bytes from a single I2C register."""
    try:
        if length == 1:
            # Read a single byte
            data = bus.read_byte_data(device_address, reg_addr)
        else:
            # Read multiple bytes
            data = bus.read_i2c_block_data(device_address, reg_addr, length)
        return data
    except Exception as e:
        print(f"Error reading register {reg_addr}: {e}")
        return None

def display_data(screen):
    curses.curs_set(0)  # Hide cursor
    screen.nodelay(True)  # Make getch() non-blocking

    while True:
        screen.clear()        
        for reg_addr, reg_info in registers.items():
            reg_name, length = reg_info
            data = read_register_data(reg_addr, length)
            if data is not None:
                if isinstance(data, list):
                    data_str = ' '.join([f"{byte:02b}" for byte in data])
                else:
                    data_str = f"{data:02b}"
                screen.addstr(f"{reg_name} ({reg_addr:02b}): {data_str}\n")
        
        screen.refresh()
        key = screen.getch()
        if key == ord('q'):
            break  # Exit loop

        curses.napms(500)  # Refresh every 500 milliseconds

# Initialize curses application
curses.wrapper(display_data)
