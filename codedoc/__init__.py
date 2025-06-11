"""
🚀 CodeDoc AI - Smart Documentation Generator

The future of code documentation is here!
"""

__version__ = "0.1.0"
__author__ = "CodeDoc AI Team"
__email__ = "hello@codedoc-ai.com"

from .core import DocumentationGenerator
from .parser import CodeParser
from .ai import AIExampleGenerator

__all__ = ["DocumentationGenerator", "CodeParser", "AIExampleGenerator"] 