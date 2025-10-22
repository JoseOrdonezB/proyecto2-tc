from typing import Dict, List, Set, Tuple
from grammar_txt import Grammar

Symbol = str
RHS = Tuple[Symbol, ...]

def build_cyk_indexes(g: Grammar) -> Tuple[Dict[str, Set[Symbol]], Dict[Tuple[Symbol, Symbol], Set[Symbol]]]:
    terminal_to_vars: Dict[str, Set[Symbol]] = {}
    pair_to_vars: Dict[Tuple[Symbol, Symbol], Set[Symbol]] = {}

    for A, rhss in g.P.items():
        for rhs in rhss:
            if len(rhs) == 1:
                a = rhs[0]
                # Regla A -> a (terminal)
                terminal_to_vars.setdefault(a, set()).add(A)
            elif len(rhs) == 2:
                B, C = rhs
                # Regla A -> B C (binaria)
                pair_to_vars.setdefault((B, C), set()).add(A)
            elif len(rhs) == 0:
                # A -> ε existe (solo válido si A == g.S en CNF)
                pass
            else:
                raise ValueError(f"RHS no-CNF en {A} -> {' '.join(rhs)}")

    return terminal_to_vars, pair_to_vars

def cyk(tokens: List[str], g: Grammar):
    n = len(tokens)

    # Caso especial: cadena vacía
    if n == 0:
        acepta_vacio = any(len(rhs) == 0 for rhs in g.P.get(g.S, []))
        return acepta_vacio, [], {}

    terminal_to_vars, pair_to_vars = build_cyk_indexes(g)

    # Tabla triangular: T[i][j] con 0 <= i <= j < n
    T: List[List[Set[Symbol]]] = [[set() for _ in range(n)] for _ in range(n)]
    back: Dict[Tuple[int, int, Symbol], Tuple] = {}

    # Caso base: substrings de longitud 1
    for i, a in enumerate(tokens):
        for A in terminal_to_vars.get(a, ()):
            T[i][i].add(A)
            back[(i, i, A)] = ('term', a)

    # Substrings de longitud >= 2
    for span in range(2, n + 1):
        for i in range(0, n - span + 1):
            j = i + span - 1
            # dividir en (i..k) y (k+1..j)
            for k in range(i, j):
                left_vars = T[i][k]
                right_vars = T[k + 1][j]
                if not left_vars or not right_vars:
                    continue
                # probar todas las combinaciones B∈left, C∈right
                for B in left_vars:
                    for C in right_vars:
                        for A in pair_to_vars.get((B, C), ()):
                            if A not in T[i][j]:
                                T[i][j].add(A)
                                back[(i, j, A)] = ('split', k, B, C)

    aceptado = (g.S in T[0][n - 1])
    return aceptado, T, back

def reconstruct_tree(back: Dict[Tuple[int, int, Symbol], Tuple], i: int, j: int, A: Symbol):
    kind, *info = back[(i, j, A)]
    if kind == 'term':
        (a,) = info
        return (A, a)
    else:
        k, B, C = info
        left = reconstruct_tree(back, i, k, B)
        right = reconstruct_tree(back, k + 1, j, C)
        return (A, left, right)


def format_brackets(tree) -> str:
    if not isinstance(tree, tuple):
        return str(tree)
    if len(tree) == 2 and isinstance(tree[1], str):
        # (A, 'a')
        return f"({tree[0]} {tree[1]})"
    if len(tree) == 3:
        # (A, left, right)
        return f"({tree[0]} {format_brackets(tree[1])} {format_brackets(tree[2])})"
    # fallback
    return str(tree)
