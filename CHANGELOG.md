# Changelog

## 0.2.1 - 2026-08-31

- 新增指定 VRChat Avatar 插件的版本核对、备份、单包更新、功能回归和授权回滚流程。
- 将 `manifest.json`、`packages-lock.json`、UPM 解析、编译、MCP 重连、屏幕对比和 Avatar 功能测试分成独立状态，避免把“下载成功”写成“更新后正常”。
- 新增 `references/plugin-update-workflow.md` 和 `TOOLCHAIN_PROFILE.md` 的插件更新记录模板，并纳入 GitHub 发布检查。

## 0.2.0 - 2026-08-31

- 将 Skill 收窄为面向不会改模用户的 VRChat Avatar 改模助手。
- 加入从资料查询、Unity MCP、静态文件核查、屏幕观察到逐项验收的完整引导。
- 把服装、发型、眼睛材质、菜单、Animator、动态组件和 Blender 交接经验整理为公开可复用规则。
- 按公开 GitHub Skill 的常见结构重写 README，补充 Features、Workflow、Use cases、Environment、Installation、Repository structure 和 Safety boundaries。
- 移除个人对话台账、项目案例档案、心率研究和 GitHub 发布教程，避免把非改模内容带入公开 Skill。
