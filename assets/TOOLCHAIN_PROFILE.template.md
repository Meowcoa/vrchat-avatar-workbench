# TOOLCHAIN_PROFILE.md

这是工程自己的工具链选择记录，不是 Skill 的安装清单。先读包清单和实际组件，再填写。工具“已安装”和“本任务允许使用”是两个独立字段。

## 工程身份

- `project_root`：
- `unity_version`：
- `active_scene`：
- `avatar_root`：
- `profile_date`：

## 角色分工

| 工作角色 | 选择 | Package/组件证据 | 允许操作 | 备注 |
| --- | --- | --- | --- | --- |
| Clothing/Wardrobe | lilycalInventory / DressingTools / Modular Avatar / existing provider / unknown | | inspect / change | |
| Facial expression | FaceEmo / existing source / VRCFT add-on / none | | inspect / change | |
| Props/features | asset-declared provider / Modular Avatar / VRCFury / unknown | | inspect / change | |
| Preview | Gesture Manager / Play Mode / screen only / none | | preview only | |
| Optimization | AAO / SDK only / measured target / none | | audit / build | |
| Mesh/DCC | Blender / CATS / Tuxedo / other | | handoff | |
| Editor bridge | Unity MCP / UnityAgent / none | | read / controlled edit | |

## MCP 状态记录

- 发现方式：`mcpforunity://instances`
- 选定实例（每次会话重新发现）：
- `project/info` 路径与版本：
- `editor/state`：`ready_for_tools` / `is_compiling` / `is_dirty` / `blocking_reasons`
- 当前状态新鲜度：
- 失败/恢复记录：
- 任何 `tools/call` 或写操作是否获得独立授权：

## 版本边界

- 当前工程的 MA/NDMF/SDK 不得自动升级：
- Provider 版本和作者测试环境是否一致：
- 仅包级推断的组合：
- 需要真实导入/构建验证的结论：

## Owner 与验证

- Scene/Prefab owner：
- Import owner：
- Compile/build owner：
- 当前任务最终目标证据层：
- 未运行层：

## 插件更新记录（按需）

只在用户明确要求检查或更新插件时填写。每一行只记录一个 `Package ID`，不要把“网页显示 Latest”直接当成已适配当前 Avatar。

| 检查日期 | Package ID | 当前解析版本 | 目标版本 | 官方来源 | 稳定/测试版 | 备份/基线 | 更新结果 | 回归/回滚证据 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| | | | | | | | | |

- 更新前 `manifest.json`：
- 更新前 `packages-lock.json`：
- 目标插件实际使用的菜单/参数/Animator/材质/动态组件：
- 目标平台：PC / Android / both
- 未运行的回归：
