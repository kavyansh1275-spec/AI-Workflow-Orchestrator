from __future__ import annotations

import json
import threading
import tkinter as tk
from tkinter import messagebox, ttk
from typing import Callable

from core.orchestrator import Orchestrator


class ToolControlCenter(tk.Tk):
    """Desktop control center for the AI Workflow Orchestrator.

    Each tool is a clickable module. The modules call the existing orchestrator
    services instead of duplicating business logic in the UI.
    """

    TOOLS = (
        ("🧠", "AI Brain", "Understand and plan requests", "brain"),
        ("🔄", "Workflow Builder", "Create and inspect workflows", "workflow"),
        ("🔍", "Research", "Research a business/automation idea", "research"),
        ("🌐", "App Builder", "Generate an application plan", "app"),
        ("🧪", "Test & Repair", "Validate and repair workflows", "repair"),
        ("🚀", "Deployment", "Plan a safe deployment", "deploy"),
        ("🔌", "Integrations", "Inspect available integrations", "integrations"),
        ("🔐", "Credentials", "Check provider readiness", "credentials"),
    )

    def __init__(self, orchestrator: Orchestrator | None = None) -> None:
        super().__init__()
        self.orchestrator = orchestrator or Orchestrator()
        self.title("AI Business Operator — Control Center")
        self.geometry("1180x760")
        self.minsize(980, 650)
        self.configure(bg="#0b1020")

        self._configure_styles()
        self._build_shell()
        self.show_home()

    def _configure_styles(self) -> None:
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("App.TFrame", background="#0b1020")
        style.configure("Sidebar.TFrame", background="#11182d")
        style.configure("Card.TFrame", background="#151e35")
        style.configure("Title.TLabel", background="#0b1020", foreground="#f7f9ff",
                        font=("Segoe UI", 24, "bold"))
        style.configure("Subtitle.TLabel", background="#0b1020", foreground="#9aa8c7",
                        font=("Segoe UI", 11))
        style.configure("CardTitle.TLabel", background="#151e35", foreground="#ffffff",
                        font=("Segoe UI", 13, "bold"))
        style.configure("CardText.TLabel", background="#151e35", foreground="#9aa8c7",
                        font=("Segoe UI", 9))
        style.configure("Nav.TButton", background="#11182d", foreground="#dce5ff",
                        borderwidth=0, padding=(14, 11), font=("Segoe UI", 10, "bold"))
        style.map("Nav.TButton", background=[("active", "#1d2947")])
        style.configure("Primary.TButton", background="#4f7cff", foreground="#ffffff",
                        borderwidth=0, padding=(16, 10), font=("Segoe UI", 10, "bold"))
        style.map("Primary.TButton", background=[("active", "#6a90ff")])
        style.configure("Tool.TButton", background="#151e35", foreground="#ffffff",
                        borderwidth=0, padding=14, font=("Segoe UI", 11, "bold"))
        style.map("Tool.TButton", background=[("active", "#202d4d")])
        style.configure("TEntry", fieldbackground="#11182d", foreground="#ffffff",
                        insertcolor="#ffffff", padding=9)
        style.configure("TCombobox", fieldbackground="#11182d", foreground="#ffffff")
        style.configure("TNotebook", background="#0b1020", borderwidth=0)
        style.configure("TLabel", background="#0b1020", foreground="#dce5ff")

    def _build_shell(self) -> None:
        root = ttk.Frame(self, style="App.TFrame")
        root.pack(fill="both", expand=True)

        sidebar = ttk.Frame(root, style="Sidebar.TFrame", width=235)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        brand = tk.Label(sidebar, text="⚡ AI OPERATOR", bg="#11182d", fg="#ffffff",
                         font=("Segoe UI", 16, "bold"), pady=24)
        brand.pack(fill="x")

        home = ttk.Button(sidebar, text="⌂  Dashboard", style="Nav.TButton",
                          command=self.show_home)
        home.pack(fill="x", padx=10, pady=(4, 3))

        for icon, name, desc, key in self.TOOLS:
            ttk.Button(
                sidebar,
                text=f"{icon}  {name}",
                style="Nav.TButton",
                command=lambda k=key: self.show_tool(k),
            ).pack(fill="x", padx=10, pady=2)

        tk.Label(
            sidebar,
            text="V12 • Tool Control Center\nSafe dry-run by default",
            bg="#11182d",
            fg="#7080a5",
            font=("Segoe UI", 9),
            justify="left",
            padx=18,
            pady=20,
        ).pack(side="bottom", fill="x")

        self.content = ttk.Frame(root, style="App.TFrame")
        self.content.pack(side="left", fill="both", expand=True, padx=32, pady=28)

    def _clear(self) -> None:
        for child in self.content.winfo_children():
            child.destroy()

    def _header(self, title: str, subtitle: str) -> None:
        ttk.Label(self.content, text=title, style="Title.TLabel").pack(anchor="w")
        ttk.Label(self.content, text=subtitle, style="Subtitle.TLabel").pack(anchor="w", pady=(4, 22))

    def _tool_card(self, parent: tk.Misc, icon: str, name: str, desc: str, key: str) -> None:
        card = ttk.Frame(parent, style="Card.TFrame")
        card.pack(side="left", fill="both", expand=True, padx=7, pady=7)
        ttk.Label(card, text=f"{icon}  {name}", style="CardTitle.TLabel").pack(anchor="w", padx=16, pady=(18, 6))
        ttk.Label(card, text=desc, style="CardText.TLabel", wraplength=220).pack(anchor="w", padx=16, pady=(0, 14))
        ttk.Button(card, text="Open tool →", style="Tool.TButton",
                   command=lambda: self.show_tool(key)).pack(fill="x", padx=14, pady=(0, 15))

    def show_home(self) -> None:
        self._clear()
        self._header("AI Business Operator", "One interface for your AI tools. Click a tool to open it.")

        intro = ttk.Frame(self.content, style="Card.TFrame")
        intro.pack(fill="x", pady=(0, 18))
        ttk.Label(intro, text="What do you want the AI to do?", style="CardTitle.TLabel").pack(
            anchor="w", padx=18, pady=(16, 5)
        )
        ttk.Label(
            intro,
            text="Describe a task in normal language. The selected tool will use the existing orchestration engine.",
            style="CardText.TLabel",
        ).pack(anchor="w", padx=18, pady=(0, 14))

        rows = [self.TOOLS[i:i + 3] for i in range(0, len(self.TOOLS), 3)]
        for row in rows:
            frame = ttk.Frame(self.content, style="App.TFrame")
            frame.pack(fill="x")
            for icon, name, desc, key in row:
                self._tool_card(frame, icon, name, desc, key)

    def _text_area(self, parent: tk.Misc, height: int = 13) -> tk.Text:
        box = tk.Text(parent, height=height, bg="#11182d", fg="#e9efff",
                      insertbackground="#ffffff", relief="flat", borderwidth=0,
                      font=("Consolas", 10), padx=12, pady=10, wrap="word")
        box.pack(fill="both", expand=True, pady=(8, 12))
        return box

    def _run_async(self, work: Callable[[], object], output: tk.Text, button: ttk.Button | None = None) -> None:
        if button:
            button.configure(state="disabled")
        output.delete("1.0", "end")
        output.insert("end", "Running...\n")

        def runner() -> None:
            try:
                result = work()
                payload = result if isinstance(result, str) else json.dumps(result, indent=2, default=str)
            except Exception as exc:
                payload = f"ERROR: {exc}"
            self.after(0, lambda: self._finish(output, payload, button))

        threading.Thread(target=runner, daemon=True).start()

    def _finish(self, output: tk.Text, payload: str, button: ttk.Button | None) -> None:
        output.delete("1.0", "end")
        output.insert("end", payload)
        if button:
            button.configure(state="normal")

    def show_tool(self, key: str) -> None:
        pages = {
            "brain": self._brain_page,
            "workflow": self._workflow_page,
            "research": self._research_page,
            "app": self._app_page,
            "repair": self._repair_page,
            "deploy": self._deploy_page,
            "integrations": self._integrations_page,
            "credentials": self._credentials_page,
        }
        pages[key]()

    def _request_page(self, title: str, subtitle: str, action: str, worker: Callable[[str], object]) -> None:
        self._clear()
        self._header(title, subtitle)

        card = ttk.Frame(self.content, style="Card.TFrame")
        card.pack(fill="both", expand=True)
        ttk.Label(card, text="Describe what you need", style="CardTitle.TLabel").pack(
            anchor="w", padx=18, pady=(18, 4)
        )
        request = self._text_area(card, 7)
        request.insert("1.0", "Build a workflow that ...")

        result = self._text_area(card, 18)
        button = ttk.Button(
            card, text=action, style="Primary.TButton",
            command=lambda: self._run_async(lambda: worker(request.get("1.0", "end").strip()), result, button),
        )
        button.pack(fill="x", padx=18, pady=(0, 10))
        result.pack_forget()
        result.pack(fill="both", expand=True, padx=18, pady=(4, 18))

    def _brain_page(self) -> None:
        self._request_page(
            "🧠 AI Brain",
            "Understand a request and show the selected provider, requirements, and clarification needs.",
            "Analyze request",
            self.orchestrator.decide,
        )

    def _workflow_page(self) -> None:
        self._request_page(
            "🔄 Workflow Builder",
            "Turn natural language into a validated workflow plan.",
            "Build workflow",
            lambda request: self.orchestrator.build(request).model_dump(mode="json"),
        )

    def _research_page(self) -> None:
        self._request_page(
            "🔍 Research",
            "Run the repository's research engine against a business or automation request.",
            "Research",
            self.orchestrator.research,
        )

    def _app_page(self) -> None:
        self._request_page(
            "🌐 App Builder",
            "Create an autonomous project plan using the existing project builder.",
            "Build app plan",
            self.orchestrator.build_project,
        )

    def _repair_page(self) -> None:
        self._request_page(
            "🧪 Test & Repair",
            "Test a workflow and attempt deterministic repairs.",
            "Test & repair",
            self.orchestrator.test_and_repair,
        )

    def _deploy_page(self) -> None:
        self._request_page(
            "🚀 Deployment",
            "Create a safe deployment plan. Live external deployment remains disabled by default.",
            "Plan deployment",
            self.orchestrator.plan_deployment,
        )

    def _integrations_page(self) -> None:
        self._clear()
        self._header("🔌 Integrations", "See the capabilities currently registered with the orchestrator.")
        result = self._text_area(self.content, 28)
        try:
            payload = self.orchestrator.list_integrations()
            result.insert("end", json.dumps(payload, indent=2, default=str))
        except Exception as exc:
            result.insert("end", f"ERROR: {exc}")

    def _credentials_page(self) -> None:
        self._clear()
        self._header("🔐 Credentials", "Check provider readiness without exposing secret values.")
        result = self._text_area(self.content, 28)
        try:
            payload = self.orchestrator.credential_status()
            result.insert("end", json.dumps(payload, indent=2, default=str))
        except Exception as exc:
            result.insert("end", f"ERROR: {exc}")


def launch() -> None:
    ToolControlCenter().mainloop()


if __name__ == "__main__":
    launch()
