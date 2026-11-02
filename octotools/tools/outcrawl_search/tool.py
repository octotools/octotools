import os
import requests
from typing import List, Dict, Any

from octotools.tools.base import BaseTool

from dotenv import load_dotenv
load_dotenv()


class Outcrawl_Search_Tool(BaseTool):
    def __init__(self):
        super().__init__(
            tool_name="Outcrawl_Search_Tool",
            tool_description="A tool that performs web searches through the Outcrawl API and returns the title, link, and snippet of each result.",
            tool_version="1.0.0",
            input_types={
                "query": "str - The search query to be used for the web search.",
                "num_results": "int - The number of search results to return (default: 10, max: 20).",
            },
            output_type="list - A list of dictionaries containing search result information.",
            demo_commands=[
                {
                    "command": 'execution = tool.execute(query="Python programming")',
                    "description": "Perform a web search for 'Python programming' and return the default number of results."
                },
                {
                    "command": 'execution = tool.execute(query="latest James Webb telescope discoveries", num_results=5)',
                    "description": "Search for 'latest James Webb telescope discoveries' and return 5 results."
                },
            ],
        )
        self.api_key = os.getenv("OUTCRAWL_API_KEY")  # Ref: https://outcrawl.ai
        self.base_url = "https://api.outcrawl.ai/v1/search"

    def execute(self, query: str, num_results: int = 10) -> List[Dict[str, Any]]:
        """
        Executes a web search through Outcrawl based on the provided query.

        Parameters:
            query (str): The search query.
            num_results (int): The number of search results to return (default: 10, max: 20).

        Returns:
            List[Dict[str, Any]]: A list of dictionaries containing search result information.
        """
        if not self.api_key:
            return [{"error": "Outcrawl API key is not set. Please set the OUTCRAWL_API_KEY environment variable."}]

        num_results = max(1, min(int(num_results), 20))
        payload = {"query": query, "limit": num_results}
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "octotools",
        }

        try:
            response = requests.post(self.base_url, json=payload, headers=headers, timeout=30)
            if response.status_code != 200:
                try:
                    data = response.json()
                except ValueError:
                    data = None
                detail = data.get("error") if isinstance(data, dict) else None
                return [{"error": f"Outcrawl API error (HTTP {response.status_code}): {detail or response.reason}"}]
            data = response.json()

            output = []
            for item in data.get("hits") or []:
                link = item.get("url") or ""
                if not link.startswith(("http://", "https://")):
                    continue
                output.append({
                    "title": item.get("title", ""),
                    "link": link,
                    "snippet": item.get("snippet", ""),
                })
                if len(output) >= num_results:
                    break

            if not output:
                return [{"error": "No results found."}]
            return output

        except Exception as e:
            return [{"error": f"An error occurred: {str(e)}"}]

    def get_metadata(self):
        """
        Returns the metadata for the Outcrawl_Search_Tool.

        Returns:
            dict: A dictionary containing the tool's metadata.
        """
        metadata = super().get_metadata()
        return metadata


if __name__ == "__main__":
    # Test command:
    """
    Run the following commands in the terminal to test the script:

    export OUTCRAWL_API_KEY=your_api_key_here
    cd octotools/tools/outcrawl_search
    python tool.py
    """

    # Example usage of the Outcrawl_Search_Tool
    tool = Outcrawl_Search_Tool()

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
                print(f"   Snippet: {item['snippet']}")
    except Exception as e:
        print(f"Execution failed: {e}")

    print("Done!")
