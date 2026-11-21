import io, os, re, subprocess

def ler(p):
    with io.open(p, encoding="utf-8") as f:
        return f.read()

def grava(p, s):
    with io.open(p, "w", encoding="utf-8", newline="\n") as f:
        f.write(s)

M = "app/src/main/AndroidManifest.xml"
s = ler(M)

print("[1] MainActivity exportado=false")
m = re.search(r'<activity\s[^>]*?\.MainActivity"[^>]*?/>', s, re.S)
if not m:
    print("  !! tag do MainActivity nao encontrada")
else:
    t = m.group(0)
    if 'android:exported="false"' in t:
        print("  ja aplicado")
    else:
        t2 = re.sub(r'\s*android:exported="[^"]*"', "", t)
        t2 = t2[:-2].rstrip() + '\n        android:exported="false" />'
        grava(M, s.replace(t, t2, 1))
        print("  ok  MainActivity fechado")

print("[2] conferencia do manifest")
s = ler(M)
for nome, rx in (
        ("SetupActivity declarada", r'<activity\s[^>]*?\.SetupActivity'),
        ("alias aponta para Setup", r'targetActivity="\.SetupActivity"'),
        ("MainActivity fechado", r'<activity\s[^>]*?\.MainActivity"[^>]*?exported="false"')):
    print(("  ok   " if re.search(rx, s, re.S) else "  FALTA ") + nome)

print("[3] git")
for c in (["git", "add", "-A"],
          ["git", "commit", "-m", "fecha MainActivity, setup guiada sem loja"]):
    r = subprocess.run(c, capture_output=True, text=True)
    print("  $ %s -> %s" % (" ".join(c), r.returncode))
r = subprocess.run(["git", "pull", "--rebase", "--autostash"], capture_output=True, text=True)
print("  $ pull --rebase -> %s" % r.returncode)
for ln in (r.stdout + r.stderr).strip().splitlines()[:6]:
    print("    " + ln)
r = subprocess.run(["git", "push"], capture_output=True, text=True)
print("  $ push -> %s" % r.returncode)
for ln in (r.stdout + r.stderr).strip().splitlines()[:12]:
    print("    " + ln)
