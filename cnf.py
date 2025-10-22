from typing import Dict, List, Set, Tuple
from grammar_txt import Grammar

# Tipos básicos para legibilidad
Symbol = str
RHS = Tuple[Symbol, ...]   # RHS = lado derecho de una producción (tupla de símbolos)

# Validador de CNF
def is_cnf(g: Grammar) -> bool:
    # Revisa que todas las reglas sean: A->a  |  A->BC  |  S->e
    for A, rhss in g.P.items():
        for rhs in rhss:
            # Caso epsilon: solo permitido si A es el símbolo inicial
            if len(rhs) == 0:
                if A != g.S:
                    return False
                continue

            # Caso terminal único: A -> a (a ∈ T)
            if len(rhs) == 1:
                s = rhs[0]
                if s not in g.T:
                    return False
                continue

            # Caso binario: A -> B C (B,C ∈ V)
            if len(rhs) == 2:
                B, C = rhs
                if B not in g.V or C not in g.V:
                    return False
                continue

            # Cualquier otra forma no es CNF
            return False

    return True

# Nuevo símbolo inicial
def add_new_start(g: Grammar) -> Grammar:
    # Si S aparece en alguna RHS, crear S0 -> S para proteger a S
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


# Eliminar ε-producciones
def remove_epsilon(g: Grammar) -> Grammar:
    # Encuentra símbolos anulables y genera variantes sin ellos
    nullable = set()

    # 1) Marcar anulables por cierre
    changed = True
    while changed:
        changed = False
        for A, rhss in g.P.items():
            for rhs in rhss:
                if len(rhs) == 0 or all(s in nullable for s in rhs):
                    if A not in nullable:
                        nullable.add(A)
                        changed = True

    # 2) Crear nuevas RHS removiendo opcionalmente símbolos anulables
    new_P: Dict[Symbol, List[RHS]] = {}
    for A, rhss in g.P.items():
        new_rules = set()
        for rhs in rhss:
            if len(rhs) == 0:
                continue  # quitamos A->e (se maneja aparte para S)
            positions = [i for i, s in enumerate(rhs) if s in nullable]
            n = len(positions)
            for mask in range(1 << n):
                # Construir RHS eliminando las posiciones elegidas en 'mask'
                new_rhs = [s for i, s in enumerate(rhs)
                           if i not in positions or not (mask & (1 << positions.index(i)))]
                new_rules.add(tuple(new_rhs))
        new_P[A] = list(new_rules)

    # Permitir S->e si S era anulable
    if g.S in nullable:
        new_P.setdefault(g.S, []).append(tuple())

    g.P = new_P
    return g

# Eliminar unitarias A->B
def remove_unit(g: Grammar) -> Grammar:
    # Usa clausura unitaria para sustituir A->B por reglas de B (no unitarias)
    new_P: Dict[Symbol, List[RHS]] = {A: [] for A in g.V}

    # Clausura unitaria: para cada A, a qué B llega por unitarias
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

    # Copiar reglas no unitarias de todos los B alcanzables
    for A in g.V:
        rules = set()
        for B in unit[A]:
            for rhs in g.P.get(B, []):
                if len(rhs) == 1 and rhs[0] in g.V:
                    continue  # saltar unitarias
                rules.add(rhs)
        new_P[A] = list(rules)

    g.P = new_P
    return g

# Terminalizar y binarizar
def terminalize_and_binarize(g: Grammar) -> Grammar:
    # Reemplaza terminales en RHS largas y binariza RHS de tamaño > 2
    counter = 1
    term_to_var: Dict[str, str] = {}

    # Copia de producciones para no mutar mientras iteramos
    old_productions = dict(g.P)
    new_productions: Dict[Symbol, List[RHS]] = {}

    # 1) Terminalización: A-> ... a ...  (en RHS de largo>=2)  => usa T1->a, T1 en RHS
    for A, rhss in old_productions.items():
        updated_rhss = []
        for rhs in rhss:
            if len(rhs) >= 2:
                new_rhs = []
                for s in rhs:
                    if s in g.T:  # terminal en regla larga
                        if s not in term_to_var:
                            X = f"T{counter}"
                            counter += 1
                            g.V.add(X)
                            new_productions.setdefault(X, []).append((s,))  # X->a
                            term_to_var[s] = X
                        new_rhs.append(term_to_var[s])
                    else:
                        new_rhs.append(s)
                updated_rhss.append(tuple(new_rhs))
            else:
                updated_rhss.append(rhs)
        new_productions.setdefault(A, []).extend(updated_rhss)

    # 2) Binarización: A->B C D ...  => introduce variables intermedias
    final_productions: Dict[Symbol, List[RHS]] = {}
    for A, rhss in new_productions.items():
        for rhs in rhss:
            if len(rhs) <= 2:
                final_productions.setdefault(A, []).append(rhs)
            else:
                # Encadena variables nuevas para dejar solo pares
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


# Pipeline a CNF (con validación previa)
def to_cnf(g: Grammar) -> Grammar:
    # Si ya está en CNF, no tocar
    if is_cnf(g):
        print("✔️ La gramática ya está en CNF. No se aplicaron transformaciones.")
        return g

    # Orden estándar: nuevo start -> epsilon -> unitarias -> terminalizar/binarizar
    g = add_new_start(g)
    g = remove_epsilon(g)
    g = remove_unit(g)
    g = terminalize_and_binarize(g)
    return g
