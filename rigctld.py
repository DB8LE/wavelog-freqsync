import socket, time

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

    def _send_command(self, command: str) -> str:
        """Send command to connected rigctld instance and return first line of response"""

        # Send command
        self.socket.sendall((command + "\n").encode("ascii"))

        # Get response
        response = self.socket.recv(4096).decode("ascii")
        response = response.splitlines()

        # Get first line of response if it there is at least one line
        if len(response) > 0:
            response = response[0].strip()
        else:
            response = ""

        time.sleep(0.1) # Wait a bit to force some wait between commands

        return response
    
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
            if response == "1": # Some rigs will return zero while off, while others will cause a timeout
                is_on = True
        except socket.timeout:
            is_on = False

        return is_on
    
    def get_frequency(self) -> int:
        """Get frequency from connected rigctld instance"""

        response = self._send_command("f")

        freq = int(response) # If this line fails, something is wrong with rigctld

        return freq
    
    def get_mode(self) -> str:
        """Get mode from connected rigctld instance"""

        response = self._send_command("m")

        return response
    
    def set_frequency(self, frequency: int):
        """Set rig frequency"""

        self._send_command("F "+str(frequency))

    def set_mode(self, mode: str):
        """Set rig mode"""

        self._send_command("M "+mode)
