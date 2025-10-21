from typing import Dict, List, Set, Tuple
from grammar_txt import Grammar

Symbol = str
RHS = Tuple[Symbol, ...]

def is_cnf(g: Grammar) -> bool:
    for A, rhss in g.P.items():
        for rhs in rhss:
            if len(rhs) == 0:
                if A != g.S:
                    return False
                continue

            if len(rhs) == 1:
                s = rhs[0]
                if s not in g.T:
                    return False
                continue

            if len(rhs) == 2:
                B, C = rhs
                if B not in g.V or C not in g.V:
                    return False
                continue

            return False

    return True

def add_new_start(g: Grammar) -> Grammar:
    appears_in_rhs = any(g.S in rhs for rhss in g.P.values() for rhs in rhss)
    if not appears_in_rhs:
        return g 

    S0 = "S0"
    while S0 in g.V or S0 in g.T:
        S0 += "_"

    g.V.add(S0)
    g.P[S0] = [(g.S,)]
    g.S = S0
    return g


def remove_epsilon(g: Grammar) -> Grammar:
    nullable = set()

    changed = True
    while changed:
        changed = False
        for A, rhss in g.P.items():
            for rhs in rhss:
                if len(rhs) == 0 or all(s in nullable for s in rhs):
                    if A not in nullable:
                        nullable.add(A)
                        changed = True

    new_P: Dict[Symbol, List[RHS]] = {}
    for A, rhss in g.P.items():
        new_rules = set()
        for rhs in rhss:
            if len(rhs) == 0:
                continue
            positions = [i for i, s in enumerate(rhs) if s in nullable]
            n = len(positions)
            for mask in range(1 << n):
                new_rhs = [s for i, s in enumerate(rhs)
                           if i not in positions or not (mask & (1 << positions.index(i)))]
                new_rules.add(tuple(new_rhs))
        new_P[A] = list(new_rules)

    if g.S in nullable:
        new_P.setdefault(g.S, []).append(tuple())

    g.P = new_P
    return g


def remove_unit(g: Grammar) -> Grammar:
    new_P: Dict[Symbol, List[RHS]] = {A: [] for A in g.V}

    unit: Dict[Symbol, Set[Symbol]] = {A: {A} for A in g.V}
    changed = True
    while changed:
        changed = False
        for A in g.V:
            for rhs in g.P.get(A, []):
                if len(rhs) == 1 and rhs[0] in g.V:
                    B = rhs[0]
                    if B not in unit[A]:
                        unit[A].add(B)
                        changed = True

    for A in g.V:
        rules = set()
        for B in unit[A]:
            for rhs in g.P.get(B, []):
                if len(rhs) == 1 and rhs[0] in g.V:
                    continue
                rules.add(rhs)
        new_P[A] = list(rules)

    g.P = new_P
    return g


def terminalize_and_binarize(g: Grammar) -> Grammar:
    counter = 1
    term_to_var: Dict[str, str] = {}

    old_productions = dict(g.P)
    new_productions: Dict[Symbol, List[RHS]] = {}

    for A, rhss in old_productions.items():
        updated_rhss = []
        for rhs in rhss:
            if len(rhs) >= 2:
                new_rhs = []
                for s in rhs:
                    if s in g.T:
                        if s not in term_to_var:
                            X = f"T{counter}"
                            counter += 1
                            g.V.add(X)
                            new_productions.setdefault(X, []).append((s,))
                            term_to_var[s] = X
                        new_rhs.append(term_to_var[s])
                    else:
                        new_rhs.append(s)
                updated_rhss.append(tuple(new_rhs))
            else:
                updated_rhss.append(rhs)
        new_productions.setdefault(A, []).extend(updated_rhss)

    final_productions: Dict[Symbol, List[RHS]] = {}
    for A, rhss in new_productions.items():
        for rhs in rhss:
            if len(rhs) <= 2:
                final_productions.setdefault(A, []).append(rhs)
            else:
                symbols = list(rhs)
                prev = symbols[0]
                for i in range(1, len(symbols) - 1):
                    new_var = f"X{counter}"
                    counter += 1
                    g.V.add(new_var)
                    final_productions.setdefault(new_var, []).append((symbols[i], symbols[i + 1]))
                    prev = new_var
                final_productions.setdefault(A, []).append((symbols[0], prev))

    g.P = final_productions
    return g

def to_cnf(g: Grammar) -> Grammar:
    if is_cnf(g):
        print("✔️ La gramática ya está en CNF. No se aplicaron transformaciones.")
        return g

    g = add_new_start(g)
    g = remove_epsilon(g)
    g = remove_unit(g)
    g = terminalize_and_binarize(g)
    return g
