import curses
import smbus

# Initialize I2C bus
bus = smbus.SMBus(1)
device_address = 0x6B  # Example device address; replace with your actual device address

# Define registers and their byte lengths
# This is a simplified map based on your description; add all necessary registers and lengths here
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

def interpret_register_data(reg_addr, data):
    # Messages for each bit depending on its state (0 or 1)

    ###################
    if reg_addr == 0x20:
        bit_messages = {
            0: {0: "Nominal", 1: "VAC1 Over-voltage"},
            1: {0: "Nominal", 1: "VAC2 Over-voltage"},
            2: {0: "Nominal", 1: "Converter Over-current Protection Active"},
            3: {0: "Nominal", 1: "BAT Over-current Protection Active"},
            4: {0: "Nominal", 1: "BUS Over-current Protection Active"},
            5: {0: "Nominal", 1: "BAT Over-voltage Protection Active"},
            6: {0: "Nominal", 1: "BUS Over-voltage Protection Active"},
            7: {0: "Nominal", 1: "Device in Battery Discharging Current Regulation"},
        }
    
        # Initialize an empty list to store messages for the current register data
        messages = []
    
        # Iterate through each bit position from 0 to 7
        for bit_pos in range(8):
            # Determine the state of the bit at bit_pos (0 or 1)
            bit_state = (data >> bit_pos) & 1
            # Append the corresponding message for the bit's state to the messages list
            if bit_pos in bit_messages:
                messages.append(bit_messages[bit_pos][bit_state])
    
        # Join all messages with a newline character and return the result
        return "\n".join(messages)

    ###################
    if reg_addr == 0x19:  # Assuming 0x19 is the address of the ICO_Current_Limit Register
        # Combine the two bytes into one 16-bit value (assuming the data is big-endian)
        combined_data = (data[0] << 8) | data[1]
        # Extract the ICO_ILIM field (assuming it's bits 0-7)
        ico_ilim = combined_data & 0xFF  # Masking with 0xFF to get the lowest 8 bits
        # Convert the binary value to an actual current limit
        current_limit_mA = ico_ilim * 10  # Each step is 10mA
        return f"ICO Current Limit: {current_limit_mA} mA"

    ###################
    if reg_addr == 0x18:  # Conditional for register at 0x18
        # Interpret the TS_COOL field (bits 7-6)
        ts_cool = (data >> 6) & 0x03
        if ts_cool == 0:
            ts_cool_msg = "71.1% (5°C)"
        elif ts_cool == 1:
            ts_cool_msg = "68.4% (10°C) - default"
        elif ts_cool == 2:
            ts_cool_msg = "65.5% (15°C)"
        else:  # ts_cool == 3
            ts_cool_msg = "62.4% (20°C)"
        
        # Interpret the TS_WARM field (bits 5-4)
        ts_warm = (data >> 4) & 0x03
        if ts_warm == 0:
            ts_warm_msg = "48.4% (40°C)"
        elif ts_warm == 1:
            ts_warm_msg = "44.8% (45°C) - default"
        elif ts_warm == 2:
            ts_warm_msg = "41.2% (50°C)"
        else:  # ts_warm == 3
            ts_warm_msg = "37.7% (55°C)"
        
        # Interpret the BHOT field (bits 3-2)
        bhot = (data >> 2) & 0x03
        if bhot == 0:
            bhot_msg = "55°C"
        elif bhot == 1:
            bhot_msg = "60°C - default"
        elif bhot == 2:
            bhot_msg = "65°C"
        else:  # bhot == 3
            bhot_msg = "Disable"
        
        # Interpret the BCOLD bit (bit 1)
        bcold = (data >> 1) & 0x01
        bcold_msg = "NOT ignore" if bcold == 0 else "Ignore"
        
        # Interpret the TS_IGNORE bit (bit 0)
        ts_ignore = data & 0x01
        ts_ignore_msg = "NOT ignore" if ts_ignore == 0 else "Ignore"
        
        # Combine messages
        return f"TS_COOL: {ts_cool_msg}, TS_WARM: {ts_warm_msg}, BHOT: {bhot_msg}, BCOLD: {bcold_msg}, TS_IGNORE: {ts_ignore_msg}"

    ###################
    return f"{data:02x}"  # Return data as a hexadecimal string

def display_data(screen):
    curses.curs_set(0)
    screen.nodelay(True)

    while True:
        screen.clear()
        for reg_addr, reg_info in registers.items():
            reg_name, length = reg_info
            data = read_register_data(reg_addr, length)
            if data is not None:
                if isinstance(data, list):
                    # Interpret each byte of data if multiple bytes were read
                    data_str = ' '.join([interpret_register_data(reg_addr, byte) for byte in data])
                else:
                    # Interpret the data if a single byte was read
                    data_str = interpret_register_data(reg_addr, data)
                screen.addstr(f"{reg_name} ({reg_addr:02x}): {data_str}\n")

        screen.refresh()
        key = screen.getch()
        if key == ord('q'):
            break

        curses.napms(250)
