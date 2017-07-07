import string
from itertools import chain
from typing import Dict, NamedTuple, Set, Tuple


class CFG(NamedTuple):
    initial_symbol: str
    productions: Dict[str, Set[str]]
    nonterminals: Set[str]
    terminals: Set[str]

    def first(self, symbol: str) -> Set[str]:
        # first of terminal is itself
        if symbol not in self.nonterminals:
            return {symbol}

        first = set()
        if '&' in self.productions[symbol]:
            first |= {'&'}

        for production in (p.split() for p in self.productions[symbol]):
            # compute transitive closure of first(yn)
            for y in production:
                first_y = self.first(y)
                first |= (first_y - {'&'})

                if '&' not in first_y:
                    break

            # if for never breaks, & in first(yk)
            else:
                first |= {'&'}

        return first

    def first_nonterminal(self, symbol: str) -> Set[str]:
        if symbol in self.terminals:
            return set()

        if symbol == '&':
            return {symbol}

        first = set()
        if '&' in self.productions[symbol]:
            first |= {'&'}

        for production in (p.split() for p in self.productions[symbol]):
            # compute transitive closure of first_nonterminal(yn)
            for y in production:
                if y in self.nonterminals:
                    first |= {y}

                first_y = self.first_nonterminal(y)
                first |= (first_y - {'&'})

                if '&' not in first_y:
                    break

            # if for never breaks, & in first(yk)
            else:
                first |= {'&'}

        return first

    def follow(self, symbol: str) -> Set[str]:
        ret = set()
        if symbol == self.initial_symbol:
            ret |= {'$'}

        for k, v in self.productions.items():
            if k == symbol:
                continue

            for production in (p.split() for p in v):
                i = -1
                while True:
                    try:
                        i = production.index(symbol, i+1)
                    except ValueError:
                        break

                    for y in production[i + 1:]:
                        first = self.first(y)
                        ret |= (first - {'&'})

                        if '&' not in first:
                            break

                    # if for never breaks, symbol might be last of production
                    else:
                        ret |= self.follow(k)

        return ret

    def is_ll1(self) -> bool:
        def has_left_recursion() -> bool:
            for x in self.nonterminals:
                if x in self.first_nonterminal(x):
                    return True
            return False

        def is_factored() -> bool:
            for y in self.productions.values():
                if len(y) != len(set(production[0] for production in y)):
                    return False
            return True

        def has_ambiguity():
            for x in self.nonterminals:
                first = self.first(x)
                if '&' not in first:
                    continue

                if first & self.follow(x):
                    return True
            return False

        return not has_left_recursion() and is_factored() and not has_ambiguity()

    def parse_table(self) -> Dict[Tuple[str, str], str]:
        table = {}

        for nt, p in ((x, y) for x, v in self.productions.items() for y in v):
            symbols = p.split(maxsplit=1)
            first = self.first(symbols[0])

            for t in (first - {'&'}):
                table[(nt, t)] = p

            while '&' in first:
                if len(symbols) > 1:
                    symbols = symbols[1].split(maxsplit=1)
                    symbol = symbols[0]
                    first = self.first(symbol)
                    for t in self.first(symbol):
                        table[(nt, t)] = p
                else:
                    for t in self.follow(nt):
                        table[(nt, t)] = p
                    break

        return table

    def parse(self, sentence: str):
        table = self.parse_table()

        sentence = list(sentence) + ['$']
        stack = ['$', self.initial_symbol]

        yield sentence[:-1], stack[1:]

        while True:
            front, top = sentence[0], stack.pop()

            # we stacked empty symbol
            if top == '&':
                continue

            # sentence is over
            if top == front == '$':
                break

            if top in self.terminals:
                if top != front:
                    raise ValueError(f'{top} != {front}')

                _, *sentence = sentence

            else:
                rule = table.get((top, front))
                if rule:
                    if rule != '&':
                        stack.extend(reversed(rule.split()))

                else:
                    raise ValueError(f'there is no ({top}, {front}) in parse table')

            yield sentence[:-1], stack[1:]

    def without_infertile(self):
        def fertile(ni):
            for symbol in ni:
                yield symbol

            allowed = ni | self.terminals
            for symbol, productions in self.productions.items():
                for production in productions:
                    if set(production) <= allowed:
                        yield symbol

        ni, next_ni = set(), set(fertile(set()))
        while ni != next_ni:
            ni, next_ni = set(next_ni), set(fertile(next_ni))

        fertile = ni | self.terminals
        return self.create(
            initial_symbol=self.initial_symbol,
            productions={
                symbol: {
                    production
                    for production in productions
                    if all(v in fertile for v in production.split())
                }
                for symbol, productions in self.productions.items()
                if symbol in fertile
            }
        )

    def __str__(self):
        alphabet = self.initial_symbol + string.ascii_letters + '& '

        def key(word):
            return [alphabet.index(c) for c in word]

        output = []
        for symbol in sorted(self.productions.keys(), key=key):
            productions = sorted(self.productions[symbol], key=key)
            output.append(f"{symbol} -> {' | '.join(productions)}")

        return "<CFG initial_symbol='{}' productions={{\n\t{}\n}}>".format(
            self.initial_symbol,
            '\n\t'.join(output),
        )

    @classmethod
    def create(cls, initial_symbol: str, productions: Dict[str, Set[str]]):
        nonterminals = set(productions.keys())

        return cls(
            initial_symbol=initial_symbol,
            productions=productions,
            nonterminals=nonterminals,
            terminals={
                symbol
                for production in chain.from_iterable(productions.values())
                for symbol in production.split()
                if symbol != '&' and symbol not in nonterminals
            }
        )
