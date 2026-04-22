from typing import TypedDict, List, Dict, Any, Optional
from langgraph.graph import StateGraph, START, END
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage

# Initialize our LLM
model = ChatOllama(model="qwen2:7b", temperature=0)

class EmailState(TypedDict):
    email: Dict[str, Any]
    is_spam: Optional[bool]
    spam_reason: Optional[str]
    email_category: Optional[str]
    email_draft: Optional[str]
    messages: List[Dict[str, Any]]

def read_email(state: EmailState):
    email = state["email"]
    print(f"Processing an email from {email['sender']} with subject: {email['subject']}")
    return {}


def classify_email(state: EmailState):
    email = state["email"]

    prompt = f"""Classify the email below as either SPAM or HAM.

Rules:
- HAM: any personal message, threat, alert, or communication requiring my attention.
- SPAM: unsolicited commercial messages, advertisements, investment pitches, promotions, or bulk marketing.

Email:
From: {email['sender']}
Subject: {email['subject']}
Body: {email['body']}

Respond with exactly one word — either HAM or SPAM. Do not explain.
Answer:"""
    messages = [HumanMessage(content=prompt)]
    response = model.invoke(messages)

    response_text = response.content.lower()
    print(response_text)
    is_spam = "spam" in response_text and "ham" not in response_text

    if not is_spam:
        new_messages = state.get("messages", []) + [
            {"role": "user", "content": prompt},
            {"role": "assistant", "content": response.content}
        ]
    else:
        new_messages = state.get("messages", [])

    return {
        "is_spam": is_spam,
        "messages": new_messages
    }


def handle_spam(state: EmailState):
    print(f"Marked the email as spam.")
    return {}


def drafting_response(state: EmailState):
    email = state["email"]

    prompt = f"""
Draft a polite preliminary response to this email.

Email:
From: {email['sender']}
Subject: {email['subject']}
Body: {email['body']}

Draft a brief, professional response that I can review and personalize before sending.
    """

    messages = [HumanMessage(content=prompt)]
    response = model.invoke(messages)

    new_messages = state.get("messages", []) + [
        {"role": "user", "content": prompt},
        {"role": "assistant", "content": response.content}
    ]

    return {
        "email_draft": response.content,
        "messages": new_messages
    }


def notify_me(state: EmailState):
    email = state["email"]

    print("\n" + "=" * 50)
    print(f"Sir, you've received an email from {email['sender']}.")
    print(f"Subject: {email['subject']}")
    print("\nI've prepared a draft response for your review:")
    print("-" * 50)
    print(state["email_draft"])
    print("=" * 50 + "\n")

    return {}


# Define routing logic
def route_email(state: EmailState) -> str:
    if state["is_spam"]:
        return "spam"
    else:
        return "legitimate"


# Create the graph
email_graph = StateGraph(EmailState)

# Add nodes
email_graph.add_node("read_email", read_email)  # the read_email node executes the read_mail function
email_graph.add_node("classify_email", classify_email)  # the classify_email node will execute the classify_email function
email_graph.add_node("handle_spam", handle_spam)  #same logic
email_graph.add_node("drafting_response", drafting_response)  #same logic
email_graph.add_node("notify_me", notify_me)  # same logic

# Add edges
email_graph.add_edge(START, "read_email")  # After starting we go to the "read_email" node

email_graph.add_edge("read_email", "classify_email")  # after_reading we classify

# Add conditional edges
email_graph.add_conditional_edges(
    "classify_email",  # after classify, we run the "route_email" function"
    route_email,
    {
        "spam": "handle_spam",  # if it return "Spam", we go the "handle_span" node
        "legitimate": "drafting_response"  # and if it's legitimate, we go to the "drafting response" node
    }
)

# Add final edges
email_graph.add_edge("handle_spam", END)  # after handling spam we always end
email_graph.add_edge("drafting_response", "notify_me")
email_graph.add_edge("notify_me", END)

# Compile the graph
compiled_graph = email_graph.compile()

import base64
import requests

def save_graph_image(graph, path="graph.png"):
    mermaid_code = graph.get_graph().draw_mermaid()
    encoded = base64.urlsafe_b64encode(mermaid_code.encode("utf-8")).decode("utf-8")
    url = f"https://mermaid.ink/img/{encoded}"
    response = requests.get(url)
    response.raise_for_status()
    with open(path, "wb") as f:
        f.write(response.content)
    print(f"Graph saved to {path}")

save_graph_image(compiled_graph)
emails = [
    {
        "sender": "Dr. Sarah Collins",
        "subject": "Your annual check-up results",
        "body": "Dear Mr. Doe, your blood test results from last Tuesday are in. Everything looks normal. Please call the clinic at your earliest convenience to schedule a follow-up. Best regards, Dr. Collins."
    },
    {
        "sender": "Alfred Pennyworth",
        "subject": "Tonight's dinner reservation",
        "body": "Sir, I have confirmed your reservation at Le Bernardin for 8 PM tonight. Your guest, Mr. Fox, has been notified. The car will be ready at 7:30 PM."
    },
    {
        "sender": "Nigerian Prince <prince.royale@quickmail.net>",
        "subject": "URGENT: $45,000,000 transfer — your help needed",
        "body": "Dear Friend, I am a prince from Nigeria with $45 million USD frozen in a bank account. I need your help to transfer the funds. You will receive 30% commission. Please send your bank details immediately. God bless."
    },
    {
        "sender": "SlimFast Pills <noreply@bestpills4u.biz>",
        "subject": "Lose 30 pounds in 7 days — GUARANTEED!!!",
        "body": "AMAZING NEW PILL dissolves belly fat overnight!! Doctors HATE this trick. Click here NOW for a FREE trial. Limited stock. ACT FAST!!! www.bestpills4u.biz/order"
    },
]

for email in emails:
    print(f"\nProcessing email from {email['sender']}...")
    compiled_graph.invoke({
        "email": email,
        "is_spam": None,
        "spam_reason": None,
        "email_category": None,
        "email_draft": None,
        "messages": []
    })
