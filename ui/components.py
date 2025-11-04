from __future__ import annotations
import streamlit as st
from typing import List, Dict, Any
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import os

st.markdown("""
    <style>
    .stImage > img {
        border-radius: 16px;
        transition: 0.3s;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    .stImage > img:hover {
        transform: scale(1.03);
        box-shadow: 0 4px 12px rgba(0,0,0,0.25);
    }
    .product-box {
        text-align: center;
        padding: 0.4em 0.1em;
        border-radius: 12px;
        background-color: rgba(240, 248, 255, 0.25);
        transition: 0.3s;
    }
    .product-box:hover {
        background-color: rgba(180, 220, 255, 0.4);
    }
    </style>
""", unsafe_allow_html=True)

def product_picker(alternatives):
    st.subheader("🛍️ Chọn sản phẩm (tick để so sánh)")
    selected_ids = []

    cols = st.columns(4)
    for i, alt in enumerate(alternatives):
        with cols[i % 4]:
            img_path = alt.get("image", "")
            if img_path and os.path.exists(img_path):
                img = Image.open(img_path)
                st.image(
                    img,
                    caption=f"{alt['id']} – {alt['name']}",
                    use_container_width=True
                )
            else:
                st.warning(f"Không tìm thấy ảnh cho {alt['id']}")
            checked = st.checkbox(f"Chọn {alt['name']}", key=f"chk_{alt['id']}")
            if checked:
                selected_ids.append(alt["id"])

    return selected_ids

def show_results(df_scores, best_row, bar_fig):
    st.markdown("### 📊 **Kết quả DSS**")
    st.dataframe(df_scores, use_container_width=True, height=260)
    st.success(
        f"**Phương án tối ưu:** 🥇 `{best_row['id']}` – **{best_row['name']}**  \n"
        f"Điểm hợp nhất = `{best_row['score_total']:.4f}`"
    )

    st.markdown("#### 🔎 Biểu đồ tổng hợp so sánh")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("##### 🔸 So sánh điểm SAW & TOPSIS")
        st.pyplot(bar_fig)

    with col2:
        fig2, ax2 = plt.subplots(figsize=(4.5, 4))
        idx = np.arange(len(df_scores))
        ax2.barh(idx, df_scores["score_saw"], label="SAW")
        ax2.barh(idx, df_scores["score_topsis"], left=df_scores["score_saw"], label="TOPSIS")
        ax2.set_yticks(idx)
        ax2.set_yticklabels(df_scores["id"].tolist())
        ax2.set_xlabel("Điểm")
        ax2.legend()
        st.pyplot(fig2)

    st.markdown("#### 🌐 Radar Chart: Hiệu năng theo từng tiêu chí")


    criteria = ["C1", "C2", "C3", "C4"]
    crit_labels = ["Giá bán", "Độ bền", "Ý nghĩa", "Rủi ro tồn kho"]
    colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"]

    fig_radar = plt.figure(figsize=(5, 5))
    ax = fig_radar.add_subplot(111, polar=True)
    angles = np.linspace(0, 2 * np.pi, len(criteria), endpoint=False).tolist()
    angles += angles[:1]

    for i, row in df_scores.iterrows():
        vals = row[["score_saw", "score_topsis"]].mean() * np.ones(len(criteria))
        vals = np.append(vals, vals[0])
        ax.plot(angles, vals, label=row["id"], linewidth=2)
        ax.fill(angles, vals, alpha=0.15)

    ax.set_thetagrids(np.degrees(angles[:-1]), crit_labels)
    ax.set_title("Hiệu năng trung bình theo tiêu chí", va="bottom")
    ax.legend(loc="upper right", bbox_to_anchor=(1.3, 1.1))
    st.pyplot(fig_radar)
