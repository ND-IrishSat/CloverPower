# Makefile for i2c_monitor program

# Compiler and flags
CC = gcc
CFLAGS = -Wall -Wextra -O2
LDFLAGS = -lncurses

# Target executable name
TARGET = i2c_monitor

# Source files
SRCS = i2c_monitor.c

# Default target to build the program
all: $(TARGET)

# Rule to build the target
$(TARGET): $(SRCS)
	$(CC) $(CFLAGS) -o $(TARGET) $(SRCS) $(LDFLAGS)

# Clean up build artifacts
clean:
	rm -f $(TARGET)

# Install required libraries (commented out as a reminder)
install:
	sudo apt-get install -y libi2c-dev libncurses5-dev

# Run the program with sudo
run: $(TARGET)
	sudo ./$(TARGET)
