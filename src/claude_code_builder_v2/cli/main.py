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
@click.argument("project_dir", type=click.Path(exists=True, path_type=Path))
def status(project_dir: Path) -> None:
    """Show status of a build project."""
    console.print(f"[cyan]Project:[/cyan] {project_dir}")

    # Check for build artifacts
    logs_dir = project_dir / "logs"
    if logs_dir.exists():
        log_files = list(logs_dir.glob("*.log"))
        console.print(f"[cyan]Log files:[/cyan] {len(log_files)}")
    else:
        console.print("[yellow]No logs found[/yellow]")


if __name__ == "__main__":
    cli()
