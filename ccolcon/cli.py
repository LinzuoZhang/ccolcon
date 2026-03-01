"""Command-line interface for ccolcon."""

import sys
import argparse
import os
import subprocess
from pathlib import Path

from ccolcon.app import CcolconApp
from ccolcon.colcon.executor import ColconExecutor
from ccolcon.models.build_config import BuildConfig


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments.

    Returns:
        Parsed arguments namespace.
    """
    parser = argparse.ArgumentParser(
        description="ccolcon - Interactive terminal tool for compiling ROS2 workspaces"
    )
    parser.add_argument(
        "command",
        nargs="?",
        help="Colcon command to execute (build, list, info, etc.)"
    )
    parser.add_argument(
        "args",
        nargs=argparse.REMAINDER,
        help="Additional arguments to pass to colcon"
    )
    parser.add_argument(
        "--workspace",
        "-w",
        default=".",
        help="Path to ROS2 workspace (default: current directory)"
    )
    parser.add_argument(
        "--log-dir",
        "-l",
        default="log",
        help="Directory for build logs (default: log)"
    )
    return parser.parse_args()


def main() -> int:
    """Main entry point for ccolcon CLI.

    Returns:
        Exit code (0 for success, non-zero for failure).
    """
    args = parse_args()

    # Resolve workspace path
    workspace_path = Path(args.workspace).resolve()

    if args.command == "build":
        # Run TUI interface for build command
        print("Starting ccolcon build interface...")
        print(f"Workspace: {workspace_path}")
        print()

        # Run TUI
        app = CcolconApp(workspace_path=str(workspace_path))
        config = app.run_with_config()

        if config:
            # Save configuration to .ccolcon file
            config.save_to_file()

            # User confirmed, execute build
            print()
            print("=" * 80)
            print("Building packages...")
            print("=" * 80)
            print()

            # Build command arguments
            build_args = config.get_colcon_args()

            # Show command
            cmd_str = "colcon build " + " ".join(build_args)
            for arg in sys.argv[2:]:
                if arg.startswith("--workspace") or arg.startswith("-w"):
                    continue  # Skip workspace argument in display
                if arg.startswith("--log-dir") or arg.startswith("-l"):
                    continue  # Skip log dir argument in display
                if not arg.startswith("--") or arg.startswith("-"):
                    continue
                if arg.startswith("--help") or arg.startswith("-h"):
                    continue  # Skip help argument in display
                cmd_str += f" {arg}"
            print(f"Command: {cmd_str}")
            print()

            # Execute
            executor = ColconExecutor(
                workspace_path=str(workspace_path),
                log_dir=args.log_dir
            )
            exit_code = executor.build(build_args)

            print()
            print("=" * 80)
            if exit_code == 0:
                print("Build completed successfully!")
            else:
                print(f"Build failed with exit code: {exit_code}")
            print(f"Log saved to: {executor.log_dir}")
            print("=" * 80)

            return exit_code
        else:
            # User cancelled, show colcon verbs
            print("Build cancelled by user.")
            print()
            print("Available colcon commands:")
            subprocess.run(["colcon", "--help"])
            return 0
    elif args.command:
        # Direct execution of other colcon commands
        # Pass all remaining arguments directly to colcon
        # Remove 'ccolcon' from sys.argv, keep everything else
        cmd = ["colcon"] + sys.argv[1:]
        exit_code = subprocess.run(cmd).returncode
        return exit_code
    else:
        # No command specified, show help
        print("ccolcon - Interactive terminal tool for compiling ROS2 workspaces")
        print()
        print("Usage: ccolcon [command] [options] [args...]")
        print()
        print("Commands:")
        print("  build              Interactive build interface (default for build command)")
        print("  extension-points    List extension points")
        print("  extensions         List extensions")
        print("  graph             Generate dependency graph")
        print("  info              Show package information")
        print("  list              List packages")
        print("  metadata          Manage metadata of packages")
        print("  mixin             Manage mixin predefined sets")
        print("  test              Run tests")
        print("  test-result       Show test results")
        print("  version-check     Check colcon version")
        print()
        print("Options:")
        print("  -w, --workspace PATH   Path to ROS2 workspace")
        print("  -l, --log-dir DIR     Directory for build logs")
        print()
        print("Examples:")
        print("  ccolcon build")
        print("  ccolcon list")
        print("  ccolcon info --help")
        print("  ccolcon test --packages-select my_package")
        return 0


if __name__ == "__main__":
    sys.exit(main())
