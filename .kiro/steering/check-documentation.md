---
inclusion: always
---

# Documentation and Context Checking

When creating or updating Python or CDK (TypeScript) code:

1. **Check AWS documentation** using available MCP tools before implementing AWS services
2. **Use Context7** to look up library-specific documentation for:
   - Python libraries (FastAPI, SQLAlchemy, Pydantic, etc.)
   - AWS CDK constructs and patterns
   - TypeScript/Node.js packages

3. **Search for best practices** and current patterns rather than relying solely on general knowledge
4. **Verify API signatures** and parameter requirements from official docs
5. **Check for recent updates** to libraries and services that might affect implementation

This ensures code follows current best practices and uses correct, up-to-date APIs.
