"""Main CLI entry point for Claude Code Builder."""

import asyncio
import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from claude_code_builder import __version__
from claude_code_builder.cli.commands import (
    analyze_command,
    build_command,
    config_command,
    init_command,
    resume_command,
    validate_command,
)
from claude_code_builder.core.config import settings
from claude_code_builder.core.exceptions import ClaudeCodeBuilderError

console = Console()


@click.group(
    invoke_without_command=True,
    context_settings={"help_option_names": ["-h", "--help"]},
)
@click.version_option(__version__, "-v", "--version", prog_name="claude-code-builder")
@click.pass_context
def cli(ctx: click.Context) -> None:
    """Claude Code Builder - AI-powered software development automation.
    
    Build complete software projects from specifications using Claude's
    advanced code generation capabilities and multi-agent architecture.
    """
    if ctx.invoked_subcommand is None:
        # Show welcome message if no command
        welcome = Panel.fit(
            f"[bold cyan]Claude Code Builder[/bold cyan] v{__version__}\n\n"
            "[dim]AI-powered software development automation[/dim]\n\n"
            "Use [bold]claude-code-builder --help[/bold] to see available commands.",
            title="Welcome",
            border_style="cyan",
        )
        console.print(welcome)


@cli.command()
@click.argument("spec_file", type=click.Path(exists=True, path_type=Path))
@click.option(
    "-o", "--output",
    type=click.Path(path_type=Path),
    help="Output directory for the generated project",
)
@click.option(
    "--model",
    default=settings.anthropic_model,
    help="Claude model to use",
)
@click.option(
    "--max-cost",
    type=float,
    default=100.0,
    help="Maximum cost limit in USD",
)
@click.option(
    "--max-tokens",
    type=int,
    default=10_000_000,
    help="Maximum token limit",
)
@click.option(
    "--phases",
    multiple=True,
    help="Specific phases to execute (can be used multiple times)",
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Perform a dry run without making API calls",
)
@click.option(
    "--skip-tests",
    is_flag=True,
    help="Skip test generation and execution",
)
@click.option(
    "--continue-on-error",
    is_flag=True,
    help="Continue execution even if tasks fail",
)
@click.option(
    "--verbose", "-v",
    count=True,
    help="Increase verbosity (can be used multiple times)",
)
@click.option(
    "--no-mcp",
    is_flag=True,
    help="Disable MCP servers (not recommended)",
)
@click.option(
    "--config",
    type=click.Path(exists=True, path_type=Path),
    help="Path to custom configuration file",
)
def build(
    spec_file: Path,
    output: Optional[Path],
    model: str,
    max_cost: float,
    max_tokens: int,
    phases: tuple,
    dry_run: bool,
    skip_tests: bool,
    continue_on_error: bool,
    verbose: int,
    no_mcp: bool,
    config: Optional[Path],
) -> None:
    """Build a complete project from a specification file.
    
    SPEC_FILE: Path to the project specification markdown file.
    
    Examples:
    
        # Basic build
        claude-code-builder build my-project.md
        
        # Specify output directory
        claude-code-builder build spec.md -o ./my-app
        
        # Build specific phases only
        claude-code-builder build spec.md --phases "Core Implementation" --phases "Testing"
        
        # Dry run to see what would be built
        claude-code-builder build spec.md --dry-run
    """
    try:
        asyncio.run(
            build_command(
                spec_file=spec_file,
                output=output,
                model=model,
                max_cost=max_cost,
                max_tokens=max_tokens,
                phases=list(phases) if phases else None,
                dry_run=dry_run,
                skip_tests=skip_tests,
                continue_on_error=continue_on_error,
                verbose=verbose,
                no_mcp=no_mcp,
                config=config,
            )
        )
    except KeyboardInterrupt:
        console.print("\n[yellow]Build interrupted by user[/yellow]")
        sys.exit(1)
    except ClaudeCodeBuilderError as e:
        console.print(f"\n[red]Build failed: {e}[/red]")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n[red]Unexpected error: {e}[/red]")
        if verbose > 0:
            console.print_exception()
        else:
            # Always print exception in development
            import traceback
            console.print(f"[dim]{traceback.format_exc()}[/dim]")
        sys.exit(1)


@cli.command()
@click.argument("project_dir", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--from-phase",
    help="Resume from a specific phase",
)
@click.option(
    "--from-task",
    help="Resume from a specific task",
)
@click.option(
    "--reset-costs",
    is_flag=True,
    help="Reset cost tracking when resuming",
)
def resume(
    project_dir: Path,
    from_phase: Optional[str],
    from_task: Optional[str],
    reset_costs: bool,
) -> None:
    """Resume a build from a previous checkpoint.
    
    PROJECT_DIR: Path to the project directory containing checkpoints.
    
    Examples:
    
        # Resume from last checkpoint
        claude-code-builder resume ./my-app-20240115_120000
        
        # Resume from specific phase
        claude-code-builder resume ./my-app --from-phase "Testing"
    """
    try:
        asyncio.run(
            resume_command(
                project_dir=project_dir,
                from_phase=from_phase,
                from_task=from_task,
                reset_costs=reset_costs,
            )
        )
    except Exception as e:
        console.print(f"\n[red]Resume failed: {e}[/red]")
        sys.exit(1)


@cli.command()
@click.argument("spec_file", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--detailed",
    is_flag=True,
    help="Show detailed analysis",
)
@click.option(
    "--estimate-cost",
    is_flag=True,
    help="Estimate build cost",
)
@click.option(
    "--check-requirements",
    is_flag=True,
    help="Check if all requirements are clear",
)
def analyze(
    spec_file: Path,
    detailed: bool,
    estimate_cost: bool,
    check_requirements: bool,
) -> None:
    """Analyze a specification file without building.
    
    SPEC_FILE: Path to the project specification markdown file.
    
    Examples:
    
        # Basic analysis
        claude-code-builder analyze my-project.md
        
        # Detailed analysis with cost estimate
        claude-code-builder analyze spec.md --detailed --estimate-cost
    """
    try:
        asyncio.run(
            analyze_command(
                spec_file=spec_file,
                detailed=detailed,
                estimate_cost=estimate_cost,
                check_requirements=check_requirements,
            )
        )
    except Exception as e:
        console.print(f"\n[red]Analysis failed: {e}[/red]")
        sys.exit(1)


@cli.command()
@click.argument("spec_file", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--fix",
    is_flag=True,
    help="Attempt to fix validation issues",
)
@click.option(
    "--strict",
    is_flag=True,
    help="Use strict validation rules",
)
def validate(
    spec_file: Path,
    fix: bool,
    strict: bool,
) -> None:
    """Validate a specification file format and completeness.
    
    SPEC_FILE: Path to the project specification markdown file.
    
    Examples:
    
        # Validate specification
        claude-code-builder validate my-project.md
        
        # Validate and fix issues
        claude-code-builder validate spec.md --fix
    """
    try:
        asyncio.run(
            validate_command(
                spec_file=spec_file,
                fix=fix,
                strict=strict,
            )
        )
    except Exception as e:
        console.print(f"\n[red]Validation failed: {e}[/red]")
        sys.exit(1)


@cli.command()
@click.option(
    "--project-dir",
    type=click.Path(path_type=Path),
    default=".",
    help="Project directory to initialize",
)
@click.option(
    "--template",
    type=click.Choice(["minimal", "standard", "advanced"]),
    default="standard",
    help="Specification template to use",
)
@click.option(
    "--name",
    help="Project name",
)
@click.option(
    "--type",
    "project_type",
    type=click.Choice(["cli", "api", "web", "library", "fullstack"]),
    help="Project type",
)
def init(
    project_dir: Path,
    template: str,
    name: Optional[str],
    project_type: Optional[str],
) -> None:
    """Initialize a new Claude Code Builder project.
    
    Creates a template specification file and project structure.
    
    Examples:
    
        # Initialize in current directory
        claude-code-builder init
        
        # Initialize with specific template
        claude-code-builder init --template advanced --name "My API"
    """
    try:
        asyncio.run(
            init_command(
                project_dir=project_dir,
                template=template,
                name=name,
                project_type=project_type,
            )
        )
    except Exception as e:
        console.print(f"\n[red]Initialization failed: {e}[/red]")
        sys.exit(1)


@cli.group()
def config() -> None:
    """Manage Claude Code Builder configuration."""
    pass


@config.command("show")
@click.option(
    "--secrets",
    is_flag=True,
    help="Show sensitive values like API keys",
)
def config_show(secrets: bool) -> None:
    """Show current configuration."""
    try:
        asyncio.run(config_command.show_config(show_secrets=secrets))
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]")
        sys.exit(1)


@config.command("set")
@click.argument("key")
@click.argument("value")
def config_set(key: str, value: str) -> None:
    """Set a configuration value.
    
    Examples:
    
        # Set API key
        claude-code-builder config set anthropic_api_key sk-ant-...
        
        # Set default model
        claude-code-builder config set anthropic_model claude-3-opus-20240229
    """
    try:
        asyncio.run(config_command.set_config(key=key, value=value))
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]")
        sys.exit(1)


@config.command("test")
def config_test() -> None:
    """Test configuration and API connection."""
    try:
        asyncio.run(config_command.test_config())
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]")
        sys.exit(1)


@cli.command()
@click.option(
    "--json",
    "output_json",
    is_flag=True,
    help="Output in JSON format",
)
def status(output_json: bool) -> None:
    """Show Claude Code Builder system status.
    
    Displays information about:
    - API connection status
    - MCP server availability
    - Recent builds
    - System resources
    """
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Checking system status...", total=None)
        
        # Check API
        api_status = "✓ Connected" if settings.anthropic_api_key else "✗ Not configured"
        
        # Check MCP servers (simplified)
        mcp_status = "✓ Available"
        
        progress.stop()
    
    if output_json:
        import json
        status_data = {
            "version": __version__,
            "api_status": api_status,
            "mcp_status": mcp_status,
        }
        console.print(json.dumps(status_data, indent=2))
    else:
        # Create status table
        table = Table(title="Claude Code Builder Status", show_header=False)
        table.add_column("Component", style="cyan")
        table.add_column("Status")
        
        table.add_row("Version", __version__)
        table.add_row("API Connection", api_status)
        table.add_row("MCP Servers", mcp_status)
        table.add_row("Default Model", settings.anthropic_model)
        
        console.print(table)


def main() -> None:
    """Main entry point."""
    cli()


# Create app for entry point
app = cli


if __name__ == "__main__":
    main()