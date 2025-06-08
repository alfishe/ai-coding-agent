import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Any

from lsprotocol.types import (
    Position,
    Range,
    Location,
    SymbolKind,
    SymbolInformation,
    DocumentSymbol,
    WorkspaceSymbolParams,
    DocumentSymbolParams,
    ReferenceParams
)
from pygls.protocol import LanguageServerProtocol
from pygls.server import LanguageServer

from .base import BaseTool, ToolParameter, ToolResult


class SemanticSearchTool(BaseTool):
    """Tool for performing semantic code search using LSP."""
    
    name = "semantic_search"
    description = "Search for code using semantic queries via LSP"
    parameters = [
        ToolParameter(
            name="query",
            description="Semantic search query",
            required=True,
            type="string"
        ),
        ToolParameter(
            name="workspace_path",
            description="Path to the workspace root",
            required=True,
            type="string"
        ),
        ToolParameter(
            name="language",
            description="Programming language to search in",
            required=True,
            type="string"
        ),
        ToolParameter(
            name="symbol_kind",
            description="Type of symbols to search for (function, class, method, etc.)",
            required=False,
            type="string"
        )
    ]
    
    def __init__(self):
        super().__init__()
        self._servers: Dict[str, LanguageServer] = {}
    
    async def _get_server(self, language: str) -> LanguageServer:
        """Get or create an LSP server for the given language."""
        if language not in self._servers:
            # Initialize LSP server for the language
            # This is a placeholder - you'll need to implement proper server initialization
            # based on the language server you want to use
            server = LanguageServer()
            self._servers[language] = server
        return self._servers[language]
    
    async def execute(
        self,
        query: str,
        workspace_path: str,
        language: str,
        symbol_kind: Optional[str] = None
    ) -> ToolResult:
        try:
            server = await self._get_server(language)
            
            # Convert symbol kind to LSP symbol kind if provided
            kind = None
            if symbol_kind:
                kind = getattr(SymbolKind, symbol_kind.upper(), None)
            
            # Perform workspace symbol search
            params = WorkspaceSymbolParams(query=query)
            symbols = await server.workspace_symbol(params)
            
            # Filter by symbol kind if specified
            if kind is not None:
                symbols = [s for s in symbols if s.kind == kind]
            
            # Convert symbols to a more readable format
            results = []
            for symbol in symbols:
                result = {
                    "name": symbol.name,
                    "kind": SymbolKind(symbol.kind).name,
                    "location": {
                        "uri": symbol.location.uri,
                        "range": {
                            "start": {
                                "line": symbol.location.range.start.line,
                                "character": symbol.location.range.start.character
                            },
                            "end": {
                                "line": symbol.location.range.end.line,
                                "character": symbol.location.range.end.character
                            }
                        }
                    }
                }
                results.append(result)
            
            return ToolResult(success=True, data=results)
        except Exception as e:
            return ToolResult(success=False, error=str(e))


class SymbolInfoTool(BaseTool):
    """Tool for getting detailed information about code symbols using LSP."""
    
    name = "symbol_info"
    description = "Get detailed information about code symbols via LSP"
    parameters = [
        ToolParameter(
            name="file_path",
            description="Path to the file",
            required=True,
            type="string"
        ),
        ToolParameter(
            name="position",
            description="Position in the file (line, character)",
            required=True,
            type="object"
        ),
        ToolParameter(
            name="language",
            description="Programming language of the file",
            required=True,
            type="string"
        )
    ]
    
    def __init__(self):
        super().__init__()
        self._servers: Dict[str, LanguageServer] = {}
    
    async def _get_server(self, language: str) -> LanguageServer:
        """Get or create an LSP server for the given language."""
        if language not in self._servers:
            server = LanguageServer()
            self._servers[language] = server
        return self._servers[language]
    
    async def execute(
        self,
        file_path: str,
        position: Dict[str, int],
        language: str
    ) -> ToolResult:
        try:
            server = await self._get_server(language)
            
            # Convert file path to URI
            uri = Path(file_path).resolve().as_uri()
            
            # Create position object
            pos = Position(
                line=position["line"],
                character=position["character"]
            )
            
            # Get hover information
            hover = await server.hover(uri, pos)
            
            # Get definition
            definition = await server.definition(uri, pos)
            
            # Get references
            references = await server.references(
                ReferenceParams(
                    text_document=uri,
                    position=pos,
                    context={"include_declaration": True}
                )
            )
            
            # Get document symbols
            symbols = await server.document_symbol(
                DocumentSymbolParams(text_document=uri)
            )
            
            result = {
                "hover": hover.contents if hover else None,
                "definition": definition[0].dict() if definition else None,
                "references": [r.dict() for r in references] if references else [],
                "symbols": [s.dict() for s in symbols] if symbols else []
            }
            
            return ToolResult(success=True, data=result)
        except Exception as e:
            return ToolResult(success=False, error=str(e))


class CodeNavigationTool(BaseTool):
    """Tool for navigating code using LSP."""
    
    name = "code_navigation"
    description = "Navigate code using LSP features"
    parameters = [
        ToolParameter(
            name="file_path",
            description="Path to the file",
            required=True,
            type="string"
        ),
        ToolParameter(
            name="position",
            description="Position in the file (line, character)",
            required=True,
            type="object"
        ),
        ToolParameter(
            name="language",
            description="Programming language of the file",
            required=True,
            type="string"
        ),
        ToolParameter(
            name="action",
            description="Navigation action to perform (definition, references, etc.)",
            required=True,
            type="string"
        )
    ]
    
    def __init__(self):
        super().__init__()
        self._servers: Dict[str, LanguageServer] = {}
    
    async def _get_server(self, language: str) -> LanguageServer:
        """Get or create an LSP server for the given language."""
        if language not in self._servers:
            server = LanguageServer()
            self._servers[language] = server
        return self._servers[language]
    
    async def execute(
        self,
        file_path: str,
        position: Dict[str, int],
        language: str,
        action: str
    ) -> ToolResult:
        try:
            server = await self._get_server(language)
            
            # Convert file path to URI
            uri = Path(file_path).resolve().as_uri()
            
            # Create position object
            pos = Position(
                line=position["line"],
                character=position["character"]
            )
            
            # Perform the requested navigation action
            if action == "definition":
                result = await server.definition(uri, pos)
            elif action == "references":
                result = await server.references(
                    ReferenceParams(
                        text_document=uri,
                        position=pos,
                        context={"include_declaration": True}
                    )
                )
            elif action == "implementation":
                result = await server.implementation(uri, pos)
            elif action == "type_definition":
                result = await server.type_definition(uri, pos)
            else:
                return ToolResult(
                    success=False,
                    error=f"Unsupported navigation action: {action}"
                )
            
            # Convert result to a more readable format
            if result:
                locations = []
                for loc in result:
                    locations.append({
                        "uri": loc.uri,
                        "range": {
                            "start": {
                                "line": loc.range.start.line,
                                "character": loc.range.start.character
                            },
                            "end": {
                                "line": loc.range.end.line,
                                "character": loc.range.end.character
                            }
                        }
                    })
                return ToolResult(success=True, data=locations)
            else:
                return ToolResult(success=True, data=[])
        except Exception as e:
            return ToolResult(success=False, error=str(e)) 