from dataclasses import dataclass
from typing import Dict, List, Set, Tuple

# Tipos básicos para legibilidad
Symbol = str
RHS = Tuple[Symbol, ...]  # Lado derecho de una producción (tupla de símbolos)


@dataclass
class Grammar:
    # Tipo de datos para almacenar una CFG
    V: Set[Symbol]                 # No terminales
    T: Set[Symbol]                 # Terminales
    S: Symbol                      # Símbolo inicial
    P: Dict[Symbol, List[RHS]]     # Producciones: A -> [alpha1, alpha2, ...]


def load_txt_grammar(path: str) -> Grammar:
    # Función para cargar la gramática desde un TXT con líneas: A -> α1 | α2 | ...
    V: Set[Symbol] = set()
    T: Set[Symbol] = set()
    P: Dict[Symbol, List[RHS]] = {}
    start_symbol: Symbol | None = None

    with open(path, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()

            # Saltar líneas vacías o comentarios
            if not line or line.startswith("#") or line.startswith("//"):
                continue

            # Validar separador ->
            if "->" not in line:
                raise ValueError(f"Línea inválida (falta '->'): {line}")

            # Separar LHS y RHS
            lhs, rhs_part = [x.strip() for x in line.split("->", 1)]
            if not lhs:
                raise ValueError(f"LHS vacío en línea: {line}")

            # Definir símbolo inicial con la primera regla
            if start_symbol is None:
                start_symbol = lhs

            V.add(lhs)  # LHS siempre es no terminal

            # Separar alternativas por '|'
            alternatives = [alt.strip() for alt in rhs_part.split("|") if alt.strip()]
            for alt in alternatives:
                # Manejo de epsilon (e)
                if alt == "e":
                    P.setdefault(lhs, []).append(tuple())
                    continue

                # Tokenizar RHS por espacios
                symbols = alt.split()
                P.setdefault(lhs, []).append(tuple(symbols))

                # Inferir no terminales y terminales (heurística: mayúscula = no terminal)
                for s in symbols:
                    if s == "e":
                        continue
                    if s[0].isupper():
                        V.add(s)
                    else:
                        T.add(s)

    # Validar que se haya definido el símbolo inicial
    if start_symbol is None:
        raise ValueError("No se encontró símbolo inicial (archivo vacío).")

    # Si un símbolo aparece en V y T, priorizarlo como no terminal
    T = {t for t in T if t not in V}

    return Grammar(V=V, T=T, S=start_symbol, P=P)


def pretty_print(g: Grammar) -> str:
    # Función para imprimir la gramática de forma legible
    lines = [
        f"Start symbol: {g.S}",
        "Nonterminals: " + ", ".join(sorted(g.V)),
        "Terminals: " + ", ".join(sorted(g.T)),
        "Productions:"
    ]
    for A in sorted(g.P.keys()):
        right_sides = []
        for rhs in g.P[A]:
            # Mostrar 'e' para epsilon
            if len(rhs) == 0:
                right_sides.append("e")
            else:
                right_sides.append(" ".join(rhs))
        lines.append(f"  {A} -> {' | '.join(right_sides)}")
    return "\n".join(lines)
