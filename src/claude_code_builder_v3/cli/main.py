"""
Claude Code Builder v3 CLI.

Main CLI entry point with commands for:
- Building projects with skills
- Managing skills (list, generate, test, stats)
- Skill discovery and generation
"""

import asyncio
import os
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
import structlog

from claude_code_builder_v3.sdk.build_orchestrator import BuildOrchestrator
from claude_code_builder_v3.skills.manager import SkillManager
from claude_code_builder_v3.agents.skill_generator import SkillGenerator
from claude_code_builder_v3.agents.skill_validator import SkillValidator
from claude_code_builder_v3.core.models import SkillGap

console = Console()
logger = structlog.get_logger(__name__)


def get_api_key() -> str:
    """Get Anthropic API key from environment."""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        console.print(
            "[red]Error: ANTHROPIC_API_KEY environment variable not set[/red]"
        )
        raise click.Abort()
    return api_key


@click.group()
@click.version_option(version="3.0.0", prog_name="Claude Code Builder v3")
def cli() -> None:
    """
    Claude Code Builder v3 - Skills-Powered Development Platform.

    Transform specifications into production-ready applications using
    intelligent Claude Skills.
    """
    pass


@cli.command()
@click.argument("spec_file", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--output-dir",
    "-o",
    type=click.Path(path_type=Path),
    required=True,
    help="Output directory for generated code",
)
@click.option(
    "--no-skill-generation",
    is_flag=True,
    help="Disable automatic skill generation",
)
@click.option(
    "--model",
    default="claude-sonnet-4-5-20250929",
    help="Claude model to use",
)
def build(
    spec_file: Path,
    output_dir: Path,
    no_skill_generation: bool,
    model: str,
) -> None:
    """
    Build a project from specification with automatic skill generation.

    This command:
    1. Analyzes the specification
    2. Identifies required skills
    3. Generates missing skills automatically (unless --no-skill-generation)
    4. Builds the complete project using skills
    5. Outputs production-ready code

    Example:
        claude-code-builder-v3 build spec.md --output-dir ./myproject
    """
    api_key = get_api_key()

    async def run_build() -> None:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Initializing build orchestrator...", total=None)

            # Initialize orchestrator
            orchestrator = BuildOrchestrator(api_key=api_key, model=model)
            await orchestrator.initialize()

            progress.update(task, description="Executing build...")

            # Execute build
            result = await orchestrator.execute_build(
                spec_path=spec_file,
                output_dir=output_dir,
                generate_missing_skills=not no_skill_generation,
            )

            progress.stop()

            # Display results
            if result.success:
                console.print(Panel.fit(
                    f"[green]✓ Build completed successfully![/green]\n\n"
                    f"Files generated: {len(result.generated_files)}\n"
                    f"Skills used: {len(result.skills_used)}\n"
                    f"Skills generated: {len(result.generated_skills)}\n"
                    f"Duration: {result.total_duration_ms / 1000:.2f}s\n"
                    f"Tokens used: {result.total_tokens_used:,}\n"
                    f"Cost: ${result.total_cost_usd:.4f}",
                    title="Build Success",
                ))

                console.print(f"\n[cyan]Output directory:[/cyan] {output_dir}")

                if result.generated_skills:
                    console.print(f"\n[yellow]Generated Skills:[/yellow]")
                    for skill_name in result.generated_skills:
                        console.print(f"  • {skill_name}")

            else:
                console.print("[red]✗ Build failed[/red]")
                if result.errors:
                    console.print("\n[red]Errors:[/red]")
                    for error in result.errors:
                        console.print(f"  • {error}")

    asyncio.run(run_build())


@cli.group()
def skills() -> None:
    """Manage Claude Skills."""
    pass


@skills.command("list")
@click.option("--category", help="Filter by category")
@click.option("--search", help="Search skills by query")
def list_skills(category: Optional[str], search: Optional[str]) -> None:
    """
    List available Claude Skills.

    Shows all discovered skills from:
    - Built-in skills
    - Generated skills
    - Installed marketplace skills

    Example:
        claude-code-builder-v3 skills list
        claude-code-builder-v3 skills list --category backend
        claude-code-builder-v3 skills list --search fastapi
    """
    async def run_list() -> None:
        manager = SkillManager()
        await manager.initialize()

        if search:
            skill_list = await manager.search_skills(search)
            title = f"Skills matching '{search}'"
        elif category:
            skill_list = await manager.list_all_skills(category=category)
            title = f"Skills in category '{category}'"
        else:
            skill_list = await manager.list_all_skills()
            title = "All Available Skills"

        if not skill_list:
            console.print("[yellow]No skills found[/yellow]")
            return

        # Create table
        table = Table(title=title, show_header=True, header_style="bold cyan")
        table.add_column("Name", style="green")
        table.add_column("Description")
        table.add_column("Technologies", style="blue")
        table.add_column("Category", style="magenta")

        for skill in skill_list:
            table.add_row(
                skill.name,
                skill.description[:60] + "..." if len(skill.description) > 60 else skill.description,
                ", ".join(skill.technologies[:3]) + ("..." if len(skill.technologies) > 3 else ""),
                skill.category or "N/A",
            )

        console.print(table)
        console.print(f"\n[cyan]Total skills: {len(skill_list)}[/cyan]")

    asyncio.run(run_list())


@skills.command("generate")
@click.option("--name", required=True, help="Skill name (kebab-case)")
@click.option("--description", required=True, help="Skill description")
@click.option("--technologies", required=True, help="Comma-separated technologies")
@click.option("--model", default="claude-sonnet-4-5-20250929", help="Claude model")
def generate_skill(
    name: str, description: str, technologies: str, model: str
) -> None:
    """
    Generate a new Claude Skill.

    Creates a complete skill with:
    - SKILL.md with proper format
    - Example implementations
    - Validation tests
    - Best practices

    Example:
        claude-code-builder-v3 skills generate \\
            --name fastapi-redis-cache \\
            --description "FastAPI with Redis caching" \\
            --technologies "FastAPI,Redis,Python"
    """
    api_key = get_api_key()

    async def run_generate() -> None:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Generating skill...", total=None)

            # Create skill gap
            tech_list = [t.strip() for t in technologies.split(",")]
            gap = SkillGap(
                name=name,
                description=description,
                technologies=tech_list,
                patterns=[],
                integration_points=[],
            )

            # Generate
            generator = SkillGenerator(api_key=api_key, model=model)
            skill = await generator.generate_skill(gap)

            progress.update(task, description="Validating skill...")

            # Validate
            validator = SkillValidator()
            validation = await validator.validate_skill(skill)

            if not validation.valid:
                progress.stop()
                console.print("[red]✗ Skill validation failed[/red]")
                for error in validation.errors:
                    console.print(f"  • {error}")
                return

            progress.update(task, description="Saving skill...")

            # Save
            skill_path = await generator.save_generated_skill(skill)

            progress.stop()

            console.print(Panel.fit(
                f"[green]✓ Skill generated successfully![/green]\n\n"
                f"Name: {skill.name}\n"
                f"Location: {skill_path}\n"
                f"Examples: {len(skill.examples)}\n"
                f"Tests: {len(skill.tests)}",
                title="Skill Generated",
            ))

    asyncio.run(run_generate())


@skills.command("stats")
def show_stats() -> None:
    """
    Show skill usage statistics.

    Displays:
    - Total skills available
    - Usage counts per skill
    - Success rates
    - Token savings

    Example:
        claude-code-builder-v3 skills stats
    """
    async def run_stats() -> None:
        manager = SkillManager()
        await manager.initialize()

        stats = manager.get_all_stats()

        if not stats or all(s.total_uses == 0 for s in stats):
            console.print("[yellow]No skill usage statistics yet[/yellow]")
            return

        # Create table
        table = Table(title="Skill Usage Statistics", show_header=True, header_style="bold cyan")
        table.add_column("Skill", style="green")
        table.add_column("Uses", justify="right")
        table.add_column("Success Rate", justify="right")
        table.add_column("Avg Duration", justify="right")

        for stat in stats:
            if stat.total_uses > 0:
                table.add_row(
                    stat.skill_name,
                    str(stat.total_uses),
                    f"{stat.success_rate * 100:.1f}%",
                    f"{stat.average_duration_ms:.0f}ms",
                )

        console.print(table)

        # Overall stats
        manager_stats = manager.get_manager_stats()
        console.print(f"\n[cyan]Overall Statistics:[/cyan]")
        console.print(f"  Total Skills: {manager_stats['total_skills']}")
        console.print(f"  Total Uses: {manager_stats['total_skill_uses']}")
        console.print(f"  Success Rate: {manager_stats['overall_success_rate'] * 100:.1f}%")

    asyncio.run(run_stats())


if __name__ == "__main__":
    cli()
