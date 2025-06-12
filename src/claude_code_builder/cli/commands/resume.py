"""Resume command implementation."""

from pathlib import Path
from typing import Optional

from rich.console import Console

from claude_code_builder.core.output_manager import ProjectDirectory, ProjectResumer
from claude_code_builder.executor.build_orchestrator import BuildOrchestrator

console = Console()


async def resume_command(
    project_dir: Path,
    from_phase: Optional[str] = None,
    from_task: Optional[str] = None,
    reset_costs: bool = False,
) -> None:
    """Resume a build from checkpoint."""
    console.print(f"\n[cyan]Resuming build from: {project_dir}[/cyan]\n")
    
    try:
        # Load project directory
        project = await ProjectDirectory.load(project_dir)
        
        console.print(f"[bold]Project:[/bold] {project.metadata.project_name}")
        console.print(f"[bold]Can Resume:[/bold] {'Yes' if project.can_resume else 'No'}")
        
        if project.last_phase:
            console.print(f"[bold]Last Phase:[/bold] {project.last_phase}")
        
        if not project.can_resume:
            console.print("\n[red]Cannot resume: No valid checkpoint found[/red]")
            return
        
        # Create orchestrator
        orchestrator = BuildOrchestrator(
            spec_path=Path(project.metadata.specification_path),
            resume_from=project_dir,
        )
        
        # Set up and resume
        await orchestrator.setup()
        
        if reset_costs:
            orchestrator.executor.total_cost = 0.0
            orchestrator.executor.total_tokens_used = 0
            console.print("[yellow]Cost tracking reset[/yellow]\n")
        
        # Resume build
        metrics = await orchestrator.build()
        
        console.print("\n[green]Build resumed and completed successfully![/green]")
        
    except Exception as e:
        console.print(f"\n[red]Resume failed: {e}[/red]")
        raise