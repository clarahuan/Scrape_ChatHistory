import streamlit as st

st.set_page_config(
    page_title="聊天记录导出工具",
    page_icon="💬",
)

st.title("聊天记录导出工具")
st.caption("本地运行 · 第一版原型")

st.info("当前页面尚未连接微信，先验证网页和日期选择功能。")

start_date = st.date_input("开始日期")
end_date = st.date_input("结束日期")

if st.button("检查时间范围"):
    if start_date > end_date:
        st.error("开始日期不能晚于结束日期。")
    else:
        st.success(
            f"已选择：{start_date:%Y-%m-%d} 至 "
            f"{end_date:%Y-%m-%d}"
        )