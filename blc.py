#!/usr/bin/env python3
"""
Life Cockpit CLI - Main entry point for automation commands.

Usage:
    python blc.py auth test
    python blc.py dataverse list
    python blc.py graph users
"""

import asyncio
import os
import json
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
@app.command(name="templates")
def templates_cmd(
    action: str = typer.Argument(..., help="Action: list, render"),
    name: Optional[str] = typer.Argument(None, help="Template name (for render)"),
    data_file: Optional[str] = typer.Option(None, "--data-file", help="JSON file with render context"),
):
    """Templates management and rendering."""

    from utils.templates import discover_templates, load_template_by_name, render_template

    if action == "list":
        tpls = discover_templates()
        if not tpls:
            console.print("No templates found in templates/ directory")
            return
        console.print("[bold]Templates:[/bold]")
        for t in tpls:
            console.print(f"  • {t.meta.name} [dim]({t.rel_path})[/dim]  v{t.meta.version}  type={t.meta.type}")
        return

    elif action == "render":
        if not name:
            console.print("[red]❌ Template name required[/red]")
            raise typer.Exit(1)
        context = {}
        if data_file:
            with open(data_file, "r", encoding="utf-8") as f:
                context = json.load(f)
        tmpl = load_template_by_name(name)
        output = render_template(tmpl, context)
        console.print(Panel(output, title=f"Rendered: {name}", expand=True))
        return

    else:
        console.print(f"[red]❌ Unknown action: {action}[/red]")
        console.print("Available: list, render")
        raise typer.Exit(1)



@app.command()
def version():
    """Show Life Cockpit version."""
    config = get_config()
    console.print(Panel(
        f"[bold blue]Life Cockpit[/bold blue] v{config.app_version}\n"
        f"Microsoft 365 Automation Framework",
        title="🚀 Life Cockpit"
    ))
@app.command(name="config")
def config_cmd(
    action: str = typer.Argument(..., help="Action: check"),
):
    """Configuration inspection commands."""
    from utils.config import load_config
    load_config()  # ensure normalization
    if action == "check":
        console.print("[bold]Effective environment variables (sensitive values hidden):[/bold]")
        def mask(val: str | None) -> str:
            if not val:
                return "<unset>"
            return val[:3] + "***" if len(val) > 3 else "***"
        pairs = [
            ("AAD_CLIENT_ID", os.getenv("AAD_CLIENT_ID")),
            ("AAD_TENANT_ID", os.getenv("AAD_TENANT_ID")),
            ("AAD_CLIENT_SECRET", os.getenv("AAD_CLIENT_SECRET")),
            ("AZURE_CLIENT_ID", os.getenv("AZURE_CLIENT_ID")),
            ("AZURE_TENANT_ID", os.getenv("AZURE_TENANT_ID")),
            ("AZURE_CLIENT_SECRET", os.getenv("AZURE_CLIENT_SECRET")),
            ("DATAVERSE_URL", os.getenv("DATAVERSE_URL")),
        ]
        for k, v in pairs:
            console.print(f"  {k}: {mask(v)}")
    else:
        console.print(f"[red]❌ Unknown action: {action}[/red]")
        console.print("Available: check")
        raise typer.Exit(1)



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


@app.command(name="dataverse")
def dataverse(
    operation: str = typer.Argument(..., help="Operation: whoami, entity-def, get, query, create, update, delete, note, probe"),
    logical_name: Optional[str] = typer.Argument(None, help="Logical name"),
    record_id: Optional[str] = typer.Argument(None, help="Record ID (GUID)"),
    data_file: Optional[str] = typer.Option(None, "--data-file", help="JSON file with data"),
    select: Optional[str] = typer.Option(None, "--select", help="OData $select"),
    expand: Optional[str] = typer.Option(None, "--expand", help="OData $expand"),
    filter: Optional[str] = typer.Option(None, "--filter", help="OData $filter"),
    top: int = typer.Option(10, "--top", help="OData $top"),
    subject: Optional[str] = typer.Option(None, "--subject", help="Note subject"),
    body_file: Optional[str] = typer.Option(None, "--body-file", help="Note body file"),
    template: Optional[str] = typer.Option(None, "--template", help="Template name for note body (uses --data-file as context)"),
    as_user: Optional[str] = typer.Option(None, "--as-user", help="Impersonate user (systemuserid)"),
):
    """Basic Dataverse CRUD operations"""
    
    def run_dataverse():
        # Ensure config is loaded first
        from utils.config import load_config
        load_config()
        
        from dataverse.dev import whoami, entity_def, entity_set, get, query, create, update, delete, create_note, probe
        
        if operation == "probe":
            results = probe()
            console.print("🔍 [bold]Dataverse Connection Probe:[/bold]")
            for test, result in results.items():
                console.print(f"   {test}: {result}")
            return
            
        elif operation == "whoami":
            result = whoami(as_user)
            console.print(f"👤 [green]User Info:[/green]")
            console.print(f"   User ID: {result.get('UserId')}")
            console.print(f"   Business Unit ID: {result.get('BusinessUnitId')}")
            console.print(f"   Organization ID: {result.get('OrganizationId')}")
            
        elif operation == "entity-def":
            if not logical_name:
                console.print("[red]❌ Logical name required[/red]")
                raise typer.Exit(1)
            result = entity_def(logical_name)
            console.print(f"📋 [green]Entity Definition for {logical_name}:[/green]")
            console.print(f"   Entity Set: {result.get('EntitySetName')}")
            console.print(f"   Primary ID: {result.get('PrimaryIdAttribute')}")
            console.print(f"   Primary Name: {result.get('PrimaryNameAttribute')}")
            
        elif operation == "get":
            if not logical_name or not record_id:
                console.print("[red]❌ Logical name and record ID required[/red]")
                raise typer.Exit(1)
            entity_set_name = entity_set(logical_name)
            result = get(entity_set_name, record_id, select, expand)
            console.print(f"📄 [green]Record:[/green]")
            console.print(json.dumps(result, indent=2))
            
        elif operation == "query":
            if not logical_name:
                console.print("[red]❌ Logical name required[/red]")
                raise typer.Exit(1)
            entity_set_name = entity_set(logical_name)
            result = query(entity_set_name, filter, select, top)
            console.print(f"🔍 [green]Query Results:[/green]")
            console.print(f"   Count: {result.get('@odata.count', 'unknown')}")
            console.print(f"   Records: {len(result.get('value', []))}")
            for record in result.get('value', []):
                console.print(f"   • {record}")
                
        elif operation == "create":
            if not logical_name or not data_file:
                console.print("[red]❌ Logical name and data file required[/red]")
                raise typer.Exit(1)
            entity_set_name = entity_set(logical_name)
            with open(data_file, 'r') as f:
                payload = json.load(f)
            result = create(entity_set_name, payload, impersonate=as_user)
            console.print(f"✅ [green]Created record with ID: {result['id']}[/green]")
            
        elif operation == "update":
            if not logical_name or not record_id or not data_file:
                console.print("[red]❌ Logical name, record ID, and data file required[/red]")
                raise typer.Exit(1)
            entity_set_name = entity_set(logical_name)
            with open(data_file, 'r') as f:
                payload = json.load(f)
            update(entity_set_name, record_id, payload, impersonate=as_user)
            console.print(f"✅ [green]Updated record {record_id}[/green]")
            
        elif operation == "delete":
            if not logical_name or not record_id:
                console.print("[red]❌ Logical name and record ID required[/red]")
                raise typer.Exit(1)
            entity_set_name = entity_set(logical_name)
            delete(entity_set_name, record_id, impersonate=as_user)
            console.print(f"✅ [green]Deleted record {record_id}[/green]")
            
        elif operation == "note":
            if not logical_name or not record_id or not subject:
                console.print("[red]❌ Logical name, record ID, and subject required[/red]")
                raise typer.Exit(1)

            # Determine note body: template > body_file
            if template:
                try:
                    from utils.templates import load_template_by_name, render_template
                    ctx = {}
                    if data_file:
                        with open(data_file, 'r', encoding='utf-8') as df:
                            ctx = json.load(df)
                    tmpl = load_template_by_name(template)
                    notetext = render_template(tmpl, ctx)
                except Exception as e:
                    console.print(f"[red]❌ Template rendering failed: {e}[/red]")
                    raise typer.Exit(1)
            else:
                if not body_file:
                    console.print("[red]❌ Provide either --template or --body-file for note body[/red]")
                    raise typer.Exit(1)
                with open(body_file, 'r', encoding='utf-8') as f:
                    notetext = f.read()

            result = create_note(logical_name, record_id, subject, notetext, impersonate=as_user)
            console.print(f"📝 [green]Created note with ID: {result['id']}[/green]")
            
        else:
            console.print(f"[red]❌ Unknown operation: {operation}[/red]")
            console.print("Available operations: whoami, entity-def, get, query, create, update, delete, note, probe")
            raise typer.Exit(1)
    
    run_dataverse()


# Short alias: dv
@app.command(name="dv")
def dv(
    operation: str = typer.Argument(..., help="Alias of dataverse command"),
    logical_name: Optional[str] = typer.Argument(None),
    record_id: Optional[str] = typer.Argument(None),
    data_file: Optional[str] = typer.Option(None, "--data-file"),
    select: Optional[str] = typer.Option(None, "--select"),
    expand: Optional[str] = typer.Option(None, "--expand"),
    filter: Optional[str] = typer.Option(None, "--filter"),
    top: int = typer.Option(10, "--top"),
    subject: Optional[str] = typer.Option(None, "--subject"),
    body_file: Optional[str] = typer.Option(None, "--body-file"),
    as_user: Optional[str] = typer.Option(None, "--as-user"),
):
    """Alias for dataverse command."""
    return dataverse(
        operation=operation,
        logical_name=logical_name,
        record_id=record_id,
        data_file=data_file,
        select=select,
        expand=expand,
        filter=filter,
        top=top,
        subject=subject,
        body_file=body_file,
        as_user=as_user,
    )


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
