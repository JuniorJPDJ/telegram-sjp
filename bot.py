import argparse
import asyncio

import aiohttp
from telethon import TelegramClient, events

import sjp

async def main():
    parser = argparse.ArgumentParser(description='Bot information')
    parser.add_argument('api_id', type=int, help='Telegram app API ID')
    parser.add_argument('api_hash', type=str, help='Telegram app API hash')
    parser.add_argument('bot_token', type=str, help='Telegram bot token')
    args = parser.parse_args()

    bot = TelegramClient('bot', args.api_id, args.api_hash)
    await bot.start(bot_token=args.bot_token)

    async with aiohttp.ClientSession() as sess:
        sjp_obj = sjp.SJP(sess)

        # inline version
        @bot.on(events.InlineQuery)
        async def handler(event):
            if not event.text:
                return
            builder = event.builder
            d = await sjp_obj.get_definition(event.text)
            autocomplete = await sjp_obj.get_autocomplete(event.text)
            if d is not None:
                await event.answer([builder.article(d, text=d)])
            else:
                if len(autocomplete):
                    autocomplete = autocomplete[:10]
                    done, _ = await asyncio.wait([asyncio.create_task(sjp_obj.get_definition(x)) for x in autocomplete], timeout=5)
                    results = [d.result() for d in done]
                    k = [builder.article(a, text=a) for a in results if a is not None]
                    await event.answer(k[:2])

        # standard version
        @bot.on(events.NewMessage)
        async def my_event_handler(event):
            chat = await event.get_chat()
            d = await sjp_obj.get_definition(event.raw_text)
            if d is not None:
                await event.reply(d)
            else:
                await event.reply('Nie znalazłem definicji')
                autocomplete = await sjp_obj.get_autocomplete(event.raw_text)
                suggestions = ''
                if autocomplete:
                    for w in autocomplete:
                        suggestions += '\n' + w
                await bot.send_message(chat, 'Czy chodziło ci o:' + suggestions)

        await bot.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
