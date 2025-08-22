# Logic Apps Orchestration (Timer)

Use Azure Logic Apps (Consumption) to schedule your Dynamics Message Processor or other HTTP-triggered functions.

## Repo Workflow JSON

- File: `azure/logic-apps/dynamics-message-scheduler.json`
- Purpose: Timer trigger that performs an HTTP POST to your Azure Function endpoint on a schedule (e.g., every 5 minutes).

## Parameters to set

- Function URL (with function key)
- Recurrence frequency and interval (minutes)

## Deploy (manual)

1. In Azure Portal, create a Logic App (Consumption).
2. Open the Code View and paste the JSON from the repo file.
3. Update the HTTP action URI to your function endpoint.
4. Save and run.

## Notes

- Logic Apps are stateful and resilient; good for lightweight orchestration.
- Alternative: use Azure Functions Timer Trigger (already included under `azure/functions/dynamics_message_processor`).
- Keep both: Logic Apps for externalized schedules and orchestrations; Timer Function for simple cron in code.
