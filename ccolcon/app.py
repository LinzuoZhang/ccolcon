"""Main Textual App class for ccolcon."""

from textual.app import App
from ccolcon.models.build_config import BuildConfig
from ccolcon.screens.build_options import BuildOptionsScreen
from ccolcon.screens.package_select import PackageSelectScreen


class CcolconApp(App):
    """Main ccolcon application."""
    
    # 1. 定义全局 CSS
    CSS = """
    Screen {
        background: black;
        color: white;
    }

    #title {
        content-align: center middle;
        text-align: center;
        padding: 1;
        text-style: bold;
    }

    #help-text {
        content-align: center middle;
        text-align: center;
        padding: 1;
        text-style: dim;
    }

    /* --- DataTable 样式 --- */
    DataTable {
        margin: 2;
        border: thick white;
    }

    DataTable > .datatable--cursor {
        text-style: bold reverse;
    }

    #edit-modal {
        background: black;
        border: thick white;
        width: 60;
        height: 5;
        align: center middle;
        content-align: center middle;
    }

    Input {
        width: 50;
    }
    """

    SCREENS = {
        "build_options": BuildOptionsScreen,
        "package_select": PackageSelectScreen,
    }

    def __init__(self, workspace_path: str = ".") -> None:
        super().__init__()
        self.workspace_path = workspace_path
        self.config = BuildConfig(workspace_path=workspace_path)
        self.config.load_from_file()

    def on_mount(self) -> None:
        self.push_screen(BuildOptionsScreen(self.config))

    def run_with_config(self) -> BuildConfig | None:
        result = self.run()
        if result == "build":
            return self.config
        return None