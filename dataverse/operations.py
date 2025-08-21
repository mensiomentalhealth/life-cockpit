#!/usr/bin/env python3
"""
Dataverse Operations Module
Real environment read-only operations for Dynamics/Dataverse
"""

import asyncio
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import structlog

from dataverse.client import get_dataverse_client

logger = structlog.get_logger(__name__)

class DataverseOperations:
    """Core Dataverse operations for real environment"""
    
    def __init__(self):
        """Initialize with real Dataverse environment"""
        self.client = get_dataverse_client()
        self.environment = os.environ.get('ENVIRONMENT', 'production')
        
        logger.info("Dataverse operations initialized", 
                   environment=self.environment)
    
    # ============================================================================
    # TABLE DISCOVERY & SCHEMA
    # ============================================================================
    
    async def list_tables(self) -> List[Dict[str, Any]]:
        """List all available tables in the environment"""
        try:
            logger.info("Listing all tables")
            
            # Get all tables
            tables = await self.client.list_tables()
            
            # Get row counts for each table
            table_info = []
            for table in tables:
                try:
                    count = await self.get_table_count(table['name'])
                    table_info.append({
                        'name': table['name'],
                        'display_name': table.get('display_name', table['name']),
                        'description': table.get('description', ''),
                        'row_count': count,
                        'is_custom': table.get('is_custom', False)
                    })
                except Exception as e:
                    logger.warning("Could not get count for table", 
                                 table=table['name'], error=str(e))
                    table_info.append({
                        'name': table['name'],
                        'display_name': table.get('display_name', table['name']),
                        'description': table.get('description', ''),
                        'row_count': 'unknown',
                        'is_custom': table.get('is_custom', False)
                    })
            
            logger.info("Tables listed successfully", count=len(table_info))
            return table_info
            
        except Exception as e:
            logger.error("Failed to list tables", error=str(e))
            raise
    
    async def get_table_schema(self, table_name: str) -> Dict[str, Any]:
        """Get detailed schema for a specific table"""
        try:
            logger.info("Getting table schema", table=table_name)
            
            schema = await self.client.get_table_schema(table_name)
            
            logger.info("Table schema retrieved", 
                       table=table_name, 
                       columns=len(schema.get('columns', [])))
            return schema
            
        except Exception as e:
            logger.error("Failed to get table schema", 
                        table=table_name, error=str(e))
            raise
    
    async def get_table_count(self, table_name: str) -> int:
        """Get row count for a specific table"""
        try:
            # Use a simple query to get count
            query = f"SELECT COUNT(*) as count FROM {table_name}"
            result = await self.client.execute_query(query)
            
            if result and len(result) > 0:
                return result[0].get('count', 0)
            return 0
            
        except Exception as e:
            logger.error("Failed to get table count", 
                        table=table_name, error=str(e))
            raise
    
    # ============================================================================
    # CLIENT/CONTACT OPERATIONS
    # ============================================================================
    
    async def list_clients(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """List all client/contact records"""
        try:
            logger.info("Listing clients", limit=limit, offset=offset)
            
            # Query both account and contact tables
            account_query = f"""
            SELECT 
                accountid, name, emailaddress1, telephone1, 
                address1_city, address1_stateorprovince, statuscode,
                createdon, modifiedon
            FROM account 
            ORDER BY name
            LIMIT {limit} OFFSET {offset}
            """
            
            contact_query = f"""
            SELECT 
                contactid, firstname, lastname, emailaddress1, telephone1,
                address1_city, address1_stateorprovince, statuscode,
                createdon, modifiedon
            FROM contact 
            ORDER BY lastname, firstname
            LIMIT {limit} OFFSET {offset}
            """
            
            accounts = await self.client.execute_query(account_query)
            contacts = await self.client.execute_query(contact_query)
            
            # Combine and format results
            clients = []
            
            for account in accounts:
                clients.append({
                    'id': account['accountid'],
                    'type': 'account',
                    'name': account['name'],
                    'email': account.get('emailaddress1'),
                    'phone': account.get('telephone1'),
                    'city': account.get('address1_city'),
                    'state': account.get('address1_stateorprovince'),
                    'status': account.get('statuscode'),
                    'created': account.get('createdon'),
                    'modified': account.get('modifiedon')
                })
            
            for contact in contacts:
                clients.append({
                    'id': contact['contactid'],
                    'type': 'contact',
                    'name': f"{contact.get('firstname', '')} {contact.get('lastname', '')}".strip(),
                    'email': contact.get('emailaddress1'),
                    'phone': contact.get('telephone1'),
                    'city': contact.get('address1_city'),
                    'state': contact.get('address1_stateorprovince'),
                    'status': contact.get('statuscode'),
                    'created': contact.get('createdon'),
                    'modified': contact.get('modifiedon')
                })
            
            logger.info("Clients listed successfully", 
                       count=len(clients), 
                       accounts=len(accounts), 
                       contacts=len(contacts))
            return clients
            
        except Exception as e:
            logger.error("Failed to list clients", error=str(e))
            raise
    
    async def get_client_details(self, client_id: str, client_type: str = 'auto') -> Optional[Dict[str, Any]]:
        """Get detailed information for a specific client"""
        try:
            logger.info("Getting client details", client_id=client_id, type=client_type)
            
            # Determine table based on ID or type
            if client_type == 'auto':
                # Try to determine from ID format or query both
                account_query = f"SELECT * FROM account WHERE accountid eq '{client_id}'"
                contact_query = f"SELECT * FROM contact WHERE contactid eq '{client_id}'"
                
                try:
                    account_result = await self.client.execute_query(account_query)
                    if account_result:
                        return {
                            'type': 'account',
                            'data': account_result[0]
                        }
                except:
                    pass
                
                try:
                    contact_result = await self.client.execute_query(contact_query)
                    if contact_result:
                        return {
                            'type': 'contact',
                            'data': contact_result[0]
                        }
                except:
                    pass
                
                return None
            else:
                table_name = 'account' if client_type == 'account' else 'contact'
                query = f"SELECT * FROM {table_name} WHERE {table_name}id eq '{client_id}'"
                result = await self.client.execute_query(query)
                
                if result:
                    return {
                        'type': client_type,
                        'data': result[0]
                    }
                return None
                
        except Exception as e:
            logger.error("Failed to get client details", 
                        client_id=client_id, error=str(e))
            raise
    
    async def search_clients(self, search_term: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Search clients by name, email, or phone"""
        try:
            logger.info("Searching clients", search_term=search_term, limit=limit)
            
            # Search in both account and contact tables
            account_query = f"""
            SELECT 
                accountid, name, emailaddress1, telephone1, 
                address1_city, address1_stateorprovince, statuscode
            FROM account 
            WHERE contains(name, '{search_term}') 
               OR contains(emailaddress1, '{search_term}')
               OR contains(telephone1, '{search_term}')
            ORDER BY name
            LIMIT {limit}
            """
            
            contact_query = f"""
            SELECT 
                contactid, firstname, lastname, emailaddress1, telephone1,
                address1_city, address1_stateorprovince, statuscode
            FROM contact 
            WHERE contains(firstname, '{search_term}') 
               OR contains(lastname, '{search_term}')
               OR contains(emailaddress1, '{search_term}')
               OR contains(telephone1, '{search_term}')
            ORDER BY lastname, firstname
            LIMIT {limit}
            """
            
            accounts = await self.client.execute_query(account_query)
            contacts = await self.client.execute_query(contact_query)
            
            # Format results
            results = []
            
            for account in accounts:
                results.append({
                    'id': account['accountid'],
                    'type': 'account',
                    'name': account['name'],
                    'email': account.get('emailaddress1'),
                    'phone': account.get('telephone1'),
                    'city': account.get('address1_city'),
                    'state': account.get('address1_stateorprovince'),
                    'status': account.get('statuscode')
                })
            
            for contact in contacts:
                results.append({
                    'id': contact['contactid'],
                    'type': 'contact',
                    'name': f"{contact.get('firstname', '')} {contact.get('lastname', '')}".strip(),
                    'email': contact.get('emailaddress1'),
                    'phone': contact.get('telephone1'),
                    'city': contact.get('address1_city'),
                    'state': contact.get('address1_stateorprovince'),
                    'status': contact.get('statuscode')
                })
            
            logger.info("Client search completed", 
                       results=len(results), 
                       accounts=len(accounts), 
                       contacts=len(contacts))
            return results
            
        except Exception as e:
            logger.error("Failed to search clients", 
                        search_term=search_term, error=str(e))
            raise
    
    # ============================================================================
    # SESSION/APPOINTMENT OPERATIONS
    # ============================================================================
    
    async def list_sessions(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """List all session/appointment records"""
        try:
            logger.info("Listing sessions", limit=limit, offset=offset)
            
            query = f"""
            SELECT 
                appointmentid, subject, starttime, endtime, 
                _regardingobjectid_value, regardingobjectid,
                statuscode, description, location
            FROM appointment 
            ORDER BY starttime DESC
            LIMIT {limit} OFFSET {offset}
            """
            
            result = await self.client.execute_query(query)
            
            logger.info("Sessions listed successfully", count=len(result))
            return result
            
        except Exception as e:
            logger.error("Failed to list sessions", error=str(e))
            raise
    
    async def get_session_details(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information for a specific session"""
        try:
            logger.info("Getting session details", session_id=session_id)
            
            query = f"SELECT * FROM appointment WHERE appointmentid eq '{session_id}'"
            result = await self.client.execute_query(query)
            
            if result:
                logger.info("Session details retrieved", session_id=session_id)
                return result[0]
            return None
            
        except Exception as e:
            logger.error("Failed to get session details", 
                        session_id=session_id, error=str(e))
            raise
    
    # ============================================================================
    # MESSAGE OPERATIONS
    # ============================================================================
    
    async def list_scheduled_messages(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """List all scheduled messages"""
        try:
            logger.info("Listing scheduled messages", limit=limit, offset=offset)
            
            query = f"""
            SELECT 
                cre92_scheduledmessageid, MessageID, ClientName, Email,
                MessageStatus, MessageSubject, MessageText, MessageType,
                ScheduledTimestamp, Sent, SentAt, CreatedOn, ModifiedOn
            FROM cre92_scheduledmessage 
            ORDER BY ScheduledTimestamp DESC
            LIMIT {limit} OFFSET {offset}
            """
            
            result = await self.client.execute_query(query)
            
            logger.info("Scheduled messages listed successfully", count=len(result))
            return result
            
        except Exception as e:
            logger.error("Failed to list scheduled messages", error=str(e))
            raise
    
    async def get_message_logs(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """List message delivery logs"""
        try:
            logger.info("Listing message logs", limit=limit, offset=offset)
            
            query = f"""
            SELECT 
                id, message_id, message_type, recipient, subject,
                provider, external_id, status, created_at
            FROM messages_log 
            ORDER BY created_at DESC
            LIMIT {limit} OFFSET {offset}
            """
            
            result = await self.client.execute_query(query)
            
            logger.info("Message logs listed successfully", count=len(result))
            return result
            
        except Exception as e:
            logger.error("Failed to list message logs", error=str(e))
            raise
    
    # ============================================================================
    # STATISTICS & ANALYTICS
    # ============================================================================
    
    async def get_client_statistics(self) -> Dict[str, Any]:
        """Get client statistics and counts"""
        try:
            logger.info("Getting client statistics")
            
            # Account statistics
            account_stats_query = """
            SELECT 
                statuscode, COUNT(*) as count
            FROM account 
            GROUP BY statuscode
            """
            
            # Contact statistics
            contact_stats_query = """
            SELECT 
                statuscode, COUNT(*) as count
            FROM contact 
            GROUP BY statuscode
            """
            
            account_stats = await self.client.execute_query(account_stats_query)
            contact_stats = await self.client.execute_query(contact_stats_query)
            
            # Total counts
            total_accounts = sum(stat['count'] for stat in account_stats)
            total_contacts = sum(stat['count'] for stat in contact_stats)
            
            stats = {
                'total_clients': total_accounts + total_contacts,
                'total_accounts': total_accounts,
                'total_contacts': total_contacts,
                'account_statuses': {stat['statuscode']: stat['count'] for stat in account_stats},
                'contact_statuses': {stat['statuscode']: stat['count'] for stat in contact_stats}
            }
            
            logger.info("Client statistics retrieved", stats=stats)
            return stats
            
        except Exception as e:
            logger.error("Failed to get client statistics", error=str(e))
            raise
    
    async def get_session_statistics(self) -> Dict[str, Any]:
        """Get session/appointment statistics"""
        try:
            logger.info("Getting session statistics")
            
            # Status statistics
            status_stats_query = """
            SELECT 
                statuscode, COUNT(*) as count
            FROM appointment 
            GROUP BY statuscode
            """
            
            # Date range statistics (last 30 days)
            date_stats_query = """
            SELECT 
                COUNT(*) as count
            FROM appointment 
            WHERE starttime ge 2024-01-01
            """
            
            status_stats = await self.client.execute_query(status_stats_query)
            date_stats = await self.client.execute_query(date_stats_query)
            
            stats = {
                'total_sessions': sum(stat['count'] for stat in status_stats),
                'status_breakdown': {stat['statuscode']: stat['count'] for stat in status_stats},
                'recent_sessions': date_stats[0]['count'] if date_stats else 0
            }
            
            logger.info("Session statistics retrieved", stats=stats)
            return stats
            
        except Exception as e:
            logger.error("Failed to get session statistics", error=str(e))
            raise
    
    async def get_message_statistics(self) -> Dict[str, Any]:
        """Get message statistics"""
        try:
            logger.info("Getting message statistics")
            
            # Scheduled message statistics
            scheduled_stats_query = """
            SELECT 
                MessageStatus, COUNT(*) as count
            FROM cre92_scheduledmessage 
            GROUP BY MessageStatus
            """
            
            # Message log statistics
            log_stats_query = """
            SELECT 
                status, COUNT(*) as count
            FROM messages_log 
            GROUP BY status
            """
            
            scheduled_stats = await self.client.execute_query(scheduled_stats_query)
            log_stats = await self.client.execute_query(log_stats_query)
            
            stats = {
                'total_scheduled': sum(stat['count'] for stat in scheduled_stats),
                'status_breakdown': {stat['MessageStatus']: stat['count'] for stat in scheduled_stats},
                'total_sent': sum(stat['count'] for stat in log_stats if stat['status'] == 'success'),
                'total_failed': sum(stat['count'] for stat in log_stats if stat['status'] == 'failed')
            }
            
            logger.info("Message statistics retrieved", stats=stats)
            return stats
            
        except Exception as e:
            logger.error("Failed to get message statistics", error=str(e))
            raise

# Global instance for easy access
dataverse_operations = DataverseOperations()
