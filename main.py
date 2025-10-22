import time
from grammar_txt import load_txt_grammar
from cnf import to_cnf
from cyk import cyk, reconstruct_tree, format_brackets

g = load_txt_grammar("1.txt")
original_start = g.S
g = to_cnf(g)

try:
    raw = input("Ingresa la cadena a evaluar: ").strip()
except EOFError:
    raw = ""
tokens = [] if raw == "" else raw.split()

t0 = time.perf_counter()
ok, T, back = cyk(tokens, g)
t1 = time.perf_counter()
elapsed_ms = (t1 - t0) * 1000.0

print("Aceptada:", ok)
print(f"Tiempo de validación (CYK): {elapsed_ms:.3f} ms")

if ok and tokens:
    n = len(tokens)
    root = original_start if original_start in T[0][n-1] else g.S
    tree = reconstruct_tree(back, 0, n - 1, root)

    print("\nÁrbol:")
    print(format_brackets(tree))