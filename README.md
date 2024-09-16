# AlertifyPi (Meeting Reminders via LEDs)

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Prerequisites](#prerequisites)
  - [Hardware](#hardware)
  - [Software](#software)
- [Hardware Setup](#hardware-setup)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

## Overview

**Meeting LED Indicator** is a Python-based application designed to run on a Raspberry Pi. It integrates with the Microsoft Graph API to fetch your daily meetings and uses GPIO-controlled LEDs to provide visual cues:

- **Yellow LED**: Blinks 15 minutes before a meeting.
- **Orange LED**: Turns on 5 minutes before a meeting.
- **Red LED**: Illuminates during an ongoing meeting.

This setup helps you stay aware of upcoming meetings without constantly checking your calendar.

## Features

- **Real-Time Meeting Updates**: Fetches and displays your meetings for the day.
- **Visual Alerts**: Uses LEDs to indicate different meeting statuses.
- **Configurable Runtime**: Adjust the script's maximum runtime as needed.
- **Timezone Support**: Handles meetings across different time zones.
- **Graceful Shutdown**: Ensures GPIO pins are cleaned up on exit.

## Prerequisites

### Hardware

- **Raspberry Pi** (any model with GPIO pins)
- **LEDs**:
  - Yellow LED
  - Orange LED
  - Red LED
- **Resistors**: 220Ω for each LED
- **Breadboard and Jumper Wires**

### Software

- **Operating System**: Raspberry Pi OS (formerly Raspbian) or any compatible Linux distribution.
- **Python 3.7+**
- **Libraries**:
  - `RPi.GPIO`
  - `requests`
  - `msal`
  - `pytz`
  - `python-dateutil`

## Hardware Setup

1. **Connect the LEDs to GPIO Pins**:

   | LED Color | GPIO Pin | Resistor |
   |-----------|----------|----------|
   | Yellow    | GPIO 17  | 220Ω     |
   | Orange    | GPIO 27  | 220Ω     |
   | Red       | GPIO 22  | 220Ω     |

2. **Wiring Instructions**:

   - Connect the anode (longer leg) of each LED to the respective GPIO pin through a 220Ω resistor.
   - Connect the cathode (shorter leg) of each LED to the Raspberry Pi's GND pin.
