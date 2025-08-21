# Life Cockpit CI/CD Strategy

**Minimal Viable to Ultimate Compliance Pipeline**

Life Cockpit implements a dual-track CI/CD strategy: **Minimal Viable CI/CD** for immediate tinkering safety, and **Ultimate CI/CD** for hospital-grade compliance.

## 🎯 **Dual-Track Strategy**

### **Core Principle**
- **One Repository** - Single codebase for all environments
- **Classification-Based** - Policy packs determine security requirements
- **Velocity + Safety** - Fast tinkering with safety guardrails
- **Scalable Compliance** - Evolve from minimal to hospital-grade

### **Classification Policy Packs**
- **Personal** → Light, fast, tinkering-friendly
- **Business** → Moderate (audit + single approval)
- **Clinical** → Strict (full HIPAA/PHIPA, dual control, DLP, audit)

## ⚡ **Minimal Viable CI/CD (MVP)**

### **Goal: Tinker Safely This Week**
Enable immediate automation with safety guardrails, confined to dev/staging environments.

### **Key Features**
- **Local Sandbox Mode** - Mock services for fast development
- **Dry-Run Default** - All operations safe by default
- **Run Logging** - Every execution tracked in staging Dataverse
- **Single Pipeline** - Simple GitHub Actions workflow
- **No Production Writes** - Production blocked at code + pipeline

### **Pipeline Stages**

#### **1. Local Development**
```bash
# Local sandbox with mock services
export BLC_LOCAL=true
python blc.py --dry-run client-report generate

# Safe execution with approval
python blc.py --approve --run-id=123 client-report generate
```

#### **2. CI Pipeline (GitHub Actions)**
```yaml
# .github/workflows/ci.yml
name: Life Cockpit CI/CD

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.12'
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-asyncio pytest-cov black isort mypy
    - name: Run linting
      run: |
        black --check --diff .
        isort --check-only --diff .
        mypy auth/ dataverse/ utils/ blc.py
    - name: Run tests
      run: |
        pytest tests/ --cov=. --cov-report=xml
      env:
        AZURE_CLIENT_ID: ${{ secrets.AZURE_CLIENT_ID }}
        AZURE_CLIENT_SECRET: ${{ secrets.AZURE_CLIENT_SECRET }}
        AZURE_TENANT_ID: ${{ secrets.AZURE_TENANT_ID }}
        DATAVERSE_URL: ${{ secrets.DATAVERSE_URL }}

  security:
    runs-on: ubuntu-latest
    needs: test
    steps:
    - uses: actions/checkout@v4
    - name: Run security scan
      uses: github/codeql-action/init@v2
      with:
        languages: python
    - name: Perform CodeQL Analysis
      uses: github/codeql-action/analyze@v2

  deploy-staging:
    runs-on: ubuntu-latest
    needs: [test, security]
    if: github.ref == 'refs/heads/develop'
    environment: staging
    steps:
    - uses: actions/checkout@v4
    - name: Deploy to staging
      run: |
        echo "Deploying to staging environment"
        # Add staging deployment logic here
    - name: Run integration tests
      run: |
        echo "Running integration tests against staging"
        # Add integration test logic here
```

#### **3. Staging Environment**
- **Synthetic Data** - Real APIs with test data
- **Full Audit Logging** - Every operation tracked
- **Integration Testing** - End-to-end workflow validation
- **Preview Environments** - Ephemeral staging per PR

#### **4. Safety Guardrails**
- **Dry-Run Default** - All operations show what they would do
- **Approval Required** - `--approve` flag for any writes
- **Run ID Tracking** - Every operation has unique identifier
- **Classification Enforcement** - Operations checked against classification

### **MVP Success Criteria**
- ✅ **Tinker Safely** - Can experiment without risk
- ✅ **Fast Iteration** - Quick development cycles
- ✅ **Safety Guardrails** - Prevents accidental damage
- ✅ **Audit Trail** - Track all operations
- ✅ **No Production Risk** - Production protected

## 🏥 **Ultimate CI/CD (Hospital-Grade)**

### **Goal: Impress a Regulator Review**
Full compliance-grade pipeline with enterprise security and governance.

### **Key Features**
- **Multi-Environment** - Dev → Staging → Production with separate subscriptions
- **Advanced Security** - OIDC federation, managed identities, Key Vault
- **Compliance Gates** - CodeQL, IaC scans, license checks, DLP checks
- **Immutable Audit** - Tamper-proof audit trails
- **Dual Approval** - Two-person approval for clinical operations

### **Pipeline Architecture**

#### **1. Development Environment**
```
Purpose: Fast development and testing
Data: Mock and synthetic data
Security: Basic security controls
Compliance: Light compliance checks
```

#### **2. Staging Environment**
```
Purpose: Integration testing and validation
Data: Synthetic/anonymized data
Security: Moderate security controls
Compliance: Full compliance validation
```

#### **3. Production Environment**
```
Purpose: Live clinical operations
Data: Real PHI and clinical data
Security: Maximum security controls
Compliance: Full regulatory compliance
```

### **Advanced Pipeline Stages**

#### **CI Pipeline (All PRs)**
```yaml
jobs:
  test:
    # Unit tests, integration tests, security scans
  compliance:
    # HIPAA/PHIPA compliance checks
  security:
    # SAST, DAST, dependency scanning
  quality:
    # Code quality, performance, accessibility
```

#### **Staging CD (release/*)**
```yaml
jobs:
  deploy-infra:
    # Deploy infrastructure (Bicep/Terraform)
  deploy-solutions:
    # Deploy application components
  integration-tests:
    # Run integration tests on synthetic data
  compliance-artifacts:
    # Generate compliance documentation
```

#### **Production CD (main)**
```yaml
jobs:
  dual-approval:
    # Require two approvals for clinical operations
  canary-deploy:
    # Gradual rollout to production
  post-deploy-audit:
    # Verify deployment compliance
  auto-rollback:
    # Automatic rollback on failure
```

### **Policy-as-Code**
```yaml
# Classification determines required checks
personal:
  required_checks: [lint, test, security]
  approval: none
  audit: basic

business:
  required_checks: [lint, test, security, compliance]
  approval: single
  audit: full

clinical:
  required_checks: [lint, test, security, compliance, dlp]
  approval: dual
  audit: immutable
```

### **Ultimate Success Criteria**
- ✅ **Regulatory Compliance** - Meets all HIPAA/PHIPA requirements
- ✅ **Enterprise Security** - Hospital-grade security controls
- ✅ **Audit Excellence** - Comprehensive audit trails
- ✅ **Governance** - Clear approval and escalation paths
- ✅ **Scalability** - Handles practice growth and expansion

## 🔄 **Migration Path**

### **Phase 1: MVP Implementation (This Week)**
- [ ] **Local Sandbox** - Mock services for fast development
- [ ] **Basic CI Pipeline** - GitHub Actions with testing
- [ ] **Safety Guardrails** - Dry-run defaults and approval
- [ ] **Staging Environment** - Synthetic data testing

### **Phase 2: Enhanced Security (Next Month)**
- [ ] **Advanced Security** - OIDC, managed identities, Key Vault
- [ ] **Compliance Gates** - HIPAA/PHIPA compliance checks
- [ ] **Enhanced Audit** - Comprehensive audit logging
- [ ] **Policy-as-Code** - Classification-based policies

### **Phase 3: Hospital-Grade (Future)**
- [ ] **Multi-Environment** - Separate dev/staging/prod
- [ ] **Dual Approval** - Two-person approval for clinical
- [ ] **Comprehensive Audit** - Tamper-evident audit trails
- [ ] **Auto-Rollback** - Automatic failure recovery

## 🛡️ **Safety Mechanisms**

### **Dry-Run Default**
```bash
# All operations show what they would do
python blc.py client-report generate
# Output: "Would generate report for client 123 (DRY RUN)"

# Explicit approval required for actual execution
python blc.py --approve --run-id=456 client-report generate
# Output: "Generating report for client 123 (APPROVED)"
```

### **Run ID Tracking**
```bash
# Every operation gets a unique identifier
python blc.py --run-id=789 session-summary generate
# Logged: "Run ID 789: session-summary generate - STARTED"
# Logged: "Run ID 789: session-summary generate - COMPLETED"
```

### **Classification Enforcement**
```bash
# Personal operations - no approval needed
python blc.py --classification=personal household-task create

# Business operations - single approval
python blc.py --classification=business --approve billing-process run

# Clinical operations - dual approval
python blc.py --classification=clinical --approve --clinical session-note create
```

## 📊 **Metrics & Monitoring**

### **Pipeline Metrics**
- **Build Success Rate** - Percentage of successful builds
- **Test Coverage** - Code coverage percentage
- **Security Scan Results** - Security vulnerabilities found
- **Deployment Frequency** - How often code is deployed

### **Compliance Metrics**
- **Compliance Score** - Overall compliance rating
- **Audit Trail Completeness** - Percentage of operations logged
- **Approval Compliance** - Percentage of operations properly approved
- **Security Incident Rate** - Number of security incidents

## 🤖 **LLM Integration Strategy**

### **Model-Agnostic CI/CD**
- **Provider Flexibility** - Support for Azure OpenAI, Google AI, Claude, and other providers
- **Compliance Controls** - Same security and audit requirements regardless of provider
- **Testing Strategy** - Mock LLM responses in development, real providers in staging/prod
- **Version Management** - Track LLM model versions and prompt changes

### **LLM Safety Gates**
- **Content Filtering** - Automated PHI detection and redaction
- **Prompt Validation** - Ensure prompts don't leak sensitive data
- **Output Validation** - Verify outputs meet compliance requirements
- **Audit Logging** - Log all LLM interactions for compliance

## 🔗 **Related Documentation**

---

*Last Updated: August 20, 2025*
*CI/CD Strategy Version: 1.0*
*Your Professional Healthcare Practice*
