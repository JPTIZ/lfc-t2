from cfg import CFG


def non_terminals(grammar):
    return grammar.nonterminals


def as_proper(grammar):
    grammar = grammar.epsilon_free()
    #grammar = grammar.without_infertile()
    return grammar


def first(grammar):
    return {s: grammar.first(s) for s in grammar.nonterminals}


def follow(grammar):
    return {s: grammar.follow(s) for s in grammar.nonterminals}


def first_nt(grammar):
    return {s: grammar.first_nonterminal(s) for s in grammar.nonterminals}


def build_parse_table(grammar):
    return grammar.parse_table()


class Grammar:
    '''Stub grammar.'''
    def __init__(self):
        self.nonterminals = {'S', 'A'}

    def make_proper(self):
        return self

    def _first_(self):
        return {'S': {'a', 'b'},
                'A': {'b'}}

    def _follow_(self):
        return {'S': {'$', 'a', 'b'},
                'A': {'a'}}

    def _first_nt_(self):
        return {'S': {'B'},
                'A': {}}

    def parse_table(self):
        return {
                (0, 'a'): {'-'},
                (0, 'b'): {'R1'},
                (0, '$'): {'S2'},
                (0, 'S'): {'2'},
                (0, 'A'): {'1'},
                (1, 'a'): {'HALT'},
                (1, 'b'): {'-'},
                (1, '$'): {'-'},
                (1, 'S'): {'2'},
                (1, 'A'): {'2'},
                (2, 'a'): {'R2'},
                (2, 'b'): {'-'},
                (2, '$'): {'-'},
                (2, 'S'): {'1'},
                (2, 'A'): {'2'},
               }
