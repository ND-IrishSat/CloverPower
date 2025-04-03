# -*- coding: utf-8 -*-
import time
from flask import Flask, jsonify, render_template, request
import smbus

app = Flask(__name__)

# I2C bus (usually 1 for Raspberry Pi)
I2C_BUS = 1
bus = smbus.SMBus(I2C_BUS)

# Device addresses (displayed in hexadecimal)
PAC1934_ADDR1 = 0x10
PAC1934_ADDR2 = 0x17
BQ25672_ADDR = 0x6B
PCA9557_ADDR = 0x18

# ----- PAC1934 Settings -----
PAC1934_REFRESH_REG = 0x00    # Refresh command
PAC1934_VBUS_START   = 0x07    # VBUS1 register start
PAC1934_VSENSE_START = 0x0B    # VSENSE1 register start
PAC1934_POWER_START  = 0x17    # VPOWER1 register start
PAC1934_CHANNELS     = 4
RSENSE = 0.05  # 50 milliohm sense resistor

# ----- BQ25672 Settings -----
# ADC registers are 16-bit
BQ25672_ADC_REGS = [0x31, 0x33, 0x35, 0x37, 0x39, 0x3B, 0x3D, 0x41, 0x43]
# Conversion parameters (fixed offset, step size, unit) from datasheet
bq25672_adc_params = {
    0x31: {"name": "Bus Current (IBUS)", "offset": 0, "step": 0.001, "unit": "A"},
    0x33: {"name": "Battery Current (IBAT)", "offset": 0, "step": 0.001, "unit": "A"},
    0x35: {"name": "Bus Voltage (VBUS)",  "offset": 0, "step": 0.001, "unit": "V"},
    0x37: {"name": "VAC1",  "offset": 0, "step": 0.001, "unit": "V"},
    0x39: {"name": "VAC2",   "offset": 0, "step": 0.001,    "unit": "V"},
    0x3B: {"name": "Battery Voltage (VBAT)", "offset": 0, "step": 0.001,   "unit": "V"},
    0x3D: {"name": "System Voltage (VSYS)",  "offset": 0, "step": 0.001,   "unit": "V"},
    # 0x3F: {"name": "VOTG", "offset": 0, "step": 4.88e-3, "unit": "V"},
    0x41: {"name": "TS", "offset": 0, "step": 0.0976563,   "unit": "%"},
    0x43: {"name": "TDIE","offset": 0, "step": 0.5,      "unit": "K"}  # Changed from "deg C" to "K"
}
# Additional registers:
# MPPT: register 0x15, bit 0; ICO: register 0x0F, bit 4; Charge Status: register 0x1C, bits 7-5.
charge_status_map = {
    0: "Not Charging",
    1: "Trickle Charge",
    2: "Pre Charge",
    3: "Fast Charge",
    4: "Taper Charge",
    5: "Reserved",
    6: "Top-off",
    7: "Charge Done"
}

# ----- PCA9557 Settings -----
PCA9557_INPUT_REG    = 0x00
PCA9557_OUTPUT_REG   = 0x01
PCA9557_POLARITY_REG = 0x02
PCA9557_CONFIG_REG   = 0x03

# ---------- I2C Helper Functions ----------
def i2c_read_reg(dev_addr, reg):
    try:
        return bus.read_byte_data(dev_addr, reg)
    except Exception as e:
        return f"ERR: {e}"

def i2c_write_reg(dev_addr, reg, value):
    try:
        bus.write_byte_data(dev_addr, reg, value)
        return "Write OK"
    except Exception as e:
        return f"ERR: {e}"

# ---------- PAC1934 Functions ----------
def pac1934_refresh(dev_addr):
    bus.write_byte(dev_addr, PAC1934_REFRESH_REG)
    time.sleep(0.01)

def read_pac1934_voltage(dev_addr, channel):
    reg = PAC1934_VBUS_START + (channel - 1)
    data = bus.read_i2c_block_data(dev_addr, reg, 2)
    return (data[0] << 8 | data[1]) * 32.0 / 65536

def read_pac1934_current(dev_addr, channel):
    reg = PAC1934_VSENSE_START + (channel - 1)
    data = bus.read_i2c_block_data(dev_addr, reg, 2)
    vsense = (data[0] << 8 | data[1]) * 100.0 / 65536
    return (vsense / 1000) / RSENSE * 1000

def read_pac1934_power(dev_addr, channel):
    reg = PAC1934_POWER_START + (channel - 1)
    data = bus.read_i2c_block_data(dev_addr, reg, 4)
    raw_power = (data[0] << 24) | (data[1] << 16) | (data[2] << 8) | data[3]
    return (raw_power * 32.0 * 100.0) / (65536 * 1000 * 65536 * RSENSE)

def get_pac1934_data(dev_addr):
    pac1934_refresh(dev_addr)
    if dev_addr == PAC1934_ADDR1:
        labels = {1: "SDR", 2: "Payload", 3: "Flight Comp", 4: "Motor"}
    elif dev_addr == PAC1934_ADDR2:
        labels = {1: "SYS_IN", 2: "Heat", 3: "Unused", 4: "Unused"}
    else:
        labels = {ch: f"Ch{ch}" for ch in range(1, PAC1934_CHANNELS + 1)}
    channels = []
    for ch in range(1, PAC1934_CHANNELS + 1):
        channels.append({
            "channel": ch,
            "label": labels.get(ch, f"Ch{ch}"),
            "voltage": round(read_pac1934_voltage(dev_addr, ch), 3),
            "current": round(read_pac1934_current(dev_addr, ch), 3),
            "power": round(read_pac1934_power(dev_addr, ch), 3)
        })
    return {"address": f"0x{dev_addr:02X}", "channels": channels}

# ---------- BQ25672 Functions ----------
def read_bq25672_reg(dev_addr, reg, length=2):
    data = bus.read_i2c_block_data(dev_addr, reg, length)
    if length == 2:
        return (data[0] << 8) | data[1]
    return data

def twos_comp(val, bits):
    """compute the 2's complement of int value val"""
    if (val & (1 << (bits - 1))) != 0: # if sign bit is set e.g., 8bit: 128-255
        val = val - (1 << bits)        # compute negative value
    return val    

def get_bq25672_data():
    regs = []
    for reg in BQ25672_ADC_REGS:
        raw = read_bq25672_reg(BQ25672_ADDR, reg)
        bin_str = format(raw, '016b')
        raw = twos_comp(raw, 16) # convert to negative when needed
        params = bq25672_adc_params.get(reg, {"name": "Unknown", "offset": 0, "step": 1, "unit": ""})
        actual = (raw - params["offset"]) * params["step"]
        regs.append({
            "reg": f"0x{reg:02X}",
            "name": params["name"],
            "binary": bin_str,
            "value": round(actual, 3),
            "unit": params["unit"]
        })
    # Additional indicators:
    # MPPT: register 0x15, bit 0
    mppt_reg = i2c_read_reg(BQ25672_ADDR, 0x15)
    mppt = "On" if isinstance(mppt_reg, int) and (mppt_reg & 0x01) else "Off"
    # ICO: register 0x0F, bit 4
    ico_reg = i2c_read_reg(BQ25672_ADDR, 0x0F)
    ico = "On" if isinstance(ico_reg, int) and ((ico_reg >> 4) & 0x01) else "Off"
    # Charge Status: register 0x1C, bits 7-5
    charge_reg = i2c_read_reg(BQ25672_ADDR, 0x1C)
    if isinstance(charge_reg, int):
        charge_bits = (charge_reg >> 5) & 0x07
        charge_status = charge_status_map.get(charge_bits, "Unknown")
    else:
        charge_status = "ERR"
    extra = {
        "mppt": mppt,
        "ico": ico,
        "charge_status": charge_status
    }
    return {"address": f"0x{BQ25672_ADDR:02X}", "registers": regs, "extra": extra}

# ---------- PCA9557 Functions ----------
def get_pca9557_data():
    config = i2c_read_reg(PCA9557_ADDR, PCA9557_CONFIG_REG)
    output = i2c_read_reg(PCA9557_ADDR, PCA9557_OUTPUT_REG)
    pins = []
    # Only consider pins 0-4 with custom labels
    if isinstance(config, int) and isinstance(output, int):
        label_map = {
            0: "Flight Computer",
            1: "Payload",
            2: "Heat",
            3: "Motor",
            4: "SDR"
        }
        for pin in range(5):
            mode = (config >> pin) & 0x01
            status = "HIZ" if mode else ("High" if ((output >> pin) & 0x01) else "Low")
            pins.append({"pin": label_map.get(pin, f"P{pin}"), "status": status})
    return {"address": f"0x{PCA9557_ADDR:02X}", "pins": pins}

# ---------- New BQ25672 Button Endpoints ----------
@app.route("/mppt_enable", methods=["POST"])
def mppt_enable():
    try:
        reg_val = bus.read_byte_data(BQ25672_ADDR, 0x15)
        new_val = reg_val | 0x01  # set bit 0 to 1
        bus.write_byte_data(BQ25672_ADDR, 0x15, new_val)
        return jsonify({"status": "success", "message": "MPPT enabled"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route("/mppt_disable", methods=["POST"])
def mppt_disable():
    try:
        reg_val = bus.read_byte_data(BQ25672_ADDR, 0x15)
        new_val = reg_val & ~0x01  # clear bit 0
        bus.write_byte_data(BQ25672_ADDR, 0x15, new_val)
        return jsonify({"status": "success", "message": "MPPT disabled"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route("/ico_enable", methods=["POST"])
def ico_enable():
    try:
        reg_val = bus.read_byte_data(BQ25672_ADDR, 0x0F)
        new_val = reg_val | 0x10  # set bit 4
        bus.write_byte_data(BQ25672_ADDR, 0x0F, new_val)
        return jsonify({"status": "success", "message": "ICO enabled"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route("/ico_disable", methods=["POST"])
def ico_disable():
    try:
        reg_val = bus.read_byte_data(BQ25672_ADDR, 0x0F)
        new_val = reg_val & ~0x10  # clear bit 4
        bus.write_byte_data(BQ25672_ADDR, 0x0F, new_val)
        return jsonify({"status": "success", "message": "ICO disabled"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route("/adc_enable", methods=["POST"])
def adc_enable():
    try:
        # Set bit 7 of register 0x2E to 1 to enable ADC
        reg_val = bus.read_byte_data(BQ25672_ADDR, 0x2E)
        new_val = reg_val | 0b10000000
        bus.write_byte_data(BQ25672_ADDR, 0x2E, new_val)
        # Set bit 5 of register 0x14 to 1 to enable IBAT sensing
        reg_val = bus.read_byte_data(BQ25672_ADDR, 0x14)
        new_val = reg_val | 0b00100000
        bus.write_byte_data(BQ25672_ADDR, 0x14, new_val)
        return jsonify({"status": "success", "message": "ADC enabled"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route("/adc_disable", methods=["POST"])
def adc_disable():
    try:
        reg_val = bus.read_byte_data(BQ25672_ADDR, 0x2E)
        new_val = reg_val & ~0x80  # clear bit 7
        bus.write_byte_data(BQ25672_ADDR, 0x2E, new_val)
        return jsonify({"status": "success", "message": "ADC disabled"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

# ---------- New BQ25672 Reset and Watchdog Disable Endpoints ----------
@app.route("/bq25672_reset", methods=["POST"])
def bq25672_reset():
    try:
        # Set bit 6 of register 0x09 to 1
        reg_val = bus.read_byte_data(BQ25672_ADDR, 0x09)
        new_val = reg_val | 0b01000000  # Set bit 6
        bus.write_byte_data(BQ25672_ADDR, 0x09, new_val)
        return jsonify({"status": "success", "message": "Reset triggered"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route("/bq25672_watchdog_disable", methods=["POST"])
def bq25672_watchdog_disable():
    try:
        # Set bits 0-2 of register 0x10 to 0
        reg_val = bus.read_byte_data(BQ25672_ADDR, 0x10)
        new_val = reg_val & 0b11111000  # Clear bits 0-2
        bus.write_byte_data(BQ25672_ADDR, 0x10, new_val)
        return jsonify({"status": "success", "message": "Watchdog disabled"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

# ---------- PCA9557 Control Endpoints ----------
@app.route("/pca9557_set_high", methods=["POST"])
def pca9557_set_high():
    try:
        pin = int(request.form.get("pin"))
        # Set the pin's bit in register 0x03 to 0 (output mode)
        config_reg_val = bus.read_byte_data(PCA9557_ADDR, PCA9557_CONFIG_REG)
        new_config_val = config_reg_val & ~(1 << pin)  # Clear the pin's bit
        bus.write_byte_data(PCA9557_ADDR, PCA9557_CONFIG_REG, new_config_val)
        # Set the pin's bit in register 0x01 to 1 (High)
        output_reg_val = bus.read_byte_data(PCA9557_ADDR, PCA9557_OUTPUT_REG)
        new_output_val = output_reg_val | (1 << pin)  # Set the pin's bit to 1
        bus.write_byte_data(PCA9557_ADDR, PCA9557_OUTPUT_REG, new_output_val)
        return jsonify({"status": "success", "message": f"Pin {pin} set to High"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route("/pca9557_set_low", methods=["POST"])
def pca9557_set_low():
    try:
        pin = int(request.form.get("pin"))
        # Set the pin's bit in register 0x03 to 0 (output mode)
        config_reg_val = bus.read_byte_data(PCA9557_ADDR, PCA9557_CONFIG_REG)
        new_config_val = config_reg_val & ~(1 << pin)  # Clear the pin's bit
        bus.write_byte_data(PCA9557_ADDR, PCA9557_CONFIG_REG, new_config_val)
        # Set the pin's bit in register 0x01 to 0 (Low)
        output_reg_val = bus.read_byte_data(PCA9557_ADDR, PCA9557_OUTPUT_REG)
        new_output_val = output_reg_val & ~(1 << pin)  # Clear the pin's bit
        bus.write_byte_data(PCA9557_ADDR, PCA9557_OUTPUT_REG, new_output_val)
        return jsonify({"status": "success", "message": f"Pin {pin} set to Low"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route("/pca9557_set_hiz", methods=["POST"])
def pca9557_set_hiz():
    try:
        pin = int(request.form.get("pin"))
        # Set the pin's bit in register 0x03 to 1 (HIZ mode)
        config_reg_val = bus.read_byte_data(PCA9557_ADDR, PCA9557_CONFIG_REG)
        new_config_val = config_reg_val | (1 << pin)  # Set the pin's bit to 1
        bus.write_byte_data(PCA9557_ADDR, PCA9557_CONFIG_REG, new_config_val)
        return jsonify({"status": "success", "message": f"Pin {pin} set to HIZ"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

# ---------- New HVDCP Control Endpoints ----------
@app.route("/enable_hvdcp", methods=["POST"])
def enable_hvdcp():
    try:
        # Set bits 3, 4, and 5 of register 0x11 to 1
        reg_val = bus.read_byte_data(BQ25672_ADDR, 0x11)
        new_val = reg_val | 0b00111000  # Set bits 3, 4, and 5
        bus.write_byte_data(BQ25672_ADDR, 0x11, new_val)
        return jsonify({"status": "success", "message": "HVDCP enabled"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route("/disable_hvdcp", methods=["POST"])
def disable_hvdcp():
    try:
        # Set bits 3, 4, and 5 of register 0x11 to 0
        reg_val = bus.read_byte_data(BQ25672_ADDR, 0x11)
        new_val = reg_val & ~0b00111000  # Clear bits 3, 4, and 5
        bus.write_byte_data(BQ25672_ADDR, 0x11, new_val)
        return jsonify({"status": "success", "message": "HVDCP disabled"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route("/set_9v", methods=["POST"])
def set_9v():
    try:
        # Set bit 4 to 1 and bit 5 to 0 in register 0x11
        reg_val = bus.read_byte_data(BQ25672_ADDR, 0x11)
        new_val = (reg_val | 0b00010000) & ~0b00100000  # Set bit 4, clear bit 5
        bus.write_byte_data(BQ25672_ADDR, 0x11, new_val)
        return jsonify({"status": "success", "message": "Set to 9V"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route("/set_12v", methods=["POST"])
def set_12v():
    try:
        # Set bit 5 to 1 and bit 4 to 0 in register 0x11
        reg_val = bus.read_byte_data(BQ25672_ADDR, 0x11)
        new_val = (reg_val | 0b00100000) & ~0b00010000  # Set bit 5, clear bit 4
        bus.write_byte_data(BQ25672_ADDR, 0x11, new_val)
        return jsonify({"status": "success", "message": "Set to 12V"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})
# ---------- Flask Routes ----------
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/data")
def data():
    data = {
        "pac1934_0x10": get_pac1934_data(PAC1934_ADDR1),
        "pac1934_0x17": get_pac1934_data(PAC1934_ADDR2),
        "bq25672": get_bq25672_data(),
        "pca9557": get_pca9557_data()
    }
    return jsonify(data)

@app.route("/custom_read", methods=["POST"])
def custom_read():
    try:
        dev_addr = int(request.form.get("dev_addr", ""), 16)
        reg = int(request.form.get("reg", ""), 16)
        value = i2c_read_reg(dev_addr, reg)
        if isinstance(value, int):
            bin_value = format(value, '08b')
            return jsonify({"status": "success", "value": bin_value})
        else:
            return jsonify({"status": "error", "message": value})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route("/custom_write", methods=["POST"])
def custom_write():
    try:
        dev_addr = int(request.form.get("dev_addr", ""), 16)
        reg = int(request.form.get("reg", ""), 16)
        value = int(request.form.get("value", ""), 2)
        status = i2c_write_reg(dev_addr, reg, value)
        return jsonify({"status": "success", "message": status})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)