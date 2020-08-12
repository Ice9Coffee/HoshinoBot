import re

import pygtrie
import zhconv

import hoshino
from hoshino import util
from hoshino.typing import CQEvent


class BaseTrigger:
    def add(self, x, sf: "ServiceFunc"):
        raise NotImplementedError

    def find_handler(self, event: CQEvent) -> "ServiceFunc":
        raise NotImplementedError


class PrefixTrigger(BaseTrigger):
    def __init__(self):
        super().__init__()
        self.trie = pygtrie.CharTrie()

    def add(self, prefix: str, sf: "ServiceFunc"):
        if prefix in self.trie:
            other = self.trie[prefix]
            hoshino.logger.warning(
                f"Failed to add prefix trigger `{prefix}`: Conflicts between {sf.__name__} and {other.__name__}"
            )
            return
        self.trie[prefix] = sf
        self.trie[zhconv.convert(prefix, "zh-hant")] = sf
        hoshino.logger.debug(f"Succeed to add prefix trigger `{prefix}`")

    def find_handler(self, event: CQEvent):
        first_msg_seg = event.message[0]
        if first_msg_seg.type != "text":
            return None
        first_text = first_msg_seg.data["text"].lstrip()
        item = self.trie.longest_prefix(first_text)
        if not item:
            return None

        event["prefix"] = item.key
        first_text = first_text[len(item.key) :].lstrip()
        if not first_text and len(event.message) > 1:
            del event.message[0]
        else:
            first_msg_seg.data["text"] = first_text
        return item.value


class SuffixTrigger(BaseTrigger):
    def __init__(self):
        super().__init__()
        self.trie = pygtrie.CharTrie()

    def add(self, suffix: str, sf: "ServiceFunc"):
        suffix_r = suffix[::-1]
        if suffix_r in self.trie:
            other = self.trie[suffix_r]
            hoshino.logger.warning(
                f"Failed to add suffix trigger `{suffix}`: Conflicts between {sf.__name__} and {other.__name__}"
            )
            return
        self.trie[suffix_r] = sf
        self.trie[zhconv.convert(suffix_r, "zh-hant")] = sf
        hoshino.logger.debug(f"Succeed to add suffix trigger `{suffix}`")

    def find_handler(self, event: CQEvent):
        last_msg_seg = event.message[-1]
        if last_msg_seg.type != "text":
            return None
        last_text = last_msg_seg.data["text"].rstrip()
        item = self.trie.longest_prefix(last_text[::-1])
        if not item:
            return None

        event["suffix"] = item.key[::-1]
        last_text = last_text[: -len(item.key)].rstrip()
        if not last_text and len(event.message) > 1:
            del event.message[-1]
        else:
            last_msg_seg.data["text"] = last_text
        return item.value


class KeywordTrigger(BaseTrigger):
    def __init__(self):
        super().__init__()
        self.allkw = {}

    def add(self, keyword: str, sf: "ServiceFunc"):
        if sf.normalize_text:
            keyword = util.normalize_str(keyword)
        if keyword in self.allkw:
            other = self.allkw[keyword]
            hoshino.logger.warning(
                f"Failed to add keyword trigger `{keyword}`: Conflicts between {sf.__name__} and {other.__name__}"
            )
            return
        self.allkw[keyword] = sf
        hoshino.logger.debug(f"Succeed to add keyword trigger `{keyword}`")

    def find_handler(self, event: CQEvent) -> "ServiceFunc":
        for kw, sf in self.allkw.items():
            text = event.norm_text if sf.normalize_text else event.plain_text
            if kw in text:
                return sf
        return None


class RexTrigger(BaseTrigger):
    def __init__(self):
        super().__init__()
        self.allrex = {}

    def add(self, rex: re.Pattern, sf: "ServiceFunc"):
        self.allrex[rex] = sf
        hoshino.logger.debug(f"Succeed to add rex trigger `{rex.pattern}`")

    def find_handler(self, event: CQEvent) -> "ServiceFunc":
        for rex, sf in self.allrex.items():
            text = event.norm_text if sf.normalize_text else event.plain_text
            match = rex.search(text)
            if match:
                event["match"] = match
                return sf
        return None


class _PlainTextExtractor(BaseTrigger):
    def find_handler(self, event: CQEvent):
        event.plain_text = event.message.extract_plain_text().strip()


class _TextNormalizer(_PlainTextExtractor):
    def find_handler(self, event: CQEvent):
        super().find_handler(event)
        event.norm_text = util.normalize_str(event.plain_text)


prefix = PrefixTrigger()
suffix = SuffixTrigger()
keyword = KeywordTrigger()
rex = RexTrigger()

chain = [
    prefix,
    suffix,
    _TextNormalizer(),
    keyword,
    rex,
]
