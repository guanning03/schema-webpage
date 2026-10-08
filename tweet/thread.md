# Schema — Paper Release Thread

10 条英文帖文及配套素材。代码块内为可直接复制的正文。第 1 条引用原发布 tweet，第 2 条放 Figure 1 动画，第 3 条放 Figure 2 动画，第 5–7 条各配一段游戏视频，第 9 条讨论设计原则，第 10 条为资源与团队。

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

**媒体：** [02-overview-animation.mp4](assets/02-overview-animation.mp4)

**ALT / 描述：** Paper Figure 1 animated in sequence: Observe, Induce a program, and Plan & Act appear from left to right. The return arrows lead back to Observe, then all three benchmark result panels fade in together. The complete original figure holds at the end.

**制作备注：** 8.5-second animation: left panel, middle panel, right panel, return arrows to the left, then all three result panels together. The complete original figure holds for 3.35 seconds. DiG-bench retains the original Figure 1 configuration (90.5%); the 21-game result in post 6 uses another paper configuration.

## 3. 方法：持续演化的可执行理论

```text
Schema lets the agent direct its own learning.

It decides what to test, how to represent the world, when to revise its theory, and how to plan.

One evolving program connects these decisions: checked against experience and used for experiments and planning.
```

**字符数：** 258 / 280。

**媒体：** [03-method-animation.mp4](assets/03-method-animation.mp4)

**ALT / 描述：** Paper Figure 2 animated in causal order. Recorded history states are checked one by one before certification. Actions execute sequentially. The next predicted observation appears before the actual outcome. A mismatch stops execution and discards the remaining actions. The observed counterexample returns along the revision arrow, and the program gains a new code patch.

**制作备注：** 13.13-second animation, slowed to 0.8x the previous version. History states, execution actions, mismatch, discarded actions, counterexample feedback, and program revision retain their original order. The complete figure holds at the end.

## 4. 实例：用新证据修正理论

```text
For example, in ARC3 LS20, a refueling station disappears after use.

Schema catches the failed prediction, learns that stations are single-use, and replans.

Without verification, 42 more actions execute—including a return to the spent station. The agent runs out of energy.
```

**字符数：** 275 / 280。

**媒体：** [04-theory-revision.mp4](assets/04-theory-revision.mp4)

**ALT / 描述：** Complete LS20 level 2 replays, at the same action pace. Schema learns that refueling stations are single-use and finishes in 59 actions. Without runtime verification, the agent executes 42 further actions after a failed prediction, returns to a spent station, runs out of energy, and finishes after a reset in 143 actions. Short holds and red outlines mark the evidence.

## 5. ARC-AGI-3：视觉环境

```text
We evaluated the effectiveness of Schema on diverse environments.

Across ARC-AGI-3’s 25 games, Schema with Claude Fable 5 raises RHAE from 58.7% in Claude Code to 99.2%, and games solved from 14 to all 25.

Agentic program induction really draws out frontier models’ knowledge!
```

**字符数：** 278 / 280。

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

**媒体：** [08-ablation-combined.png](assets/08-ablation-combined.png)

**ALT / 描述：** Ablation table and four analysis plots in one figure. Left: Claude Opus 4.8 on the ten hardest ARC-AGI-3 games; RHAE is 72.9% for Schema, 58.8% for prose, 62.3% without certification, 59.2% without planning, and 52.4% without verification. Right, in a 2-by-2 grid: representation compares CN04 level progress; certification compares AR25 history agreement; planning compares LS20 level progress; verification shows actions taken after prediction mismatches across ten games. The table occupies 30% of the combined width.

**制作备注：** 合图左侧保留论文表格，宽度占 30%；右侧四张分析图按 representation、certification、planning、verification 排成 2×2。曲线、数值、图例顺序和颜色沿用论文绘图脚本，仅调整版式、字号及线宽。

## 9. 讨论：通用架构与未来展望

```text
Schema organizes learning around one evolving executable theory, tested against all experience and used for experimentation and planning.

As frontier LLMs advance, we believe this approach will become a powerful agentic paradigm for a wider range of real-world tasks!
```

**字符数：** 268 / 280。

**制作备注：** 以持续演化的同一个可执行理论组织学习，接受全部经验的检验，并直接用于实验与规划。随着 frontier LLM 能力进步，期待这一 agentic paradigm 在更多现实任务中发挥作用；后者为未来展望。

## 10. 论文、代码与团队

```text
Paper: https://arxiv.org/abs/2609.39140
Code: https://github.com/guanning03/Schema
Project Website: https://guanning03.github.io/schema-webpage/

@guanningzeng @Jiani_Wang_ @wenjie_ma @shaofeng_y27736 @ChenyangWa70207 @lustralisk95 @akanazawa @wodenimoni @xiuyu_l @Zanette_ai @HavenFeng
```

**字符数：** 243 / 280。

## 发布与核对说明

- 首帖用 Quote Post 引用旧 tweet，然后第 2–10 条依次回复上一条。正文已控制在 280 加权字符以内，链接按 23 字符折算。
- 首帖 July 15 为博客 release 日期，被引用的 Haven 公告发表于 July 16。
- 首帖保留首次 release 的约 99% 历史结果；第 5 条为完整论文的 Claude Fable 5 结果：58.7% → 99.2% RHAE，14 → 25 个游戏通关。
- Figure 1 动画分步展示论文原图，最终完整保留原图；其中 DiG-bench 面板对应 90.5% 配置。第 6 条全部 21 个游戏的结果来自论文另一组配置。DiG-bench 的生命损失在三组配置分别为 Basic → Schema：96 → 34、52 → 29、32 → 25。公开媒体只显示模型名。
- 第 4 条来自 Claude Opus 4.8 的 LS20 Level 2 消融：Schema 59 动作，Without verification 143 动作。没有删除重试或后续动作。
- 第 7 条视频的终点为 33 gems / 139 rooms；人类 top-50 中位数是 29 / 137。视频对完整轨迹加速，保留开头和结尾。第 8 条将 Claude Opus 4.8、10 个最难游戏的消融原表与四张行为分析图合为一张。
- 第 3 条突出 agent 对实验、状态表示、理论修正和规划的决策权，以及连接这些操作的持续演化程序。依据：论文方法章节。
- 第 9 条强调同一个可执行理论接受历史经验检验、并用于实验与规划，再展望这一架构随 frontier LLM 进步在更多现实任务中的潜力。依据：[论文方法及 Implementation Details](https://arxiv.org/abs/2609.39140)。
- 这是本地预览和素材包，尚未发布到 X。

## 来源

- [当前论文网页](https://guanning03.github.io/schema-webpage/)
- [原始 Blog](https://schema-harness.github.io/)
- [WorldCoder](https://arxiv.org/abs/2402.12275)
- [VISTA 论文发布 thread](https://x.com/JoshHanHi/status/2106536875586404707)
- [MaxRL 发布 thread](https://x.com/FahimTajwar10/status/2019471326944117152)
