# Product Note

## Additional Client Problem

I focused on reducing operational risk around customer escalations.

Support agents may have permission to prepare an escalation but should not accidentally execute a state-changing action without confirmation.

ParcelPilot therefore implements confirmation-gated escalation execution.

The system requires explicit confirmation and then validates account authorization and ticket ownership before creating an escalation.

## What I Would Build Next

For a production version I would add:

- Persistent database storage
- Role-based access control
- Full audit dashboard
- Semantic document retrieval
- More integrations with shipment and ticketing systems
- Human approval workflows
- Monitoring and agent evaluation
- Automated regression testing

## What I Intentionally Left Out

To keep the assessment focused, I did not implement:

- Production-grade authentication
- Real carrier API integrations
- A full vector database infrastructure
- Multi-user persistent sessions
- Complex workflow orchestration

These would be appropriate for a production implementation but were intentionally excluded to prioritize the core agent functionality.

## Success Metric

The primary product metric would be:

**Percentage of support questions resolved correctly without human intervention.**

A secondary metric would be the rate of unsafe or unauthorized state-changing actions, which should remain effectively zero.
