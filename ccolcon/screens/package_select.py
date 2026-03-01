"""Screen for selecting packages to build."""

from typing import List, Tuple
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import DataTable, Static, Header, Footer
from textual.binding import Binding
from ccolcon.models.build_config import BuildConfig
from ccolcon.colcon.executor import ColconExecutor


class PackageSelectScreen(Screen):
    """Screen for selecting packages to build."""

    BINDINGS = [
        Binding("c", "confirm", "Confirm Build", show=True),
        Binding("a", "select_all", "Select All", show=True),
        Binding("space", "toggle_selection", "Toggle", show=False),
        Binding("escape", "back", "Back", show=False),
    ]

    def __init__(self, build_config: BuildConfig) -> None:
        """Initialize the package selection screen.

        Args:
            build_config: Build configuration object.
        """
        super().__init__()
        self.config = build_config
        self.executor = ColconExecutor(
            workspace_path=build_config.workspace_path,
            log_dir="log"
        )
        # Track package selection state: {package_name: bool}
        self._selected_packages = set()

    def compose(self) -> ComposeResult:
        """Compose the screen layout."""
        yield Header()
        yield Static("[bold]Select Packages to Build[/bold]", id="title")
        yield DataTable(id="packages-table")
        yield Static("Press [bold]Space[/bold] to toggle, [bold]c[/bold] to build, [bold]a[/bold] to select all, [bold]Esc[/bold] to go back", id="help-text")
        yield Footer()

    def on_mount(self) -> None:
        """Initialize the package list when screen is mounted."""
        try:
            packages = self.executor.list_packages()

            table = self.query_one(DataTable)
            table.add_column("Package", width=30)
            table.add_column("Type", width=15)
            table.add_column("Path", width=40)
            table.add_column("Status", width=12)
            table.zebra_stripes = True

            # Load previously selected packages from config
            self._selected_packages = set(self.config.selected_packages)

            # Add all packages
            for pkg_name, pkg_path, pkg_type in packages:
                # Simplify package type for display
                type_display = pkg_type.replace("ros.", "")
                status = "Selected" if pkg_name in self._selected_packages else "Ignored"
                table.add_row(pkg_name, type_display, pkg_path, status)

            table.cursor_type = "row"
            table.focus()

        except Exception as e:
            self.app.notify(f"Failed to list packages: {e}", severity="error")
            self.action_back()

    def action_toggle_selection(self) -> None:
        """Toggle selection of the currently focused package."""
        table = self.query_one(DataTable)
        if not table.row_count:
            return

        row_index = table.cursor_row
        cell_key = table.get_row_at(row_index)[0]  # Package name is in first column

        if cell_key in self._selected_packages:
            self._selected_packages.remove(cell_key)
        else:
            self._selected_packages.add(cell_key)

        self._refresh_table(target_row=row_index)

    def action_confirm(self) -> None:
        """Confirm and start build process."""
        # Update config with selected packages
        self.config.selected_packages = list(self._selected_packages)

        # Exit UI to start build
        self.app.exit(result="build")

    def action_back(self) -> None:
        """Go back to build options screen."""
        self.app.pop_screen()

    def action_select_all(self) -> None:
        """Toggle selection of all packages."""
        table = self.query_one(DataTable)
        if not table.row_count:
            return

        if len(self._selected_packages) == table.row_count:
            # Deselect all
            self._selected_packages.clear()
        else:
            # Select all
            for row_index in range(table.row_count):
                pkg_name = table.get_row_at(row_index)[0]
                self._selected_packages.add(pkg_name)

        self._refresh_table(target_row=table.cursor_row)

    def _refresh_table(self, target_row: int = 0) -> None:
        """Refresh table with current selection state and set cursor position.

        Args:
            target_row: Row to move cursor to after refresh.
        """
        table = self.query_one(DataTable)

        # Get current cursor position and selection
        current_row = table.cursor_row if table.row_count > 0 else 0

        # Store the package name of the current row
        current_pkg = None
        if table.row_count > 0:
            current_pkg = table.get_row_at(current_row)[0]

        table.clear()

        # Re-add all packages with updated status
        try:
            packages = self.executor.list_packages()
            for pkg_name, pkg_path, pkg_type in packages:
                type_display = pkg_type.replace("ros.", "")
                status = "Selected" if pkg_name in self._selected_packages else "Ignored"
                table.add_row(pkg_name, type_display, pkg_path, status)
        except Exception:
            pass

        # Restore cursor position
        if table.row_count > 0:
            safe_row = max(0, min(target_row, table.row_count - 1))
            table.move_cursor(row=safe_row)
