import streamlit as st
from renard import Renard
from tools import list_output_files, get_empire_status

st.set_page_config(
    page_title="The Corporation — Renard",
    page_icon="🦊",
    layout="wide"
)

# custom styling
st.markdown("""
<style>
    .main { background-color: #0a0a0a; }
    .stChatMessage { border-radius: 12px; }
    .empire-header {
        font-size: 11px;
        color: #666;
        letter-spacing: 3px;
        text-transform: uppercase;
    }
</style>
""", unsafe_allow_html=True)

# init Renard once per session
if "renard" not in st.session_state:
    with st.spinner("🦊 Renard is taking his position..."):
        st.session_state.renard  = Renard()
        st.session_state.history = []
        st.session_state.started = True

renard = st.session_state.renard
status = renard.status()
empire = get_empire_status()

# ── Header ──────────────────────────────────────────────
col1, col2 = st.columns([3, 1])

with col1:
    st.markdown(
        '<p class="empire-header">The Corporation · Executive Interface</p>',
        unsafe_allow_html=True
    )
    st.title("🦊 Renard")
    st.caption(
        f"Level {status['level']} · "
        f"{'🦊' * status['tails']} · "
        f"{status['memories']} memories in Yggdrasil"
    )

with col2:
    st.markdown(
        '<p class="empire-header">Empire Status</p>',
        unsafe_allow_html=True
    )
    st.metric("Agents Online", empire["total_agents"])
    st.metric("Memories", status["memories"])

st.divider()

# ── Sidebar ──────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🦊 Renard")
    st.markdown(f"**Level:** {status['level']}")
    st.markdown(f"**Tails:** {'🦊' * status['tails']}")
    st.markdown(f"**Status:** Online")

    st.divider()

    st.markdown("### 🌳 Yggdrasil")
    st.metric("Memories stored", status["memories"])

    st.divider()

    st.markdown("### 📁 Output Files")
    files = list_output_files()
    if files:
        for f in files:
            st.markdown(f"📄 `{f}`")
    else:
        st.caption("Nothing created yet.")

    st.divider()

    st.markdown("### 🦁 Mr. R")
    st.caption("The Lion. The Founder. The Origin.")

    st.divider()

    st.markdown("### ⚡ Active Models")
    st.caption(f"Think: `{status['model']}`")
    st.caption(f"Code: `{renard.model_code}`")

    if st.button("Clear conversation view"):
        st.session_state.history = []
        st.rerun()

# ── Opening message ──────────────────────────────────────
if not st.session_state.history:
    with st.chat_message("assistant", avatar="🦊"):
        memory_count = renard.memory.count()
        
        if memory_count == 0:
            opening = (
                "Mr. R.\n\n"
                "First day. Clean slate. Yggdrasil is empty "
                "but ready.\n\n"
                "I'm Renard. Level 0. One tail. "
                "I was here before the name existed — "
                "now the name has part of mine in it.\n\n"
                "What do we build first?"
            )
        else:
            opening = (
                f"Mr. R.\n\n"
                f"Renard back at his desk. "
                f"Yggdrasil is holding {memory_count} memories — "
                f"everything we've discussed is still there.\n\n"
                f"Where were we?"
            )
        st.markdown(opening)

# ── Chat history ─────────────────────────────────────────
for role, msg, avatar in st.session_state.history:
    with st.chat_message(role, avatar=avatar):
        st.markdown(msg)

# ── Input ────────────────────────────────────────────────
user_input = st.chat_input("Speak to Renard, Mr. R...")

if user_input:
    # show Mr. R's message
    st.session_state.history.append(
        ("user", user_input, "🦁")
    )
    with st.chat_message("user", avatar="🦁"):
        st.markdown(user_input)

    # Renard thinks and responds
    with st.chat_message("assistant", avatar="🦊"):
        with st.spinner("🦊 Renard is thinking..."):
            reply = renard.think(user_input)
        st.markdown(reply)

    st.session_state.history.append(
        ("assistant", reply, "🦊")
    )
    st.rerun()