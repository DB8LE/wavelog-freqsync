import socket

class RigctldConn:
    def __init__(self, host: str, port: int):
        # Try to connect to provided host
        try:
            self.socket = socket.create_connection((host, port), timeout=3)
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

        return response
    
    def get_frequency(self) -> int:
        """Get frequency from connected rigctld instance"""

        response = self._send_command("f")

        freq = int(response) # If this line fails, something is wrong with rigctld

        return freq
    
    def get_mode(self) -> str:
        """Get mode from connected rigctld instance"""

        response = self._send_command("m")

        return response
