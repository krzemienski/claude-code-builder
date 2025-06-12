"""Analyze command implementation."""

from pathlib import Path

from rich.console import Console
from rich.table import Table

from claude_code_builder.agents import SpecAnalyzer
from claude_code_builder.core.context_manager import ContextManager
from claude_code_builder.core.models import ExecutionContext
from claude_code_builder.executor.executor import ClaudeCodeExecutor

console = Console()


async def analyze_command(
    spec_file: Path,
    detailed: bool = False,
    estimate_cost: bool = False,
    check_requirements: bool = False,
) -> None:
    """Analyze a specification file."""
    console.print(f"\n[cyan]Analyzing specification: {spec_file.name}[/cyan]\n")
    
    # Initialize components
    executor = ClaudeCodeExecutor()
    context_manager = ContextManager()
    
    # Load specification
    spec_content = spec_file.read_text()
    token_count = len(spec_content.split()) * 1.3  # Rough estimate
    
    console.print(f"Specification size: {len(spec_content):,} characters ({int(token_count):,} tokens)\n")
    
    if detailed:
        # Perform detailed analysis
        console.print("[yellow]Performing detailed analysis...[/yellow]")
        
        # Create table
        table = Table(title="Specification Analysis")
        table.add_column("Aspect", style="cyan")
        table.add_column("Details")
        
        # Basic analysis
        lines = spec_content.split('\n')
        sections = [line for line in lines if line.startswith('#')]
        
        table.add_row("Total Lines", str(len(lines)))
        table.add_row("Sections", str(len(sections)))
        table.add_row("Estimated Complexity", "Medium")  # Would be calculated
        
        console.print(table)
    
    if estimate_cost:
        # Estimate cost
        estimated_phases = 10
        tokens_per_phase = 100000
        total_tokens = estimated_phases * tokens_per_phase
        
        # Rough cost calculation
        cost_per_million = 75  # $75 per million tokens
        estimated_cost = (total_tokens / 1_000_000) * cost_per_million
        
        console.print(f"\n[bold]Cost Estimate:[/bold]")
        console.print(f"  Estimated Phases: {estimated_phases}")
        console.print(f"  Estimated Tokens: {total_tokens:,}")
        console.print(f"  Estimated Cost: ${estimated_cost:.2f}")
    
    if check_requirements:
        # Check requirements
        console.print(f"\n[bold]Requirements Check:[/bold]")
        
        # Simple checks
        has_objectives = "objective" in spec_content.lower() or "goal" in spec_content.lower()
        has_requirements = "requirement" in spec_content.lower() or "must" in spec_content.lower()
        has_tech_stack = "technology" in spec_content.lower() or "stack" in spec_content.lower()
        
        console.print(f"  ✓ Has objectives: {'Yes' if has_objectives else 'No'}")
        console.print(f"  ✓ Has requirements: {'Yes' if has_requirements else 'No'}")
        console.print(f"  ✓ Has technology stack: {'Yes' if has_tech_stack else 'No'}")
    
    console.print("\n[green]Analysis complete![/green]")