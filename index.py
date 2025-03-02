import os
import json
import subprocess
import requests
import threading
import time
import signal
import logging
from flask import send_from_directory, Flask, render_template, Response, stream_with_context
from epg import fetch_epg_for_channel

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Channel definitions
CHANNELS = {
    "CH_1": "ČT 1",
    "CH_2": "ČT 2",
    "CH_4": "ČT Sport",
    "CH_5": "ČT :D",
    "CH_6": "ČT Art",
    "CH_7": "ČT 3",
    "CH_24": "ČT 24",
    "CH_25": "CT iVysilani+ 1",
    "CH_26": "CT iVysilani+ 2",
    "CH_27": "CT iVysilani+ 3",
    "CH_28": "CT iVysilani+ 4",
    "CH_29": "CT iVysilani+ 5",
    "CH_30": "CT iVysilani+ 6",
    "CH_31": "CT iVysilani+ 7",
    "CH_32": "CT iVysilani+ 8",
    "CH_MOB_01": "CT iVysilani+ 9",
    "CH_MP_01": "CT iVysilani+ 10",
    "CH_MP_02": "CT iVysilani+ 11",
    "CH_MP_03": "CT iVysilani+ 12",
    "CH_MP_04": "CT iVysilani+ 13",
    "CH_MP_05": "CT iVysilani+ 14",
    "CH_MP_06": "CT iVysilani+ 15",
    "CH_MP_07": "CT iVysilani+ 16",
    "CH_MP_08": "CT iVysilani+ 17"
}

API_URL = "https://api.ceskatelevize.cz/video/v1/playlist-live/v1/stream-data/channel/{}?canPlayDrm=false"

# Store active ffmpeg processes
active_processes = {}
# Store active clients for each channel
channel_clients = {channel: set() for channel in CHANNELS}
# Store cached stream URLs
stream_urls = {}

def get_stream_url(channel, force_refresh=False):
    """Get streaming URL for the given channel and cache it."""
    try:
        if force_refresh or channel not in stream_urls:
            response = requests.get(API_URL.format(channel), timeout=10)
            if response.status_code == 200:
                data = response.json()
                stream_url = data.get("streamUrls", {}).get("main", None)
                if stream_url:
                    stream_urls[channel] = {
                        'url': stream_url,
                        'timestamp': time.time()
                    }
                    logger.info(f"Fetched new stream URL for {channel}")
                    return stream_url
                else:
                    logger.error(f"No stream URL found for {channel}")
            else:
                logger.error(f"Failed to get stream URL for {channel}: {response.status_code}")
        else:
            cached_data = stream_urls.get(channel)
            if cached_data and (time.time() - cached_data['timestamp']) < 300:
                return cached_data['url']
            else:
                return get_stream_url(channel, force_refresh=True)
    except Exception as e:
        logger.error(f"Error getting stream URL for {channel}: {str(e)}")
    
    cached_data = stream_urls.get(channel)
    return cached_data['url'] if cached_data else None

def start_ffmpeg_process(channel, force_refresh=False):
    """Start FFmpeg process for channel and return it."""
    if not force_refresh and channel in active_processes and active_processes[channel]['process'].poll() is None:
        return active_processes[channel]['process']
    
    stream_url = get_stream_url(channel, force_refresh=force_refresh)
    if not stream_url:
        logger.error(f"No stream URL for {channel}")
        return None
    
    os.makedirs('static/streams', exist_ok=True)
    
    cmd = [
        "ffmpeg",
        "-reconnect", "1",
        "-reconnect_streamed", "1",
        "-reconnect_delay_max", "5",
        "-timeout", "15000000",
        "-rw_timeout", "15000000",
        "-probesize", "42M",
        "-analyzeduration", "10M",
        "-fflags", "+genpts",
        "-i", stream_url,
        "-f", "mpegts",
        "-c:v", "copy",
        "-c:a", "aac",
        "-bufsize", "8192k",
        "-maxrate", "10M",
        "-tune", "zerolatency",
        "-preset", "ultrafast",
        "-metadata", f"service_provider=CT iVysilani",
        "-metadata", f"service_name={CHANNELS[channel]}",
        "-metadata", f"title={CHANNELS[channel]}",
        "-metadata", "description=Live stream",
        "-metadata", "language=Čeština",
        "pipe:1"
    ]
    
    try:
        if channel in active_processes:
            try:
                active_processes[channel]['process'].terminate()
                logger.info(f"Terminated existing FFmpeg process for {channel}")
            except:
                pass
        
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            bufsize=32 * 1024 * 1024  # Increased buffer size
        )
        
        def log_errors():
            for line in iter(process.stderr.readline, b''):
                line_str = line.decode('utf-8', errors='replace').strip()
                if "404 not found" in line_str.lower():
                    logger.error(f"FFmpeg 404 error for {channel}: {line_str}")
                    process.terminate()
                    start_ffmpeg_process(channel, force_refresh=True)
                elif "error" in line_str.lower() or "panic" in line_str.lower():
                    logger.error(f"FFmpeg error for {channel}: {line_str}")
        
        error_thread = threading.Thread(target=log_errors, daemon=True)
        error_thread.start()
        
        active_processes[channel] = {
            'process': process,
            'error_thread': error_thread,
            'last_used': time.time()
        }
        
        logger.info(f"Started FFmpeg process for {channel}")
        return process
    except Exception as e:
        logger.error(f"Failed to start FFmpeg for {channel}: {str(e)}")
        return None

def cleanup_unused_processes():
    """Terminate FFmpeg processes that haven't been used for a while."""
    while True:
        time.sleep(60)
        current_time = time.time()
        channels_to_cleanup = []
        
        for channel, process_info in active_processes.items():
            if not channel_clients[channel] and (current_time - process_info['last_used']) > 300:
                try:
                    process_info['process'].terminate()
                    logger.info(f"Terminated unused FFmpeg process for {channel}")
                except:
                    pass
                channels_to_cleanup.append(channel)
        
        for channel in channels_to_cleanup:
            active_processes.pop(channel, None)

@app.route('/')
def index():
    """Main page with channel selection."""
    return render_template("index.html", channels=CHANNELS)

@app.route('/stream/<channel>')
def stream(channel):
    """Stream the selected channel."""
    if channel not in CHANNELS:
        return "Invalid channel", 404
    
    client_id = id(threading.current_thread())
    channel_clients[channel].add(client_id)
    
    process = start_ffmpeg_process(channel)
    if not process:
        channel_clients[channel].discard(client_id)
        return Response("Stream not available", status=503)
    
    @stream_with_context
    def generate():
        nonlocal process
        error_count = 0
        chunk_count = 0
        buffer = b""
        
        # Add initial delay for proper initialization
        time.sleep(1)
        
        try:
            while True:
                chunk = process.stdout.read(256 * 1024)  # Increased chunk size
                if not chunk:
                    # Check if process is actually dead before restarting
                    if process.poll() is not None:
                        logger.warning(f"Stream for {channel} ended, checking status...")
                        error_count += 1
                        
                        # Only restart if we haven't received enough data
                        if chunk_count < 10:
                            new_process = start_ffmpeg_process(channel, force_refresh=True)
                            if new_process:
                                process = new_process
                                error_count = 0
                                chunk_count = 0
                                time.sleep(2)  # Wait for new process to initialize
                                continue
                        
                        if error_count > 3:
                            logger.error(f"Too many errors streaming {channel}, giving up")
                            break
                        
                        time.sleep(2)
                        continue
                    
                    # If process is still running, just continue
                    time.sleep(0.1)
                    continue
                
                chunk_count += 1
                error_count = 0
                
                # Update last used timestamp
                if channel in active_processes:
                    active_processes[channel]['last_used'] = time.time()
                    
                # Check if we have enough initial data before streaming
                if chunk_count < 5:
                    buffer += chunk
                    continue
                elif chunk_count == 5:
                    yield buffer + chunk
                    buffer = b""
                else:
                    yield chunk
        finally:
            channel_clients[channel].discard(client_id)
            logger.info(f"Client disconnected from {channel}, remaining clients: {len(channel_clients[channel])}")
    
    response = Response(generate(), content_type="video/mp2t")
    response.headers.add('Cache-Control', 'no-cache, no-store, must-revalidate')
    response.headers.add('Pragma', 'no-cache')
    response.headers.add('Expires', '0')
    return response

@app.route('/logo/<filename>')
def logo(filename):
    return send_from_directory('static/logos', filename)

@app.route('/player/<channel>')
def player(channel):
    """Renders a dedicated player page for the selected channel with EPG data."""
    if channel not in CHANNELS:
        return "Invalid channel", 404
    
    channel_name = CHANNELS[channel]
    epg_data = get_epg_data(channel)
    return render_template("player.html", channel=channel, channel_name=channel_name, epg_data=epg_data)

def get_epg_data(channel):
    """Fetch EPG data for the given channel."""
    date = time.strftime("%d.%m.%Y")
    epg_json = fetch_epg_for_channel(channel, date)
    filtered_programs = []
    if not epg_json:
        return {}

    current_time = time.strftime("%H:%M")
    if isinstance(epg_json, str):
        pass
    elif isinstance(epg_json, dict):
        filtered_programs = [program for program in epg_json if program['cas'] >= current_time]
    else:
        return {}
    return filtered_programs

@app.route('/status')
def status():
    """Show active streams and connected clients."""
    status_data = {
        channel: {
            "active": channel in active_processes,
            "clients": len(channel_clients[channel]),
            "display_name": CHANNELS[channel]
        } for channel in CHANNELS
    }
    return render_template("status.html", status=status_data)

def prestart_channels():
    """Pre-start encoding for popular channels."""
    popular_channels = ["CH_1", "CH_2", "CH_4", "CH_24"]
    for channel in popular_channels:
        if channel in CHANNELS:
            logger.info(f"Pre-starting encoding for {CHANNELS[channel]}")
            start_ffmpeg_process(channel)

if __name__ == '__main__':
    os.makedirs('static/logos', exist_ok=True)
    os.makedirs('static/streams', exist_ok=True)
    
    cleanup_thread = threading.Thread(target=cleanup_unused_processes, daemon=True)
    cleanup_thread.start()
    
    prestart_thread = threading.Thread(target=prestart_channels, daemon=True)
    prestart_thread.start()
    
    def signal_handler(sig, frame):
        logger.info("Shutting down, terminating FFmpeg processes...")
        for channel, process_info in active_processes.items():
            try:
                process_info['process'].terminate()
            except:
                pass
        os._exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    app.run(host='0.0.0.0', port=5090, debug=False, threaded=True)