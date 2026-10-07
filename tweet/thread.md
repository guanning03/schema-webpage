# Schema — Paper Release Thread

10 条英文帖文及配套素材。代码块内为可直接复制的正文。第 1 条引用原发布 tweet，第 2 条放 Figure 1，第 3 条放 Figure 2 动画，第 5–7 条各配一段游戏视频，第 9 条讨论设计原则，第 10 条为资源与团队。

## 1. 从首次发布引出完整论文

```text
On July 15, we released Schema, the first agent harness to reach ~99% RHAE on the ARC-AGI-3 public set.

Today, we’re sharing the full paper and code, with new results and a closer look at why Schema works.

https://guanning03.github.io/schema-webpage/ 🧵
```

**字符数：** 234 / 280。

**引用：** [首次发布 tweet](https://x.com/HavenFeng/status/2077770348876247502)，沿用已有 demo。

## 2. 问题：如何发现未知规则

```text
How does an agent learn to act when the rules aren’t given?

Scientists turn observations into theories, test their predictions, and revise them with new evidence.

Schema brings this process to agents exploring unfamiliar environments.
```

**字符数：** 236 / 280。

**媒体：** [02-paper-figure1.png](assets/02-paper-figure1.png)

**ALT / 描述：** Paper Figure 1. The agent observes an unfamiliar environment, induces an executable program, and uses it to plan and act. The bottom panels summarize ARC-AGI-3, DiG-bench, and MazeBench results.

**制作备注：** 论文 Figure 1 原图。下方 DiG-bench 面板采用论文总览图原始配置的 90.5% 结果，正文的全部 21 个游戏来自另一组已注明的配置；不改动论文原图。

## 3. 方法：持续演化的可执行理论

```text
Schema makes the theory executable.

The agent writes and revises a persistent program, tests it against all recorded experience, and uses it to design experiments and plans.

During execution, a prediction mismatch stops the plan and returns new evidence.
```

**字符数：** 256 / 280。

**媒体：** [03-method-animation.mp4](assets/03-method-animation.mp4)

**ALT / 描述：** Animated paper Figure 2. The agent and persistent workspace appear first, followed by Hypothesize, the proposed-program arrow, Certify, the counterexample feedback arrow, Plan, the commit-plan arrow, Act with verification, and finally the revision arrow. The animation ends on the complete original figure.

**制作备注：** 22 秒 MP4。图块与箭头按流程依次淡入，最后停留在完整原图。播放速度和布局固定，不移动或重绘论文内容。

## 4. 实例：用新证据修正理论

```text
In LS20, a refueling station disappears after use.

Schema catches the failed prediction, learns that stations are single-use, and replans.

Without verification, 42 more actions execute—including a return to the spent station. The agent runs out of energy.
```

**字符数：** 257 / 280。

**媒体：** [04-theory-revision.mp4](assets/04-theory-revision.mp4)

**ALT / 描述：** Complete LS20 level 2 replays, at the same action pace. Schema learns that refueling stations are single-use and finishes in 59 actions. Without runtime verification, the agent executes 42 further actions after a failed prediction, returns to a spent station, runs out of energy, and finishes after a reset in 143 actions. Short holds and red outlines mark the evidence.

## 5. ARC-AGI-3：视觉环境

```text
First, ARC-AGI-3: 25 visual games with unknown mechanics.

With Claude Fable 5, Schema raises RHAE from 58.7% in Claude Code to 99.2%, and games solved from 14 to all 25.

The model weights stay fixed; the agent learns through its program.
```

**字符数：** 239 / 280。

**媒体：** [05-arc-gameplay.mp4](assets/05-arc-gameplay.mp4)

**ALT / 描述：** Complete CN04 gameplay with Schema and Claude Fable 5. The agent solves all six levels by moving and growing pieces; the replay shows the game board, plans, and level progress.

**制作备注：** CN04 六关完整通关视频，保留网站版的原始播放节奏。

## 6. DiG-bench：文本环境

```text
The same idea carries over to text-based discovery.

DiG-bench hides rules behind games with limited lives. Schema with GPT-6 Astra solves all 21 public games and consistently loses fewer lives than the basic harness across our tested settings.
```

**字符数：** 244 / 280。

**媒体：** [06-dig-gameplay.mp4](assets/06-dig-gameplay.mp4)

**ALT / 描述：** Complete DiG-bench P-10 gameplay with Schema and GPT-6 Astra. The agent discovers hidden rules from symbolic examples, tests them, and clears all eight levels with limited lives.

**制作备注：** P-10 八关完整回放，保留文本示例、规划说明与生命数。仅显示模型名。

## 7. MazeBench：长期积累与复用

```text
Over longer interactions, those rules need to remain useful.

On MazeBench, Schema with GPT-6 Astra collects 33 gems and visits 139 rooms, exceeding the top-50 human median on both. Its program retains and reuses learned rules across context compactions.
```

**字符数：** 254 / 280。

**媒体：** [07-maze-gameplay.mp4](assets/07-maze-gameplay.mp4)

**ALT / 描述：** MazeBench exploration with Schema and GPT-6 Astra. The full recorded trajectory is shown as a timelapse, with the room map and gem progress visible. The run finishes with 33 gems and 139 rooms visited.

**制作备注：** 全程轨迹以网站回放的 4 倍速度展示，开头与结束停留保留。保留房间覆盖、宝石进度和原有游戏画面；不显示动作数、effort 或右侧 Action 标签。

## 8. 消融：各组件的贡献

```text
What drives these gains?

We ablate Schema on the 10 hardest ARC-AGI-3 games using Claude Opus 4.8.

Full Schema: 72.9% RHAE.
Replacing code with prose, or removing certification, planning, or runtime verification: 52.4–62.3%.
```

**字符数：** 226 / 280。

**媒体：** [08-ablation.png](assets/08-ablation.png)

**ALT / 描述：** Original paper ablation table. Ten hardest ARC-AGI-3 games, Claude Opus 4.8. Overall RHAE: full Schema 72.9%; without certification 62.3%; without planning 59.2%; without runtime verification 52.4%; prose-model variant 58.8%. Per-game level progress appears above the aggregate metrics.

## 9. 讨论：以更少交互学习紧凑知识

```text
Schema seeks compact, informative knowledge from minimal interaction.

Beyond WorldCoder’s predefined loop, frontier LLMs direct the full learning process: experiments, model revision, and planning.

Could this principle extend to embodied AI and automated research?
```

**字符数：** 266 / 280。

**制作备注：** 目标是高信息量、紧凑、可复用的知识与交互效率。区别在于 LLM 主导实验、理论修正与规划的完整学习过程。Embodied AI 和自动科研属于设计原则的潜在应用，而非本文已验证的结果。

## 10. 论文、代码与团队

```text
Paper: https://arxiv.org/abs/2609.39140
Code: https://github.com/guanning03/Schema
Replays: https://guanning03.github.io/schema-webpage/

Team: @guanningzeng @Jiani_Wang_ @wenjie_ma @shaofeng_y27736 @ChenyangWa70207 @lustralisk95 @akanazawa @wodenimoni @xiuyu_l @Zanette_ai @HavenFeng
```

**字符数：** 241 / 280。

## 发布与核对说明

- 首帖用 Quote Post 引用旧 tweet，然后第 2–10 条依次回复上一条。正文已控制在 280 加权字符以内，链接按 23 字符折算。
- 首帖 July 15 为博客 release 日期，被引用的 Haven 公告发表于 July 16。
- 首帖保留首次 release 的约 99% 历史结果；第 5 条为完整论文的 Claude Fable 5 结果：58.7% → 99.2% RHAE，14 → 25 个游戏通关。
- Figure 1 为论文原图；其中 DiG-bench 面板对应 90.5% 配置。第 6 条全部 21 个游戏的结果来自论文另一组配置。DiG-bench 的生命损失在三组配置分别为 Basic → Schema：96 → 34、52 → 29、32 → 25。公开媒体只显示模型名。
- 第 4 条来自 Claude Opus 4.8 的 LS20 Level 2 消融：Schema 59 动作，Without verification 143 动作。没有删除重试或后续动作。
- 第 7 条视频的终点为 33 gems / 139 rooms；人类 top-50 中位数是 29 / 137。视频对完整轨迹加速，保留开头和结尾。第 8 条为 Claude Opus 4.8、10 个最难游戏的消融原表。
- 第 9 条提出设计目标和可能的延伸方向，不声称已经在 embodied AI 或 automated research 中验证。与 WorldCoder 的区别限定于学习过程的控制权：WorldCoder 使用预定义的 REx 程序搜索过程；Schema 让 agent 决定实验、模型修正和规划。依据：[论文 related work](https://arxiv.org/abs/2609.39140)、[WorldCoder 原论文](https://openreview.net/pdf?id=QGJSXMhVaL)。
- 可执行世界模型本身也用于 WorldCoder 等工作；第 9 条不将该思想描述为 Schema 独有。
- 这是本地预览和素材包，尚未发布到 X。

## 来源

- [当前论文网页](https://guanning03.github.io/schema-webpage/)
- [原始 Blog](https://schema-harness.github.io/)
- [WorldCoder](https://arxiv.org/abs/2402.12275)
- [VISTA 论文发布 thread](https://x.com/JoshHanHi/status/2106536875586404707)
- [MaxRL 发布 thread](https://x.com/FahimTajwar10/status/2019471326944117152)
