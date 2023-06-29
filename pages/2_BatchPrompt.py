import streamlit as st
import pandas as pd

# 用户界面模块
def main():
    st.title("[WIP] Batched Prompt Evaluation Tool")

    # 上传数据集
    uploaded_file = st.file_uploader("Upload Dataset", type="csv")

    if uploaded_file is not None:
        data = pd.read_csv(uploaded_file)

        # 显示数据集信息
        st.subheader("Dataset Information")
        st.write(data.head())

        # 选择流程模板
        template = st.selectbox("Select Prompt Template", ["Template 1", "Template 2", ...])

        # 对数据集应用流程模板
        processed_data = process_data(data, template)

        # 展示处理后的结果
        st.subheader("Processed Data")
        st.write(processed_data.head())

        # 评分结果和反馈
        scores = evaluate_results(processed_data)

        # 显示结果并记录反馈
        show_results_with_feedback(processed_data, scores)

# Prompt 流程模板模块
def process_data(data, template):
    processed_data = data
    if template == "Template 1":
        # 模板1的处理逻辑
        # ...
        return processed_data
    elif template == "Template 2":
        # 模板2的处理逻辑
        # ...
        return processed_data
    # ...

# 评分模块
def evaluate_results(processed_data):
    scores = [0, 0, 0, 0]
    # 根据预定的评分标准对结果进行评分
    # ...
    return scores

# 结果展示和反馈记录模块
def show_results_with_feedback(processed_data, scores):
    for i, result in enumerate(processed_data.iterrows()):
        st.subheader(f"Result {i+1}")
        st.write(result)

        # 创建评分和反馈输入框
        score = st.number_input("Score (0-10)", min_value=0, max_value=10, key=f"score_{i}")
        feedback = st.text_area("Feedback", key=f"feedback_{i}")

        # 记录用户的评分和反馈
        record_feedback(result, score, feedback)

# 反馈记录模块
def record_feedback(result, score, feedback):
    # 将评分和反馈记录到数据库或文件中
    # ...
    pass

if __name__ == "__main__":
    main()
    st.sidebar.info("""A. 能够批量评估 prompt 效果的工具""")
    st.sidebar.text("拥有以下几大模块：\n1. 用户界面模块(上传数据集)\n2. 数据处理模块(数据清洗,预处理)\n"
                    "3. Prompt 流程模板模块(LLM)\n4. 反馈评分模块(对数据打标)")
    st.sidebar.info("""B. 数据按 worksapce 隔离""")
    st.sidebar.text("有如下特点：\n1. 云端存储, 用完即走\n2. 可以参观访问他人的 workspace")
    st.sidebar.info("""C. 评估迭代的效果""")
    st.sidebar.text("1. 当用户修改流程中环节后，重新跑一遍数据集，给出打分\n2. Good/Bad Case 修正：将用例作为梯度反馈回流程中\n"
                    "3. 追踪比较不同流程下的效果，沉淀经验和案例")
    st.__version__

    st.image("https://www.plantuml.com/plantuml/svg/PP7DJiCm48JlVefLxptmSweKLA5I5Ab5KMaUO76srCAnBNi3uktPf35ouJhpsJCUhnDZvA6tIh5XI_28hC_KGHDz7nYUFj4EoCOxE7elL5MLMdF6H51LIWMCRBG9w1WMRQ88jMEA9zIq04pGrk1Z9_BDDRf1nZ5CKqh6lK_iffdPsslsqcb2TliPkRj6jaJT6-eFE90M8D-uFSpulLBIPFamPgoW3TPZ1sE7H3mxkxquhsH9SrxXI7smoAGsJIPov-cm4aLqILdbTKWQfC5ocYQhcQ9enLv5rjvtvlJzBqkytFD0or365JN4eh-9HPjdSfVa5_g2F8uIIu2sdXxgkby3sCFuTqgjHHvw-mC0")