from core.planner import Planner


ORDER_REQUEST = (
    "Create a workflow that triggers whenever a new order is received through a webhook, "
    "extracts the customer name, email, order ID, products, and total amount, saves the order "
    "details to Google Sheets, sends a confirmation email to the customer, sends an alert to the "
    "business owner, and marks the order as processed. If the order amount is above ₹5,000, also "
    "send a high-value-order alert."
)


def test_order_webhook_request_creates_structured_workflow():
    workflow = Planner().plan(ORDER_REQUEST)

    assert len(workflow.steps) == 7
    assert [(step.app, step.action) for step in workflow.steps] == [
        ("webhook", "receive_request"),
        ("ai", "analyze"),
        ("google_sheets", "append_row"),
        ("gmail", "send_email"),
        ("gmail", "send_email"),
        ("gmail", "send_email"),
        ("orders", "mark_processed"),
    ]


def test_order_workflow_has_correct_dependencies_and_branch():
    workflow = Planner().plan(ORDER_REQUEST)
    by_id = {step.id: step for step in workflow.steps}

    assert by_id["step_2"].depends_on == ["step_1"]
    assert by_id["step_3"].depends_on == ["step_2"]
    assert by_id["step_4"].depends_on == ["step_2"]
    assert by_id["step_5"].depends_on == ["step_2"]
    assert by_id["step_6"].depends_on == ["step_2"]
    assert by_id["step_6"].condition == "step_2.output.total_amount > 5000"
    assert by_id["step_7"].depends_on == ["step_3", "step_4", "step_5", "step_6"]


def test_order_workflow_extracts_required_fields_and_maps_outputs():
    workflow = Planner().plan(ORDER_REQUEST)
    extract = workflow.steps[1].config["extract"]

    assert extract == [
        "customer_name",
        "customer_email",
        "order_id",
        "products",
        "total_amount",
    ]
    assert workflow.steps[2].config["values"]["order_id"] == "step_2.output.order_id"
    assert workflow.steps[3].config["to"] == "step_2.output.customer_email"
    assert workflow.steps[6].config["order_id"] == "step_2.output.order_id"


SECOND_ORDER_REQUEST = (
    "When a new order arrives, analyze the order, check whether the customer is new or returning, "
    "record the order in the database, notify the relevant team, send the customer a personalized "
    "confirmation, and create a follow-up task for orders that need attention."
)


def test_order_intelligence_creates_customer_status_and_follow_up_flow():
    workflow = Planner().plan(SECOND_ORDER_REQUEST)

    assert [(step.app, step.action) for step in workflow.steps] == [
        ("webhook", "receive_request"),
        ("ai", "analyze"),
        ("airtable", "find_records"),
        ("ai", "analyze"),
        ("airtable", "create_record"),
        ("slack", "send_message"),
        ("gmail", "send_email"),
        ("notion", "create_page"),
    ]

    by_id = {step.id: step for step in workflow.steps}
    assert by_id["step_3"].config["query"] == "customer_email = step_2.output.customer_email"
    assert by_id["step_4"].config["task"] == "classify customer as new or returning"
    assert by_id["step_5"].config["fields"]["customer_status"] == "step_4.output"
    assert by_id["step_6"].config["channel"] == "configure_team_channel"
    assert by_id["step_7"].config["to"] == "step_2.output.customer_email"
    assert by_id["step_8"].condition == "step_2.output.needs_attention == true"
    assert by_id["step_8"].config["destination"] == "configure_follow_up_destination"
