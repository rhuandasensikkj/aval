import io, os, re, subprocess

def ler(p):
    with io.open(p, encoding="utf-8") as f:
        return f.read()

def grava(p, s):
    with io.open(p, "w", encoding="utf-8", newline="\n") as f:
        f.write(s)

print("[1] hook do Watch")
k = "app/src/main/java/com/eloeeducacao/KeySvc.java"
s = ler(k)
if "Watch.ev()" in s:
    print("  ja aplicado")
else:
    m = re.search(r"void\s+onAccessibilityEvent\s*\([^)]*\)[^{]*\{", s)
    if m:
        grava(k, s[:m.end()] + "\n        Watch.ev();" + s[m.end():])
        print("  ok  inserido no inicio de onAccessibilityEvent")
    else:
        print("  !! metodo onAccessibilityEvent nao encontrado")

print("[2] versionCode")
b = "app/build.gradle"
s = ler(b)
m = re.search(r"versionCode\s+(\d+)", s)
if m:
    cur = int(m.group(1))
    novo = max(cur + 1, 7)
    grava(b, s[:m.start(1)] + str(novo) + s[m.end(1):])
    print("  ok  versionCode %d -> %d" % (cur, novo))
else:
    print("  !! versionCode nao encontrado")

print("[3] git")
for c in (["git", "add", "-A"],
          ["git", "commit", "-m", "hook do watch e bump de versao"]):
    r = subprocess.run(c, capture_output=True, text=True)
    print("  $ %s -> %s" % (" ".join(c), r.returncode))
print("  $ git pull --rebase --autostash")
r = subprocess.run(["git", "pull", "--rebase", "--autostash"], capture_output=True, text=True)
print("    -> %s" % r.returncode)
print("    " + "\n    ".join((r.stdout + r.stderr).strip().splitlines()[:8]))
print("  $ git push")
r = subprocess.run(["git", "push"], capture_output=True, text=True)
print("    -> %s" % r.returncode)
print("    " + "\n    ".join((r.stdout + r.stderr).strip().splitlines()[:12]))
