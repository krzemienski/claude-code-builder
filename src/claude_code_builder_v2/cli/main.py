"""Main CLI entry point for Claude Code Builder v2 (SDK-based)."""

import asyncio
import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.panel import Panel

from claude_code_builder_v2.executor import SDKBuildOrchestrator
from claude_code_builder_v2.core.config import BuildConfig, ExecutorConfig, LoggingConfig
from claude_code_builder_v2.core.exceptions import ClaudeCodeBuilderError

console = Console()
__version__ = "2.0.0-sdk"


@click.group(
    invoke_without_command=True,
    context_settings={"help_option_names": ["-h", "--help"]},
)
@click.version_option(
    __version__, "-v", "--version", prog_name="claude-code-builder-v2"
)
@click.pass_context
def cli(ctx: click.Context) -> None:
    """Claude Code Builder v2 - SDK-based AI software development automation.

    Build complete software projects from specifications using the Claude Agent SDK
    and advanced multi-agent architecture.
    """
    if ctx.invoked_subcommand is None:
        # Show welcome message if no command
        welcome = Panel.fit(
            f"[bold cyan]Claude Code Builder v2 (SDK)[/bold cyan] {__version__}\n\n"
            "[dim]SDK-based AI software development automation[/dim]\n\n"
            "Use [bold]claude-code-builder-v2 --help[/bold] to see available commands.",
            title="Welcome",
            border_style="cyan",
        )
        console.print(welcome)


@cli.command()
@click.argument("spec_file", type=click.Path(exists=True, path_type=Path))
@click.option(
    "-o",
    "--output",
    type=click.Path(path_type=Path),
    help="Output directory for the generated project",
)
@click.option(
    "--model",
    default="claude-3-haiku-20240307",
    help="Claude model to use",
)
@click.option(
    "--api-key",
    envvar="ANTHROPIC_API_KEY",
    help="Anthropic API key (or set ANTHROPIC_API_KEY env var)",
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
    default=4096,
    help="Maximum tokens per request",
)
@click.option(
    "--temperature",
    type=float,
    default=0.3,
    help="Model temperature (0.0-1.0)",
)
@click.option(
    "--verbose",
    "-v",
    count=True,
    help="Increase verbosity (can be used multiple times)",
)
def init(
    spec_file: Path,
    output: Optional[Path],
    model: str,
    api_key: Optional[str],
    max_cost: float,
    max_tokens: int,
    temperature: float,
    verbose: int,
) -> None:
    """Initialize a new project from a specification file.

    SPEC_FILE: Path to the project specification (Markdown file)

    Example:
        claude-code-builder-v2 init my-spec.md -o ./my-project
    """
    asyncio.run(
        _run_init(
            spec_file=spec_file,
            output=output,
            model=model,
            api_key=api_key,
            max_cost=max_cost,
            max_tokens=max_tokens,
            temperature=temperature,
            verbose=verbose,
        )
    )


async def _run_init(
    spec_file: Path,
    output: Optional[Path],
    model: str,
    api_key: Optional[str],
    max_cost: float,
    max_tokens: int,
    temperature: float,
    verbose: int,
) -> None:
    """Run init command (async)."""
    console.print(
        Panel.fit(
            f"[bold cyan]Claude Code Builder v2 (SDK)[/bold cyan]\n\n"
            f"[dim]Specification:[/dim] {spec_file}\n"
            f"[dim]Model:[/dim] {model}\n"
            f"[dim]Max Cost:[/dim] ${max_cost}",
            title="Initializing Build",
            border_style="cyan",
        )
    )

    if not api_key:
        console.print(
            "[red]Error: ANTHROPIC_API_KEY not set. Provide --api-key or set env var.[/red]"
        )
        sys.exit(1)

    try:
        # Create build configuration
        executor_config = ExecutorConfig(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
        )

        logging_config = LoggingConfig()
        if verbose >= 2:
            logging_config.level = "DEBUG"
        elif verbose == 1:
            logging_config.level = "INFO"

        build_config = BuildConfig(
            max_cost=max_cost,
            default_executor_config=executor_config,
            default_logging_config=logging_config,
        )

        # Create orchestrator
        orchestrator = SDKBuildOrchestrator(
            spec_path=spec_file,
            output_dir=output,
            build_config=build_config,
            api_key=api_key,
        )

        # Setup environment
        console.print("[cyan]Setting up build environment...[/cyan]")
        await orchestrator.setup()

        # Run build
        console.print("[cyan]Starting build process...[/cyan]")
        metrics = await orchestrator.build()

        # Display results
        console.print(
            Panel.fit(
                f"[bold green]Build completed successfully![/bold green]\n\n"
                f"[dim]Phases completed:[/dim] {metrics.phases_completed}\n"
                f"[dim]Tasks completed:[/dim] {metrics.tasks_completed}\n"
                f"[dim]Duration:[/dim] {metrics.total_duration:.2f}s\n"
                f"[dim]Total cost:[/dim] ${metrics.total_cost:.4f}",
                title="Build Complete",
                border_style="green",
            )
        )

    except ClaudeCodeBuilderError as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)
    except KeyboardInterrupt:
        console.print("\n[yellow]Build interrupted by user[/yellow]")
        sys.exit(130)
    except Exception as e:
        console.print(f"[red]Unexpected error: {e}[/red]")
        if verbose >= 2:
            import traceback

            traceback.print_exc()
        sys.exit(1)


@cli.command()
@click.argument("project_dir", type=click.Path(exists=True, path_type=Path))
def resume(project_dir: Path) -> None:
    """Resume a previously interrupted build.

    PROJECT_DIR: Path to the project directory

    Example:
        claude-code-builder-v2 resume ./my-project
    """
    console.print("[yellow]Resume command not yet implemented in v2[/yellow]")
    console.print("This feature will be available in a future release")


@cli.command()
@click.argument("project_dir", type=click.Path(exists=True, path_type=Path))
def status(project_dir: Path) -> None:
    """Check the status of a project build.

    PROJECT_DIR: Path to the project directory

    Example:
        claude-code-builder-v2 status ./my-project
    """
    console.print("[yellow]Status command not yet implemented in v2[/yellow]")
    console.print("This feature will be available in a future release")


@cli.command()
def version() -> None:
    """Show version information."""
    console.print(
        Panel.fit(
            f"[bold cyan]Claude Code Builder v2 (SDK)[/bold cyan]\n\n"
            f"[dim]Version:[/dim] {__version__}\n"
            f"[dim]Based on:[/dim] Claude Agent SDK for Python\n"
            f"[dim]API:[/dim] Anthropic Claude API",
            title="Version",
            border_style="cyan",
        )
    )


def main() -> None:
    """Main entry point."""
    cli()


if __name__ == "__main__":
    main()
