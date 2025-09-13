import tomllib
from typing import Self

class Config:
    def __init__(self) -> None:
        self.radio_name = None

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

        # Wavelog section
        conf_wavelog = conf_data["wavelog"]
        self.radio_name = conf_wavelog["radio_name"]

        return self