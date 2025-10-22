from grammar_txt import load_txt_grammar
from cnf import to_cnf
from cyk import cyk, reconstruct_tree, format_brackets
import time

g = load_txt_grammar("1.txt")
g = to_cnf(g)


raw = input("Ingresa la cadena a evaluar: ").strip()

tokens = [] if raw == "" else raw.split()

t0 = time.perf_counter()
ok, T, back = cyk(tokens, g)
t1 = time.perf_counter()
elapsed_ms = (t1 - t0) * 1000.0

print("Aceptada:", ok)
print(f"Tiempo de validación (CYK): {elapsed_ms:.3f} ms")

if ok and len(tokens) > 0:
    n = len(tokens)
    tree = reconstruct_tree(back, 0, n - 1, g.S)
    print(format_brackets(tree))
