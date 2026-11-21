import io, re, subprocess

def ler(p):
    with io.open(p, encoding="utf-8") as f:
        return f.read()

def grava(p, s):
    with io.open(p, "w", encoding="utf-8", newline="\n") as f:
        f.write(s)

p = "app/src/main/res/values/strings.xml"
s = ler(p)
vistos = set()
saida = []
for linha in s.splitlines():
    m = re.search(r'<string\s+name="([^"]+)"', linha)
    if m:
        if m.group(1) in vistos:
            print("  removida repeticao: " + m.group(1))
            continue
        vistos.add(m.group(1))
    saida.append(linha)
grava(p, "\n".join(saida).rstrip() + "\n")

print("\n--- strings.xml final ---")
print(ler(p))

# confere se sobrou duplicata em qualquer values
import glob
for f in glob.glob("app/src/main/res/values*/**/*.xml", recursive=True):
    t = ler(f)
    nomes = re.findall(r'<string\s+name="([^"]+)"', t)
    dup = [n for n in set(nomes) if nomes.count(n) > 1]
    if dup:
        print("  !! ainda duplicado em %s: %s" % (f, dup))

for c in (["git", "add", "-A"],
          ["git", "commit", "-m", "remove strings duplicadas"]):
    r = subprocess.run(c, capture_output=True, text=True)
    print("  $ %s -> %s" % (" ".join(c), r.returncode))
r = subprocess.run(["git", "push"], capture_output=True, text=True)
print("  $ push -> %s" % r.returncode)
for ln in (r.stdout + r.stderr).strip().splitlines()[:8]:
    print("    " + ln)
