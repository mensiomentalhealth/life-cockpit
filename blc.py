#!/usr/bin/env python3
"""
Life Cockpit CLI - Main entry point for automation commands.

Usage:
    python blc.py auth test
    python blc.py dataverse list
    python blc.py graph users
"""

import asyncio
import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from auth.graph import get_auth_manager
from dataverse.list_tables import get_dataverse_tables
from utils.config import get_config
from utils.logger import get_logger, setup_logging

# Initialize Typer app
app = typer.Typer(
    name="blc",
    help="Life Cockpit - Microsoft 365 Automation CLI",
    add_completion=False,
    rich_markup_mode="rich"
)

# Initialize console for rich output
console = Console()
logger = get_logger(__name__)


@app.command()
def version():
    """Show Life Cockpit version."""
    config = get_config()
    console.print(Panel(
        f"[bold blue]Life Cockpit[/bold blue] v{config.app_version}\n"
        f"Microsoft 365 Automation Framework",
        title="🚀 Life Cockpit"
    ))


@app.command()
def auth(
    action: str = typer.Argument(..., help="Action to perform: test, status")
):
    """Authentication management commands."""
    
    async def run_auth():
        setup_logging(log_level="INFO")
        
        if action == "test":
            console.print("[bold]Testing Microsoft Graph API authentication...[/bold]")
            auth_manager = get_auth_manager()
            
            # Test basic authentication
            basic_success = await auth_manager.test_basic_auth()
            if basic_success:
                console.print("✅ [green]Basic authentication successful![/green]")
                
                # Test API access
                api_success = await auth_manager.test_connection()
                if api_success:
                    console.print("🎉 [green]Full authentication and API test completed successfully![/green]")
                else:
                    console.print("⚠️ [yellow]Authentication works but API access needs permissions[/yellow]")
            else:
                console.print("❌ [red]Basic authentication failed![/red]")
                raise typer.Exit(1)
                
        elif action == "status":
            console.print("[bold]Checking authentication status...[/bold]")
            auth_manager = get_auth_manager()
            
            try:
                # Get token info
                credential = auth_manager._credential
                token = credential.get_token("https://graph.microsoft.com/.default")
                
                console.print(f"✅ [green]Token acquired successfully[/green]")
                console.print(f"   Expires: {token.expires_on}")
                console.print(f"   Scope: https://graph.microsoft.com/.default")
                
            except Exception as e:
                console.print(f"❌ [red]Authentication error: {e}[/red]")
                raise typer.Exit(1)
        else:
            console.print(f"❌ [red]Unknown action: {action}[/red]")
            console.print("Available actions: test, status")
            raise typer.Exit(1)
    
    asyncio.run(run_auth())


@app.command()
def dataverse(
    action: str = typer.Argument(..., help="Action to perform: list, test, whoami")
):
    """Dataverse operations."""
    
    async def run_dataverse():
        setup_logging(log_level="INFO")
        
        if action == "list":
            console.print("[bold]Fetching Dataverse tables...[/bold]")
            
            from dataverse.list_tables import list_dataverse_tables
            success = await list_dataverse_tables()
            if not success:
                console.print("❌ [red]Failed to list Dataverse tables[/red]")
                raise typer.Exit(1)
                
        elif action == "test":
            console.print("[bold]Testing Dataverse connection...[/bold]")
            
            from dataverse.list_tables import test_dataverse_connection
            success = await test_dataverse_connection()
            if success:
                console.print("✅ [green]Dataverse connection successful![/green]")
            else:
                console.print("❌ [red]Dataverse connection failed[/red]")
                raise typer.Exit(1)
                
        elif action == "whoami":
            console.print("[bold]Getting Dataverse user info...[/bold]")
            
            from dataverse.list_tables import test_dataverse_connection
            success = await test_dataverse_connection()
            if not success:
                console.print("❌ [red]Failed to get Dataverse user info[/red]")
                raise typer.Exit(1)
        else:
            console.print(f"❌ [red]Unknown action: {action}[/red]")
            console.print("Available actions: list, test, whoami")
            raise typer.Exit(1)
    
    asyncio.run(run_dataverse())


@app.command()
def graph(
    action: str = typer.Argument(..., help="Action to perform: users, org")
):
    """Microsoft Graph API operations."""
    
    async def run_graph():
        setup_logging(log_level="INFO")
        
        if action == "users":
            console.print("[bold]Fetching users from Microsoft Graph...[/bold]")
            
            auth_manager = get_auth_manager()
            if not await auth_manager.test_connection():
                console.print("❌ [red]Graph API authentication failed![/red]")
                raise typer.Exit(1)
            
            try:
                client = auth_manager.get_client()
                users = await client.users.get()
                
                if users and users.value:
                    console.print(f"👥 [green]Found {len(users.value)} users:[/green]")
                    for user in users.value[:10]:  # Show first 10
                        console.print(f"  • {user.display_name} ({user.user_principal_name})")
                    if len(users.value) > 10:
                        console.print(f"  ... and {len(users.value) - 10} more")
                else:
                    console.print("⚠️ [yellow]No users found[/yellow]")
                    
            except Exception as e:
                console.print(f"❌ [red]Error fetching users: {e}[/red]")
                raise typer.Exit(1)
                
        elif action == "org":
            console.print("[bold]Fetching organization info from Microsoft Graph...[/bold]")
            
            auth_manager = get_auth_manager()
            if not await auth_manager.test_connection():
                console.print("❌ [red]Graph API authentication failed![/red]")
                raise typer.Exit(1)
            
            try:
                client = auth_manager.get_client()
                org = await client.organization.get()
                
                if org and org.value:
                    org_info = org.value[0]
                    console.print(f"🏢 [green]Organization: {org_info.display_name}[/green]")
                    console.print(f"   ID: {org_info.id}")
                    if hasattr(org_info, 'business_phones') and org_info.business_phones:
                        console.print(f"   Phone: {org_info.business_phones[0]}")
                else:
                    console.print("⚠️ [yellow]No organization info found[/yellow]")
                    
            except Exception as e:
                console.print(f"❌ [red]Error fetching organization: {e}[/red]")
                raise typer.Exit(1)
        else:
            console.print(f"❌ [red]Unknown action: {action}[/red]")
            console.print("Available actions: users, org")
            raise typer.Exit(1)
    
    asyncio.run(run_graph())


@app.command()
def rollback(
    action: str = typer.Argument(..., help="Action to perform: list, create, execute")
):
    """Rollback management operations."""
    
    from utils.rollback import get_rollback_manager
    
    rollback_manager = get_rollback_manager()
    
    if action == "list":
        console.print("[bold]Rollback Points:[/bold]")
        points = rollback_manager.list_points()
        
        if not points:
            console.print("No rollback points found")
            return
        
        for point_id, point_data in points.items():
            console.print(f"  • {point_id}")
            console.print(f"    Operation: {point_data['operation']}")
            console.print(f"    Description: {point_data['description']}")
            console.print(f"    Timestamp: {point_data['timestamp']}")
            console.print()
    
    elif action == "create":
        console.print("[bold]Creating rollback point...[/bold]")
        # This would be used programmatically, not from CLI
        console.print("Rollback points are created automatically during operations")
    
    elif action == "execute":
        console.print("[bold]Rollback execution...[/bold]")
        # This would be used programmatically, not from CLI
        console.print("Rollback execution is handled automatically on failures")
    
    else:
        console.print(f"❌ [red]Unknown action: {action}[/red]")
        console.print("Available actions: list, create, execute")
        raise typer.Exit(1)

@app.command()
def guardrails(
    action: str = typer.Argument(..., help="Action to perform: list, approve, status")
):
    """Safety guardrails management."""
    
    from utils.guardrails import list_runs, approve_run, get_run_status
    
    if action == "list":
        console.print("[bold]Active Runs:[/bold]")
        runs = list_runs()
        
        if not runs:
            console.print("No active runs found")
            return
        
        for run_id, run_data in runs.items():
            status_color = "green" if run_data.get('status') == 'completed' else "yellow"
            console.print(f"  • {run_id}")
            console.print(f"    Operation: {run_data['operation']}")
            console.print(f"    Classification: {run_data['classification']}")
            console.print(f"    Status: [{status_color}]{run_data.get('status', 'unknown')}[/{status_color}]")
            console.print(f"    Created: {run_data['created_at']}")
            console.print()
    
    elif action == "approve":
        run_id = typer.prompt("Enter run ID to approve")
        success = approve_run(run_id)
        
        if success:
            console.print(f"✅ [green]Run {run_id} approved[/green]")
        else:
            console.print(f"❌ [red]Failed to approve run {run_id}[/red]")
    
    elif action == "status":
        run_id = typer.prompt("Enter run ID to check status")
        status = get_run_status(run_id)
        
        if status:
            console.print(f"[bold]Run Status: {run_id}[/bold]")
            console.print(f"  Operation: {status['operation']}")
            console.print(f"  Classification: {status['classification']}")
            console.print(f"  Status: {status.get('status', 'unknown')}")
            console.print(f"  Created: {status['created_at']}")
            if 'completed_at' in status:
                console.print(f"  Completed: {status['completed_at']}")
        else:
            console.print(f"❌ [red]Run {run_id} not found[/red]")
    
    else:
        console.print(f"❌ [red]Unknown action: {action}[/red]")
        console.print("Available actions: list, approve, status")
        raise typer.Exit(1)

@app.command()
def logic_apps(
    action: str = typer.Argument(..., help="Action to perform: list, create, delete")
):
    """Logic Apps workflow management."""
    
    async def run_logic_apps():
        from azure.logic_apps import logic_apps_cli
        
        if action == "list":
            console.print("[bold]Logic Apps Workflows:[/bold]")
            workflows = await logic_apps_cli.list_workflows()
            
            if not workflows:
                console.print("No Logic Apps workflows found")
                return
            
            for workflow in workflows:
                console.print(f"  • {workflow['name']}")
                console.print(f"    State: {workflow['state']}")
                console.print(f"    Location: {workflow['location']}")
                console.print()
        
        elif action == "create":
            workflow_type = typer.prompt("Workflow type", choices=["webhook", "email", "scheduled"])
            name = typer.prompt("Workflow name")
            function_url = typer.prompt("Azure Function URL")
            
            if workflow_type == "webhook":
                result = await logic_apps_cli.create_webhook_listener(name, function_url)
            elif workflow_type == "email":
                result = await logic_apps_cli.create_email_automation(name, function_url)
            elif workflow_type == "scheduled":
                schedule = typer.prompt("Schedule (cron format)", default="0 0 * * *")
                result = await logic_apps_cli.create_scheduled_task(name, function_url, schedule)
            
            console.print(f"✅ [green]Created Logic App: {name}[/green]")
        
        elif action == "delete":
            name = typer.prompt("Workflow name to delete")
            success = await logic_apps_cli.delete_workflow(name)
            
            if success:
                console.print(f"✅ [green]Deleted Logic App: {name}[/green]")
            else:
                console.print(f"❌ [red]Failed to delete Logic App: {name}[/red]")
        
        else:
            console.print(f"❌ [red]Unknown action: {action}[/red]")
            console.print("Available actions: list, create, delete")
            raise typer.Exit(1)
    
    asyncio.run(run_logic_apps())

@app.command()
def functions(
    action: str = typer.Argument(..., help="Action to perform: test-webhook, send-email, execute-task")
):
    """Azure Functions testing."""
    
    async def run_functions():
        from azure.functions import functions_manager
        from utils.guardrails import create_run_id, Classification
        
        if action == "test-webhook":
            entity = typer.prompt("Entity type", default="accounts")
            operation = typer.prompt("Operation", default="Create")
            run_id = create_run_id("test-webhook", Classification.BUSINESS)
            
            test_data = {"accountid": "test-123", "name": "Test Account"}
            result = await functions_manager.process_dataverse_webhook(entity, operation, test_data, run_id)
            
            console.print(f"✅ [green]Webhook test completed[/green]")
            console.print(f"Run ID: {run_id}")
            console.print(f"Result: {result}")
        
        elif action == "send-email":
            to = typer.prompt("Recipient email")
            subject = typer.prompt("Email subject")
            body = typer.prompt("Email body")
            run_id = create_run_id("send-email", Classification.BUSINESS)
            
            result = await functions_manager.send_email(to, subject, body, run_id=run_id)
            
            console.print(f"✅ [green]Email test completed[/green]")
            console.print(f"Run ID: {run_id}")
            console.print(f"Result: {result}")
        
        elif action == "execute-task":
            task = typer.prompt("Task to execute", default="daily_backup")
            run_id = create_run_id("execute-task", Classification.PERSONAL)
            
            result = await functions_manager.execute_scheduled_task(task, run_id)
            
            console.print(f"✅ [green]Task execution completed[/green]")
            console.print(f"Run ID: {run_id}")
            console.print(f"Result: {result}")
        
        elif action == "test-message-processor":
            from azure.message_processor import message_processor_cli
            
            console.print("[bold]Testing message processor...[/bold]")
            result = await message_processor_cli.test_processing()
            
            if result.get('success', False):
                console.print(f"✅ [green]Message processor test completed[/green]")
                console.print(f"Processed: {result.get('processed_count', 0)}")
                console.print(f"Success: {result.get('success_count', 0)}")
                console.print(f"Failed: {result.get('failed_count', 0)}")
                console.print(f"Run ID: {result.get('run_id', 'N/A')}")
            else:
                console.print(f"⚠️ [yellow]Message processor test requires approval[/yellow]")
                console.print(f"Error: {result.get('error', 'Unknown error')}")
                console.print(f"Run ID: {result.get('run_id', 'N/A')}")
                console.print("Use 'python blc.py guardrails approve' to approve the operation")
        
        elif action == "test-dynamics-processor":
            from azure.dynamics_message_processor import dynamics_message_processor_cli
            
            console.print("[bold]Testing Dynamics message processor...[/bold]")
            result = await dynamics_message_processor_cli.test_processing()
            
            if result.get('success', False):
                console.print(f"✅ [green]Dynamics message processor test completed[/green]")
                console.print(f"Processed: {result.get('processed_count', 0)}")
                console.print(f"Success: {result.get('success_count', 0)}")
                console.print(f"Failed: {result.get('failed_count', 0)}")
                console.print(f"Run ID: {result.get('run_id', 'N/A')}")
            else:
                console.print(f"⚠️ [yellow]Dynamics message processor test requires approval[/yellow]")
                console.print(f"Error: {result.get('error', 'Unknown error')}")
                console.print(f"Run ID: {result.get('run_id', 'N/A')}")
                console.print("Use 'python blc.py guardrails approve' to approve the operation")
        
        else:
            console.print(f"❌ [red]Unknown action: {action}[/red]")
            console.print("Available actions: test-webhook, send-email, execute-task, test-message-processor, test-dynamics-processor")
            raise typer.Exit(1)
    
    asyncio.run(run_functions())

@app.command()
def sandbox(
    action: str = typer.Argument(..., help="Action to perform: enable, disable, reset, export, import")
):
    """Local sandbox mode management."""
    
    async def run_sandbox():
        from utils.sandbox import sandbox_manager
        
        if action == "enable":
            os.environ["BLC_LOCAL_SANDBOX"] = "true"
            console.print("✅ [green]Sandbox mode enabled[/green]")
            console.print("All operations will use mock services")
        
        elif action == "disable":
            os.environ["BLC_LOCAL_SANDBOX"] = "false"
            console.print("✅ [green]Sandbox mode disabled[/green]")
            console.print("All operations will use real services")
        
        elif action == "reset":
            await sandbox_manager.reset_data()
            console.print("✅ [green]Sandbox data reset[/green]")
        
        elif action == "export":
            filepath = typer.prompt("Export file path", default="sandbox_data.json")
            await sandbox_manager.export_data(filepath)
            console.print(f"✅ [green]Sandbox data exported to {filepath}[/green]")
        
        elif action == "import":
            filepath = typer.prompt("Import file path")
            await sandbox_manager.import_data(filepath)
            console.print(f"✅ [green]Sandbox data imported from {filepath}[/green]")
        
        else:
            console.print(f"❌ [red]Unknown action: {action}[/red]")
            console.print("Available actions: enable, disable, reset, export, import")
            raise typer.Exit(1)
    
    asyncio.run(run_sandbox())

if __name__ == "__main__":
    app()
