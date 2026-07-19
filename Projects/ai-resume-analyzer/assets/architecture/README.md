# Architecture Diagram

This folder contains the official Version 1.0 RC architecture artwork for NEXUS AI Resume Intelligence Platform.

## Files

- `architecture.svg` — canonical editable vector, 1920×1080 (16:9)
- `architecture.png` — high-resolution raster export for presentations and platforms without SVG support

## Flow represented

User → Upload Resume PDF → PDF Reader → Text Extraction → Resume Parser → Skill Matcher → ATS Engine → Resume Intelligence Engine → Analytics Engine → Dashboard → HTML/TXT reports.

The diagram describes logical responsibilities. “Resume Parser” and “Analytics Engine” represent processing stages composed from the existing modular code; they do not imply additional network services or separate deployed applications.

## Usage

Prefer the SVG in GitHub Markdown and documentation. Use the PNG in presentations or portfolio systems that do not render SVG reliably. Preserve the 16:9 aspect ratio and do not recolor individual boxes in ways that reduce contrast.
