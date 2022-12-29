from .notifier import Notifier
from .ceph import Ceph
from .moex import Moex

import asyncio
from os import environ
from telegram.ext import Application, CommandHandler, ContextTypes

import logging


async def update(context: ContextTypes.DEFAULT_TYPE) -> None:
    moex, notifier = context.job.data
    await moex.update()
    notifier.schedule_notification_all(context.job_queue)


def main():
    asyncio.set_event_loop(asyncio.new_event_loop())
    app = Application.builder().token(environ["MOEXN_TG_TOKEN"]).build()

    moex = Moex()
    ceph = Ceph(
        environ["MOEXN_CEPH_CONF"],
        environ["MOEXN_CEPH_KEYRING"],
        environ["MOEXN_CEPH_POOL"])
    bot = Notifier(moex, ceph)
    app.job_queue.run_repeating(update, 3.0, data=[moex, bot])

    for handler in (
            CommandHandler("start", bot.start),
            CommandHandler("help", bot.info),
            CommandHandler("add", bot.add),
            CommandHandler("del", bot.remove),
            CommandHandler("current", bot.current),
            CommandHandler("stop", bot.stop),
            CommandHandler("list", bot.list_all)):
        app.add_handler(handler)

    app.run_polling()


if __name__ == "__main__":
    logging.basicConfig(level="DEBUG")
    main()
