#!/usr/bin/env python3
"""
Claude Chat Export Browser
Browses and exports conversations from a Claude data export zip file.
"""

import argparse
import curses
import datetime
import io
import json
import os
import sys
import zipfile
from typing import Any, Optional


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def load_conversations_from_zip(zip_path: str) -> list[dict[str, Any]]:
    """Open the export zip entirely in memory and return the parsed conversations list."""
    with open(zip_path, "rb") as fh:
        raw = fh.read()

    with zipfile.ZipFile(io.BytesIO(raw)) as zf:
        # The conversations file can live at the root or inside a data-* sub-dir.
        candidates = [n for n in zf.namelist() if n.endswith("conversations.json")]
        if not candidates:
            raise FileNotFoundError(
                "conversations.json not found inside the zip archive."
            )
        # Prefer the shortest path (least nested).
        target = sorted(candidates, key=len)[0]
        conversations = json.loads(zf.read(target).decode("utf-8"))

    conversations.sort(key=lambda c: c.get("updated_at", ""), reverse=True)
    return conversations


# ---------------------------------------------------------------------------
# Export helpers
# ---------------------------------------------------------------------------

def _safe_filename(text: str, max_len: int = 50) -> str:
    safe = "".join(c if c.isalnum() or c in " _-" else "_" for c in text).strip()
    return safe[:max_len] if len(safe) > max_len else safe or "untitled"


def _parse_iso(ts: str) -> Optional[datetime.datetime]:
    try:
        return datetime.datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except Exception:
        return None


def _message_text(msg: dict[str, Any]) -> str:
    """Return a plain-text preview of a message (no tool blocks, first text only)."""
    text = msg.get("text", "")
    if not text:
        for item in msg.get("content", []):
            if item.get("type") == "text":
                text = item.get("text", "")
                break
    return text


def _render_content_blocks(msg: dict[str, Any]) -> str:
    """
    Render all content blocks of a message into Markdown, including
    tool_use (function calls) and tool_result (responses from tools).
    Falls back to the top-level 'text' field if no content blocks exist.
    """
    blocks = msg.get("content", [])

    # No structured content — use the plain text field.
    if not blocks:
        return msg.get("text", "")

    parts: list[str] = []
    for item in blocks:
        kind = item.get("type", "")

        if kind == "text":
            t = item.get("text", "").strip()
            if t:
                parts.append(t)

        elif kind == "tool_use":
            name = item.get("name", "unknown_tool")
            inp = item.get("input", {})
            inp_str = json.dumps(inp, ensure_ascii=False, indent=2) if inp else ""
            block = f"```tool-call\n🔧 {name}"
            if inp_str:
                block += f"\n{inp_str}"
            block += "\n```"
            parts.append(block)

        elif kind == "tool_result":
            content = item.get("content", "")
            if isinstance(content, list):
                result_text = "\n".join(
                    c.get("text", "") for c in content if c.get("type") == "text"
                ).strip()
            else:
                result_text = str(content).strip()
            if result_text:
                parts.append(f"```tool-result\n{result_text}\n```")

    return "\n\n".join(parts)


def export_conversation(
    conversation: dict[str, Any], export_dir: str
) -> tuple[str, str]:
    """Write markdown + JSON exports; return (md_path, json_path)."""
    os.makedirs(export_dir, exist_ok=True)

    name = _safe_filename(conversation.get("name") or "conversation")
    dt = _parse_iso(conversation.get("updated_at", ""))
    date_str = dt.strftime("%Y%m%d_%H%M%S") if dt else "unknown_date"

    base = f"{date_str}_{name}"
    md_path = os.path.join(export_dir, f"{base}.md")
    json_path = os.path.join(export_dir, f"{base}.json")

    # Sort messages chronologically for export.
    messages = sorted(
        conversation.get("chat_messages", []),
        key=lambda m: m.get("created_at", ""),
    )

    # --- Markdown ---
    lines: list[str] = [
        f"# {name}\n",
        f"Date: {date_str}\n",
        f"ID: {conversation.get('uuid', 'Unknown')}\n\n",
    ]
    for msg in messages:
        body = _render_content_blocks(msg)
        if not body:
            continue
        sender = "**User**:" if msg.get("sender") == "human" else "**Claude**:"
        ts = ""
        msg_dt = _parse_iso(msg.get("created_at", ""))
        if msg_dt:
            ts = f" [{msg_dt.strftime('%Y-%m-%d %H:%M:%S')}]"
        lines.append(f"{sender}{ts}\n\n{body}\n\n---\n\n")

    with open(md_path, "w", encoding="utf-8") as fh:
        fh.write("".join(lines))

    # --- JSON (sorted messages) ---
    export_conv = {**conversation, "chat_messages": messages}
    with open(json_path, "w", encoding="utf-8") as fh:
        json.dump(export_conv, fh, indent=2, ensure_ascii=False)

    return md_path, json_path


# ---------------------------------------------------------------------------
# Formatting helpers
# ---------------------------------------------------------------------------

def format_title(conversation: dict[str, Any]) -> str:
    name = conversation.get("name", "")
    if not name:
        for msg in conversation.get("chat_messages", []):
            if msg.get("sender") == "human":
                name = (_message_text(msg) or "")[:50]
                if name:
                    break
    name = name or "Untitled conversation"

    dt = _parse_iso(conversation.get("updated_at", ""))
    date_str = dt.strftime("%Y-%m-%d %H:%M") if dt else "No date"
    msg_count = len(conversation.get("chat_messages", []))

    return f"{date_str} | {msg_count:>4} msgs | {name}"


# ---------------------------------------------------------------------------
# TUI
# ---------------------------------------------------------------------------

PAGE_SIZE = 10


class Browser:
    def __init__(self, conversations: list[dict[str, Any]], export_dir: str) -> None:
        self.conversations = conversations
        self.export_dir = export_dir
        self.page = 0

    # --- Pagination ---

    def total_pages(self) -> int:
        return max(1, (len(self.conversations) + PAGE_SIZE - 1) // PAGE_SIZE)

    def page_items(self) -> list[dict[str, Any]]:
        start = self.page * PAGE_SIZE
        return self.conversations[start : start + PAGE_SIZE]

    # --- Entry point ---

    def run(self) -> None:
        curses.wrapper(self._main)

    # --- Main loop ---

    def _main(self, stdscr: "curses._CursesWindow") -> None:
        curses.curs_set(0)
        curses.start_color()
        curses.use_default_colors()
        curses.init_pair(1, curses.COLOR_CYAN, -1)    # selected row
        curses.init_pair(2, curses.COLOR_GREEN, -1)   # headers / success
        curses.init_pair(3, curses.COLOR_YELLOW, -1)  # hints / paths

        selected = 0

        while True:
            stdscr.erase()
            h, w = stdscr.getmaxyx()
            items = self.page_items()

            self._draw_header(stdscr, w)

            for i, conv in enumerate(items):
                y = i + 4
                if y >= h - 3:
                    break
                title = format_title(conv)
                if len(title) > w - 2:
                    title = title[: w - 5] + "..."
                attr = (curses.color_pair(1) | curses.A_BOLD) if i == selected else 0
                stdscr.addstr(y, 1, title, attr)

            footer = "↑/↓: navegar | ←/→: página | Enter: seleccionar | q: salir"
            self._center(stdscr, h - 2, w, footer, curses.color_pair(3))

            stdscr.refresh()

            key = stdscr.getch()
            if key == ord("q"):
                break
            elif key == curses.KEY_UP:
                selected = max(0, selected - 1)
            elif key == curses.KEY_DOWN:
                selected = min(len(items) - 1, selected + 1)
            elif key == curses.KEY_LEFT and self.page > 0:
                self.page -= 1
                selected = 0
            elif key == curses.KEY_RIGHT and self.page < self.total_pages() - 1:
                self.page += 1
                selected = 0
            elif key in (curses.KEY_ENTER, 10, 13):
                if items:
                    self._detail_screen(stdscr, items[selected])

    def _draw_header(self, stdscr: "curses._CursesWindow", w: int) -> None:
        self._center(
            stdscr, 0, w,
            "CLAUDE CHAT EXPORT BROWSER",
            curses.color_pair(2) | curses.A_BOLD,
        )
        self._center(stdscr, 1, w, "Exporta tus conversaciones de Claude")
        page_info = f"Página {self.page + 1}/{self.total_pages()}  —  {len(self.conversations)} conversaciones"
        self._center(stdscr, 2, w, page_info)

    # --- Detail / export screen ---

    def _detail_screen(
        self, stdscr: "curses._CursesWindow", conv: dict[str, Any]
    ) -> None:
        h, w = stdscr.getmaxyx()
        stdscr.erase()

        self._center(stdscr, 0, w, "CLAUDE CHAT EXPORT BROWSER", curses.color_pair(2) | curses.A_BOLD)
        self._center(stdscr, 1, w, "DETALLES DE CONVERSACIÓN", curses.A_BOLD)

        name = conv.get("name") or "Sin título"
        dt = _parse_iso(conv.get("updated_at", ""))
        date_str = dt.strftime("%Y-%m-%d %H:%M") if dt else "Sin fecha"
        msg_count = len(conv.get("chat_messages", []))

        info_lines = [
            f"Título:    {name}",
            f"Fecha:     {date_str}",
            f"Mensajes:  {msg_count}",
            f"UUID:      {conv.get('uuid', 'Desconocido')}",
        ]

        y = 3
        for line in info_lines:
            stdscr.addstr(y, 2, line[: w - 3])
            y += 1

        y += 1
        stdscr.addstr(y, 2, "Previsualización:", curses.A_BOLD)
        y += 1

        preview_msgs = conv.get("chat_messages", [])[:3]
        for msg in preview_msgs:
            if y >= h - 5:
                break
            text = (_message_text(msg) or "").replace("\n", " ")
            sender = "Usuario" if msg.get("sender") == "human" else "Claude"
            line = f"{sender}: {text}"
            if len(line) > w - 4:
                line = line[: w - 7] + "..."
            stdscr.addstr(y, 2, line)
            y += 1

        prompt = "¿Exportar esta conversación? (s/n)"
        self._center(stdscr, h - 3, w, prompt, curses.color_pair(3) | curses.A_BOLD)
        stdscr.refresh()

        while True:
            key = stdscr.getch()
            if key in (ord("s"), ord("S"), ord("y"), ord("Y")):
                self._do_export(stdscr, conv)
                break
            elif key in (ord("n"), ord("N"), 27):  # 27 = ESC
                break

    def _do_export(
        self, stdscr: "curses._CursesWindow", conv: dict[str, Any]
    ) -> None:
        h, w = stdscr.getmaxyx()
        stdscr.erase()
        try:
            md_path, json_path = export_conversation(conv, self.export_dir)
            self._center(stdscr, h // 2 - 2, w, "✓ Exportación completada", curses.color_pair(2) | curses.A_BOLD)
            self._center(stdscr, h // 2, w, f"Markdown → {md_path}", curses.color_pair(3))
            self._center(stdscr, h // 2 + 1, w, f"JSON    → {json_path}", curses.color_pair(3))
        except Exception as exc:
            self._center(stdscr, h // 2, w, f"Error: {exc}", curses.color_pair(1))
        self._center(stdscr, h // 2 + 3, w, "Pulsa cualquier tecla...", curses.color_pair(3))
        stdscr.refresh()
        stdscr.getch()

    # --- Utility ---

    @staticmethod
    def _center(
        stdscr: "curses._CursesWindow",
        y: int,
        w: int,
        text: str,
        attr: int = 0,
    ) -> None:
        x = max(0, (w - len(text)) // 2)
        try:
            stdscr.addstr(y, x, text, attr)
        except curses.error:
            pass  # Ignore write-past-edge errors on tiny terminals.


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="claude_chat_browser",
        description="Navega y exporta conversaciones de un zip de exportación de Claude.",
    )
    parser.add_argument(
        "zip_file",
        metavar="ZIP",
        help="Ruta al archivo .zip exportado desde Claude.",
    )
    parser.add_argument(
        "-o", "--output-dir",
        metavar="DIR",
        default=None,
        help=(
            "Directorio donde se guardarán las exportaciones. "
            "Por defecto: exports/ junto al zip."
        ),
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    zip_path = os.path.abspath(args.zip_file)
    if not os.path.isfile(zip_path):
        parser.error(f"No se encuentra el archivo: {zip_path}")
    if not zipfile.is_zipfile(zip_path):
        parser.error(f"El archivo no es un zip válido: {zip_path}")

    export_dir = args.output_dir or os.path.join(os.path.dirname(zip_path), "exports")
    export_dir = os.path.abspath(export_dir)

    print(f"Cargando conversaciones de: {zip_path}")
    try:
        conversations = load_conversations_from_zip(zip_path)
    except Exception as exc:
        print(f"Error al leer el zip: {exc}", file=sys.stderr)
        sys.exit(1)

    print(f"  → {len(conversations)} conversaciones encontradas.")
    print(f"  → Los exports se guardarán en: {export_dir}")
    print("Iniciando interfaz…\n")

    Browser(conversations, export_dir).run()


if __name__ == "__main__":
    main()