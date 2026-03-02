import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict, Optional
from ccolcon.models.options import BuildOption

class OptionRegistry:
    """管理所有可用的构建选项及其状态。"""
    
    def __init__(self):
        # 初始化默认选项列表
        self._options: Dict[str, BuildOption] = {
            opt.name: opt for opt in [
                BuildOption("symlink-install", "bool", "true", "Use symlink install"),
                BuildOption("install-base", "string", "install", "Installation base directory"),
                BuildOption("merge-install", "bool", "false", "Merge install space"),
                BuildOption("continue-on-error", "bool", "false", "Continue building on error"),
                BuildOption("parallel-workers", "int", "4", "Number of parallel workers"),
            ]
        }

    def get_all(self) -> List[BuildOption]:
        return list(self._options.values())

    def update(self, name: str, value: str):
        if name not in self._options:
            return
        
        opt = self._options[name]
        if opt.opt_type == "bool":
            # 统一转换为字符串形式的 "True"/"False"
            normalized_value = str(value).lower() in ("true", "1", "yes", "on")
            opt.current_value = str(normalized_value).lower()
        else:
            opt.current_value = str(value)

    def get_value(self, name: str) -> str:
        opt = self._options.get(name)
        if not opt:
            return ""
        return opt.current_value if opt.current_value is not None else opt.default_value

    def reset_to_defaults(self):
        for opt in self._options.values():
            opt.current_value = None


@dataclass
class BuildConfig:
    """colcon 构建配置模型。"""
    
    selected_packages: List[str] = field(default_factory=list)
    workspace_path: str = "."
    # 将选项管理封装在内部
    options: OptionRegistry = field(default_factory=OptionRegistry)

    def get_all_options(self) -> List[dict]:
        """供 UI 或外部读取的序列化列表。"""
        return [
            {
                "name": opt.name,
                "value": self.options.get_value(opt.name),
                "type": opt.opt_type,
                "default_value": opt.default_value,
            }
            for opt in self.options.get_all()
        ]

    def update_option(self, name: str, value: str) -> None:
        self.options.update(name, value)

    def get_colcon_args(self) -> List[str]:
        """生成 colcon 命令行参数。"""
        args = []
        
        for opt in self.options.get_all():
            val = self.options.get_value(opt.name)
            
            if opt.opt_type == "bool":
                if val == "true":
                    args.append(f"--{opt.name}")
            elif opt.opt_type in ("string", "int", "float"):
                if val and val != opt.default_value:
                    args.extend([f"--{opt.name}", val])

        if self.selected_packages:
            args.extend(["--packages-select"] + self.selected_packages)
        
        return args

    def _get_config_file_path(self) -> Path:
        return Path(self.workspace_path) / ".ccolcon"

    def save_to_file(self) -> None:
        config_data = {
            "version": "1.1",
            "options": {opt.name: self.options.get_value(opt.name) for opt in self.options.get_all()},
            "selected_packages": self.selected_packages
        }
        
        config_file = self._get_config_file_path()
        config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(config_file, "w") as f:
            json.dump(config_data, f, indent=2)

    def load_from_file(self) -> None:
        config_file = self._get_config_file_path()
        if not config_file.exists():
            return

        try:
            with open(config_file, "r") as f:
                data = json.load(f)
            
            # 加载选项
            for name, val in data.get("options", {}).items():
                self.options.update(name, str(val))
            
            # 加载包
            self.selected_packages = data.get("selected_packages", [])
        except Exception:
            pass # 实际生产中建议记录日志