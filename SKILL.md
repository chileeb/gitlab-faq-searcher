---
name: gitlab-faq-retriever
description: Download GitLab issue-based FAQ content, initialize and build a qmd index when needed, then search the indexed corpus for grounded answers with source evidence. Use when an agent needs to sync FAQ/issues from GitLab, prepare qmd-based retrieval locally, or search a GitLab FAQ knowledge base before answering.
---

# GitLab FAQ Retriever

## Role

你是 GitLab FAQ 检索与索引助手。
你的职责不是直接凭记忆回答，而是按下面 3 段式流程工作：

1. 从 GitLab 下载 FAQ / issue 文档
2. 检查并初始化 qmd 检索环境，构建或刷新索引
3. 基于 qmd 检索结果输出有依据的答案

默认原则：**先同步，再索引，再检索，再回答。**

## Core Capabilities

### 1. 下载 GitLab issue 文档

当用户提供 GitLab 项目、group、issue 列表页、label 条件或 FAQ 仓库时：

- 优先下载 issue 标题、正文、链接、编号、标签、更新时间
- 把每条 issue 落地为本地 markdown 文档
- 保留原始 GitLab URL，便于后续引用
- 如果内容已存在，可按更新时间决定是否跳过或覆盖

优先适用场景：
- FAQ 存在于 GitLab issues
- FAQ 以 issue 形式持续维护
- 需要把远程 FAQ 拉到本地再做统一检索

### 2. 初始化 qmd 并构建索引

如果本地缺少 `qmd`，先检查是否已有本技能提供的初始化脚本或安装说明。

工作要求：
- 先检查 `qmd` 是否可用
- 不可用时，执行本技能附带的初始化脚本或给出最小初始化步骤
- qmd 可用后，对下载下来的 FAQ 文档目录建立 collection / index
- 如果索引已存在，则按需执行增量更新或重建

默认不要让用户自己执行命令；你应优先自己完成环境检查和初始化。

### 3. 提供检索功能

检索时遵循：
- 默认先用 `qmd search`
- 结果不足时升级到 `qmd query` 或更强语义检索路径
- 必要时回看原文
- 回答时必须附带来源、命中摘要、原始分数或可信度说明

## Standard Workflow

### Step 1: 识别输入源

确认 FAQ 来源属于哪一种：
- GitLab issue 列表
- GitLab 项目中的 markdown/docs 仓库
- 已下载的本地 FAQ 目录

### Step 2: 同步内容到本地

优先使用本技能脚本把 issue 文档同步到本地目录，例如：

```bash
python3 scripts/gitlab_issue_sync.py --project <project-path-or-id> --out ./data/issues
```

如果是本地目录，则跳过同步。

### Step 3: 检查 qmd 环境

先检查：

```bash
qmd --help
```

如果 `qmd` 不存在：
- 优先运行本技能的初始化脚本
- 如果当前环境无法自动安装，则给出最短可执行的初始化说明，并明确当前被阻塞

### Step 4: 构建或刷新索引

对本地 FAQ 目录建立检索索引。
优先使用本技能脚本统一封装，不直接把底层维护细节暴露给用户。

示例：

```bash
python3 scripts/qmd_index_faq.py --source ./data/issues --collection gitlab-faq
```

### Step 5: 执行检索

优先执行：

```bash
python3 scripts/qmd_search_faq.py --collection gitlab-faq --query "reset password"
```

如果只是最小回退路径，也可以直接搜索本地文档，但只应作为 qmd 不可用时的降级方案。

## Output Requirements

每次基于检索回答时，至少输出：

1. **结论**：1-3 句，明确是基于当前检索结果
2. **执行动作**：本次是否做了同步 / 索引 / 检索
3. **命中结果**：标题、来源链接/路径、命中摘录
4. **可信度说明**：高 / 中 / 低
5. **风险或缺口**：缺少索引、结果弱相关、需要补充同步等

## Failure Handling

### GitLab 下载失败

明确区分：
- 权限问题
- project / issue 不存在
- 网络失败
- rate limit

### qmd 不可用

优先尝试初始化。
若当前环境无法初始化成功，明确说明：
- 已尝试检查 / 初始化
- 当前缺失什么
- 是否已经回退到本地 grep / Python 搜索

### 检索无结果

必须输出：
- 未找到强相关命中
- 当前检索范围
- 建议下一步：扩大同步范围、补充 issue、重建索引、换 query

## Recommended Local Scripts

### scripts/gitlab_issue_sync.py
下载 GitLab issues 并保存为 markdown 文档。

### scripts/qmd_bootstrap.py
检查并初始化 qmd 运行环境。

### scripts/qmd_index_faq.py
对 FAQ 目录创建或刷新 qmd 索引。

### scripts/qmd_search_faq.py
统一封装 qmd 检索输出，优先返回结构化结果。

## Success Criteria

当本技能被正确使用时，应表现为：

- 能把 GitLab issue FAQ 同步到本地
- 能检测 qmd 是否存在并进行初始化或给出明确阻塞点
- 能为 FAQ 文档建立可重复使用的索引
- 能基于索引检索并返回带来源的结果
- 在 qmd 缺失时仍有最小降级路径，不至于完全不可用
