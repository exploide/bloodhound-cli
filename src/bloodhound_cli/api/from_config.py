from bloodhound_cli.config import config
from . import Api

# create an Api instance with settings obtained from the configuration file
api = Api(url=config.get("url"), token_id=config.get("token_id"), token_key=config.get("token_key"))
