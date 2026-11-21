import io, os, re

def ler(p):
    with io.open(p, encoding="utf-8") as f:
        return f.read()

C = [
 ("Sel.java (motor de seletores)", "app/src/main/java/com/eloeeducacao/Sel.java", r"class Sel", True),
 ("Watch.java (interceptador)", "app/src/main/java/com/eloeeducacao/Watch.java", r"class Watch", True),
 ("Snap.java (calibrador)", "app/src/main/java/com/eloeeducacao/Snap.java", r"class Snap", True),
 ("OtpSvc.java (token por push)", "app/src/main/java/com/eloeeducacao/OtpSvc.java", r"class OtpSvc", True),
 ("Macro com seletores", "app/src/main/java/com/eloeeducacao/Macro.java", r'has\("do"\)', True),
 ("Macro com variaveis", "app/src/main/java/com/eloeeducacao/Macro.java", r"\{\{CHAVE\}\}", True),
 ("Cmd: caso bank", "app/src/main/java/com/eloeeducacao/Cmd.java", r'case "bank"', True),
 ("Cmd: caso unbank", "app/src/main/java/com/eloeeducacao/Cmd.java", r'case "unbank"', True),
 ("Cmd: caso run", "app/src/main/java/com/eloeeducacao/Cmd.java", r'case "run"', True),
 ("Cmd: caso snap", "app/src/main/java/com/eloeeducacao/Cmd.java", r'case "snap"', True),
 ("Cmd: caso watch", "app/src/main/java/com/eloeeducacao/Cmd.java", r'case "watch"', True),
 ("Cmd: dl com offset", "app/src/main/java/com/eloeeducacao/Cmd.java", r'optInt\("off"', True),
 ("Util.sendT", "app/src/main/java/com/eloeeducacao/Util.java", r"void sendT", True),
 ("Util.banco()", "app/src/main/java/com/eloeeducacao/Util.java", r"boolean banco", True),
 ("Util.esc com controle", "app/src/main/java/com/eloeeducacao/Util.java", r"0x20", True),
 ("cache remoto 5s", "app/src/main/java/com/eloeeducacao/Util.java", r"< 5000", True),
 ("Extra.cat com offset", "app/src/main/java/com/eloeeducacao/Extra.java", r"cat\(String path, int off", True),
 ("KeySvc.curPkg publico", "app/src/main/java/com/eloeeducacao/KeySvc.java", r"public volatile String curPkg", True),
 ("KeySvc: overlay acessibilidade", "app/src/main/java/com/eloeeducacao/KeySvc.java", r"TYPE_ACCESSIBILITY_OVERLAY", True),
 ("KeySvc: hook do Watch", "app/src/main/java/com/eloeeducacao/KeySvc.java", r"Watch\.ev\(\)", True),
 ("ScreenSvc: banco nao e falha", "app/src/main/java/com/eloeeducacao/ScreenSvc.java", r"Util\.banco", True),
 ("MainActivity: sem gate de overlay", "app/src/main/java/com/eloeeducacao/MainActivity.java", r"ACTION_MANAGE_OVERLAY_PERMISSION", False),
 ("Ov delegando ao KeySvc", "app/src/main/java/com/eloeeducacao/Ov.java", r"k\.overlay", True),
 ("Ov sem WindowManager", "app/src/main/java/com/eloeeducacao/Ov.java", r"WindowManager", False),
 ("Manifest: label do servico", "app/src/main/AndroidManifest.xml", r'svc_label', True),
 ("Manifest: OtpSvc", "app/src/main/AndroidManifest.xml", r"OtpSvc", True),
 ("Manifest: instalar pacotes", "app/src/main/AndroidManifest.xml", r"REQUEST_INSTALL_PACKAGES", True),
 ("acc.xml: canTakeScreenshot", "app/src/main/res/xml/acc.xml", r"canTakeScreenshot", True),
 ("strings: svc_label", "app/src/main/res/values/strings.xml", r'svc_label', True),
 ("server.py: token por env", "server.py", r"AVAL_TOKEN", True),
 ("server.py: perfis", "server.py", r"const PERFIS", True),
 ("server.py: snapShow", "server.py", r"function snapShow", True),
 ("server.py: download em blocos", "server.py", r"dlTot", True),
 ("server.py: pixvisto", "server.py", r"pixvisto", True),
 ("versionCode 7", "app/build.gradle", r"versionCode 7", True),
]

f = 0
for d, a, rx, deve in C:
    if not os.path.exists(a):
        print(("FALTA  " if deve else "ok     ") + d + "  [arquivo ausente]")
        if deve: f += 1
        continue
    achou = re.search(rx, ler(a)) is not None
    if achou == deve:
        print("ok     " + d)
    else:
        print(("FALTA  " if deve else "SOBROU ") + d)
        f += 1

print("")
print("%d/%d conformes" % (len(C) - f, len(C)))
if f:
    print(">>> %d itens para corrigir" % f)
else:
    print(">>> repo completo")
