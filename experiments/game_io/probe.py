"""Une capture, une impulsion clavier bornée, puis une capture (Windows natif)."""

import argparse
import ctypes
from ctypes import wintypes
import json
from pathlib import Path
import sys
import time

KEYS = {"left": 0x25, "up": 0x26, "right": 0x27, "down": 0x28}


def valid_duration(value):
    seconds = float(value)
    if not 0 < seconds <= 0.5:
        raise argparse.ArgumentTypeError("La durée doit être dans ]0 ; 0,5] seconde.")
    return seconds


class WindowsGame:
    def __init__(self, title):
        self.title = title.casefold()
        self.api = ctypes.WinDLL("user32", use_last_error=True)
        self.api.SetProcessDPIAware()
        self.api.GetForegroundWindow.restype = wintypes.HWND
        self.api.GetWindowTextW.argtypes = [wintypes.HWND, wintypes.LPWSTR, ctypes.c_int]
        self.api.GetClientRect.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.RECT)]
        self.api.ClientToScreen.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.POINT)]
        self.api.GetAsyncKeyState.argtypes = [ctypes.c_int]
        self.api.GetAsyncKeyState.restype = ctypes.c_short
        # INPUT doit inclure la plus grande variante de son union (MOUSEINPUT).
        class MouseInput(ctypes.Structure):
            _fields_ = [("dx", wintypes.LONG), ("dy", wintypes.LONG),
                        ("data", wintypes.DWORD), ("flags", wintypes.DWORD),
                        ("time", wintypes.DWORD), ("extra", ctypes.c_size_t)]

        class KeyboardInput(ctypes.Structure):
            _fields_ = [("vk", wintypes.WORD), ("scan", wintypes.WORD),
                        ("flags", wintypes.DWORD), ("time", wintypes.DWORD),
                        ("extra", ctypes.c_size_t)]

        class InputUnion(ctypes.Union):
            _fields_ = [("mouse", MouseInput), ("keyboard", KeyboardInput)]

        class Input(ctypes.Structure):
            _fields_ = [("type", wintypes.DWORD), ("value", InputUnion)]

        self.Input = Input
        self.KeyboardInput = KeyboardInput
        self.api.SendInput.argtypes = [wintypes.UINT, ctypes.POINTER(Input), ctypes.c_int]
        self.api.SendInput.restype = wintypes.UINT

    def focused(self, expected=None):
        handle = self.api.GetForegroundWindow()
        text = ctypes.create_unicode_buffer(512)
        self.api.GetWindowTextW(handle, text, len(text))
        if not handle or self.title not in text.value.casefold() or (expected and handle != expected):
            raise RuntimeError("Brotato doit rester au premier plan.")
        return handle

    def capture(self, handle, path):
        from PIL import ImageGrab
        started = time.perf_counter()
        self.focused(handle)
        rect = wintypes.RECT()
        if not self.api.GetClientRect(handle, ctypes.byref(rect)):
            raise ctypes.WinError(ctypes.get_last_error())
        origin = wintypes.POINT(0, 0)
        if not self.api.ClientToScreen(handle, ctypes.byref(origin)):
            raise ctypes.WinError(ctypes.get_last_error())
        if rect.right <= 0 or rect.bottom <= 0:
            raise RuntimeError("La fenêtre n'a pas de zone visible exploitable.")
        ImageGrab.grab(bbox=(origin.x, origin.y, origin.x + rect.right, origin.y + rect.bottom),
                       all_screens=True).save(path)
        return round((time.perf_counter() - started) * 1000, 3)

    def key(self, vk, release=False):
        # Les flèches sont des touches étendues ; 0x0002 correspond à KEYUP.
        event = self.Input()
        event.type = 1
        event.value.keyboard = self.KeyboardInput(vk, 0, 0x0001 | (0x0002 if release else 0), 0, 0)
        if self.api.SendInput(1, ctypes.byref(event), ctypes.sizeof(event)) != 1:
            raise RuntimeError("SendInput a échoué ; vérifier les droits et le focus.")

    def pulse(self, direction, seconds, handle):
        vk = KEYS[direction]
        self.focused(handle)
        if any(self.api.GetAsyncKeyState(key) & 0x8000 for key in KEYS.values()):
            raise RuntimeError("Relâcher les flèches avant l'essai.")
        try:
            self.key(vk)
            deadline = time.monotonic() + seconds
            while time.monotonic() < deadline:
                self.focused(handle)
                time.sleep(0.01)
        finally:
            self.key(vk, release=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true", help="Envoyer réellement l'impulsion")
    parser.add_argument("--direction", choices=KEYS, default="right")
    parser.add_argument("--seconds", type=valid_duration, default=0.2)
    parser.add_argument("--out-dir", type=Path, default=Path("runs/game_io"))
    args = parser.parse_args()
    if not args.live:
        print(json.dumps({"mode": "dry-run", "direction": args.direction,
                          "seconds": args.seconds, "input_sent": False}))
        return
    if sys.platform != "win32":
        parser.error("--live nécessite Python sous Windows natif, hors WSL/Docker.")
    args.out_dir.mkdir(parents=True, exist_ok=True)
    print("Dans 3 secondes : placer Brotato au premier plan, dans une vague.", flush=True)
    time.sleep(3)
    try:
        game = WindowsGame("brotato")
        handle = game.focused()
        before_ms = game.capture(handle, args.out_dir / "before.png")
        started = time.perf_counter()
        game.pulse(args.direction, args.seconds, handle)
        elapsed_ms = (time.perf_counter() - started) * 1000
        after_ms = game.capture(handle, args.out_dir / "after.png")
    except (RuntimeError, OSError) as error:
        parser.exit(1, str(error) + "\n")
    result = {"mode": "live", "direction": args.direction, "seconds": args.seconds,
              "elapsed_ms": round(elapsed_ms, 3), "capture_before_ms": before_ms,
              "capture_after_ms": after_ms, "movement_verified": False}
    (args.out_dir / "result.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print("Impulsion envoyée. Vérifier le déplacement dans before.png et after.png.")


if __name__ == "__main__":
    main()
