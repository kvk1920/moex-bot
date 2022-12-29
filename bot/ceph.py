from .chat import Chat

from rados import Rados

from json import dumps, loads
from typing import Dict, List

from logging import debug


# TODO(kvk1920): Async?
class Ceph:
    def __init__(self, conffile: str, keyring: str, pool: str) -> None:
        self.cluster = Rados(conffile=conffile, conf={"keyring": keyring})
        self.cluster.connect()
        self.pool = pool

    def save(self, chat_id: str, chat: Chat) -> None:
        serialized = "\n".join(map(dumps, [
            chat.req_bids, chat.rsp_bids, chat.req_offers, chat.rsp_offers]))
        ioctx = self.cluster.open_ioctx(self.pool)
        ioctx.write_full(chat_id, serialized.encode())
        ioctx.close()

    def remove(self, chat_id: str) -> None:
        ioctx = self.cluster.open_ioctx(self.pool)
        ioctx.remove_object(chat_id)
        ioctx.close()

    def load(self, chat_id: str) -> Dict[str, float]:
        ioctx = self.cluster.open_ioctx(self.pool)
        try:
            serialized = ioctx.read(chat_id).decode().splitlines()
            debug(f"Serialized: {serialized}")
            ioctx.close()

            chat = Chat(
                req_bids=loads(serialized[0]),
                rsp_bids=loads(serialized[1]),
                req_offers=loads(serialized[2]),
                rsp_offers=loads(serialized[3]),
            )
            debug(f"Loaded {chat_id}: {chat}")
            return chat
        except Exception as ex:
            debug(ex.with_traceback())
            ioctx.close()
            return Chat()

    def get_all_chats(self) -> List[str]:
        ioctx = self.cluster.open_ioctx(self.pool)
        result = [chat.key for chat in ioctx.list_objects()]
        ioctx.close()
        debug(f"Found chats: {result}")
        return result
