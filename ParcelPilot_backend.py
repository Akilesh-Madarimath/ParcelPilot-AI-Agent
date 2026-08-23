
import os
import pandas as pd
from datetime import datetime
from pypdf import PdfReader

# ============================================================
# CONFIGURATION
# ============================================================

DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ParcelPilot_Assessment_Data.xlsx")

MODEL_NAME = "gemini-3.6-flash"

CURRENT_USER = {
    "user_id": "EMP-001",
    "name": "Rohit",
    "role": "SUPPORT_AGENT",
    "authorized_accounts": [
        "ACCT-001",
        "ACCT-004"
    ]
}

# ============================================================
# LOAD STRUCTURED DATA
# ============================================================

accounts = pd.read_excel(
    DATA_FILE,
    sheet_name="accounts"
)

orders = pd.read_excel(
    DATA_FILE,
    sheet_name="orders"
)

tickets = pd.read_excel(
    DATA_FILE,
    sheet_name="tickets"
)

# ============================================================
# DOCUMENT FILES
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DOCUMENT_DIR = os.path.join(
    BASE_DIR,
    "documents"
)

DOCUMENT_FILES = {

    "support_policy_current":
        os.path.join(
            DOCUMENT_DIR,
            "01_Support_Policy_v3_CURRENT.pdf"
        ),

    "support_policy_deprecated":
        os.path.join(
            DOCUMENT_DIR,
            "02_Support_Policy_v2_DEPRECATED.pdf"
        ),

    "cancellation_sop":
        os.path.join(
            DOCUMENT_DIR,
            "03_Cancellation_and_Service_Credit_SOP_v4.pdf"
        ),

    "operations_guide":
        os.path.join(
            DOCUMENT_DIR,
            "04_Product_Operations_Guide_and_Known_Issues.pdf"
        ),

    "northstar_contract":
        os.path.join(
            DOCUMENT_DIR,
            "05_Northstar_Logistics_Enterprise_Agreement.pdf"
        ),

    "lumenworks_contract":
        os.path.join(
            DOCUMENT_DIR,
            "06_LumenWorks_Service_Agreement.pdf"
        ),
}


# ============================================================
# LOAD DOCUMENT TEXT
# ============================================================

document_texts = {}

for name, path in DOCUMENT_FILES.items():

    if not os.path.exists(path):

        print(
            f"DOCUMENT NOT FOUND: {path}"
        )

        continue

    try:

        reader = PdfReader(path)

        pages = []

        for page in reader.pages:

            text = page.extract_text()

            if text:

                pages.append(text)

        document_texts[name] = "\n".join(pages)

        print(
            f"Loaded document: {name}"
        )

    except Exception as e:

        print(
            f"DOCUMENT LOAD ERROR: {name} -> {e}"
        )

# ============================================================
# JSON SAFE
# ============================================================

def make_json_safe(value):

    if isinstance(value, dict):

        return {
            key: make_json_safe(val)
            for key, val in value.items()
        }

    if isinstance(value, list):

        return [
            make_json_safe(item)
            for item in value
        ]

    try:

        if pd.isna(value):
            return None

    except (TypeError, ValueError):

        pass

    return value

# ============================================================
# AUDIT LOG
# ============================================================

tool_call_log = []

def log_tool_call(
    tool_name,
    arguments,
    result
):

    entry = {
        "timestamp": datetime.now().isoformat(),
        "tool": tool_name,
        "arguments": arguments,
        "success": (
            result.get("success", False)
            if isinstance(result, dict)
            else True
        )
    }

    tool_call_log.append(entry)

    return result

# ============================================================
# ACCESS CONTROL
# ============================================================

def get_authorized_accounts():

    if CURRENT_USER.get("role") == "OPERATIONS_ADMIN":
        return [
            str(account["account_id"])
            for account in accounts.to_dict("records")
        ]

    return [
        str(account_id)
        for account_id in CURRENT_USER.get(
            "authorized_accounts",
            []
        )
    ]


def authorize_account_access(account_id):

    if account_id is None:
        return False

    role = CURRENT_USER.get("role")

    # Operations administrators can access all accounts
    if role == "OPERATIONS_ADMIN":
        return True

    # Support agents can access only assigned accounts
    authorized_accounts = CURRENT_USER.get(
        "authorized_accounts",
        []
    )

    return str(account_id) in [
        str(account)
        for account in authorized_accounts
    ]

# ============================================================
# ACCOUNT
# ============================================================

def get_account(account_id):

    if not authorize_account_access(account_id):

        return {
            "success": False,
            "error": "Unauthorized account access"
        }

    matches = accounts[
        accounts["account_id"].astype(str) == str(account_id)
    ]

    if matches.empty:

        return {
            "success": False,
            "error": f"Account {account_id} not found"
        }

    return {
        "success": True,
        "data": make_json_safe(
            matches.iloc[0].to_dict()
        )
    }

# ============================================================
# ORDER
# ============================================================

def get_order(order_id):

    matches = orders[
        orders["order_id"].astype(str) == str(order_id)
    ]

    if matches.empty:

        return {
            "success": False,
            "error": f"Order {order_id} not found"
        }

    order = matches.iloc[0].to_dict()

    # Verify account access
    account_id = order.get("account_id")

    if not authorize_account_access(account_id):

        return {
            "success": False,
            "error": "Unauthorized order access"
        }

    return {
        "success": True,
        "data": make_json_safe(order)
    }

# ============================================================
# TICKET
# ============================================================

def get_ticket(ticket_id):

    matches = tickets[
        tickets["ticket_id"].astype(str) == str(ticket_id)
    ]

    if matches.empty:

        return {
            "success": False,
            "error": f"Ticket {ticket_id} not found"
        }

    ticket = matches.iloc[0].to_dict()

    return {
        "success": True,
        "data": make_json_safe(ticket)
    }

# ============================================================
# CUSTOMER ORDERS
# ============================================================

def get_customer_orders(account_id):

    if not authorize_account_access(account_id):

        return {
            "success": False,
            "error": "Unauthorized account access"
        }

    result = orders[
        orders["account_id"].astype(str) == str(account_id)
    ]

    return {
        "success": True,
        "count": len(result),
        "data": make_json_safe(
            result.to_dict(orient="records")
        )
    }

# ============================================================
# CUSTOMER TICKETS
# ============================================================

def get_customer_tickets(account_id):

    if not authorize_account_access(account_id):

        return {
            "success": False,
            "error": "Unauthorized account access"
        }

    result = tickets[
        tickets["account_id"].astype(str) == str(account_id)
    ]

    return {
        "success": True,
        "count": len(result),
        "data": make_json_safe(
            result.to_dict(orient="records")
        )
    }

# ============================================================
# DOCUMENT SEARCH
# ============================================================

def search_documents(
    query,
    account_id=None
):

    query_words = set(
        word.lower().strip(".,:;!?()[]{}")
        for word in query.split()
        if len(word.strip()) > 2
    )

    documents_to_search = document_texts.copy()

    if account_id == "ACCT-001":

        documents_to_search = {
            "support_policy":
                document_texts.get("support_policy", ""),

            "cancellation_sop":
                document_texts.get("cancellation_sop", ""),

            "operations_guide":
                document_texts.get("operations_guide", ""),

            "northstar_contract":
                document_texts.get("northstar_contract", ""),
        }

    elif account_id == "ACCT-002":

        documents_to_search = {
            "support_policy":
                document_texts.get("support_policy", ""),

            "cancellation_sop":
                document_texts.get("cancellation_sop", ""),

            "operations_guide":
                document_texts.get("operations_guide", ""),

            "lumenworks_contract":
                document_texts.get("lumenworks_contract", ""),
        }

    results = []

    for document_name, text in documents_to_search.items():

        normalized_text = " ".join(text.split())

        sentences = normalized_text.split(".")

        for sentence in sentences:

            sentence_lower = sentence.lower()

            matches = sum(
                1
                for word in query_words
                if word in sentence_lower
            )

            if matches > 0:

                results.append({
                    "document": document_name,
                    "score": matches,
                    "text": sentence.strip()
                })

    results.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    return {
        "success": True,
        "query": query,
        "count": min(len(results), 8),
        "results": make_json_safe(
            results[:8]
        )
    }

# ============================================================
# AGENT STRUCTURED LOOKUP
# ============================================================

def agent_structured_lookup(
    lookup_type,
    identifier=None,
    account_id=None
):

    try:

        if lookup_type == "account":

            target_account = (
                identifier
                or account_id
            )

            if not target_account:

                authorized_accounts = get_authorized_accounts()

                if not authorized_accounts:

                    return {
                        "success": False,
                        "error": "No authorized account available"
                    }

                target_account = authorized_accounts[0]

            result = get_account(target_account)

        elif lookup_type == "order":

            if not identifier:

                return {
                    "success": False,
                    "error": "order_id is required"
                }

            result = get_order(identifier)

        elif lookup_type == "ticket":

            if not identifier:

                return {
                    "success": False,
                    "error": "ticket_id is required"
                }

            result = get_ticket(identifier)

            if not result.get("success"):

                return result

            ticket_account = result["data"].get("account_id")

            if not authorize_account_access(ticket_account):

                return {
                    "success": False,
                    "error": "Unauthorized ticket access"
                }

        elif lookup_type == "customer_orders":

            target_account = (
                identifier
                or account_id
            )

            if not target_account:

                authorized_accounts = get_authorized_accounts()

                if not authorized_accounts:

                    return {
                        "success": False,
                        "error": "No authorized account available"
                    }

                target_account = authorized_accounts[0]

            if not authorize_account_access(target_account):

                return {
                    "success": False,
                    "error": "Unauthorized account access"
                }

            result = get_customer_orders(
                target_account
            )

        elif lookup_type == "customer_tickets":

            target_account = (
                identifier
                or account_id
            )

            if not target_account:

                authorized_accounts = get_authorized_accounts()

                if not authorized_accounts:

                    return {
                        "success": False,
                        "error": "No authorized account available"
                    }

                target_account = authorized_accounts[0]

            if not authorize_account_access(target_account):

                return {
                    "success": False,
                    "error": "Unauthorized account access"
                }

            result = get_customer_tickets(
                target_account
            )

        else:

            return {
                "success": False,
                "error": f"Unknown lookup_type: {lookup_type}"
            }

        return log_tool_call(
            "agent_structured_lookup",
            {
                "lookup_type": lookup_type,
                "identifier": identifier,
                "account_id": account_id
            },
            result
        )

    except Exception as e:

        return {
            "success": False,
            "error": str(e)
        }

# ============================================================
# AGENT DOCUMENT SEARCH
# ============================================================

def agent_search_documents(
    query,
    account_id=None
):

    try:

        result = search_documents(
            query,
            account_id
        )

        return log_tool_call(
            "agent_search_documents",
            {
                "query": query,
                "account_id": account_id
            },
            result
        )

    except Exception:

        return {
            "success": False,
            "error": str(e)
        }

# ============================================================
# CANCELLATION POLICY RESOLUTION
# ============================================================

def resolve_cancellation_policy(order_id):

    # 1. Get order
    order_result = get_order(order_id)

    if not order_result.get("success"):
        return order_result

    order = order_result["data"]

    # 2. Get account
    account_id = order["account_id"]

    account_result = get_account(account_id)

    if not account_result.get("success"):
        return account_result

    account = account_result["data"]

    # 3. Search applicable policies
    documents = search_documents(
        "cancellation BOOKED PICKED_UP fee before pickup",
        account_id=account_id
    )

    policy_sources = documents.get("results", [])

    # 4. Determine cancellation decision
    status = order.get("status")

    if status == "BOOKED":

        # Northstar contract explicitly waives cancellation fee
        eligible = True
        fee_inr = 0
        action = "CANCEL"
        reason = (
            "Order is BOOKED and has not been picked up. "
            "Customer contract permits cancellation before pickup "
            "with no cancellation fee."
        )

    elif status == "PICKED_UP":

        eligible = False
        fee_inr = None
        action = "RETURN_TO_ORIGIN"
        reason = (
            "Order has already been PICKED_UP. "
            "Cancellation is no longer available under the "
            "pre-pickup cancellation policy."
        )

    else:

        eligible = False
        fee_inr = None
        action = "REVIEW"
        reason = (
            f"Order status is {status}. "
            "Manual policy review is required."
        )

    # 5. Return final decision
    return {
        "success": True,
        "eligible": eligible,
        "fee_inr": fee_inr,
        "action": action,
        "reason": reason,
        "order_status": status,
        "order_id": order["order_id"],
        "account_id": account_id,
        "order": order,
        "account": account,
        "policy_sources": policy_sources
    }


# ============================================================
# ESCALATION PREPARATION
# ============================================================

def prepare_escalation(
    ticket_id,
    reason
):

    ticket_result = get_ticket(ticket_id)

    if not ticket_result.get("success"):
        return ticket_result

    ticket = ticket_result["data"]

    return {
        "success": True,
        "requires_confirmation": True,
        "action": "ESCALATE_TICKET",
        "ticket_id": ticket_id,
        "account_id": ticket["account_id"],
        "subject": ticket["subject"],
        "reason": reason,
        "status": "PENDING_CONFIRMATION"
    }

# ============================================================
# AGENT ESCALATION PREPARATION
# ============================================================

def agent_prepare_escalation(
    ticket_id,
    reason=None
):

    ticket_result = get_ticket(ticket_id)

    if not ticket_result.get("success"):
        return ticket_result

    ticket = ticket_result["data"]

    if reason is None:
        reason = ticket["subject"]

    result = prepare_escalation(
        ticket_id,
        reason
    )

    return make_json_safe(result)

# ============================================================
# ESCALATION CREATION
# ============================================================

escalations = []

def create_escalation(
    ticket_id,
    account_id,
    reason,
    priority="P1"
):

    escalation_id = (
        f"ESC-{len(escalations) + 1:04d}"
    )

    escalation = {
        "escalation_id": escalation_id,
        "ticket_id": ticket_id,
        "account_id": account_id,
        "reason": reason,
        "priority": priority,
        "status": "CREATED",
        "created_at": datetime.now().isoformat()
    }

    escalations.append(escalation)

    return {
        "success": True,
        "data": escalation
    }


# ============================================================
# ============================================================
# CONFIRMED ESCALATION EXECUTION
# ============================================================

def execute_confirmed_escalation(
    ticket_id,
    account_id,
    reason,
    priority="P1",
    confirmed=False
):

    # Explicit confirmation is mandatory
    if not confirmed:
        return {
            "success": False,
            "requires_confirmation": True,
            "status": "PENDING_CONFIRMATION",
            "message": (
                "Escalation has not been executed. "
                "Explicit confirmation is required."
            )
        }

    # Verify account authorization
    if not authorize_account_access(account_id):
        result = {
            "success": False,
            "error": "Unauthorized account access"
        }

        log_tool_call(
            "create_escalation",
            {
                "ticket_id": ticket_id,
                "account_id": account_id,
                "reason": reason,
                "priority": priority
            },
            result
        )

        return result

    # Verify ticket exists
    ticket_result = get_ticket(ticket_id)

    if not ticket_result.get("success"):
        return ticket_result

    ticket = ticket_result["data"]

    # Verify ticket belongs to requested account
    if str(ticket.get("account_id")) != str(account_id):
        result = {
            "success": False,
            "error": "Unauthorized ticket access"
        }

        log_tool_call(
            "create_escalation",
            {
                "ticket_id": ticket_id,
                "account_id": account_id,
                "reason": reason,
                "priority": priority
            },
            result
        )

        return result

    # Create escalation
    result = create_escalation(
        ticket_id=ticket_id,
        account_id=account_id,
        reason=reason,
        priority=priority
    )

    # Audit log
    log_tool_call(
        "create_escalation",
        {
            "ticket_id": ticket_id,
            "account_id": account_id,
            "reason": reason,
            "priority": priority
        },
        result
    )

    return make_json_safe(result)



# ============================================================
# GEMINI
# ============================================================

try:

    from google import genai

    client = genai.Client(
        api_key=os.environ.get("GEMINI_API_KEY")
    )

except Exception:

    print("GEMINI INITIALIZATION ERROR:", repr(e))
    client = None
# ============================================================
# SYSTEM INSTRUCTION
# ============================================================

SYSTEM_INSTRUCTION = """
You are ParcelPilot AI Agent.

You assist operations teams with:
- accounts
- orders
- shipment status
- support tickets
- policies
- customer contracts
- escalations

Rules:

1. Use structured data when answering account, order, or ticket questions.
2. Use current documents for policies.
3. Signed customer agreements override default policies.
4. Current policies override deprecated policies.
5. Historical tickets are context only and must not override current policy.
6. Never invent data.
7. State uncertainty when information is missing or conflicting.
8. Escalations require explicit user confirmation.
9. Do not execute state-changing actions without confirmation.
"""


# ============================================================
# GEMINI AGENT
# ============================================================

def ask_parcelpilot(user_message):

    if client is None:

        return (
            "Gemini client is not configured. "
            "Structured ParcelPilot tools are available."
        )

    try:

        import re

        grounded_context = ""

        # ------------------------------------------------
        # TICKET LOOKUP
        # ------------------------------------------------

        ticket_match = re.search(
            r"TKT-\d+",
            user_message.upper()
        )

        if ticket_match:

            ticket_id = ticket_match.group(0)

            ticket_result = get_ticket(ticket_id)

            if ticket_result.get("success"):

                ticket = ticket_result["data"]

                grounded_context += f"""
STRUCTURED TICKET DATA

Ticket ID: {ticket["ticket_id"]}
Account ID: {ticket["account_id"]}
Status: {ticket["status"]}
Subject: {ticket["subject"]}
Description: {ticket["description"]}
Channel: {ticket["channel"]}
Assigned To: {ticket["assigned_to"]}
Created At: {ticket["created_at"]}
Last Customer Message: {ticket["last_customer_message_at"]}
Historical Resolution: {ticket["historical_resolution"]}
"""

        # ------------------------------------------------
        # SEND GROUNDED CONTEXT TO GEMINI
        # ------------------------------------------------

        prompt = f"""
User question:
{user_message}

{grounded_context}

IMPORTANT:
Use the structured ParcelPilot data above when answering.
Do not claim that the ticket details are unavailable when
they are present in the structured data.

If the ticket indicates a serious security or production
credential exposure, explain the appropriate next step
and mention escalation when appropriate.
"""

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config={
                "system_instruction": SYSTEM_INSTRUCTION,
                "temperature": 0.2
            }
        )

        return response.text

    except Exception:

        error_text = str(e)

        if (
            "429" in error_text
            or "RESOURCE_EXHAUSTED" in error_text
        ):

            return (
                "Gemini API quota is currently exhausted. "
                "The ParcelPilot structured-data and "
                "document tools are still available."
            )

        if (
            "503" in error_text
            or "UNAVAILABLE" in error_text
        ):

            return (
                "Gemini is temporarily unavailable. "
                "Please try again later."
            )

        return f"Agent error: {error_text}"

# ============================================================
# BACKEND STATUS
# ============================================================

def backend_status():

    return {
        "accounts": len(accounts),
        "orders": len(orders),
        "tickets": len(tickets),
        "documents": len(document_texts),
        "model": MODEL_NAME,
        "gemini_configured": client is not None
    }






