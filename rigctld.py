import socket, time
from typing import Dict, Optional

class RigctldConn:
    def __init__(self, host: str, port: int):
        # Try to connect to provided host
        self.host = (host, port)
        self._connect()
    
    def _connect(self):
        """Connecet to rigctld. Closes and reopens socket if its already connected"""

        # Close socket if it has been defined already
        try:
            self.socket.close()
        except AttributeError:
            pass

        # Create socket
        try:
            self.socket = socket.create_connection(self.host, timeout=3)
        except Exception as e:
            print("ERROR: Failed to connect to rigctld.", e)
            exit(1)

    def _send_command(self, command: str) -> Dict[str, str]:
        """Send command to connected rigctld instance and return first line of response"""

        # Send command
        self.socket.sendall((f"+{command}\n").encode("ascii"))

        time.sleep(0.1) # Wait a bit to force some wait between commands

        # Get response
        try:
            response = self.socket.recv(4096).decode("ascii")
        except TimeoutError:
            print("ERROR: Rigctld command timed out")
            return {}
        response = response.splitlines()

        # Get first line of response if it there is at least one line
        if len(response) < 0:
            return {}

        # Check status code
        status_line = response.pop()
        status_code = int(status_line.removeprefix("RPRT ").strip())
        if status_code != 0:
            print(f"ERROR: Rigctld replied with non-zero status code to command '+{command}'")
            return {}

        # Parse response to dict
        out = {}
        for line in response:
            try:
                parts = line.strip().split(":")
                if len(parts) == 1: # Skip initial line echoing back command
                    continue

                key = parts[0].lower().replace(" ", "_")
                value = parts[1].strip()
                out[key] = value
            except Exception:
                pass

        return out

    def wait_until_active(self):
        """Wait until rig reports that it is on using its powerstate"""

        while True:
            is_on = self.get_powerstate()

            if is_on:
                self._connect() # Reconnect socket to avoid weirdness
                return

            # Wait one second to avoid spamming rigctl if powerstate was zero instead of timeout
            time.sleep(1)

    def get_powerstate(self) -> bool:
        """Get powerstate of rig (true = on). May require timeout to be hit on some rigs."""

        is_on = False
        try:
            response = self._send_command("\\get_powerstat")
            if response.get("power_status") == "1": # Some rigs will return zero while off, while others will cause a timeout
                is_on = True
        except socket.timeout:
            is_on = False

        return is_on
    
    def get_frequency(self) -> Optional[int]:
        """Get frequency from connected rigctld instance"""

        response = self._send_command("f")

        frequency = response.get("frequency")
        if frequency is not None:
            return int(frequency)
        return None
    
    def get_mode(self) -> Optional[str]:
        """Get mode from connected rigctld instance"""

        response = self._send_command("m")

        return response.get("mode")
    
    def set_frequency(self, frequency: int):
        """Set rig frequency"""

        self._send_command("F "+str(frequency))

    def set_mode(self, mode: str):
        """Set rig mode"""

        self._send_command("M "+mode+" -1")
