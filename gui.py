from __future__ import annotations

import json
import queue
import threading
import tkinter as tk
from tkinter import ttk

from brain import BrainEvent, JarvisBrain
from core.skill_registry import list_skills


class ToolControlCenter(tk.Tk):
    """JARVIS control center: every command is routed through brain.py."""

    TOOLS = (
        ("🧠", "AI Brain", "Understand and route", "brain"),
        ("🔄", "Workflow Builder", "Build automations", "workflow"),
        ("🔍", "Research", "Research ideas and problems", "research"),
        ("🌐", "App Builder", "Build software", "app"),
        ("🧪", "Test & Repair", "Test and repair", "repair"),
        ("🚀", "Deployment", "Prepare deployment", "deploy"),
        ("🧩", "Skills", "View capabilities", "skills"),
        ("🔌", "Integrations", "View integrations", "integrations"),
    )

    def __init__(self) -> None:
        super().__init__()
        self.brain = JarvisBrain()
        self.title("JARVIS — AI Engineering & Operations")
        self.geometry("1280x820")
        self.minsize(1050, 700)
        self.configure(bg="#0b1020")
        self._style()
        self._shell()
        self.home()

    def _style(self) -> None:
        s = ttk.Style(self)
        s.theme_use("clam")
        s.configure("App.TFrame", background="#0b1020")
        s.configure("Side.TFrame", background="#11182d")
        s.configure("Title.TLabel", background="#0b1020", foreground="#f7f9ff", font=("Segoe UI", 22, "bold"))
        s.configure("Sub.TLabel", background="#0b1020", foreground="#9aa8c7", font=("Segoe UI", 10))
        s.configure("Nav.TButton", background="#11182d", foreground="#dce5ff", borderwidth=0, padding=10)
        s.configure("Primary.TButton", background="#4f7cff", foreground="#ffffff", borderwidth=0, padding=10)

    def _shell(self) -> None:
        root = ttk.Frame(self, style="App.TFrame"); root.pack(fill="both", expand=True)
        side = ttk.Frame(root, style="Side.TFrame", width=220); side.pack(side="left", fill="y"); side.pack_propagate(False)
        tk.Label(side, text="⚡ JARVIS", bg="#11182d", fg="#fff", font=("Segoe UI", 20, "bold"), pady=22).pack(fill="x")
        ttk.Button(side, text="⌂  Dashboard", style="Nav.TButton", command=self.home).pack(fill="x", padx=10, pady=3)
        for icon, name, _, key in self.TOOLS:
            ttk.Button(side, text=f"{icon}  {name}", style="Nav.TButton",
                       command=lambda k=key: self.tool(k)).pack(fill="x", padx=10, pady=2)
        tk.Label(side, text="42 non-creative skills\nCreative Studio excluded",
                 bg="#11182d", fg="#7080a5", font=("Segoe UI", 9), justify="left", padx=18, pady=18).pack(side="bottom", fill="x")
        self.content = ttk.Frame(root, style="App.TFrame"); self.content.pack(fill="both", expand=True, padx=28, pady=24)

    def _clear(self) -> None:
        for child in self.content.winfo_children(): child.destroy()

    def _header(self, title: str, subtitle: str) -> None:
        ttk.Label(self.content, text=title, style="Title.TLabel").pack(anchor="w")
        ttk.Label(self.content, text=subtitle, style="Sub.TLabel").pack(anchor="w", pady=(4, 18))

    def _box(self, parent: tk.Misc) -> tk.Text:
        box = tk.Text(parent, bg="#11182d", fg="#e9efff", insertbackground="#fff",
                      relief="flat", font=("Consolas", 9), padx=10, pady=10, wrap="word")
        box.pack(fill="both", expand=True)
        return box

    def _workspace(self, default: str = "Tell JARVIS what you want to build or do...") -> None:
        card = ttk.Frame(self.content, style="App.TFrame"); card.pack(fill="both", expand=True)
        entry = tk.Text(card, height=5, bg="#11182d", fg="#e9efff", insertbackground="#fff",
                        relief="flat", font=("Consolas", 11), padx=12, pady=10)
        entry.pack(fill="x", pady=(0, 10)); entry.insert("1.0", default)

        panes = ttk.Frame(card, style="App.TFrame"); panes.pack(fill="both", expand=True)
        left = ttk.Frame(panes, style="App.TFrame"); left.pack(side="left", fill="both", expand=True, padx=(0, 6))
        right = ttk.Frame(panes, style="App.TFrame"); right.pack(side="left", fill="both", expand=True, padx=(6, 0))
        ttk.Label(left, text="CHAT", style="Sub.TLabel").pack(anchor="w")
        ttk.Label(right, text="LIVE TERMINAL", style="Sub.TLabel").pack(anchor="w")
        chat = self._box(left); terminal = self._box(right)
        button = ttk.Button(card, text="▶ Run JARVIS", style="Primary.TButton",
                            command=lambda: self._run(entry.get("1.0", "end").strip(), chat, terminal, button))
        button.pack(fill="x", pady=(10, 0))

    def _run(self, request: str, chat: tk.Text, terminal: tk.Text, button: ttk.Button) -> None:
        if not request: return
        chat.delete("1.0", "end"); terminal.delete("1.0", "end"); button.configure(state="disabled")
        events: queue.Queue[BrainEvent] = queue.Queue()

        def worker() -> None:
            try:
                result = self.brain.execute(request, emit=events.put)
                events.put(BrainEvent("result", "completed", "Final result ready.", {"result": result}))
            except Exception as exc:
                events.put(BrainEvent("error", "failed", str(exc), {"type": type(exc).__name__}))
            events.put(BrainEvent("_done", "completed", ""))

        threading.Thread(target=worker, daemon=True).start()

        def pump() -> None:
            done = False
            while True:
                try: event = events.get_nowait()
                except queue.Empty: break
                if event.stage == "_done": done = True; continue
                terminal.insert("end", f"[{event.stage.upper():10}] {event.status:10} {event.message}\n")
                terminal.see("end")
                if event.stage == "result":
                    chat.insert("end", json.dumps(event.data["result"], indent=2, default=str) + "\n")
                else:
                    chat.insert("end", event.message + "\n")
            if done: button.configure(state="normal")
            else: self.after(80, pump)
        pump()

    def home(self) -> None:
        self._clear()
        self._header("JARVIS Control Center", "interface → main.py → brain.py → skill/tool → execution → result")
        self._workspace("Build me an application that ...")

    def tool(self, key: str) -> None:
        if key == "skills":
            self._json_page("🧩 Skills", list_skills()); return
        if key == "integrations":
            self._json_page("🔌 Integrations", self.brain.orchestrator.list_integrations()); return
        titles = {
            "brain": ("🧠 AI Brain", "Understand and route any command."),
            "workflow": ("🔄 Workflow Builder", "Build and simulate automations."),
            "research": ("🔍 Research", "Research problems, customers and opportunities."),
            "app": ("🌐 App Builder", "Build software projects."),
            "repair": ("🧪 Test & Repair", "Test and repair workflows."),
            "deploy": ("🚀 Deployment", "Prepare a deployment plan."),
        }
        title, subtitle = titles[key]
        self._clear(); self._header(title, subtitle); self._workspace()

    def _json_page(self, title: str, payload: object) -> None:
        self._clear(); self._header(title, "Live registry from the JARVIS engine.")
        box = self._box(self.content); box.insert("end", json.dumps(payload, indent=2, default=str))


def launch() -> None:
    ToolControlCenter().mainloop()


if __name__ == "__main__":
    launch()
