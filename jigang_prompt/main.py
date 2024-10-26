import streamlit as st
from zhipuai import ZhipuAI
import os

# 从环境变量获取API密钥
api_key = os.getenv("ZHIPUAI_API_KEY")

# 如果环境变量中没有API密钥，则提示用户输入
if not api_key:
    api_key = st.text_input("请输入您的智谱AI API密钥:", type="password")
    if not api_key:
        st.error("请提供有效的API密钥才能继续。")
        st.stop()

# 初始化ZhipuAI客户端
client = ZhipuAI(api_key=api_key)

def convert_lisp_to_prompt(lisp_code, output_format):
    try:
        system_content = """你是一个专业的程序员，擅长将 Lisp 伪代码转换为详细的自然语言提示词。你的任务是完全理解 Lisp 代码的每个细节，然后创建一个全面的提示词，确保原始代码中的所有信息都被准确转换。"""
        
        user_content = f"""请仔细分析以下 Lisp 伪代码，并将其转换为详细的自然语言提示词。转换时必须严格遵循以下要求：

1. 完全理解并保留 Lisp 代码的每个细节，包括但不限于：
   - 所有函数及其功能
   - 所有变量及其用途
   - 数据结构和算法
   - 控制流程和逻辑
   - 任何特殊的计算或处理步骤
2. 将每个代码元素转换为清晰的自然语言描述，确保不遗漏任何信息。
3. 保持原始代码的结构和逻辑顺序，以自然语言形式呈现。
4. 使用非技术性语言解释复杂的概念，但保持技术准确性。
5. {"将所有 SVG 相关的描述准确转换为等效的 HTML5 和 CSS 描述，确保视觉效果和功能保持一致。" if output_format == "HTML5" else "保留所有关于生成 SVG 的描述，确保可以准确生成 SVG 图形。"}
6. 提供足够的细节，使得根据此提示词可以准确重建原始功能。
7. 直接返回转换后的提示词，不要包含任何额外解释、注释或原始代码。

Lisp 伪代码：
{lisp_code}"""

        response = client.chat.completions.create(
            model="glm-4-flashx",
            messages=[
                {"role": "system", "content": system_content},
                {"role": "user", "content": user_content}
            ]
        )
        prompt = response.choices[0].message.content
        return prompt.strip()
    except Exception as e:
        st.error(f"转换过程中发生错误: {str(e)}")
        return None

def generate_response(prompt, user_input, output_format):
    try:
        user_message = ""
        if output_format == "HTML5":
            user_message = f"请生成html5卡片代码,要求尽量美观，输入为: {user_input}"
        else:  # SVG
            user_message = f"请生成SVG代码,要求尽量美观，输入为: {user_input}"
        
        response = client.chat.completions.create(
            model="glm-4-flashx",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": user_message}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"生成响应时发生错误: {str(e)}")
        return None

def extract_code(response, output_format):
    if output_format == "HTML5":
        start = response.lower().find('<!doctype html')
        if start == -1:
            start = response.lower().find('<html')
        end = response.lower().rfind('</html>') + 7
        if start == -1 or end == -1:
            # 如果没有找到完整的HTML标签，尝试匹配body内容
            start = response.lower().find('<body')
            end = response.lower().rfind('</body>') + 7
            if start == -1 or end == -1:
                # 如果仍然没有找到，尝试匹配任何HTML内容
                start = response.find('<')
                end = response.rfind('>') + 1
    else:  # SVG
        start = response.find('<svg')
        end = response.find('</svg>', start) + 6
    
    if start != -1 and end != -1:
        return response[start:end]
    return None

st.title("李继刚提示词转换器")

# 使用session_state来保存状态
if 'prompt' not in st.session_state:
    st.session_state.prompt = None
if 'output_format' not in st.session_state:
    st.session_state.output_format = None

lisp_code = st.text_area("请输入lisp伪代码提示词:", height=300)

output_format = st.radio("选择输出格式:", ("SVG", "HTML5"))

if st.button("转换"):
    if lisp_code:
        st.session_state.prompt = convert_lisp_to_prompt(lisp_code, output_format)
        st.session_state.output_format = output_format
        
if st.session_state.prompt:
    st.subheader("转换后的提示词:")
    st.text_area("提示词", st.session_state.prompt, height=200)
    
    st.subheader("生成:")
    user_input = st.text_input("请输入:")
    
    if st.button("生成"):
        if user_input:
            response = generate_response(st.session_state.prompt, user_input, st.session_state.output_format)
            if response:
                code_content = extract_code(response, st.session_state.output_format)
                if code_content:
                    st.subheader("预览:")
                    st.components.v1.html(code_content, height=600)
                    st.subheader("生成的代码:")
                    st.code(code_content, language="html" if st.session_state.output_format == "HTML5" else "xml")
                    
                else:
                    st.write(response)
        else:
            st.warning("请先输入")
else:
    st.warning("请先转换lisp伪代码提示词")
