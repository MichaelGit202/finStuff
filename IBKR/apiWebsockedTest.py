import asyncio
import importlib
import json
import os
import ssl
from urllib.parse import urlparse


def _insecure_ssl_context() -> ssl.SSLContext:
	"""Client Portal Gateway uses a self-signed cert by default on localhost."""
	ctx = ssl.create_default_context()
	ctx.check_hostname = False
	ctx.verify_mode = ssl.CERT_NONE
	return ctx


async def _get_json(session, base_url: str, path: str) -> dict:
	async with session.get(f"{base_url}{path}") as resp:
		text = await resp.text()
		if resp.status >= 400:
			raise RuntimeError(f"GET {path} failed ({resp.status}): {text}")
		return json.loads(text) if text else {}


async def _post_json(
	session,
	base_url: str,
	path: str,
	payload: dict | None = None,
) -> dict:
	async with session.post(f"{base_url}{path}", json=payload or {}) as resp:
		text = await resp.text()
		if resp.status >= 400:
			raise RuntimeError(f"POST {path} failed ({resp.status}): {text}")
		return json.loads(text) if text else {}


async def _tcp_open(host: str, port: int, timeout: float = 1.5) -> bool:
	try:
		reader, writer = await asyncio.wait_for(asyncio.open_connection(host, port), timeout)
		writer.close()
		await writer.wait_closed()
		return True
	except Exception:
		return False


async def main() -> None:
	try:
		aiohttp = importlib.import_module("aiohttp")
	except ModuleNotFoundError as e:
		raise RuntimeError(
			"Missing dependency: aiohttp. Install with: pip install aiohttp"
		) from e

	# Start IBKR Client Portal Gateway first (default: https://localhost:5000)
	# and ensure you are logged in.
	base_url = os.getenv("IBKR_CP_BASE", "https://localhost:5000")
	parsed = urlparse(base_url)
	host = parsed.hostname or "localhost"
	port = parsed.port or (443 if parsed.scheme == "https" else 80)

	if port in (4001, 4002, 7496, 7497):
		raise RuntimeError(
			"IBKR_CP_BASE is pointing to a TWS/Gateway socket port. "
			"For Client Portal websocket API use HTTPS on 5000/5001, e.g. https://localhost:5000"
		)

	if not await _tcp_open(host, port):
		raise RuntimeError(
			f"Cannot reach Client Portal Gateway at {base_url}. "
			"Start Client Portal Gateway and use IBKR_CP_BASE=https://localhost:5000 "
			"(or the Windows host IP from WSL)."
		)

	ws_url = os.getenv("IBKR_WS_URL", f"{base_url.replace('https://', 'wss://')}/v1/api/ws")

	# Example AAPL conid. You can override this for another symbol.
	conid = os.getenv("IBKR_CONID", "265598")
	symbol = os.getenv("IBKR_SYMBOL", "AAPL")

	# Last price field only. If your account has delayed-only entitlement,
	# this may arrive as delayed last via the same field code.
	fields = os.getenv("IBKR_FIELDS", "31").split(",")
	fields = [f.strip() for f in fields if f.strip()]

	ssl_ctx = _insecure_ssl_context()
	connector = aiohttp.TCPConnector(ssl=ssl_ctx)

	async with aiohttp.ClientSession(connector=connector) as session:
		print(f"Using Client Portal base URL: {base_url}")

		auth = await _post_json(session, base_url, "/v1/api/iserver/auth/status")
		authenticated = bool(auth.get("authenticated"))
		connected = bool(auth.get("connected"))
		print(f"Auth status -> authenticated={authenticated}, connected={connected}")

		if not authenticated:
			raise RuntimeError(
				"Not authenticated. Open Client Portal Gateway in your browser and sign in first."
			)

		# Keep the backend session warm.
		await _post_json(session, base_url, "/v1/api/tickle")

		print(f"Connecting websocket: {ws_url}")
		async with session.ws_connect(ws_url, heartbeat=20) as ws:
			# Subscribe market data stream for the selected conid.
			sub = f"smd+{conid}+{{\"fields\":{json.dumps(fields)}}}"
			print(f"Subscribing: {sub}")
			await ws.send_str(sub)

			print("Streaming delayed/real-time last price only. Press Ctrl+C to stop.\n")
			while True:
				msg = await ws.receive()

				if msg.type == aiohttp.WSMsgType.TEXT:
					data = msg.data
					try:
						obj = json.loads(data)
					except json.JSONDecodeError:
						print(data)
						continue

					if isinstance(obj, dict):
						# Some responses are status/error payloads, not market ticks.
						if obj.get("error"):
							print(f"Gateway message: {obj.get('error')}")
							continue

						if "31" in obj and obj.get("31") not in (None, ""):
							print(f"{symbol} last: {obj.get('31')}")
							continue

					# Keep raw output when payload shape is unexpected.
					print(data)
				elif msg.type == aiohttp.WSMsgType.ERROR:
					raise RuntimeError(f"Websocket error: {ws.exception()}")
				elif msg.type in (aiohttp.WSMsgType.CLOSED, aiohttp.WSMsgType.CLOSE):
					print("Websocket closed by server.")
					break


if __name__ == "__main__":
	try:
		asyncio.run(main())
	except KeyboardInterrupt:
		print("\nStopped by user.")
