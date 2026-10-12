DEV CLINIC CHATBOT - UPDATED FILES

Folder layout:
  main.py
  ai_agent.py
  mcp_server.py
  database.py
  requirements.txt
  .env.example
  templates/index.html
  static/chatbot.css
  static/chatbot.js

SETUP:
1. Copy these files into your project folder, keeping the templates/ and static/ folders.
2. Install dependencies:
     python -m pip install -r requirements.txt
3. Copy .env.example to .env and set your real GROQ_API_KEY.
4. Terminal 1, run MCP server:
     python mcp_server.py
   Keep this terminal open. It listens on http://127.0.0.1:8001/mcp.
5. Terminal 2, run web app:
     uvicorn main:app --reload --port 8000
6. Open http://127.0.0.1:8000/
   API testing docs: http://127.0.0.1:8000/docs

IMPORTANT:
- Start the MCP server before testing chat messages.
- If your installed FastMCP version rejects the `path` argument in mcp.run(),
  remove `path="/mcp"`; then inspect the startup URL and set MCP_SERVER_URL
  in .env to that exact URL.
- This is a starter SQLite database. Existing clinic.db data is preserved;
  sample records are inserted only when the relevant table is empty.
- The API returns detailed backend error text for local development. Do not
  expose detailed exception text in production.
