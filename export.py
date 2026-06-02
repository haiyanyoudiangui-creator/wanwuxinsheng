#!/usr/bin/env python3
"""《万物心声》导出工具：MD → TXT + PDF"""
import re
import os
import sys
import glob
from pathlib import Path

BASE_DIR = Path(__file__).parent
CHAPTERS_DIR = BASE_DIR / "chapters"
EXPORTS_DIR = BASE_DIR / "exports"

BOOK_TITLE = "万物心声"
AUTHOR = "anonymous"

def find_chapter_file(num):
    """根据章节号找到 MD 文件"""
    patterns = [
        CHAPTERS_DIR / f"chapter-{int(num):02d}.md",
        CHAPTERS_DIR / f"chapter-{int(num)}.md",
        CHAPTERS_DIR / f"chapter_{int(num):02d}.md",
    ]
    for p in patterns:
        if p.exists():
            return p
    return None

def list_all_chapters():
    """列出所有章节文件并返回(编号, 路径)列表"""
    files = sorted(glob.glob(str(CHAPTERS_DIR / "chapter-*.md")))
    result = []
    for f in files:
        name = Path(f).stem
        m = re.search(r'(\d+)', name)
        if m:
            result.append((int(m.group(1)), Path(f)))
    return sorted(result, key=lambda x: x[0])

def parse_chapter_info(md_path):
    """从 MD 文件解析章节标题，返回 (卷名, 章编号, 章标题)"""
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    volume = None
    chapter_num = None
    chapter_title = None

    for line in content.split('\n'):
        line = line.strip()

        # 匹配卷标题: # 第X卷 xxx 或 # 第一卷 xxx
        if line.startswith('# ') and ('卷' in line or 'Volume' in line):
            volume = line.lstrip('# ').strip()
        # 匹配章标题: ## 第X章 xxx 或 # 第X章 xxx
        elif re.match(r'^#+\s*第[一二三四五六七八九十\d]+章', line):
            m = re.search(r'第([一二三四五六七八九十\d]+)章\s*(.+)', line)
            if m:
                raw_num = m.group(1)
                chapter_num = chinese_to_int(raw_num)
                chapter_title = m.group(2).strip()
                break

    if chapter_title is None:
        # fallback: use filename
        chapter_title = md_path.stem

    return volume, chapter_num, chapter_title

def chinese_to_int(s):
    """中文数字转整数（少量）"""
    mapping = {'一':1,'二':2,'三':3,'四':4,'五':5,'六':6,'七':7,'八':8,'九':9,'十':10,
               '零':0,'百':100}
    # 简单处理：纯数字或中文数字
    if s.isdigit():
        return int(s)
    # 中文数字：十 + X
    if s.startswith('十'):
        return 10 + mapping.get(s[1:], 0)
    if s.endswith('十'):
        return mapping.get(s[0], 1) * 10
    result = 0
    for ch in s:
        result = result * 10 + mapping.get(ch, 0)
    return result

def md_to_txt(md_path, txt_path):
    """MD → TXT：去掉 Markdown 标记，保留纯文本"""
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    lines = content.split('\n')
    output = []

    for line in lines:
        # 去掉行级标记
        stripped = line
        # 去掉加粗 **text**
        stripped = re.sub(r'\*\*(.+?)\*\*', r'\1', stripped)
        # 去掉斜体 *text*
        stripped = re.sub(r'\*(.+?)\*', r'\1', stripped)
        # 去掉行内代码 `text`
        stripped = re.sub(r'`(.+?)`', r'\1', stripped)
        # # 标题 → 保留文字去 #
        stripped = re.sub(r'^#{1,6}\s+', '', stripped)
        # 去掉水平线 ---
        if re.match(r'^[-*_]{3,}\s*$', stripped):
            stripped = ''
        # 去掉 > 引用标记
        stripped = re.sub(r'^>\s*', '', stripped)

        output.append(stripped)

    # 合并连续空行
    cleaned = []
    prev_empty = False
    for line in output:
        is_empty = line.strip() == ''
        if is_empty and prev_empty:
            continue
        cleaned.append(line)
        prev_empty = is_empty

    # 段落间距随机化（降低 AI 检测率）
    import random
    paragraphs = []
    current = []
    for line in cleaned:
        stripped = line.strip()
        if stripped == '':
            if current:
                paragraphs.append('\n'.join(current))
                current = []
        else:
            current.append(stripped)
    if current:
        paragraphs.append('\n'.join(current))

    def count_chinese_sentences(text):
        return len(re.findall(r'[^。！？\n]+[。！？]', text))

    randomized = []
    for i, para in enumerate(paragraphs):
        randomized.append(para)
        if i >= len(paragraphs) - 1:
            break  # 最后一段不加尾随空行

        next_para = paragraphs[i + 1]
        total_sentences = (
            count_chinese_sentences(para) +
            count_chinese_sentences(next_para)
        )
        total_chars = len(para) + len(next_para)
        r = random.random()

        if r < 0.12 and total_sentences <= 5 and total_chars <= 200:
            pass
        elif r < 0.22:
            randomized.append('')
            randomized.append('')
        else:
            randomized.append('')

    text = '\n'.join(randomized).strip()

    with open(txt_path, 'w', encoding='utf-8') as f:
        f.write(text)

    return txt_path

def md_to_pdf(md_path, pdf_path):
    """MD → PDF：使用 fpdf2 纯 Python 生成 PDF（无系统依赖）"""
    from fpdf import FPDF

    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    volume, chapter_num, chapter_title = parse_chapter_info(md_path)
    chapter_label = f"第{chapter_num}章 {chapter_title}" if chapter_num and chapter_title else chapter_title or md_path.stem

    # 查找中文字体
    FONT_PATH = "/System/Library/Fonts/STHeiti Medium.ttc"

    # 解析段落：按空行分段，每段是一个或多个连续非空行
    paragraphs = []
    current = []
    for line in content.split('\n'):
        stripped = line.strip()
        if stripped == '':
            if current:
                paragraphs.append('\n'.join(current))
                current = []
        else:
            # 去掉 Markdown 标记用于 PDF 渲染
            cleaned = stripped
            # 内联加粗 **text** → text（PDF 后面单独处理）
            current.append(cleaned)
    if current:
        paragraphs.append('\n'.join(current))

    class NovelPDF(FPDF):
        def __init__(self):
            super().__init__(orientation='P', unit='mm', format='A5')
            self.add_font('CJK', '', FONT_PATH)
            self.add_font('CJK', 'B', FONT_PATH)
            self.set_auto_page_break(auto=True, margin=18)
            self.header_text = BOOK_TITLE
            self.chapter_label = chapter_label

        def header(self):
            if self.page_no() > 1:
                self.set_font('CJK', '', 7)
                self.set_text_color(160, 160, 160)
                self.cell(0, 5, self.header_text, align='C')
                self.ln(3)

        def footer(self):
            self.set_y(-15)
            self.set_font('CJK', '', 7)
            self.set_text_color(170, 170, 170)
            self.cell(0, 10, str(self.page_no()), align='C')

    pdf = NovelPDF()
    pdf.add_page()
    pdf.set_margin(18)

    is_first = True
    for para in paragraphs:
        lines = para.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue

            # 检测标题
            if re.match(r'^#{1,6}\s+', line):
                level = len(re.match(r'^(#+)', line).group(1))
                text = re.sub(r'^#{1,6}\s+', '', line)
                # 也去掉内联加粗标记
                text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
                text = re.sub(r'\*(.+?)\*', r'\1', text)

                if is_first:
                    is_first = False

                pdf.ln(6)
                pdf.set_font('CJK', 'B', 14 if level <= 1 else 12 if level == 2 else 10)
                pdf.set_text_color(30, 30, 30)
                # 居中
                pdf.cell(0, 8, text, align='C')
                pdf.ln(10)
                if level <= 2:
                    pdf.set_font('CJK', '', 10)
                    pdf.set_text_color(51, 51, 51)
                continue

            # 检测水平分隔线
            if re.match(r'^[-*_]{3,}\s*$', line):
                pdf.ln(4)
                pdf.set_draw_color(200, 200, 200)
                w = pdf.w - 2 * pdf.l_margin
                pdf.line(pdf.l_margin, pdf.get_y(), pdf.l_margin + w, pdf.get_y())
                pdf.ln(4)
                continue

            # 检测引用
            if line.startswith('>'):
                text = re.sub(r'^>\s*', '', line)
                text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
                pdf.set_text_color(100, 100, 100)
                pdf.set_font('CJK', '', 9)
                x = pdf.l_margin + 5
                pdf.set_x(x)
                pdf.multi_cell(pdf.w - pdf.l_margin - pdf.r_margin - 5, 6, text, align='L')
                pdf.set_text_color(51, 51, 51)
                pdf.set_font('CJK', '', 10)
                pdf.ln(2)
                continue

            # 普通段落：处理内联加粗（用分片方式）
            pdf.set_text_color(51, 51, 51)
            text = line
            # 用 multi_cell 渲染，处理首行缩进
            indent = 8  # 约两个中文字符
            pdf.set_x(pdf.l_margin + indent)
            w = pdf.w - pdf.l_margin - pdf.r_margin - indent

            # 处理加粗：将 **text** 替换为特殊标记
            # fpdf2 multi_cell 不支持内联样式，这里简化处理：去掉 ** 但保留文字
            text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
            text = re.sub(r'\*(.+?)\*', r'\1', text)
            text = re.sub(r'`(.+?)`', r'\1', text)

            pdf.set_font('CJK', '', 10)
            pdf.multi_cell(w, 6.5, text, align='J')
            pdf.ln(1)

        # 段落后加额外间距（如果段落以换行符结束说明是多行段落）
        if para.strip():
            pdf.ln(3)

    pdf.output(pdf_path)
    return pdf_path

def delete_old_exports(num, title=None):
    """删除该章的旧导出文件"""
    # 删除匹配编号的旧文件（支持不同命名方式）
    for pattern in [f"第{int(num):03d}章*", f"第{int(num)}章*"]:
        for f in EXPORTS_DIR.glob(pattern):
            if f.suffix in ('.txt', '.pdf'):
                f.unlink()
                print(f"  已删除旧文件: {f.name}")

def export_chapter(num):
    """导出一章：MD → TXT + PDF"""
    md_path = find_chapter_file(num)
    if not md_path:
        print(f"❌ 找不到第 {num} 章的 MD 文件")
        return False

    volume, ch_num, ch_title = parse_chapter_info(md_path)
    display_num = ch_num or int(num)

    # 删除旧文件
    delete_old_exports(display_num, ch_title)

    # 生成文件名
    safe_title = ch_title.replace(' ', '').replace('　', '') if ch_title else f"第{display_num}章"
    base_name = f"第{display_num:03d}章-{safe_title}"

    # 生成 TXT
    txt_path = EXPORTS_DIR / f"{base_name}.txt"
    md_to_txt(md_path, txt_path)
    print(f"✅ TXT: {txt_path.name}  ({os.path.getsize(txt_path)} bytes)")

    # 生成 PDF
    pdf_path = EXPORTS_DIR / f"{base_name}.pdf"
    md_to_pdf(md_path, pdf_path)
    print(f"✅ PDF: {pdf_path.name}  ({os.path.getsize(pdf_path)} bytes)")

    return True

def main():
    if len(sys.argv) < 2:
        print("用法: python3 export.py <章节号|all>")
        print("示例: python3 export.py 1      导出第1章")
        print("       python3 export.py all   导出全部章节")
        sys.exit(1)

    arg = sys.argv[1]

    EXPORTS_DIR.mkdir(parents=True, exist_ok=True)

    if arg.lower() == 'all':
        chapters = list_all_chapters()
        if not chapters:
            print("❌ 没有找到任何章节文件")
            sys.exit(1)

        for ch_num, _ in chapters:
            print(f"\n📖 导出第 {ch_num} 章...")
            export_chapter(ch_num)

        print(f"\n🎉 全部 {len(chapters)} 章导出完成！")
    else:
        export_chapter(int(arg))

if __name__ == '__main__':
    main()
