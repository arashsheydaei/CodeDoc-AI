"""
FastAPI Web Interface for CodeDoc AI 🚀

Beautiful, modern web interface for generating AI-powered documentation.
Upload code, get instant documentation with live preview!
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
import tempfile
import shutil
from pathlib import Path
from typing import Optional, List
import asyncio
import json
from datetime import datetime

# Import our core modules
import sys
sys.path.append('..')
from codedoc.core import DocumentationGenerator
from codedoc.parser import CodeParser


# Initialize FastAPI app
app = FastAPI(
    title="CodeDoc AI Web Interface",
    description="🚀 AI-Powered Documentation Generator - Upload code, get beautiful docs!",
    version="1.0.0"
)

# Setup static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Global documentation generator
doc_generator = DocumentationGenerator(use_ai=False)  # Start without AI for now


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Home page with upload interface."""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@app.post("/api/upload")
async def upload_file(
    file: UploadFile = File(...),
    use_ai: bool = Form(False),
    output_format: str = Form("html"),
    include_private: bool = Form(False)
):
    """Upload and process a code file."""
    
    # Validate file type
    if not file.filename.endswith(('.py', '.js', '.ts')):
        raise HTTPException(
            status_code=400, 
            detail="Unsupported file type. Please upload .py, .js, or .ts files."
        )
    
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as tmp_file:
            shutil.copyfileobj(file.file, tmp_file)
            tmp_path = tmp_file.name
        
        # Generate documentation
        result = await generate_documentation_async(
            tmp_path, 
            file.filename,
            use_ai=use_ai,
            output_format=output_format,
            include_private=include_private
        )
        
        # Clean up temp file
        os.unlink(tmp_path)
        
        return JSONResponse({
            "success": True,
            "filename": file.filename,
            "documentation": result["content"],
            "stats": result["stats"],
            "format": output_format
        })
        
    except Exception as e:
        # Clean up temp file if it exists
        if 'tmp_path' in locals():
            try:
                os.unlink(tmp_path)
            except:
                pass
        
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")


@app.post("/api/analyze")
async def analyze_code(
    code: str = Form(...),
    language: str = Form("python"),
    filename: str = Form("code.py")
):
    """Analyze code directly from text input."""
    
    try:
        # Save code to temporary file
        file_extension = {
            "python": ".py",
            "javascript": ".js", 
            "typescript": ".ts"
        }.get(language, ".py")
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix=file_extension) as tmp_file:
            tmp_file.write(code)
            tmp_path = tmp_file.name
        
        # Analyze the code
        if language == "python":
            parser = CodeParser()
            result = parser.parse_file(tmp_path)
            
            # Clean up temp file
            os.unlink(tmp_path)
            
            return JSONResponse({
                "success": True,
                "language": language,
                "stats": {
                    "functions": len(result["functions"]),
                    "classes": len(result["classes"]),
                    "total_items": result["total_items"]
                },
                "functions": [
                    {
                        "name": func.name,
                        "params": func.args,
                        "docstring": func.docstring,
                        "line_number": func.line_number
                    }
                    for func in result["functions"]
                ],
                "classes": [
                    {
                        "name": cls.name,
                        "docstring": cls.docstring,
                        "methods": len(cls.methods),
                        "line_number": cls.line_number
                    }
                    for cls in result["classes"]
                ]
            })
        else:
            # For JS/TS, return basic analysis for now
            lines = code.split('\n')
            functions = [line.strip() for line in lines if 'function ' in line or '=>' in line]
            classes = [line.strip() for line in lines if 'class ' in line]
            
            os.unlink(tmp_path)
            
            return JSONResponse({
                "success": True,
                "language": language,
                "stats": {
                    "functions": len(functions),
                    "classes": len(classes),
                    "total_items": len(functions) + len(classes)
                },
                "functions": functions[:5],  # Show first 5
                "classes": classes[:5]
            })
            
    except Exception as e:
        # Clean up temp file if it exists
        if 'tmp_path' in locals():
            try:
                os.unlink(tmp_path)
            except:
                pass
        
        raise HTTPException(status_code=500, detail=f"Error analyzing code: {str(e)}")


@app.get("/demo")
async def demo_page(request: Request):
    """Demo page with sample code."""
    demo_code = '''def calculate_discount(price: float, discount_percent: float) -> float:
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
'''
    
    return templates.TemplateResponse("demo.html", {
        "request": request,
        "demo_code": demo_code
    })


@app.get("/api/stats")
async def get_stats():
    """Get system statistics."""
    return JSONResponse({
        "total_processed": 0,  # Would track this in real app
        "supported_languages": ["Python", "JavaScript", "TypeScript"],
        "features": [
            "AI-powered enhancement",
            "Multiple output formats",
            "Beautiful HTML output",
            "Markdown export",
            "Live preview",
            "Syntax highlighting"
        ],
        "version": "1.0.0"
    })


async def generate_documentation_async(
    file_path: str, 
    filename: str,
    use_ai: bool = False,
    output_format: str = "html",
    include_private: bool = False
) -> dict:
    """Generate documentation asynchronously."""
    
    try:
        # Initialize generator with appropriate settings
        generator = DocumentationGenerator(use_ai=use_ai)
        
        # Generate documentation
        content = generator.generate_documentation(
            source_path=file_path,
            output_format=output_format,
            include_private=include_private
        )
        
        # Get basic stats
        if file_path.endswith('.py'):
            parser = CodeParser()
            result = parser.parse_file(file_path)
            stats = {
                "functions": len(result["functions"]),
                "classes": len(result["classes"]),
                "total_items": result["total_items"],
                "language": "Python"
            }
        else:
            # Basic stats for other languages
            with open(file_path, 'r') as f:
                lines = f.readlines()
            stats = {
                "functions": len([l for l in lines if 'function' in l or '=>' in l]),
                "classes": len([l for l in lines if 'class ' in l]),
                "total_items": 0,
                "language": "JavaScript/TypeScript"
            }
        
        return {
            "content": content,
            "stats": stats
        }
        
    except Exception as e:
        raise Exception(f"Documentation generation failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting CodeDoc AI Web Interface...")
    print("📱 Open http://localhost:8000 in your browser")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True) 