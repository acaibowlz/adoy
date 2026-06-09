import functools
import http.server
import shutil
import threading
import time
from importlib.resources import files
from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.console import Console
from rich.panel import Panel
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from adoy.builder import build as run_build
from adoy.parser import load_config
from adoy.validator import ConfigValidationError, validate_config

app = typer.Typer(no_args_is_help=True, help="adoy — a static site generator for large sites with incremental builds.")
console = Console()
err_console = Console(stderr=True)

_SCAFFOLD = files("adoy.scaffold")


@app.command()
def init(
    name: Annotated[str, typer.Argument(help="Name of the project to create.")],
) -> None:
    """Create a new adoy project with a sample config, templates, and content."""
    root = Path.cwd() / name
    if root.exists():
        typer.echo(f"Directory already exists: {root}", err=True)
        raise typer.Exit(1)

    (root / "static").mkdir(parents=True)

    # Copy scaffold directories
    for subdir in ("templates", "content"):
        shutil.copytree(str(_SCAFFOLD.joinpath(subdir)), root / subdir)

    # Render adoy.toml with the project name
    toml = _SCAFFOLD.joinpath("adoy.toml").read_text(encoding="utf-8").format(name=name)
    (root / "adoy.toml").write_text(toml)

    claude_md = _SCAFFOLD.joinpath("CLAUDE.md").read_text(encoding="utf-8").replace("{name}", name)
    (root / "CLAUDE.md").write_text(claude_md)

    (root / ".gitignore").write_text("public/\n.adoy-cache.json\n")

    console.print(f"\n[bold green]✓[/] Created project [bold]{name}[/]\n")
    console.print(f"  [dim]cd {name}[/]")
    console.print("  [dim]adoy build[/]\n")


@app.command()
def build(  # type: ignore[misc]
    project: Annotated[
        Optional[Path],
        typer.Option("--project", "-p", help="Path to the project root. Defaults to the current directory."),
    ] = None,
    clean: Annotated[
        bool,
        typer.Option(
            "--clean-build", help="Remove the incremental build cache before building, forcing a full rebuild."
        ),
    ] = False,
) -> None:
    """Build the site from source into the output directory.

    Performs an incremental build by default — only changed content, templates,
    or config triggers a rebuild of affected pages. Use --clean-build to force
    a full rebuild from scratch.
    """
    root = project or Path.cwd()
    try:
        config = load_config(root)
        validate_config(config, root)
    except FileNotFoundError as e:
        err_console.print(f"[bold red]Error:[/] {e}")
        raise typer.Exit(1)
    except ConfigValidationError as e:
        err_console.print(Panel(str(e), title="[bold red]Config errors[/]", border_style="red"))
        raise typer.Exit(1)

    if clean:
        cache_file = root / ".adoy-cache.json"
        if cache_file.exists():
            cache_file.unlink()

    with console.status("[bold cyan]Building...[/]"):
        run_build(config, root)
    console.print("[bold green]✓[/] Build complete.")


@app.command()
def serve(
    project: Annotated[
        Optional[Path],
        typer.Option("--project", "-p", help="Path to the project root. Defaults to the current directory."),
    ] = None,
    port: Annotated[int, typer.Option("--port", help="Port to serve on.")] = 8000,
) -> None:
    """Build the site and serve it locally with live reload.

    Watches content/, templates/, and adoy.toml for changes and automatically
    rebuilds affected pages. Serves the output directory over HTTP.
    """
    root = project or Path.cwd()
    try:
        config = load_config(root)
        validate_config(config, root)
    except (FileNotFoundError, ConfigValidationError) as e:
        err_console.print(f"[bold red]Error:[/] {e}")
        raise typer.Exit(1)

    with console.status("[bold cyan]Building...[/]"):
        run_build(config, root)
    console.print(f"[bold green]✓[/] Serving at [bold cyan]http://localhost:{port}[/] — watching for changes...")

    output_dir = root / config.paths.output
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(output_dir))
    httpd = http.server.HTTPServer(("", port), handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()

    class _Handler(FileSystemEventHandler):
        def on_any_event(self, event):  # type: ignore[override]
            if event.is_directory:
                return
            try:
                run_build(config, root)
                console.print("[bold green]✓[/] Rebuilt.")
            except Exception as exc:
                err_console.print(f"[bold red]Build error:[/] {exc}")

    observer = Observer()
    for watch_dir in [root / config.paths.content, root / config.paths.templates]:
        observer.schedule(_Handler(), str(watch_dir), recursive=True)
    observer.schedule(_Handler(), str(root / "adoy.toml"))
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        httpd.shutdown()
    observer.join()


if __name__ == "__main__":
    app()
