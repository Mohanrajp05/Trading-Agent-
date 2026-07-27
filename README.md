# Trading-Agent
An autonomous AI trading platform with three core agents—Researcher (finds market insights), Trader (executes trades), and Evaluator (monitors performance)—all connected through Model Context Protocol (MCP).


title: Agent Week 6
emoji: 📈
colorFrom: yellow
colorTo: gray
sdk: docker
pinned: false


### Commands to run the project ###

Create new terminals and add these commands 
Backend 

cd "C:\Users\Mohan Raj P\Agent week 6\6_mcp"
uv run uvicorn backend.api:app --port 8000 --reload

Frontend

cd "C:\Users\Mohan Raj P\Agent week 6\6_mcp\frontend"
npm run dev

 cd "C:\Users\Mohan Raj P\Agent week 6\6_mcp"
uv run python -m backend.trading_floor

