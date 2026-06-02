# 《万物心声》写作项目

## 文件结构

```
agent writing/
├── CLAUDE.md          ← Claude 自动加载的指令文件
├── CHARACTERS.md      ← 角色档案
├── OUTLINE.md         ← 100章大纲
├── net-novel.md       ← 写作 persona（网文风格）
├── export.py          ← 导出工具：MD → TXT + PDF
├── EXPORT.md          ← 导出规则说明
├── chapters/          ← 源文件（MD，在此编辑）
│   └── chapter-01.md
└── exports/           ← 导出产物（TXT 上传番茄小说 + PDF 分享）
    ├── 第001章-标题.txt
    └── 第001章-标题.pdf
```

## 日常操作

直接在 Claude 中说：

- `写第X章` → 自动生成 `chapters/chapter-XX.md`
- `导出第X章` → 自动运行 `python3 export.py X`，生成 TXT + PDF 到 `exports/`
- `导出全部` → 批量导出所有已完成的章节
- `修订第X章` → 修改已写好的章节

## 导出说明

- 导出 = 同时生成 TXT（给番茄小说上传）和 PDF（分享给人看）
- 每次导出自动删除旧文件再重新生成，保证内容同步
- TXT 含段落空行随机化处理以降低 AI 检测率
- 不再使用 Word/docx 格式
