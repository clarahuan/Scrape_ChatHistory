import io
import json
import unittest
import zipfile
from datetime import date
from pathlib import Path
from docx import Document
from streamlit.testing.v1 import AppTest
from chat_core import load_messages, filter_messages, export_bundle

class ChatTests(unittest.TestCase):
    def setUp(self):
        self.messages = load_messages(Path('sample_messages.json').read_bytes(), 'sample.json')

    def test_boundary_and_filters(self):
        result = filter_messages(self.messages, ['friend_001'], date(2026,10,20), date(2026,10,20))
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['dt'].second, 59)
        self.assertFalse(filter_messages(self.messages, [], date(2026,10,18), date(2026,10,21)))
        self.assertEqual(len(filter_messages(self.messages, ['group_001'], date(2026,10,18), date(2026,10,21), '方案', ['text'])), 1)
        with self.assertRaises(ValueError):
            filter_messages(self.messages, [], date(2026,10,21), date(2026,10,18))

    def test_import(self):
        for bad in (b'{}', b'[]', b'[{"sender":"a"}]', b'not json'):
            with self.assertRaises(ValueError):
                load_messages(bad, 'x.json')
        csv_data = 'conversation_id,conversation,sender,timestamp,type,content\na,测试,我,2026-10-20T16:00:00Z,text,hello'
        m = load_messages(csv_data.encode('utf-8-sig'), 'x.csv')[0]
        self.assertEqual(m['dt'].date(), date(2026,10,21))

    def test_exports(self):
        docx, pdf, archive = export_bundle(self.messages, date(2026,10,18), date(2026,10,21), '虚构示例数据，仅用于测试。')
        doc = Document(io.BytesIO(docx))
        text = '\n'.join(p.text for p in doc.paragraphs)
        self.assertIn('附件未嵌入', text)
        self.assertIn('方案已经确认', text)
        with zipfile.ZipFile(io.BytesIO(archive)) as z:
            self.assertEqual(len(z.namelist()), 5)
            self.assertTrue(all('/' not in n and '\\' not in n for n in z.namelist()))
        Path('tmp').mkdir(exist_ok=True)
        Path('tmp/test.docx').write_bytes(docx)
        Path('tmp/test.pdf').write_bytes(pdf)

    def test_ui(self):
        at = AppTest.from_file('app.py', default_timeout=20).run()
        self.assertFalse(at.exception)
        self.assertEqual(at.metric[0].value, '6')
        at.button(key='generate').click().run()
        self.assertFalse(at.exception)
        self.assertTrue(at.success)
        at.text_input[0].set_value('不存在的词').run()
        self.assertFalse(at.exception)
        self.assertFalse(at.success)
        at.text_input[0].set_value('方案').run()
        self.assertFalse(at.exception)
        self.assertFalse(at.success)
        at.segmented_control(key='source').set_value('导入文件').run()
        self.assertFalse(at.exception)

if __name__ == '__main__':
    unittest.main()
