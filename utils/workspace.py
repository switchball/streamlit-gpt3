import streamlit as st
import os
import json
import re

WORKSPACE_DIR = os.path.join(os.getcwd(), "workspaces")


class WorkspaceManager:
    def __init__(self, module_url_prefix):
        self.module_url_prefix = module_url_prefix
        self.current_password = None
        self._workspace_name = None
        # 创建工作区文件夹
        os.makedirs(WORKSPACE_DIR, exist_ok=True)

    @property
    def workspace_name(self):
        return self._workspace_name

    def create_workspace(self, workspace_name, password, is_private):
        # 校验工作区名称
        if not re.match(r'^[a-zA-Z0-9_-]{1,24}$', workspace_name):
            st.error("Invalid workspace name. Workspace name must contain only alphanumeric characters, hyphens, underscores and should not exceed 24 characters.")
            return None
        # 在工作区文件夹下创建具体工作区文件夹
        workspace_dir = os.path.join(WORKSPACE_DIR, workspace_name)
        os.makedirs(workspace_dir, exist_ok=True)

        # 保存工作区元信息到配置文件
        meta_file = os.path.join(workspace_dir, "config.json")
        with open(meta_file, "w") as f:
            config = {
                "Workspace Name": workspace_name,
                "Password": password,
                "Is Private": is_private
            }
            json.dump(config, f)

        return workspace_dir

    def validate_password(self, workspace_dir, password):
        # 读取工作区配置文件中的密码
        meta_file = os.path.join(workspace_dir, "config.json")
        with open(meta_file, "r") as f:
            config = json.load(f)
            correct_password = config["Password"]

        # 验证密码是否正确
        if password == correct_password:
            return True
        else:
            return False
        
    def is_workspace_private(self, workspace_dir):
        # 判断工作区是否为私有
        meta_file = os.path.join(workspace_dir, "config.json")
        with open(meta_file, "r") as f:
            config = json.load(f)
            is_private = config.get("Is Private", False)
        return is_private
    
    def is_workspace_exist(self, workspace_dir):
        try:
            meta_file = os.path.join(workspace_dir, "config.json")
            with open(meta_file, "r") as f:
                config = json.load(f)
        except Exception:
            return False
        return True
        

    def display_workspace_selection(self, default_selection=None):
        workspaces = os.listdir(WORKSPACE_DIR)
        options = ["Create New Workspace"] + workspaces
        k = options.index(default_selection) if default_selection in options else 0

        selected_option = st.selectbox("Select a Workspace", options, index=k)
        if selected_option == "Create New Workspace":
            workspace_name = st.text_input("Enter Workspace Name")
            password = st.text_input("Enter Password", type="password")
            is_private = st.checkbox("Private Workspace")

            if st.button("Create Workspace"):
                workspace_dir = self.create_workspace(workspace_name, password, is_private)
                if workspace_dir is not None:
                    st.info(f"Workspace '{workspace_name}' created successfully!")
                    st.markdown(self.get_link(workspace_name))
                    st.stop()
        else:
            workspace_name = selected_option
            workspace_dir = os.path.join(WORKSPACE_DIR, workspace_name)
            is_private = self.is_workspace_private(workspace_dir)
            if is_private:
                st.warning('注意：该工作区是私有的，需要提供密码才可访问，点击按钮继续')
            else:
                st.success('该工作区是公开的，任何人都可访问，点击按钮继续')

            if st.button("Access Workspace"):
                st.markdown(self.get_link(workspace_name))

    def get_link(self, workspace_name):
        module_name = self.module_url_prefix.replace("/", "")
        return f"[点击此链接进入 `{workspace_name}` 工作区](/{module_name}?workspace={workspace_name})"

    def manage_workspaces(self, default_selection=None):
        # 获取URL参数
        url_params = st.experimental_get_query_params()
        workspace_param = url_params.get("workspace", None)

        # 判断URL中是否包含workspace参数
        if workspace_param is None:
            self.display_workspace_selection(default_selection)
            return None
        else:
            workspace_name = workspace_param[0]
            workspace_dir = os.path.join(WORKSPACE_DIR, workspace_name)
            if not self.is_workspace_exist(workspace_dir):
                st.warning(f'工作区 `{workspace_name}` 不存在')
                self.display_workspace_selection(default_selection)
                return None
            is_private = self.is_workspace_private(workspace_dir)

            if is_private:
                if self.current_password is None:
                    self.current_password = st.session_state.get('password', '')
                
                # 直接先行快速验证
                if self.validate_password(workspace_dir, self.current_password):
                    return workspace_name

                password = st.text_input("Enter Password", type="password", value=self.current_password)
                if st.button("Access Workspace"):
                    if self.validate_password(workspace_dir, password):
                        st.success(f"Access granted to workspace '{workspace_name}'!")
                        # st.info(f"Workspace directory: {workspace_dir}")
                        # st.markdown(self.get_link(workspace_name))
                        # 保存密码到session_state
                        st.session_state['password'] = password
                        return workspace_name
                    else:
                        st.error("Incorrect password! Access denied.")
                        return None
            else:
                st.info(f"You are accessing public workspace '{workspace_name}'!")
                # st.info(f"Workspace directory: {workspace_dir}")
                # st.markdown(self.get_link(workspace_name))
                return workspace_name

    @classmethod
    def init_workspace(cls, module_url_prefix, default_selection=None):
        # 创建登录占位符，展示登录界面
        placeholder = st.empty()
        with placeholder.container():
            wm = cls(module_url_prefix)
            workspace_name = wm.manage_workspaces(default_selection)

        if workspace_name is None:
            # 初始化工作区失败，下游应当使用 st.stop() 阻止继续
            # st.stop()
            return None
        else:
            # 初始化工作区成功，清空登录占位符，返回工作区实例
            placeholder.empty()
            wm._workspace_name = workspace_name
            return wm