#!/bin/bash
# Generate API documentation using pdoc

echo "Generating API documentation..."
pdoc app -o docs

if [ $? -eq 0 ]; then
    echo "✓ Documentation generated successfully in backend/docs/"
    echo "  Open backend/docs/index.html in your browser to view"
else
    echo "✗ Documentation generation failed"
    exit 1
fi
