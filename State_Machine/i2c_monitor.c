#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <linux/i2c-dev.h>
#include <sys/ioctl.h>
#include <curses.h>

//install the libraries:
// sudo apt-get install libi2c-dev libncurses5-dev
//compile the code
// gcc -o i2c_monitor i2c_monitor.c -lncurses
//run the code
// sudo ./i2c_monitor

#define DEVICE_ADDRESS 0x6B  // Replace with your actual device address

typedef struct {
    const char *name;
    int length;
} RegisterInfo;

RegisterInfo registers[] = {
    {"REG00_Minimal_System_Voltage", 1},
    {"REG01_Charge_Voltage_Limit", 2},
    {"REG03_Charge_Current_Limit", 2},
    {"REG05_Input_Voltage_Limit", 1},
    {"REG06_Input_Current_Limit", 2},
    {"REG08_Precharge_Control", 1},
    {"REG09_Termination_Control", 1},
    {"REG0A_Re-charge_Control", 1},
    {"REG0B_VOTG_regulation", 2},
    {"REG0D_IOTG_regulation", 1},
    {"REG0E_Timer_Control", 1},
    {"REG0F_Charger_Control_0", 1},
    {"REG10_Charger_Control_1", 1},
    {"REG11_Charger_Control_2", 1},
    {"REG12_Charger_Control_3", 1},
    {"REG13_Charger_Control_4", 1},
    {"REG14_Charger_Control_5", 1},
    {"REG15_MPPT_Control", 1},
    {"REG16_Temperature_Control", 1},
    {"REG17_NTC_Control_0", 1},
    {"REG18_NTC_Control_1", 1},
    {"REG19_ICO_Current_Limit", 2},
    {"REG1B_Charger_Status_0", 1},
    {"REG1C_Charger_Status_1", 1},
    {"REG1D_Charger_Status_2", 1},
    {"REG1E_Charger_Status_3", 1},
    {"REG1F_Charger_Status_4", 1},
    {"REG20_FAULT_Status_0", 1},
    {"REG21_FAULT_Status_1", 1},
    {"REG22_Charger_Flag_0", 1},
    {"REG23_Charger_Flag_1", 1},
    {"REG24_Charger_Flag_2", 1},
    {"REG25_Charger_Flag_3", 1},
    {"REG26_FAULT_Flag_0", 1},
    {"REG27_FAULT_Flag_1", 1},
    {"REG28_Charger_Mask_0", 1},
    {"REG29_Charger_Mask_1", 1},
    {"REG2A_Charger_Mask_2", 1},
    {"REG2B_Charger_Mask_3", 1},
    {"REG2C_FAULT_Mask_0", 1},
    {"REG2D_FAULT_Mask_1", 1},
    {"REG2E_ADC_Control", 1},
    {"REG2F_ADC_Function_Disable_0", 1},
    {"REG30_ADC_Function_Disable_1", 1},
    {"REG31_IBUS_ADC", 2},
    {"REG33_IBAT_ADC", 2},
    {"REG35_VBUS_ADC", 2},
    {"REG37_VAC1_ADC", 2},
    {"REG39_VAC2_ADC", 2},
    {"REG3B_VBAT_ADC", 2},
    {"REG3D_VSYS_ADC", 2},
    {"REG3F_TS_ADC", 2},
    {"REG41_TDIE_ADC", 2},
    {"REG43_D+_ADC", 2},
    {"REG45_D-_ADC", 2},
    {"REG47_DPDM_Driver", 1},
    {"REG48_Part_Information", 1},
};

int i2c_fd;

int read_register_data(int reg_addr, int length, unsigned char *data) {
    if (ioctl(i2c_fd, I2C_SLAVE, DEVICE_ADDRESS) < 0) {
        perror("Failed to acquire bus access and/or talk to slave.\n");
        return -1;
    }

    // Write the register address
    if (write(i2c_fd, &reg_addr, 1) != 1) {
        perror("Failed to write to the i2c bus.\n");
        return -1;
    }

    // Read data
    if (read(i2c_fd, data, length) != length) {
        perror("Failed to read from the i2c bus.\n");
        return -1;
    }

    return 0;
}

float get_voltage() {
    unsigned char data[2] = {0};

    // Correct condition to check for read error
    if (read_register_data(0x3B, 2, data) != 0) {
        return -1.0; // Error value
    }

    // Combine high and low bytes
    int raw_value = (data[0] << 8) | data[1];
    return raw_value * 0.001f; // Convert to volts (mV to V)
}

void display_data() {
    initscr();            // Start curses mode
    noecho();             // Don't echo pressed keys
    cbreak();             // Disable line buffering
    curs_set(0);          // Hide cursor
    nodelay(stdscr, TRUE); // Make getch() non-blocking

    while (1) {
        clear();
        for (int i = 0; i < (int)(sizeof(registers) / sizeof(RegisterInfo)); i++) {
            unsigned char data[2] = {0};
            if (read_register_data(i, registers[i].length, data) == 0) {
                printw("%s (0x%02X): ", registers[i].name, i);
                for (int j = 0; j < registers[i].length; j++) {
                    // Display each byte in binary format
                    for (int k = 7; k >= 0; k--) {
                        printw("%d", (data[j] >> k) & 1);
                    }
                    printw(" "); // Space between bytes
                }
                printw("\n");
            }
        }

        // Display battery voltage
        float voltage = get_voltage();
        if (voltage >= 0) {
            printw("Battery Voltage: %.2f V\n", voltage);
        } else {
            printw("Battery Voltage: Error reading\n");
        }

        refresh();

        int key = getch();
        if (key == 'q') {
            break; // Exit loop on 'q'
        }

        usleep(100000); // Sleep for 500 milliseconds
    }

    endwin(); // End curses mode
}

int main() {
    // Open the I2C device file
    i2c_fd = open("/dev/i2c-1", O_RDWR);
    if (i2c_fd < 0) {
        perror("Failed to open the i2c bus.\n");
        return 1;
    }

    display_data();

    close(i2c_fd);
    return 0;
}
