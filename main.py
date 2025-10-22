from grammar_txt import load_txt_grammar
from cnf import to_cnf
from cyk import cyk, reconstruct_tree, format_brackets

g = load_txt_grammar("1.txt")
g = to_cnf(g)

raw = input("Ingresa la cadena a evaluar: ").strip()

tokens = [] if raw == "" else raw.split()

ok, T, back = cyk(tokens, g)
print("Aceptada:", ok)


if ok and len(tokens) > 0:
    n = len(tokens)
    tree = reconstruct_tree(back, 0, n - 1, g.S)
    print(format_brackets(tree))
