import unittest

import io

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

        cfg = CFG.create(
            initial_symbol='S',
            productions={
                'S': {'a S a', 'b S b', 'a', 'b'},
            },
        )
        self.assertEqual({'a', 'b'}, cfg.first('S'))

    def test_first_nt(self):
        cfg = CFG.create(
            initial_symbol='S',
            productions={
                'S': {'A b', 'A B c'},
                'B': {'b B', 'A d', '&'},
                'A': {'a A', '&'},
            },
        )

        self.assertSetEqual({'A', 'B'}, cfg.first_nonterminal('S'))
        self.assertSetEqual({'&'}, cfg.first_nonterminal('A'))
        self.assertSetEqual({'A', '&'}, cfg.first_nonterminal('B'))

        cfg = CFG.create(
            initial_symbol='S',
            productions={
                'S': {'A B C'},
                'A': {'a A', '&'},
                'B': {'b B', 'A C d'},
                'C': {'c C', '&'},
            },
        )

        self.assertSetEqual({'A', 'B', 'C'}, cfg.first_nonterminal('S'))
        self.assertSetEqual({'&'}, cfg.first_nonterminal('A'))
        self.assertSetEqual({'A', 'C'}, cfg.first_nonterminal('B'))
        self.assertSetEqual({'&'}, cfg.first_nonterminal('C'))

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

        cfg = CFG.create(
            initial_symbol='S',
            productions={
                'S': {'a S a', 'b S b', 'a', 'b'},
            },
        )
        self.assertEqual({'a', 'b', '$'}, cfg.follow('S'))

        cfg = CFG.create(
            initial_symbol='S',
            productions={
                'S': {'A a A b', 'B b B a'},
                'A': {'&'},
                'B': {'&'},
            },
        )
        self.assertEqual({'a', 'b'}, cfg.follow('A'))
        self.assertEqual({'a', 'b'}, cfg.follow('B'))

    def test_is_ll1(self):
        cfg = CFG.create(
            initial_symbol='S',
            productions={
                'S': {'a S a', 'b S b', 'a', 'b'}
            }
        )

        self.assertFalse(cfg.is_ll1())

    def test_parse_table(self):
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

        self.assertDictEqual({
            ('E', 'id'): "T E'",
            ('E', '('): "T E'",
            ("E'", ')'): '&',
            ("E'", '+'): "+ T E'",
            ("E'", '$'): '&',
            ('T', 'id'): "F T'",
            ('T', '('): "F T'",
            ("T'", ')'): '&',
            ("T'", '+'): '&',
            ("T'", '*'): "* F T'",
            ("T'", '$'): '&',
            ('F', 'id'): 'id',
            ('F', '('): '( E )',
        }, cfg.parse_table())

    def test_parse(self):
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

        parse = cfg.parse('id + id')

        self.assertTupleEqual((['id', '+', 'id'], ['E']), next(parse))
        self.assertTupleEqual((['id', '+', 'id'], ["E'", 'T']), next(parse))
        self.assertTupleEqual((['id', '+', 'id'], ["E'", "T'", 'F']), next(parse))
        self.assertTupleEqual((['id', '+', 'id'], ["E'", "T'", 'id']), next(parse))
        self.assertTupleEqual((['+', 'id'], ["E'", "T'"]), next(parse))
        self.assertTupleEqual((['+', 'id'], ["E'"]), next(parse))
        self.assertTupleEqual((['+', 'id'], ["E'", 'T', '+']), next(parse))
        self.assertTupleEqual((['id'], ["E'", 'T']), next(parse))
        self.assertTupleEqual((['id'], ["E'", "T'", 'F']), next(parse))
        self.assertTupleEqual((['id'], ["E'", "T'", 'id']), next(parse))
        self.assertTupleEqual(([], ["E'", "T'"]), next(parse))
        self.assertTupleEqual(([], ["E'"]), next(parse))
        self.assertTupleEqual(([], []), next(parse))

        with self.assertRaises(StopIteration):
            next(parse)

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

        cfg = CFG.create(
            initial_symbol='S',
            productions={
                'S': {'A a A b'},
                'A': {'c', '&'},
            },
        )

        fertile = cfg.without_infertile()
        self.assertEqual({
            'S': {'A a A b'},
            'A': {'c', '&'},
        }, fertile.productions)

    def test_load(self):
        buf = io.StringIO("""
            E -> T E'
            E' -> + T E' | &
            T -> F T'
            T' -> * F T' | &
            F -> ( E ) | id
        """)

        cfg = CFG.load(buf)
        self.assertEqual('E', cfg.initial_symbol)
        self.assertDictEqual({
            'E': {"T E'"},
            "E'": {"+ T E'", '&'},
            'T': {"F T'"},
            "T'": {"* F T'", '&'},
            'F': {'( E )', 'id'}
        }, cfg.productions)

        buf = io.StringIO('')
        with self.assertRaises(ValueError):
            CFG.load(buf)

        buf = io.StringIO("""
            S ->
        """)
        with self.assertRaises(ValueError):
            CFG.load(buf)


if __name__ == '__main__':
    unittest.main()
