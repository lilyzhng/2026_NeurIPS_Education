# Lilian《Harness Engineering》Section 1 逐段 annotation

原文完整 MD：`lilian-harness-full.md`（pandoc 转自她 GitHub repo 的编译版 HTML，repo 里没有 MD 源文件）。
本文件：Section 1（Harness Design Patterns）逐段拆，每段一条行文结构注释。后续 section 写到哪拆到哪。

# Harness Design Patterns

<!-- 段1｜对比已知：锚在读者背得出的旧公式上（还给自己 2023 年的 Agents 文加了内链），用 additionally include 说清"新在哪"，斜体强调新增清单。第二句紧跟重定义 + 五个动词排比（observes, acts, memorizes, checks itself, improves），把抽象概念变成动作清单。 -->

Compared with [early agent frameworks](https://lilianweng.github.io/posts/2023-06-23-agent/), "agent = LLM + memory + tools + planning + action", harnesses engineering additionally include *workflow design (e.g. loop engineering), evaluation, permission controls, and persistent state management*. It is no longer only prompt templates, but closer to runtime and software system design: how the model observes, acts, memorizes, checks itself, and improves.

<!-- 段2｜设计原则 + 类比：先给一句设计判断（simple and generic to enable generalization），再类比到人人懂的 OS（encapsulate complicated logic, simple interface），收一句 forward-looking（协议会标准化）。节开场就这两段，立刻进 Pattern。 -->

The design should be deliberately simple and generic to enable generalization, likely with reference to existing software engineering practices to benefit from prertaining knowlege. There is also a strong analogy between operating systems and harnesses. Similar to an OS, a harness should encapsulate complicated logic while keeping the interface simple. Meanwhile, configs, tool interfaces and other protocols may gradually become standardized across the industry.

## Pattern 1: Workflow Automation

<!-- 段1｜一句话定义这个 pattern 是什么（defining a workflow ... is a key design），第二句立刻给真实例子带链接（Karpathy repo），第三句用动词链描述 loop（plan, execute, observe/test, improve, execute again until），第四句补一个边界情况（主动向用户要澄清）。 -->

Defining a workflow in which the model can operate, test, and iterate is a key design for automation. Karpathy's autoresearch repo (<https://github.com/karpathy/autoresearch>) is a clean example of how such a workflow can be constructed. A common workflow follows a goal-oriented loop of plan, execute, observe/test, improve, and execute again *until* the goal is achieved. The process may trigger proactive requests to users for clarity in task specification or execution preference.

<!-- 图｜每个 pattern 配一张图 + 一句 caption + 图片来源链接。 -->

（图：A simplified Codex agent loop，来源 OpenAI codex agent post）

<!-- 段2｜图后一句收尾：把图里的机制升华成一个设计判断（agent runtime 而不是 static prompt template）。 -->

The workflow graph also emphasizes the model analyzing its own trajectories and failure cases and then iterating on its progress through an "agent runtime" rather than a static prompt template.

## Pattern 2: File System as Persistent Memory

<!-- 段1｜句式换开头（A recurring pattern is...），第二句用 should not ... instead 给出对错对照，第三句列具体 artifact 清单（logs, diffs, summaries, traces）说明为什么需要。 -->

A recurring pattern in long-horizon agent systems is simple control over rich states and artifacts. A harness should not carry the entire workflow and all logs in context; instead, it should keep durable state in files. In long-horizon agentic rollout, artifacts such as experiment logs, code diffs, paper summaries, error traces, and past rollout trajectories often grow much longer than the context window that the model has trained for.

<!-- 段2｜收尾设计判断：把这个 pattern 接到模型能力的大趋势上（files 这种简单形式会随核心能力一起变强）。 -->

Learning how to read, write, and edit the file system (commonly via `bash` commands) is a foundation skill for LLMs, and thus managing persistent memory in the simple form of files naturally benefits from improvements in core model capability.

## Pattern 3: Sub-agent and Backend Jobs

<!-- 段1｜一句定义 + This is useful when 三个并列场景 + 需要什么配套（a small process manager: 四个动词）。 -->

A harness can spawn multiple subagents to execute in parallel and monitor backend jobs. This is useful when the main agent needs to search multiple hypotheses, run experiments concurrently, or delegate isolated subtasks without polluting the main context. The parent agent then needs a small process manager: launch jobs, inspect logs, cancel failed runs, and merge results back into the main agent thread.

<!-- 段2｜收尾设计判断，用 if...if... 对照句讲清 key design choice（explicit and inspectable）。 -->

The key design choice is to make parallelism explicit and inspectable. If subagent outputs only live in a transient chat context, they quickly become obselete and hidden. If they are stored as files, logs, and status records, the model can recover after interruptions and reason over its own execution history.

## Case study: Coding Agent Harness

<!-- 落到读者天天用的产品：点名 Claude Code / Codex / OpenCode / Cursor，一张 loop 图 + 一个工具表。抽象 pattern 接到具体。 -->

The core interface of mainstream coding agents has become stabilized across Claude Code, Codex, OpenCode, and Cursor-style agents. They commonly use a loop like: （图 + 工具表）

## Harness Layer vs Core Intelligence?

<!-- 收尾 discussion：先承认不确定（It is hard to forecast），然后亮出自己的 prediction（编号两条），最后用一个历史先例收束（prompt engineering 的教训：技巧被内化，但 specify goals/constraints/context/evaluation 的需求不消失）。承上启下。 -->

It is hard to forecast how much the future of RSI will rely on harness engineering, but the near-term path of RSI is unlikely to start as a model directly rewriting its weights. My prediction of a practical near-term path is: (1) harness engineering evolves toward meta-methodology... (2) mature harnesses enable auto-research... Eventually many harness improvements will be *internalized* into core model behavior, but the interface with external context and tools should remain. We have seen a softer version of this pattern with prompt engineering: manual prompt tricks became less central as instruction tuning and model reasoning improved, but *the need to specify goals, constraints, context, and evaluation did not disappear*.
