import openai
import os
import discord
from dotenv import load_dotenv
from discord.ext import commands
import asyncio
import functools

# load dotenv from system
load_dotenv()

# set the token through the .env file
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
OPEN_AI_TOKEN = os.getenv('OPEN_AI_KEY')

# create discord bot client
client = discord.Bot()

openai.api_key = OPEN_AI_TOKEN

@client.event
async def on_ready():
    print(f"{client.user.name} is online and ready to go :)")
    # sets the bots custom status
    await client.change_presence(activity=discord.Game(name='try "/chat"!'))


@client.command(name="chat", description="Chat with ChatGPT, an ai with human like responses.")
async def _chat(ctx, prompt, engine: discord.Option(name="engine", choices=["text-davinci-002", "text-curie-001", "text-babbage-001", "text-adapter-002"]) = "text-davinci-002", fun_level=0.5):

    # send a message, and save it to edit after the response
    discord_response = await ctx.respond("Ok! Waiting for ChatGPT...")

    # Use GPT-3 to generate a response in a separate thread

    # find the total chars to send, the more in the original prompt the more the bot's response will be limited, ig i could change this but its fine
    # if you wanted to just add an option, either true or false, to include the original response in the embed, then depending just don't add that field

    total_chars = len(prompt)+len("Original prompt") + len("AI Response")+1
    # +1 is just for safety


    partial_function = functools.partial(
        my_blocking_function, prompt, engine, fun_level, total_chars)

    result = await asyncio.get_event_loop().run_in_executor(None, partial_function)
    result = dict(result)["choices"][0]["text"]

    if len(result) >= 1000:
        result = result[:999]

        print(len(result))

    embed = discord.Embed(title="ChatGPT")
    embed.add_field(name="Original prompt", value=prompt, inline=False)
    embed.add_field(name="AI Response",
                    value=result, inline=False)
    embed.set_author(name=_engine)

    await discord_response.edit_original_response(content="", embed=embed)

    # Do some more async work


def my_blocking_function(prompt, engine, accuracy, current_char_amount=0):
    ai_response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=prompt,
        temperature=float(accuracy),
        top_p=1,
        max_tokens=600,
        stop=str(1000-current_char_amount),
        frequency_penalty=0.5,
        presence_penalty=0.5
    )

    print(ai_response, "\n\n"+str(type(dict(ai_response))))
    return dict(ai_response)


def main():
    client.run(DISCORD_TOKEN)


if __name__ == '__main__':
    main()
