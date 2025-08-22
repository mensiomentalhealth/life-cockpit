# Life Cockpit Safety Guardrails

**Safety Mechanisms and Approval Workflows**

Life Cockpit implements comprehensive safety guardrails to ensure secure and compliant operations while maintaining development velocity.

## 🛡️ **Safety Principles**

### **Core Safety Principles**
- **Fail Safe** - Operations fail safely rather than dangerously
- **Explicit Approval** - No dangerous operations without explicit approval
- **Audit Everything** - Every operation is logged and auditable
- **Rollback Capability** - All operations can be rolled back
- **Classification Enforcement** - Operations respect data classification

### **Safety Hierarchy**
1. **Prevention** - Prevent dangerous operations
2. **Detection** - Detect when safety is compromised
3. **Response** - Respond quickly to safety issues
4. **Recovery** - Recover from safety incidents

## 🔒 **Safety Mechanisms**

### **Dry-Run Default**
All operations default to dry-run mode, showing what they would do without actually doing it.

```bash
# Default behavior - shows what would happen
python blc.py client-report generate --client-id 123
# Output: "Would generate report for client 123 (DRY RUN)"

# Explicit approval required for actual execution
python blc.py --approve client-report generate --client-id 123
# Output: "Generating report for client 123 (APPROVED)"
```

### **Approval Workflows**
Different operations require different levels of approval based on classification.

```bash
# Personal operations - no approval needed
python blc.py household-task create "Buy groceries"

# Business operations - single approval
python blc.py --approve billing-process run --client-id 123

# Clinical operations - dual approval
python blc.py --approve --clinical session-note create --client-id 123
```

### **Run ID Tracking**
Every operation gets a unique identifier for tracking and rollback.

```bash
# Operation with run ID
python blc.py --run-id=789 session-summary generate --client-id 123

# Logged operations
# 2025-08-20 10:30:15 - Run ID 789: session-summary generate - STARTED
# 2025-08-20 10:30:17 - Run ID 789: session-summary generate - COMPLETED
```

### **Classification Enforcement**
Operations are automatically checked against their classification requirements.

```python
@classification("clinical")
def create_session_note(client_id: str, note_content: str):
    """Create clinical session note."""
    # Automatically requires dual approval
    # Automatically logs with clinical classification
    # Automatically encrypts PHI data
    pass
```

## 🚨 **Safety Gates**

### **Pre-Execution Gates**
Safety checks that happen before an operation executes.

```python
def pre_execution_safety_check(operation: str, classification: str, args: dict):
    """Check safety before operation execution."""
    
    # Check classification requirements
    if classification == "clinical":
        if not has_dual_approval():
            raise SafetyError("Dual approval required for clinical operations")
    
    # Check data access permissions
    if not has_data_access_permission(operation, args):
        raise SafetyError("Insufficient permissions for data access")
    
    # Check environment restrictions
    if not is_safe_environment(operation, classification):
        raise SafetyError("Operation not allowed in current environment")
    
    # Check data validation
    if not validate_data_safety(operation, args):
        raise SafetyError("Data validation failed")
```

### **Execution Gates**
Safety checks that happen during operation execution.

```python
def execution_safety_check(operation: str, classification: str):
    """Check safety during operation execution."""
    
    # Monitor for anomalies
    if detect_anomaly(operation):
        raise SafetyError("Anomaly detected during execution")
    
    # Check resource limits
    if exceeds_resource_limits(operation):
        raise SafetyError("Resource limits exceeded")
    
    # Validate data integrity
    if not validate_data_integrity(operation):
        raise SafetyError("Data integrity check failed")
```

### **Post-Execution Gates**
Safety checks that happen after operation execution.

```python
def post_execution_safety_check(operation: str, result: dict):
    """Check safety after operation execution."""
    
    # Verify operation success
    if not operation_successful(result):
        raise SafetyError("Operation failed safety verification")
    
    # Log operation result
    log_operation_result(operation, result)
    
    # Update audit trail
    update_audit_trail(operation, result)
    
    # Check for side effects
    if detect_side_effects(operation, result):
        raise SafetyError("Unexpected side effects detected")
```

## 🔄 **Rollback Mechanisms**

### **Automatic Rollback**
Operations that fail safety checks are automatically rolled back.

```python
def safe_operation_execution(operation: str, args: dict):
    """Execute operation with automatic rollback on failure."""
    
    # Create rollback point
    rollback_id = create_rollback_point(operation, args)
    
    try:
        # Execute operation
        result = execute_operation(operation, args)
        
        # Verify safety
        post_execution_safety_check(operation, result)
        
        # Commit operation
        commit_operation(operation, result)
        
    except SafetyError as e:
        # Automatic rollback
        rollback_operation(rollback_id)
        log_safety_incident(operation, e)
        raise
```

### **Manual Rollback**
Operations can be manually rolled back using run IDs.

```bash
# Rollback specific operation
python blc.py rollback execute --run-id=789

# List rollback points
python blc.py rollback list

# Create rollback point
python blc.py rollback create --operation="session-note-create" --description="Create session note"
```

## 📊 **Safety Monitoring**

### **Real-Time Monitoring**
Continuous monitoring of safety metrics and alerts.

```python
def safety_monitoring():
    """Monitor safety metrics in real-time."""
    
    # Monitor approval compliance
    approval_compliance = calculate_approval_compliance()
    if approval_compliance < 95.0:
        alert_safety_team("Low approval compliance detected")
    
    # Monitor classification violations
    classification_violations = detect_classification_violations()
    if classification_violations:
        alert_safety_team("Classification violations detected")
    
    # Monitor audit trail completeness
    audit_completeness = calculate_audit_completeness()
    if audit_completeness < 100.0:
        alert_safety_team("Incomplete audit trail detected")
```

### **Safety Metrics**
Key metrics for monitoring safety effectiveness.

```python
def calculate_safety_metrics():
    """Calculate safety metrics."""
    
    metrics = {
        "approval_compliance": calculate_approval_compliance(),
        "classification_violations": count_classification_violations(),
        "audit_completeness": calculate_audit_completeness(),
        "rollback_rate": calculate_rollback_rate(),
        "safety_incidents": count_safety_incidents(),
        "response_time": calculate_response_time()
    }
    
    return metrics
```

## 🚨 **Incident Response**

### **Safety Incident Types**
Different types of safety incidents and their responses.

```python
SAFETY_INCIDENT_TYPES = {
    "classification_violation": {
        "severity": "high",
        "response": "immediate_rollback",
        "notification": "safety_team"
    },
    "approval_bypass": {
        "severity": "critical",
        "response": "immediate_rollback",
        "notification": "safety_team_and_management"
    },
    "data_integrity_failure": {
        "severity": "high",
        "response": "investigation_and_rollback",
        "notification": "safety_team"
    },
    "audit_trail_gap": {
        "severity": "medium",
        "response": "investigation",
        "notification": "safety_team"
    }
}
```

### **Incident Response Workflow**
Standard workflow for responding to safety incidents.

```python
def handle_safety_incident(incident_type: str, details: dict):
    """Handle safety incident according to type."""
    
    # Get incident response plan
    response_plan = SAFETY_INCIDENT_TYPES[incident_type]
    
    # Execute response
    if response_plan["response"] == "immediate_rollback":
        execute_immediate_rollback(details)
    elif response_plan["response"] == "investigation_and_rollback":
        investigate_and_rollback(details)
    elif response_plan["response"] == "investigation":
        investigate_incident(details)
    
    # Send notifications
    send_notifications(response_plan["notification"], details)
    
    # Log incident
    log_safety_incident(incident_type, details, response_plan)
```

## 🔧 **Safety Configuration**

### **Environment-Specific Safety**
Different safety levels for different environments.

```yaml
# Local development
local:
  dry_run_default: true
  approval_required: false
  audit_level: basic
  rollback_enabled: true

# Staging environment
staging:
  dry_run_default: true
  approval_required: true
  audit_level: full
  rollback_enabled: true

# Production environment
production:
  dry_run_default: false
  approval_required: true
  audit_level: immutable
  rollback_enabled: true
```

### **Classification-Specific Safety**
Different safety requirements by classification.

```yaml
# Personal classification
personal:
  approval_required: false
  audit_level: basic
  encryption: standard
  rollback_required: false

# Business classification
business:
  approval_required: true
  audit_level: full
  encryption: enhanced
  rollback_required: true

# Clinical classification
clinical:
  approval_required: dual
  audit_level: immutable
  encryption: end_to_end
  rollback_required: true
```

## 🔗 **Related Documentation**

- **[Classification System](classification.md)** - Operation classification details
- **[Environment Management](environments.md)** - Environment-specific safety
- **[CI/CD Strategy](cicd.md)** - Pipeline safety gates
- **[Compliance Framework](compliance.md)** - Regulatory safety requirements

---

### Decorator Wrapper Behavior

- `safe_operation(Classification, name)` wraps the target function and returns a dict:
  `{ success, dry_run, message, run_id, result }`
- When the original function itself returns a result dict (e.g., `processed_count`), access it via `wrapper['result']`.
- The decorator now avoids passing duplicate `dry_run` kwargs. If the caller supplies `dry_run` explicitly, it is respected; otherwise the guardrail default is injected.

---

*Last Updated: August 21, 2025*
*Safety Guardrails Version: 1.0*
*Your Professional Healthcare Practice*
