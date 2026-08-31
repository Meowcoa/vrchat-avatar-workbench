# VRChat Avatar Workbench

一个面向 Codex 的 VRChat Avatar Unity 改模 Skill，专门帮助不熟悉 Unity、VRChat Avatar 和插件的用户完成实际改模。

它会先查当前的官方/作者资料，再确认真实 Unity 工程和工具链；需要时连接或协助安装 Unity MCP，核查本地资源，使用屏幕控制查看模型，最后逐项完成并验证服装、发型、材质、菜单、动作、动态组件，以及用户明确要求的插件更新回归。

本项目只面向 VRChat Avatar，不处理 VRChat World、Udon 或世界场景逻辑。

## Features

- **Research first**：查作者安装说明、官方文档、Unity/VRChat SDK 和插件依赖，区分已确认版本与待验证推断。
- **Project discovery**：确认真正的 Unity `project path`、Unity 版本、当前 Scene、Avatar 根和 `VRCAvatarDescriptor`。
- **Unity MCP workflow**：发现 MCP 实例、检查 `editor/state`，处理缺少 MCP、连接过期、实例错误和编译阻断。
- **Local asset inspection**：检查 Prefab、FBX、Mesh、Material、Texture、Animator、菜单、参数和 GUID/fileID 引用。
- **Visual guidance**：通过 Scene/Game View、相机或屏幕控制查看正面、近景、侧面、背面、下半身和动作状态。
- **Avatar modification**：处理服装、发型、眼睛、内衣、鞋子、配件、材质、Expression Menu、Parameters、Animator、PhysBones、Contacts 和面捕接入。
- **Plugin update with regression**：只核对和更新用户指定的 Avatar 插件，记录当前/目标版本与来源，备份 UPM 状态，并用 MCP、屏幕、功能链和构建层检查更新后是否保留原功能。
- **Troubleshooting**：排查全白、紫色、错色、穿插、漂浮、动作异常、菜单无效和靠近消失。
- **Blender handoff**：遇到拓扑、权重、UV、Shape Keys 或骨骼重绑定问题时，生成 Blender/CATS/Tuxedo 交接信息并回 Unity 复核。
- **Evidence-based verification**：明确区分源文件、Unity 解析、Provider/NDMF 构建、SDK Build、Runtime 和上传结果。

## Workflow

改模任务通常按以下顺序进行：

```text
用户目标
  → 官方/作者资料
  → Unity 工程与 Avatar 身份
  → 工具链和 Unity MCP
  → 本地源文件核查
  → 屏幕/截图基线
  → 选择最小改模方法
  → （有明确请求时）单插件版本核对/更新
  → 一项一项修改
  → MCP、文件和画面回读
  → 编译/构建/Runtime 验证
```

每次只处理一个明确的改模单元，例如一套衣服、一个发型、一组眼睛材质或一条菜单功能链。资源出现、插件安装完成或模型在 Scene 中可见，都不能单独证明改模成功。

## Use cases

可以直接这样提出任务：

```text
使用 $vrchat-avatar-workbench，带我把这套衣服穿到当前 Avatar 上。
先查作者说明，再检查 Unity MCP、本地资源和当前模型，不要直接改文件。
```

```text
使用 $vrchat-avatar-workbench，我不会改模。
请通过屏幕一步一步带我检查头发、眼睛材质、菜单和动作，确认后再修改。
```

```text
使用 $vrchat-avatar-workbench，当前模型全白并且靠近会消失。
先做只读诊断，分别检查材质、灯光、Clone、Bounds、相机和 Animator。
```

```text
使用 $vrchat-avatar-workbench，检查这个衣服为什么穿插。
判断是 Transform、骨骼、权重、Bounds 还是材质问题，需要 Blender 时生成交接清单。
```

```text
使用 $vrchat-avatar-workbench，检查当前 Avatar 用到的 VRCFury 或 Gesture Manager 是否有稳定版更新。
只更新我指定的插件，先备份并记录更新前的菜单、动作和模型画面，更新后确认原功能还在；失败就停下并准备回滚。
```

## Environment

- Codex；
- 一个完整的 Unity VRChat Avatar 工程；
- 与 `ProjectSettings/ProjectVersion.txt` 匹配的 Unity Editor；
- 当前工程使用的 VRChat SDK、Shader 和 Avatar Provider；
- 工程已有的 VCC、ALCOM、Unity Package Manager 或其他可追溯的包管理入口（如任务涉及插件更新）；
- 需要 Unity 解析、屏幕观察或项目修改时，必须有对应的 Unity MCP 或明确可用的编辑器控制通道；
- 需要查询当前版本、作者说明或下载依赖时，应允许访问官方/作者资料。

没有 MCP 时，Skill 仍可做本地静态核查和改模方案，但不会把静态文件、旧截图或缓存说成已经解析、构建或运行成功。需要 MCP 时，Skill 会先说明安装影响和回滚方式，再在得到授权后协助安装。

## Installation

将仓库根目录直接放入 Codex Skills 目录，确保 `SKILL.md` 位于该目录第一层：

```text
%USERPROFILE%\.codex\skills\vrchat-avatar-workbench\SKILL.md
```

从 GitHub 克隆的 PowerShell 示例：

```powershell
git clone https://github.com/<owner>/<repository>.git `
  "$env:USERPROFILE\.codex\skills\vrchat-avatar-workbench"
```

安装后新建 Codex task 或重启 Codex，使 Skill 重新被发现。也可以直接在当前 Skill 根目录显式调用 `$vrchat-avatar-workbench`。

## Repository structure

```text
vrchat-avatar-workbench/
├── SKILL.md
├── README.md
├── LICENSE
├── CHANGELOG.md
├── agents/
│   └── openai.yaml
├── assets/
│   ├── AvatarAudit.template.md
│   ├── CodexProjectProfile.template.md
│   └── TOOLCHAIN_PROFILE.template.md
├── references/
│   ├── avatar-workflows.md
│   ├── blender-handoff.md
│   ├── evidence-and-authorization.md
│   ├── modification-lessons.md
│   ├── plugin-update-workflow.md
│   └── toolchain-mcp.md
└── scripts/
    ├── check_github_ready.py
    ├── read_mcp_sse.py
    └── scan_unity_avatar.py
```

`SKILL.md` 是执行入口；`references/` 保存按需读取的改模经验；`assets/` 是复制到实际 Unity 工程使用的模板；`scripts/` 提供只读的静态扫描和 MCP 资源读取辅助工具。

## Safety boundaries

- 检查和诊断默认只读；明确要求改模后，也只修改已确认的目标范围。
- 不直接覆盖原始 FBX、Prefab、共享 Material 或作者资源；需要实验时先复制隔离。
- 不在 MCP stale、目标工程不明、Unity 编译阻断或 Scene dirty 风险未处理时写入。
- 不把菜单数量、文件存在、Preview 或成功导入写成完整功能通过。
- 不因一个插件有新版就批量升级整个工程；更新前记录版本、来源、备份和基线，更新后按实际功能回归，未测试项明确标为 `NOT_RUN`。
- 构建、设备测试、客户端测试和 Avatar 上传是不同的验证层级；上传不会自动执行。
- 不包含任何 Avatar 模型、贴图、Unity 工程、账号信息、Token、Cookie 或私有资源。

## License

This project is released under the [MIT License](LICENSE).
