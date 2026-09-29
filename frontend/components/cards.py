import os
import streamlit as st

COCONUT_PALM_SVG = """
<svg width="120" height="120" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
  <path d="M50 95 C50 68 47 48 44 38" stroke="#6b5b45" stroke-width="6" stroke-linecap="round"/>
  <!-- Fronds -->
  <path d="M44 38 C28 28 12 28 2 38" stroke="#2d6a4f" stroke-width="4" stroke-linecap="round"/>
  <path d="M44 38 C24 18 14 8 8 2" stroke="#74c69d" stroke-width="4" stroke-linecap="round"/>
  <path d="M44 38 C44 18 49 8 54 2" stroke="#2d6a4f" stroke-width="4" stroke-linecap="round"/>
  <path d="M44 38 C64 18 74 8 80 2" stroke="#74c69d" stroke-width="4" stroke-linecap="round"/>
  <path d="M44 38 C60 28 76 28 86 38" stroke="#2d6a4f" stroke-width="4" stroke-linecap="round"/>
  <!-- Coconuts -->
  <circle cx="41" cy="40" r="4.5" fill="#543210"/>
  <circle cx="47" cy="41" r="4.5" fill="#432105"/>
  <circle cx="44" cy="45" r="4.5" fill="#543210"/>
</svg>
"""

LEAF_VEIN_SVG = """
<svg width="40" height="40" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
  <path d="M5 35 Q 20 20 35 5" stroke="#74c69d" stroke-width="3" stroke-linecap="round"/>
  <path d="M12 28 Q 18 25 22 28" stroke="#74c69d" stroke-width="2"/>
  <path d="M20 20 Q 26 17 30 20" stroke="#74c69d" stroke-width="2"/>
</svg>
"""

BOTANICAL_SHIELD_SVG = """
<svg width="50" height="50" viewBox="0 0 50 50" fill="none" xmlns="http://www.w3.org/2000/svg">
  <path d="M25 4 L42 12 V24 C42 34 25 45 25 45 C25 45 8 34 8 24 V12 L25 4 Z" fill="#d8f3dc" stroke="#2d6a4f" stroke-width="2.5"/>
  <path d="M18 24 L23 29 L32 19" stroke="#1b4332" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"/>
</svg>
"""

WARNING_BOTANICAL_SVG = """
<svg width="50" height="50" viewBox="0 0 50 50" fill="none" xmlns="http://www.w3.org/2000/svg">
  <path d="M25 5 L46 42 H4 L25 5 Z" fill="#ffe5ec" stroke="#d90429" stroke-width="2.5" stroke-linejoin="round"/>
  <line x1="25" y1="18" x2="25" y2="30" stroke="#d90429" stroke-width="3.5" stroke-linecap="round"/>
  <circle cx="25" cy="36" r="2" fill="#d90429"/>
</svg>
"""

def render_organic_metric_card(label: str, value: str, icon: str = "🌴", delta: str = None, color: str = "#1b4332"):
    """Renders styled organic metric card."""
    st.markdown(
        f"""
        <div class="organic-metric-box">
            <div style="font-size: 1.6rem; margin-bottom: 0.2rem;">{icon}</div>
            <div class="metric-value-lg" style="color: {color};">{value}</div>
            <div class="metric-label-sm">{label}</div>
            {f'<div style="font-size: 0.8rem; color: #5c6f64; margin-top: 0.35rem; font-weight: 600;">{delta}</div>' if delta else ''}
        </div>
        """,
        unsafe_allow_html=True
    )

def render_coconut_gallery():
    """Renders the Coconut Health in Focus organic image gallery."""
    st.markdown("### 🌴 Coconut Health in Focus")
    st.markdown("<p style='color: #5c6f64; margin-top: -0.5rem; margin-bottom: 1.25rem;'>Visual reference library for coconut palm canopy health and field diagnostics.</p>", unsafe_allow_html=True)

    g1, g2, g3, g4 = st.columns(4)
    img_dir = os.path.join(os.path.dirname(__file__), "..", "assets", "images")

    gallery_items = [
        {"title": "Coconut Plantation", "desc": "Lush tropical grove", "file": "hero_coconut_plantation.png"},
        {"title": "Healthy Leaf Frond", "desc": "Deep green leaf veins", "file": "coconut_leaf_detail.png"},
        {"title": "Crown Symmetry", "desc": "Robust flowering canopy", "file": "healthy_coconut_tree.png"},
        {"title": "Sustainable Farm", "desc": "Aerated palm basin", "file": "coconut_grove.png"}
    ]

    cols = [g1, g2, g3, g4]
    for idx, item in enumerate(gallery_items):
        with cols[idx]:
            local_path = os.path.join(img_dir, item["file"])
            if os.path.exists(local_path):
                st.image(local_path, use_container_width=True)
            else:
                st.image(f"http://127.0.0.1:8000/uploads/{item['file']}", use_container_width=True)
            st.markdown(
                f"""
                <div style="padding: 0.25rem 0.5rem 0.5rem 0.5rem;">
                    <h4 style="margin: 0; font-size: 0.95rem; color: #1b4332;">{item['title']}</h4>
                    <p style="margin: 0.2rem 0 0 0; font-size: 0.8rem; color: #5c6f64;">{item['desc']}</p>
                </div>
                """,
                unsafe_allow_html=True
            )
