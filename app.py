import hashlib
from datetime import datetime
from pathlib import Path
import streamlit as st
from chat_core import load_messages, filter_messages, export_bundle, TZ

st.set_page_config(page_title='聊天记录导出工具', page_icon=':material/forum:', layout='wide')
st.title('聊天记录导出工具')
st.caption('本机处理 · 按会话和日期整理 · Word / PDF')
st.session_state.setdefault('export_result', None)
source = st.segmented_control('数据来源', ['示例数据', '导入文件'], default='示例数据', key='source')
template = Path(__file__).with_name('sample_messages.json').read_bytes()
if source == '示例数据':
    st.warning('当前使用虚构示例，尚未连接你的微信。导出文件也会标记为示例数据。')
    data, filename, source_label = template, 'sample_messages.json', '虚构示例数据'
else:
    st.info('仅支持本工具规定的 JSON/CSV 格式，不能直接导入微信数据库或备份。文件只在本机进程内处理。')
    st.download_button('下载 JSON 格式示例', template, 'sample_messages.json', 'application/json')
    uploaded = st.file_uploader('选择消息文件（UTF-8，最多 20 MB）', type=['json', 'csv'])
    with st.expander('查看导入格式'):
        st.code('conversation_id,conversation,sender,timestamp,type,content\nfriend_001,张三,我,2026-10-20 10:30:00,text,你好', language='text')
        st.caption('每条记录都需要以上六个字符串字段。无时区的时间按北京时间处理；type=text 为文字，其他类型仅导出说明，不读取附件。')
    if uploaded is None:
        st.stop()
    data, filename, source_label = uploaded.getvalue(), uploaded.name, '用户导入文件（完整性未经核验）'
try:
    messages = load_messages(data, filename)
except ValueError as exc:
    st.error(str(exc))
    st.stop()
fingerprint = hashlib.sha256(data).hexdigest()
conversations = {m['conversation_id']: m['conversation'] for m in messages}
st.caption(f"已载入 {len(messages)} 条消息、{len(conversations)} 个会话；数据覆盖 {messages[0]['dt']:%Y-%m-%d} 至 {messages[-1]['dt']:%Y-%m-%d}（不代表记录完整）。")
with st.container(border=True):
    ids = st.multiselect('选择会话', list(conversations), default=list(conversations), format_func=lambda x: f'{conversations[x]} · {x}', key=f'ids_{fingerprint}')
    c1, c2 = st.columns(2)
    start = c1.date_input('开始日期', messages[0]['dt'].date(), key=f'start_{fingerprint}')
    end = c2.date_input('结束日期', messages[-1]['dt'].date(), key=f'end_{fingerprint}')
    keyword = st.text_input('关键词（可留空，搜索消息正文）')
    types = st.multiselect('消息类型', sorted({m['type'] for m in messages}), default=sorted({m['type'] for m in messages}), key=f'types_{fingerprint}')
try:
    selected = filter_messages(messages, ids, start, end, keyword, types)
except ValueError as exc:
    st.error(str(exc))
    st.stop()
if not selected:
    st.info('没有符合条件的消息，请调整会话、时间或关键词。')
    st.stop()
nontext = sum(m['type'] != 'text' for m in selected)
c1, c2, c3 = st.columns(3)
c1.metric('符合条件的消息', len(selected))
c2.metric('涉及会话', len({m['conversation_id'] for m in selected}))
c3.metric('附件未嵌入的消息', nontext)
st.caption('时间按北京时间展示，包含结束日期当天。预览最多显示前 500 条，导出包含全部筛选结果。')
st.dataframe([{'会话': m['conversation'], '时间': m['dt'].strftime('%Y-%m-%d %H:%M:%S'), '发送人': m['sender'], '类型': m['type'], '内容': m['content']} for m in selected[:500]], hide_index=True, alt='筛选后的聊天记录预览')
if nontext:
    st.warning('本版仅导出文字及非文字消息的说明，尚不嵌入图片、语音、视频等附件。')
signature = (fingerprint, source_label, tuple(ids), str(start), str(end), keyword, tuple(types))
if st.button('生成 Word、PDF 和批量压缩包', type='primary', key='generate'):
    note = (f'数据来源：{source_label}。筛选日期：{start} 至 {end}（北京时间）。'
            f'关键词：{keyword or "未设置"}。类型：{", ".join(types)}。'
            f'共 {len(selected)} 条消息。非文字消息 {nontext} 条，附件未嵌入。'
            f'导出时间：{datetime.now(TZ):%Y-%m-%d %H:%M:%S}。仅反映导入数据，不保证微信历史记录完整。')
    with st.spinner('正在生成文档，请稍候…'):
        try:
            result = export_bundle(selected, start, end, note)
            st.session_state.export_result = (signature, result)
        except Exception:
            st.error('生成失败。请减少导出消息数量，或检查依赖是否安装齐全。')
stored = st.session_state.export_result
if stored and stored[0] == signature:
    st.success('文件已生成。可以下载合并文档，或按会话分别打包的 ZIP。')
    for label, blob, suffix, mime in zip(['下载合并 Word', '下载合并 PDF', '下载按会话分开的 ZIP'], stored[1], ['docx', 'pdf', 'zip'], ['application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'application/pdf', 'application/zip']):
        st.download_button(label, blob, f'聊天记录_{start}_{end}.{suffix}', mime)
elif stored:
    st.caption('筛选条件已变化，请重新生成文件。')
