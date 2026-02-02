#!/usr/bin/env python3
"""
Convert all PNG plots to SVG using cairosvg or PIL.
Run: python convert_png_to_svg.py
"""

import subprocess
from pathlib import Path

PLOTS_DIR = Path(__file__).parent / "plots"

def convert_with_inkscape():
    """Use Inkscape for high-quality conversion (if installed)."""
    png_files = list(PLOTS_DIR.rglob("*.png"))
    print(f"Found {len(png_files)} PNG files to convert")
    
    for png_path in png_files:
        svg_path = png_path.with_suffix('.svg')
        print(f"Converting: {png_path.name} -> {svg_path.name}")
        try:
            subprocess.run([
                'inkscape', str(png_path),
                '--export-filename', str(svg_path)
            ], check=True, capture_output=True)
        except FileNotFoundError:
            print("Inkscape not found. Install with: brew install inkscape")
            return False
        except subprocess.CalledProcessError as e:
            print(f"Error converting {png_path.name}: {e}")
    return True

def convert_with_cairosvg():
    """Alternative: use cairosvg (pip install cairosvg)."""
    try:
        import cairosvg
        from PIL import Image
        import io
    except ImportError:
        print("Install dependencies: pip install cairosvg pillow")
        return False
    
    png_files = list(PLOTS_DIR.rglob("*.png"))
    print(f"Found {len(png_files)} PNG files")
    
    for png_path in png_files:
        svg_path = png_path.with_suffix('.svg')
        # Note: cairosvg converts SVG to PNG, not the other way around
        # For PNG to SVG, we need a different approach
        print(f"Note: Direct PNG→SVG conversion produces low-quality results.")
        print("Recommendation: Re-run notebooks with EXPORT_FORMAT='svg'")
    return False

if __name__ == "__main__":
    print("=== PNG to SVG Converter ===\n")
    
    # Try Inkscape first
    if not convert_with_inkscape():
        print("\n--- Alternative ---")
        print("For best results, update the notebooks to use save_plot() from plot_config.py")
        print("Then re-run the pipeline to generate native SVG files.")
