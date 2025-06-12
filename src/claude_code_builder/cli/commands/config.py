"""Config command implementation."""

from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.table import Table

from claude_code_builder.core.config import settings, GlobalConfig

console = Console()


async def config_command(
    action: str,
    key: Optional[str] = None,
    value: Optional[str] = None,
) -> None:
    """Manage configuration settings."""
    global_config = GlobalConfig()
    
    if action == "show":
        # Show current configuration
        console.print("\n[bold]Current Configuration:[/bold]\n")
        
        table = Table(title="Settings")
        table.add_column("Key", style="cyan")
        table.add_column("Value")
        table.add_column("Source", style="dim")
        
        # Add settings
        config_dict = settings.model_dump()
        for key, value in config_dict.items():
            if key == "api_key" and value:
                value = value[:10] + "..." + value[-4:]  # Mask API key
            
            source = "env" if key in ["api_key"] else "config"
            table.add_row(key, str(value), source)
        
        console.print(table)
        
    elif action == "set":
        if not key or value is None:
            console.print("[red]Error: Both key and value required for set action[/red]")
            return
        
        # Set configuration value
        try:
            global_config.set(key, value)
            console.print(f"[green]✓ Set {key} = {value}[/green]")
        except Exception as e:
            console.print(f"[red]Error setting configuration: {e}[/red]")
    
    elif action == "get":
        if not key:
            console.print("[red]Error: Key required for get action[/red]")
            return
        
        # Get configuration value
        value = global_config.get(key)
        if value is not None:
            console.print(f"{key} = {value}")
        else:
            console.print(f"[yellow]Key '{key}' not found[/yellow]")
    
    elif action == "reset":
        # Reset to defaults
        try:
            config_path = Path.home() / ".claude-code-builder" / "config.yaml"
            if config_path.exists():
                config_path.unlink()
            console.print("[green]✓ Configuration reset to defaults[/green]")
        except Exception as e:
            console.print(f"[red]Error resetting configuration: {e}[/red]")
    
    else:
        console.print(f"[red]Unknown action: {action}[/red]")
        console.print("Valid actions: show, set, get, reset")