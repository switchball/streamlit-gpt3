import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

from utils.workspace import WorkspaceManager
from utils.diagram import get_plantuml_diagram, get_common_diagram

# 用户界面模块
def main(name):
    st.title(f"[WIP] Batched Prompt Evaluation Tool ({name})")

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

def process_input_dataframe(df):
    """
    将以 'input.' 开头的列名处理为新的列名，并提取 '.' 分割后的内容作为新的列。

    输入：
    df (pandas.DataFrame): 需要进行处理的DataFrame。

    用法：
    new_df = process_dataframe(df)

    作用：
    遍历DataFrame的列，找到以 'input.' 开头的列名，提取 '.' 分割后的内容作为新的列名，并返回处理后的新DataFrame。

    返回结果：
    pandas.DataFrame: 处理后的新DataFrame。

    示例：
    >>> import pandas as pd
    >>> data = {'input.name': ['Alice', 'Bob', 'Charlie'],
    ...         'input.age': [25, 30, 35],
    ...         'score': [80, 90, 75]}
    >>> df = pd.DataFrame(data)
    >>> new_df = process_dataframe(df)
    >>> print(new_df)
          name  age
    0    Alice   25
    1      Bob   30
    2  Charlie   35
    """
    new_columns = {}
    index_counter = {}

    for column in df.columns:
        if column.lower() == 'input' or column.lower().startswith('input.'):
            new_column = column.split('.')[-1]
            if not new_column:
                new_column = 'input'

            # 处理重复的列名
            if new_column in new_columns:
                if new_column not in index_counter:
                    index_counter[new_column] = 1
                else:
                    index_counter[new_column] += 1

                new_column = f"{new_column}_{index_counter[new_column]}"

            new_columns[column] = new_column

    new_df = df.copy()  # 拷贝原始DataFrame

    # 重命名列
    new_df.rename(columns=new_columns, inplace=True)

    # 保留新列名对应的列
    new_df = new_df[[col for col in new_df.columns if col in new_columns.values()]]

    return new_df

if __name__ == "__main__":
    st.set_page_config(page_title="Batch Prompt Tool", layout="wide", initial_sidebar_state="collapsed")
    wm_instance = WorkspaceManager.init_workspace('BatchPrompt', default_selection='demo')
    if wm_instance is None:
        st.stop()
    workspace_name = wm_instance.workspace_name

    main(workspace_name)
    st.sidebar.info("""A. 能够批量评估 prompt 效果的工具""")
    st.sidebar.text("拥有以下几大模块：\n1. 用户界面模块(上传数据集)\n2. 数据处理模块(数据清洗,预处理)\n"
                    "3. Prompt 流程模板模块(LLM)\n4. 反馈评分模块(对数据打标)")
    st.sidebar.info("""B. 数据按 worksapce 隔离""")
    st.sidebar.text("有如下特点：\n1. 云端存储, 用完即走\n2. 可以参观访问他人的 workspace")
    st.sidebar.info("""C. 评估迭代的效果""")
    st.sidebar.text("1. 当用户修改流程中环节后，重新跑一遍数据集，给出打分\n2. Good/Bad Case 修正：将用例作为梯度反馈回流程中\n"
                    "3. 追踪比较不同流程下的效果，沉淀经验和案例")
    st.__version__

    # Simple Flow using Blockdiag
    block_diag_data = """blockdiag {
        "Input 1,2,3, ..." -> process -> "Output 1,2,3, ...";
    
        "Input 1,2,3, ..." [color = "greenyellow"];
        "process" [color = "pink"];
        "Output 1,2,3, ..." [color = "orange"];
    }"""

    st.subheader("基础形式")
    st.text("基本的数据流：输入 -> 处理函数 -> 输出。当输入是序列时，输出也是序列。")
    st.text("在这个数据流中，我们可以修改输入，从而影响输出。")
    st.image(get_common_diagram(block_diag_data, diagram_type="blockdiag"))

    block_diag_data = """blockdiag {
        "Input 1,2,3, ..." -> process -> "Output 1,2,3, ...";
        "Input 1,2,3, ..." -> "process(Variant)" -> "Output 1',2',3', ...";

        "Input 1,2,3, ..." [color = "greenyellow"];
        "process" [color = "pink"];
        "process(Variant)" [color = "pink"]
        "Output 1,2,3, ..." [color = "orange"];
        "Output 1',2',3', ..." [color = "orange"];
    }"""

    st.text("进阶的情况：处理函数也可能会发生变化，从而改变一整批数据的处理逻辑。")
    st.image(get_common_diagram(block_diag_data, diagram_type="blockdiag"))

    st.subheader("数据格式")
    st.markdown("输入(Input): 每组输入会有1个或多个参数，比如以 `input.name`、`input.age` 来表示有name和age两个槽位可供填充")
    st.markdown("处理(Process): 每个处理过程都可以表示为一个 DAG 有向无环图，图的节点在执行时会带上其上游节点的输出，以及输入的槽位")
    st.markdown("输出(Output): DAG 的最后一个节点的输出会作为整个流程的输出，如果 DAG 指定了不止一个最后节点，也可能会有多个输出")

    st.subheader("DAG 图的节点")
    st.markdown("- 最基本的节点是 LLM_Chat：把上游的输入作为 LLM 的提示词，从而得到 LLM 的相应作为输出（i.e. Basic Chat）")
    st.markdown("- 字符串拼接节点 Str_Tplt：有预留空位的提示词目标，会将输入参数代入（i.e. Prompt + QA）")


    st.markdown("---")
    st.subheader("开始")
    st.text("输入的内容一般来自数据库（目前支持以 Google Sheet 作为数据库）")
    gsheet_url = st.text_input("输入gsheet url")
    if gsheet_url.startswith("https://docs.google.com"):
        conn = st.experimental_connection("gsheets", type=GSheetsConnection)
        allData = conn.read(spreadsheet=gsheet_url) #, usecols=[0, 1])
    else:
        allData = None
    
    col_in, col_process, col_out = st.columns(3)
    with col_in:
        with st.expander("输入"):
            if allData is not None:
                st.dataframe(process_input_dataframe( allData ))
            else:
                st.text("No data")
    
    with col_process:
        with st.expander("预处理"):
            st.selectbox("处理方式", options=["Basic Chat", "Prompt + QA"])
    
    with col_out:
        with st.expander("输出"):
            st.text_area("输出结果")


    # 测试
    original_data = """title Batched Prompt Evaluation Tool

== Evaluation Phase ==

participant "User Interface" as UI order 1
participant "Data Processing" as DP order 2
participant "Prompt" as LM order 3
participant "Feedback Recording" as FR order 4

UI -> DP : Upload Dataset
UI -> LM : Select Prompt Template
DP -> LM : Process Data
LM -> FR : Evaluate Results

== Iterate Phase ==

UI -> LM : Modify Prompt Template
LM -> DP : Re-process Data
DP -> LM : Re-evaluate Results
LM -> FR : Generate New Feedback
FR -> UI : Send Feedback to User
    """
    diag_str = st.text_area("Diagram", value=original_data)

    st.image(get_plantuml_diagram(diag_str))
