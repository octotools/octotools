import asyncio
import math
import uuid
from urllib.parse import urlparse

from octotools.tools.base import BaseTool

MCP_URL = "https://search.parallel.ai/mcp"
USER_AGENT = "OctoTools/0.3.7 (Parallel Search MCP)"


def _error_text(exc):
    # The SDK uses task groups; preserve the underlying connection/server error.
    children = getattr(exc, "exceptions", None)
    return "; ".join(_error_text(child) for child in children) if children else str(exc)


class Parallel_Search_Tool(BaseTool):
    """Synchronous OctoTools tool using anonymous MCP Streamable HTTP."""

    def __init__(self, timeout=60):
        # The loader must skip this optional tool when its SDK is unavailable.
        try:
            import mcp
        except ImportError as exc:
            raise ImportError(
                "Install the parallel-search extra: pip install '.[parallel-search]'"
            ) from exc

        super().__init__(
            tool_name="Parallel_Search_Tool",
            tool_description=(
                "Search the web or fetch page excerpts through Parallel Search MCP. "
                "No account or API key needed; free search uses Fast mode. "
                "Supply search_queries for search, or urls for fetching, not both."
            ),
            tool_version="1.0.0",
            input_types={
                "objective": "str - Information to find; required for search, optional for fetch (max 200 characters for fetch).",
                "search_queries": "list[str] - Nonempty search queries, preferably 3-6 words each. Omit when fetching.",
                "urls": "list[str] - Up to 20 HTTP(S) page URLs to fetch. Omit when searching.",
                "session_id": "str - Optional conversation identifier (max 100 characters); reuse across related calls.",
            },
            output_type="dict - MCP result with content, optional structuredContent, and isError; local failures have an error field.",
            demo_commands=[
                {
                    "command": 'execution = tool.execute(objective="Find Python documentation", search_queries=["Python official documentation"])',
                    "description": "Search for Python documentation without a provider key.",
                },
                {
                    "command": 'execution = tool.execute(urls=["https://docs.python.org/3/"], objective="Python documentation")',
                    "description": "Fetch focused page excerpts.",
                },
            ],
        )
        if (
            not isinstance(timeout, (int, float))
            or not math.isfinite(timeout)
            or timeout <= 0
        ):
            raise ValueError("timeout must be a positive finite number of seconds")
        self.timeout = timeout
        self.session_id = str(uuid.uuid4())

    def execute(self, objective=None, search_queries=None, urls=None, session_id=None):
        """Return the server's MCP result dictionary, or a local error dictionary.

        This synchronous entry point matches OctoTools' Executor. Pass a stable
        session_id for related calls when the Executor creates new tool instances.
        """
        try:
            name, arguments = self._arguments(
                objective, search_queries, urls, session_id
            )
            try:
                asyncio.get_running_loop()
            except RuntimeError:
                pass
            else:
                raise ValueError(
                    "Call this synchronous tool outside an active event loop"
                )
            return asyncio.run(self._call_with_timeout(name, arguments))
        except ImportError:
            return {
                "error": "Install the parallel-search extra: pip install '.[parallel-search]'"
            }
        except TimeoutError:
            return {
                "error": f"Parallel Search MCP timed out after {self.timeout} seconds"
            }
        except Exception as exc:
            return {"error": f"Parallel Search MCP failed: {_error_text(exc)}"}

    def _arguments(self, objective, search_queries, urls, session_id):
        if (search_queries is None) == (urls is None):
            raise ValueError("Supply either search_queries or urls, not both")
        identifier = self.session_id if session_id is None else session_id
        if (
            not isinstance(identifier, str)
            or not identifier.strip()
            or len(identifier) > 100
        ):
            raise ValueError("session_id must contain 1-100 characters")
        arguments = {"session_id": identifier}
        if objective is not None:
            if not isinstance(objective, str) or not objective.strip():
                raise ValueError("objective must be a nonempty string")
            arguments["objective"] = objective
        values = search_queries if urls is None else urls
        if (
            not isinstance(values, list)
            or not values
            or any(not isinstance(value, str) or not value.strip() for value in values)
        ):
            raise ValueError(
                "search_queries or urls must be a nonempty list of strings"
            )
        if urls is None:
            if objective is None:
                raise ValueError("objective is required for search")
            arguments["search_queries"] = search_queries
            return "web_search", arguments
        if len(urls) > 20 or any(
            urlparse(url).scheme not in ("http", "https") or not urlparse(url).netloc
            for url in urls
        ):
            raise ValueError("Supply at most 20 valid HTTP(S) URLs")
        if objective is not None and len(objective) > 200:
            raise ValueError("Fetch objective must not exceed 200 characters")
        arguments["urls"] = urls
        return "web_fetch", arguments

    async def _call_with_timeout(self, name, arguments):
        return await asyncio.wait_for(self._call(name, arguments), timeout=self.timeout)

    async def _call(self, name, arguments):
        import httpx
        from mcp import ClientSession
        from mcp.client.streamable_http import streamable_http_client

        async with httpx.AsyncClient(
            headers={"User-Agent": USER_AGENT}, timeout=self.timeout
        ) as client:
            async with streamable_http_client(MCP_URL, http_client=client) as (
                read,
                write,
                _,
            ):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    result = await session.call_tool(name, arguments)
                    return result.model_dump(
                        mode="json", by_alias=True, exclude_none=True
                    )
