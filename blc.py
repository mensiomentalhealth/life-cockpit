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


if __name__ == "__main__":
    app()
