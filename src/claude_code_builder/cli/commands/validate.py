"""Validate command implementation."""

from pathlib import Path

from rich.console import Console
from rich.table import Table

console = Console()


async def validate_command(
    spec_file: Path,
    fix: bool = False,
    strict: bool = False,
) -> None:
    """Validate a specification file."""
    console.print(f"\n[cyan]Validating specification: {spec_file.name}[/cyan]\n")
    
    # Read specification
    spec_content = spec_file.read_text()
    lines = spec_content.split('\n')
    
    # Validation checks
    issues = []
    warnings = []
    
    # Check for required sections
    required_sections = ["objective", "requirements", "scope"]
    content_lower = spec_content.lower()
    
    for section in required_sections:
        if section not in content_lower:
            issues.append(f"Missing section: {section}")
    
    # Check for structure
    if not any(line.startswith('#') for line in lines):
        issues.append("No markdown headers found")
    
    # Check for empty sections
    current_section = None
    section_content = []
    
    for line in lines:
        if line.startswith('#'):
            # Check previous section
            if current_section and not any(section_content):
                warnings.append(f"Empty section: {current_section}")
            current_section = line
            section_content = []
        else:
            if line.strip():
                section_content.append(line)
    
    # Display results
    if not issues and not warnings:
        console.print("[green]✓ Specification is valid![/green]")
    else:
        # Create results table
        table = Table(title="Validation Results")
        table.add_column("Type", style="bold")
        table.add_column("Issue")
        
        for issue in issues:
            table.add_row("[red]Error[/red]", issue)
        
        for warning in warnings:
            table.add_row("[yellow]Warning[/yellow]", warning)
        
        console.print(table)
        
        if fix and issues:
            console.print("\n[yellow]Attempting to fix issues...[/yellow]")
            
            # Simple fix: add missing sections
            fixes = []
            for issue in issues:
                if issue.startswith("Missing section:"):
                    section = issue.split(": ")[1]
                    fixes.append(f"\n## {section.title()}\n\nTODO: Add {section} details.\n")
            
            if fixes:
                # Append fixes to file
                with open(spec_file, 'a') as f:
                    f.write('\n'.join(fixes))
                
                console.print(f"[green]Added {len(fixes)} missing sections[/green]")
        
        # Exit with error if strict mode and issues found
        if strict and issues:
            raise ValueError(f"Validation failed with {len(issues)} errors")