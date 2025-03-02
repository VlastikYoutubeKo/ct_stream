# CT iVysilani Web Streamer

A Flask-based web application for streaming Czech Television (CT) channels. This application provides a web interface for accessing CT channels, complete with EPG (Electronic Program Guide) integration and stream management.

## Features

- Live streaming of Czech Television channels
- Electronic Program Guide (EPG) integration
- Web-based channel selection interface
- Dedicated player page with program information
- Status monitoring page for active streams
- Automatic stream management and cleanup
- Pre-starting of popular channels

## Prerequisites

- Python 3.6 or higher
- FFmpeg installed on your system
- Internet connection to access CT streams

## Installation

1. Clone the repository
2. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```
3. Ensure FFmpeg is installed and available in your system PATH

## Usage

1. Start the application:
   ```bash
   python index.py
   ```
2. Access the web interface at `http://localhost:5090`
3. Select a channel to start streaming

The server will run on port 5090 by default.

## Available Channels

The application provides access to the following channels:

- ČT 1 (CH_1)
- ČT 2 (CH_2)
- ČT Sport (CH_4)
- ČT :D (CH_5)
- ČT Art (CH_6)
- ČT 3 (CH_7)
- ČT 24 (CH_24)
- CT iVysilani+ 1 (CH_25)
- CT iVysilani+ 2 (CH_26)
- CT iVysilani+ 3 (CH_27)
- CT iVysilani+ 4 (CH_28)
- CT iVysilani+ 5 (CH_29)
- CT iVysilani+ 6 (CH_30)
- CT iVysilani+ 7 (CH_31)
- CT iVysilani+ 8 (CH_32)
- CT iVysilani+ 9 (CH_MOB_01)
- CT iVysilani+ 10 (CH_MP_01)
- CT iVysilani+ 11 (CH_MP_02)
- CT iVysilani+ 12 (CH_MP_03)
- CT iVysilani+ 13 (CH_MP_04)
- CT iVysilani+ 14 (CH_MP_05)
- CT iVysilani+ 15 (CH_MP_06)
- CT iVysilani+ 16 (CH_MP_07)
- CT iVysilani+ 17 (CH_MP_08)

## Endpoints

- `/` - Main page with channel selection
- `/stream/<channel>` - Direct stream access
- `/player/<channel>` - Dedicated player page with EPG
- `/status` - System status page
- `/logo/<filename>` - Channel logo access

## Features Details

### Stream Management
- Automatic cleanup of inactive streams
- Reconnection handling for stream interruptions
- Error monitoring and automatic recovery
- Resource optimization through stream caching

### EPG Integration
- Real-time program guide information
- Current and upcoming programs display
- Channel-specific program schedules

## Directory Structure

```
web/
├── static/
│   ├── logos/    # Channel logos
│   └── streams/  # Stream temporary files
├── templates/    # HTML templates
├── index.py     # Main application file
└── requirements.txt
```

## Note

This application is designed for personal use and requires a stable internet connection to access CT streams. Make sure you have the necessary rights to access the content in your region.