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

    if reg_addr == 0x17:  # Conditional for register at 0x17
        # Decode JEITA_VSET (bits 7-5)
        jeita_vset = (data >> 5) & 0x07
        if jeita_vset == 0:
            jeita_vset_msg = "Charge Suspend"
        elif jeita_vset == 1:
            jeita_vset_msg = "VREG to VREG-800mV"
        elif jeita_vset == 2:
            jeita_vset_msg = "VREG to VREG-600mV"
        elif jeita_vset == 3:
            jeita_vset_msg = "VREG to VREG-400mV (default)"
        elif jeita_vset == 4:
            jeita_vset_msg = "VREG to VREG-300mV"
        elif jeita_vset == 5:
            jeita_vset_msg = "VREG to VREG-200mV"
        elif jeita_vset == 6:
            jeita_vset_msg = "VREG to VREG-100mV"
        else:  # jeita_vset == 7
            jeita_vset_msg = "VREG unchanged"
        
        # Decode JEITA_ISETH (bits 4-3)
        jeita_iseth = (data >> 3) & 0x03
        if jeita_iseth == 0:
            jeita_iseth_msg = "Charge Suspend"
        elif jeita_iseth == 1:
            jeita_iseth_msg = "ICHG to 20% ICHG"
        elif jeita_iseth == 2:
            jeita_iseth_msg = "ICHG to 40% ICHG"
        else:  # jeita_iseth == 3
            jeita_iseth_msg = "ICHG unchanged (default)"
        
        # Decode JEITA_ISETC (bits 2-1)
        jeita_isetc = (data >> 1) & 0x03
        if jeita_isetc == 0:
            jeita_isetc_msg = "Charge Suspend"
        elif jeita_isetc == 1:
            jeita_isetc_msg = "ICHG to 20% ICHG (default)"
        elif jeita_isetc == 2:
            jeita_isetc_msg = "ICHG to 40% ICHG"
        else:  # jeita_isetc == 3
            jeita_isetc_msg = "ICHG unchanged"
        
        # Bit 0 is reserved; no need to decode
        
        # Combine messages
        return f"JEITA_VSET: {jeita_vset_msg}, JEITA_ISETH: {jeita_iseth_msg}, JEITA_ISETC: {jeita_isetc_msg}"

    ###################

    if reg_addr == 0x16:  # Conditional for register at 0x16
        # Decode TREG (bits 7-6)
        treg = (data >> 6) & 0x03
        treg_msg = {
            0: "60°C",
            1: "80°C",
            2: "100°C",
            3: "120°C (default)"
        }.get(treg, "Unknown TREG setting")
        
        # Decode TSHUT (bits 5-4)
        tshut = (data >> 4) & 0x03
        tshut_msg = {
            0: "150°C",
            1: "130°C",
            2: "120°C",
            3: "85°C (default)"
        }.get(tshut, "Unknown TSHUT setting")
        
        # Decode pull-down enable bits (bit 3 for VBUS, bit 2 for VAC1, bit 1 for VAC2)
        vbus_pd_en = "Enabled" if (data >> 3) & 0x01 else "Disabled"
        vac1_pd_en = "Enabled" if (data >> 2) & 0x01 else "Disabled"
        vac2_pd_en = "Enabled" if (data >> 1) & 0x01 else "Disabled"
        
        # Bit 0 is reserved; no need to decode
        
        # Combine messages
        return f"TREG: {treg_msg}, TSHUT: {tshut_msg}, VBUS_PD_EN: {vbus_pd_en}, VAC1_PD_EN: {vac1_pd_en}, VAC2_PD_EN: {vac2_pd_en}"

    ###################

    if reg_addr == 0x15:  # Conditional for register at 0x15
        # Decode VOC_PCT (bits 7-5)
        voc_pct = (data >> 5) & 0x07
        voc_pct_msg = {
            0: "50.625%",
            1: "62.5%",
            2: "68.75%",
            3: "75%",
            4: "81.25%",
            5: "87.5% (default)",
            6: "93.75%",
            7: "1"
        }.get(voc_pct, "Unknown VOC_PCT setting")
        
        # Decode VOC_DLY (bits 4-3)
        voc_dly = (data >> 3) & 0x03
        voc_dly_msg = {
            0: "50ms",
            1: "300ms (default)",
            2: "2s",
            3: "5s"
        }.get(voc_dly, "Unknown VOC_DLY setting")
        
        # Decode VOC_RATE (bits 2-1)
        voc_rate = (data >> 1) & 0x03
        voc_rate_msg = {
            0: "30s",
            1: "2mins (default)",
            2: "10mins",
            3: "30mins"
        }.get(voc_rate, "Unknown VOC_RATE setting")
        
        # Decode EN_MPPT (bit 0)
        en_mppt_msg = "Enabled" if data & 0x01 else "Disabled (default)"
        
        # Combine messages
        return f"VOC_PCT: {voc_pct_msg}, VOC_DLY: {voc_dly_msg}, VOC_RATE: {voc_rate_msg}, EN_MPPT: {en_mppt_msg}"

    ####################

    if reg_addr == 0x14:  # Conditional for register at 0x14
        # Interpret the SFET_PRESENT bit (bit 7)
        sfet_present_msg = "Ship FET Populated" if (data >> 7) & 0x01 else "No Ship FET"
        
        # Interpret the EN_IBAT bit (bit 5)
        en_ibat_msg = "IBAT discharge sensing enabled" if (data >> 5) & 0x01 else "IBAT discharge sensing disabled"
        
        # Interpret the IBAT_REG bits (bits 4-3)
        ibat_reg = (data >> 3) & 0x03
        ibat_reg_msg = {
            0: "3A",
            1: "4A",
            2: "5A",
            3: "Disabled (default)"
        }.get(ibat_reg, "Unknown IBAT_REG setting")
        
        # Interpret the EN_INDPNM bit (bit 2)
        en_indpnm_msg = "Internal INDPNM resistor current limit enabled" if (data >> 2) & 0x01 else "Disabled"
        
        # Interpret the EN_EXTILIM bit (bit 1)
        en_extilim_msg = "External ILIM high input current enabled" if (data >> 1) & 0x01 else "Disabled (default)"
        
        # Interpret the EN_BATOC bit (bit 0)
        en_batoc_msg = "Battery discharging current OCP enabled" if data & 0x01 else "Disabled (default)"
        
        # Combine messages
        return f"SFET_PRESENT: {sfet_present_msg}, EN_IBAT: {en_ibat_msg}, IBAT_REG: {ibat_reg_msg}, EN_INDPNM: {en_indpnm_msg}, EN_EXTILIM: {en_extilim_msg}, EN_BATOC: {en_batoc_msg}"

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
