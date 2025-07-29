# Android Monitoring System

A comprehensive Flask-based web application designed to monitor Android devices in real-time. This system provides an intuitive dashboard to track device metrics, logs, and system information from multiple Android clients.

## Overview

The Android Monitoring System consists of two main components:
- **Server Application**: A Flask web server that collects and displays monitoring data
- **Client Agent**: A Python script that runs on Android devices (via Termux) to send system metrics

The system enables administrators to monitor multiple Android devices from a centralized web interface, tracking everything from battery status and memory usage to location data and system logs.

## Features

- **Real-time Device Monitoring**: Track multiple Android devices simultaneously
- **Comprehensive Metrics**: Monitor battery, RAM, storage, and network information
- **Location Tracking**: GPS coordinates with accuracy details
- **WhatsApp Alert System**: Automatic alerts sent to WhatsApp when critical thresholds are reached
- **Log Management**: View and analyze device logs through a clean web interface
- **Responsive Dashboard**: Bootstrap-powered UI that works on desktop and mobile
- **Device Discovery**: Automatic detection and listing of connected devices
- **JSON Data Processing**: Efficient handling of structured data from client agents

## Screenshots

![Dashboard](screenshot/Dashboard.jpg)
*Main dashboard showing connected devices and their status*

![Device Logs](screenshot/Logs.jpg)
*Detailed log viewer with filtering capabilities*

![Device List](screenshot/Devices.jpg)
*Overview of all monitored devices*

## Technologies Used

**Backend:**
- Python 3.x
- Flask (Web Framework)
- Socket Programming
- WhatsApp Business API integration
- JSON for data exchange

**Frontend:**
- HTML5/CSS3
- Bootstrap 4/5
- JavaScript

**Client-side:**
- Termux (Android Terminal)
- Python subprocess module
- Android system APIs

## Installation

### Server Setup

1. Clone the repository:
```bash
git clone https://github.com/CoderNikkcoder/Android_Monitoring.git
cd Android-monitoring
```

2. Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install flask requests
```

4. Configure WhatsApp alerts:
   - Ensure WhatsApp Web is logged in on the server machine
   - Update phone numbers in the configuration file
   - Set alert thresholds in the settings

5. Start the server:
```bash
python app.py
```

The web interface will be available at `http://localhost:5000`

### Client Setup (Android Device)

1. Install Termux from F-Droid or Google Play Store

2. Install required packages in Termux:
```bash
pkg update
pkg install python
pkg install termux-api
```

3. Copy `client.py` to your Android device

4. Run the client:
```bash
python client.py
```

5. Enter your server's IP address when prompted

## Usage

### Starting the System

1. **Launch the Server**: Run the Flask application on your monitoring machine
2. **Connect Clients**: Execute the client script on each Android device you want to monitor
3. **Access Dashboard**: Open your web browser and navigate to the server's IP address

### Monitoring Features

- **Homepage (`/`)**: Overview dashboard with summary statistics
- **Logs (`/logs`)**: Detailed view of all collected log data
- **Devices (`/devices`)**: List of connected devices with current status

### Alert System

The system automatically sends WhatsApp notifications when:
- Battery level drops below 20%
- RAM usage exceeds 85%
- Storage space falls below 10%
- Device goes offline for more than 5 minutes
- Location coordinates indicate device movement outside designated areas

### Data Collection

The client automatically collects and sends the following data every 60 seconds:
- Device IP address and hostname
- Battery level and charging status
- RAM usage (total, available, percentage)
- Storage information (total, used, free space)
- GPS location coordinates
- Android version and device information

## Project Structure

```
android-monitoring-system/
│
├── app.py                 # Main Flask application
├── client.py             # Android client agent
├── templates/            # HTML templates
│   ├── base.html        # Base template
│   ├── index.html       # Homepage template
│   ├── logs.html        # Logs viewer template
│   └── devices.html     # Device list template
└── screenshots/         # Documentation images
```

## Configuration

### Server Configuration
- Default port: `5000` (Flask)
- Data collection port: `5001` (Socket server)
- Data refresh interval: 60 seconds
- Alert thresholds: Configurable in `config.py`

### WhatsApp Configuration
- Ensure WhatsApp Web is logged in on the server machine before running
- Add recipient phone numbers to config.py (format: "+91xxxxxxxxxx")
- PyWhatKit will automatically open WhatsApp Web to send messages
- Configure message templates for different alert types

### Client Configuration
- Modify `INTERVAL` variable in `client.py` to change data sending frequency
- Update `PORT` if using a different server port

## Contributing

We welcome contributions to improve the Android Monitoring System! Here's how you can help:

1. **Fork the Repository**: Create your own copy of the project
2. **Create a Branch**: `git checkout -b feature/your-feature-name`
3. **Make Changes**: Implement your improvements or bug fixes
4. **Test Thoroughly**: Ensure your changes work across different devices
5. **Submit a Pull Request**: Describe your changes and their benefits

### Development Guidelines

- Follow Python PEP 8 style guidelines
- Add comments for complex functionality
- Test on multiple Android versions when possible
- Update documentation for new features

## Security Notes

- This system is designed for trusted networks
- Consider implementing authentication for production use
- Be mindful of location data privacy
- Review permissions required by Termux API

## Troubleshooting

**Client Connection Issues:**
- Ensure both devices are on the same network
- Check firewall settings on the server machine
- Verify the correct server IP address is entered

**Permission Errors on Android:**
- Grant necessary permissions to Termux
- Install Termux API app for location features

**Data Not Updating:**
- Check network connectivity both client and server on the same network
- Verify the client script is running continuously
- Look for error messages in the terminal output

**WhatsApp Alerts Not Working:**
- Ensure WhatsApp Web is logged in on the server machine
- Check if browser (Chrome/Firefox) is installed and accessible
- Verify recipient numbers are in correct format (+91xxxxxxxxxx)
- Make sure the server machine has GUI access (not headless)
- PyWhatKit requires a few seconds delay between messages

## Contact

**Developer**: Kunal Pawar
**Email**: kunalpawar13042004@gmail.com
**GitHub**: [@Kunal-1304](https://github.com/Kunal-1304)

---

**Note**: This project is designed for educational and personal monitoring purposes. Please ensure compliance with local privacy laws and obtain proper consent when monitoring devices.
