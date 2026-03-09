import json as js
from pathlib import Path
from datetime import datetime


OnesNames = ["Zero","One","Two","Three","Four","Five","Six","Seven","Eight","Nine","Ten","Eleven","Twelve","Thirteen","Fourteen","Fifteen","Sixteen","Seventeen","Eighteen","Nineteen","Twenty"]
TensNames = ["err","err","Twenty","Thirty","Forty","Fifty","Sixty","Seventy","Eighty","Ninety"]


class DebugLog:
    """A class that handles debug messages, and stores them until deployment is requested."""
    def flush(self):
        for parcel in self.log:
            infotype = (f'[{parcel[0]}]') if parcel[0] != '' else ''
            source = (f'in {parcel[1]}') if parcel[1] != '' else ''
            message = parcel[2]
            print(f" {infotype} {source}: {message}")
        self.log = []

    def append(self, message, infotype='', source='', pri=0, flush=True):
        if pri <= self.priorityLevel:
            self.log.append([infotype, source, str(message)])
            if flush is True:
                self.flush()

    def __init__(self, priority=0):
        self.priorityLevel = priority
        self.log = []


def GetNumberName(debug, number, spacechar='-'):
    number = int(number)
    if number > 99 or number < 1:
        debug.append(f'Number value "{number}" not accepted in GetNumberName.', 'INFO', pri=2)

    if number < 21:
        OnesName = OnesNames[int(number)]
        TensName = ""
    else:
        if int(number) % 10 == 0:
            OnesName = ""
        else:
            OnesName = spacechar + OnesNames[int(number) % 10]
        TensName = TensNames[int((int(number) - int(number) % 10) / 10)]
    return f"{TensName}{OnesName}"


def _json_error_context(raw: str, pos: int, radius: int = 20) -> str:
    start = max(0, pos - radius)
    end = min(len(raw), pos + radius)
    snippet = raw[start:end].replace("\t", "\\t").replace("\n", "\\n").replace("\r", "\\r")
    caret_pad = " " * (pos - start)
    return f"{snippet}\n{caret_pad}^"


def QueryPath(debug, relpath=None, extension="json"):
    """
    Cross-platform path resolver:
    - relpath may be: "", None, relative path, or absolute path
    - if it's a directory, returns the most recently modified matching file
    - extension matching is case-insensitive
    """
    script_root = Path(__file__).resolve().parent

    # Default: use script directory if no path provided
    p = Path(relpath) if relpath else script_root

    # If relative, interpret relative to script directory (not cwd)
    if not p.is_absolute():
        p = (script_root / p).resolve()

    ext = extension.lower().lstrip(".") if extension else None

    if p.is_file():
        debug.append('Queried path is to a FILE.', 'INFO', pri=2)
        return str(p)

    if not p.is_dir():
        debug.append(f'Issue with relpath "{relpath}". Using script ROOT directory.', 'WARN', pri=2)
        p = script_root

    # Gather candidate files (case-insensitive suffix compare)
    if ext is None:
        files = [f for f in p.iterdir() if f.is_file()]
    else:
        files = [f for f in p.iterdir() if f.is_file() and f.suffix.lower() == f".{ext}"]

    if not files:
        debug.append(f'No *.{extension} files exist in directory: {p}', 'ERROR', pri=2)
        return None

    latest = max(files, key=lambda f: f.stat().st_mtime)  # mtime is sane cross-platform
    debug.append(f'Most recent file retrieved: {latest.name}', 'INFO', pri=2)
    return str(latest)


def ReadJSON(debug, path=None):
    """Interpret a JSON file, if encoded correctly, stripping physical line breaks first."""
    filepath = QueryPath(debug, path, 'json')
    if filepath is None:
        debug.append('Unable to retrieve JSON file.', 'ERROR')
        return {}

    print(f"Actions taken on filename {filepath}.")
    raw = Path(filepath).read_text(encoding="utf-8-sig", errors="ignore")

    # Scrivener workaround: strip physical line breaks before parsing
    raw = raw.replace("\r\n", "\n").replace("\r", "\n").replace("\n", "")

    try:
        loaded = js.loads(raw)
    except js.JSONDecodeError as e:
        ctx = _json_error_context(raw, e.pos, radius=20)
        err_str = (
            "> Error in compilation of the JSON file.\n"
            f"Exception at LINE {e.lineno}, COL {e.colno} (pos {e.pos}).\n"
            f"Message: {e.msg}\n"
            "--- context (±20 chars) ---\n"
            f"{ctx}\n"
            "--- end context ---"
        )
        debug.append(err_str, 'ERROR')
        raise

    debug.append('JSON file successfully loaded.', 'INFO', pri=1)
    return loaded


def GetTTS_JSON(directory=""):
    debug = DebugLog(1)
    return ReadJSON(debug, directory)


if __name__ == "__main__":
    JSON = GetTTS_JSON("")  # pass a directory or file path here if desired
    print(JSON)
    
    