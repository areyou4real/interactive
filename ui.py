import streamlit as st

def inject_global_ui():
    st.markdown(
        """
        <style>
          /* Card wrapper used by card_open/card_close */
          .card {
            border: 1px solid rgba(148,163,184,0.22);
            background: rgba(15,23,42,0.45);
            border-radius: 18px;
            padding: 14px 14px 10px 14px;
            box-shadow: 0 10px 28px rgba(0,0,0,0.22);
            margin-bottom: 12px;

            /* IMPORTANT: prevent “empty blobs” */
            min-height: 0 !important;
          }

          /* Optional: subtle section dividers */
          .hr {
            height: 1px;
            background: rgba(148,163,184,0.18);
            border: 0;
            margin: 12px 0;
          }

          /* Chips used elsewhere */
          .chips { display:flex; flex-wrap: wrap; gap: 8px; }
          .chip{
            display:inline-flex;
            align-items:center;
            padding: 8px 10px;
            border-radius: 999px;
            border: 1px solid rgba(148,163,184,0.16);
            background: rgba(15,23,42,0.38);
            color: rgba(226,232,240,0.88);
            font-size: 13px;
          }
        </style>
        """,
        unsafe_allow_html=True,
    )

def card_open():
    # open only; DO NOT create an extra empty div
    st.markdown("<div class='card'>", unsafe_allow_html=True)

def card_close():
    st.markdown("</div>", unsafe_allow_html=True)
