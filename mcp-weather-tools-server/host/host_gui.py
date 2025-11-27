import json
import socket
import threading
import queue
import tkinter as tk
from tkinter import ttk, messagebox

HOST = "127.0.0.1"
PORT = 8787

class MCPClient:
    def __init__(self, host, port):
        self.host, self.port = host, port
        self.sock = None
        self.file = None
        self.lock = threading.Lock()
        self.counter = 0
        self.recv_queue = queue.Queue()

    def connect(self):
        self.sock = socket.create_connection((self.host, self.port), timeout=5)
        self.sock.settimeout(None)
        self.file = self.sock.makefile(mode="rwb")
        threading.Thread(target=self._reader, daemon=True).start()

    def _reader(self):
        try:
            while True:
                line = self.file.readline()
                if not line:
                    break
                data = json.loads(line.decode("utf-8").strip())
                self.recv_queue.put(data)
        except Exception as e:
            self.recv_queue.put({"id": None, "ok": False, "error": f"Desconectado: {e}"})

    def call_tool(self, tool: str, args: dict) -> str:
        with self.lock:
            self.counter += 1
            rid = str(self.counter)
            req = {"id": rid, "tool": tool, "args": args}
            self.file.write((json.dumps(req) + "\n").encode("utf-8"))
            self.file.flush()
            return rid

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Clima – MCP Host")
        self.geometry("480x320")
        self.client = MCPClient(HOST, PORT)
        self.connected = False
        self._build_ui()
        self.after(200, self._poll_responses)
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_ui(self):
        pad = {"padx": 10, "pady": 6}
        frm = ttk.Frame(self); frm.pack(fill="both", expand=True, **pad)

        self.status = ttk.Label(frm, text="Estado: Desconectado")
        self.status.pack(anchor="w", **pad)

        top = ttk.Frame(frm); top.pack(fill="x", **pad)
        ttk.Label(top, text="Ciudad:").pack(side="left")
        self.entry_city = ttk.Entry(top, width=28)
        self.entry_city.pack(side="left", padx=6)
        self.entry_city.insert(0, "Montevideo")

        self.btn_connect = ttk.Button(top, text="Conectar", command=self.on_connect)
        self.btn_connect.pack(side="left", padx=4)

        self.btn_get = ttk.Button(top, text="Consultar",
                                  command=self.on_get, state="disabled")
        self.btn_get.pack(side="left", padx=4)

        # --- Auto-actualización ---
        ref = ttk.Frame(frm); ref.pack(fill="x", padx=10, pady=5)
        ttk.Label(ref, text="Auto-actualizar (seg):").pack(side="left")
        self.spin_sec = ttk.Spinbox(ref, from_=10, to=600, width=6)
        self.spin_sec.set("60")  # valor por defecto
        self.spin_sec.pack(side="left", padx=6)
        self.var_auto = tk.BooleanVar(value=False)
        self.chk_auto = ttk.Checkbutton(
            ref, text="Activar", variable=self.var_auto,
            command=self.on_auto_toggle, state="disabled"
        )
        self.chk_auto.pack(side="left")

        self.text = tk.Text(frm, height=10)
        self.text.pack(fill="both", expand=True, **pad)

    def on_connect(self):
        try:
            self.client.connect()
            self.connected = True
            self.status.config(text=f"Estado: Conectado a {HOST}:{PORT}")
            self.btn_get.config(state="normal")
            # habilitar auto-refresh una vez conectados
            if hasattr(self, "chk_auto"):
                self.chk_auto.config(state="normal")
        except Exception as e:
            messagebox.showerror("Error de conexión", str(e))

    def on_get(self):
        city = self.entry_city.get().strip()
        if not city:
            messagebox.showwarning("Falta dato", "Ingresá una ciudad")
            return
        rid = self.client.call_tool("get_weather", {"q": city})
        self.status.config(text=f"Consultando {city} (id {rid})...")

    # --- Auto-actualización ---
    def on_auto_toggle(self):
        if self.var_auto.get():
            # arranca el ciclo
            self.after(100, self._auto_loop)
            self.status.config(text="Auto-actualización activada")
        else:
            self.status.config(text="Auto-actualización desactivada")

    def _auto_loop(self):
        if not self.var_auto.get():
            return
        self.on_get()
        try:
            delay = int(self.spin_sec.get()) * 1000
        except Exception:
            delay = 60000
        self.after(delay, self._auto_loop)

    def _poll_responses(self):
        while True:
            try:
                data = self.client.recv_queue.get_nowait()
            except queue.Empty:
                break
            if data.get("ok"):
                res = data["result"]
                self._show_weather(res)
            else:
                self._append(f"⚠️ Error: {data.get('error')}")
        self.after(200, self._poll_responses)

    def _show_weather(self, res: dict):
        msg = (
            f"📍 {res.get('location')}\n"
            f"🌡️ Temp: {res.get('temp_c')} °C\n"
            f"💧 Humedad: {res.get('humidity')} %\n"
            f"☁️ Condición: {res.get('condition')}\n"
            f"💨 Viento: {res.get('wind_kph')} km/h\n"
            f"⏱️ Actualizado: {res.get('updated_at')}\n"
            + "—"*20
        )
        self._append(msg)
        self.status.config(text="Listo")

    def _append(self, txt: str):
        self.text.insert("end", txt + "\n")
        self.text.see("end")

    def _on_close(self):
        try:
            # cerrar socket si existe
            if getattr(self.client, "file", None):
                self.client.file.close()
            if getattr(self.client, "sock", None):
                self.client.sock.close()
        except Exception:
            pass
        self.destroy()

if __name__ == "__main__":
    App().mainloop()
