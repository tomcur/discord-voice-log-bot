import discord
import asyncio
import config

server_channels = {} # Server channel cache
client = discord.Client()

def find_channel(server, refresh = False):
    """
    Find and return the channel to log the voice events to.
    
    :param server: The server to find the channel for.
    :param refresh: Whether to refresh the channel cache for this server.
    """
    if not refresh and server in server_channels:
        return server_channels[server]
        
    for channel in client.get_all_channels():
        if channel.server == server and channel.name == config.CHANNEL_NAME:
            print("%s: refreshed destination log channel" % server)
            server_channels[server] = channel
            return channel
            
    return None

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

@client.event
async def on_voice_state_update(member_before, member_after):
    """
    Called when the voice state of a member on a server changes.
    
    :param member_before: The state of the member before the change.
    :param member_after: The state of the member after the change.
    """
    server = member_after.server
    channel = find_channel(server)
    
    voice_channel_before = member_before.voice_channel
    voice_channel_after = member_after.voice_channel
    
    if voice_channel_before == voice_channel_after:
        # No change
        return
    
    if voice_channel_before == None:
        # The member was not on a voice channel before the change
        msg = "%s joined voice channel _%s_" % (member_after.mention, voice_channel_after.name)
    else:
        # The member was on a voice channel before the change
        if voice_channel_after == None:
            # The member is no longer on a voice channel after the change
            msg = "%s left voice channel _%s_" % (member_after.mention, voice_channel_before.name)
        else:
            # The member is still on a voice channel after the change
            msg = "%s switched from voice channel _%s_ to _%s_" % (member_after.mention, voice_channel_before.name, voice_channel_after.name)
    
    # Try to log the voice event to the channel
    try:
        await client.send_message(channel, msg)
    except:
        # No message could be sent to the channel; force refresh the channel cache and try again
        channel = find_channel(server, refresh = True)
        if channel == None:
            # The channel could not be found
            print("Error: channel #%s does not exist on server %s." % (config.CHANNEL_NAME, server))
        else:
            # Try sending a message again
            try:
                await client.send_message(channel, msg)
            except discord.DiscordException as exception:
                # Print the exception
                print("Error: no message could be sent to channel #%s on server %s. Exception: %s" % (config.CHANNEL_NAME, server, exception))

client.run(config.BOT_TOKEN)
