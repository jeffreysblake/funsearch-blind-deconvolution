"""Main CLI application for FunSearch framework."""

from pathlib import Path
from typing import Optional

import typer
from rich import print as rprint
from rich.console import Console
from rich.table import Table

app = typer.Typer(
    name="funsearch",
    help="FunSearch Framework - Program synthesis using evolutionary algorithms + LLMs",
    add_completion=False,
)

console = Console()


@app.command()
def init(
    name: str = typer.Argument(..., help="Project name"),
    template: Optional[str] = typer.Option(None, help="Template to use"),
    config: Optional[Path] = typer.Option(None, help="Config file to create"),
):
    """
    Initialize a new FunSearch project.

    Creates project directory structure and configuration file.
    """
    console.print(f"[bold green]Initializing project: {name}[/bold green]")

    # Create project directory
    project_dir = Path(".funsearch/projects") / name
    project_dir.mkdir(parents=True, exist_ok=True)

    console.print(f"✓ Created project directory: {project_dir}")

    # Create config if specified
    if config:
        config_path = project_dir / "config.yaml"
        # Copy template config
        from config.models import Config, ExecutionConfig, FunSearchConfig, LLMConfig, SandboxConfig

        default_config = Config(
            mode="development",
            llm=LLMConfig(provider="template_mock", model="mock-gpt-4"),
            sandbox=SandboxConfig(provider="subprocess"),
            funsearch=FunSearchConfig(),
            execution=ExecutionConfig(),
        )
        default_config.to_file(config_path)
        console.print(f"✓ Created config: {config_path}")

    console.print(f"\n[bold]Next steps:[/bold]")
    console.print(f"1. Edit project specification in: {project_dir}/spec.py")
    console.print(f"2. Run experiment: funsearch run --project {name}")


@app.command()
def test(
    config_file: Optional[Path] = typer.Option(None, "--config", "-c", help="Config file to use"),
):
    """
    Test configuration and components.

    Validates configuration and tests that mock components work.
    """
    from backend.core.factory import ComponentFactory
    from config.models import load_config

    console.print("[bold]Testing FunSearch configuration...[/bold]\n")

    # Load config
    try:
        config = load_config(config_file)
        console.print("[green]✓[/green] Configuration loaded successfully")

        # Display config summary
        table = Table(title="Configuration Summary")
        table.add_column("Component", style="cyan")
        table.add_column("Provider", style="magenta")
        table.add_column("Details", style="white")

        table.add_row(
            "LLM",
            config.llm.provider,
            f"{config.llm.model} (temp={config.llm.temperature})",
        )
        table.add_row(
            "Sandbox",
            config.sandbox.provider,
            f"{config.sandbox.max_workers} workers, {config.sandbox.timeout}s timeout",
        )
        table.add_row(
            "FunSearch",
            "Algorithm",
            f"{config.funsearch.num_islands} islands, {config.funsearch.samples_per_prompt} samples/prompt",
        )

        console.print(table)

    except Exception as e:
        console.print(f"[red]✗[/red] Configuration error: {e}")
        raise typer.Exit(1)

    # Test components
    console.print("\n[bold]Testing components...[/bold]\n")

    try:
        # Create sampler
        console.print("Creating LLM sampler...")
        sampler = ComponentFactory.create_sampler(config)
        console.print(f"[green]✓[/green] {sampler.__class__.__name__} created")

        # Test sampling
        console.print("Testing code generation...")
        prompt = "def stopping_criterion(iteration, psnr, psnr_delta):\n    "
        samples = sampler.sample(prompt, num_samples=2)
        console.print(f"[green]✓[/green] Generated {len(samples)} code samples")

        for i, sample in enumerate(samples, 1):
            console.print(f"\n[dim]Sample {i}:[/dim]")
            console.print(f"[yellow]{sample}[/yellow]")

        stats = sampler.get_stats()
        console.print(f"\n[dim]Sampler stats: {stats}[/dim]")

    except Exception as e:
        console.print(f"[red]✗[/red] Sampler error: {e}")
        raise typer.Exit(1)

    try:
        # Create evaluator
        console.print("\n\nCreating evaluator...")
        evaluator = ComponentFactory.create_evaluator(config)
        console.print(f"[green]✓[/green] {evaluator.__class__.__name__} created")

        # Test evaluation
        console.print("Testing code evaluation...")
        test_program = """
def evaluate(test_input):
    return 42.0
"""
        score = evaluator.evaluate(test_program, {})
        console.print(f"[green]✓[/green] Evaluation successful: score = {score}")

        evaluator.close()

    except Exception as e:
        console.print(f"[red]✗[/red] Evaluator error: {e}")
        raise typer.Exit(1)

    console.print("\n[bold green]All tests passed![/bold green]")


@app.command()
def info():
    """
    Display system information and configuration.

    Shows available models, services, and configuration.
    """
    from config.models import Config

    console.print("[bold]FunSearch Framework Information[/bold]\n")

    # Check services
    console.print("[bold]Service Status:[/bold]")

    # Check LM Studio
    try:
        import httpx

        response = httpx.get("http://localhost:1234/v1/models", timeout=2)
        if response.status_code == 200:
            console.print("[green]✓[/green] LM Studio: Available")
            models = response.json().get("data", [])
            for model in models[:3]:  # Show first 3
                console.print(f"  - {model.get('id', 'unknown')}")
        else:
            console.print("[yellow]⚠[/yellow] LM Studio: Not responding")
    except Exception:
        console.print("[red]✗[/red] LM Studio: Not available")

    # Check Docker
    try:
        import docker

        client = docker.from_env()
        client.ping()
        console.print("[green]✓[/green] Docker: Available")
    except Exception:
        console.print("[red]✗[/red] Docker: Not available")

    # Show config locations
    console.print("\n[bold]Configuration Files:[/bold]")
    config_paths = [
        Path(".funsearch/config.yaml"),
        Path(".funsearch/config.dev.yaml"),
        Path(".funsearch/config.prod.yaml"),
    ]

    for path in config_paths:
        if path.exists():
            console.print(f"[green]✓[/green] {path}")
        else:
            console.print(f"[dim]  {path} (not found)[/dim]")


@app.command()
def version():
    """Display version information."""
    import backend
    import cli

    console.print(f"FunSearch Framework")
    console.print(f"Backend: v{backend.__version__}")
    console.print(f"CLI: v{cli.__version__}")


if __name__ == "__main__":
    app()
