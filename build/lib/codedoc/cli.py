"""
CLI Interface for CodeDoc AI 🚀

Command-line interface for generating AI-powered documentation.
"""

import click
import os
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from .core import DocumentationGenerator
from . import __version__


console = Console()


@click.group()
@click.version_option(version=__version__, message="🚀 CodeDoc AI v%(version)s")
def cli():
    """🚀 CodeDoc AI - Smart Documentation Generator
    
    Generate beautiful, AI-powered documentation for your Python code!
    """
    pass


@cli.command()
@click.argument('source_path', type=click.Path(exists=True))
@click.option('--output', '-o', default='./docs', help='Output directory for documentation')
@click.option('--format', '-f', type=click.Choice(['html', 'markdown', 'both']), 
              default='html', help='Output format (html, markdown, or both)')
@click.option('--api-key', '-k', help='OpenAI API key (or set OPENAI_API_KEY env var)')
@click.option('--no-ai', is_flag=True, help='Generate basic documentation without AI features')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
def generate(source_path, output, format, api_key, no_ai, verbose):
    """Generate AI-powered documentation for Python code.
    
    SOURCE_PATH: Path to Python file or directory to document
    """
    
    # Display header
    console.print(Panel.fit(
        Text("🚀 CodeDoc AI - Smart Documentation Generator", style="bold blue"),
        border_style="blue"
    ))
    
    # Validate API key if AI is enabled
    if not no_ai:
        openai_key = api_key or os.getenv('OPENAI_API_KEY')
        if not openai_key:
            console.print("⚠️  No OpenAI API key found!", style="yellow")
            console.print("Set OPENAI_API_KEY environment variable or use --api-key option", style="yellow")
            console.print("Continuing without AI features (use --no-ai to suppress this warning)", style="yellow")
            no_ai = True
    
    try:
        # Initialize generator
        generator = DocumentationGenerator(
            openai_api_key=api_key,
            use_ai=not no_ai
        )
        
        # Display configuration
        config_text = f"""
📁 Source: {source_path}
📄 Output: {output}
🎨 Format: {format}
🤖 AI Enhanced: {'Yes' if not no_ai else 'No'}
        """
        console.print(Panel(config_text.strip(), title="Configuration", border_style="green"))
        
        # Generate documentation
        result = generator.generate_documentation(
            source_path=source_path,
            output_path=output,
            format_type=format
        )
        
        if result['status'] == 'success':
            # Display success summary
            summary_text = f"""
✅ Documentation generated successfully!

📊 Summary:
• Functions documented: {result['functions_documented']}
• Classes documented: {result['classes_documented']}
• AI enhanced: {'Yes' if result['ai_enhanced'] else 'No'}
• Output files: {len(result['output_files'])}

📁 Files created:
{chr(10).join(['• ' + Path(f).name for f in result['output_files']])}

🌐 Open documentation:
• HTML: {Path(output) / 'documentation.html'}
• View in browser: file://{Path(output).absolute() / 'documentation.html'}
            """
            
            console.print(Panel(summary_text.strip(), title="🎉 Success!", border_style="green"))
            
            if verbose:
                console.print("\n📄 Full result:", style="dim")
                console.print(result)
        
        else:
            console.print(f"❌ Error: {result.get('message', 'Unknown error')}", style="red")
            
    except Exception as e:
        console.print(f"💥 Fatal error: {str(e)}", style="bold red")
        if verbose:
            import traceback
            console.print("\n🔍 Full traceback:", style="dim")
            console.print(traceback.format_exc())
        raise click.Abort()


@cli.command()
@click.argument('source_path', type=click.Path(exists=True))
def parse(source_path):
    """Parse Python code and show structure (no AI, no output files).
    
    SOURCE_PATH: Path to Python file or directory to analyze
    """
    
    console.print(Panel.fit(
        Text("🔍 CodeDoc AI - Code Parser", style="bold cyan"),
        border_style="cyan"
    ))
    
    try:
        from .parser import CodeParser
        
        parser = CodeParser()
        
        if Path(source_path).is_file():
            result = parser.parse_file(source_path)
        else:
            # For directories, we'd need to implement directory parsing in parser
            console.print("❌ Directory parsing not implemented in parse command", style="red")
            console.print("Use 'codedoc generate' instead", style="yellow")
            return
        
        console.print(f"\n📊 Analysis Results for: {source_path}")
        console.print(f"Functions found: {len(result['functions'])}")
        console.print(f"Classes found: {len(result['classes'])}")
        
        if result['functions']:
            console.print("\n📋 Functions:", style="bold blue")
            for func in result['functions']:
                console.print(f"  • {func.name}({', '.join(func.args)})")
                if func.docstring:
                    console.print(f"    📝 {func.docstring[:100]}...", style="dim")
        
        if result['classes']:
            console.print("\n🏗️ Classes:", style="bold green")
            for cls in result['classes']:
                console.print(f"  • {cls.name}")
                if cls.docstring:
                    console.print(f"    📝 {cls.docstring[:100]}...", style="dim")
                if cls.methods:
                    console.print(f"    🔧 Methods: {', '.join([m.name for m in cls.methods])}", style="dim")
        
        if not result['functions'] and not result['classes']:
            console.print("⚠️  No functions or classes found to analyze", style="yellow")
    
    except Exception as e:
        console.print(f"❌ Error parsing code: {str(e)}", style="red")
        raise click.Abort()


@cli.command()
def demo():
    """Create a demo Python file and generate documentation for it."""
    
    console.print(Panel.fit(
        Text("🎭 CodeDoc AI - Demo Mode", style="bold magenta"),
        border_style="magenta"
    ))
    
    # Create demo file
    demo_code = '''"""
Demo Python Module for CodeDoc AI 🚀

This module contains sample functions and classes to demonstrate
the power of CodeDoc AI documentation generation.
"""

import math
from typing import List, Optional


def calculate_discount(price: float, discount_percent: float) -> float:
    """Calculate the discount amount for a given price and percentage.
    
    Args:
        price: The original price
        discount_percent: Discount percentage (0-100)
        
    Returns:
        The discount amount
    """
    if discount_percent < 0 or discount_percent > 100:
        raise ValueError("Discount percentage must be between 0 and 100")
    
    return price * (discount_percent / 100)


def fibonacci_sequence(n: int) -> List[int]:
    """Generate Fibonacci sequence up to n numbers."""
    if n <= 0:
        return []
    elif n == 1:
        return [0]
    elif n == 2:
        return [0, 1]
    
    fib = [0, 1]
    for i in range(2, n):
        fib.append(fib[i-1] + fib[i-2])
    
    return fib


class Calculator:
    """A simple calculator class with basic mathematical operations."""
    
    def __init__(self, precision: int = 2):
        """Initialize calculator with specified precision."""
        self.precision = precision
        self.history = []
    
    def add(self, a: float, b: float) -> float:
        """Add two numbers."""
        result = round(a + b, self.precision)
        self.history.append(f"{a} + {b} = {result}")
        return result
    
    def multiply(self, a: float, b: float) -> float:
        """Multiply two numbers."""
        result = round(a * b, self.precision)
        self.history.append(f"{a} × {b} = {result}")
        return result
    
    def power(self, base: float, exponent: float) -> float:
        """Calculate base raised to the power of exponent."""
        result = round(math.pow(base, exponent), self.precision)
        self.history.append(f"{base}^{exponent} = {result}")
        return result
    
    def get_history(self) -> List[str]:
        """Get calculation history."""
        return self.history.copy()
    
    def clear_history(self) -> None:
        """Clear calculation history."""
        self.history.clear()


class DataProcessor:
    """Process and analyze data with various statistical operations."""
    
    def __init__(self):
        self.data = []
    
    def add_data(self, values: List[float]) -> None:
        """Add new data points."""
        self.data.extend(values)
    
    def calculate_mean(self) -> Optional[float]:
        """Calculate the arithmetic mean of the data."""
        if not self.data:
            return None
        return sum(self.data) / len(self.data)
    
    def calculate_median(self) -> Optional[float]:
        """Calculate the median of the data."""
        if not self.data:
            return None
        
        sorted_data = sorted(self.data)
        n = len(sorted_data)
        
        if n % 2 == 0:
            return (sorted_data[n//2 - 1] + sorted_data[n//2]) / 2
        else:
            return sorted_data[n//2]
    
    def get_summary(self) -> dict:
        """Get a summary of the data statistics."""
        if not self.data:
            return {"error": "No data available"}
        
        return {
            "count": len(self.data),
            "mean": self.calculate_mean(),
            "median": self.calculate_median(),
            "min": min(self.data),
            "max": max(self.data),
            "range": max(self.data) - min(self.data)
        }
'''
    
    # Write demo file
    demo_file = Path("demo_module.py")
    demo_file.write_text(demo_code)
    
    console.print(f"📝 Created demo file: {demo_file}")
    
    # Generate documentation
    console.print("🚀 Generating documentation...\n")
    
    try:
        generator = DocumentationGenerator(use_ai=False)  # Demo without AI to avoid API key requirement
        
        result = generator.generate_documentation(
            source_path=str(demo_file),
            output_path="./demo_docs",
            format_type="both"
        )
        
        if result['status'] == 'success':
            console.print(Panel(f"""
🎉 Demo documentation generated successfully!

📁 Files created:
• demo_docs/documentation.html
• demo_docs/documentation.md  
• demo_docs/style.css
• demo_docs/documentation_data.json

🌐 Open the HTML file in your browser to see the results!
file://{Path('./demo_docs/documentation.html').absolute()}

🧹 Clean up: Delete demo_module.py and demo_docs/ when done.
            """.strip(), title="Demo Complete!", border_style="green"))
        
    except Exception as e:
        console.print(f"❌ Demo failed: {str(e)}", style="red")
        # Clean up demo file on error
        if demo_file.exists():
            demo_file.unlink()


def main():
    """Main entry point for the CLI."""
    cli()


if __name__ == '__main__':
    main() 