import io, os, re, subprocess

def ler(p):
    with io.open(p, encoding="utf-8") as f:
        return f.read()

def grava(p, s):
    with io.open(p, "w", encoding="utf-8", newline="\n") as f:
        f.write(s)

print("[1] corrige variavel duplicada no KeySvc")
K = "app/src/main/java/com/eloeeducacao/KeySvc.java"
s = ler(K)
novo, n = re.subn(r"catch \(Throwable t\)(\s*\{\s*lp\.type)", r"catch (Throwable th)\1", s)
if n:
    grava(K, novo)
    print("  ok  %d ocorrencia(s) renomeada(s)" % n)
else:
    print("  ja aplicado")

print("[2] varredura de riscos")
import glob
ruim = 0
for f in glob.glob("app/src/main/res/values*/**/*.xml", recursive=True):
    t = ler(f)
    nomes = re.findall(r'<string\s+name="([^"]+)"', t)
    dup = sorted({x for x in nomes if nomes.count(x) > 1})
    if dup:
        print("  !! string duplicada em %s: %s" % (f, dup)); ruim += 1
M = "app/src/main/AndroidManifest.xml"
t = ler(M)
for rx, rot in ((r'<uses-permission android:name="([^"]+)"', "permissao"),
                (r'<activity\s[^>]*android:name="([^"]+)"', "activity"),
                (r'<service\s[^>]*android:name="([^"]+)"', "service")):
    nomes = re.findall(rx, t)
    dup = sorted({x for x in nomes if nomes.count(x) > 1})
    if dup:
        print("  !! %s duplicado no manifest: %s" % (rot, dup)); ruim += 1
for f in glob.glob("app/src/main/java/**/*.java", recursive=True):
    t = ler(f)
    cls = re.findall(r"^\s*(?:public\s+)?(?:final\s+)?class\s+(\w+)", t, re.M)
    dup = sorted({x for x in cls if cls.count(x) > 1})
    if dup:
        print("  !! classe duplicada em %s: %s" % (f, dup)); ruim += 1
    if t.count("{") != t.count("}"):
        print("  !! chaves desbalanceadas em %s (%d/%d)" % (f, t.count("{"), t.count("}")))
        ruim += 1
print("  %s" % ("nada suspeito" if not ruim else "%d risco(s) acima" % ruim))

print("[3] dump completo para revisao")
alvos = []
for base in ("app/src/main", "."):
    for f in glob.glob(os.path.join(base, "**", "*"), recursive=True):
        if not os.path.isfile(f): continue
        if f.startswith(".git"): continue
        if f.endswith((".java", ".xml", ".gradle", ".py")) and "build" not in f.split(os.sep):
            alvos.append(f)
alvos = sorted(set(alvos))
with io.open("dump.txt", "w", encoding="utf-8", newline="\n") as out:
    for f in alvos:
        out.write("\n===== %s =====\n" % f)
        try: out.write(ler(f))
        except Exception as e: out.write("(erro: %s)\n" % e)
print("  ok  dump.txt com %d arquivos (%d KB)" % (len(alvos), os.path.getsize("dump.txt") // 1024))

for c in (["git", "add", "-A"], ["git", "commit", "-m", "corrige variavel duplicada no overlay"]):
    r = subprocess.run(c, capture_output=True, text=True)
    print("  $ %s -> %s" % (" ".join(c), r.returncode))
r = subprocess.run(["git", "push"], capture_output=True, text=True)
print("  $ push -> %s" % r.returncode)
for ln in (r.stdout + r.stderr).strip().splitlines()[:8]:
    print("    " + ln)
