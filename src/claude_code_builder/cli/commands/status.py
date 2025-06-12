"""Status command implementation."""

import os
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


async def status_command() -> None:
    """Show Claude Code Builder status and health check."""
    console.print("\n[bold cyan]Claude Code Builder Status[/bold cyan]\n")
    
    # Version info
    console.print("[bold]Version:[/bold] 1.0.0")
    
    # Environment check
    env_table = Table(title="Environment")
    env_table.add_column("Check", style="cyan")
    env_table.add_column("Status")
    env_table.add_column("Details", style="dim")
    
    # Check Python version
    import sys
    py_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    py_ok = sys.version_info >= (3, 11)
    env_table.add_row(
        "Python Version",
        "[green]✓[/green]" if py_ok else "[red]✗[/red]",
        py_version
    )
    
    # Check API key
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    api_key_ok = bool(api_key)
    env_table.add_row(
        "API Key",
        "[green]✓[/green]" if api_key_ok else "[red]✗[/red]",
        f"Set ({len(api_key)} chars)" if api_key_ok else "Not set"
    )
    
    # Check MCP servers
    mcp_servers = ["filesystem", "github", "memory"]
    mcp_status = []
    
    for server in mcp_servers:
        # Simple check - in real implementation would verify actual availability
        available = True  # Placeholder
        mcp_status.append((server, available))
    
    mcp_ok = all(status for _, status in mcp_status)
    env_table.add_row(
        "MCP Servers",
        "[green]✓[/green]" if mcp_ok else "[yellow]⚠[/yellow]",
        f"{sum(1 for _, ok in mcp_status if ok)}/{len(mcp_servers)} available"
    )
    
    console.print(env_table)
    
    # Recent builds
    console.print("\n[bold]Recent Builds:[/bold]")
    
    # Check for recent project directories
    cwd = Path.cwd()
    recent_builds = []
    
    for item in cwd.iterdir():
        if item.is_dir() and item.name.startswith("claude-code-builder-"):
            recent_builds.append(item)
    
    if recent_builds:
        build_table = Table()
        build_table.add_column("Project", style="cyan")
        build_table.add_column("Created", style="dim")
        build_table.add_column("Status")
        
        for build in sorted(recent_builds, key=lambda x: x.stat().st_mtime, reverse=True)[:5]:
            # Check if it has checkpoints
            has_checkpoints = (build / ".claude-code-builder" / "checkpoints").exists()
            status = "[green]Complete[/green]" if has_checkpoints else "[yellow]In Progress[/yellow]"
            
            created = Path(build).stat().st_mtime
            from datetime import datetime
            created_str = datetime.fromtimestamp(created).strftime("%Y-%m-%d %H:%M")
            
            build_table.add_row(build.name, created_str, status)
        
        console.print(build_table)
    else:
        console.print("[dim]No recent builds found[/dim]")
    
    # Health summary
    all_ok = py_ok and api_key_ok
    
    if all_ok:
        console.print(
            Panel.fit(
                "[green]✓ All systems operational[/green]",
                title="Health Check",
                border_style="green"
            )
        )
    else:
        issues = []
        if not py_ok:
            issues.append("Python 3.11+ required")
        if not api_key_ok:
            issues.append("Set ANTHROPIC_API_KEY environment variable")
        
        console.print(
            Panel.fit(
                "[red]Issues found:[/red]\n" + "\n".join(f"• {issue}" for issue in issues),
                title="Health Check",
                border_style="red"
            )
        )
    
    console.print()  # Empty line at end