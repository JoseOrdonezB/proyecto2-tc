from grammar_txt import load_txt_grammar, pretty_print
from cnf import to_cnf

g = load_txt_grammar("1.txt")

print("=== Gramática Original ===")
print(pretty_print(g))


cnf = to_cnf(g)

print("=== Gramática despues de CNF ===")
print(pretty_print(cnf))
