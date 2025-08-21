#!/usr/bin/env python3
"""
Dataverse CLI Commands
Command-line interface for Dataverse operations
"""

import asyncio
import typer
from typing import Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

from dataverse.operations import dataverse_operations

console = Console()
app = typer.Typer(name="dataverse", help="Dataverse operations")

# ============================================================================
# TABLE OPERATIONS
# ============================================================================

@app.command()
def tables(
    action: str = typer.Argument(..., help="Action: list, schema, count"),
    table_name: Optional[str] = typer.Argument(None, help="Table name for schema/count")
):
    """Table discovery and schema operations"""
    
    async def run_tables():
        if action == "list":
            console.print("[bold blue]📋 Listing all tables...[/bold blue]")
            
            try:
                tables = await dataverse_operations.list_tables()
                
                # Create table
                table = Table(title="Dataverse Tables")
                table.add_column("Name", style="cyan")
                table.add_column("Display Name", style="green")
                table.add_column("Row Count", style="yellow")
                table.add_column("Custom", style="magenta")
                table.add_column("Description", style="white")
                
                for t in tables:
                    table.add_row(
                        t['name'],
                        t['display_name'],
                        str(t['row_count']),
                        "Yes" if t['is_custom'] else "No",
                        t['description'][:50] + "..." if len(t['description']) > 50 else t['description']
                    )
                
                console.print(table)
                console.print(f"[green]✅ Found {len(tables)} tables[/green]")
                
            except Exception as e:
                console.print(f"[red]❌ Error listing tables: {str(e)}[/red]")
                raise typer.Exit(1)
        
        elif action == "schema":
            if not table_name:
                console.print("[red]❌ Table name required for schema action[/red]")
                raise typer.Exit(1)
            
            console.print(f"[bold blue]🔍 Getting schema for table: {table_name}[/bold blue]")
            
            try:
                schema = await dataverse_operations.get_table_schema(table_name)
                
                # Create table for columns
                table = Table(title=f"Schema for {table_name}")
                table.add_column("Column", style="cyan")
                table.add_column("Type", style="green")
                table.add_column("Required", style="yellow")
                table.add_column("Description", style="white")
                
                for column in schema.get('columns', []):
                    table.add_row(
                        column.get('name', ''),
                        column.get('type', ''),
                        "Yes" if column.get('required', False) else "No",
                        column.get('description', '')[:50] + "..." if len(column.get('description', '')) > 50 else column.get('description', '')
                    )
                
                console.print(table)
                console.print(f"[green]✅ Schema retrieved with {len(schema.get('columns', []))} columns[/green]")
                
            except Exception as e:
                console.print(f"[red]❌ Error getting schema: {str(e)}[/red]")
                raise typer.Exit(1)
        
        elif action == "count":
            if not table_name:
                console.print("[red]❌ Table name required for count action[/red]")
                raise typer.Exit(1)
            
            console.print(f"[bold blue]📊 Getting row count for table: {table_name}[/bold blue]")
            
            try:
                count = await dataverse_operations.get_table_count(table_name)
                console.print(f"[green]✅ Table {table_name} has {count:,} rows[/green]")
                
            except Exception as e:
                console.print(f"[red]❌ Error getting count: {str(e)}[/red]")
                raise typer.Exit(1)
        
        else:
            console.print(f"[red]❌ Unknown action: {action}[/red]")
            console.print("Available actions: list, schema, count")
            raise typer.Exit(1)
    
    asyncio.run(run_tables())

# ============================================================================
# CLIENT OPERATIONS
# ============================================================================

@app.command()
def clients(
    action: str = typer.Argument(..., help="Action: list, search, details, stats"),
    query: Optional[str] = typer.Argument(None, help="Search query or client ID"),
    limit: int = typer.Option(50, "--limit", "-l", help="Limit results")
):
    """Client/Contact operations"""
    
    async def run_clients():
        if action == "list":
            console.print("[bold blue]👥 Listing clients...[/bold blue]")
            
            try:
                clients = await dataverse_operations.list_clients(limit=limit)
                
                # Create table
                table = Table(title=f"Clients (showing {len(clients)})")
                table.add_column("ID", style="cyan")
                table.add_column("Type", style="green")
                table.add_column("Name", style="yellow")
                table.add_column("Email", style="white")
                table.add_column("Phone", style="magenta")
                table.add_column("Location", style="blue")
                
                for client in clients:
                    location = f"{client.get('city', '')}, {client.get('state', '')}".strip(', ')
                    table.add_row(
                        client['id'][:8] + "...",
                        client['type'].title(),
                        client['name'][:30] + "..." if len(client['name']) > 30 else client['name'],
                        client.get('email', '')[:25] + "..." if len(client.get('email', '')) > 25 else client.get('email', ''),
                        client.get('phone', '')[:15] + "..." if len(client.get('phone', '')) > 15 else client.get('phone', ''),
                        location[:20] + "..." if len(location) > 20 else location
                    )
                
                console.print(table)
                console.print(f"[green]✅ Found {len(clients)} clients[/green]")
                
            except Exception as e:
                console.print(f"[red]❌ Error listing clients: {str(e)}[/red]")
                raise typer.Exit(1)
        
        elif action == "search":
            if not query:
                console.print("[red]❌ Search query required[/red]")
                raise typer.Exit(1)
            
            console.print(f"[bold blue]🔍 Searching clients for: {query}[/bold blue]")
            
            try:
                results = await dataverse_operations.search_clients(query, limit=limit)
                
                # Create table
                table = Table(title=f"Search Results for '{query}' (showing {len(results)})")
                table.add_column("ID", style="cyan")
                table.add_column("Type", style="green")
                table.add_column("Name", style="yellow")
                table.add_column("Email", style="white")
                table.add_column("Phone", style="magenta")
                table.add_column("Location", style="blue")
                
                for client in results:
                    location = f"{client.get('city', '')}, {client.get('state', '')}".strip(', ')
                    table.add_row(
                        client['id'][:8] + "...",
                        client['type'].title(),
                        client['name'][:30] + "..." if len(client['name']) > 30 else client['name'],
                        client.get('email', '')[:25] + "..." if len(client.get('email', '')) > 25 else client.get('email', ''),
                        client.get('phone', '')[:15] + "..." if len(client.get('phone', '')) > 15 else client.get('phone', ''),
                        location[:20] + "..." if len(location) > 20 else location
                    )
                
                console.print(table)
                console.print(f"[green]✅ Found {len(results)} matching clients[/green]")
                
            except Exception as e:
                console.print(f"[red]❌ Error searching clients: {str(e)}[/red]")
                raise typer.Exit(1)
        
        elif action == "details":
            if not query:
                console.print("[red]❌ Client ID required[/red]")
                raise typer.Exit(1)
            
            console.print(f"[bold blue]👤 Getting client details for: {query}[/bold blue]")
            
            try:
                client = await dataverse_operations.get_client_details(query)
                
                if client:
                    # Create detailed view
                    data = client['data']
                    client_type = client['type'].title()
                    
                    panel = Panel(
                        f"[bold]{client_type} Details[/bold]\n\n"
                        f"ID: {data.get('accountid') or data.get('contactid')}\n"
                        f"Name: {data.get('name') or f'{data.get('firstname', '')} {data.get('lastname', '')}'.strip()}\n"
                        f"Email: {data.get('emailaddress1', 'N/A')}\n"
                        f"Phone: {data.get('telephone1', 'N/A')}\n"
                        f"Address: {data.get('address1_line1', 'N/A')}\n"
                        f"City: {data.get('address1_city', 'N/A')}\n"
                        f"State: {data.get('address1_stateorprovince', 'N/A')}\n"
                        f"Status: {data.get('statuscode', 'N/A')}\n"
                        f"Created: {data.get('createdon', 'N/A')}\n"
                        f"Modified: {data.get('modifiedon', 'N/A')}",
                        title=f"{client_type} Information",
                        border_style="green"
                    )
                    console.print(panel)
                else:
                    console.print(f"[yellow]⚠️ Client not found: {query}[/yellow]")
                
            except Exception as e:
                console.print(f"[red]❌ Error getting client details: {str(e)}[/red]")
                raise typer.Exit(1)
        
        elif action == "stats":
            console.print("[bold blue]📊 Getting client statistics...[/bold blue]")
            
            try:
                stats = await dataverse_operations.get_client_statistics()
                
                # Create statistics panel
                panel = Panel(
                    f"[bold]Client Statistics[/bold]\n\n"
                    f"Total Clients: {stats['total_clients']:,}\n"
                    f"Total Accounts: {stats['total_accounts']:,}\n"
                    f"Total Contacts: {stats['total_contacts']:,}\n\n"
                    f"[bold]Account Statuses:[/bold]\n" + 
                    "\n".join([f"  {status}: {count:,}" for status, count in stats['account_statuses'].items()]) + "\n\n"
                    f"[bold]Contact Statuses:[/bold]\n" + 
                    "\n".join([f"  {status}: {count:,}" for status, count in stats['contact_statuses'].items()]),
                    title="Client Analytics",
                    border_style="blue"
                )
                console.print(panel)
                
            except Exception as e:
                console.print(f"[red]❌ Error getting client statistics: {str(e)}[/red]")
                raise typer.Exit(1)
        
        else:
            console.print(f"[red]❌ Unknown action: {action}[/red]")
            console.print("Available actions: list, search, details, stats")
            raise typer.Exit(1)
    
    asyncio.run(run_clients())

# ============================================================================
# SESSION OPERATIONS
# ============================================================================

@app.command()
def sessions(
    action: str = typer.Argument(..., help="Action: list, details, stats"),
    session_id: Optional[str] = typer.Argument(None, help="Session ID for details"),
    limit: int = typer.Option(50, "--limit", "-l", help="Limit results")
):
    """Session/Appointment operations"""
    
    async def run_sessions():
        if action == "list":
            console.print("[bold blue]📅 Listing sessions...[/bold blue]")
            
            try:
                sessions = await dataverse_operations.list_sessions(limit=limit)
                
                # Create table
                table = Table(title=f"Sessions (showing {len(sessions)})")
                table.add_column("ID", style="cyan")
                table.add_column("Subject", style="yellow")
                table.add_column("Start Time", style="green")
                table.add_column("End Time", style="green")
                table.add_column("Status", style="magenta")
                table.add_column("Location", style="blue")
                
                for session in sessions:
                    table.add_row(
                        session['appointmentid'][:8] + "...",
                        session.get('subject', '')[:30] + "..." if len(session.get('subject', '')) > 30 else session.get('subject', ''),
                        str(session.get('starttime', ''))[:19] if session.get('starttime') else 'N/A',
                        str(session.get('endtime', ''))[:19] if session.get('endtime') else 'N/A',
                        str(session.get('statuscode', 'N/A')),
                        session.get('location', '')[:20] + "..." if len(session.get('location', '')) > 20 else session.get('location', '')
                    )
                
                console.print(table)
                console.print(f"[green]✅ Found {len(sessions)} sessions[/green]")
                
            except Exception as e:
                console.print(f"[red]❌ Error listing sessions: {str(e)}[/red]")
                raise typer.Exit(1)
        
        elif action == "details":
            if not session_id:
                console.print("[red]❌ Session ID required[/red]")
                raise typer.Exit(1)
            
            console.print(f"[bold blue]📅 Getting session details for: {session_id}[/bold blue]")
            
            try:
                session = await dataverse_operations.get_session_details(session_id)
                
                if session:
                    # Create detailed view
                    panel = Panel(
                        f"[bold]Session Details[/bold]\n\n"
                        f"ID: {session.get('appointmentid')}\n"
                        f"Subject: {session.get('subject', 'N/A')}\n"
                        f"Start Time: {session.get('starttime', 'N/A')}\n"
                        f"End Time: {session.get('endtime', 'N/A')}\n"
                        f"Status: {session.get('statuscode', 'N/A')}\n"
                        f"Location: {session.get('location', 'N/A')}\n"
                        f"Description: {session.get('description', 'N/A')[:100]}...\n"
                        f"Created: {session.get('createdon', 'N/A')}\n"
                        f"Modified: {session.get('modifiedon', 'N/A')}",
                        title="Session Information",
                        border_style="green"
                    )
                    console.print(panel)
                else:
                    console.print(f"[yellow]⚠️ Session not found: {session_id}[/yellow]")
                
            except Exception as e:
                console.print(f"[red]❌ Error getting session details: {str(e)}[/red]")
                raise typer.Exit(1)
        
        elif action == "stats":
            console.print("[bold blue]📊 Getting session statistics...[/bold blue]")
            
            try:
                stats = await dataverse_operations.get_session_statistics()
                
                # Create statistics panel
                panel = Panel(
                    f"[bold]Session Statistics[/bold]\n\n"
                    f"Total Sessions: {stats['total_sessions']:,}\n"
                    f"Recent Sessions (2024): {stats['recent_sessions']:,}\n\n"
                    f"[bold]Status Breakdown:[/bold]\n" + 
                    "\n".join([f"  {status}: {count:,}" for status, count in stats['status_breakdown'].items()]),
                    title="Session Analytics",
                    border_style="blue"
                )
                console.print(panel)
                
            except Exception as e:
                console.print(f"[red]❌ Error getting session statistics: {str(e)}[/red]")
                raise typer.Exit(1)
        
        else:
            console.print(f"[red]❌ Unknown action: {action}[/red]")
            console.print("Available actions: list, details, stats")
            raise typer.Exit(1)
    
    asyncio.run(run_sessions())

# ============================================================================
# MESSAGE OPERATIONS
# ============================================================================

@app.command()
def messages(
    action: str = typer.Argument(..., help="Action: list, logs, stats"),
    limit: int = typer.Option(50, "--limit", "-l", help="Limit results")
):
    """Message operations"""
    
    async def run_messages():
        if action == "list":
            console.print("[bold blue]📧 Listing scheduled messages...[/bold blue]")
            
            try:
                messages = await dataverse_operations.list_scheduled_messages(limit=limit)
                
                # Create table
                table = Table(title=f"Scheduled Messages (showing {len(messages)})")
                table.add_column("ID", style="cyan")
                table.add_column("Client", style="yellow")
                table.add_column("Email", style="white")
                table.add_column("Subject", style="green")
                table.add_column("Type", style="magenta")
                table.add_column("Status", style="blue")
                table.add_column("Scheduled", style="cyan")
                table.add_column("Sent", style="green")
                
                for message in messages:
                    table.add_row(
                        message.get('MessageID', '')[:8] + "...",
                        message.get('ClientName', '')[:20] + "..." if len(message.get('ClientName', '')) > 20 else message.get('ClientName', ''),
                        message.get('Email', '')[:25] + "..." if len(message.get('Email', '')) > 25 else message.get('Email', ''),
                        message.get('MessageSubject', '')[:30] + "..." if len(message.get('MessageSubject', '')) > 30 else message.get('MessageSubject', ''),
                        message.get('MessageType', 'N/A'),
                        str(message.get('MessageStatus', 'N/A')),
                        str(message.get('ScheduledTimestamp', ''))[:19] if message.get('ScheduledTimestamp') else 'N/A',
                        "Yes" if message.get('Sent') else "No"
                    )
                
                console.print(table)
                console.print(f"[green]✅ Found {len(messages)} scheduled messages[/green]")
                
            except Exception as e:
                console.print(f"[red]❌ Error listing messages: {str(e)}[/red]")
                raise typer.Exit(1)
        
        elif action == "logs":
            console.print("[bold blue]📋 Listing message logs...[/bold blue]")
            
            try:
                logs = await dataverse_operations.get_message_logs(limit=limit)
                
                # Create table
                table = Table(title=f"Message Logs (showing {len(logs)})")
                table.add_column("ID", style="cyan")
                table.add_column("Message ID", style="yellow")
                table.add_column("Type", style="magenta")
                table.add_column("Recipient", style="white")
                table.add_column("Subject", style="green")
                table.add_column("Provider", style="blue")
                table.add_column("Status", style="cyan")
                table.add_column("Created", style="green")
                
                for log in logs:
                    table.add_row(
                        str(log.get('id', ''))[:8] + "...",
                        log.get('message_id', '')[:8] + "...",
                        log.get('message_type', 'N/A'),
                        log.get('recipient', '')[:25] + "..." if len(log.get('recipient', '')) > 25 else log.get('recipient', ''),
                        log.get('subject', '')[:30] + "..." if len(log.get('subject', '')) > 30 else log.get('subject', ''),
                        log.get('provider', 'N/A'),
                        log.get('status', 'N/A'),
                        str(log.get('created_at', ''))[:19] if log.get('created_at') else 'N/A'
                    )
                
                console.print(table)
                console.print(f"[green]✅ Found {len(logs)} message logs[/green]")
                
            except Exception as e:
                console.print(f"[red]❌ Error listing message logs: {str(e)}[/red]")
                raise typer.Exit(1)
        
        elif action == "stats":
            console.print("[bold blue]📊 Getting message statistics...[/bold blue]")
            
            try:
                stats = await dataverse_operations.get_message_statistics()
                
                # Create statistics panel
                panel = Panel(
                    f"[bold]Message Statistics[/bold]\n\n"
                    f"Total Scheduled: {stats['total_scheduled']:,}\n"
                    f"Total Sent: {stats['total_sent']:,}\n"
                    f"Total Failed: {stats['total_failed']:,}\n\n"
                    f"[bold]Status Breakdown:[/bold]\n" + 
                    "\n".join([f"  {status}: {count:,}" for status, count in stats['status_breakdown'].items()]),
                    title="Message Analytics",
                    border_style="blue"
                )
                console.print(panel)
                
            except Exception as e:
                console.print(f"[red]❌ Error getting message statistics: {str(e)}[/red]")
                raise typer.Exit(1)
        
        else:
            console.print(f"[red]❌ Unknown action: {action}[/red]")
            console.print("Available actions: list, logs, stats")
            raise typer.Exit(1)
    
    asyncio.run(run_messages())

if __name__ == "__main__":
    app()
