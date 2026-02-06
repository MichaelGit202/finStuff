import json

try:
    import pysimdjson as simdjson
    _HAS_SIMDJSON = True
    # prefer simdjson.loads if available, otherwise create a Parser
    _SIMD_LOADS = getattr(simdjson, 'loads', None)
    _SIMD_PARSER = None if _SIMD_LOADS else simdjson.Parser()
except Exception:
    _HAS_SIMDJSON = False
    _SIMD_LOADS = None
    _SIMD_PARSER = None



#general json data structure
#time series data [
    # typical OHLCV data + time stamp
#]

# the part of me that is thinking too fat ahead thinks:
# #TODO support parralell / non-linear data streams, ie a sequential time series data + news data
    # - news data is slower than market data

# im just gona focus on the pure OHLCV data for now



class simulator:

    # init that assumes the data is in one file
    def __init__(self, file_path: str, start_step: int = 0, chunk_size: int = 1000, initial_money: float = 1000.0):
        self.file_path = str(file_path)
        self.current_step = start_step
        self.data = None
        self.chunkSize = int(chunk_size)
        self.cash = initial_money
        self.equity = 0.0 # invested money
        self._fh = None
        self._mode = None  # 'ndjson' or 'array'
        self._eof = False
        self._eoc = True

    def __del__(self):
        try:
            if self._fh:
                self._fh.close()
        except Exception:
            pass

    def _open_if_needed(self):
        if self._fh is not None:
            return
        self._fh = open(self.file_path, 'r', encoding='utf-8')
        # detect format by peeking first non-whitespace char
        while True:
            c = self._fh.read(1)
            if not c:
                break
            if not c.isspace():
                if c == '[':
                    self._mode = 'array'
                elif c == '{':
                    # top-level object; try to find the first array inside it and stream that
                    # scan forward until we hit a '[' that is not inside a string
                    in_string = False
                    escape = False
                    while True:
                        d = self._fh.read(1)
                        if not d:
                            break
                        if in_string:
                            if escape:
                                escape = False
                            elif d == '\\':
                                escape = True
                            elif d == '"':
                                in_string = False
                            continue
                        else:
                            if d == '"':
                                in_string = True
                                continue
                            if d == '[':
                                self._mode = 'array'
                                # file pointer is just after the '[' ready to read first element
                                break
                    # if we didn't find an array, treat as ndjson fallback
                    if self._mode != 'array':
                        self._mode = 'ndjson'
                else:
                    self._mode = 'ndjson'
                break
        # if we decided it's ndjson, rewind to start so reading lines works
        if self._mode == 'ndjson':
            self._fh.seek(0)

    def _parse_json(self, s: str):
        if _HAS_SIMDJSON:
            try:
                if _SIMD_LOADS:
                    return _SIMD_LOADS(s)
                else:
                    # Parser.parse accepts bytes or str depending on binding
                    return _SIMD_PARSER.parse(s)
            except Exception:
                return json.loads(s)
        else:
            return json.loads(s)


    def _read_next_array_item(self):
        fh = self._fh
        buf = []
        in_string = False
        escape = False
        depth = None  # None = not seen container yet, 0 = primitive
        started = False

        while True:
            c = fh.read(1)
            if not c:
                # EOF
                if not buf:
                    self._eof = True
                    return None
                break

            if not started:
                if c.isspace() or c == ',':
                    continue
                if c == ']':
                    self._eof = True
                    return None
                started = True
                buf.append(c)
                if c == '"':
                    in_string = True
                    depth = 0
                elif c == '{' or c == '[':
                    depth = 1
                else:
                    depth = 0
                continue

            buf.append(c)

            if in_string:
                if escape:
                    escape = False
                elif c == '\\':
                    escape = True
                elif c == '"':
                    in_string = False
                continue

            # not in string
            if c == '"':
                in_string = True
            elif c == '{' or c == '[':
                if depth is None:
                    depth = 1
                else:
                    depth += 1
            elif c == '}' or c == ']':
                if depth is None:
                    depth = 0
                elif depth > 0:
                    depth -= 1
                # if we've closed the top-level container and depth is 0, item done
                if depth == 0:
                    # consume any whitespace after the value, and optionally a comma or closing bracket
                    # but we already consumed the closing brace/bracket
                    break
            elif depth == 0 and (c == ',' or c == ']'):
                # primitive ended; remove delimiter from buffer
                buf.pop()
                if c == ']':
                    self._eof = True
                break

        s = ''.join(buf).strip()
        if not s:
            return None
        return self._parse_json(s)

    def load_chunk(self):
        self._open_if_needed()
        if self._eof:
            return []

        items = []
        if self._mode == 'ndjson':
            while len(items) < self.chunkSize:
                line = self._fh.readline()
                if not line:
                    self._eof = True
                    break
                line = line.strip()
                if not line:
                    continue
                items.append(self._parse_json(line))
        else:  # array mode
            while len(items) < self.chunkSize:
                it = self._read_next_array_item()
                if it is None:
                    break
                items.append(it)

        self.current_step += len(items)
        self.data = items
        return items

    def buy(amount: float):
        cash = self.cash
        if amount > cash:
            raise ValueError("Insufficient cash to buy")
        elif amount <= 0:
            raise ValueError("Buy amount must be positive")
        else:
            self.cash -= amount
            self.equity += amount

    def sell(amount: float):
        if amount > self.equity:
            raise ValueError("Insufficient equity to sell")
        elif amount <= 0:
            raise ValueError("Sell amount must be positive")
        else:
            self.equity -= amount
            self.cash += amount

    def step(self):

        if self._eoc:
            print("end of chunk")
            self.data = self.load_chunk()
            print()
            self._eoc = False

        if self._eof:
            return []


        if len(self.data) >= self.current_step + 1:
            self.eoc = True

        self.current_step += 1

        return  self.data[self.current_step % self.chunkSize : (self.current_step % self.chunkSize) + 1]
    