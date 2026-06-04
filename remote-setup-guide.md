# 🏠 在家办公连接教程

> **给 AI 助手看**：请按以下步骤指导用户在家庭电脑上连接回公司 Mac 并搭建小说写作环境。

---

## 一、背景信息

| 项目 | 详情 |
|------|------|
| 公司 Mac 机器名 | `qiuhaihuimac-mini` |
| 公司 Mac 已启动 | VS Code Remote Tunnel（常驻运行） |
| 连接方式 | 浏览器打开 vscode.dev → 远程连接 |
| 项目 Git 仓库 | `https://github.com/haiyanyoudiangui-creator/wanwuxinsheng.git` |
| 项目文件夹 | `~/agent writing`（公司 Mac 上） |
| 写作内容 | 小说《万物心声》，Markdown 文件在 `chapters/` 目录 |

---

## 二、在家电脑连接公司 Mac

### 方式 A：VS Code 桌面版（推荐，功能最全）

1. 在家电脑上安装 VS Code（https://code.visualstudio.com）
2. 打开 VS Code，按 `F1`，输入 `Remote Tunnels: Connect to Tunnel...`
3. 用和公司 Mac 上**同一个 GitHub 账号**登录
4. 在远程机器列表里选择 `qiuhaihuimac-mini`
5. 连接成功后，你现在操作的就是公司 Mac 了！

### 方式 B：纯浏览器（无需安装任何东西）

1. 打开浏览器 → https://vscode.dev
2. 同样用你的 GitHub 账号登录
3. 左侧底部找到远程连接入口，选择 `qiuhaihuimac-mini`
4. 连接后就能用完整 VS Code + 终端

### 方式 C：SSH 直连（备选）

如果 Tunnel 出问题，在家 Mac 终端输入：
```bash
# 需要知道公司 Mac 的公网 IP 或做了内网穿透
ssh 你的用户名@公司Mac的IP或域名
```

---

## 三、连接后：拉取项目并开始写作

连接成功后，在 VS Code 终端（`Ctrl+`` 或 `Cmd+``）中执行：

```bash
# 1. 进入项目目录
cd ~/agent\ writing

# 2. 拉取最新代码（如果在家之前在公司已经 push 了）
git pull

# 3. （可选）安装 Claude Code
npm install -g @anthropic-ai/claude-code

# 4. 开始写作
claude
# 或者直接用 VS Code 打开 chapters/ 目录下的章节文件
```

---

## 四、日常工作流

### 在公司下班前：
```bash
cd ~/agent\ writing
git add -A
git commit -m "WIP: 下班前提交"
git push origin main
```
⚠️ **一定记得 push！** 不然回家拉不到最新代码。

### 到家后：
1. vscode.dev 连回公司 Mac
2. `cd ~/agent\ writing && git pull`
3. 开写

### 在家写完后：
```bash
git add -A
git commit -m "第X章 修订/完成"
git push origin main
```

### 第二天到公司：
```bash
git pull
# 继续工作，无缝衔接
```

---

## 五、常见问题

**Q：Tunnel 连不上？**
- 检查公司 Mac 是否开机且未休眠
- SSH 进去执行 `code tunnel restart`
- 或者让同事帮忙重新启动公司 Mac

**Q：忘记 push 就回家了？**
- 如果有 VPN：连公司 VPN → SSH 到公司 Mac → `git push`
- 如果没有 VPN：只能第二天到公司再 push 了 😅

**Q：公司 Mac 休眠了 Tunnel 会断吗？**
- 当前启动时加了 `--no-sleep` 参数，正常不会
- 建议再去「系统设置 → 电池 → 电源适配器」把「防止自动休眠」打开

---

## 六、项目速查

```bash
# 写第X章（需要先读角色和提纲）
# 在 Claude Code 中直接说："写第X章"

# 导出第X章为 TXT + PDF
python3 export.py X

# 导出全部章节
python3 export.py all

# 查看角色设定
cat CHARACTERS.md

# 查看100章大纲
cat OUTLINE.md
```
