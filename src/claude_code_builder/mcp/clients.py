"""MCP client implementations for each server."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, TYPE_CHECKING

from claude_code_builder.core.enums import MCPServer
from claude_code_builder.core.exceptions import MCPServerError


class DateTimeEncoder(json.JSONEncoder):
    """JSON encoder that handles datetime and Path objects."""
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, Path):
            return str(obj)
        return super().default(obj)

if TYPE_CHECKING:
    from claude_code_builder.mcp.orchestrator import MCPOrchestrator


class BaseMCPClient:
    """Base class for MCP clients."""
    
    def __init__(self, orchestrator: "MCPOrchestrator", server: MCPServer) -> None:
        """Initialize the client."""
        self.orchestrator = orchestrator
        self.server = server
        self.logger = orchestrator.logger

    async def call(self, method: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """Make a call to the MCP server."""
        try:
            return await self.orchestrator.call_server(self.server, method, params)
        except Exception as e:
            raise MCPServerError(
                f"MCP call failed: {str(e)}",
                self.server.value,
                method,
                {"params": params, "error": str(e)},
            )


class FilesystemClient(BaseMCPClient):
    """Client for filesystem MCP server."""
    
    def __init__(self, orchestrator: "MCPOrchestrator") -> None:
        """Initialize the client."""
        super().__init__(orchestrator, MCPServer.FILESYSTEM)

    async def read_file(self, path: str) -> str:
        """Read a file."""
        result = await self.call("read_file", {"path": path})
        return result.get("data", {}).get("content", "")

    async def write_file(self, path: str, content: str) -> None:
        """Write a file."""
        await self.call("write_file", {"path": path, "content": content})

    async def list_directory(self, path: str) -> List[Dict[str, Any]]:
        """List directory contents."""
        result = await self.call("list_directory", {"path": path})
        return result.get("data", {}).get("entries", [])

    async def create_directory(self, path: str) -> None:
        """Create a directory."""
        await self.call("create_directory", {"path": path})

    async def move_file(self, source: str, destination: str) -> None:
        """Move or rename a file."""
        await self.call("move_file", {"source": source, "destination": destination})

    async def search_files(
        self,
        path: str,
        pattern: str,
        exclude_patterns: Optional[List[str]] = None,
    ) -> List[str]:
        """Search for files."""
        params = {
            "path": path,
            "pattern": pattern,
        }
        if exclude_patterns:
            params["excludePatterns"] = exclude_patterns
        
        result = await self.call("search_files", params)
        return result.get("data", {}).get("matches", [])

    async def get_file_info(self, path: str) -> Dict[str, Any]:
        """Get file information."""
        result = await self.call("get_file_info", {"path": path})
        return result.get("data", {})


class MemoryClient(BaseMCPClient):
    """Client for memory MCP server."""
    
    def __init__(self, orchestrator: "MCPOrchestrator") -> None:
        """Initialize the client."""
        super().__init__(orchestrator, MCPServer.MEMORY)

    async def create_entities(self, entities: List[Dict[str, Any]]) -> None:
        """Create entities in the knowledge graph."""
        await self.call("create_entities", {"entities": entities})

    async def create_relations(self, relations: List[Dict[str, Any]]) -> None:
        """Create relations between entities."""
        await self.call("create_relations", {"relations": relations})

    async def add_observations(self, observations: List[Dict[str, Any]]) -> None:
        """Add observations to entities."""
        await self.call("add_observations", {"observations": observations})

    async def read_graph(self) -> Dict[str, Any]:
        """Read the entire knowledge graph."""
        result = await self.call("read_graph")
        return result.get("data", {})

    async def search_nodes(self, query: str) -> List[Dict[str, Any]]:
        """Search for nodes in the graph."""
        result = await self.call("search_nodes", {"query": query})
        return result.get("data", {}).get("nodes", [])

    async def open_nodes(self, names: List[str]) -> List[Dict[str, Any]]:
        """Open specific nodes by name."""
        result = await self.call("open_nodes", {"names": names})
        return result.get("data", {}).get("nodes", [])

    async def store_project_knowledge(
        self,
        project_name: str,
        phase: str,
        data: Dict[str, Any],
    ) -> None:
        """Store project-specific knowledge."""
        # Create entity for the project phase
        entity = {
            "name": f"{project_name}:{phase}",
            "entityType": "ProjectPhase",
            "observations": [
                f"Phase: {phase}",
                f"Timestamp: {data.get('timestamp', 'unknown')}",
                f"Status: {data.get('status', 'unknown')}",
            ],
        }
        
        await self.create_entities([entity])
        
        # Add detailed observations
        if "details" in data:
            observations = [
                {
                    "entityName": entity["name"],
                    "contents": [json.dumps(data["details"], cls=DateTimeEncoder)],
                }
            ]
            await self.add_observations(observations)


class Context7Client(BaseMCPClient):
    """Client for Context7 MCP server."""
    
    def __init__(self, orchestrator: "MCPOrchestrator") -> None:
        """Initialize the client."""
        super().__init__(orchestrator, MCPServer.CONTEXT7)

    async def resolve_library_id(self, library_name: str) -> Dict[str, Any]:
        """Resolve a library name to Context7 ID."""
        result = await self.call("resolve-library-id", {"libraryName": library_name})
        return result.get("data", {})

    async def get_library_docs(
        self,
        library_id: str,
        tokens: int = 10000,
        topic: Optional[str] = None,
    ) -> str:
        """Get library documentation."""
        params = {
            "context7CompatibleLibraryID": library_id,
            "tokens": tokens,
        }
        if topic:
            params["topic"] = topic
        
        result = await self.call("get-library-docs", params)
        return result.get("data", {}).get("documentation", "")

    async def get_claude_code_docs(self, topic: Optional[str] = None) -> str:
        """Get Claude Code SDK documentation."""
        # Claude Code SDK has a known Context7 ID
        return await self.get_library_docs(
            "/anthropic/claude-code-sdk",
            tokens=20000,
            topic=topic,
        )


class GitClient(BaseMCPClient):
    """Client for git MCP server."""
    
    def __init__(self, orchestrator: "MCPOrchestrator") -> None:
        """Initialize the client."""
        super().__init__(orchestrator, MCPServer.GIT)

    async def status(self, repo_path: str) -> Dict[str, Any]:
        """Get git status."""
        result = await self.call("git_status", {"repo_path": repo_path})
        return result.get("data", {})

    async def add(self, repo_path: str, files: List[str]) -> None:
        """Add files to staging."""
        await self.call("git_add", {"repo_path": repo_path, "files": files})

    async def commit(self, repo_path: str, message: str) -> str:
        """Create a commit."""
        result = await self.call("git_commit", {
            "repo_path": repo_path,
            "message": message,
        })
        return result.get("data", {}).get("commit_sha", "")

    async def diff(self, repo_path: str, target: Optional[str] = None) -> str:
        """Get diff."""
        params = {"repo_path": repo_path}
        if target:
            params["target"] = target
        
        result = await self.call("git_diff", params)
        return result.get("data", {}).get("diff", "")

    async def log(self, repo_path: str, max_count: int = 10) -> List[Dict[str, Any]]:
        """Get commit log."""
        result = await self.call("git_log", {
            "repo_path": repo_path,
            "max_count": max_count,
        })
        return result.get("data", {}).get("commits", [])

    async def create_branch(
        self,
        repo_path: str,
        branch_name: str,
        base_branch: Optional[str] = None,
    ) -> None:
        """Create a new branch."""
        params = {
            "repo_path": repo_path,
            "branch_name": branch_name,
        }
        if base_branch:
            params["base_branch"] = base_branch
        
        await self.call("git_create_branch", params)

    async def checkout(self, repo_path: str, branch_name: str) -> None:
        """Checkout a branch."""
        await self.call("git_checkout", {
            "repo_path": repo_path,
            "branch_name": branch_name,
        })


class GithubClient(BaseMCPClient):
    """Client for GitHub MCP server."""
    
    def __init__(self, orchestrator: "MCPOrchestrator") -> None:
        """Initialize the client."""
        super().__init__(orchestrator, MCPServer.GITHUB)

    async def create_repository(
        self,
        name: str,
        description: Optional[str] = None,
        private: bool = False,
        auto_init: bool = True,
    ) -> Dict[str, Any]:
        """Create a new repository."""
        params = {
            "name": name,
            "private": private,
            "autoInit": auto_init,
        }
        if description:
            params["description"] = description
        
        result = await self.call("create_repository", params)
        return result.get("data", {})

    async def create_issue(
        self,
        owner: str,
        repo: str,
        title: str,
        body: Optional[str] = None,
        labels: Optional[List[str]] = None,
        assignees: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Create an issue."""
        params = {
            "owner": owner,
            "repo": repo,
            "title": title,
        }
        if body:
            params["body"] = body
        if labels:
            params["labels"] = labels
        if assignees:
            params["assignees"] = assignees
        
        result = await self.call("create_issue", params)
        return result.get("data", {})

    async def create_pull_request(
        self,
        owner: str,
        repo: str,
        title: str,
        head: str,
        base: str,
        body: Optional[str] = None,
        draft: bool = False,
    ) -> Dict[str, Any]:
        """Create a pull request."""
        params = {
            "owner": owner,
            "repo": repo,
            "title": title,
            "head": head,
            "base": base,
            "draft": draft,
        }
        if body:
            params["body"] = body
        
        result = await self.call("create_pull_request", params)
        return result.get("data", {})

    async def push_files(
        self,
        owner: str,
        repo: str,
        branch: str,
        files: List[Dict[str, str]],
        message: str,
    ) -> None:
        """Push multiple files to repository."""
        await self.call("push_files", {
            "owner": owner,
            "repo": repo,
            "branch": branch,
            "files": files,
            "message": message,
        })


class SequentialThinkingClient(BaseMCPClient):
    """Client for sequential thinking MCP server."""
    
    def __init__(self, orchestrator: "MCPOrchestrator") -> None:
        """Initialize the client."""
        super().__init__(orchestrator, MCPServer.SEQUENTIAL_THINKING)

    async def think_through(
        self,
        thought: str,
        thought_number: int,
        total_thoughts: int,
        next_thought_needed: bool = True,
        is_revision: bool = False,
        revises_thought: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Process a thought in the chain."""
        params = {
            "thought": thought,
            "thoughtNumber": thought_number,
            "totalThoughts": total_thoughts,
            "nextThoughtNeeded": next_thought_needed,
            "isRevision": is_revision,
        }
        if revises_thought is not None:
            params["revisesThought"] = revises_thought
        
        result = await self.call("sequentialthinking", params)
        return result.get("data", {})

    async def solve_problem(
        self,
        problem: str,
        estimated_steps: int = 5,
    ) -> List[Dict[str, Any]]:
        """Solve a problem using sequential thinking."""
        thoughts = []
        thought_number = 1
        total_thoughts = estimated_steps
        
        # Initial thought
        result = await self.think_through(
            f"Understanding the problem: {problem}",
            thought_number,
            total_thoughts,
        )
        thoughts.append(result)
        
        # Continue thinking until done
        while result.get("nextThoughtNeeded", True) and thought_number < 50:
            thought_number += 1
            
            # Adjust total thoughts if needed
            if thought_number > total_thoughts:
                total_thoughts = thought_number + 2
            
            # Generate next thought based on previous
            next_thought = f"Building on previous analysis..."  # Would be more sophisticated
            
            result = await self.think_through(
                next_thought,
                thought_number,
                total_thoughts,
            )
            thoughts.append(result)
        
        return thoughts


class TaskMasterClient(BaseMCPClient):
    """Client for TaskMaster AI MCP server."""
    
    def __init__(self, orchestrator: "MCPOrchestrator") -> None:
        """Initialize the client."""
        super().__init__(orchestrator, MCPServer.TASKMASTER)

    async def get_tasks(
        self,
        project_root: str,
        status: Optional[str] = None,
        with_subtasks: bool = False,
    ) -> List[Dict[str, Any]]:
        """Get tasks from TaskMaster."""
        params = {
            "projectRoot": project_root,
            "withSubtasks": with_subtasks,
        }
        if status:
            params["status"] = status
        
        result = await self.call("get_tasks", params)
        return result.get("data", {}).get("tasks", [])

    async def set_task_status(
        self,
        project_root: str,
        task_id: str,
        status: str,
    ) -> None:
        """Set task status."""
        await self.call("set_task_status", {
            "projectRoot": project_root,
            "id": task_id,
            "status": status,
        })

    async def parse_prd(
        self,
        project_root: str,
        input_path: Optional[str] = None,
        num_tasks: str = "10",
        force: bool = False,
    ) -> Dict[str, Any]:
        """Parse PRD to generate tasks."""
        params = {
            "projectRoot": project_root,
            "numTasks": num_tasks,
            "force": force,
        }
        if input_path:
            params["input"] = input_path
        
        result = await self.call("parse_prd", params)
        return result.get("data", {})

    async def initialize_project(
        self,
        project_root: str,
        skip_install: bool = False,
    ) -> None:
        """Initialize TaskMaster project."""
        await self.call("initialize_project", {
            "projectRoot": project_root,
            "skipInstall": skip_install,
            "yes": True,  # Always skip prompts
        })

    async def expand_task(
        self,
        project_root: str,
        task_id: str,
        num_subtasks: str = "5",
        prompt: Optional[str] = None,
        research: bool = False,
    ) -> Dict[str, Any]:
        """Expand a task into subtasks."""
        params = {
            "projectRoot": project_root,
            "id": task_id,
            "num": num_subtasks,
            "research": research,
        }
        if prompt:
            params["prompt"] = prompt
        
        result = await self.call("expand_task", params)
        return result.get("data", {})

    async def next_task(self, project_root: str) -> Optional[Dict[str, Any]]:
        """Get the next task to work on."""
        result = await self.call("next_task", {"projectRoot": project_root})
        return result.get("data", {}).get("task")


__all__ = [
    "Context7Client",
    "FilesystemClient",
    "MemoryClient",
    "GitClient",
    "GithubClient",
    "SequentialThinkingClient",
    "TaskMasterClient",
]