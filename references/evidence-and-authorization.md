# 证据层与授权边界

本文件是所有 VRChat Avatar 改模任务的判断底座。它解决两个常见错误：把低层证据说成最终行为，以及把用户授权的一个动作扩大成一连串未授权写入。

## 1. 证据优先级

优先级从高到低不是“越高就能回答所有问题”，而是“同一事实发生冲突时先相信更接近当前目标、且证据层更高的来源”：

1. 当前目标工程磁盘上的源文件、当前选定 Unity MCP 实例和当前明确授权的构建/运行结果；
2. 当前工程自己的 `CodexProjectProfile.md`、`TOOLCHAIN_PROFILE.md`、审计报告和备份差异；
3. 当前安装包的 `package.json`、Lock、官方文档和版本发布页；
4. 日期化的历史对话、记忆、旧报告、截图和缓存；
5. 社区文章、视频或文件名推断。

历史记录只能提供搜索词和假设。任何可能漂移的事实（Unity、SDK、包版本、当前实例、菜单状态、构建结果）都必须回到当前工程复核。

## 2. 标准证据标签

| 标签 | 含义 | 可以证明 | 不能单独证明 |
| --- | --- | --- | --- |
| `STATIC_SOURCE` | `Assets/`、`Packages/`、`ProjectSettings/`、`.meta`、GUID/fileID、源包目录 | 文件存在、字面字段、引用链候选、包来源 | Unity 是否成功导入、Prefab 解析后状态、玩家可见行为 |
| `UNITY_RESOLVED` | 当前匹配 Unity 版本解析出的层级、组件、导入资源、Prefab 实例 | 对象实际存在、非激活对象、材质/骨骼/组件当前值 | NDMF/MA/VRCFury/AAO 后的最终状态 |
| `PROVIDER_PREVIEW` | Provider 或预览工具生成的临时/预览结果 | 该 Provider 在当前预览中的行为和生成意图 | SDK Build、客户端上传结果 |
| `NDMF_BUILT` | NDMF/MA/VRCFury/AAO 等构建后的生成 Avatar | 构建链生成了什么、菜单/参数/Renderer 的构建态结果 | VRChat 客户端中的真实输入、已上传头像 |
| `SDK_BUILD` | VRChat SDK 的明确 Build/Build & Test 日志和产物 | SDK 对一次明确目标的验证结果 | 另一个场景、另一个平台、上传成功 |
| `CLIENT_RUNTIME` | Gesture Manager、Play Mode、Build & Test、桌面/VR 客户端实际操作 | 指定运行层的可见/可交互结果 | 未运行的其他平台和上传后的结果 |
| `UPLOAD_CONFIRMED` | 用户明确授权并观察过的上传头像 | 指定账户/目标上的结果 | 其他 Avatar、其他版本或未来变更 |

兼容旧资料的别名：`source_static` ≈ `STATIC_SOURCE`，`unity_resolved` ≈ `UNITY_RESOLVED`，`build_resolved` ≈ `NDMF_BUILT`。不要因为旧报告用了小写标签就省略更精确的 Provider、SDK 或 Runtime 层。

## 3. 结论状态

- `CONFIRMED`：证据层足以支持这句话，目标和时间明确。
- `INFERRED`：根据包元数据、结构或相似案例推断；必须说明推断依据。
- `NOT_RUN`：需要的验证没有执行。
- `BLOCKED`：有明确阻断原因，例如目标目录不可读、Unity 被锁定、编译失败或用户未授权。
- `MCP_REQUIRED`：静态文件不能回答，必须连接正确 Unity MCP 实例。
- `STALE`：结果来自过期快照、旧缓存、旧 Clone 或旧报告，不能作为当前结论。

报告不要把 `NOT_RUN` 写成“暂时没问题”，也不要把 `INFERRED` 写成“已经兼容”。

## 4. 授权矩阵

| 动作 | 默认权限 | 需要的额外确认 | 最低验证 |
| --- | --- | --- | --- |
| 读取工程源文件、包清单、旧报告 | 允许只读 | 目标路径必须明确 | 路径、时间、证据范围 |
| 读取 Unity MCP 资源 | 允许只读 | 先确认实例与项目路径 | `instances`、`project/info`、`editor/state` |
| 操作 Scene/Game View 截图、查看面板 | 只限当前任务 | 不能借机改设置或保存 | 截图来源、目标对象、运行层 |
| 调用 Unity 语义查询/Provider Preview | 只读时允许 | 不能触发保存、构建或上传 | 当前实例、状态、Console、完成标记 |
| 修改 Scene/Prefab/Animator/Material/参数 | 不默认允许 | 目标、影响、备份、方法、验证 | 磁盘 diff + Unity/MCP 回读 |
| 导入模型、贴图、UnityPackage 或插件 | 不默认允许 | 来源、隔离目录、覆盖风险、依赖、回滚 | 导入日志、资源路径、引用和编译 |
| 保存 Scene/Prefab/Assets | 不默认允许 | 明确保存哪个对象/文件 | 保存前后 hash/diff、脏状态、回读 |
| 改 `manifest.json`、Lock、embedded/file 包 | 不默认允许 | 版本、来源、依赖、备份、恢复 | UPM 解析、编译、版本回读 |
| 构建/Build & Test/生成优化副本 | 不默认允许 | 目标 Avatar、平台、输出位置、是否可写 | 构建完成标记、日志、产物和错误 |
| 上传/发布 Avatar | 永不自动执行 | 用户明确授权账户、目标和平台 | 只报告用户自行确认的结果 |

“用户说请帮我改”通常足以授权任务范围内的修改，但仍不能推断删除共享资产、改包、上传或系统级操作；这些动作要单独确认。

## 5. “删除”必须拆成四种动作

当用户说“删掉原装/删衣服/减少显存”时，先显示可选含义：

1. **隐藏/禁用**：保留源资产，只改变当前实例或菜单状态；最容易回滚。
2. **从 Scene/Prefab 实例移除**：改变实例结构，需检查 Prefab override、菜单、动画和生成器引用。
3. **移除组件或注入链**：删除 MA/VRCFury/Animator/Constraint/Contact 等功能来源，不一定删除网格。
4. **删除资产文件**：最后一步，可能影响共享消费者、其他 Avatar 和版本回滚；必须有明确备份及再次确认。

先做引用清单：对象路径、Prefab、Mesh、Material、Texture、Animation、Controller、Menu、Parameter、Provider、约束和动态组件。没有清单，不做第 3/4 类动作。

## 6. 备份与回滚

- 优先使用项目已有 Git、Unity Undo 或明确命名的备份目录；没有 Git 时复制修改前源文件并记录 SHA-256。
- 备份目录必须与源目录清楚区分，例如 `Backups/Codex/<date>-before-<change>/`，不得把备份放到会被当成当前 Avatar 的同名路径。
- 对一次修改保留：目标文件、修改前 hash、修改后 hash、授权内容、执行方法、验证输出和回滚方法。
- 不覆盖原始 FBX、Blend、Prefab、共享 Material、下载包或作者资源来“试试看”；测试材质、测试场景和临时 Clone 要隔离。
- 关闭或停止 Play Mode 后，先检查是否产生外部修改或 NDMF 生成物，再决定是否刷新；不要把刷新当成保存。

## 7. 必须停止写入的条件

- 目标项目、场景或 Avatar 根无法证明；
- MCP `ready_for_tools=false`、`stale_status`、实例与路径不一致；
- Unity 正在编译、锁定项目或 Console 有阻断性编译错误；
- 当前 Scene 有用户未保存改动，而拟议动作可能覆盖它；
- 目标是生成物、缓存或 Clone，却没有找到稳定源配置；
- 包版本和作者测试环境不一致，且导入/构建验证尚未完成；
- 用户未说明是 PC、Android 还是两套独立 Avatar；
- 删除/覆盖/上传会影响范围外对象或外部人员。

可继续做的事情是静态取证、生成方案、写 handoff、列出恢复条件，不是强行写入。

## 8. 报告示例

```text
结论：部分完成（CONFIRMED / NOT_RUN）
目标：<project> / Assets/<scene>.unity / <avatar path>
已确认：STATIC_SOURCE：manifest 中有 nadena.dev.modular-avatar；UNITY_RESOLVED：Renderer 当前材质槽非空。
推断：可能由动画改写 Shader 属性导致发白；尚未运行 NDMF_BUILT 或 CLIENT_RUNTIME。
未验证：完整菜单点击、Android Build、VRChat 上传。
改动：无；没有保存、删除、构建或上传。
最小下一步：授权一次隔离 Play Mode 观察，并保留现有 Scene 不保存。
```
