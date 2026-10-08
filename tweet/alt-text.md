# Media descriptions

## 2 — 问题：如何发现未知规则

Paper Figure 1 animated in sequence: Observe, Induce a program, and Plan & Act appear from left to right. The return arrows lead back to Observe, then all three benchmark result panels fade in together. The complete original figure holds at the end.

## 3 — 方法：持续演化的可执行理论

Paper Figure 2 animated in causal order. Recorded history states are checked one by one before certification. Actions execute sequentially. The next predicted observation appears before the actual outcome. A mismatch stops execution and discards the remaining actions. The observed counterexample returns along the revision arrow, and the program gains a new code patch.

## 4 — 实例：用新证据修正理论

Complete LS20 level 2 replays, at the same action pace. Schema learns that refueling stations are single-use and finishes in 59 actions. Without runtime verification, the agent executes 42 further actions after a failed prediction, returns to a spent station, runs out of energy, and finishes after a reset in 143 actions. Short holds and red outlines mark the evidence.

## 5 — ARC-AGI-3：视觉环境

Complete CN04 gameplay with Schema and Claude Fable 5. The agent solves all six levels by moving and growing pieces; the replay shows the game board, plans, and level progress.

## 6 — DiG-bench：文本环境

Complete DiG-bench P-10 gameplay with Schema and GPT-6 Astra. The agent discovers hidden rules from symbolic examples, tests them, and clears all eight levels with limited lives.

## 7 — MazeBench：长期积累与复用

MazeBench exploration with Schema and GPT-6 Astra. The full recorded trajectory is shown as a timelapse, with the room map and gem progress visible. The run finishes with 33 gems and 139 rooms visited.

## 8 — 消融：各组件的贡献

Ablation table and four analysis plots in one figure. Left: Claude Opus 4.8 on the ten hardest ARC-AGI-3 games; RHAE is 72.9% for Schema, 58.8% for prose, 62.3% without certification, 59.2% without planning, and 52.4% without verification. Right, in a 2-by-2 grid: representation compares CN04 level progress; certification compares AR25 history agreement; planning compares LS20 level progress; verification shows actions taken after prediction mismatches across ten games. The table occupies 30% of the combined width.
