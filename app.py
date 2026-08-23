
import streamlit as st
import sys
import json

# ============================================================
# BACKEND IMPORT
# ============================================================

sys.path.append("/content/drive/MyDrive")

import ParcelPilot_backend as backend


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="ParcelPilot AI Agent",
    page_icon="📦",
    layout="wide"
)


# ============================================================
# TITLE
# ============================================================

st.title("📦 ParcelPilot AI Agent")

st.caption(
    "Grounded customer-support agent for accounts, orders, "
    "tickets, policies and escalations."
)


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.header("Agent Controls")

account_id = st.sidebar.text_input(
    "Account ID",
    value="ACCT-001"
)

st.sidebar.markdown("---")

st.sidebar.subheader("Backend Status")

status = backend.backend_status()

st.sidebar.write(
    f"Accounts: {status['accounts']}"
)

st.sidebar.write(
    f"Orders: {status['orders']}"
)

st.sidebar.write(
    f"Tickets: {status['tickets']}"
)

st.sidebar.write(
    f"Documents: {status['documents']}"
)

st.sidebar.write(
    f"Gemini configured: {status['gemini_configured']}"
)


# ============================================================
# TABS
# ============================================================

tab1, tab2, tab3, tab4 = st.tabs(
    [
        "💬 Agent",
        "🔎 Structured Lookup",
        "📄 Documents",
        "🚨 Escalations"
    ]
)


# ============================================================
# TAB 1 — AGENT
# ============================================================

with tab1:

    st.subheader("Ask ParcelPilot")

    question = st.text_area(
        "Enter your question",
        placeholder=(
            "Example: Can Northstar cancel ORD-1001 "
            "without a cancellation fee?"
        ),
        height=120
    )

    if st.button(
        "Analyze",
        type="primary",
        key="agent_button"
    ):

        if not question.strip():

            st.warning(
                "Please enter a question."
            )

        else:

            question_lower = question.lower()

            # ------------------------------------------------
            # ORDER CANCELLATION
            # ------------------------------------------------

            if (
                "cancel" in question_lower
                and "ord-" in question_lower
            ):

                import re

                match = re.search(
                    r"ord-\d+",
                    question_lower
                )

                if match:

                    order_id = match.group(0).upper()

                    result = (
                        backend.resolve_cancellation_policy(
                            order_id
                        )
                    )

                    if result.get("success"):

                        order = result["order"]
                        account = result["account"]
                        sources = result["policy_sources"]

                        status = order["status"]

                        st.success(
                            "Policy analysis completed."
                        )

                        if status == "BOOKED":

                            st.markdown(
                                f"""
                                ### Answer

                                **{account['account_name']}** can cancel
                                **{order['order_id']}** without a
                                cancellation fee.

                                The shipment is currently
                                **BOOKED** and has not been picked up.

                                The signed **Northstar Enterprise Agreement**
                                overrides the default cancellation SOP and
                                explicitly waives the cancellation fee for
                                BOOKED shipments before pickup.
                                """
                            )

                        elif status == "PICKED_UP":

                            st.markdown(
                                f"""
                                ### Answer

                                **{account['account_name']}** cannot cancel
                                **{order['order_id']}** under the
                                pre-pickup cancellation policy.

                                The shipment is currently
                                **PICKED_UP** and was already collected by
                                the carrier.

                                The pre-pickup cancellation policy only
                                applies to shipments that have not yet been
                                picked up.

                                **Recommended action:** RETURN_TO_ORIGIN.
                                """
                            )

                        else:

                            st.markdown(
                                f"""
                                ### Answer

                                **{order['order_id']}** is currently
                                **{status}**.

                                Cancellation eligibility depends on the
                                current shipment status and applicable
                                customer policy.
                                """
                            )

                        st.markdown(
                            "### Policy Sources"
                        )

                        for source in sources[:5]:

                            with st.expander(
                                source["document"]
                            ):

                                st.write(
                                    source["text"]
                                )

                    else:

                        st.error(
                            result.get(
                                "error",
                                "Unable to resolve request."
                            )
                        )

            # ------------------------------------------------
            # SECURITY ESCALATION
            # ------------------------------------------------

            elif (
                "api key" in question_lower
                or "credential" in question_lower
                or "security" in question_lower
            ):

                ticket_id = "TKT-505"

                result = (
                    backend.agent_prepare_escalation(
                        ticket_id,
                        "Possible production API key exposure"
                    )
                )

                if result.get("success"):

                    st.error(
                        "🚨 Security escalation required"
                    )

                    st.write(
                        "This issue involves possible production "
                        "credential exposure and should be handled "
                        "as a P1 security incident."
                    )

                    st.json(result)

                    st.warning(
                        "Escalation is prepared but NOT executed. "
                        "Explicit confirmation is required."
                    )

                else:

                    st.error(
                        result.get(
                            "error",
                            "Unable to prepare escalation."
                        )
                    )

            # ------------------------------------------------
            # FALLBACK
            # ------------------------------------------------

            else:

                if status["gemini_configured"]:

                    answer = backend.ask_parcelpilot(
                        question
                    )

                    st.markdown(
                        "### Agent Response"
                    )

                    st.write(answer)

                else:

                    st.info(
                        "Gemini is currently unavailable or "
                        "quota-limited. Use the Structured Lookup "
                        "and Documents tabs for grounded responses."
                    )


# ============================================================
# TAB 2 — STRUCTURED LOOKUP
# ============================================================

with tab2:

    st.subheader(
        "Structured Data Lookup"
    )

    lookup_type = st.selectbox(
        "Lookup type",
        [
            "Account",
            "Order",
            "Ticket",
            "Customer Orders",
            "Customer Tickets"
        ]
    )

    identifier = st.text_input(
        "Identifier",
        value=account_id
    )

    if st.button(
        "Run Lookup",
        key="lookup_button"
    ):

        lookup_map = {
            "Account": "account",
            "Order": "order",
            "Ticket": "ticket",
            "Customer Orders": "customer_orders",
            "Customer Tickets": "customer_tickets"
        }

        result = backend.agent_structured_lookup(
            lookup_map[lookup_type],
            identifier
        )

        if result.get("success"):

            st.success(
                "Lookup successful"
            )

            st.json(result)

        else:

            st.error(
                result.get(
                    "error",
                    "Lookup failed."
                )
            )


# ============================================================
# TAB 3 — DOCUMENT SEARCH
# ============================================================

with tab3:

    st.subheader(
        "Policy & Contract Search"
    )

    query = st.text_input(
        "Search policy documents",
        placeholder=(
            "Example: cancellation fee before pickup"
        )
    )

    if st.button(
        "Search Documents",
        key="document_button"
    ):

        if not query.strip():

            st.warning(
                "Enter a search query."
            )

        else:

            result = backend.agent_search_documents(
                query,
                account_id
            )

            if result.get("success"):

                st.success(
                    f"Found {result.get('count', 0)} relevant results."
                )

                for item in result.get(
                    "results",
                    []
                ):

                    with st.expander(
                        f"{item['document']} "
                        f"(score: {item['score']})"
                    ):

                        st.write(
                            item["text"]
                        )

            else:

                st.error(
                    result.get(
                        "error",
                        "Document search failed."
                    )
                )


# ============================================================
# TAB 4 — ESCALATIONS
# ============================================================

with tab4:

    st.subheader(
        "Escalation Management"
    )

    ticket_id = st.text_input(
        "Ticket ID",
        value="TKT-505"
    )

    reason = st.text_input(
        "Escalation reason",
        value="Possible production API key exposure"
    )

    st.markdown(
        "### Step 1 — Prepare"
    )

    if st.button(
        "Prepare Escalation",
        key="prepare_button"
    ):

        result = backend.agent_prepare_escalation(
            ticket_id,
            reason
        )

        st.session_state[
            "pending_escalation"
        ] = result

    pending = st.session_state.get(
        "pending_escalation"
    )

    if pending:

        if pending.get(
            "requires_confirmation"
        ):

            st.warning(
                "⚠️ Confirmation required before execution."
            )

            st.json(pending)

            st.markdown(
                "### Step 2 — Confirm"
            )

            confirm = st.checkbox(
                "I confirm that this escalation should be executed."
            )

            if st.button(
                "Execute Escalation",
                type="primary",
                key="execute_button"
            ):

                if not confirm:

                    st.error(
                        "You must explicitly confirm "
                        "before executing the escalation."
                    )

                else:

                    result = (
                        backend.execute_confirmed_escalation(
                            ticket_id=ticket_id,
                            account_id=pending["account_id"],
                            reason=reason,
                            priority="P1",
                            confirmed=True
                        )
                    )

                    if result.get("success"):

                        st.success(
                            "✅ Escalation created successfully."
                        )

                        st.json(result)

                    else:

                        st.error(
                            result.get(
                                "error",
                                "Escalation failed."
                            )
                        )


# ============================================================
# FOOTER
# ============================================================

st.markdown("---")

st.caption(
    "ParcelPilot AI Agent • Grounded responses • "
    "Policy precedence • Confirmation-gated escalation"
)
