# MCP Weather Tools – LLM Tool Calling Demo

This project implements an **MCP (Model Context Protocol) Server and Host** that enable an LLM client (such as Claude Desktop) to call a structured tool (`get_weather`) to retrieve real-time weather information from the Open-Meteo API.

It demonstrates practical experience with:

- MCP Server/Client communication  
- Tool schemas and structured LLM responses  
- Python-based service orchestration  
- Real-time API integration  
- LLM-driven agent workflows  
- GUI integration using Tkinter  

---

## 📦 Project Structure
```
mcp-clima/
│
├── server/
│ ├── server.py # MCP Server: registers tools and handles requests
│ ├── providers.py # Weather provider logic (Open-Meteo)
│ ├── requirements.txt
│
└── host/
├── host_gui.py # Tkinter GUI acting as an MCP Host (Client)
```

---

## 🚀 Running the MCP Server

```bash
cd server
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python server.py

```

When started successfully, the console will show:

```csharp

[MCP-Server] listening on 127.0.0.1:8787

```

## 🖥 Running the GUI Host

```bash

cd host
python -m venv .venv
source .venv/bin/activate

python host_gui.py

```
--- 

### The GUI allows you to:
- Connect to the MCP server
- Enter a city (e.g., "Montevideo")
- Fetch real-time weather data
- Enable auto-refresh to retrieve updates periodically


