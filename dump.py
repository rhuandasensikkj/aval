import io, glob, os
alvos = [f for f in glob.glob("app/src/main/**/*", recursive=True)
         if os.path.isfile(f) and f.endswith((".java", ".xml"))]
alvos += ["app/build.gradle", "server.py"]
with io.open("dump.txt", "w", encoding="utf-8", newline="\n") as o:
    for f in sorted(alvos):
        o.write("\n===== %s =====\n" % f)
        o.write(io.open(f, encoding="utf-8").read())
print("%d arquivos, %d KB" % (len(alvos), os.path.getsize("dump.txt") // 1024))
