# Claude 指令

## 导出 = 运行 export.py（不是 Word）

**用户说"导出"时，永远不要生成 .docx 或 Word 文件。只执行 `python3 export.py`。这个脚本会同时生成 TXT 和 PDF。**

## 触发词

| 用户说 | 你必须执行 |
|--------|-----------|
| `导出第X章` | `python3 export.py X` |
| `导出全部` | `python3 export.py all` |
| `导出` | 提示用户指定章节号，或导出全部 |
| `写第X章` | 先读 CHARACTERS.md + OUTLINE.md，用 net-novel.md 风格写 `chapters/chapter-XX.md` |
| `修订第X章` | 读对应章 MD + 用户修改意见，直接编辑源文件 |

## 项目文件

- 源文件：`chapters/chapter-XX.md`
- 导出软件：`python3 export.py X`（生成 TXT + PDF 到 `exports/`）
- 角色档案：`CHARACTERS.md`
- 100章大纲：`OUTLINE.md`
- 写作 persona：`net-novel.md`

## 小说基本信息

- 书名：《万物心声》
- 主角：冉峰，22岁，星辰科技新入职后端程序员
- 女主：余楚乔，25岁，同公司高级产品经理，普通人
- 核心设定：猝死觉醒"万物心声"系统，能听懂并与生命体/非生命体沟通
- 写作风格：网文（net-novel.md），爽文节奏，手机阅读适配，每章4000字左右
