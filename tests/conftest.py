import os

# Disable loading user's global ~/.config/reny/config.toml during unit tests
os.environ['DISABLE_CONFIG_FOR_TESTS'] = '1'
