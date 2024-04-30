"""Simple Trie of strings, where paths are stored lower-cased, and the end
node contains the original string (with capitalization)."""


class Trie:
    def __init__(self):
        self.len = 0
        self.root = {}

    def __contains__(self, word):
        node = self._find(word)
        if not node:
            return False

        return node.get("")

    def __len__(self):
        return self.len

    def add(self, word):
        node = self.root
        for char in word.lower():
            node = node.setdefault(char, {})

        # store the original, non-lowercased word under the "" key
        added = node.setdefault("", word)
        if added:
            self.len += 1

    def update(self, words):
        for word in words:
            self.add(word)

    def autocomplete(self, prefix):
        node = self._find(prefix.lower())
        if not node:
            return

        yield from Trie._recurse(node, prefix)

    def _find(self, word):
        node = self.root
        for char in word:
            try:
                node = node[char]
            except KeyError:
                try:
                    node = node[char.lower()]
                except KeyError:
                    return
        return node

    @staticmethod
    def _recurse(node, val):
        for k, v in node.items():
            if k == "":
                # reached terminal node, return the value
                yield v
            elif isinstance(v, dict):
                yield from Trie._recurse(v, val + k)


if __name__ == "__main__":
    import unittest

    class Tests(unittest.TestCase):
        def test_basic(self):
            trie = Trie()
            words = ["per", "perra", "perkele", "perkka", "p"]
            trie.update(words)
            self.assertEqual(len(set(words)), len(trie))
            for word in words:
                self.assertIn(word, trie)

            prefix_per = list(trie.autocomplete("per"))
            self.assertEqual(
                set(prefix_per), set(["per", "perra", "perkele", "perkka"])
            )

        def test_propernoun(self):
            words = ["Trond", "Tromsø", "tromme", "trommehinne", "Troms", "tro"]
            trie = Trie()
            trie.update(words)
            self.assertEqual(len(words), len(trie))
            expected = set(["tro", "tromme", "trommehinne", "Troms", "Tromsø", "Trond"])
            actual = set(trie.autocomplete("tro"))
            self.assertEqual(expected, actual)

    unittest.main()
