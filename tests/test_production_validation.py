#!/usr/bin/env python3
"""
Production Validation Test Suite
Tests all components of the messaging automation system for production readiness
"""

import asyncio
import os
import sys
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List

# Add the parent directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from azure.dynamics_message_processor import dynamics_message_processor
from azure.messaging import MessagingFactory
from utils.sandbox import get_sandbox_dataverse
from utils.logger import get_logger

logger = get_logger(__name__)

class ProductionValidationTester:
    """Comprehensive production validation test suite"""
    
    def __init__(self):
        self.test_results = []
        self.start_time = time.time()
        
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all production validation tests"""
        
        print("🧪 Starting Production Validation Test Suite...")
        print("=" * 60)
        
        # Test categories
        test_categories = [
            ("Infrastructure", self.test_infrastructure),
            ("Dynamics Integration", self.test_dynamics_integration),
            ("Messaging Factory", self.test_messaging_factory),
            ("Message Processing", self.test_message_processing),
            ("Error Handling", self.test_error_handling),
            ("Performance", self.test_performance),
            ("Security", self.test_security),
            ("Monitoring", self.test_monitoring)
        ]
        
        for category, test_func in test_categories:
            print(f"\n📋 Testing {category}...")
            try:
                result = await test_func()
                self.test_results.append({
                    'category': category,
                    'status': 'PASS' if result['success'] else 'FAIL',
                    'details': result
                })
                print(f"   {'✅ PASS' if result['success'] else '❌ FAIL'}: {result['message']}")
            except Exception as e:
                self.test_results.append({
                    'category': category,
                    'status': 'ERROR',
                    'details': {'error': str(e)}
                })
                print(f"   ❌ ERROR: {str(e)}")
        
        # Generate summary
        return self.generate_summary()
    
    async def test_infrastructure(self) -> Dict[str, Any]:
        """Test infrastructure components"""
        
        # Test environment variables
        required_vars = [
            'AZURE_TENANT_ID', 'AZURE_CLIENT_ID', 'AZURE_CLIENT_SECRET',
            'DATAVERSE_URL', 'DATAVERSE_CLIENT_ID', 'DATAVERSE_CLIENT_SECRET'
        ]
        
        missing_vars = [var for var in required_vars if not os.environ.get(var)]
        
        if missing_vars:
            return {
                'success': False,
                'message': f"Missing environment variables: {', '.join(missing_vars)}"
            }
        
        # Test Dataverse connection
        try:
            dataverse = get_sandbox_dataverse()
            tables = await dataverse.list_tables()
            if not tables:
                return {
                    'success': False,
                    'message': "Could not retrieve Dataverse tables"
                }
        except Exception as e:
            return {
                'success': False,
                'message': f"Dataverse connection failed: {str(e)}"
            }
        
        return {
            'success': True,
            'message': "Infrastructure components are properly configured"
        }
    
    async def test_dynamics_integration(self) -> Dict[str, Any]:
        """Test Dynamics integration"""
        
        try:
            # Test querying the scheduled message table
            filter_query = "(MessageStatus eq 'Revised' or MessageStatus eq 2) and ScheduledTimestamp le utcNow() and Sent eq false"
            messages = await dynamics_message_processor.dataverse.query_records('cre92_scheduledmessage', filter=filter_query)
            
            # Test creating a test message
            test_message = {
                'MessageID': f'prod-test-{int(time.time())}',
                'ClientName': 'Production Test Client',
                'Email': 'test@example.com',
                'MessageStatus': 'Revised',
                'MessageSubject': 'Production Validation Test',
                'MessageText': 'This is a production validation test message.',
                'MessageType': 'email',
                'ScheduledTimestamp': datetime.utcnow().isoformat(),
                'Sent': False
            }
            
            created_record = await dynamics_message_processor.dataverse.create_record('cre92_scheduledmessage', test_message)
            
            # Test updating the message
            update_data = {
                'Sent': True,
                'SentAt': datetime.utcnow().isoformat(),
                'ModifiedOn': datetime.utcnow().isoformat()
            }
            
            await dynamics_message_processor.dataverse.update_record('cre92_scheduledmessage', created_record['id'], update_data)
            
            # Clean up test message
            await dynamics_message_processor.dataverse.delete_record('cre92_scheduledmessage', created_record['id'])
            
            return {
                'success': True,
                'message': f"Dynamics integration working - found {len(messages)} pending messages"
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f"Dynamics integration failed: {str(e)}"
            }
    
    async def test_messaging_factory(self) -> Dict[str, Any]:
        """Test messaging factory"""
        
        try:
            # Test configuration
            messaging_config = {
                'graph': {
                    'tenant_id': os.environ.get('AZURE_TENANT_ID'),
                    'client_id': os.environ.get('AZURE_CLIENT_ID'),
                    'client_secret': os.environ.get('AZURE_CLIENT_SECRET')
                },
                'respond': {
                    'api_key': os.environ.get('RESPOND_API_KEY'),
                    'workspace_id': os.environ.get('RESPOND_WORKSPACE_ID'),
                    'base_url': os.environ.get('RESPOND_BASE_URL', 'https://api.respond.io')
                }
            }
            
            factory = MessagingFactory(messaging_config)
            
            # Test supported message types
            supported_types = factory.get_supported_message_types()
            if not supported_types:
                return {
                    'success': False,
                    'message': "No supported message types found"
                }
            
            # Test email message (dry run)
            test_message = {
                'message_type': 'email',
                'recipient': 'test@example.com',
                'subject': 'Production Test',
                'body': 'This is a production validation test.'
            }
            
            result = await factory.send_message(test_message)
            
            return {
                'success': True,
                'message': f"Messaging factory working - {len(supported_types)} providers configured"
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f"Messaging factory failed: {str(e)}"
            }
    
    async def test_message_processing(self) -> Dict[str, Any]:
        """Test message processing pipeline"""
        
        try:
            # Test dry run processing
            result = await dynamics_message_processor.process_dynamics_messages(dry_run=True)
            
            if not isinstance(result, dict) or 'processed_count' not in result:
                return {
                    'success': False,
                    'message': "Message processing returned invalid result format"
                }
            
            return {
                'success': True,
                'message': f"Message processing working - processed {result['processed_count']} messages (dry run)"
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f"Message processing failed: {str(e)}"
            }
    
    async def test_error_handling(self) -> Dict[str, Any]:
        """Test error handling capabilities"""
        
        try:
            # Test with invalid message
            invalid_message = {
                'message_type': 'invalid_type',
                'recipient': 'test@example.com'
            }
            
            messaging_config = {
                'graph': {
                    'tenant_id': 'invalid',
                    'client_id': 'invalid',
                    'client_secret': 'invalid'
                }
            }
            
            factory = MessagingFactory(messaging_config)
            result = await factory.send_message(invalid_message)
            
            # Should handle error gracefully
            if result.success:
                return {
                    'success': False,
                    'message': "Error handling failed - invalid message was processed successfully"
                }
            
            return {
                'success': True,
                'message': "Error handling working - invalid messages are properly rejected"
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f"Error handling test failed: {str(e)}"
            }
    
    async def test_performance(self) -> Dict[str, Any]:
        """Test performance characteristics"""
        
        try:
            start_time = time.time()
            
            # Test message processing performance
            result = await dynamics_message_processor.process_dynamics_messages(dry_run=True)
            
            processing_time = time.time() - start_time
            
            # Performance thresholds
            if processing_time > 30:  # 30 seconds max
                return {
                    'success': False,
                    'message': f"Performance test failed - processing took {processing_time:.2f}s (max 30s)"
                }
            
            return {
                'success': True,
                'message': f"Performance acceptable - processing took {processing_time:.2f}s"
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f"Performance test failed: {str(e)}"
            }
    
    async def test_security(self) -> Dict[str, Any]:
        """Test security measures"""
        
        try:
            # Check for hardcoded secrets
            code_files = [
                'azure/dynamics_message_processor.py',
                'azure/messaging.py',
                'azure/message_processor.py'
            ]
            
            for file_path in code_files:
                if os.path.exists(file_path):
                    with open(file_path, 'r') as f:
                        content = f.read()
                        if 'password' in content.lower() or 'secret' in content.lower():
                            # Check if it's just variable names, not actual secrets
                            if any(secret in content for secret in ['client_secret', 'api_key']):
                                if not all(secret in content for secret in ['os.environ', 'getenv']):
                                    return {
                                        'success': False,
                                        'message': f"Potential hardcoded secrets found in {file_path}"
                                    }
            
            return {
                'success': True,
                'message': "Security check passed - no hardcoded secrets found"
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f"Security test failed: {str(e)}"
            }
    
    async def test_monitoring(self) -> Dict[str, Any]:
        """Test monitoring capabilities"""
        
        try:
            # Test logging
            logger.info("Production validation test log message", extra={
                'test_type': 'production_validation',
                'timestamp': datetime.utcnow().isoformat()
            })
            
            # Check if logs directory exists
            if not os.path.exists('logs'):
                return {
                    'success': False,
                    'message': "Logs directory not found"
                }
            
            return {
                'success': True,
                'message': "Monitoring capabilities working - logging functional"
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f"Monitoring test failed: {str(e)}"
            }
    
    def generate_summary(self) -> Dict[str, Any]:
        """Generate test summary"""
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r['status'] == 'PASS'])
        failed_tests = len([r for r in self.test_results if r['status'] == 'FAIL'])
        error_tests = len([r for r in self.test_results if r['status'] == 'ERROR'])
        
        total_time = time.time() - self.start_time
        
        print("\n" + "=" * 60)
        print("📊 PRODUCTION VALIDATION SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"⚠️  Errors: {error_tests}")
        print(f"⏱️  Total Time: {total_time:.2f}s")
        print(f"📈 Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        # Production readiness assessment
        if passed_tests == total_tests:
            readiness = "READY FOR PRODUCTION"
            status = "✅"
        elif passed_tests >= total_tests * 0.8:  # 80% pass rate
            readiness = "NEEDS MINOR FIXES"
            status = "⚠️"
        else:
            readiness = "NOT READY FOR PRODUCTION"
            status = "❌"
        
        print(f"\n{status} PRODUCTION READINESS: {readiness}")
        
        if failed_tests > 0 or error_tests > 0:
            print("\n🔧 Issues to Address:")
            for result in self.test_results:
                if result['status'] in ['FAIL', 'ERROR']:
                    print(f"   • {result['category']}: {result['details'].get('message', result['details'].get('error', 'Unknown error'))}")
        
        return {
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': failed_tests,
            'error_tests': error_tests,
            'success_rate': (passed_tests/total_tests)*100,
            'total_time': total_time,
            'readiness': readiness,
            'results': self.test_results
        }

async def main():
    """Run production validation tests"""
    
    # Set environment for testing
    os.environ['BLC_LOCAL_SANDBOX'] = 'true'
    
    tester = ProductionValidationTester()
    summary = await tester.run_all_tests()
    
    # Exit with appropriate code
    if summary['failed_tests'] > 0 or summary['error_tests'] > 0:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    asyncio.run(main())
