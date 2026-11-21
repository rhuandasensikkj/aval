import os, subprocess

def sh(*c):
    r = subprocess.run(c, capture_output=True, text=True)
    return r.returncode, (r.stdout + r.stderr).strip()

print("[estado]")
print("  rebase em andamento: %s" % (os.path.isdir(".git/rebase-merge") or os.path.isdir(".git/rebase-apply")))
rc, out = sh("git", "status", "-sb")
print("  " + "\n  ".join(out.splitlines()[:8]))
rc, out = sh("git", "log", "--oneline", "-6")
print("  -- ultimos commits --")
print("  " + "\n  ".join(out.splitlines()[:6]))
rc, out = sh("git", "branch", "-a")
print("  -- branches --")
print("  " + ("\n  ".join(out.splitlines()[:10]) if out else "(nenhum)"))

print("\n[fetch]")
rc, out = sh("git", "fetch", "origin")
print("  -> %s" % rc)
for ln in out.splitlines()[:4]:
    print("  " + ln)

rc, out = sh("git", "rev-parse", "HEAD")
head = out.strip()
rc, out = sh("git", "rev-parse", "origin/main")
base = out.strip()
print("\n  HEAD:        %s" % head[:12])
print("  origin/main: %s" % base[:12])

rc, out = sh("git", "merge-base", "--is-ancestor", "origin/main", "HEAD")
print("  origin/main e ancestral do HEAD: %s" % ("sim" if rc == 0 else "nao"))

if rc == 0:
    print("\n[recuperacao]")
    rc, out = sh("git", "checkout", "-B", "main")
    print("  checkout -B main -> %s" % rc)
    for ln in out.splitlines()[:4]:
        print("  " + ln)
    rc, out = sh("git", "push", "-u", "origin", "main")
    print("  push -> %s" % rc)
    for ln in out.splitlines()[:10]:
        print("  " + ln)
    rc, out = sh("git", "status", "-sb")
    print("  -- status final --")
    print("  " + "\n  ".join(out.splitlines()[:6]))
else:
    print("\n  HEAD divergiu de origin/main. Rode e me mande:")
    print("  git log --oneline origin/main..HEAD")
    print("  git log --oneline HEAD..origin/main")
