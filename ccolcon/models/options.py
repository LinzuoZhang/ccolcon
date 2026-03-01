"""Build option definitions."""

from dataclasses import dataclass


@dataclass
class BuildOption:
    """A build option definition."""

    name: str
    opt_type: str  # "bool", "string", "int", "float"
    default_value: str
    description: str
    current_value: str = ""  # Optional current value for display
    def __init__(self, name, opt_type, default_value, description):
        self.name = name
        self.opt_type = opt_type
        self.default_value = default_value
        self.current_value = default_value
        self.description = description
        
    @property
    def type_name(self) -> str:
        """Get the type name for display."""
        return self.opt_type.capitalize()

    @property
    def type_display(self) -> str:
        """Get the type for display (e.g., Bool, Int, Float)."""
        mapping = {
            "bool": "Bool",
            "string": "String",
            "int": "Int",
            "float": "Float",
        }
        return mapping.get(self.opt_type, self.opt_type)
