import PyPDF2
import re

def read_pdf_sample():
    with open('../data/专业列表.pdf', 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ''
        for page in reader.pages[:3]:
            text += page.extract_text()
        print('PDF前3页内容预览:')
        print(text[:1500])
        
        # 尝试提取专业信息
        lines = text.split('\n')
        print('\n前20行内容:')
        for i, line in enumerate(lines[:20]):
            print(f"{i+1}: {line}")

if __name__ == "__main__":
    read_pdf_sample()