import json
try:
    import pysimdjson as simdjson
    _HAS_SIMDJSON = True
    _SIMD_LOADS = getattr(simdjson, 'loads', None)
    _SIMD_PARSER = None if _SIMD_LOADS else simdjson.Parser()
except Exception:
    _HAS_SIMDJSON = False
    _SIMD_LOADS = None
    _SIMD_PARSER = None

class json_reader:

    def __init__(self, file_path, chunk_size=100):
        self.file_path = file_path
        self.chunk_size = chunk_size
        self._fh = None
        self._mode = None  # 'ndjson' or 'array'
        self._eof = False
        self._chunk_pos = 0
        self.data = None
        self._open_if_needed()

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
        while True:
            c = self._fh.read(1)
            if not c:
                break
            if not c.isspace():
                if c == '[':
                    self._mode = 'array'
                elif c == '{':
                    in_string = False
                    escape = False
                    while True:
                        d = self._fh.read(1)
                        if not d:
                            break
                        if in_string:
                            if escape:
                                escape = False
                            elif d == f'\\':
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
                                break
                    if self._mode != 'array':
                        self._mode = 'ndjson'
                else:
                    self._mode = 'ndjson'
                break
        if self._mode == 'ndjson':
            self._fh.seek(0)

    def _parse_json(self, s):
        if _HAS_SIMDJSON:
            try:
                if _SIMD_LOADS:
                    return _SIMD_LOADS(s)
                else:
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
        depth = None
        started = False
        while True:
            c = fh.read(1)
            if not c:
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
                elif c == f'\\':
                    escape = True
                elif c == '"':
                    in_string = False
                continue
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
                if depth == 0:
                    break
            elif depth == 0 and (c == ',' or c == ']'):
                buf.pop()
                if c == ']':
                    self._eof = True
                break
        s = ''.join(buf).strip()
        if not s:
            return None
        return self._parse_json(s)

    def get_next_entry(self):
        self._open_if_needed()
        if self._eof:
            return None
        if self._mode == 'ndjson':
            line = self._fh.readline()
            if not line:
                self._eof = True
                return None
            line = line.strip()
            if not line:
                return self.get_next_entry()
            return self._parse_json(line)
        else:
            return self._read_next_array_item()


    def read_chunk(self):
        self._open_if_needed()
        if self._eof:
            return []
        items = []
        if self._mode == 'ndjson':
            while len(items) < self.chunk_size:
                line = self._fh.readline()
                if not line:
                    self._eof = True
                    break
                line = line.strip()
                if not line:
                    continue
                items.append(self._parse_json(line))
        else:
            while len(items) < self.chunk_size:
                it = self._read_next_array_item()
                if it is None:
                    break
                items.append(it)
        return items