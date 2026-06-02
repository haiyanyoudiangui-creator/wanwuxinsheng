#!/usr/bin/env python3
"""
万物心声 — 静态网站生成器
将 chapters/ 下的 Markdown 章节文件转换为 HTML 网站，输出到 site/ 目录。
"""

import os
import re
import html
import glob

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CHAPTERS_DIR = os.path.join(BASE_DIR, "chapters")
SITE_DIR = os.path.join(BASE_DIR, "site")
CSS_PATH = "css/style.css"

CHAPTER_CHAPTER_PATTERN = re.compile(r"chapters/chapter-(\d+)\.md")


def parse_chapter_md(filepath: str) -> dict:
    """解析章节 MD 文件，返回标题和 HTML 正文。"""
    with open(filepath, "r", encoding="utf-8") as f:
        raw = f.read().strip()

    lines = raw.split("\n")
    title = ""
    body_lines = []

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("# ") and not title:
            title = stripped[2:].strip()
        else:
            body_lines.append(line)

    body_html = md_to_html("\n".join(body_lines))
    return {"title": title, "body": body_html}


def md_to_html(text: str) -> str:
    """将基础 Markdown 转换为 HTML (支持本项目章节格式)。"""
    lines = text.split("\n")
    out = []
    in_para = False
    para_buf = []

    def flush_para():
        nonlocal in_para
        if para_buf:
            content = "<br>".join(para_buf)
            out.append(f"<p>{content}</p>")
            para_buf.clear()
            in_para = False

    for i, line in enumerate(lines):
        # 章节分隔符 (---)
        if re.match(r"^---+$", line.strip()):
            flush_para()
            out.append('<hr class="section-break">')
            continue

        # 二级标题
        if re.match(r"^## ", line):
            flush_para()
            h2 = re.sub(r"^## ", "", line)
            out.append(f"<h2>{inline_md(h2)}</h2>")
            continue

        # 三级标题
        if re.match(r"^### ", line):
            flush_para()
            h3 = re.sub(r"^### ", "", line)
            out.append(f"<h3>{inline_md(h3)}</h3>")
            continue

        # 引用
        if line.startswith('"> ') or line.startswith("> "):
            flush_para()
            block = "\n".join(
                l[3:] if l.startswith('"> ') else l[2:] if l.startswith("> ") else l
                for l in [line]
            )
            out.append(f"<blockquote>{inline_md(block)}</blockquote>")
            continue

        # 水平线
        if line.strip() in ("---", "***", "___"):
            flush_para()
            out.append("<hr>")
            continue

        # 空行 = 段落分隔
        if line.strip() == "":
            flush_para()
            continue

        # 普通行
        para_buf.append(inline_md(line))
        in_para = True

    flush_para()
    return "\n".join(out)


def inline_md(text: str) -> str:
    """行内 markdown 转换：加粗、斜体、行内代码。"""
    text = html.escape(text)
    # 加粗
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    # 斜体
    text = re.sub(r"\*(.+?)\*", r"<em>\1</em>", text)
    return text


def render_page(title: str, content: str, active_nav: str = "") -> str:
    """生成完整 HTML 页面。"""
    nav_html = ""
    if active_nav == "index":
        nav_html = '<a href="index.html" class="active">目录</a>'
    elif active_nav == "chapter":
        nav_html = '<a href="index.html">目录</a>'

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} — 万物心声</title>
<link rel="stylesheet" href="{CSS_PATH}">
</head>
<body>
<div class="progress-bar" id="progressBar"></div>
<nav class="navbar">
  <div class="navbar-inner">
    <a class="logo" href="index.html">万物心声</a>
    <div class="nav-links">
      {nav_html}
    </div>
  </div>
</nav>
<div class="container">
{content}
</div>
<footer class="footer">
  <p>《万物心声》© 2025 &mdash; 冉峰的故事，从这里开始</p>
  <p style="margin-top:0.3rem"><a href="index.html">返回目录</a></p>
</footer>
<script>
(function() {{
  var bar = document.getElementById('progressBar');
  if (bar) {{
    window.addEventListener('scroll', function() {{
      var h = document.documentElement;
      var p = (h.scrollTop / (h.scrollHeight - h.clientHeight)) * 100;
      bar.style.width = Math.min(p, 100) + '%';
    }});
  }}
}})();
</script>
</body>
</html>"""


def render_index(chapters: list) -> str:
    """生成首页。"""
    chapter_items = ""
    for ch in chapters:
        num = ch["num"]
        title = ch["title"]
        chapter_items += f"""  <div class="chapter-item">
    <span class="chapter-num">第{num}章</span>
    <a href="chapter-{num:02d}.html">{html.escape(title)}</a>
  </div>\n"""

    content = f"""
<div class="hero">
  <h1>万物心声</h1>
  <p class="subtitle">当心脏开口说话，世界从此不同</p>
  <p class="meta">都市 · 系统 · 爽文 · 连载中</p>
</div>

<div class="intro-card">
  <h2>📖 作品简介</h2>
  <p>冉峰，星辰科技新入职后端程序员，22岁。连续通宵三天后，凌晨三点心脏骤停倒在工位——醒来后，他听到了心脏在骂他。</p>
  <p style="margin-top:0.6rem">从此，他拥有了"万物心声"系统：能听懂电脑的报怨、打印机的八卦、饮水机的碎碎念。但这只是开始——当公司内斗将他卷入更深的漩涡，他发现了系统背后隐藏的百年秘密：他不是第一个觉醒者，也不会是最后一个。</p>
  <p style="margin-top:0.6rem">从被碾碎的牛马到掌握世界之声，冉峰只有一个原则：<strong>动我可以，动我身边的人——不行。</strong></p>
</div>

<div class="chapter-list">
  <h2>📚 章节目录</h2>
{chapter_items}
</div>
"""
    return content


def main():
    # 找到所有章节文件
    md_files = sorted(
        glob.glob(os.path.join(CHAPTERS_DIR, "chapter-*.md")),
        key=lambda p: int(re.search(r"chapter-(\d+)", p).group(1))
    )

    if not md_files:
        print("⚠️  没有找到章节文件 (chapters/chapter-*.md)")
        return

    print(f"📄 找到 {len(md_files)} 个章节文件")

    chapters = []
    for filepath in md_files:
        num = int(re.search(r"chapter-(\d+)", filepath).group(1))
        parsed = parse_chapter_md(filepath)
        chapters.append({
            "num": num,
            "title": parsed["title"],
            "body": parsed["body"],
        })
        print(f"   ✅ 第{num}章: {parsed['title']}")

    # 生成章节页面
    for i, ch in enumerate(chapters):
        prev_link = ""
        next_link = ""

        if i > 0:
            prev_ch = chapters[i - 1]
            prev_link = f'<a href="chapter-{prev_ch["num"]:02d}.html">← 第{prev_ch["num"]}章 · {html.escape(prev_ch["title"])}</a>'
        else:
            prev_link = '<span class="disabled">← 已是第一章</span>'

        if i < len(chapters) - 1:
            next_ch = chapters[i + 1]
            next_link = f'<a href="chapter-{next_ch["num"]:02d}.html">第{next_ch["num"]}章 · {html.escape(next_ch["title"])} →</a>'
        else:
            next_link = '<span class="disabled">已是最后一章 →</span>'

        content = f"""
<div class="chapter-header">
  <h1>第{ch["num"]}章 · {html.escape(ch["title"])}</h1>
</div>

<div class="chapter-nav-top">
  {prev_link}
  <a href="index.html">📋 目录</a>
  {next_link}
</div>

<div class="chapter-content">
{ch["body"]}
</div>

<div class="chapter-nav">
  {prev_link}
  <a class="toc-link" href="index.html">📋 目录</a>
  {next_link}
</div>
"""
        html_page = render_page(
            f"第{ch['num']}章 · {ch['title']}", content, active_nav="chapter"
        )
        out_path = os.path.join(SITE_DIR, f"chapter-{ch['num']:02d}.html")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(html_page)
        print(f"   📝 chapter-{ch['num']:02d}.html")

    # 生成首页
    index_content = render_index(chapters)
    index_html = render_page("万物心声 — 小说目录", index_content, active_nav="index")
    index_path = os.path.join(SITE_DIR, "index.html")
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(index_html)
    print(f"   🏠 index.html")

    print(f"\n✨ 网站已生成到 {SITE_DIR}/")
    print(f"   用浏览器打开 site/index.html 即可预览")
    print(f"   或运行: cd site && python3 -m http.server 8080")


if __name__ == "__main__":
    main()
