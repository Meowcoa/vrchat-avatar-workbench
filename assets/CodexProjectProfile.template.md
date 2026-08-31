# CodexProjectProfile.md

把本文件复制到实际 Unity 工程根目录，并以当前工程文件为准填写。不要把它复制回 Skill 仓库，也不要填写 Token、Cookie、密码或私有下载链接。

## 身份与证据范围

- 工程根（本地绝对路径，仅保存在工程内，不提交到公开 Skill 仓库）：
- 工程用途：PC Avatar / Quest Avatar / 只读副本 / 备份 / 其他
- 当前源工程、工作区副本、交接副本的关系：
- 当前证据日期（`YYYY-MM-DD`）：
- 是否存在 Git：是 / 否；仓库根：
- 当前允许范围：只读 / 可修改指定源 / 可构建 / 其他

## Unity 与 Avatar 入口

- Unity 版本（`ProjectSettings/ProjectVersion.txt`）：
- 当前场景（`Assets/...`）：
- Avatar 根完整层级路径：
- `VRCAvatarDescriptor` 所在对象路径：
- 目标平台：PC / Android / 两者分开 / 未决定
- 目标 Avatar 是否为测试 Clone、Prefab Stage 或 NDMF 生成物：

## 包与版本

| Package ID | 当前版本/来源 | 是否可升级 | 证据文件 | 备注 |
| --- | --- | --- | --- | --- |
| `com.vrchat.base` | | 否 | `Packages/manifest.json` | |
| `com.vrchat.avatars` | | 否 | `Packages/manifest.json` | |
| `nadena.dev.modular-avatar` | | 先不升级 | manifest/lock/package.json | |
| `nadena.dev.ndmf` | | 先不升级 | manifest/lock/package.json | |
| `com.anatawa12.avatar-optimizer` | | 按测量决定 | manifest/lock/package.json | |
| `jp.lilxyzw.liltoon` | | 按素材要求 | manifest/lock/package.json | |
| `com.coplaydev.unity-mcp` | | 先确认来源 | manifest/lock/package.json | |
| 其他构建相关包 | | | | |

- `file:` / embedded / 外部绝对路径包：
- 不应重复安装或随意升级的包：
- 版本信息最后复核日期：

## Provider 与工具职责

| 角色 | 已安装/当前使用 | 版本 | 谁拥有源配置 | 结论证据层 |
| --- | --- | --- | --- | --- |
| Wardrobe / clothing | | | | |
| Face / expression | | | | |
| Props / feature prefabs | | | | |
| Preview | | | | |
| Optimization | | | | |
| Unity MCP | | | | |
| Blender/DCC | | | | |

## 目录与命名

- 场景、Prefab、菜单、参数、Controller、服装和生成物命名约定：
- 当前源资产目录：
- 禁止当作源文件的目录：`Library/`、`Temp/`、`Logs/`、`Obj/`、生成 Clone、旧截图和旧缓存
- 关键关键词：
- PC/Quest 或版本变体的分离规则：

## 已知风险与回滚

- 当前编译错误/警告：
- MCP 状态/实例/过期风险：
- Unity 锁定、管理员运行或系统弹窗：
- 已有未保存场景改动：
- 备份位置和恢复方式：
- 删除/覆盖/保存/构建/上传的额外确认要求：

## 报告与验证约定

- 静态报告位置（默认 `Temp/CodexReports/`，不放 `Assets/`）：
- `UNITY_RESOLVED` 的获取方式：
- `NDMF_BUILT` / `SDK_BUILD` 的获取方式：
- Runtime 测试方法：
- 目前明确未验证的项目：
