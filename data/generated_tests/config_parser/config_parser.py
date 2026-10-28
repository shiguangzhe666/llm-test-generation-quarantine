"""
Config parser module - a realistic Python utility for testing.
Parses INI-style configuration with section inheritance and variable interpolation.
"""
import re
from collections import OrderedDict


class ConfigParser:
    """Simple configuration parser with section support."""
    
    def __init__(self, defaults=None):
        self._sections = OrderedDict()
        self._defaults = dict(defaults) if defaults else {}
    
    def read_string(self, text):
        """Parse configuration from a string."""
        current_section = None
        
        for lineno, line in enumerate(text.splitlines(), 1):
            line = line.strip()
            
            # Skip empty lines and comments
            if not line or line.startswith('#') or line.startswith(';'):
                continue
            
            # Section header
            match = re.match(r'\[([^\]]+)\]', line)
            if match:
                section_name = match.group(1).strip()
                if section_name not in self._sections:
                    self._sections[section_name] = OrderedDict()
                current_section = section_name
                continue
            
            # Key = Value
            if '=' in line:
                key, _, value = line.partition('=')
                key = key.strip()
                value = value.strip()
                
                # Remove quotes
                if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
                    value = value[1:-1]
                
                if current_section is None:
                    self._defaults[key] = value
                else:
                    self._sections[current_section][key] = value
            else:
                raise ValueError(
                    "Invalid line {}: {}".format(lineno, line)
                )
    
    def sections(self):
        """Return list of section names."""
        return list(self._sections.keys())
    
    def has_section(self, section):
        """Check if section exists."""
        return section in self._sections
    
    def get(self, section, key, fallback=None):
        """Get a value from a section, with fallback to defaults."""
        if section in self._sections:
            if key in self._sections[section]:
                return self._interpolate(
                    self._sections[section][key], section
                )
        if key in self._defaults:
            return self._interpolate(self._defaults[key], section)
        if fallback is not None:
            return fallback
        raise KeyError("No option '{}' in section '{}'".format(key, section))
    
    def getint(self, section, key, fallback=None):
        """Get an integer value."""
        value = self.get(section, key, fallback=fallback)
        if value is fallback:
            return fallback
        try:
            return int(value)
        except (ValueError, TypeError):
            raise ValueError(
                "Cannot convert '{}' to int for [{}/{}]".format(value, section, key)
            )
    
    def getboolean(self, section, key, fallback=None):
        """Get a boolean value."""
        value = self.get(section, key, fallback=fallback)
        if value is fallback:
            return fallback
        if isinstance(value, bool):
            return value
        if value.lower() in ('true', 'yes', '1', 'on'):
            return True
        if value.lower() in ('false', 'no', '0', 'off'):
            return False
        raise ValueError(
            "Cannot convert '{}' to bool for [{}/{}]".format(value, section, key)
        )
    
    def items(self, section):
        """Return key-value pairs for a section (including defaults)."""
        result = dict(self._defaults)
        if section in self._sections:
            result.update(self._sections[section])
        return list(result.items())
    
    def _interpolate(self, value, section):
        """Resolve ${section:key} or ${key} variable references."""
        if not isinstance(value, str):
            return value
        
        def replacer(match):
            ref = match.group(1)
            if ':' in ref:
                ref_section, ref_key = ref.split(':', 1)
                return self.get(ref_section, ref_key, fallback=match.group(0))
            else:
                # Look in current section first, then defaults
                if section in self._sections and ref in self._sections[section]:
                    return self._sections[section][ref]
                return self._defaults.get(ref, match.group(0))
        
        return re.sub(r'\$\{([^}]+)\}', replacer, value)
    
    def to_dict(self):
        """Export all configuration as nested dictionary."""
        result = {}
        for section in self._sections:
            result[section] = dict(self._sections[section])
        return result
