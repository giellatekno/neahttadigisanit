"""Simple Trie of strings, with no data."""


class Trie:
    def __init__(self):
        self.len = 0
        self.root = {}

    def __contains__(self, word):
        node = Trie._find(self.root, word)
        if not node:
            return False

        return node.get("")

    def __len__(self):
        return self.len

    def add(self, word):
        node = self.root
        for char in word:
            node = node.setdefault(char, {})

        added = node.setdefault("", True)
        if added:
            self.len += 1

    def update(self, words):
        for word in words:
            self.add(word)

    def autocomplete(self, prefix):
        node = Trie._find(self.root, prefix.lower())
        if not node:
            return

        yield from Trie._recurse(node, prefix)

    @staticmethod
    def _find(node, word):
        for char in word:
            try:
                node = node[char]
            except KeyError:
                return
        return node

    @staticmethod
    def _recurse(node, val):
        for k, v in node.items():
            if k == "":
                yield val
            elif isinstance(v, dict):
                yield from Trie._recurse(v, val + k)


if __name__ == "__main__":
    words = ["per", "perra", "perkele", "perkka", "p"]
    trie = Trie()
    trie.update(words)
    assert len(words) == len(trie), f"{len(words)=}, {len(trie)=}"
    for word in words:
        assert word in trie

    prefix_per = list(trie.autocomplete("per"))
    assert set(prefix_per) == set(["per", "perra", "perkele", "perkka"])
