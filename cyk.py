from typing import Dict, List, Set, Tuple
from grammar_txt import Grammar

# Tipos básicos
Symbol = str
RHS = Tuple[Symbol, ...]  # RHS = lado derecho de una producción


# Índices para acelerar CYK
def build_cyk_indexes(g: Grammar) -> Tuple[Dict[str, Set[Symbol]], Dict[Tuple[Symbol, Symbol], Set[Symbol]]]:
    # terminal_to_vars[a] = {A | A->a}; pair_to_vars[(B,C)] = {A | A->BC}
    terminal_to_vars: Dict[str, Set[Symbol]] = {}
    pair_to_vars: Dict[Tuple[Symbol, Symbol], Set[Symbol]] = {}

    for A, rhss in g.P.items():
        for rhs in rhss:
            if len(rhs) == 1:
                a = rhs[0]
                terminal_to_vars.setdefault(a, set()).add(A)   # A -> a
            elif len(rhs) == 2:
                B, C = rhs
                pair_to_vars.setdefault((B, C), set()).add(A)  # A -> B C
            elif len(rhs) == 0:
                pass  # A -> ε (solo si A==S), no indexa
            else:
                # Si aparece algo distinto, no es CNF
                raise ValueError(f"RHS no-CNF en {A} -> {' '.join(rhs)}")

    return terminal_to_vars, pair_to_vars


# Algoritmo CYK (DP bottom-up)
def cyk(tokens: List[str], g: Grammar):
    # Devuelve: (aceptado, tabla T, backpointers)
    n = len(tokens)

    # Caso cadena vacía: aceptar sólo si S -> ε
    if n == 0:
        acepta_vacio = any(len(rhs) == 0 for rhs in g.P.get(g.S, []))
        return acepta_vacio, [], {}

    terminal_to_vars, pair_to_vars = build_cyk_indexes(g)

    # T[i][j]: conjunto de variables que generan tokens[i..j]
    T: List[List[Set[Symbol]]] = [[set() for _ in range(n)] for _ in range(n)]
    # back[(i,j,A)] = lista de ('term', a) o ('split', k, B, C)
    back: Dict[Tuple[int, int, Symbol], List[Tuple]] = {}

    # Base: substrings de longitud 1
    for i, a in enumerate(tokens):
        for A in terminal_to_vars.get(a, ()):
            T[i][i].add(A)
            back.setdefault((i, i, A), []).append(('term', a))

    # Combinar spans de 2..n
    for span in range(2, n + 1):
        for i in range(0, n - span + 1):
            j = i + span - 1
            for k in range(i, j):
                left_vars = T[i][k]
                right_vars = T[k + 1][j]
                if not left_vars or not right_vars:
                    continue
                # Para toda pareja (B,C) presente, agregar A con A->BC
                for B in left_vars:
                    for C in right_vars:
                        for A in pair_to_vars.get((B, C), ()):
                            if A not in T[i][j]:
                                T[i][j].add(A)
                            back.setdefault((i, j, A), []).append(('split', k, B, C))

    aceptado = (g.S in T[0][n - 1])
    return aceptado, T, back

# Reconstrucción de UN árbol
def reconstruct_tree(back: Dict[Tuple[int, int, Symbol], List[Tuple]], i: int, j: int, A: Symbol):
    # Toma la primera alternativa guardada para (i,j,A)
    opts = back.get((i, j, A))
    if not opts:
        raise ValueError(f"No hay backpointer para ({i},{j},{A})")
    kind, *info = opts[0]
    if kind == 'term':
        (a,) = info
        return (A, a)  # hoja: A -> a
    else:
        k, B, C = info
        left = reconstruct_tree(back, i, k, B)
        right = reconstruct_tree(back, k + 1, j, C)
        return (A, left, right)  # nodo binario: A -> B C

# Reconstrucción de TODOS los árboles
def reconstruct_all(back: Dict[Tuple[int, int, Symbol], List[Tuple]], i: int, j: int, A: Symbol):
    # Generador que recorre todas las alternativas en (i,j,A)
    for opt in back.get((i, j, A), []):
        kind, *info = opt
        if kind == 'term':
            (a,) = info
            yield (A, a)
        else:
            k, B, C = info
            for left in reconstruct_all(back, i, k, B):
                for right in reconstruct_all(back, k + 1, j, C):
                    yield (A, left, right)

# Impresión en formato brackets
def format_brackets(tree) -> str:
    # (A a) para hojas y (A (..) (..)) para nodos binarios
    if not isinstance(tree, tuple):
        return str(tree)
    if len(tree) == 2 and isinstance(tree[1], str):
        return f"({tree[0]} {tree[1]})"
    if len(tree) == 3:
        return f"({tree[0]} {format_brackets(tree[1])} {format_brackets(tree[2])})"
    return str(tree)
