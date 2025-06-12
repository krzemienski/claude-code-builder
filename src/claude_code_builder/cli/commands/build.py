"""Build command implementation."""

from pathlib import Path
from typing import List, Optional

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn

from claude_code_builder.core.config import BuildConfig
from claude_code_builder.executor.build_orchestrator import BuildOrchestrator

console = Console()


async def build_command(
    spec_file: Path,
    output: Optional[Path] = None,
    model: str = "claude-opus-4-20250514",  # Updated to Opus 4
    max_cost: float = 100.0,
    max_tokens: int = 10_000_000,
    phases: Optional[List[str]] = None,
    dry_run: bool = False,
    skip_tests: bool = False,
    continue_on_error: bool = False,
    verbose: int = 0,
    no_mcp: bool = False,
    config: Optional[Path] = None,
) -> None:
    """Execute the build command."""
    # Display build configuration
    console.print(
        Panel.fit(
            f"[bold]Building from:[/bold] {spec_file.name}\n"
            f"[bold]Output:[/bold] {output or 'Auto-generated'}\n"
            f"[bold]Model:[/bold] {model}\n"
            f"[bold]Max Cost:[/bold] ${max_cost:.2f}\n"
            f"[bold]Max Tokens:[/bold] {max_tokens:,}",
            title="Build Configuration",
            border_style="blue",
        )
    )
    
    # Create build configuration
    build_config = BuildConfig(
        max_cost=max_cost,
        max_tokens=max_tokens,
        phases_to_execute=phases,
        dry_run=dry_run,
        skip_tests=skip_tests,
        continue_on_error=continue_on_error,
        verbose=verbose,
    )
    
    # Initialize orchestrator
    orchestrator = BuildOrchestrator(
        spec_path=spec_file,
        output_dir=output,
        build_config=build_config,
    )
    
    # Set up build environment
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        TimeElapsedColumn(),
        console=console,
    ) as progress:
        setup_task = progress.add_task("Setting up build environment...", total=None)
        await orchestrator.setup()
        progress.remove_task(setup_task)
    
    # Execute build
    console.print("\n[bold cyan]Starting build process...[/bold cyan]\n")
    
    try:
        metrics = await orchestrator.build()
        
        # Display results
        console.print("\n" + "="*60 + "\n")
        console.print(
            Panel.fit(
                f"[bold green]✓ Build completed successfully![/bold green]\n\n"
                f"[bold]Output Directory:[/bold] {orchestrator.project_dir.path}\n"
                f"[bold]Phases Completed:[/bold] {metrics.completed_phases}/{metrics.total_phases}\n"
                f"[bold]Tasks Completed:[/bold] {metrics.completed_tasks}/{metrics.total_tasks}\n"
                f"[bold]Files Generated:[/bold] {metrics.files_generated}\n"
                f"[bold]Lines of Code:[/bold] {metrics.lines_of_code:,}\n"
                f"[bold]Total Cost:[/bold] ${metrics.total_cost:.2f}\n"
                f"[bold]Total Tokens:[/bold] {metrics.total_tokens_used:,}\n"
                f"[bold]Build Time:[/bold] {metrics.build_duration_seconds/60:.1f} minutes",
                title="Build Results",
                border_style="green",
            )
        )
        
        if verbose > 0:
            console.print(f"\n[dim]MCP Servers Used: {metrics.mcp_servers_used}[/dim]")
            console.print(f"[dim]Checkpoints Created: {metrics.checkpoints_created}[/dim]")
        
    except Exception as e:
        console.print(f"\n[red]Build failed: {e}[/red]")
        if verbose > 0:
            console.print_exception()
        raise