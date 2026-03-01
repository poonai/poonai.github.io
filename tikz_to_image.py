#!/usr/bin/env python3
"""
TikZ to Image Generator
Place your TikZ code in the TIKZ_CODE variable below and run this script.

Requirements:
- pdflatex (TeX Live, MiKTeX, or MacTeX)
- pdftoppm (poppler-utils) OR convert (ImageMagick) for PNG/JPG
- pdf2svg for SVG (optional)

Install on Ubuntu/Debian:
  sudo apt install texlive-full poppler-utils imagemagick pdf2svg

Install on macOS:
  brew install mactex poppler imagemagick pdf2svg
"""

# Place your TikZ code here
TIKZ_CODE = r"""
\begin{tikzpicture}
\begin{axis}[axis lines=middle, axis on top, xmin=-10, xmax=10, ymin=-10, ymax=15, xlabel={$x_0$}, ylabel={$x_1$}]
\fill[gray!30] (axis cs:0,0) -- (axis cs:10,5) -- (axis cs:10,14.28) -- cycle;
\addplot[domain=0:10, thick] {x/.7} node[pos=0.5, below, sloped, font=\small] {$0.7x_1 < x_0$};
\addplot[domain=0:10, dashed] {x};
\addplot[domain=0:10, thick] {x/2} node[pos=0.7, above, sloped, font=\small] {$2x_1 > x_0$};
\end{axis}
\end{tikzpicture}
"""

# Output settings
OUTPUT_FILENAME = "tikz_output"  # without extension
OUTPUT_FORMAT = "png"  # Options: png, svg, pdf, jpg

import os
import subprocess
import tempfile
import shutil


def generate_tikz_image(tikz_code, output_filename, output_format):
    """Generate an image from TikZ code."""
    temp_dir = tempfile.mkdtemp()

    try:
        latex_content = (
            r"""
\documentclass[border=10pt]{standalone}
\usepackage{tikz}
\usepackage{amsmath}
\usetikzlibrary{arrows.meta, positioning}
\usepackage{pgfplots}
\pgfplotsset{compat=1.18}
\begin{document}
"""
            + tikz_code
            + r"""
\end{document}
"""
        )

        tex_file = os.path.join(temp_dir, f"{output_filename}.tex")
        with open(tex_file, "w") as f:
            f.write(latex_content)

        print("Compiling TikZ code...")
        result = subprocess.run(
            [
                "pdflatex",
                "-interaction=nonstopmode",
                "-output-directory",
                temp_dir,
                tex_file,
            ],
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            print("LaTeX compilation failed:")
            print("STDERR:", result.stderr)
            print("STDOUT:", result.stdout[-1500:] if result.stdout else "No stdout")
            return False

        pdf_file = os.path.join(temp_dir, f"{output_filename}.pdf")

        if output_format == "pdf":
            output_path = f"{output_filename}.pdf"
            shutil.copy(pdf_file, output_path)
            print(f"✓ Generated {output_path}")

        elif output_format in ["png", "jpg"]:
            output_path = f"{output_filename}.{output_format}"

            if shutil.which("pdftoppm"):
                if output_format == "png":
                    subprocess.run(
                        ["pdftoppm", "-png", "-singlefile", pdf_file, output_filename]
                    )
                else:
                    subprocess.run(
                        ["pdftoppm", "-png", "-singlefile", pdf_file, output_filename]
                    )
                    try:
                        from PIL import Image

                        img = Image.open(f"{output_filename}.png")
                        img.save(output_path, "JPEG")
                        os.remove(f"{output_filename}.png")
                    except ImportError:
                        print("Warning: PIL not installed, using PNG instead")
                        output_path = f"{output_filename}.png"
                print(f"✓ Generated {output_path}")

            elif shutil.which("convert"):
                subprocess.run(["convert", "-density", "300", pdf_file, output_path])
                print(f"✓ Generated {output_path}")

            else:
                print(
                    "Error: Neither pdftoppm nor convert found. Install poppler-utils or imagemagick."
                )
                return False

        elif output_format == "svg":
            if shutil.which("pdf2svg"):
                svg_path = f"{output_filename}.svg"
                subprocess.run(["pdf2svg", pdf_file, svg_path])
                print(f"✓ Generated {svg_path}")
            else:
                print("Error: pdf2svg not found.")
                return False

        return True

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    print("TikZ to Image Generator")
    print("=" * 40)

    deps_ok = True
    if not shutil.which("pdflatex"):
        print("✗ pdflatex not found. Install a TeX distribution.")
        deps_ok = False

    if not deps_ok:
        print("\nInstall required dependencies and try again.")
        exit(1)

    success = generate_tikz_image(TIKZ_CODE, OUTPUT_FILENAME, OUTPUT_FORMAT)

    if success:
        print(f"\nDone! Image saved as: {OUTPUT_FILENAME}.{OUTPUT_FORMAT}")
    else:
        print("\nFailed to generate image.")
        exit(1)
