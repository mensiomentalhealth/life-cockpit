# Life Cockpit Environment Management

**Classification-Based Environment Strategy**

Life Cockpit uses a classification-based environment strategy that provides different security and compliance levels based on the type of data being processed.

## 🎯 **Classification-Based Architecture**

### **Core Principle**
Every operation in Life Cockpit is tagged with a classification that determines:
- **Security requirements** - Encryption, access controls, audit logging
- **Compliance requirements** - HIPAA, PHIPA, PCI DSS
- **Approval workflows** - Who can approve what operations
- **Data handling** - How data is processed and stored

### **Classifications**

| Classification | Description | Security Level | Approval Required | Data Type | Examples |
|----------------|-------------|----------------|-------------------|-----------|----------|
| **personal** | Personal life management | Light | None | Personal data only | Household tasks, personal projects |
| **business** | Business operations | Moderate | Single approval | Business data, no PHI | Billing, scheduling, reporting |
| **clinical** | Healthcare operations | Strict | Dual approval | PHI, clinical records | Therapy sessions, client data |

## 🏗️ **Environment Tiers**

### **Local Sandbox (Development)**
```
Purpose: Fast tinkering and development
Data: Mock data only, no real PHI
Access: Local only, no network access
Classification: All (personal, business, clinical)
Security: Basic local security
```

**Features:**
- **Mock Services** - Simulated Dataverse, Graph API, LLM
- **Fast Iteration** - No compliance overhead
- **Dry-Run Default** - All operations safe by default
- **Local Only** - No network access to real data

**Use Cases:**
- **Development** - Building new features
- **Testing** - Unit and integration testing
- **Experimentation** - Trying new workflows
- **Learning** - Understanding system behavior

### **Staging Environment**
```
Purpose: Integration testing and validation
Data: Synthetic/anonymized data
Access: Controlled, audit logged
Classification: All (with appropriate data)
Security: Moderate security controls
```

**Features:**
- **Real APIs** - Actual Microsoft services
- **Test Data** - Synthetic or anonymized data
- **Full Audit** - Complete audit logging
- **Integration Testing** - End-to-end workflow testing

**Use Cases:**
- **Integration Testing** - Testing with real APIs
- **Workflow Validation** - Validating business processes
- **Performance Testing** - Load and stress testing
- **Compliance Testing** - Testing compliance features

### **Production Environment**
```
Purpose: Live clinical operations
Data: Real client data (PHI)
Access: Strict controls, dual approval
Classification: All (with full compliance)
Security: Maximum security controls
```

**Features:**
- **Real Data** - Actual client data and PHI
- **Full Compliance** - HIPAA, PHIPA, PCI DSS
- **Dual Approval** - Two-person approval for clinical operations
- **Comprehensive Audit** - Immutable audit trails

**Use Cases:**
- **Live Operations** - Actual client care
- **Clinical Workflows** - Therapy session management
- **Financial Operations** - Billing and payments
- **Compliance Reporting** - Regulatory reporting

## 🔧 **Environment Configuration**

### **Environment Variables**
```bash
# Environment selection
BLC_ENV=local|staging|production
BLC_CLASSIFICATION=personal|business|clinical

# Security settings
BLC_ENCRYPTION_ENABLED=true|false
BLC_AUDIT_LOGGING=true|false
BLC_APPROVAL_REQUIRED=true|false

# Data settings
BLC_USE_MOCK_DATA=true|false
BLC_DATA_ANONYMIZATION=true|false
BLC_PHI_ENCRYPTION=true|false
```

### **Local Development**
```bash
# Set environment
export BLC_ENV=local
export BLC_CLASSIFICATION=personal

# Run with local sandbox
python blc.py --dry-run client-report generate
python blc.py --approve --run-id=123 client-report generate
```

### **Staging Testing**
```bash
# Set environment
export BLC_ENV=staging
export BLC_CLASSIFICATION=business

# Run with staging data
python blc.py --env=staging billing-process run
```

### **Production Operations**
```bash
# Set environment
export BLC_ENV=production
export BLC_CLASSIFICATION=clinical

# Run with full compliance
python blc.py --env=prod --approve --run-id=456 session-summary generate
```

## 🛡️ **Security by Classification**

### **Personal Classification**
- **Data**: Personal data only
- **Access**: Local or personal accounts
- **Audit**: Basic logging
- **Approval**: None required
- **Encryption**: Basic encryption
- **Examples**: Household management, personal projects

### **Business Classification**
- **Data**: Business data, no PHI
- **Access**: Business accounts, audit logged
- **Audit**: Full audit trail
- **Approval**: Single approval required
- **Encryption**: Standard encryption
- **Examples**: Billing, scheduling, business reporting

### **Clinical Classification**
- **Data**: PHI, clinical records
- **Access**: Strict controls, dual approval
- **Audit**: Comprehensive audit trail
- **Approval**: Dual approval required
- **Encryption**: Platform encryption + app-layer envelope encryption for sensitive fields
- **Examples**: Session summaries, client reports, PHI processing

## 📊 **Environment Matrix**

| Environment | Personal | Business | Clinical | Data Type | Approval | Audit |
|-------------|----------|----------|----------|-----------|----------|-------|
| **Local** | ✅ | ✅ | ✅ | Mock | None | Basic |
| **Staging** | ✅ | ✅ | ✅ | Synthetic | Single | Full |
| **Production** | ✅ | ✅ | ✅ | Real | Dual (clinical) | Immutable |

## 🔄 **Environment Promotion**

### **Local → Staging**
```bash
# Test in staging
python blc.py --env=staging --dry-run feature-test

# Promote if successful
python blc.py --env=staging --approve feature-deploy
```

### **Staging → Production**
```bash
# Business operations
python blc.py --env=prod --approve business-operation

# Clinical operations (dual approval)
python blc.py --env=prod --approve --clinical clinical-operation
```

## 🚨 **Safety Guardrails**

### **Dry-Run Default**
- All operations default to dry-run mode
- Must explicitly approve with `--approve` flag
- Run ID required for audit trail

### **Classification Enforcement**
- Operations automatically checked against classification
- Clinical operations require additional approval
- Data access restricted by classification

### **Audit Logging**
- Every operation logged with classification
- Run ID tracked for rollback capability
- Audit trail immutable and searchable

### **Data Isolation**
- Mock data in local environment
- Synthetic data in staging environment
- Real data only in production environment

## 📝 **Implementation Plan**

### **Phase 1: Local Sandbox (Current)**
- [ ] **Mock Services** - Implement mock Dataverse, Graph API, LLM
- [ ] **Classification Decorators** - Add classification to CLI commands
- [ ] **Dry-Run Default** - All operations safe by default
- [ ] **Basic Audit** - Simple operation logging

### **Phase 2: Staging Environment (Next)**
- [ ] **Synthetic Data** - Create anonymized test datasets
- [ ] **Integration Testing** - Full workflow testing
- [ ] **Enhanced Audit** - Comprehensive audit logging
- [ ] **Safety Gates** - Classification-based restrictions

### **Phase 3: Production Readiness (Future)**
- [ ] **Dual Approval** - Two-person approval for clinical operations
- [ ] **Compliance Validation** - HIPAA/PHIPA checks
- [ ] **Comprehensive Audit** - Tamper-evident audit trails
- [ ] **Auto-Rollback** - Automatic recovery on failures

## 🔗 **Related Documentation**

- **[Compliance Framework](compliance.md)** - Regulatory compliance requirements
- **[Security Architecture](security.md)** - Technical security implementation
- **[CI/CD Strategy](cicd.md)** - Deployment and promotion workflows
- **[Classification System](classification.md)** - Verb classification details
- **[Safety Guardrails](guardrails.md)** - Safety mechanisms and approval workflows

---

*Last Updated: August 20, 2025*
*Environment Management Version: 1.0*
*Your Professional Healthcare Practice*
