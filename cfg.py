import logging
import string
from itertools import chain
from typing import Dict, NamedTuple, Set, Tuple, TextIO

logger = logging.getLogger(__name__)


class CFG(NamedTuple):
    initial_symbol: str
    productions: Dict[str, Set[str]]
    nonterminals: Set[str]
    terminals: Set[str]

    def first(self, sentence: str) -> Set[str]:
        first = set()

        # compute transitive closure of first(yn)
        for y in sentence.split():
            # first of terminal is itself
            if y not in self.nonterminals:
                return first | {y}

            first_y = set()
            for x in self.productions[y]:
                first_y |= self.first(x)

            first |= (first_y - {'&'})

            if '&' not in first_y:
                return first

        # if for never breaks, & in first(yk)
        return first | {'&'}

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
            for symbol in p.split():
                first = self.first(symbol)

                for t in (first - {'&'}):
                    table[(nt, t)] = p

                if '&' not in first:
                    break
            else:
                for t in self.follow(symbol):
                    table[(nt, t)] = p

        return table

    def parse(self, sentence: str):
        table = self.parse_table()

        sentence = sentence.split() + ['$']
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

    @classmethod
    def load(cls, fp: TextIO):
        initial_symbol, productions = None, {}

        for line in fp:
            line = line.strip()
            if not line:
                continue

            if '->' not in line:
                logger.warning(f'Invalid line, skipping: {line}')
                continue

            x, y = [s.strip() for s in line.split('->', maxsplit=1)]
            if not x:
                logger.warning(f'Invalid symbol, skipping: {x}')
                continue

            if '->' in y:
                logger.warning(f'Invalid productions, skipping')
                continue

            if not initial_symbol:
                initial_symbol = x

            def filter_productions(productions):
                for p in productions.split('|'):
                    q = p.strip()
                    if not q:
                        logger.warning(f'Empty production, skipping...')
                        continue

                    yield q

            y = set(filter_productions(y))
            if not y:
                logger.warning(f'Symbol with no productions, skipping...')
                continue

            productions[x] = y

        if not initial_symbol:
            raise ValueError('Grammar with no symbols!')

        if not productions:
            raise ValueError('Grammer with no productions!')

        return cls.create(initial_symbol, productions)
