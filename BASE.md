# BASE — como este projeto funciona

Documento de referência. Leia antes de mexer em qualquer coisa.

## O que e
Acesso remoto a um Android sem rede local e sem acesso fisico: app de acessibilidade
injeta toques, espelha a tela, le teclado, clipboard, OTP e notificacoes, e responde a
comandos vindos de um painel web.

## Topologia
celular (cliente WebSocket) -> Cloudflare quick tunnel -> server.py :8080 -> painel.html

O celular sempre inicia a conexao para fora. Nada de porta aberta no roteador, nada de
IP fixo, nada de mesma rede.

## Descoberta de endereco (ordem real em Util.candidates)
1. prefs "url" — ultima conexao que funcionou
2. host.txt no raw.githubusercontent.com
3. host.txt no cdn.jsdelivr.net
4. host.txt via api.github.com (Accept: application/vnd.github.raw)
5. broadcast UDP 8089 com payload "AVAL"
6. scan da /24 do proprio IP na porta 8080
7. Cfg.TUNNEL (constante, hoje vazia)

host.txt e escrito por tunel.ps1 e commitado/pushado automaticamente a cada novo tunel.

## Arquivos
- server.py — C2: WebSocket /ws (aparelhos), /panel (operador), /keys, /cofre, /health
- painel.html — interface do operador, servida em /?t=TOKEN
- tunel.ps1 — abre cloudflared, extrai a URL, grava host.txt, commit e push
- servir.ps1 — sobe server.py, espera /health, sobe tunel.ps1, imprime o link
- dump.py — concatena fontes em dump.txt (entrada para outro chat)
- Cfg.java — TOKEN, PORT 8080, DISC 8089, URLs das fontes, id do aparelho
- Net.java — WebSocket com backoff, keepalive 10s, watchdog 35s
- Util.java — descoberta de endereco, dump de dispositivo, exec de shell, lista de bancos
- KeySvc.java — AccessibilityService: toques, gestos, texto, teclado, telas
- ScreenSvc.java — MediaProjection: frames JPEG por binario
- SetupActivity.java — onboarding em 3 passos (restricoes, acessibilidade, sobreposicao)
- Cmd.java — despacho dos comandos recebidos
- OtpSvc.java — NotificationListenerService (OTP)
- Boot.java — reinicia no boot / apos atualizacao
- AndroidManifest.xml — permissoes e componentes

## Rodar o servidor
    .\servir.ps1

Imprime o link do painel com token. Mantenha a janela do tunel aberta.

## Gerar APK
Cada push dispara .github/workflows/build.yml e publica o artifact "apk".
Assinatura: ks.jks, store/key avalaval, alias aval. minSdk 26, targetSdk 34.

## Protocolo
App -> servidor: hello, ka, k (tecla), cred, cartao, otp, clip, pixvisto
Painel -> servidor: sel, info, shot, geo, e os comandos repassados ao Cmd
Binario do app: frames de tela

## Limites conhecidos
- MediaProjection exige consentimento a cada reinicio do aparelho
- banco com FLAG_SECURE fica preto na captura; usar log de teclado
- acessibilidade e obrigatoria e o banco sempre avisa
- apk fora da Play Store sempre passa por "fonte desconhecida"
- Android 13+ exige "permitir configuracoes restritas" nos 3 pontinhos

## Regras para nao quebrar instalacoes existentes
- NAO trocar Cfg.TOKEN (aparelhos instalados param de conectar)
- NAO trocar ks.jks (assinatura diferente = nao atualiza, so desinstalando)
- NAO renomear applicationId com.eloeeducacao
- SEMPRE subir versionCode em app/build.gradle antes de publicar
- entregar diff pontual, nunca reescrever arquivo inteiro sem pedir
- rodar dump.py antes de qualquer mudanca grande
