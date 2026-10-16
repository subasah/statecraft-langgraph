"""
Interactive CLI for StateCraft: Stateful Agentic Workflows.

Provides rich terminal rendering for inspecting and executing:
- Pattern 1: Dynamic Branching & Conditional Routing
- Pattern 2: Self-Correction & Evaluator-Optimizer Loop
- Pattern 3: Resilience & Retry Circuit
- Pattern 4: Human-in-the-Loop Checkpoints & Resumption
- Pattern 5: Hierarchical Supervisor & Multi-Agent Subgraph
- Flagship: Enterprise Autonomous Release Pipeline
"""

import sys
import time
from typing import Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.markdown import Markdown
from rich.prompt import Prompt, Confirm
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command

from statecraft.patterns.dynamic_branching import build_branching_graph
from statecraft.patterns.self_correction import build_self_correction_graph
from statecraft.patterns.resilience_retries import build_resilience_graph
from statecraft.patterns.human_in_the_loop import build_hitl_graph
from statecraft.patterns.hierarchical_supervisor import build_supervisor_graph
from statecraft.orchestrator.enterprise_pipeline import build_enterprise_pipeline

console = Console()


def print_banner():
    banner = """
    ╔═══════════════════════════════════════════════════════════════════╗
    ║      STATECRAFT: STATEFUL AGENTIC WORKFLOWS (LANGGRAPH)           ║
    ║   Branching • Retries • Self-Correction • HITL • Orchestration    ║
    ╚═══════════════════════════════════════════════════════════════════╝
    """
    console.print(f"[bold cyan]{banner}[/bold cyan]")


def run_cli_branching():
    console.print(Panel.fit("[bold green]Pattern 1: Dynamic Branching & Conditional Routing[/bold green]"))
    query = Prompt.ask(
        "[yellow]Enter test prompt (or press Enter for default security query)[/yellow]",
        default="How do I patch a critical authentication bypass CVE?"
    )
    
    app = build_branching_graph()
    with console.status("[bold blue]Executing dynamic routing graph...[/bold blue]"):
        result = app.invoke({"query": query})

    table = Table(title="Routing Decision & Telemetry", show_header=True, header_style="bold magenta")
    table.add_column("Field", style="cyan")
    table.add_column("Value", style="white")
    table.add_row("Input Query", query)
    table.add_row("Category Detected", result.get("category", "N/A"))
    table.add_row("Complexity Score", f"{result.get('complexity_score', 0):.2f}")
    table.add_row("Route Taken", f"[bold yellow]{result.get('selected_route', 'N/A')}[/bold yellow]")
    table.add_row("Path Steps", " -> ".join(result.get("execution_path", [])))
    
    console.print(table)
    console.print(Panel(result.get("response", ""), title="[bold green]Specialist Response[/bold green]"))


def run_cli_self_correction():
    console.print(Panel.fit("[bold green]Pattern 2: Self-Correction & Evaluator-Optimizer Loop[/bold green]"))
    app = build_self_correction_graph()
    initial_state = {
        "task": "Write calculate_moving_average(numbers: list[float], window_size: int) -> list[float]",
        "max_iterations": 3,
        "iterations": 0,
        "logs": []
    }
    
    with console.status("[bold blue]Executing generator-evaluator loop...[/bold blue]"):
        result = app.invoke(initial_state)

    table = Table(title="Self-Correction Execution Log", show_header=True, header_style="bold magenta")
    table.add_column("Step / Cycle", style="cyan")
    table.add_column("Evaluation Outcome", style="white")

    for log in result.get("logs", []):
        style = "green" if "PASSED" in log or "Verified" in log else "red" if "FAILED" in log else "yellow"
        table.add_row(log.split("]")[0] + "]", f"[{style}]{log}[/{style}]")

    console.print(table)
    console.print(Panel(result.get("code", ""), title=f"[bold green]Final Code ({result.get('status')})[/bold green]", subtitle="Python"))


def run_cli_resilience():
    console.print(Panel.fit("[bold green]Pattern 3: Resilience, Retries & Fallback Circuit[/bold green]"))
    endpoint_choice = Prompt.ask(
        "[yellow]Choose scenario[/yellow]",
        choices=["flaky", "down", "healthy"],
        default="flaky"
    )
    url_map = {
        "flaky": "https://api.internal/flaky_telemetry",
        "down": "https://api.internal/down_service",
        "healthy": "https://api.internal/healthy_telemetry"
    }

    app = build_resilience_graph()
    with console.status("[bold blue]Executing resilient retry graph...[/bold blue]"):
        result = app.invoke({
            "endpoint": url_map[endpoint_choice],
            "max_retries": 3,
            "attempt": 0,
            "failures_encountered": [],
            "execution_trace": []
        })

    table = Table(title="Resilience Telemetry", show_header=True, header_style="bold magenta")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="white")
    table.add_row("Target Endpoint", url_map[endpoint_choice])
    table.add_row("Total Attempts", str(result.get("attempt", 0)))
    table.add_row("Fallback Activated", f"[bold]{result.get('fallback_used')}[/bold]")
    table.add_row("Circuit State", f"[bold yellow]{result.get('circuit_state')}[/bold yellow]")
    console.print(table)

    console.print("\n[bold]Execution Trace:[/bold]")
    for step in result.get("execution_trace", []):
        color = "green" if "Succeeded" in step or "Success" in step else "red" if "Failed" in step or "Tripped" in step else "white"
        console.print(f"  [{color}]{step}[/{color}]")


def run_cli_hitl():
    console.print(Panel.fit("[bold green]Pattern 4: Human-in-the-Loop Checkpoints & Resumption[/bold green]"))
    checkpointer = MemorySaver()
    app = build_hitl_graph(checkpointer=checkpointer)
    thread_id = f"cli-thread-{int(time.time())}"
    config = {"configurable": {"thread_id": thread_id}}

    console.print(f"[cyan]Initializing workflow thread: {thread_id}...[/cyan]")
    res1 = app.invoke({
        "draft_title": "Production Kubernetes Zero-Downtime Migration Spec",
        "draft_body": "Migrate ingress controllers to Cilium eBPF mesh. Drain nodes in rack B-12.",
        "risk_level": "HIGH",
        "audit_trail": []
    }, config=config)

    state_snap = app.get_state(config)
    if state_snap.next and "human_review_checkpoint" in state_snap.next:
        interrupt_val = state_snap.tasks[0].interrupts[0].value
        console.print(Panel(
            f"[bold red]INTERRUPT TRIGGERED - CHECKPOINT REACHED[/bold red]\n\n"
            f"Draft: {interrupt_val.get('draft_title')}\n"
            f"Risk Level: {interrupt_val.get('risk_level')}\n"
            f"Content: {interrupt_val.get('draft_body')}\n"
            f"Safety Notes: {interrupt_val.get('safety_notes')}",
            title="Human Review Gate",
            border_style="red"
        ))

        action = Prompt.ask("[yellow]Reviewer Action[/yellow]", choices=["approve", "edit", "reject"], default="approve")
        feedback = Prompt.ask("[yellow]Reviewer Feedback[/yellow]", default="Approved after engineering review")
        edited = None
        if action == "edit":
            edited = Prompt.ask("[yellow]Enter Edited Content[/yellow]", default="Migrate ingress controllers with canary traffic splitting (10% -> 50% -> 100%).")

        console.print("[cyan]Resuming paused thread via Command(resume=...)[/cyan]")
        res2 = app.invoke(Command(resume={
            "action": action,
            "feedback": feedback,
            "edited_content": edited,
            "reviewed_by": "lead.architect@enterprise.internal"
        }), config=config)

        console.print(Panel(
            f"Status: {res2.get('status')}\n\n" + str(res2.get("published_output")),
            title="Workflow Resumption Outcome",
            border_style="green"
        ))


def run_cli_enterprise():
    console.print(Panel.fit("[bold green]Flagship: Autonomous Enterprise Release Pipeline[/bold green]"))
    ticket = Prompt.ask("[yellow]Ticket ID[/yellow]", default="SEC-4091")
    req = Prompt.ask("[yellow]Requirement[/yellow]", default="Implement secure token moving average algorithm with zero-trust validation.")

    checkpointer = MemorySaver()
    app = build_enterprise_pipeline(checkpointer=checkpointer)
    config = {"configurable": {"thread_id": f"ticket-{ticket}"}}

    console.print("\n[cyan]Starting Enterprise Pipeline...[/cyan]")
    app.invoke({
        "ticket_id": ticket,
        "requirement": req,
        "max_correction_cycles": 3,
        "correction_cycles": 0,
        "pipeline_trace": []
    }, config=config)

    snap = app.get_state(config)
    if snap.next and "human_governance_checkpoint" in snap.next:
        interrupt_val = snap.tasks[0].interrupts[0].value
        console.print(Panel(
            f"[bold yellow]HITL GOVERNANCE GATE REACHED[/bold yellow]\n"
            f"Ticket: {interrupt_val.get('ticket_id')} (Tier: {interrupt_val.get('risk_tier')})\n"
            f"Cycles: {interrupt_val.get('correction_cycles')} self-correction passes completed.\n"
            f"Tests: {interrupt_val.get('evaluator_feedback', {}).get('critique')}",
            title="Security Sign-off Required"
        ))

        action = Prompt.ask("[yellow]Governance Decision[/yellow]", choices=["approve", "reject"], default="approve")
        resumed = app.invoke(Command(resume={
            "action": action,
            "feedback": f"Executive approval granted by SecOps lead via CLI.",
            "reviewed_by": "secops-director@enterprise.internal"
        }), config=config)

        console.print(Panel(resumed.get("release_notes", ""), title="Final Release Manifest", border_style="green"))


def main():
    print_banner()
    while True:
        console.print("\n[bold]Select an Orchestration Pattern to Execute:[/bold]")
        console.print("  [1] Dynamic Branching & Conditional Routing")
        console.print("  [2] Self-Correction & Evaluator-Optimizer Loop")
        console.print("  [3] Resilience, Retries & Fallback Circuit")
        console.print("  [4] Human-in-the-Loop Checkpoints & Time-Travel")
        console.print("  [5] Hierarchical Supervisor Multi-Agent")
        console.print("  [6] Flagship End-to-End Enterprise Release Pipeline")
        console.print("  [0] Exit")

        choice = Prompt.ask("\nEnter choice", choices=["0", "1", "2", "3", "4", "5", "6"], default="6")
        if choice == "0":
            console.print("[cyan]Exiting StateCraft. Happy coding![/cyan]")
            break
        elif choice == "1":
            run_cli_branching()
        elif choice == "2":
            run_cli_self_correction()
        elif choice == "3":
            run_cli_resilience()
        elif choice == "4":
            run_cli_hitl()
        elif choice == "5":
            from statecraft.patterns.hierarchical_supervisor import build_supervisor_graph
            app = build_supervisor_graph()
            res = app.invoke({
                "objective": "Zero-Trust API Gateway Token Deserialization Security Hardening",
                "worker_outputs": {},
                "completed_subtasks": [],
                "supervisor_notes": [],
                "iterations": 0,
                "max_iterations": 10
            })
            console.print(Panel(res.get("final_synthesis", ""), title="Supervisor Synthesis"))
        elif choice == "6":
            run_cli_enterprise()


if __name__ == "__main__":
    main()
