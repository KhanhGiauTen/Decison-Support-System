from __future__ import annotations
import os
import numpy as np
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from pymongo import MongoClient

from data.loader import load_from_json, load_from_mongo
from dss.engine import ahp_weights_from_pairwise, saw_score, topsis_score
from ui.components import product_picker, show_results

from data.DataWarehouse import connect

st.set_page_config(page_title="DSS chọn sản phẩm 20/11", layout="wide")

st.title("🌸 DSS chọn sản phẩm cho chiến dịch 20/11 (La vie est belle)")
st.caption("UI · Data · DSS Engine — AHP → SAW/TOPSIS")


tab1, tab2 = st.tabs(["📊 DSS Phân tích lựa chọn", "🗄️ Quản lý kho dữ liệu"])


with tab1:
    with st.sidebar:
        st.header("⚙️ Data Source")
        db_name = st.text_input("DB Name", value=os.getenv("MONGO_DB", "flower_shop"))
        col_name = st.text_input("Collection", value=os.getenv("MONGO_COL", "flowers"))

        st.header("⚖️ AHP Weights")
        weight_source = st.radio("Nguồn trọng số", ["Cố định (từ AHP)"])

    DATA_PATH = os.path.join("data", "data.json")
    json_data = load_from_json(DATA_PATH)

    criteria = json_data["criteria"]
    weights = json_data.get("weights", {})
    alternatives = json_data["alternatives"]

    selected_ids = product_picker(alternatives)
    if not selected_ids:
        st.info("Hãy chọn ít nhất 1 sản phẩm để tiếp tục.")
        st.stop()
    alts = [a for a in alternatives if a["id"] in selected_ids]

    crit_ids = [c["id"] for c in criteria]
    crit_types = [c["type"] for c in criteria]

    X = np.array([[alt["values"][cid] for cid in crit_ids] for alt in alts], dtype=float)

    weight_source == "Cố định (từ AHP)"
    w = np.array([weights[cid] for cid in crit_ids], dtype=float)
       

    saw = saw_score(X, crit_types, w)
    topsis, ideal_pos, ideal_neg = topsis_score(X, crit_types, w)

    def minmax(v):
        if v.max() == v.min():
            return np.ones_like(v)
        return (v - v.min()) / (v.max() - v.min())

    saw_n = minmax(saw)
    top_n = minmax(topsis)
    total = 0.5 * saw_n + 0.5 * top_n

    df = pd.DataFrame({
        "id": [a["id"] for a in alts],
        "name": [a["name"] for a in alts],
        "score_saw": saw,
        "score_topsis": topsis,
        "score_total": total
    }).sort_values(by="score_total", ascending=False).reset_index(drop=True)

    st.markdown("### 🔍 Bảng so sánh")
    st.dataframe(df, use_container_width=True, height=260)
    best = df.iloc[0]

    fig = plt.figure()
    ax = fig.add_subplot(111)
    idx = np.arange(len(df))
    ax.bar(idx - 0.15, df["score_saw"].values, width=0.3, label="SAW")
    ax.bar(idx + 0.15, df["score_topsis"].values, width=0.3, label="TOPSIS")
    ax.set_xticks(idx)
    ax.set_xticklabels(df["id"].tolist())
    ax.set_xlabel("Phương án")
    ax.set_ylabel("Điểm")
    ax.legend()

    show_results(df, best, fig)

    st.caption("Mẹo: Bật 'Dùng MongoDB' và nhập URI/DB/Collection để truy vấn kho dữ liệu thực tế. Nếu không, app dùng data.json.")


with tab2:
    st.subheader("🗄️ Quản lý kho dữ liệu (MongoDB)")
    collection = connect()

    st.markdown("#### 📋 Dữ liệu hiện tại trong MongoDB")
    data = list(collection.find())
    if data:
        df_data = pd.DataFrame([
            {
                "_id": d.get("_id"),
                "name": d.get("name"),
                "image": d.get("image"),
                **d.get("values", {})
            } for d in data
        ])
        st.dataframe(df_data, use_container_width=True, height=300)
    else:
        st.info("⚠️ Chưa có dữ liệu trong kho.")

    st.markdown("---")
    st.markdown("#### ➕ Thêm sản phẩm mới")

    with st.form("add_flower"):
        new_id = st.text_input("Mã hoa (_id)", placeholder="A5")
        new_name = st.text_input("Tên hoa")
        new_img = st.text_input("Đường dẫn ảnh (ví dụ: assets/A5.png)")
        c1 = st.number_input("C1 – Giá bán", min_value=0.0)
        c2 = st.number_input("C2 – Độ bền", min_value=0.0)
        c3 = st.number_input("C3 – Ý nghĩa", min_value=0.0)
        c4 = st.number_input("C4 – Rủi ro tồn kho", min_value=0.0)
        submit = st.form_submit_button("Thêm hoa mới")

        if submit:
            if collection.find_one({"_id": new_id}):
                st.warning("❗ ID này đã tồn tại, vui lòng chọn ID khác.")
            else:
                doc = {
                    "_id": new_id,
                    "name": new_name,
                    "image": new_img,
                    "values": {"C1": c1, "C2": c2, "C3": c3, "C4": c4}
                }
                collection.insert_one(doc)
                st.success(f"✅ Đã thêm '{new_name}' vào kho dữ liệu!")

    st.markdown("---")
    st.markdown("#### ✏️ Cập nhật dữ liệu sản phẩm")
    edit_id = st.text_input("Nhập ID hoa cần cập nhật")
    if edit_id:
        flower = collection.find_one({"_id": edit_id})
        if flower:
            field = st.selectbox("Chọn trường cần sửa", ["name", "image", "values.C1", "values.C2", "values.C3", "values.C4"])
            new_val = st.text_input("Giá trị mới")
            if st.button("Cập nhật"):
                try:
                    val = float(new_val) if field.startswith("values.") else new_val
                    collection.update_one({"_id": edit_id}, {"$set": {field: val}})
                    st.success("✅ Cập nhật thành công!")
                except Exception as e:
                    st.error(f"Lỗi khi cập nhật: {e}")
        else:
            st.warning("Không tìm thấy ID này trong cơ sở dữ liệu.")
