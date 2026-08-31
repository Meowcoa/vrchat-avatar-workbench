# VRChat 插件更新与回归验证

当用户希望更新某个 VRChat Avatar 插件、修复旧版本问题，或确认“更新后原功能还能不能正常用”时，使用本流程。它只更新明确指定的插件，不把“有新版本”理解成升级整个 Unity 工程。

本参考只处理 Avatar 工具链中的包更新。VRChat SDK、Unity Editor、MCP 服务端和第三方 Avatar 插件的更新边界不同：先确认用户要更新的对象，再选择对应入口和验证层。不要因为某个包的 release 页面有新版本，就顺手升级其他包。

官方资料入口（按需读取）：

- [VRChat：Updating the SDK](https://creators.vrchat.com/sdk/updating-the-sdk)：确认 SDK 更新与旧版/Package-based 工程的边界；
- [Unity：Project manifest](https://docs.unity3d.com/Manual/upm-manifestPrj.html)：确认工程直接依赖写入 `Packages/manifest.json`；
- [Unity：Lock files](https://docs.unity3d.com/Manual/upm-conflicts-auto.html)：确认 `packages-lock.json` 是依赖解析结果；
- [Unity：Package Manager](https://docs.unity3d.com/Manual/Packages.html)：选择工程已有的包管理入口。

## 1. 更新前先查资料

先查目标插件的一手来源：

- 官方 GitHub release、changelog 或文档；
- VPM registry、Unity `package.json` 和包的依赖声明；
- 作者的安装说明、迁移说明、兼容 Unity/SDK 范围和已知破坏性变更。

记录：

```text
PACKAGE_ID       目标 Package ID
CURRENT_VERSION  当前工程实际版本
TARGET_VERSION   用户想要的版本或经过资料确认的候选版本
SOURCE           VPM / Git tag / local package / other official source
REASON           Bug fix / compatibility / feature / user request
RISK             breaking change / dependency / generated output / unknown
```

“Latest”只是网页标签，不是充分证据。必须写明检查日期、版本号和来源；如果只能确认包级兼容范围，不能写成当前 Avatar 已兼容。

## 2. 更新前确认工程和插件真的在使用

先读取当前工程：

- `ProjectSettings/ProjectVersion.txt`；
- `Packages/manifest.json`；
- `Packages/packages-lock.json`；
- 目标插件的 `package.json`；
- 当前 Scene、Avatar 根、`VRCAvatarDescriptor` 和 Provider/组件；
- 该插件是否拥有菜单、参数、Animator、材质、PhysBones、生成对象或构建链。

必须区分：

- 插件已下载但没有被工程解析；
- 包已解析但没有被目标 Avatar 使用；
- 源组件存在；
- NDMF/MA/VRCFury/Provider 生成结果存在；
- 旧版本的功能已经通过测试。

如果目标插件没有被当前 Avatar 使用，先告诉用户更新不会自动改善这个 Avatar 的表现；不要为“可能以后用到”升级无关依赖。

如果没有可追溯的稳定版来源、只有来历不明的压缩包，或目标版本与当前 Unity/SDK 的兼容性无法判断，停止在版本审计和只读建议，不强行安装。`Latest`、下载完成和 Package Manager 列出候选版本都不是兼容性证明。

## 3. 设定更新范围和回滚点

真正写入前明确：

```text
TARGET       哪个 Unity 工程和哪个插件
FROM         当前已解析版本
TO           目标版本和来源
IMPACT       manifest/lock、依赖、脚本、生成物和 Avatar 功能
BACKUP       manifest、lock、包目录、项目备份或 Git 分支
BASELINE     更新前的编译、菜单、材质、动作、动态组件和截图结果
VERIFY       更新后要回归哪些功能
ROLLBACK     失败时恢复什么、由谁执行
```

只说“试试更新”时，默认只尝试目标插件的一个明确版本，并在执行前告诉用户会修改 `Packages`/UPM 状态。不要把多个插件批量升级后再猜是哪一个造成回归。

## 4. 执行更新

1. 保存或记录当前 Scene dirty 状态；不要覆盖用户未保存改动。
2. 备份 `manifest.json`、`packages-lock.json`、目标 package 的来源信息和受影响的项目文档。
3. 使用官方 VPM、官方 Git tag 或工程现有的包管理方式；不要使用来历不明的 zip、未固定的 `main` 或第二个同名包。
4. 一次只更新一个目标 Package ID；依赖包只有在目标版本明确要求时才更新。
5. 不要手工伪造 `packages-lock.json`。让 UPM/ALCOM/工程已有包管理器解析依赖；手动修改只能在用户明确授权且没有更安全的包管理入口时使用。
6. 等待 UPM 导入、Unity domain reload 和 C# 编译完成；读取 Console 和 `editor/state`。
7. 如果出现 Missing Script、编译错误、UPM 解析错误、GUID 断链或 Unity lock，停止继续升级。

把以下状态分开报告：

```text
downloaded/staged
manifest_changed
package_resolved
compiled
MCP_connected
avatar_regression_tested
build_or_runtime_tested
```

前面的状态不能代替后面的状态。

## 5. 更新后的回归测试

先做最小门禁，再做与目标插件相关的专项测试。

### 基础门禁

- Unity 能打开目标工程和目标 Scene；
- UPM/Manifest/Lock 的 Package ID 和版本一致；
- Console 没有新增阻断性编译错误；
- MCP 重新连接到正确工程，`project/info`、`editor/state` 和 Avatar 根一致；
- Avatar 在 Scene/Game View 中可见，未意外变成空对象或重复 `(Clone)`。

### Avatar 外观回归

至少比较更新前后的：

- 正面、近景、侧面、背面和下半身/鞋子；
- 服装、发型、眼睛、内衣和配件开关；
- 材质槽、Shader、贴图、颜色、Emission 和透明效果；
- 模型尺度、骨骼位置、Bounds、穿插和靠近相机时的可见性。

### 功能回归

按目标插件实际拥有的功能检查：

- Expression Menu、子菜单、参数类型/默认值/同步和位预算；
- Animator Controller、Layer、State、Transition、Clip、Driver 和目标路径；
- Modular Avatar/NDMF/VRCFury/其他 Provider 的源组件和生成结果；
- PhysBones、Collider、Contacts、Constraint、ParticleSystem 和灯光；
- Face Tracking、BlendShape、OSC 或 Gesture Manager（如果目标插件涉及）；
- PC 与 Android 的独立材质、构建和表现。

菜单能显示、资源能导入或 Preview 能生成，不等于功能回归通过。至少点击或等价验证本次更新会影响的控件；如果没有执行，标为 `NOT_RUN`。

按插件的实际角色选择回归重点：

| 插件角色 | 重点回归 | 不能单独作为成功证据 |
| --- | --- | --- |
| Preview/调试工具（例如 Gesture Manager） | 预览姿态、Gesture/AFK 控件、参数驱动和 Console | 工具窗口能打开 |
| 构建/组装工具（例如 Modular Avatar、VRCFury、NDMF 相关工具） | 源组件、菜单/参数/Animator 注入、生成 Avatar、SDK Build | Scene 中源对象还在 |
| 材质/Shader（例如 lilToon） | Material slot、贴图、颜色、透明、Emission、PC/Android 材质 | Shader 编译完成 |
| 动态/灯光工具（例如 PhysBones、Contacts、Light Limit Changer） | 近远距离可见性、动态响应、碰撞/约束、灯光表现和平台差异 | 组件字段存在 |

插件名称只是例子，不要假定每个工程都安装了这些工具；必须以当前工程的 `Package ID` 和实际消费者为准。

## 6. 构建和运行验证

根据用户目标逐层增加验证：

```text
STATIC_SOURCE
  → UNITY_RESOLVED
  → PROVIDER_PREVIEW / NDMF_BUILT
  → SDK_BUILD
  → CLIENT_RUNTIME
```

如果用户只要求“更新并确认工程没报错”，做到导入、编译、MCP 回读和基础画面回归即可，但要说明菜单点击、SDK Build、设备和客户端尚未验证。

如果用户要求保持原功能效果，至少要完成：

- 更新前后同一 Avatar、同一 Scene、同一视角的对比；
- 目标插件功能的菜单/参数/对象测试；
- 相关动画、材质和动态组件测试；
- 目标平台的构建或明确说明未构建。

如果目标是 `Unity MCP` 或其 server，而不是 Avatar 包：更新后先确认旧进程已退出、重新发现 `mcpforunity://instances`，再读取 `mcpforunity://editor/state` 和 `mcpforunity://project/info`。在 MCP 连接恢复前，任何 Avatar 外观或功能结论都只能标为 `STATIC_SOURCE` 或 `NOT_RUN`。

## 7. 失败处理和回滚

以下情况视为更新失败或部分失败：

- Unity 无法解析包或编译错误；
- 菜单、参数、Animator、材质、骨骼或动态组件丢失；
- 原来可见的 Avatar 变成空对象、紫色、发白、穿插或近距离消失；
- NDMF/MA/VRCFury 生成结果变化且没有用户要求；
- PC/Android 其中一个平台回归失败；
- 无法判断问题来自目标插件还是依赖升级。

先停止继续升级，并保存错误、版本和回归证据。若用户已授权回滚，恢复备份的 Manifest/Lock/包来源或 Git 回滚点，再等待 UPM 重新解析和编译，重新检查基础门禁。不要为了“清干净”直接删除 `Library/`、生成物或共享资产。

如果回滚也未验证，报告为 `ROLLBACK_UNVERIFIED`，不要写成已恢复。

## 8. 更新报告格式

```text
结论：更新成功 / 部分成功 / 已回滚 / 更新失败 / 未验证
插件：<Package ID>
版本：<from> → <to>
来源：<official source>
工程：<project> / <scene> / <avatar root>
改动：<manifest/lock/package/generated files>
基础门禁：<import / compile / MCP / console>
外观回归：<front / close / side / back / lower-body>
功能回归：<menu / parameter / animator / dynamics / target feature>
构建运行：<SDK_BUILD / CLIENT_RUNTIME / NOT_RUN>
保留功能：<passed items>
未验证：<items>
回滚点：<backup or git reference>
```

只有目标版本已经解析、编译和相关回归测试通过，才能说“更新后保持正常”。
