import string
from itertools import chain
from typing import Dict, NamedTuple, Set


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
                try:
                    i = production.index(symbol)
                except ValueError:
                    continue

                for y in production[i + 1:]:
                    first = self.first(y)
                    ret |= (first - {'&'})

                    if '&' not in first:
                        break

                # if for never breaks, symbol might be last of production
                else:
                    ret |= self.follow(k)

        return ret

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
