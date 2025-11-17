"""CLI entry point for Claude Code Builder v2."""

import asyncio
import os
import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.table import Table

from claude_code_builder_v2.core.config import BuildConfig
from claude_code_builder_v2.executor import SDKBuildOrchestrator

console = Console()


@click.group()
@click.version_option(version="2.0.0")
def cli() -> None:
    """Claude Code Builder v2 - AI-powered software development."""
    pass


@cli.command()
@click.argument("spec_file", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--output-dir",
    "-o",
    type=click.Path(path_type=Path),
    help="Output directory for build",
)
@click.option(
    "--max-cost",
    type=float,
    default=10.0,
    help="Maximum cost in USD",
)
@click.option(
    "--api-key",
    envvar="ANTHROPIC_API_KEY",
    help="Anthropic API key",
)
def build(
    spec_file: Path,
    output_dir: Optional[Path],
    max_cost: float,
    api_key: Optional[str],
) -> None:
    """Build a project from specification file."""
    if not api_key:
        console.print("[red]Error: ANTHROPIC_API_KEY not set[/red]")
        sys.exit(1)

    console.print(f"[cyan]Building from specification:[/cyan] {spec_file}")

    # Create build config
    config = BuildConfig(max_cost=max_cost)

    # Create orchestrator
    orchestrator = SDKBuildOrchestrator(
        spec_path=spec_file,
        build_config=config,
        output_dir=output_dir,
        api_key=api_key,
    )

    # Run build
    try:
        with console.status("[cyan]Initializing build..."):
            asyncio.run(orchestrator.setup())

        with console.status("[cyan]Running build..."):
            metrics = asyncio.run(orchestrator.build())

        # Display results
        console.print("\n[green]✓ Build completed[/green]\n")

        table = Table(title="Build Metrics")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")

        table.add_row("Build ID", metrics.build_id[:8])
        table.add_row("Status", metrics.status.value)
        table.add_row("Phases Completed", str(metrics.phases_completed))
        table.add_row("Phases Failed", str(metrics.phases_failed))
        table.add_row("Duration", f"{metrics.total_duration:.2f}s")
        table.add_row("Cost", f"${metrics.total_cost:.4f}")
        table.add_row("Tokens", str(metrics.total_tokens))

        console.print(table)

        if orchestrator.project_dir:
            console.print(f"\n[cyan]Output:[/cyan] {orchestrator.project_dir}")

    except Exception as e:
        console.print(f"\n[red]✗ Build failed: {e}[/red]")
        sys.exit(1)


@cli.command()
@click.argument("spec_file", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--output-dir",
    "-o",
    type=click.Path(path_type=Path),
    required=True,
    help="Output directory for project initialization",
)
@click.option(
    "--api-key",
    envvar="ANTHROPIC_API_KEY",
    help="Anthropic API key",
)
def init(
    spec_file: Path,
    output_dir: Path,
    api_key: Optional[str],
) -> None:
    """Initialize a new project from specification."""
    if not api_key:
        console.print("[red]Error: ANTHROPIC_API_KEY not set[/red]")
        sys.exit(1)

    console.print(f"[cyan]Initializing project from:[/cyan] {spec_file}")
    console.print(f"[cyan]Output directory:[/cyan] {output_dir}")

    # Create build config
    config = BuildConfig()

    # Create orchestrator
    orchestrator = SDKBuildOrchestrator(
        spec_path=spec_file,
        build_config=config,
        output_dir=output_dir,
        api_key=api_key,
    )

    # Run setup only
    try:
        with console.status("[cyan]Initializing project..."):
            asyncio.run(orchestrator.setup())

        console.print(f"\n[green]✓ Project initialized:[/green] {orchestrator.project_dir}")
        console.print("\n[cyan]Next steps:[/cyan]")
        console.print(f"  1. Review the project structure at {orchestrator.project_dir}")
        console.print(f"  2. Run 'claude-code-builder build {spec_file}' to build")
        console.print(f"     or 'claude-code-builder resume {output_dir}' to continue")

    except Exception as e:
        console.print(f"\n[red]✗ Initialization failed: {e}[/red]")
        sys.exit(1)


@cli.command()
@click.argument("project_dir", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--api-key",
    envvar="ANTHROPIC_API_KEY",
    help="Anthropic API key",
)
@click.option(
    "--max-cost",
    type=float,
    default=10.0,
    help="Maximum cost in USD",
)
def resume(
    project_dir: Path,
    api_key: Optional[str],
    max_cost: float,
) -> None:
    """Resume an interrupted build."""
    if not api_key:
        console.print("[red]Error: ANTHROPIC_API_KEY not set[/red]")
        sys.exit(1)

    console.print(f"[cyan]Resuming build:[/cyan] {project_dir}")

    # Look for spec file in project directory
    spec_candidates = list(project_dir.glob("*.md"))
    spec_file = spec_candidates[0] if spec_candidates else None

    if not spec_file:
        console.print("[red]Error: No specification file found in project directory[/red]")
        sys.exit(1)

    # Create build config
    config = BuildConfig(max_cost=max_cost)

    # Create orchestrator
    orchestrator = SDKBuildOrchestrator(
        spec_path=spec_file,
        build_config=config,
        output_dir=project_dir,
        api_key=api_key,
    )

    # Resume build
    try:
        with console.status("[cyan]Resuming build..."):
            metrics = asyncio.run(orchestrator.build())

        # Display results
        console.print("\n[green]✓ Build completed[/green]\n")

        table = Table(title="Build Metrics")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")

        table.add_row("Build ID", metrics.build_id[:8])
        table.add_row("Status", metrics.status.value)
        table.add_row("Phases Completed", str(metrics.phases_completed))
        table.add_row("Phases Failed", str(metrics.phases_failed))
        table.add_row("Duration", f"{metrics.total_duration:.2f}s")
        table.add_row("Cost", f"${metrics.total_cost:.4f}")
        table.add_row("Tokens", str(metrics.total_tokens))

        console.print(table)

    except Exception as e:
        console.print(f"\n[red]✗ Resume failed: {e}[/red]")
        sys.exit(1)


@cli.command()
@click.argument("project_dir", type=click.Path(exists=True, path_type=Path))
def status(project_dir: Path) -> None:
    """Show status of a build project."""
    console.print(f"[cyan]Project:[/cyan] {project_dir}")

    # Check for build artifacts
    logs_dir = project_dir / "logs"
    if logs_dir.exists():
        log_files = list(logs_dir.glob("*.log"))
        console.print(f"[cyan]Log files:[/cyan] {len(log_files)}")

        # Show latest log file
        if log_files:
            latest_log = max(log_files, key=lambda p: p.stat().st_mtime)
            console.print(f"[cyan]Latest log:[/cyan] {latest_log.name}")

            # Show file size
            size_bytes = latest_log.stat().st_size
            size_kb = size_bytes / 1024
            console.print(f"[cyan]Log size:[/cyan] {size_kb:.2f} KB")
    else:
        console.print("[yellow]No logs found[/yellow]")

    # Check for build state
    state_file = project_dir / ".ccb_state.json"
    if state_file.exists():
        console.print("[green]✓ Build state found[/green]")
    else:
        console.print("[yellow]No build state found[/yellow]")


@cli.command()
@click.argument("project_dir", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--tail",
    "-n",
    type=int,
    default=50,
    help="Number of lines to show from end of log",
)
@click.option(
    "--follow",
    "-f",
    is_flag=True,
    help="Follow log file (tail -f behavior)",
)
def logs(
    project_dir: Path,
    tail: int,
    follow: bool,
) -> None:
    """Show build logs."""
    logs_dir = project_dir / "logs"

    if not logs_dir.exists():
        console.print("[red]Error: No logs directory found[/red]")
        sys.exit(1)

    log_files = list(logs_dir.glob("*.log"))
    if not log_files:
        console.print("[yellow]No log files found[/yellow]")
        sys.exit(0)

    # Get latest log file
    latest_log = max(log_files, key=lambda p: p.stat().st_mtime)
    console.print(f"[cyan]Showing:[/cyan] {latest_log.name}\n")

    try:
        if follow:
            # Follow mode - continuously show new lines
            console.print("[cyan]Following log file (Ctrl+C to stop)...[/cyan]\n")
            import time

            with latest_log.open("r") as f:
                # Go to end of file
                f.seek(0, 2)
                while True:
                    line = f.readline()
                    if line:
                        print(line, end="")
                    else:
                        time.sleep(0.1)
        else:
            # Tail mode - show last N lines
            with latest_log.open("r") as f:
                lines = f.readlines()
                for line in lines[-tail:]:
                    print(line, end="")

    except KeyboardInterrupt:
        console.print("\n[yellow]Stopped following log[/yellow]")
    except Exception as e:
        console.print(f"\n[red]Error reading log: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    cli()
