import pygame
import smbus

# Initialize I2C bus
bus = smbus.SMBus(1)
device_address = 0x6B  # Replace with your actual device address

# Define registers and their byte lengths
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
            data = bus.read_byte_data(device_address, reg_addr)
        else:
            data = bus.read_i2c_block_data(device_address, reg_addr, length)
        return data
    except Exception as e:
        print(f"Error reading register {reg_addr}: {e}")
        return None

def display_data(screen, font):
    """Display I2C data on the Pygame screen."""
    screen.fill((0, 0, 0))  # Clear screen with black

    y = 10  # Initial y position for text
    for reg_addr, reg_info in registers.items():
        reg_name, length = reg_info
        data = read_register_data(reg_addr, length)
        if data is not None:
            if isinstance(data, list):
                data_str = ' '.join([f"{byte:02x}" for byte in data])
            else:
                data_str = f"{data:02x}"
            text_surface = font.render(f"{reg_name} (0x{reg_addr:02x}): {data_str}", True, (255, 255, 255))
            screen.blit(text_surface, (10, y))
            y += 30  # Move to the next line

def main():
    pygame.init()

    # Set up display
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("I2C Register Monitor")

    # Set up font
    font = pygame.font.SysFont('Arial', 24)

    # Create a clock object to manage the refresh rate
    clock = pygame.time.Clock()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        display_data(screen, font)
        pygame.display.flip()  # Update the screen

        clock.tick(2)  # Limit refresh to 2 frames per second

    pygame.quit()

if __name__ == "__main__":
    main()
