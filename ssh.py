import discord
from discord.ext import commands, tasks
import paramiko
import configparser
import shlex
import os
from datetime from datetime
import asyncio

current_ssh_username = None

config = configparser.ConfigParser()
config.read('config.ini')

bot_token = config['Bot']['BotToken']
activity_timeout = config['Bot']['ActivityTimeout']

ssh_hostname = config['SSH']['hostname']

ssh_client = None
ssh_connected = False
connection_channel = None

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

def create_auto_files():
    log_file_path = 'rcon.log'
    if not os.path.exists(log_file_path):
        with open(log_file_path, 'w'):
            pass

def log_command_used(username, command):
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"{current_time} - {username} - {command}\n"
    log_file_path = 'rcon.log'

    if not os.path.exists(log_file_path):
        with open(log_file_path, 'w') as new_log_file:
            pass

    with open(log_file_path, 'a') as log_file:
        log_file.write(log_message)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    activity_check.start()

@tasks.loop(minutes=1)
async def activity_check():
    global ssh_client, ssh_connected, connection_channel, bot
    if ssh_connected:
        async for message in connection_channel.history(limit=1):
            last_bot_message = message
            break
        else:
            await close_ssh_connection()
            await connection_channel.send(f'SSH connection automatically closed due to inactivity ({activity_timeout} minutes).')
            return

        last_message_time = last_bot_message.created_at.timestamp()
        current_time = datetime.datetime.now().timestamp()
        elapsed_time = current_time - last_message_time

        if elapsed_time > float(activity_timeout) * 60:
            await close_ssh_connection()
            await connection_channel.send(f'SSH connection automatically closed due to inactivity ({activity_timeout} minutes).')

async def close_ssh_connection():
    global ssh_client, ssh_connected, connection_channel
    if ssh_connected:
        try:
            ssh_client.close()
        
        except Exception as e:
            print(f'Error closing SSH connection: {e}')
    
        finally:
            ssh_connected = False

@bot.command(name='ssh_start')
async def ssh_start(ctx, username, send_message=True):
    global ssh_client, ssh_connected, connection_channel, current_ssh_username

    channel_name = ctx.channel.mention

    if ssh_connected:
        await close_ssh_connection()
        await ctx.send('Old SSH connection closed.')

    try:
        print(f'Connecting to {ssh_hostname}...')

        ssh_username_to_use = config['SSH'].get(f'username_{username}', '')
        ssh_password_to_use = config['SSH'].get(f'password_{username}', '')

        if not ssh_username_to_use or not ssh_password_to_use:
            await ctx.send(f'Invalid username: {username}')
            return

        current_ssh_username = username

        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        ssh_port = config['SSH'].get('port', 22)
        ssh_client.connect(ssh_hostname, port=int(ssh_port), username=ssh_username_to_use, password=ssh_password_to_use)

        ssh_connected = True
        connection_channel = ctx.channel

        if send_message:
            await ctx.send(f'SSH connection started in channel {channel_name} with username {ssh_username_to_use}.')
    
    except Exception as e:
        print(f'Error starting SSH connection: {e}')
        await ctx.send(f'Error starting SSH connection: {e}')

@bot.command(name='ssh')
async def ssh_command(ctx, *, full_command):
    global ssh_client, ssh_connected, connection_channel, current_ssh_username

    if not ssh_connected or ctx.channel != connection_channel:
        channel_name = connection_channel.mention
        await ctx.send(f'You can only use the !ssh command in {channel_name} where !ssh_start was used.')
        return

    try:
        command_str = f'/bin/bash -c {shlex.quote(full_command)}'
        stdin, stdout, stderr = ssh_client.exec_command(command_str)
        log_command_used(ctx.author.name, full_command)

        await asyncio.sleep(1)

        if not stdout.channel.exit_status_ready():
            await close_ssh_connection()
            await ssh_start(ctx, current_ssh_username, send_message=False)
            await ctx.send(f'The previous command is still running. SSH connection restarted.')
            return

        output = stdout.read().decode('utf-8')

        if not output:
            output = stderr.read().decode('utf-8')

        if not output:
            output = 'Command produced no output.'

        await connection_channel.send(f'```{output}```')

    except Exception as e:
        print(f'An error occurred: {e}')
        await connection_channel.send(f'An error occurred: {e}')

@bot.command(name='ssh_stop')
async def ssh_stop(ctx):
    global ssh_client, ssh_connected, connection_channel
    if ssh_connected:
        try:
            ssh_client.close()
            await ctx.send('SSH connection closed.')
        
        except Exception as e:
            print(f'Error closing SSH connection: {e}')
            await connection_channel.send(f'Error closing SSH connection: {e}')
        
        finally:
            ssh_connected = False
    else:
        await ctx.send('No SSH connection to close.')

bot.run(bot_token)
