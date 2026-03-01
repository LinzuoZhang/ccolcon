"""Build configuration data model."""

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import List
from ccolcon.models.options import BuildOption

ALL_OPTIONS = [
    BuildOption(
        name="symlink-install",
        opt_type="bool",
        default_value="true",
        description="Use symlink install (default: true)"
    ),
    BuildOption(
        name="install-base",
        opt_type="string",
        default_value="install",
        description="Installation base directory (default: install)"
    ),
    BuildOption(
        name="merge-install",
        opt_type="bool",
        default_value="false",
        description="Merge install space (default: false)"
    ),
    BuildOption(
        name="continue-on-error",
        opt_type="bool",
        default_value="false",
        description="Continue building packages even if some fail (default: false)"
    ),
    BuildOption(
        name="parallel-workers",
        opt_type="int",
        default_value="4",
        description="Number of parallel workers (default: 4)"
    ),
]


@dataclass
class BuildConfig:
    """Configuration for colcon build command."""

    selected_packages: List[str] = field(default_factory=list)
    workspace_path: str = "."
    
    def get_all_options(self) -> List[dict]:
        """Get all options with their current values.

        Returns:
            List of option dictionaries with name, value, type, default_value.
        """
        options = []

        for opt in ALL_OPTIONS:
            if not isinstance(opt, BuildOption):
                continue
            # Use default value as fallback
            current_value = opt.current_value if opt.current_value else opt.default_value
            options.append({
                "name": opt.name,
                "value": current_value,
                "type": opt.opt_type,
                "default_value": opt.default_value,
            })

        return options

    def _to_bool(self, value: str) -> bool:
        """Convert string to boolean.

        Args:
            value: String value.

        Returns:
            Boolean value.
        """
        return value.lower() in ("true", "1", "yes", "on", "ON")

    def update_option(self, name: str, value: str) -> None:
        """Update an option value in the configuration.

        Args:
            name: Option name.
            value: New value as string.
        """
        for opt in ALL_OPTIONS:
            if not isinstance(opt, BuildOption):
                continue
            if opt.name == name:
                if opt.opt_type == "bool":
                    opt.current_value = str(self._to_bool(value))
                elif opt.opt_type in ("string", "int", "float"):
                    opt.current_value = value
                break

    def get_colcon_args(self) -> List[str]:
        """Generate colcon command arguments from configuration.

        Returns:
            List of command line arguments for colcon build.
        """
        args = []

        for opt in ALL_OPTIONS:
            if not isinstance(opt, BuildOption):
                continue
            current_value = opt.current_value if opt.current_value else opt.default_value
    
            if opt.opt_type == "bool":
                if self._to_bool(current_value):
                    args.append(f"--{opt.name}")
            elif opt.opt_type in ("string", "int", "float"):
                default_value = opt.default_value
                if str(current_value) != default_value and str(current_value) != "":
                    args.extend([f"--{opt.name}", str(current_value)])
        if len(self.selected_packages) <= 0:
            print("No packages selected, building all packages in workspace.")
        else:
            args.extend(["--packages-select"] + self.selected_packages)

        return args

    def _get_config_file_path(self) -> Path:
        """Get the path to the .ccolcon config file.

        Returns:
            Path object for the config file.
        """
        return Path(self.workspace_path) / ".ccolcon"

    def save_to_file(self) -> None:
        """Save current configuration to .ccolcon file."""
        config_file = self._get_config_file_path()

        # Build options dictionary
        options_dict = {}
        for opt in ALL_OPTIONS:
            if isinstance(opt, BuildOption):
                value = opt.current_value if opt.current_value else opt.default_value
                options_dict[opt.name] = value

        config_data = {
            "version": "1.0",
            "options": options_dict,
            "selected_packages": self.selected_packages
        }

        # Create parent directory if it doesn't exist
        config_file.parent.mkdir(parents=True, exist_ok=True)

        with open(config_file, "w") as f:
            json.dump(config_data, f, indent=2)

    def load_from_file(self) -> None:
        """Load configuration from .ccolcon file if it exists."""
        config_file = self._get_config_file_path()

        if not config_file.exists():
            return  # Use defaults if file doesn't exist

        try:
            with open(config_file, "r") as f:
                config_data = json.load(f)

            # Load options
            if "options" in config_data:
                for name, value in config_data["options"].items():
                    for opt in ALL_OPTIONS:
                        if isinstance(opt, BuildOption) and opt.name == name:
                            opt.current_value = str(value)
                            break

            # Load selected packages
            if "selected_packages" in config_data:
                self.selected_packages = config_data["selected_packages"]

        except (json.JSONDecodeError, KeyError, IOError):
            # If file is corrupted, use defaults
            pass
