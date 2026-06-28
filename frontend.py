from __future__ import annotations

import os
from datetime import date, datetime
from typing import Any

import flet as ft
import requests
from dotenv import load_dotenv


load_dotenv()

API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")
MONEY = "R$ {:,.2f}"
CENTER = ft.Alignment(0, 0)


def padding_symmetric(vertical: int = 0, horizontal: int = 0) -> ft.Padding:
    return ft.Padding(horizontal, vertical, horizontal, vertical)


def border_all(width: int = 1, color: str = "#e5e7eb") -> ft.Border:
    side = ft.BorderSide(width, color)
    return ft.Border(top=side, right=side, bottom=side, left=side)


def border_right(width: int = 1, color: str = "#e5e7eb") -> ft.Border:
    return ft.Border(right=ft.BorderSide(width, color))


def money(value: float | int | None) -> str:
    if value is None:
        value = 0
    return MONEY.format(float(value)).replace(",", "X").replace(".", ",").replace("X", ".")


def format_api_error(detail: Any, fallback: str) -> str:
    if isinstance(detail, str):
        return detail
    if isinstance(detail, list):
        messages = []
        for error in detail:
            if not isinstance(error, dict):
                continue
            field = " > ".join(str(part) for part in error.get("loc", []) if part != "body")
            message = error.get("msg", fallback)
            messages.append(f"{field}: {message}" if field else message)
        if messages:
            return "; ".join(messages)
    return fallback


def parse_optional_date(value: str) -> str | None:
    value = value.strip()
    if not value:
        return None
    try:
        datetime.strptime(value, "%Y-%m-%d")
    except ValueError as exc:
        raise ValueError("Use uma data no formato AAAA-MM-DD, por exemplo 2026-12-31.") from exc
    return value


class ApiClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self.token: str | None = None
        self.user: dict[str, Any] | None = None

    @property
    def headers(self) -> dict[str, str]:
        if not self.token:
            return {}
        return {"Authorization": f"Bearer {self.token}"}

    def request(self, method: str, path: str, **kwargs: Any) -> Any:
        response = requests.request(
            method,
            f"{self.base_url}{path}",
            headers={**self.headers, **kwargs.pop("headers", {})},
            timeout=10,
            **kwargs,
        )
        try:
            payload = response.json()
        except ValueError:
            payload = {}
        if response.status_code >= 400:
            detail = payload.get("detail") if isinstance(payload, dict) else None
            raise RuntimeError(format_api_error(detail, f"Erro HTTP {response.status_code}"))
        return payload

    def login(self, email: str, password: str) -> None:
        payload = self.request("POST", "/api/auth/login", json={"email": email, "password": password})
        self.token = payload["access_token"]
        self.user = payload.get("user")

    def register(self, name: str, email: str, password: str) -> None:
        self.request(
            "POST",
            "/api/auth/register",
            json={"full_name": name, "email": email, "password": password},
        )

    def get(self, path: str) -> Any:
        return self.request("GET", path)

    def post(self, path: str, payload: dict[str, Any]) -> Any:
        return self.request("POST", path, json=payload)

    def put(self, path: str, payload: dict[str, Any]) -> Any:
        return self.request("PUT", path, json=payload)

    def delete(self, path: str) -> Any:
        return self.request("DELETE", path)


class FinanceApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.api = ApiClient(API_BASE_URL)
        self.selected_tab = 0
        self.categories: list[dict[str, Any]] = []
        self.transactions: list[dict[str, Any]] = []
        self.goals: list[dict[str, Any]] = []
        self.summary: dict[str, Any] = {}
        self.current_dialog: ft.AlertDialog | None = None

        page.title = "Finance"
        page.theme_mode = ft.ThemeMode.LIGHT
        page.padding = 0
        page.bgcolor = "#f6f7f9"
        page.window_min_width = 980
        page.window_min_height = 680
        page.theme = ft.Theme(
            color_scheme_seed="#0f766e",
            visual_density=ft.VisualDensity.COMFORTABLE,
            font_family="Arial",
        )

    def run(self) -> None:
        self.show_auth()

    def notify(self, message: str, error: bool = False) -> None:
        self.page.snack_bar = ft.SnackBar(
            ft.Text(message),
            bgcolor="#b91c1c" if error else "#0f766e",
        )
        self.page.snack_bar.open = True
        self.page.update()

    def show_auth(self) -> None:
        login_email = ft.TextField(label="Email", keyboard_type=ft.KeyboardType.EMAIL, autofocus=True)
        login_password = ft.TextField(label="Senha", password=True, can_reveal_password=True)
        register_name = ft.TextField(label="Nome completo")
        register_email = ft.TextField(label="Email", keyboard_type=ft.KeyboardType.EMAIL)
        register_password = ft.TextField(label="Senha", password=True, can_reveal_password=True)

        def do_login(_: ft.ControlEvent) -> None:
            try:
                self.api.login(login_email.value.strip(), login_password.value)
                self.load_data()
                self.show_app()
            except Exception as exc:
                self.notify(str(exc), error=True)

        def do_register(_: ft.ControlEvent) -> None:
            try:
                self.api.register(
                    register_name.value.strip(),
                    register_email.value.strip(),
                    register_password.value,
                )
                self.notify("Cadastro criado. Entre com seu email e senha.")
                login_email.value = register_email.value
                login_password.value = ""
                self.page.update()
            except Exception as exc:
                self.notify(str(exc), error=True)

        self.page.controls = [
            ft.Container(
                expand=True,
                alignment=CENTER,
                padding=32,
                content=ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        self.auth_card(
                            "Finance",
                            "Entre para gerenciar receitas, despesas, categorias e metas.",
                            [login_email, login_password, ft.FilledButton("Entrar", icon=ft.Icons.LOGIN, on_click=do_login)],
                            large=True,
                        ),
                        self.auth_card(
                            "Criar conta",
                            "",
                            [
                                register_name,
                                register_email,
                                register_password,
                                ft.OutlinedButton("Cadastrar", icon=ft.Icons.PERSON_ADD, on_click=do_register),
                            ],
                        ),
                    ],
                ),
            )
        ]
        self.page.update()

    def auth_card(self, title: str, subtitle: str, controls: list[ft.Control], large: bool = False) -> ft.Control:
        content = [ft.Text(title, size=36 if large else 24, weight=ft.FontWeight.BOLD, color="#111827")]
        if subtitle:
            content.append(ft.Text(subtitle, color="#4b5563"))
        content.extend(controls)
        return ft.Container(
            width=420,
            padding=32,
            border_radius=8,
            bgcolor="#ffffff",
            border=border_all(1, "#e5e7eb"),
            content=ft.Column(spacing=18, tight=True, controls=content),
        )

    def show_app(self) -> None:
        user = self.api.user or {}
        rail = ft.NavigationRail(
            selected_index=self.selected_tab,
            label_type=ft.NavigationRailLabelType.ALL,
            min_width=96,
            destinations=[
                ft.NavigationRailDestination(icon=ft.Icons.DASHBOARD_OUTLINED, selected_icon=ft.Icons.DASHBOARD, label="Resumo"),
                ft.NavigationRailDestination(icon=ft.Icons.SWAP_VERT, label="Transacoes"),
                ft.NavigationRailDestination(icon=ft.Icons.CATEGORY_OUTLINED, selected_icon=ft.Icons.CATEGORY, label="Categorias"),
                ft.NavigationRailDestination(icon=ft.Icons.FLAG_OUTLINED, selected_icon=ft.Icons.FLAG, label="Metas"),
            ],
            on_change=self.change_tab,
        )
        self.content = ft.Container(expand=True, padding=24)
        self.page.controls = [
            ft.Row(
                expand=True,
                spacing=0,
                controls=[
                    ft.Container(
                        width=220,
                        bgcolor="#ffffff",
                        border=border_right(1, "#e5e7eb"),
                        padding=padding_symmetric(vertical=20),
                        content=ft.Column(
                            expand=True,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            controls=[
                                ft.Text("Finance", size=24, weight=ft.FontWeight.BOLD, color="#0f766e"),
                                ft.Text(user.get("name", ""), size=12, color="#6b7280"),
                                ft.Divider(height=24),
                                ft.Container(expand=True, content=rail),
                                ft.Container(expand=True),
                                ft.IconButton(icon=ft.Icons.LOGOUT, tooltip="Sair", on_click=self.logout),
                            ],
                        ),
                    ),
                    self.content,
                ],
            )
        ]
        self.render_content()
        self.page.update()

    def change_tab(self, event: ft.ControlEvent) -> None:
        self.selected_tab = event.control.selected_index
        self.render_content()

    def logout(self, _: ft.ControlEvent) -> None:
        self.api.token = None
        self.api.user = None
        self.show_auth()

    def load_data(self) -> None:
        self.summary = self.api.get("/api/reports/summary")
        self.categories = self.api.get("/api/categories")
        self.transactions = self.api.get("/api/transactions")
        self.goals = self.api.get("/api/goals")

    def refresh(self) -> None:
        try:
            self.load_data()
            self.render_content()
            self.notify("Dados atualizados.")
        except Exception as exc:
            self.notify(str(exc), error=True)

    def render_content(self) -> None:
        views = [self.dashboard_view, self.transactions_view, self.categories_view, self.goals_view]
        self.content.content = views[self.selected_tab]()
        self.page.update()

    def header(self, title: str, action: ft.Control | None = None) -> ft.Control:
        controls = [
            ft.Column(
                spacing=2,
                controls=[
                    ft.Text(title, size=28, weight=ft.FontWeight.BOLD, color="#111827"),
                    ft.Text("API: " + self.api.base_url, size=12, color="#6b7280"),
                ],
            ),
            ft.Container(expand=True),
            ft.IconButton(icon=ft.Icons.REFRESH, tooltip="Atualizar", on_click=lambda _: self.refresh()),
        ]
        if action:
            controls.append(action)
        return ft.Row(controls=controls, vertical_alignment=ft.CrossAxisAlignment.CENTER)

    def metric_card(self, label: str, value: str, icon: str, color: str) -> ft.Control:
        return ft.Container(
            expand=True,
            padding=18,
            border_radius=8,
            bgcolor="#ffffff",
            border=border_all(1, "#e5e7eb"),
            content=ft.Row(
                controls=[
                    ft.Container(
                        width=44,
                        height=44,
                        border_radius=8,
                        bgcolor=color,
                        alignment=CENTER,
                        content=ft.Icon(icon, color="#ffffff"),
                    ),
                    ft.Column(
                        spacing=2,
                        controls=[
                            ft.Text(label, size=12, color="#6b7280"),
                            ft.Text(value, size=22, weight=ft.FontWeight.BOLD, color="#111827"),
                        ],
                    ),
                ],
            ),
        )

    def dashboard_view(self) -> ft.Control:
        expenses = self.summary.get("expenses_by_category", [])
        goals = self.summary.get("goals_progress", [])
        return ft.Column(
            expand=True,
            spacing=20,
            scroll=ft.ScrollMode.AUTO,
            controls=[
                self.header("Resumo"),
                ft.Row(
                    controls=[
                        self.metric_card("Receitas", money(self.summary.get("total_income")), ft.Icons.TRENDING_UP, "#0f766e"),
                        self.metric_card("Despesas", money(self.summary.get("total_expenses")), ft.Icons.TRENDING_DOWN, "#dc2626"),
                        self.metric_card("Saldo", money(self.summary.get("balance")), ft.Icons.ACCOUNT_BALANCE_WALLET, "#2563eb"),
                        self.metric_card("Transacoes", str(self.summary.get("transaction_count", 0)), ft.Icons.RECEIPT_LONG, "#7c3aed"),
                    ]
                ),
                ft.Row(
                    vertical_alignment=ft.CrossAxisAlignment.START,
                    controls=[
                        self.panel(
                            "Gastos por categoria",
                            [
                                ft.ListTile(
                                    leading=ft.Container(width=12, height=12, border_radius=6, bgcolor=item.get("color", "#2563eb")),
                                    title=ft.Text(item.get("category", "")),
                                    trailing=ft.Text(money(item.get("total")), weight=ft.FontWeight.BOLD),
                                )
                                for item in expenses
                            ]
                            or [ft.Text("Nenhuma despesa registrada.", color="#6b7280")],
                        ),
                        self.panel(
                            "Progresso das metas",
                            [
                                ft.Column(
                                    spacing=6,
                                    controls=[
                                        ft.Row(
                                            controls=[
                                                ft.Text(item.get("title", ""), weight=ft.FontWeight.BOLD),
                                                ft.Container(expand=True),
                                                ft.Text(f"{item.get('progress_percent', 0)}%"),
                                            ]
                                        ),
                                        ft.ProgressBar(value=min(float(item.get("progress_percent", 0)) / 100, 1), color="#0f766e"),
                                        ft.Text(f"{money(item.get('current_amount'))} de {money(item.get('target_amount'))}", size=12, color="#6b7280"),
                                    ],
                                )
                                for item in goals
                            ]
                            or [ft.Text("Nenhuma meta cadastrada.", color="#6b7280")],
                        ),
                    ],
                ),
            ],
        )

    def panel(self, title: str, controls: list[ft.Control]) -> ft.Control:
        return ft.Container(
            expand=True,
            padding=18,
            border_radius=8,
            bgcolor="#ffffff",
            border=border_all(1, "#e5e7eb"),
            content=ft.Column(
                spacing=12,
                controls=[ft.Text(title, size=18, weight=ft.FontWeight.BOLD, color="#111827"), *controls],
            ),
        )

    def transactions_view(self) -> ft.Control:
        add_button = ft.FilledButton("Nova", icon=ft.Icons.ADD, on_click=lambda _: self.open_transaction_dialog())
        rows = []
        category_names = {item["id"]: item["name"] for item in self.categories}
        for item in self.transactions:
            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(item.get("transaction_date", ""))),
                        ft.DataCell(ft.Text(item.get("description", ""))),
                        ft.DataCell(ft.Text(item.get("type", ""))),
                        ft.DataCell(ft.Text(category_names.get(item.get("category_id"), "-"))),
                        ft.DataCell(ft.Text(money(item.get("amount")))),
                        ft.DataCell(
                            ft.Row(
                                spacing=0,
                                controls=[
                                    ft.IconButton(ft.Icons.EDIT, tooltip="Editar", on_click=lambda _, tx=item: self.open_transaction_dialog(tx)),
                                    ft.IconButton(ft.Icons.DELETE_OUTLINE, tooltip="Excluir", on_click=lambda _, tx=item: self.delete_item("transactions", tx["id"])),
                                ],
                            )
                        ),
                    ]
                )
            )
        return ft.Column(
            expand=True,
            spacing=20,
            controls=[
                self.header("Transacoes", add_button),
                ft.Container(
                    expand=True,
                    padding=12,
                    border_radius=8,
                    bgcolor="#ffffff",
                    border=border_all(1, "#e5e7eb"),
                    content=ft.Column(
                        scroll=ft.ScrollMode.AUTO,
                        controls=[
                            ft.DataTable(
                                columns=[
                                    ft.DataColumn(ft.Text("Data")),
                                    ft.DataColumn(ft.Text("Descricao")),
                                    ft.DataColumn(ft.Text("Tipo")),
                                    ft.DataColumn(ft.Text("Categoria")),
                                    ft.DataColumn(ft.Text("Valor")),
                                    ft.DataColumn(ft.Text("Acoes")),
                                ],
                                rows=rows,
                            )
                        ],
                    ),
                ),
            ],
        )

    def categories_view(self) -> ft.Control:
        add_button = ft.FilledButton("Nova", icon=ft.Icons.ADD, on_click=lambda _: self.open_category_dialog())
        return ft.Column(
            expand=True,
            spacing=20,
            controls=[
                self.header("Categorias", add_button),
                ft.GridView(
                    expand=True,
                    max_extent=320,
                    child_aspect_ratio=2.6,
                    spacing=12,
                    run_spacing=12,
                    controls=[
                        ft.Container(
                            padding=16,
                            border_radius=8,
                            bgcolor="#ffffff",
                            border=border_all(1, "#e5e7eb"),
                            content=ft.Row(
                                controls=[
                                    ft.Container(width=12, height=48, border_radius=6, bgcolor=item.get("color", "#2563eb")),
                                    ft.Column(
                                        expand=True,
                                        spacing=2,
                                        controls=[
                                            ft.Text(item.get("name", ""), weight=ft.FontWeight.BOLD),
                                            ft.Text(item.get("type", ""), size=12, color="#6b7280"),
                                        ],
                                    ),
                                    ft.IconButton(ft.Icons.EDIT, tooltip="Editar", on_click=lambda _, cat=item: self.open_category_dialog(cat)),
                                    ft.IconButton(ft.Icons.DELETE_OUTLINE, tooltip="Excluir", on_click=lambda _, cat=item: self.delete_item("categories", cat["id"])),
                                ],
                            ),
                        )
                        for item in self.categories
                    ],
                ),
            ],
        )

    def goals_view(self) -> ft.Control:
        add_button = ft.FilledButton("Nova", icon=ft.Icons.ADD, on_click=lambda _: self.open_goal_dialog())
        goals_by_id = {item.get("id"): item for item in self.goals}
        goal_progress = self.summary.get("goals_progress") or self.goals
        return ft.Column(
            expand=True,
            spacing=20,
            controls=[
                self.header("Metas", add_button),
                ft.GridView(
                    expand=True,
                    max_extent=420,
                    child_aspect_ratio=2.2,
                    spacing=12,
                    run_spacing=12,
                    controls=[self.goal_card(item, goals_by_id.get(item.get("id"), item)) for item in goal_progress],
                ),
            ],
        )

    def goal_card(self, item: dict[str, Any], editable_item: dict[str, Any] | None = None) -> ft.Control:
        editable_item = editable_item or item
        target = float(item.get("target_amount") or 0)
        current = float(item.get("current_amount") or 0)
        percent = current / target if target else 0
        return ft.Container(
            padding=16,
            border_radius=8,
            bgcolor="#ffffff",
            border=border_all(1, "#e5e7eb"),
            content=ft.Column(
                spacing=8,
                controls=[
                    ft.Row(
                        controls=[
                            ft.Text(item.get("title", ""), expand=True, weight=ft.FontWeight.BOLD),
                            ft.IconButton(ft.Icons.EDIT, tooltip="Editar", on_click=lambda _, goal=editable_item: self.open_goal_dialog(goal)),
                            ft.IconButton(ft.Icons.DELETE_OUTLINE, tooltip="Excluir", on_click=lambda _, goal=editable_item: self.delete_item("goals", goal["id"])),
                        ]
                    ),
                    ft.ProgressBar(value=min(percent, 1), color="#0f766e"),
                    ft.Text(f"{money(current)} de {money(target)}", size=12, color="#6b7280"),
                    ft.Text(f"{item.get('status', '')} | prazo: {item.get('deadline') or '-'}", size=12, color="#6b7280"),
                ],
            ),
        )

    def open_transaction_dialog(self, item: dict[str, Any] | None = None) -> None:
        item = item or {}
        description = ft.TextField(label="Descricao", value=item.get("description", ""))
        amount = ft.TextField(label="Valor", value=str(item.get("amount", "")), keyboard_type=ft.KeyboardType.NUMBER)
        transaction_type = ft.Dropdown(
            label="Tipo",
            value=item.get("type", "despesa"),
            options=[ft.dropdown.Option("receita"), ft.dropdown.Option("despesa")],
        )
        category = ft.Dropdown(
            label="Categoria",
            value=str(item.get("category_id")) if item.get("category_id") else None,
            options=[ft.dropdown.Option(str(cat["id"]), cat["name"]) for cat in self.categories],
        )
        transaction_date = ft.TextField(label="Data", value=item.get("transaction_date", date.today().isoformat()))
        payment_method = ft.TextField(label="Pagamento", value=item.get("payment_method") or "")
        notes = ft.TextField(label="Notas", value=item.get("notes") or "", multiline=True, min_lines=2)

        def save(_: ft.ControlEvent) -> None:
            payload = {
                "description": description.value.strip(),
                "type": transaction_type.value,
                "amount": float((amount.value or "0").replace(",", ".")),
                "transaction_date": transaction_date.value.strip(),
                "category_id": int(category.value) if category.value else None,
                "payment_method": payment_method.value.strip() or None,
                "notes": notes.value.strip() or None,
            }
            self.save_dialog("transactions", item.get("id"), payload)

        self.open_dialog(
            "Transacao",
            [description, ft.Row([amount, transaction_type]), category, transaction_date, payment_method, notes],
            save,
        )

    def open_category_dialog(self, item: dict[str, Any] | None = None) -> None:
        item = item or {}
        name = ft.TextField(label="Nome", value=item.get("name", ""))
        category_type = ft.Dropdown(
            label="Tipo",
            value=item.get("type", "despesa"),
            options=[ft.dropdown.Option("receita"), ft.dropdown.Option("despesa")],
        )
        color = ft.TextField(label="Cor", value=item.get("color", "#2563eb"))

        def save(_: ft.ControlEvent) -> None:
            self.save_dialog(
                "categories",
                item.get("id"),
                {"name": name.value.strip(), "type": category_type.value, "color": color.value.strip()},
            )

        self.open_dialog("Categoria", [name, category_type, color], save)

    def open_goal_dialog(self, item: dict[str, Any] | None = None) -> None:
        item = item or {}
        title = ft.TextField(label="Titulo", value=item.get("title", ""))
        target = ft.TextField(label="Valor alvo", value=str(item.get("target_amount", "")), keyboard_type=ft.KeyboardType.NUMBER)
        current = ft.TextField(label="Valor atual", value=str(item.get("current_amount", 0)), keyboard_type=ft.KeyboardType.NUMBER)
        deadline = ft.TextField(
            label="Prazo (AAAA-MM-DD)",
            hint_text="AAAA-MM-DD",
            value=item.get("deadline") or "",
        )
        status = ft.Dropdown(
            label="Status",
            value=item.get("status", "ativa"),
            options=[ft.dropdown.Option("ativa"), ft.dropdown.Option("concluida"), ft.dropdown.Option("pausada")],
        )

        def save(_: ft.ControlEvent) -> None:
            try:
                payload = {
                    "title": title.value.strip(),
                    "target_amount": float((target.value or "0").replace(",", ".")),
                    "current_amount": float((current.value or "0").replace(",", ".")),
                    "deadline": parse_optional_date(deadline.value),
                    "status": status.value,
                }
            except ValueError as exc:
                self.notify(str(exc), error=True)
                return
            self.save_dialog("goals", item.get("id"), payload)

        self.open_dialog("Meta", [title, ft.Row([target, current]), deadline, status], save)

    def open_dialog(self, title: str, controls: list[ft.Control], on_save) -> None:
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(title),
            content=ft.Container(width=520, content=ft.Column(tight=True, spacing=12, controls=controls)),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda _: self.close_dialog()),
                ft.FilledButton("Salvar", icon=ft.Icons.SAVE, on_click=on_save),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.current_dialog = dialog
        self.page.show_dialog(dialog)

    def close_dialog(self) -> None:
        if self.current_dialog:
            self.page.pop_dialog()
            self.current_dialog = None

    def save_dialog(self, resource: str, item_id: int | None, payload: dict[str, Any]) -> None:
        try:
            if item_id:
                self.api.put(f"/api/{resource}/{item_id}", payload)
            else:
                self.api.post(f"/api/{resource}", payload)
            self.close_dialog()
            self.load_data()
            self.render_content()
            self.notify("Salvo com sucesso.")
        except Exception as exc:
            self.notify(str(exc), error=True)

    def delete_item(self, resource: str, item_id: int) -> None:
        try:
            self.api.delete(f"/api/{resource}/{item_id}")
            self.load_data()
            self.render_content()
            self.notify("Item excluido.")
        except Exception as exc:
            self.notify(str(exc), error=True)


def main(page: ft.Page) -> None:
    FinanceApp(page).run()


if __name__ == "__main__":
    ft.run(main)
