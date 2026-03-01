"""Execute colcon commands and manage output."""

import subprocess
from pathlib import Path
from typing import List, Tuple
from datetime import datetime


class ColconExecutor:
    """Execute colcon commands and manage output."""

    def __init__(self, workspace_path: str = ".", log_dir: str = "log"):
        """Initialize the executor.

        Args:
            workspace_path: Path to ROS2 workspace.
            log_dir: Directory for log files.
        """
        self.workspace_path = Path(workspace_path).resolve()
        self.log_dir = Path(log_dir).resolve()
        self.log_dir.mkdir(parents=True, exist_ok=True)

    def build(self, build_args: List[str]) -> int:
        """Execute colcon build command with streaming output.

        Args:
            build_args: Additional arguments for colcon build (without "colcon build").

        Returns:
            Exit code from colcon build.
        """
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        log_file = self.log_dir / f"build_{timestamp}.log"

        # Build command
        cmd = ["colcon", "build"] + build_args

        # Log the command
        with open(log_file, "w") as f:
            f.write(f"Command: {' '.join(cmd)}\n")
            f.write(f"Workspace: {self.workspace_path}\n")
            f.write(f"Timestamp: {timestamp}\n")
            f.write("=" * 80 + "\n\n")

        # Stream output to both terminal and log
        with open(log_file, "a") as f:
            process = subprocess.Popen(
                cmd,
                cwd=self.workspace_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )

            for line in process.stdout:
                print(line, end="")
                f.write(line)

            process.wait()
            f.write(f"\n\nExit code: {process.returncode}\n")

        return process.returncode

    def list_packages(self) -> List[Tuple[str, str, str]]:
        """Get list of packages in workspace.

        Returns:
            List of (package_name, package_path, package_type) tuples.
        """
        result = subprocess.run(
            ["colcon", "list"],
            cwd=self.workspace_path,
            capture_output=True,
            text=True,
            check=True
        )

        packages = []
        for line in result.stdout.strip().split("\n"):
            if line:
                parts = line.split("\t")
                if len(parts) >= 3:
                    packages.append((parts[0], parts[1], parts[2]))

        return packages
