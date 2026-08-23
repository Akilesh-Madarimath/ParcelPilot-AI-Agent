# ParcelPilot AI Agent

ParcelPilot AI Agent is a grounded customer-support operations assistant designed to answer questions about accounts, orders, shipment status, support tickets, policies, customer contracts, and escalations.

## Live Demo

https://parcelpilot-ai-agent-sfv6t69fzrw7hiqc5shmkb.streamlit.app/

## Repository

https://github.com/Akilesh-Madarimath/ParcelPilot-AI-Agent

## Features

- Account and order lookup
- Support ticket lookup
- Policy analysis
- Customer contract analysis
- Current vs deprecated document handling
- Conflict resolution between policies and signed agreements
- Confirmation-gated escalation execution
- Account authorization checks
- Ticket ownership validation
- Escalation audit logging
- Streamlit-based user interface
- Gemini integration for agent reasoning

## Architecture

The application follows a simple grounded-agent architecture:

User
↓
Streamlit UI
↓
ParcelPilot Agent
↓
Structured Data + Document Retrieval
↓
Policy / Contract Reasoning
↓
Answer or Confirmed Action

Structured data is stored in the assessment Excel workbook. Operational documents and customer contracts are loaded from the `documents/` directory.

## Source Reliability

The agent follows a source hierarchy:

1. Signed customer agreements
2. Current policies
3. Operational documentation
4. Historical/deprecated information

When sources conflict, higher-priority and current sources are preferred. The agent avoids inventing information when the required data is unavailable.

## Escalation Safety

Escalations require explicit confirmation before execution.

The system also verifies:

- Account authorization
- Ticket existence
- Ticket ownership by the account

Successful escalations are recorded with an escalation ID, timestamp, priority, and audit information.

## Tech Stack

- Python
- Pandas
- Streamlit
- Google Gemini API
- Excel
- Python-PDF / document processing
- GitHub

## Setup

```bash
git clone https://github.com/Akilesh-Madarimath/ParcelPilot-AI-Agent.git
cd ParcelPilot-AI-Agent

pip install -r requirements.txt

streamlit run app.py
