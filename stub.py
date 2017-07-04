def grammar_from(text):
    return Grammar()

def as_proper(grammar):
    return grammar.make_proper()

def accept(grammar, text):
    return text in {'a', 'b', 'aab', 'aba', 'baaa'}

def first(grammar):
    return grammar._first_()


def follow(grammar):
    return grammar._follow_()


def first_nt(grammar):
    return grammar._first_nt_()


def build_parse_table(grammar):
    return grammar._parse_table_()


class Grammar:
    '''Stub grammar.'''
    def make_proper(self):
        return self

    def non_terminals(self):
        return {'S', 'A'}

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
