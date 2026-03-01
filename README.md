# ccolcon

Interactive terminal tool for compiling ROS2 workspaces, similar to ccmake.

## Installation

```bash
pip install -e .
```

## Usage

```bash
cd /path/to/your/ros2/workspace
ccolcon build
```

## Features

- Interactive terminal UI (TUI)
- Configure build options (symlink-install, install-base)
- Select packages to build
- Execute colcon with selected options
- Automatic build logging

## Requirements

- Python 3.8+
- textual >= 8.0.0
- colcon (ROS2 build tool)
