# Life Cockpit Classification System

**Verb Classification for Security and Compliance**

Life Cockpit uses a classification system to tag every operation (verb) with appropriate security and compliance requirements.

## 🏷️ **Classification Overview**

### **Core Principle**
Every CLI command and API operation is classified based on:
- **Data Sensitivity** - What type of data is being processed
- **Risk Level** - Potential impact of the operation
- **Compliance Requirements** - Regulatory requirements
- **Approval Workflow** - Who needs to approve the operation

### **Classification Levels**

| Classification | Data Type | Risk Level | Approval | Examples |
|----------------|-----------|------------|----------|----------|
| **personal** | Personal data only | Low | None | Household tasks, personal projects |
| **business** | Business data, no PHI | Medium | Single | Billing, scheduling, reporting |
| **clinical** | PHI, clinical records | High | Dual | Therapy sessions, client data |

## �� **Classification Implementation**

### **CLI Command Classification**
```python
@classification("clinical")
@app.command()
def session_summary(
    client_id: str = typer.Argument(..., help="Client ID"),
    session_date: str = typer.Option(None, help="Session date")
):
    """Generate session summary for client."""
    # Clinical operation - requires dual approval
    pass

@classification("business")
@app.command()
def billing_process(
    client_id: str = typer.Argument(..., help="Client ID")
):
    """Process billing for client."""
    # Business operation - requires single approval
    pass

@classification("personal")
@app.command()
def household_task(
    task: str = typer.Argument(..., help="Task description")
):
    """Create household task."""
    # Personal operation - no approval required
    pass
```

### **API Operation Classification**
```python
@classification("clinical")
async def create_session_note(client_id: str, note_content: str):
    """Create clinical session note."""
    # Requires dual approval for clinical data
    pass

@classification("business")
async def process_payment(client_id: str, amount: float):
    """Process client payment."""
    # Requires single approval for business data
    pass

@classification("personal")
async def create_personal_reminder(reminder: str):
    """Create personal reminder."""
    # No approval required for personal data
    pass
```

## 📋 **Classification Matrix**

### **Personal Classification**
- **Data Type**: Personal data only
- **Risk Level**: Low
- **Approval Required**: None
- **Audit Level**: Basic
- **Encryption**: Standard
- **Examples**:
  - Household task management
  - Personal project tracking
  - Personal reminders
  - Personal calendar events

### **Business Classification**
- **Data Type**: Business data, no PHI
- **Risk Level**: Medium
- **Approval Required**: Single approval
- **Audit Level**: Full audit trail
- **Encryption**: Enhanced
- **Examples**:
  - Billing and payment processing
  - Appointment scheduling
  - Business reporting
  - Client communication (non-clinical)
  - Practice management

### **Clinical Classification**
- **Data Type**: PHI, clinical records
- **Risk Level**: High
- **Approval Required**: Dual approval
- **Audit Level**: Immutable audit trail
- **Encryption**: End-to-end encryption
- **Examples**:
  - Therapy session notes
  - Client assessments
  - Treatment plans
  - Session summaries
  - Clinical communications
  - Progress reports

## 🛡️ **Classification Enforcement**

### **Automatic Enforcement**
```python
def classification(level: str):
    """Decorator to classify operations."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Check classification requirements
            if level == "clinical":
                # Require dual approval
                if not has_dual_approval():
                    raise ClassificationError("Dual approval required for clinical operations")
            elif level == "business":
                # Require single approval
                if not has_single_approval():
                    raise ClassificationError("Single approval required for business operations")
            
            # Log operation with classification
            log_operation(func.__name__, level, *args, **kwargs)
            
            # Execute operation
            return func(*args, **kwargs)
        return wrapper
    return decorator
```

### **Approval Workflows**
```python
def has_single_approval() -> bool:
    """Check if single approval is provided."""
    return "--approve" in sys.argv

def has_dual_approval() -> bool:
    """Check if dual approval is provided."""
    return "--approve" in sys.argv and "--clinical" in sys.argv

def log_operation(operation: str, classification: str, *args, **kwargs):
    """Log operation with classification."""
    logger.info(f"Operation: {operation}, Classification: {classification}")
```

## 📊 **Classification Examples**

### **Personal Operations**
```bash
# No approval required
python blc.py household-task create "Buy groceries"
python blc.py personal-reminder set "Call mom"
python blc.py personal-project start "Learn Python"
```

### **Business Operations**
```bash
# Single approval required
python blc.py --approve billing-process run --client-id 123
python blc.py --approve appointment-schedule create --client-id 123
python blc.py --approve business-report generate --period monthly
```

### **Clinical Operations**
```bash
# Dual approval required
python blc.py --approve --clinical session-note create --client-id 123
python blc.py --approve --clinical assessment-generate --client-id 123
python blc.py --approve --clinical treatment-plan update --client-id 123
```

## 🔍 **Classification Validation**

### **Runtime Validation**
```python
def validate_classification(operation: str, classification: str):
    """Validate operation classification."""
    # Check if operation matches classification
    if operation.startswith("session") and classification != "clinical":
        raise ClassificationError("Session operations must be clinical")
    
    if operation.startswith("billing") and classification != "business":
        raise ClassificationError("Billing operations must be business")
    
    if operation.startswith("household") and classification != "personal":
        raise ClassificationError("Household operations must be personal")
```

### **Static Analysis**
```python
# Pre-commit hook to check classification
def check_classification():
    """Check that all operations have proper classification."""
    for file in get_python_files():
        for function in get_functions(file):
            if is_cli_command(function) and not has_classification(function):
                raise ClassificationError(f"CLI command {function} missing classification")
```

## 📈 **Classification Metrics**

### **Usage Tracking**
- **Operation Count** - Number of operations by classification
- **Approval Rate** - Percentage of operations properly approved
- **Compliance Score** - Overall classification compliance
- **Risk Assessment** - Risk level by classification

### **Compliance Reporting**
```python
def generate_classification_report():
    """Generate classification compliance report."""
    report = {
        "personal": {
            "operations": count_operations("personal"),
            "approval_rate": 100.0,  # No approval required
            "compliance_score": 100.0
        },
        "business": {
            "operations": count_operations("business"),
            "approval_rate": calculate_approval_rate("business"),
            "compliance_score": calculate_compliance_score("business")
        },
        "clinical": {
            "operations": count_operations("clinical"),
            "approval_rate": calculate_approval_rate("clinical"),
            "compliance_score": calculate_compliance_score("clinical")
        }
    }
    return report
```

## 🔗 **Related Documentation**

- **[Environment Management](environments.md)** - Environment strategy by classification
- **[Safety Guardrails](guardrails.md)** - Safety mechanisms and approval workflows
- **[CI/CD Strategy](cicd.md)** - Pipeline policies by classification
- **[Compliance Framework](compliance.md)** - Regulatory requirements by classification

---

*Last Updated: August 20, 2025*
*Classification System Version: 1.0*
*Your Professional Healthcare Practice*
