import unittest

from cfg import CFG


class CFGTest(unittest.TestCase):
    def test_nonterminals(self):
        cfg = CFG.create(
            initial_symbol='S',
            productions={
                'S': {'a A', '&'},
                'A': {'b S'},
            },
        )

        self.assertSetEqual({'S', 'A'}, cfg.nonterminals)

    def test_terminals(self):
        cfg = CFG.create(
            initial_symbol='S',
            productions={
                'S': {'a A', '&'},
                'A': {'b S'},
            },
        )

        self.assertSetEqual({'a', 'b'}, cfg.terminals)

    def test_first(self):
        cfg = CFG.create(
            initial_symbol='S',
            productions={
                'S': {'A b', 'A B c'},
                'B': {'b B', 'A d', '&'},
                'A': {'a A', '&'},
            },
        )

        self.assertSetEqual({'a', 'b', 'c', 'd'}, cfg.first('S'))
        self.assertSetEqual({'a', '&'}, cfg.first('A'))
        self.assertSetEqual({'a', 'b', 'd', '&'}, cfg.first('B'))

        cfg = CFG.create(
            initial_symbol='S',
            productions={
                'S': {'A B C'},
                'A': {'a A', '&'},
                'B': {'b B', 'A C d'},
                'C': {'c C', '&'},
            },
        )

        self.assertSetEqual({'a', 'b', 'c', 'd'}, cfg.first('S'))
        self.assertSetEqual({'a', '&'}, cfg.first('A'))
        self.assertSetEqual({'a', 'b', 'c', 'd'}, cfg.first('B'))
        self.assertSetEqual({'c', '&'}, cfg.first('C'))

    def test_follow(self):
        cfg = CFG.create(
            initial_symbol='S',
            productions={
                'S': {'A B C'},
                'A': {'a A', '&'},
                'B': {'b B', 'A C d'},
                'C': {'c C', '&'},
            },
        )

        self.assertSetEqual({'$'}, cfg.follow('S'))
        self.assertSetEqual({'a', 'b', 'c', 'd'}, cfg.follow('A'))
        self.assertSetEqual({'c', '$'}, cfg.follow('B'))
        self.assertSetEqual({'d', '$'}, cfg.follow('C'))

        cfg = CFG.create(
            initial_symbol='E',
            productions={
                'E': {"T E'"},
                "E'": {"+ T E'", '&'},
                'T': {"F T'"},
                "T'": {"* F T'", '&'},
                'F': {'( E )', 'id'}
            },
        )

        self.assertSetEqual({')', '$'}, cfg.follow('E'))
        self.assertSetEqual({')', '$'}, cfg.follow("E'"))
        self.assertSetEqual({'+', ')', '$'}, cfg.follow('T'))
        self.assertSetEqual({'+', ')', '$'}, cfg.follow("T'"))
        self.assertSetEqual({'*', '+', ')', '$'}, cfg.follow("F"))

    def test_without_infertile(self):
        cfg = CFG.create(
            initial_symbol='S',
            productions={
                'S': {'a A', 'a'},
                'A': {'a A'},
            },
        )

        fertile = cfg.without_infertile()
        self.assertEqual('S', fertile.initial_symbol)
        self.assertDictEqual({
            'S': {'a'}
        }, fertile.productions)


if __name__ == '__main__':
    unittest.main()
