from .ceph import Ceph
from .chat import Chat
from .moex import Moex

from math import inf
from telegram import Update
from telegram.ext import ContextTypes, JobQueue
from typing import Dict

from logging import debug


class Notifier:
    def __init__(self, moex: Moex, ceph: Ceph):
        self.moex = moex
        self.ceph = ceph
        self.chats: Dict[str, Chat] = {
            chat_id: ceph.load(chat_id)
            for chat_id in ceph.get_all_chats()
        }

    async def notify(self, context: ContextTypes.DEFAULT_TYPE) -> None:
        chat_id = context.job.chat_id
        debug(f"notification: {chat_id}")
        chat = self.chats[chat_id]
        currents = self.moex.current
        message = []
        debug(f"{chat_id}: {chat}")
        for stock, delta in chat.req_offers.items():
            if stock not in currents:
                continue
            if chat.rsp_offers.get(stock, inf) - delta >= currents[stock].last_offer:
                message.append(f"{stock} offer: {currents[stock].last_offer:.4f}")
                chat.rsp_offers[stock] = currents[stock].last_offer
        for stock, delta in chat.req_bids.items():
            if stock not in currents:
                continue
            if chat.rsp_bids.get(stock, -inf) + delta <= currents[stock].last_bid:
                message.append(f"{stock} bid: {currents[stock].last_bid:.4f}")
                chat.rsp_bids[stock] = currents[stock].last_bid
        if message:
            await context.bot.send_message(chat_id, "\n".join(message))
            self.ceph.save(chat_id, chat)

    def schedule_notification(self, chat_id: str, job_queue: JobQueue) -> None:
        debug(f"scheduling notification: {chat_id}")
        job_queue.run_once(self.notify, .5, chat_id=chat_id, name=chat_id)

    def schedule_notification_all(self, job_queue: JobQueue) -> None:
        for chat_id in self.chats:
            self.schedule_notification(chat_id, job_queue)

    async def info(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await update.message.reply_text(
            "Usage:\n"
            "  /start\n"
            "  /stop\n"
            "  /help\n"
            "  /list\n"
            "  /current <stock>\n"
            "  /add inc <stock> <rubles>\n"
            "  /add dec <stock> <rubles>\n"
            "  /del inc <stock>\n"
            "  /del dec <stock>")

    async def current(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        stock = context.args[0]
        message = []
        if stock in self.moex.current:
            message.append(f"{stock} offer: {self.moex.current[stock].last_offer:.4f}")
            message.append(f"{stock} bid: {self.moex.current[stock].last_bid:.4f}")
        if message:
            await update.message.reply_text("\n".join(message))

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        chat_id = str(update.message.chat_id)
        self.chats[chat_id] = Chat()
        await self.info(update, context)

    async def add(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        chat_id = str(update.message.chat_id)
        chat = self.chats[chat_id]
        stock = context.args[1]
        delta = float(context.args[2])
        if context.args[0] == "inc":
            chat.rsp_bids.pop(stock, None)
            chat.req_bids[stock] = delta
        elif context.args[0] == "dec":
            chat.rsp_offers.pop(stock, None)
            chat.req_offers[stock] = delta
        else:
            await self.info(update, context)
            return
        self.ceph.save(chat_id, chat)
        self.schedule_notification(chat_id, context.job_queue)

    async def remove(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        chat_id = str(update.message.chat_id)
        if chat_id not in self.chats:
            return
        chat = self.chats[chat_id]
        stock = context.args[1]
        if context.args[0] == "inc":
            chat.req_bids.pop(stock, None)
        elif context.args[0] == "dec":
            chat.req_offers.pop(stock, None)
        else:
            await self.info(update, context)
            return
        self.ceph.save(chat_id, chat)
        self.schedule_notification(chat_id, context.job_queue)

    async def stop(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        chat_id = str(update.message.chat_id)
        for job in context.job_queue.get_jobs_by_name(chat_id):
            job.schedule_removal()
        self.ceph.remove(chat_id)
        self.chats.pop(chat_id)

    async def list_all(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        chat_id = str(update.message.chat_id)
        if chat_id not in self.chats:
            await update.message.reply_text("Nothing to show")
            return
        message = []
        for stock, delta in self.chats[chat_id].req_offers.items():
            message.append(f"dec {stock} {delta:.4f}")
        for stock, delta in self.chats[chat_id].req_bids.items():
            message.append(f"inc {stock} {delta:.4f}")

        if not message:
            await update.message.reply_text("Nothing to show")
            return
        await update.message.reply_text("\n".join(message))
