import streamlit as st
import ollama
import json
import re

from database import *

MODEL_NAME = "qwen2.5-coder:3b"

st.set_page_config(
    page_title="Placement Code Assistant",
    page_icon="💻",
    layout="wide"
)

st.markdown("""
<style>

.block-container{
    padding-top:1rem;
    max-width:1400px;
}

[data-testid="stSidebar"]{
    min-width:320px;
    max-width:320px;
}

.stButton > button{
    width:100%;
}

[data-testid="stChatMessage"]{
    border-radius:12px;
    padding:10px;
}

</style>
""", unsafe_allow_html=True)

init_db()

if "chat_id" not in st.session_state:
    st.session_state.chat_id = None

if "rename_chat" not in st.session_state:
    st.session_state.rename_chat = None


def show_bullets(data):
    """
    Display strings or lists as bullet points.
    """

    if isinstance(data, list):

        if not data:
            st.markdown("- Not available")

        for item in data:
            st.markdown(f"- {item}")

    elif data:

        st.markdown(f"- {data}")

    else:

        st.markdown("- Not available")


with st.sidebar:

    st.title("💬 Chats")

    if st.button("➕ New Chat"):

        new_chat_id = create_chat("New Chat")

        st.session_state.chat_id = new_chat_id

        st.rerun()

    st.divider()

    chats = get_chats()

    for cid, title in chats:

        col1, col2 = st.columns([8, 1])

        with col1:

            if st.button(
                title,
                key=f"chat_{cid}"
            ):

                st.session_state.chat_id = cid
                st.rerun()

        with col2:

            with st.popover("⋮"):

                if st.button(
                    "✏️ Rename",
                    key=f"rename_{cid}"
                ):

                    st.session_state.rename_chat = cid
                    st.rerun()

                if st.button(
                    "🗑️ Delete",
                    key=f"delete_{cid}"
                ):

                    delete_chat(cid)

                    if st.session_state.chat_id == cid:
                        st.session_state.chat_id = None

                    st.rerun()

    st.divider()

    st.subheader("🎯 Placement Analysis")

    if st.session_state.chat_id:

        tips = get_tips(
            st.session_state.chat_id
        ) or {}

        with st.expander("📌 Pattern"):
            show_bullets(
                tips.get("pattern")
            )

        with st.expander("🔥 Difficulty"):
            show_bullets(
                tips.get("difficulty")
            )

        with st.expander("⏱ Average Time"):
            show_bullets(
                tips.get("average_time")
            )

        with st.expander("⚡ Complexity"):
            show_bullets(
                tips.get("complexity")
            )

        with st.expander("❌ Common Mistakes"):
            show_bullets(
                tips.get("mistakes")
            )

        with st.expander("🎯 Interview Tips"):
            show_bullets(
                tips.get("tips")
            )

        with st.expander("🧠 Follow-Ups"):
            show_bullets(
                tips.get("followups")
            )


# -----------------------------
# Rename Chat Section
# -----------------------------

if st.session_state.rename_chat:

    with st.expander(
        "✏️ Rename Chat",
        expanded=True
    ):

        new_name = st.text_input(
            "New Chat Name"
        )

        c1, c2 = st.columns(2)

        with c1:

            if st.button(
                "Save",
                key="save_chat_name"
            ):

                if new_name.strip():

                    update_chat_title(
                        st.session_state.rename_chat,
                        new_name.strip()
                    )

                st.session_state.rename_chat = None
                st.rerun()

        with c2:

            if st.button(
                "Cancel",
                key="cancel_chat_name"
            ):

                st.session_state.rename_chat = None
                st.rerun()
                
        # ----------------------------------
# Create First Chat Automatically
# ----------------------------------

if st.session_state.chat_id is None:

    first_chat = create_chat(
        "New Chat"
    )

    st.session_state.chat_id = first_chat


# ----------------------------------
# Main UI
# ----------------------------------

st.title("💻 Placement Code Assistant")

mode = st.selectbox(
    "Choose Mode",
    [
        "Code Generation",
        "Code Review"
    ]
)

current_chat = st.session_state.chat_id


# ----------------------------------
# Display Previous Messages
# ----------------------------------

messages = get_messages(
    current_chat
)

for role, content in messages:

    with st.chat_message(role):

        st.markdown(content)


# ----------------------------------
# User Input
# ----------------------------------

prompt = st.chat_input(
    "Ask coding questions or paste code..."
)


# ----------------------------------
# Process Prompt
# ----------------------------------

if prompt:

    add_message(
        current_chat,
        "user",
        prompt
    )

    with st.chat_message("user"):
        st.markdown(prompt)

    all_messages = get_messages(
        current_chat
    )

    # Auto rename first message
    if len(all_messages) == 1:

        update_chat_title(
            current_chat,
            prompt[:40]
        )

    # ----------------------------------
    # System Prompt
    # ----------------------------------

    if mode == "Code Generation":

        system_prompt = """
You are an expert coding mentor.

For every coding problem provide:

1. Solution
2. Explanation
3. Time Complexity
4. Space Complexity
5. Best Approach

Give clean interview-ready code.

Prefer Python unless another language is requested.
"""

    else:

        system_prompt = """
You are a strict technical interviewer.

Analyze the submitted code.

Provide:

1. Status (Correct / Incorrect)
2. Syntax Errors
3. Logical Errors
4. Runtime Errors
5. Corrected Code
6. Time Complexity
7. Space Complexity
8. Code Quality Score (/10)
9. Interview Feedback

Never assume the code is correct.
"""

    # ----------------------------------
    # Build Conversation
    # ----------------------------------

    convo = [
        {
            "role": "system",
            "content": system_prompt
        }
    ]

    all_messages = get_messages(
        current_chat
    )

    for role, content in all_messages:

        convo.append(
            {
                "role": role,
                "content": content
            }
        )

    # ----------------------------------
    # Generate Assistant Response
    # ----------------------------------

    with st.chat_message("assistant"):

        with st.spinner("Thinking..."):

            try:

                response = ollama.chat(
                    model=MODEL_NAME,
                    messages=convo
                )

                answer = response.get(
                    "message",
                    {}
                ).get(
                    "content",
                    "No response generated."
                )

            except Exception as e:

                answer = f"Error: {str(e)}"

            st.markdown(answer)

    add_message(
        current_chat,
        "assistant",
        answer
    )

    # ----------------------------------
    # Placement Analysis Input
    # ----------------------------------

    analysis_input = f"""
User Question:
{prompt}

Assistant Response:
{answer}
"""

    # ----------------------------------
    # Placement Analysis
    # ----------------------------------

    try:

        placement_response = ollama.chat(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": """
Analyze the coding problem and solution.

Return ONLY this JSON:

{
  "pattern":"",
  "difficulty":"",
  "average_time":"",
  "complexity":"",
  "mistakes":[],
  "tips":[],
  "followups":[]
}

Rules:
- JSON only
- No markdown
- No explanations
- No code fences
"""
                },
                {
                    "role": "user",
                    "content": analysis_input
                }
            ]
        )

        raw = placement_response.get(
            "message",
            {}
        ).get(
            "content",
            ""
        )

        # Debugging
        st.sidebar.subheader("🔍 Debug")
        st.sidebar.code(raw)

        raw = raw.replace(
            "```json",
            ""
        )

        raw = raw.replace(
            "```",
            ""
        )

        raw = raw.strip()

        match = re.search(
            r"\{.*\}",
            raw,
            re.DOTALL
        )

        if not match:
            raise ValueError(
                "No JSON found in model output"
            )

        tips_data = json.loads(
            match.group()
        )

        # Ensure all keys exist

        tips_data.setdefault(
            "pattern",
            ""
        )

        tips_data.setdefault(
            "difficulty",
            ""
        )

        tips_data.setdefault(
            "average_time",
            ""
        )

        tips_data.setdefault(
            "complexity",
            ""
        )

        tips_data.setdefault(
            "mistakes",
            []
        )

        tips_data.setdefault(
            "tips",
            []
        )

        tips_data.setdefault(
            "followups",
            []
        )

        # Normalize keys and types to expected schema before saving
        def _get_str(d, *keys):
            for k in keys:
                v = d.get(k)
                if isinstance(v, str) and v.strip():
                    return v.strip()
                if v is not None and not isinstance(v, (list, dict)):
                    return str(v)
            return ""

        def _get_list(d, *keys):
            for k in keys:
                v = d.get(k)
                if isinstance(v, list):
                    return v
                if isinstance(v, str) and v.strip():
                    return [v.strip()]
            return []

        normalized = {
            "pattern": _get_str(tips_data, "pattern", "Pattern"),
            "difficulty": _get_str(tips_data, "difficulty", "Difficulty"),
            "average_time": _get_str(tips_data, "average_time", "averageTime", "Average Time"),
            "complexity": _get_str(tips_data, "complexity", "Complexity"),
            "mistakes": _get_list(tips_data, "mistakes", "Mistakes", "commonMistakes", "Common Mistakes"),
            "tips": _get_list(tips_data, "tips", "Tips"),
            "followups": _get_list(tips_data, "followups", "Followups", "followUps", "Follow-Ups"),
        }

        save_tips(
            current_chat,
            normalized
        )

    except Exception as e:

        st.sidebar.error(
            f"Placement Analysis Failed: {e}"
        )

        save_tips(
            current_chat,
            {
                "pattern": "",
                "difficulty": "",
                "average_time": "",
                "complexity": "",
                "mistakes": [],
                "tips": [],
                "followups": []
            }
        )

    st.rerun()
