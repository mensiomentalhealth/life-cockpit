# Life Cockpit Architecture

## Overview

Life Cockpit is a layered, modular Python automation framework designed to replace GUI-based workflows with script-based automation in the Microsoft 365 ecosystem. The architecture emphasizes **terminal-driven verbs**, AI-assisted orchestration, and portable backends. The system prioritizes **modularity, security, and extensibility** while evolving from temporary scaffolding to durable systems.

### Strategic Vision
- **Excel and triage tools are initial kludges**, not the final state
- **Terminal-driven verbs** are the primary control mechanism (e.g., `blc report generate`)
- **AI-assisted orchestration** with human-in-the-loop (HITL) approval gates
- **Portable backends** with replaceable dependencies (Swap-30 principle)
- **Governance by design**: Idempotency, explainability, reversibility, and TTL for experiments

---

## 🏗️ System Architecture

### Visual Layer Map
```
          [Client Web Dashboards]
                  │
         [Terminal + Excel UI]
                  │
      ┌──────────Orchestration──────────┐
      │    Logic Apps / Python / AI     │
      │  (event + command driven verbs) │
      └─────────────────────────────────┘
                  │
        ┌───────Data Layer───────┐
        │   Dataverse + Storage  │
        │   Excel (temporary)    │
        └────────────────────────┘
                  │
        ┌──────Governance Layer───────┐
        │ Idempotent, Explainable,    │
        │ Reversible, TTL, Swap-30    │
        └─────────────────────────────┘
```

### Core Components

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Authentication │    │   Configuration │    │     Logging     │
│      (auth/)     │    │     (utils/)     │    │     (utils/)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   Core Modules   │
                    │                 │
                    │ ┌─────────────┐ │
                    │ │  Dataverse  │ │
                    │ │  (dataverse/)│ │
                    │ └─────────────┘ │
                    │ ┌─────────────┐ │
                    │ │   Sessions  │ │
                    │ │  (sessions/)│ │
                    │ └─────────────┘ │
                    │ ┌─────────────┐ │
                    │ │  Reminders  │ │
                    │ │ (reminders/)│ │
                    │ └─────────────┘ │
                    │ ┌─────────────┐ │
                    │ │    Stripe   │ │
                    │ │   (stripe/) │ │
                    │ └─────────────┘ │
                    └─────────────────┘
                                 │
                    ┌─────────────────┐
                    │  Execution Layer │
                    │                 │
                    │ ┌─────────────┐ │
                    │ │   Terminal  │ │
                    │ └─────────────┘ │
                    │ ┌─────────────┐ │
                    │ │    Cursor   │ │
                    │ └─────────────┘ │
                    │ ┌─────────────┐ │
                    │ │   Webhooks  │ │
                    │ └─────────────┘ │
                    └─────────────────┘
```

---

## Layers

### 1. Interface Layer
- **Terminal (Core)**: Primary control via verbs (e.g., `blc report generate`, `blc reminder create`)
- **Excel (Temporary UI)**: Initial visual scaffolding for PM and OPS. To be deprecated once Cockpit-native UI is ready
- **Web (Client-Facing)**: React/SPA dashboards with auth (via Entra/Key Vault)
- **AI Copilot Assistants**: Integrated copilots for prompts, templates, and explanations

### 2. Orchestration Layer
- **Power Automate → Logic Apps → Python Functions** (migration path)
- **All logic externalized** from GUIs
- **Event + Command Driven**: Every action as a verb with logs
- **AI-assisted workflows** with rationale blocks and error routing

### 3. Data Layer
- **Dataverse**: Primary backend for structured data
- **Excel**: Temporary staging/kludge (to be phased out)
- **Azure Storage / OneDrive**: File artifacts
- **Action Log**: All actions/events logged with runID

### 4. AI Layer
- **Prompt Versioning**: Every template stored, versioned, and logged
- **Rationale + Error Routing**: AI outputs rationale blocks; errors routed to triage queue
- **Human-in-the-Loop (HITL)**: Approval gates for high-risk actions

### 5. Governance Layer
- **Idempotency, Explainability, Reversibility**: Embedded in every action
- **Experiment TTL**: Default 30 days
- **Dependency Swap-30**: Replaceable deps
- **Freedom Floor**: Human override always possible

---

## 🔐 Authentication Layer

### Microsoft Graph API Authentication
- **OAuth2 Flow**: Client credentials grant for service-to-service authentication
- **Token Management**: Automatic token refresh and caching
- **Scopes**: Configurable permissions for different automation needs

### Dataverse Authentication
- **Service Principal**: Azure AD application registration
- **Connection String**: Secure credential management
- **Multi-tenant Support**: Configurable for different environments

## ⚙️ Configuration Management

### Environment-Based Configuration
- **Secrets**: Stored in `.env` files (gitignored)
- **Validation**: Pydantic-based configuration validation
- **Type Safety**: Strong typing for all configuration parameters

### Configuration Hierarchy
1. **Environment Variables** (highest priority)
2. **`.env` File** (local development)
3. **Default Values** (fallback)

## 📝 Logging & Monitoring

### Structured Logging
- **JSON Format**: Machine-readable log entries
- **Log Levels**: Configurable verbosity
- **File Rotation**: Automatic log management
- **Console Output**: Colored, human-readable format
- **Action Logging**: Every verb execution logged with runID

### Log Categories
- **Authentication**: Login attempts, token refresh
- **API Calls**: Request/response logging
- **Business Logic**: Workflow execution steps
- **Errors**: Exception handling and debugging
- **AI Operations**: Prompt versions, rationale blocks, HITL decisions

## 🔄 Data Flow

### 1. Authentication Flow
```
User/Service → OAuth2 → Access Token → API Calls
```

### 2. Automation Workflow
```
Trigger → Authentication → Business Logic → External APIs → Logging → Response
```

### 3. AI-Assisted Workflow
```
Command → AI Processing → Rationale Block → HITL Approval → Execution → Logging
```

### 4. Error Handling
```
Exception → Logging → Recovery/Retry → Fallback → Notification → Triage Queue
```

## 🧩 Module Architecture

### Core Modules
Each module follows a consistent pattern:

```
module_name/
├── __init__.py          # Module initialization
├── main.py              # Primary functionality
├── models.py            # Data models (if needed)
├── exceptions.py        # Custom exceptions
└── tests/               # Module-specific tests
```

### Module Responsibilities
- **auth/**: Authentication and token management
- **dataverse/**: Dataverse operations and data access
- **sessions/**: Session management and state
- **reminders/**: Reminder and notification workflows
- **stripe/**: Payment processing integration
- **utils/**: Shared utilities and helpers

## 🔌 Integration Points

### Microsoft 365 Ecosystem
- **Graph API**: User management, email, calendar
- **Dataverse**: Business data and workflows
- **Logic Apps**: Workflow orchestration
- **Power Automate**: Trigger integration

### External Services
- **Stripe**: Payment processing
- **Email Services**: SMTP/SendGrid integration
- **Notification Services**: Push notifications, SMS

## 🚀 Deployment Architecture

### Development Environment
- **Local Python**: Direct execution
- **Virtual Environment**: Isolated dependencies
- **Local Configuration**: `.env` files

### Production Environment
- **Containerized**: Docker support
- **Cloud Deployment**: Azure Functions, AWS Lambda
- **Secrets Management**: Azure Key Vault, AWS Secrets Manager

## 🔒 Security Architecture

### Authentication Security
- **No Hardcoded Secrets**: All credentials in environment
- **Token Expiration**: Automatic refresh handling
- **Least Privilege**: Minimal required permissions

### Data Security
- **Encryption at Rest**: Sensitive data encryption
- **Encryption in Transit**: TLS for all API calls
- **Audit Logging**: Complete activity tracking

## 📊 Performance Considerations

### Caching Strategy
- **Token Caching**: Reduce authentication overhead
- **Response Caching**: Cache frequently accessed data
- **Connection Pooling**: Reuse HTTP connections

### Scalability
- **Stateless Design**: No server-side state
- **Async Support**: Non-blocking operations
- **Batch Operations**: Efficient bulk processing

## 🔄 Versioning & Compatibility

### API Versioning
- **Graph API**: Version-specific endpoints
- **Dataverse**: API version compatibility
- **Backward Compatibility**: Graceful degradation

### Dependency Management
- **Pinned Versions**: Reproducible builds
- **Security Updates**: Regular dependency updates
- **Compatibility Matrix**: Tested version combinations

## 🛠️ Development Workflow

### Code Organization
- **Modular Design**: Independent, testable modules
- **Clear Interfaces**: Well-defined module boundaries
- **Documentation**: Comprehensive docstrings and examples

### Testing Strategy
- **Unit Tests**: Individual module testing
- **Integration Tests**: End-to-end workflow testing
- **Mock Services**: Isolated testing environment

---

## Transitional Phases

### Phase 1: Excel Triage System (Current)
- **Immediate, temporary PM system**
- Excel-based workflows for project management
- Basic automation with Python scripts

### Phase 2: Terminal + Excel Hybrid (Short-term)
- **Terminal-driven verbs** for core operations
- Excel remains for visual scaffolding
- AI-assisted workflows begin integration

### Phase 3: Cockpit-Native PM Module (Planned)
- **Full terminal-driven interface**
- AI copilot assistants integrated
- Excel dependency eliminated
- Robust governance layer active

---

## Examples

### Reminder System v1
```
blc reminder create --type email --recipient client@example.com --message "Follow up"
```
- Dry-run → show queued reminders
- Apply → send email
- Log → Action Log with runID
- Rollback → cancel unsent queue

### Client Report Automation v1
```
blc report generate --client-id 123 --template quarterly
```
- AI generates draft with rationale
- HITL approval required
- Commit → Dataverse rich text
- Rollback → delete draft

### Session Management
```
blc session start --project "Q4 Planning"
blc session log --message "Completed stakeholder interviews"
blc session end --summary "Project phase 1 complete"
```

---

## Governance Principles

### Idempotency
- All operations can be safely repeated
- State checks before execution
- Conflict resolution strategies

### Explainability
- AI outputs include rationale blocks
- All decisions logged with context
- Human-readable audit trails

### Reversibility
- Rollback mechanisms for all operations
- Undo capabilities where possible
- Graceful degradation on failures

### Experiment TTL
- Default 30-day expiration for experiments
- Automatic cleanup of temporary resources
- Clear migration paths to production

### Dependency Swap-30
- All dependencies replaceable within 30 days
- No vendor lock-in
- Modular, pluggable architecture

### Freedom Floor
- Human override always possible
- No fully automated critical decisions
- Clear escalation paths

---

## Notes
- **Excel is a temporary kludge UI**, not architecture
- **AI layer must follow same dev practices** as code (versioned, logged, reversible)
- **Revisit architecture quarterly** to retire scaffolding
- **Terminal verbs are the primary interface** - design for CLI first
- **All actions are logged** with runID for traceability
- **Human-in-the-loop** for high-risk operations
- **Portable backends** enable future migration paths

This architecture provides both the strategic vision for evolution and the concrete technical foundation for building reliable, scalable automation workflows while maintaining security, explainability, and human oversight.
