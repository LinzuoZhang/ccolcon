"""Screen for configuring build options."""

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import DataTable, Static, Header, Footer, Input
from textual.binding import Binding
from textual.containers import Vertical, Horizontal, Container
from ccolcon.models.build_config import BuildConfig, ALL_OPTIONS
from ccolcon.screens.package_select import PackageSelectScreen


class BuildOptionsScreen(Screen):
    """Screen for configuring build options."""

    BINDINGS = [
        Binding("c", "confirm", "confirm", show=True),
        Binding("e", "edit_or_toggle", "Edit/Toggle", show=True),
        Binding("escape", "exit_or_cancel", "Exit/Cancel", show=False),
    ]

    def __init__(self, config: BuildConfig) -> None:
        """Initialize the build options screen.

        Args:
            config: Build configuration object.
        """
        super().__init__()
        self.config = config
        self.editing_index = -1
        self._is_editing = False


    def compose(self) -> ComposeResult:
        """Compose the screen layout."""
        yield Header()
        yield Static("[bold]Build Options Configuration[/bold]", id="title")
        yield DataTable(id="options-table")
        yield Static("Press [bold]c[/bold] to continue, [bold]Enter[/bold] to edit/toggle, [bold]Esc[/bold] to exit", id="help-text")
        yield Footer()

    def on_mount(self) -> None:
        """Initialize the table when screen is mounted."""
        table = self.query_one(DataTable)
        table.add_column("Option", width=30)
        table.add_column("Value", width=40)
        table.zebra_stripes = True

        self._refresh_table()
        table.cursor_type = "row"
        table.focus()

    def _refresh_table(self, target_row: int = 0) -> None:
        """Refresh table with current values and set cursor position."""
        table = self.query_one(DataTable)
        
        table.clear()
        options = self.config.get_all_options()
        for option in options:
            display_value = self._get_display_value(option)
            table.add_row(option["name"], display_value)
        
        if table.row_count > 0:
            safe_row = max(0, min(target_row, table.row_count - 1))
            table.move_cursor(row=safe_row)
            
    def _get_display_value(self, option: dict) -> str:
        """Get display value for an option.

        Args:
            option: Option dictionary.

        Returns:
            Display value string.
        """
        if option["type"] == "bool":
            return "ON" if self._to_bool(option["value"]) else "OFF"
        return option["value"]

    def _to_bool(self, value: str) -> bool:
        """Convert string to boolean.

        Args:
            value: String value.

        Returns:
            Boolean value.
        """
        return value.lower() in ("true", "1", "yes", "on", "ON")

    def action_edit_or_toggle(self) -> None:
        """Edit or toggle the currently selected row."""
        table = self.query_one(DataTable)
        if not table.row_count:
            return

        row_index = table.cursor_row
        options = self.config.get_all_options()
        option = options[row_index]
        new_value = None
        if option["type"] == "bool":
            # Toggle boolean
            new_value = str(not self._to_bool(option["value"]))
            self.config.update_option(option["name"], new_value)
            self._refresh_table(target_row=row_index)
        elif option["type"] in ("string", "int", "float"):
            # Enter edit mode for string/int/float
            new_value = self.enter_edit_mode(row_index, option)
    
    def enter_edit_mode(self, row_index: int, option: dict) -> None:
        """Enter edit mode for the current string option.

        Args:
            row_index: Index of the row being edited.
            option: Option dictionary.
        """
        self._is_editing = True

        # Create a modal container for editing
        edit_container = Container(id="edit-modal")

        # Mount the edit modal
        self.app.mount(edit_container)

        # Create input widget
        input_widget = Input(value=option["value"], id="edit-input")
        edit_container.mount(input_widget)
        input_widget.focus()
        input_widget.cursor_position = len(input_widget.value)

        # Store state for callback
        self._editing_row_index = row_index

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle input submission.

        Args:
            event: Input submitted event.
        """
        if event.input.id == "edit-input":
            options = self.config.get_all_options()
            opt_name = options[self._editing_row_index]["name"]
            self.config.update_option(opt_name, event.value)
            self._refresh_table(target_row=self._editing_row_index)
            self._is_editing = False
            # Remove edit modal
            edit_modal = self.query_one("#edit-modal", Container)
            edit_modal.remove()
            # Focus back to table
            table = self.query_one(DataTable)
            table.focus()
            return event.value
        return None
    def action_confirm(self) -> None:
        """Confirm and move to next screen."""
        # Notify app to switch screens
        self.app.push_screen(PackageSelectScreen(self.config))

    def action_exit_or_cancel(self) -> None:
        """Exit the application or cancel editing."""
        if self._is_editing:
            # Cancel edit mode
            self._is_editing = False
            edit_modal = self.query_one("#edit-modal", Container)
            edit_modal.remove()
            # Focus back to table
            table = self.query_one(DataTable)
            table.focus()
        else:
            # Exit the application
            self.app.exit()
