from dataclasses import dataclass
from typing import Dict, List, Set, Tuple

Symbol = str
RHS = Tuple[Symbol, ...]


@dataclass
class Grammar:
    V: Set[Symbol]                 # No terminales
    T: Set[Symbol]                 # Terminales
    S: Symbol                      # Símbolo inicial
    P: Dict[Symbol, List[RHS]]     # Producciones: A -> [alpha1, alpha2, ...]

def load_txt_grammar(path: str) -> Grammar:
    V: Set[Symbol] = set()
    T: Set[Symbol] = set()
    P: Dict[Symbol, List[RHS]] = {}
    start_symbol: Symbol | None = None

    with open(path, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if not line or line.startswith("#") or line.startswith("//"):
                continue

            if "->" not in line:
                raise ValueError(f"Línea inválida (falta '->'): {line}")

            lhs, rhs_part = [x.strip() for x in line.split("->", 1)]
            if not lhs:
                raise ValueError(f"LHS vacío en línea: {line}")

            if start_symbol is None:
                start_symbol = lhs

            V.add(lhs)

            alternatives = [alt.strip() for alt in rhs_part.split("|") if alt.strip()]
            for alt in alternatives:
                if alt == "e":
                    P.setdefault(lhs, []).append(tuple())
                    continue

                symbols = alt.split()
                P.setdefault(lhs, []).append(tuple(symbols))

                for s in symbols:
                    if s == "e":
                        continue
                    if s[0].isupper():
                        V.add(s)
                    else:
                        T.add(s)

    if start_symbol is None:
        raise ValueError("No se encontró símbolo inicial (archivo vacío).")

    T = {t for t in T if t not in V}

    return Grammar(V=V, T=T, S=start_symbol, P=P)


def pretty_print(g: Grammar) -> str:
    lines = [
        f"Start symbol: {g.S}",
        "Nonterminals: " + ", ".join(sorted(g.V)),
        "Terminals: " + ", ".join(sorted(g.T)),
        "Productions:"
    ]
    for A in sorted(g.P.keys()):
        right_sides = []
        for rhs in g.P[A]:
            if len(rhs) == 0:
                right_sides.append("e")
            else:
                right_sides.append(" ".join(rhs))
        lines.append(f"  {A} -> {' | '.join(right_sides)}")
    return "\n".join(lines)
