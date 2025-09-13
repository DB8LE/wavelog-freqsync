import requests, urllib3, datetime

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
