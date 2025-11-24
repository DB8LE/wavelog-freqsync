import requests, urllib3, datetime, threading, socket
from typing import Deque, Tuple

urllib3.disable_warnings(category=urllib3.exceptions.InsecureRequestWarning)

class WavelogConn:
    def __init__(self, host: str, api_key: str):
        self.api_url = host+"/index.php/api/radio"
        self.api_key = api_key
    
    def set_rig_freq_mode(self, rig_name: str, frequency: int, mode: str):
        """Set the frequency and mode of a hardware interface in wavelog"""

        # Get current utc time in specific format
        time = datetime.datetime.now(datetime.timezone.utc).strftime("%Y/%m/%d %H:%M")

        # Prepare request data
        request_data = {
            "key": self.api_key,
            "radio": rig_name,
            "frequency": frequency,
            "mode": mode,
            "timestamp": time
        }

        # Send post request to API
        request = requests.post(
            url=self.api_url,
            json=request_data,
            verify=False
        )

        if request.status_code != 200:
            print("WARNING: wavelog API returned status code", request.status_code)

class WavelogCallbackListener:
    def __init__(self, port: int, out_queue: Deque[Tuple[int, str]]) -> None:
        self.port = port
        self.out_queue = out_queue

        self.listener_thread = None
        self.run_listener = False

    def _listen(self):
        """Internal function run by listener thread"""

        # Initialize socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)

        # Start listening for connections
        print("Starting wavelog callback listener")
        sock.bind(("", self.port))
        sock.listen(1)
        while self.run_listener:
            try:
                # Try to accept a connection and receive data from it
                conn, addr = sock.accept()
                data = conn.recv(1024)
                text = data.decode("utf-8")

                # Parse get request to obtain frequency and mode
                lines = text.splitlines()
                parts = lines[0].split(" ")
                _, frequency, mode = parts[1].split("/")

                print(f"Got callback for {frequency} {mode.upper()} from {addr[0]}")
                self.out_queue.append((int(frequency), mode.upper()))

                conn.sendall(data) # Echo data back
            except TimeoutError: # Allow listener to stop by timing out every second without request
                pass
            except Exception as e: # Likely some parsing error
                print("Got exception while listening for wavelog callbacks: "+str(e))

    def start(self):
        """Start listening for callbacks"""

        if self.listener_thread is None:
            self.run_listener = True
            self.listener_thread = threading.Thread(target=self._listen)
            self.listener_thread.start()
    
    def close(self):
        """Stop listening for callbacks"""

        if self.listener_thread is not None:
            self.run_listener = False
            self.listener_thread.join(timeout=3)

