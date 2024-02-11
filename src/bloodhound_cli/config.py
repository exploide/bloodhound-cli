import configparser
import os

from bloodhound_cli.logger import log


class Config:
    """Class to interact with the tool's configuration file."""

    def __init__(self):
        """Initialize the Config class, read (and if necessary create) the config file."""

        self._configparser = configparser.ConfigParser()
        self._configparser.read_dict({
            "DEFAULT": {
                "url": "",
                "token_id": "",
                "token_key": "",
            }
        })

        config_home = os.environ.get("XDG_CONFIG_HOME", default=os.path.join(os.path.expanduser("~"), ".config"))
        config_dir = os.path.join(config_home, "bhcli")
        self.config_file = os.path.join(config_dir, "bhcli.ini")

        if not os.path.exists(self.config_file):
            log.info("No config file found, creating it...")
            os.makedirs(config_dir, mode=0o700, exist_ok=True)
            with open(self.config_file, "w", encoding="UTF-8") as f:
                self._configparser.write(f)
            log.info("Created empty config file: %s", self.config_file)

        self._configparser.read(self.config_file)


    def get(self, key):
        """Return the configuration value specified by a given key."""

        return self._configparser["DEFAULT"][key]


    def update(self, **kwargs):
        """Update the configuration with key=value pairs and save to file."""

        for k, v in kwargs.items():
            self._configparser["DEFAULT"][k] = v

        with open(self.config_file, "w", encoding="UTF-8") as f:
            self._configparser.write(f)


config = Config()
