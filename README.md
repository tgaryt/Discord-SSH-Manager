# Discord-SSH

## Introduction
This Discord bot was created by [tgaryt](https://ugc-gaming.net/index.php?members/ryt.3/) for [UGC-Gaming.NET](https://ugc-gaming.net).

## Requirements

- **Python:** Version 3.7.3
- **discord.py:** Version 1.7.3
- **python-paramiko** Version 3.4.0
- **Discord Bot Configuration:** Ensure that the bot has all Privileged Gateway Intents enabled.

## Installation

```bash
# Update package lists
sudo apt update

# Install Python 3 and pip
sudo apt install python3 python3-pip

# Navigate to the project directory
cd your-bot-directory

# Install Python virtual environment
sudo apt install python3-venv

# Create a virtual environment
python3 -m venv ssh

# Activate the virtual environment
source ssh/bin/activate

# Install the required Python libraries
pip install discord.py paramiko

# Run the bot in the background using nohup
nohup python ssh.py &

# Deactivate the virtual environment
deactivate
```
## Commands

### RCON Command
- **Command**: `!ssh_start`
  - Start the SSH connection.
 
  - **Command**: `!ssh [command]`
  - Send a command through SSH.
 
  - **Command**: `!ssh_stop`
  - Close the SSH connection.

## License
This project is licensed under the [MIT License](LICENSE).
