from typing import Self, List
import tomllib

class Config:
    def __init__(self) -> None:
        # General
        self.update_delay: int
        self.print_rig_data: bool

        # Wavelog
        self.wavelog_host: str
        self.wavelog_radio_name: str
        self.wavelog_api_keys: List[str]
        self.wavelog_keepalive_sec: int


        # Rigctld
        self.rigctld_host: str
        self.rigctld_port: int
        self.rigctld_allow_offline: bool
        self.rigctld_boot_time: int

    def read_config(self) -> Self:
        """Read config.toml in current directory"""

        # Read config
        try:
            with open("config.toml", "rb") as f:
                conf_data = tomllib.load(f)
        except FileNotFoundError:
            print("ERROR: Couldn't find config.toml in current directory")
            exit(1)
        except tomllib.TOMLDecodeError:
            print("ERROR: Failed to parse TOML in config.toml")
            exit(1)
        
        # Set values of self

        # General section
        conf_general = conf_data["general"]
        self.update_delay = conf_general["update_delay"]
        self.print_rig_data = conf_general["print_rig_data"]

        # Wavelog section
        conf_wavelog = conf_data["wavelog"]
        self.wavelog_host = conf_wavelog["host"]
        self.wavelog_radio_name = conf_wavelog["radio_name"]
        self.wavelog_api_keys = conf_wavelog["api_keys"]
        self.wavelog_keepalive_sec = conf_wavelog["keepalive_seconds"]

        # Rigctld section
        conf_rigctld = conf_data["rigctld"]
        self.rigctld_host = conf_rigctld["host"]
        self.rigctld_port = int(conf_rigctld["port"])
        self.rigctld_allow_offline = conf_rigctld["allow_offline"]
        self.rigctld_boot_time = int(conf_rigctld["boot_time"])

        return self