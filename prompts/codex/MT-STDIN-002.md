# MT-STDIN-002：stdin prompt 修复验证第 2 轮

这是 conversation_id=`multi-turn-stdin-smoke` 的第 2 轮。

请只做最小动作：

1. 不修改业务代码、不安装依赖、不运行长耗时命令。
2. 检查你收到的上下文中是否包含第 1 轮标记 `STDIN_FIRST_MARKER: long prompt context established`。
3. 在最终输出中原样写出：`STDIN_SECOND_SAW_FIRST_MARKER: yes` 或 `STDIN_SECOND_SAW_FIRST_MARKER: no`。

本轮用于验证 runner 不再把长 merged prompt 作为命令行参数传给 Codex，而是通过 stdin 传入。
