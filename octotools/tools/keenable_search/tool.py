import os
import requests
from typing import List, Dict, Any, Optional

from octotools.tools.base import BaseTool

from dotenv import load_dotenv
load_dotenv()


class Keenable_Search_Tool(BaseTool):
    # Works without an API key, so load it only when it is named in enabled_tools, not via ["all"].
    load_with_all = False

    def __init__(self):
        super().__init__(
            tool_name="Keenable_Search_Tool",
            tool_description="A tool that performs web searches through the Keenable API and returns the title, link, and snippet of each result. Works without an API key. Supports site and publication date filtering.",
            tool_version="1.0.0",
            input_types={
                "query": "str - The search query to be used for the web search.",
                "num_results": "int - The number of search results to return (default: 10, max: 50).",
                "site": "str - Optional domain to restrict results to, e.g. 'arxiv.org' (default: None).",
                "published_after": "str - Optional start date filter in YYYY-MM-DD format (default: None).",
                "published_before": "str - Optional end date filter in YYYY-MM-DD format (default: None).",
            },
            output_type="list - A list of dictionaries containing search result information.",
            demo_commands=[
                {
                    "command": 'execution = tool.execute(query="Python programming")',
                    "description": "Perform a web search for 'Python programming' and return the default number of results."
                },
                {
                    "command": 'execution = tool.execute(query="protein structure prediction", num_results=5, site="arxiv.org", published_after="2025-01-01")',
                    "description": "Search arxiv.org for 'protein structure prediction' pages published since 2025-01-01 and return 5 results."
                },
            ],
        )
        self.api_key = os.getenv("KEENABLE_API_KEY")  # Optional, lifts rate limits (Ref: https://keenable.ai)
        self.base_url = "https://api.keenable.ai/v1/search"
        self.app_title = "OctoTools"

    def execute(
        self,
        query: str,
        num_results: int = 10,
        site: Optional[str] = None,
        published_after: Optional[str] = None,
        published_before: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Executes a web search through Keenable based on the provided query.

        Parameters:
            query (str): The search query.
            num_results (int): The number of search results to return (default: 10, max: 50).
            site (str): Optional domain to restrict results to.
            published_after (str): Optional start date filter in YYYY-MM-DD format.
            published_before (str): Optional end date filter in YYYY-MM-DD format.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries containing search result information.
        """
        num_results = max(1, min(int(num_results), 50))
        payload = {"query": query, "max_results": num_results}
        if site:
            payload["site"] = site
        if published_after:
            payload["published_after"] = published_after
        if published_before:
            payload["published_before"] = published_before

        # Without a key, use the public endpoint, which requires an app title.
        headers = {"X-Keenable-Title": self.app_title}
        url = f"{self.base_url}/public"
        if self.api_key:
            headers["X-API-Key"] = self.api_key
            url = self.base_url

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            data = response.json()
            if response.status_code != 200:
                detail = (data.get("message") or data.get("error")) if isinstance(data, dict) else None
                return [{"error": f"Keenable API error (HTTP {response.status_code}): {detail or response.reason}"}]

            output = []
            for item in data.get("results") or []:
                result = {
                    "title": item.get("title", ""),
                    "link": item.get("url", ""),
                    "snippet": (item.get("snippet") or item.get("description") or "")[:2000],  # Limit each snippet to 2000 characters
                }
                if item.get("published_at"):
                    result["published_date"] = item["published_at"]
                output.append(result)
                if len(output) >= num_results:
                    break

            if not output:
                return [{"error": "No results found."}]
            return output

        except Exception as e:
            return [{"error": f"An error occurred: {str(e)}"}]

    def get_metadata(self):
        """
        Returns the metadata for the Keenable_Search_Tool.

        Returns:
            dict: A dictionary containing the tool's metadata.
        """
        metadata = super().get_metadata()
        return metadata


if __name__ == "__main__":
    # Test command:
    """
    Run the following commands in the terminal to test the script:

    export KEENABLE_API_KEY=your_api_key_here  # optional, lifts rate limits
    cd octotools/tools/keenable_search
    python tool.py
    """

    # Example usage of the Keenable_Search_Tool
    tool = Keenable_Search_Tool()

    # Get tool metadata
    metadata = tool.get_metadata()
    print(metadata)

    # Execute the tool to perform a web search
    query = "nobel prize winners in chemistry 2024"
    try:
        execution = tool.execute(query=query, num_results=5)
        print("\nExecution Result:")
        print(f"Search query: {query}")
        print(f"Number of results: {len(execution)}")
        print("\nSearch Results:")
        if "error" in execution[0]:
            print(f"Error: {execution[0]['error']}")
        else:
            for i, item in enumerate(execution, 1):
                print(f"\n{i}. Title: {item['title']}")
                print(f"   URL: {item['link']}")
                print(f"   Snippet: {item['snippet'][:200]}...")
    except Exception as e:
        print(f"Execution failed: {e}")

    print("Done!")
