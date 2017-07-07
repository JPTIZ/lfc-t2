from cfg import CFG


def grammar_from(text):
    if text == '5':
        return CFG.create(initial_symbol='S',
                          productions={'S': {'a S a', 'b S b', 'a', 'b'}})
    if text == '7c':
        return CFG.create(initial_symbol='S',
                          productions={'S': {'a A b S', 'aS', 'c'},
                                       'A': {'a A b A', 'c'},
                                      })
    if text == '7d':
        return CFG.create(initial_symbol='S',
                          productions={'S': {'L a R', 'R'},
                                       'L': {'b R', 'i'},
                                       'R': {'L'},
                                      })
    if text == '7e':
        return CFG.create(initial_symbol='S',
                          productions={'S': {'A a A b', 'B b B a'},
                                       'A': {'&'},
                                       'B': {'&'},
                                      })
    return CFG.create(initial_symbol='S',
                      productions={'S': {'&'}})

def non_terminals(grammar):
    return grammar.nonterminals

def as_proper(grammar):
    return grammar

def accept(grammar, text):
    try:
        *_, result = grammar.parse(text)
    except ValueError as e:
        print(f'Rejected. Reason: {e}')
        return False
    return True

def first(grammar):
    return {s: grammar.first(s) for s in grammar.nonterminals}


def follow(grammar):
    return {s: grammar.follow(s) for s in grammar.nonterminals}


def first_nt(grammar):
    return {s: grammar.first_nonterminal(s) for s in grammar.nonterminals}


def build_parse_table(grammar):
    return grammar.parse_table()


class Grammar:
    def __init__(self):
        self.nonterminals = {'S', 'A'}


    '''Stub grammar.'''
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

    def _parse_table_(self):
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
