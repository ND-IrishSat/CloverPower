import streamlit as st
import random

# Initialize I2C bus

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
    """
    Mock function to simulate reading bytes from a single I2C register.
    Generates random data for testing without actual device.
    """
    # Generate random data based on the length of the register
    if length == 1:
        # Return a single byte value
        return random.randint(0, 255)
    else:
        # Return a list of byte values
        return [random.randint(0, 255) for _ in range(length)]

def interpret_register_data(reg_addr, data):
    # Messages for each bit depending on its state (0 or 1)
    if isinstance(data, list):
        combined_data = 0
        for byte in data:
            combined_data = (combined_data << 8) | byte
        data = combined_data
    if reg_addr == 0x21:  # Conditional for register at 0x21
        # Dictionary to hold the status messages for each bit
        bit_messages = {
            7: {0: "VSYS_SHORT_STAT: Normal", 1: "VSYS_SHORT_STAT: Device in SYS short circuit protection"},
            6: {0: "VSYS_OVP_STAT: Normal", 1: "VSYS_OVP_STAT: Device in SYS over-voltage protection"},
            5: {0: "OTG_OVP_STAT: Normal", 1: "OTG_OVP_STAT: Device in OTG over-voltage"},
            4: {0: "OTG_UVP_STAT: Normal", 1: "OTG_UVP_STAT: Device in OTG under voltage"},
            2: {0: "TSHUT_STAT: Normal", 1: "TSHUT_STAT: Device in thermal shutdown protection"},
        }
        
        # Initialize an empty list to store messages for the current register data
        messages = []
    
        # Reserved bits are 0, 1, and 3. They are not used, so no need to add a message for them.
        # Loop through each bit and append the corresponding message to the messages list
        for bit in bit_messages:
            bit_value = (data >> bit) & 0x01
            messages.append(bit_messages[bit][bit_value])
    
        # Join all messages with a comma
        return ', '.join(messages)  # Returns a string of status messages
    
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
    
    if reg_addr == 0x1F:  # Conditional for register at 0x1F
        # Dictionary to hold the status messages for each bit
        bit_messages = {
            0: {0: "TS_HOT_STAT: Temperature is NOT in the hot range", 1: "TS_HOT_STAT: Temperature is in the hot range, higher than T5"},
            1: {0: "TS_WARM_STAT: Temperature is NOT in the warm range", 1: "TS_WARM_STAT: Temperature is in the warm range, between T3 and T5"},
            2: {0: "TS_COOL_STAT: Temperature is NOT in the cool range", 1: "TS_COOL_STAT: Temperature is in the cool range, between T1 and T2"},
            3: {0: "TS_COLD_STAT: Temperature is NOT in the cold range", 1: "TS_COLD_STAT: Temperature is in the cold range, lower than T1"},
            4: {0: "VBATOTG_LOW_STAT: Battery voltage is high enough to enable OTG operation", 
                1: "VBATOTG_LOW_STAT: Battery voltage is too low to enable OTG operation"},
        }
        
        # Initialize an empty list to store messages for the current register data
        messages = []
    
        # Bits 5 to 7 are reserved, add a generic message for them if set
        for bit in range(5, 8):
            if (data >> bit) & 0x01:
                messages.append(f"Bit {bit}: Reserved bit is set")
    
        # Loop through each bit and append the corresponding message to the messages list
        for bit in bit_messages:
            bit_value = (data >> bit) & 0x01
            messages.append(bit_messages[bit][bit_value])
        
        # Join all messages with a comma
        return ', '.join(messages)  # Returns a string of status messages

    ###################

    if reg_addr == 0x1E:  # Conditional for register at 0x1E
        # Dictionary to hold the status messages for each bit with context
        bit_messages = {
            1: {0: "Pre-charge timer status: Normal", 1: "Pre-charge timer status: Safety timer expired"},
            3: {0: "CHRG_INHIBIT status: VBUS not above VBUS_MIN (device not ready to charge)", 
                1: "CHRG_INHIBIT status: VBUS above VBUS_MIN (device ready to charge)"},
            4: {0: "Fast charge timer status: Not expired", 
                1: "Fast charge timer status: Safety timer expired"},
            5: {0: "IINDPM status: Not in DPM regulation", 
                1: "IINDPM status: In DPM regulation"},
            6: {0: "VINDPM status: Not in input voltage regulation", 
                1: "VINDPM status: In input voltage regulation"},
            7: {0: "Thermal regulation status: No thermal regulation", 
                1: "Thermal regulation status: Thermal regulation active"},
        }
        
        # Initialize an empty list to store messages for the current register data
        messages = []
        
        # Handle the reserved bits
        reserved_bits = [0, 2]
        for bit in reserved_bits:
            messages.append(f"Bit {bit}: Reserved")
        
        # Loop through each bit and append the corresponding message to the messages list
        for bit in bit_messages:
            bit_value = (data >> bit) & 0x01
            messages.append(bit_messages[bit][bit_value])
        
        # Join all messages with a comma
        return ', '.join(messages)  # Returns a string of status messages

    ###################

    if reg_addr == 0x1D:  # Conditional for register at 0x1D
        # Dictionary to hold the status messages for each bit
        bit_messages = {
            0: {0: "VBAT NOT present", 1: "VBAT present"},
            1: {0: "D+/D- detection is NOT started, or the detection is done", 1: "D+/D- detection is ongoing"},
            2: {0: "Device in Normal thermal regulation", 1: "Device in thermal regulation"},
            # Bits 3 to 5 are reserved
            6: {0: "ICO disabled", 1: "ICO optimization in progress", 2: "Maximum input current detected", 3: "Reserved"},
            7: {}  # Bit 7 is reserved
        }
        
        # Initialize an empty list to store messages for the current register data
        messages = []

        # Handling for single-bit fields
        messages.append(bit_messages[0][data & 0x01])
        messages.append(bit_messages[1][(data >> 1) & 0x01])
        messages.append(bit_messages[2][(data >> 2) & 0x01])

        # Handling for multi-bit fields
        ico_stat = (data >> 6) & 0x03
        if ico_stat in bit_messages[6]:
            messages.append(bit_messages[6][ico_stat])
        else:
            messages.append("ICO Status: Reserved")
        
        # Join all messages with a comma
        return ', '.join(filter(None, messages))  # filter is used to remove empty messages

    ###################

    if reg_addr == 0x1C:  # Conditional for register at 0x1C
        # Dictionary to hold the status messages for each bit
        bit_messages = {
            'CHG_STAT': {
                0: "Not Charging",
                1: "Trickle Charge",
                2: "Pre Charge",
                3: "Fast Charge (CC mode)",
                4: "Taper Charge (CV mode)",
                5: "Reserved",
                6: "Top-off Timer Active Charging",
                7: "Charge Termination Done"
            },
            'VBUS_STAT': {
                0: "No input or DPM or BQOCL in OTG mode",
                1: "USB host SDP (0.5A)",
                2: "USB CDP (1.5A)",
                3: "USB DCP (3.25A)",
                4: "Adjustable High Voltage DCP (>3.25A)",
                5: "Unknown adapter",
                6: "Non-standard adapter (1A/2.1A/2.4A)",
                7: "Non-qualified adapter"
            },
            'DPM_STAT': {
                0: "Not DPM",
                1: "DPM"
            },
            'PG_STAT': {
                0: "Power NOT good",
                1: "Power good"
            },
            'THERM_STAT': {
                0: "Thermistor NOT in regulation",
                1: "Thermistor in regulation"
            },
            'VSYS_STAT': {
                0: "VSYS NOT regulated",
                1: "VSYS regulated"
            },
            'CHRG_DONE': {
                0: "Charge NOT done",
                1: "Charge done"
            }
        }
        
        # Initialize an empty list to store messages for the current register data
        messages = []

        # Interpretation for VBUS_STAT (bits 6-4)
        vbus_stat = (data >> 4) & 0x07
        messages.append(bit_messages['VBUS_STAT'][vbus_stat])

        # Interpretation for CHG_STAT (bits 3-2)
        chg_stat = (data >> 2) & 0x03
        messages.append(bit_messages['CHG_STAT'][chg_stat])

        # Interpretation for single-bit statuses
        messages.append(bit_messages['DPM_STAT'][(data >> 1) & 0x01])
        messages.append(bit_messages['PG_STAT'][(data >> 3) & 0x01])
        messages.append(bit_messages['THERM_STAT'][(data >> 5) & 0x01])
        messages.append(bit_messages['VSYS_STAT'][(data >> 6) & 0x01])
        messages.append(bit_messages['CHRG_DONE'][(data >> 7) & 0x01])

        # Combine messages
        return ', '.join(filter(None, messages))  # filter is used to remove empty messages

    ####################
    
    if reg_addr == 0x1B:  # Conditional for register at 0x1B
        # Dictionary to hold the status messages for each bit
        bit_messages = {
            0: {0: "VBUS NOT present", 1: "VBUS present (above present threshold)"},
            1: {0: "AC1 NOT present", 1: "AC1 present (above present threshold)"},
            2: {0: "AC2 NOT present", 1: "AC2 present (above present threshold)"},
            3: {0: "Power OK NOT in good status", 1: "Power OK in good status"},
            4: {0: "", 1: ""},  # Reserved or not specified in the given image
            5: {0: "Watchdog timer NOT expired", 1: "Watchdog timer expired"},
            6: {0: "VINDPM NOT in regulation or VOTG NOT in regulation", 1: "VINDPM in regulation or VOTG in regulation"},
            7: {0: "IN DPM or IOTG mode OFF", 1: "IN DPM or IOTG mode ON"}
        }
        
        # Initialize an empty list to store messages for the current register data
        messages = []

        # Iterate through each bit position and their corresponding messages
        for bit_pos in range(8):
            # Determine the state of the bit at bit_pos (0 or 1)
            bit_state = (data >> bit_pos) & 1
            # If there's a message defined for the bit state, append it to the messages list
            if bit_messages[bit_pos][bit_state]:
                messages.append(bit_messages[bit_pos][bit_state])

        # Join all messages with a comma and return the result
        return ', '.join(messages)

    ###################
    if reg_addr == 0x19:  # Assuming 0x19 is the address of the ICO_Current_Limit Register
        # Combine the two bytes into one 16-bit value (assuming the data is big-endian)
        listData = [int(i) for i in str(data)]
        combined_data = (listData[0] << 8) | listData[1]
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

    if reg_addr == 0x13:  # Conditional for register at 0x13
        # Interpret the EN_ACDC2 bit (bit 7)
        en_acdc2_msg = "AC/DC2 driver control active" if (data >> 7) & 0x01 else "AC/DC2 driver control off (default)"
        
        # Interpret the EN_ACDC1 bit (bit 6)
        en_acdc1_msg = "AC/DC1 driver control active" if (data >> 6) & 0x01 else "AC/DC1 driver control off (default)"
        
        # Interpret the PWM_FREQ bit (bit 5)
        pwm_freq_msg = "1.5 MHz" if (data >> 5) & 0x01 else "750 kHz (default)"
        
        # Interpret the DIS_STAT bit (bit 4)
        dis_stat_msg = "STAT pin output disable" if (data >> 4) & 0x01 else "STAT pin output enable (default)"
        
        # Interpret the DIS_VSYS_SHORT bit (bit 3)
        dis_vsys_short_msg = "VSYS short hiccup protection disable" if (data >> 3) & 0x01 else "VSYS short hiccup protection enable (default)"
        
        # Interpret the DIS_VOTP_LDO bit (bit 2)
        dis_votp_ldo_msg = "VOTP LDO hiccup protection disable" if (data >> 2) & 0x01 else "VOTP LDO hiccup protection enable (default)"
        
        # Interpret the FORCE_VINDPM bit (bit 1)
        force_vindpm_msg = "VINDPM force operation" if (data >> 1) & 0x01 else "VINDPM auto operation (default)"
        
        # Interpret the EN_IBUS_OCP bit (bit 0)
        en_ibus_ocp_msg = "IBUS OCP in forward mode enable" if data & 0x01 else "IBUS OCP disable (default)"
        
        # Combine messages
        return f"EN_ACDC2: {en_acdc2_msg}, EN_ACDC1: {en_acdc1_msg}, PWM_FREQ: {pwm_freq_msg}, DIS_STAT: {dis_stat_msg}, DIS_VSYS_SHORT: {dis_vsys_short_msg}, DIS_VOTP_LDO: {dis_votp_ldo_msg}, FORCE_VINDPM: {force_vindpm_msg}, EN_IBUS_OCP: {en_ibus_ocp_msg}"

    ####################

    if reg_addr == 0x12:  # Conditional for register at 0x12
        # Interpret each bit based on the datasheet information
        dis_acdrv_msg = "ACDRV disabled" if (data >> 7) & 0x01 else "ACDRV enabled (default)"
        en_otg_msg = "OTG enabled" if (data >> 6) & 0x01 else "OTG disabled (default)"
        pfm_otg_dis_msg = "PFM in OTG mode disabled" if (data >> 5) & 0x01 else "PFM in OTG mode enabled (default)"
        pfm_fwd_dis_msg = "PFM in forward mode disabled" if (data >> 4) & 0x01 else "PFM in forward mode enabled (default)"
        wkup_dly_msg = "15ms wake-up delay" if (data >> 3) & 0x01 else "0ms wake-up delay (default)"
        dis_ldo_msg = "BATFET LDO disabled" if (data >> 2) & 0x01 else "BATFET LDO enabled (default)"
        dis_otg_ooa_msg = "OOA in OTG mode disabled" if (data >> 1) & 0x01 else "OOA in OTG mode enabled (default)"
        dis_fwd_ooa_msg = "OOA in forward mode disabled" if data & 0x01 else "OOA in forward mode enabled (default)"
        
        # Combine messages
        return f"DIS_ACDRV: {dis_acdrv_msg}, EN_OTG: {en_otg_msg}, PFM_OTG_DIS: {pfm_otg_dis_msg}, PFM_FWD_DIS: {pfm_fwd_dis_msg}, WKUP_DLY: {wkup_dly_msg}, DIS_LDO: {dis_ldo_msg}, DIS_OTG_OOA: {dis_otg_ooa_msg}, DIS_FWD_OOA: {dis_fwd_ooa_msg}"

    ####################

    if reg_addr == 0x11:  # Conditional for register at 0x11
        # Interpret the FORCE_INDET bit (bit 7)
        force_indet_msg = "Force NDETP detection" if (data >> 7) & 0x01 else "Do not force NDETP detection (default)"
        
        # Interpret the AUTO_INDET_EN bit (bit 6)
        auto_indet_en_msg = "Auto NDETP detection enable" if (data >> 6) & 0x01 else "Auto NDETP detection disable (default)"
        
        # Interpret the EN_12V bit (bit 5)
        en_12v_msg = "Enable 12V mode in NVDCP" if (data >> 5) & 0x01 else "Disable 12V mode in NVDCP (default)"
        
        # Interpret the EN_9V bit (bit 4)
        en_9v_msg = "Enable 9V mode in NVDCP" if (data >> 4) & 0x01 else "Disable 9V mode in NVDCP (default)"
        
        # Interpret the NVDCP_EN bit (bit 3)
        nvdcp_en_msg = "NVDCP handshake enable" if (data >> 3) & 0x01 else "NVDCP handshake disable (default)"
        
        # Interpret the SDRV_CTRL bits (bits 2-1)
        sdrv_ctrl = (data >> 1) & 0x03
        sdrv_ctrl_msg = {
            0: "REE",
            1: "Shutdown Mode",
            2: "Ship Mode",
            3: "System Power Reset"
        }.get(sdrv_ctrl, "Unknown SDRV_CTRL setting")
        
        # Interpret the SDRV_DLY bit (bit 0)
        sdrv_dly_msg = "Add 10s delay time" if data & 0x01 else "Do not add 10s delay time (default)"
        
        # Combine messages
        return f"FORCE_INDET: {force_indet_msg}, AUTO_INDET_EN: {auto_indet_en_msg}, EN_12V: {en_12v_msg}, EN_9V: {en_9v_msg}, NVDCP_EN: {nvdcp_en_msg}, SDRV_CTRL: {sdrv_ctrl_msg}, SDRV_DLY: {sdrv_dly_msg}"

    ###################

    if reg_addr == 0x10:  # Conditional for register at 0x10
        # Interpret the VAC_OVP bits (bits 5-4)
        vac_ovp = (data >> 4) & 0x03
        vac_ovp_msg = {
            0: "16V (default)",
            1: "22V",
            2: "12V",
            3: "7V"
        }.get(vac_ovp, "Unknown VAC_OVP setting")
        
        # Interpret the WD_RST bit (bit 3)
        wd_rst_msg = "Reset" if (data >> 3) & 0x01 else "Normal (default)"
        
        # Interpret the WATCHDOG_2 bits (bits 2-0)
        watchdog_2 = data & 0x07
        watchdog_2_msg = {
            0: "Disable",
            1: "0.5s",
            2: "1s",
            3: "2s",
            4: "20s",
            5: "40s (default)",
            6: "80s",
            7: "160s"
        }.get(watchdog_2, "Unknown WATCHDOG_2 setting")
        
        # Combine messages
        return f"VAC_OVP: {vac_ovp_msg}, WD_RST: {wd_rst_msg}, WATCHDOG_2: {watchdog_2_msg}"

    ####################

    if reg_addr == 0x0F:  # Conditional for register at 0x0F
        # Interpret the EN_AUTO_IBATDIS bit (bit 7)
        en_auto_ibatdis_msg = "Enable auto battery discharging" if (data >> 7) & 0x01 else "Disable auto battery discharging (default)"
        
        # Interpret the FORCE_IBATDIS bit (bit 6)
        force_ibatdis_msg = "Force battery discharging current" if (data >> 6) & 0x01 else "Do not force battery discharging current (default)"
        
        # Interpret the EN_CHG bit (bit 5)
        en_chg_msg = "Charger enabled" if (data >> 5) & 0x01 else "Charger disabled (default)"
        
        # Interpret the EN_ICO bit (bit 4)
        en_ico_msg = "Input Current Optimizer (ICO) enabled" if (data >> 4) & 0x01 else "Input Current Optimizer (ICO) disabled (default)"
        
        # Interpret the FORCE_ICO bit (bit 3)
        force_ico_msg = "Force start ICO" if (data >> 3) & 0x01 else "Do not force start ICO (default)"
        
        # Interpret the EN_HIZ bit (bit 2)
        en_hiz_msg = "Enable HIZ mode" if (data >> 2) & 0x01 else "Disable HIZ mode (default)"
        
        # Interpret the EN_TERM bit (bit 1)
        en_term_msg = "Enable termination" if (data >> 1) & 0x01 else "Disable termination (default)"
        
        # Bit 0 is reserved
        
        # Combine messages
        return f"EN_AUTO_IBATDIS: {en_auto_ibatdis_msg}, FORCE_IBATDIS: {force_ibatdis_msg}, EN_CHG: {en_chg_msg}, EN_ICO: {en_ico_msg}, FORCE_ICO: {force_ico_msg}, EN_HIZ: {en_hiz_msg}, EN_TERM: {en_term_msg}"

    ####################

    if reg_addr == 0x0E:  # Conditional for register at 0x0E
        # Interpret the TOP_OFF_TIMER bits (bits 7-6)
        top_off_timer = (data >> 6) & 0x03
        top_off_timer_msg = {
            0: "Disabled",
            1: "15 mins",
            2: "30 mins",
            3: "45 mins"
        }.get(top_off_timer, "Unknown TOP_OFF_TIMER setting")
        
        # Interpret the EN_TRICHG_TIMER bit (bit 5)
        en_trichg_timer_msg = "Trickle charge timer enabled" if (data >> 5) & 0x01 else "Trickle charge timer disabled (default)"
        
        # Interpret the EN_PRECHG_TIMER bit (bit 4)
        en_prechg_timer_msg = "Pre-charge timer enabled" if (data >> 4) & 0x01 else "Pre-charge timer disabled (default)"
        
        # Interpret the EN_CHG_TIMER bit (bit 3)
        en_chg_timer_msg = "Fast charge timer enabled" if (data >> 3) & 0x01 else "Fast charge timer disabled (default)"
        
        # Interpret the CHG_TIMER bits (bits 2-1)
        chg_timer = (data >> 1) & 0x03
        chg_timer_msg = {
            0: "5 hrs",
            1: "8 hrs",
            2: "12 hrs (default)",
            3: "20 hrs"
        }.get(chg_timer, "Unknown CHG_TIMER setting")
        
        # Interpret the TMR2X_EN bit (bit 0)
        tmr2x_en_msg = "Timer slowed by 2x during DPM or thermal regulation" if data & 0x01 else "Timer not slowed (default)"
        
        # Combine messages
        return f"TOP_OFF_TIMER: {top_off_timer_msg}, EN_TRICHG_TIMER: {en_trichg_timer_msg}, EN_PRECHG_TIMER: {en_prechg_timer_msg}, EN_CHG_TIMER: {en_chg_timer_msg}, CHG_TIMER: {chg_timer_msg}, TMR2X_EN: {tmr2x_en_msg}"

    ###################

    if reg_addr == 0x0D:  # Conditional for register at 0x0D
        # Interpret the PRECHG_TMR bit (bit 7)
        prechg_tmr_msg = "0.5 hrs pre-charge safety timer" if (data >> 7) & 0x01 else "2 hrs pre-charge safety timer (default)"
        
        # Interpret the IOTG_6_0 bits (bits 6-0)
        # The IOTG current limit value is determined by the bits' decimal value times the step size (40mA)
        iotg_6_0_value = data & 0x7F  # Mask all but the 7 bits for IOTG
        iotg_6_0_current_limit = iotg_6_0_value * 40  # Calculate the current limit
        iotg_6_0_msg = f"{iotg_6_0_current_limit}mA OTG current limit"
        
        # Combine messages
        return f"PRECHG_TMR: {prechg_tmr_msg}, IOTG_6_0: {iotg_6_0_msg}"

    ###################

    if reg_addr == 0x0B:  # Conditional for register at 0x0B
        # Extract the 11-bit VOTG value (bits 10-0)
        votg_value = data & 0x7FF  # Mask all but the 11 bits for VOTG
        # Calculate the regulation voltage
        votg_regulation_voltage = 2800 + (votg_value * 10)  # Add the offset to the value obtained from the bits
        votg_msg = f"{votg_regulation_voltage}mV OTG regulation voltage"
        
        # Combine messages
        return f"VOTG: {votg_msg}"

    ###################

    if reg_addr == 0x0A:  # Conditional for register at 0x0A
        # Extract the CELL bits (bits 7-6), if applicable
        cell_value = (data >> 6) & 0x03
        cell_msg = f"{cell_value}-cell battery"  # Placeholder message, actual message depends on datasheet details
        
        # Extract the TREC bits (bits 5-4)
        trec_value = (data >> 4) & 0x03
        trec_msg = {
            0: "64ms",
            1: "256ms",
            2: "1024ms (default)",
            3: "2048ms"
        }.get(trec_value, "Unknown TREC setting")
        
        # Extract the VRECHG bits (bits 3-0)
        vrechg_value = data & 0x0F
        vrechg_voltage = 50 + (vrechg_value * 50)  # Calculate the voltage offset
        vrechg_msg = f"{vrechg_voltage}mV below VREG"
        
        # Combine messages
        return f"CELL: {cell_msg}, TREC: {trec_msg}, VRECHG: {vrechg_msg}"

    ####################

    if reg_addr == 0x09:  # Conditional for register at 0x09
        # Interpret the STOP_WD_CHG bit (bit 5)
        stop_wd_chg_msg = "WD timer expiration sets EN_CHG=0" if (data >> 5) & 0x01 else "WD timer expiration keeps existing EN_CHG setting (default)"
        
        # Interpret the ITERM bits (bits 4-0)
        # The ITERM current limit value is determined by the bits' decimal value times the step size (40mA)
        iterm_value = data & 0x1F  # Mask all but the 5 bits for ITERM
        iterm_current_limit = iterm_value * 40  # Calculate the current limit
        iterm_msg = f"{iterm_current_limit}mA termination current"
        
        # Combine messages
        return f"STOP_WD_CHG: {stop_wd_chg_msg}, ITERM: {iterm_msg}"

    ###################

    if reg_addr == 0x08:  # Conditional for register at 0x08
        # Interpret the VBAT_LOVW bits (bits 7-6)
        vbat_lowv = (data >> 6) & 0x03
        vbat_lowv_msg = {
            0: "15% VREG",
            1: "62.2% VREG",
            2: "66.7% VREG",
            3: "71.4% VREG"
        }.get(vbat_lowv, "Unknown VBAT_LOWV setting")
        
        # Interpret the IPRECHG bits (bits 5-0)
        # The IPRECHG current limit value is determined by the bits' decimal value times the step size (40mA)
        iprechg_value = data & 0x3F  # Mask all but the 6 bits for IPRECHG
        iprechg_current_limit = iprechg_value * 40  # Calculate the current limit
        iprechg_msg = f"{iprechg_current_limit}mA precharge current limit"
        
        # Combine messages
        return f"VBAT_LOWV: {vbat_lowv_msg}, IPRECHG: {iprechg_msg}"

    ###################

    if reg_addr == 0x06:  # Conditional for register at 0x06
        # The IINLIM value is determined by the 8-bit value multiplied by the step size (10mA)
        iinlim_value = data & 0xFF  # Extract the 8-bit value
        iinlim_current_limit = iinlim_value * 10  # Calculate the current limit (step size is 10mA)
        iinlim_msg = f"{iinlim_current_limit}mA input current limit"

    ####################

    if reg_addr == 0x05:  # Conditional for register at 0x05
        # The VINDPM value is determined by the 8-bit value multiplied by the step size (100mV)
        vindpm_value = data & 0xFF  # Extract the 8-bit value
        vindpm_voltage_limit = 3600 + (vindpm_value * 100)  # Calculate the voltage limit (base is 3600mV)
        vindpm_msg = f"{vindpm_voltage_limit}mV input voltage limit"
        
        # Combine messages
        return f"VINDPM: {vindpm_msg}"

    ####################

    if reg_addr == 0x03:  # Conditional for register at 0x03
        # The ICHG current limit value is determined by the 8-bit value multiplied by the step size (10mA)
        ichg_value = data & 0xFF  # Extract the 8-bit value
        ichg_current_limit = ichg_value * 10  # Calculate the current limit (step size is 10mA)
        ichg_msg = f"{ichg_current_limit}mA charge current limit"
        
        # Combine messages
        return f"ICHG: {ichg_msg}"

    ####################

    if reg_addr == 0x01:  # Conditional for register at 0x01
        
        # The VREG value is determined by the 11-bit value multiplied by the step size (10mV)
        vreg_value = data & 0x7FF  # Extract the 11-bit value
        vreg_voltage_limit = vreg_value * 10  # Calculate the voltage limit (step size is 10mV)
        vreg_msg = f"{vreg_voltage_limit}mV charge voltage limit"
        
        # Combine messages
        return f"VREG: {vreg_msg}"

    ####################

    if reg_addr == 0x00:  # Conditional for register at 0x00
        # The VYSMIN value is determined by the 6-bit value multiplied by the step size (250mV)
        vysmin_value = data & 0x3F  # Extract the 6-bit value
        vysmin_value = vysmin_value
        vysmin_voltage = (2500 + (vysmin_value * 250))  # Calculate the voltage (base is 2500mV)
        vysmin_msg = f"{vysmin_voltage}mV minimal system voltage"
        
        # Combine messages
        return f"VYSMIN: {vysmin_msg}"

    ###################
    return f"{data:02b}"  # Return data as a binary string

def display_data(reg_info,reg_addr):
    reg_name, length = reg_info
    data = read_register_data(reg_addr, length)
    
    # Assuming interpret_register_data returns a string description
    description = interpret_register_data(reg_addr, data)
    binary_value = f'{data:02b}' if isinstance(data, int) else ' '.join([f'{byte:02b}' for byte in data])

    # Use Streamlit to display each register's data
    st.write(f"**{reg_name}**")
    st.text(f"Binary Value: {binary_value}")
    st.text(f"Description: {description}")
    st.write("---")  # Add a separator

def main():
    st.set_page_config(layout="wide")
    st.title("I2C Register Data Viewer")
    col1, col2, col3, col4 = st.columns((2,1,1,1))

    # Create a button in Streamlit to refresh the data
    if st.button("Refresh Data"):
        # This forces Streamlit to rerun the script, refreshing the data

        # Display data in a Streamlit table
        for reg_addr, reg_info in registers.items():
            if reg_addr >= 0x00 and reg_addr <= 0x08:
                with col1:
                    display_data(reg_info,reg_addr)
            elif reg_addr > 0x08 and reg_addr <= 0x0F:
                with col2:
                    display_data(reg_info,reg_addr)
            elif reg_addr > 0x0F and reg_addr <= 0x18:
                with col3:
                    display_data(reg_info,reg_addr) 
            else:
                with col4:
                    display_data(reg_info,reg_addr)
            reg_name, length = reg_info
            data = read_register_data(reg_addr, length)
            
            # Assuming interpret_register_data returns a string description
            description = interpret_register_data(reg_addr, data)
            binary_value = f'{data:02b}' if isinstance(data, int) else ' '.join([f'{byte:02b}' for byte in data])

            # Use Streamlit to display each register's data
            st.write(f"**{reg_name}**")
            st.text(f"Binary Value: {binary_value}")
            st.text(f"Description: {description}")
            st.write("---")  # Add a separator

if __name__ == "__main__":
    main()