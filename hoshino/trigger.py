import re
from collections import defaultdict
import copy

import pygtrie
import zhconv

import hoshino
from hoshino import util
from hoshino.typing import CQEvent, List, Iterable

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hoshino.service import ServiceFunc


class BaseTrigger:
    def add(self, x, sf: "ServiceFunc"):
        raise NotImplementedError

    def find_handler(self, event: CQEvent) -> List["ServiceFunc"]:
        raise NotImplementedError


class PrefixTrigger(BaseTrigger):
    def __init__(self):
        super().__init__()
        self.trie = pygtrie.CharTrie()

    def add(self, prefix: str, sf: "ServiceFunc"):
        prefix_cht = zhconv.convert(prefix, "zh-hant")
        if prefix in self.trie:
            self.trie[prefix].append(sf)
            if prefix_cht != prefix:
                self.trie[prefix_cht].append(sf)
            hoshino.logger.warning(f"Prefix trigger `{prefix}` added multiple handlers: {sf.__name__}@{sf.sv.name}")
        else:
            self.trie[prefix] = [sf]
            if prefix_cht != prefix:
                self.trie[prefix_cht] = [sf]
            hoshino.logger.debug(f"Succeed to add prefix trigger `{prefix}`")

    def find_handler(self, event: CQEvent) -> Iterable["ServiceFunc"]:
        first_msg_seg = event.message[0]
        if first_msg_seg.type != "text":
            return
        first_text = first_msg_seg.data["text"].lstrip()
        item = self.trie.longest_prefix(first_text)
        if not item:
            return

        oldmsg = copy.deepcopy(event.message)
        event["prefix"] = item.key
        first_text = first_text[len(item.key):].lstrip()
        if not first_text and len(event.message) > 1:
            del event.message[0]
        else:
            first_msg_seg.data["text"] = first_text

        for sf in item.value:
            yield sf

        event.message = oldmsg


class SuffixTrigger(BaseTrigger):
    def __init__(self):
        super().__init__()
        self.trie = pygtrie.CharTrie()

    def add(self, suffix: str, sf: "ServiceFunc"):
        suffix_r = suffix[::-1]
        suffix_r_cht = zhconv.convert(suffix_r, "zh-hant")
        if suffix_r in self.trie:
            self.trie[suffix_r].append(sf)
            if suffix_r_cht != suffix_r:
                self.trie[suffix_r_cht].append(sf)
            hoshino.logger.warning(f"Suffix trigger `{suffix}` added multi handler: `{sf.__name__}`")
        else:
            self.trie[suffix_r] = [sf]
            if suffix_r_cht != suffix_r:
                self.trie[suffix_r_cht] = [sf]
            hoshino.logger.debug(f"Succeed to add suffix trigger `{suffix}`")

    def find_handler(self, event: CQEvent) -> Iterable["ServiceFunc"]:
        last_msg_seg = event.message[-1]
        if last_msg_seg.type != "text":
            return
        last_text = last_msg_seg.data["text"].rstrip()
        item = self.trie.longest_prefix(last_text[::-1])
        if not item:
            return

        oldmsg = copy.deepcopy(event.message)
        event["suffix"] = item.key[::-1]
        last_text = last_text[: -len(item.key)].rstrip()
        if not last_text and len(event.message) > 1:
            del event.message[-1]
        else:
            last_msg_seg.data["text"] = last_text

        for sf in item.value:
            yield sf

        event.message = oldmsg


class KeywordTrigger(BaseTrigger):
    def __init__(self):
        super().__init__()
        self.allkw = {}

    def add(self, keyword: str, sf: "ServiceFunc"):
        if sf.normalize_text:
            keyword = util.normalize_str(keyword)
        if keyword in self.allkw:
            self.allkw[keyword].append(sf)
            hoshino.logger.warning(f"Keyword trigger `{keyword}` added multi handler: `{sf.__name__}`")
        else:
            self.allkw[keyword] = [sf]
            hoshino.logger.debug(f"Succeed to add keyword trigger `{keyword}`")

    def find_handler(self, event: CQEvent) -> Iterable["ServiceFunc"]:
        for kw, sfs in self.allkw.items():
            for sf in sfs:
                text = event.norm_text if sf.normalize_text else event.plain_text
                if kw in text:
                    yield sf


class RexTrigger(BaseTrigger):
    def __init__(self):
        super().__init__()
        self.allrex = defaultdict(list)

    def add(self, rex: re.Pattern, sf: "ServiceFunc"):
        self.allrex[rex].append(sf)
        hoshino.logger.debug(f"Succeed to add rex trigger `{rex.pattern}`")

    def find_handler(self, event: CQEvent) -> "ServiceFunc":
        for rex, sfs in self.allrex.items():
            for sf in sfs:
                text = event.norm_text if sf.normalize_text else event.plain_text
                match = rex.search(text)
                if match:
                    event["match"] = match
                    yield sf


class _PlainTextExtractor(BaseTrigger):
    def find_handler(self, event: CQEvent):
        event.plain_text = event.message.extract_plain_text().strip()
        return []


class _TextNormalizer(_PlainTextExtractor):
    def find_handler(self, event: CQEvent):
        super().find_handler(event)
        event.norm_text = util.normalize_str(event.plain_text)
        return []


prefix = PrefixTrigger()
suffix = SuffixTrigger()
keyword = KeywordTrigger()
rex = RexTrigger()

chain: List[BaseTrigger] = [
    prefix,
    suffix,
    _TextNormalizer(),
    rex,
    keyword,
]
