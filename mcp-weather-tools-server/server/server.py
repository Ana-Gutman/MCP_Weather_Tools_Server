import json
import socket
import threading
from providers import OpenMeteoProvider

HOST = "127.0.0.1"
PORT = 8787 

def handle_request(req: dict) -> dict:
    tool = req.get("tool"); args = req.get("args", {})
    print(f"[MCP-Server] request: {req}", flush=True)

    if tool == "get_weather":
        q = (args.get("q") or "").strip()
        if not q:
            raise ValueError("Falta parámetro q (ciudad)")
        try:
            g = OpenMeteoProvider.geocode(q)
            w = OpenMeteoProvider.get_current_weather(g["lat"], g["lon"])
            return {"ok": True, "result": {"location": q, **w}}
        except Exception as e:
            raise ValueError(f"Ciudad no encontrada o sin datos ({q})") from e

    if tool == "tools.list":
        return {"ok": True, "result": {
            "tools": [{
                "name": "get_weather",
                "args": {"q": "string"},
                "returns": {"temp_c":"number","humidity":"number?","condition":"string","wind_kph":"number?","updated_at":"string"}
            }]
        }}

    raise ValueError(f"Tool desconocida: {tool}")

def client_thread(conn, addr):
    print(f"[MCP-Server] cliente conectado: {addr}", flush=True)
    try:
        with conn:
            f = conn.makefile(mode="rwb")
            while True:
                try:
                    line = f.readline()
                    if not line:
                        print(f"[MCP-Server] cliente {addr} cerró la conexión.", flush=True)
                        break
                    req = json.loads(line.decode("utf-8").strip())
                    try:
                        resp_body = handle_request(req)
                    except Exception as e:
                        resp_body = {"ok": False, "error": str(e)}
                    resp = {"id": req.get("id"), **resp_body}
                    f.write((json.dumps(resp) + "\n").encode("utf-8")); f.flush()
                except ConnectionResetError:
                    print(f"[MCP-Server] conexión reiniciada por {addr}.", flush=True)
                    break
    except Exception as e:
        print(f"[MCP-Server] hilo {addr} terminó con error: {e}", flush=True)

def main():
    print(f"[MCP-Server] iniciando… HOST={HOST} PORT={PORT}", flush=True)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen(5)
    print(f"[MCP-Server] escuchando en {HOST}:{PORT}", flush=True)
    try:
        while True:
            conn, addr = s.accept()
            print(f"[MCP-Server] accept de {addr}", flush=True)
            threading.Thread(target=client_thread, args=(conn, addr), daemon=True).start()
    finally:
        s.close()

if __name__ == "__main__":
    main()
