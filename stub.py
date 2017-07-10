from cfg import CFG


def non_terminals(grammar):
    return grammar.nonterminals


def as_proper(grammar):
    grammar = grammar.epsilon_free()
    grammar = grammar.without_infertile()
    return grammar


def first(grammar):
    return {s: grammar.first(s) for s in grammar.nonterminals}


def follow(grammar):
    return {s: grammar.follow(s) for s in grammar.nonterminals}


def first_nt(grammar):
    return {s: grammar.first_nonterminal(s) for s in grammar.nonterminals}


def build_parse_table(grammar):
    return grammar.parse_table()
