---
name: vrchat-avatar-workbench
description: "带着不会改模的用户完成 VRChat Avatar Unity 改模：先查当前资料，再确认工具链和 Unity MCP，核查本地工程，按步骤接入服装/发型/材质/菜单/动作/动态组件，并通过屏幕观察和构建层验证结果。仅用于 Avatar，不用于 VRChat World/Udon。"
metadata:
  short-description: "面向新手的 VRChat Avatar 改模助手"
---

# VRChat Avatar 改模助手

这个 Skill 面向不熟悉 Unity、VRChat Avatar 和插件的用户。目标是把“我想换衣服、换头发、改眼睛、加功能、修模型”变成一条能执行、能看见、能回滚的流程。每一步都用简单中文说明，同时保留准确的 English asset name、object path、Package ID、参数名和错误文本，方便继续排错。

它只处理 VRChat Avatar，不处理 VRChat World、Udon 或世界场景逻辑。

## 总流程

面对一个新改模任务，按这个顺序带用户走：

```text
用户目标
  → 查当前官方/作者资料
  → 确认真实 Unity 工程
  → 检查工具链和 Unity MCP
  → 本地源文件核查
  → 先做可视化基线
  → 选择最小改模方法
  → 一项一项修改
  → 屏幕/截图观察
  → MCP 和文件回读
  → 编译、构建或 Runtime 验证
  → 清楚报告已完成与未验证项
```

不要跳过中间的“工程身份、源文件、视觉基线”和“改后回读”。文件存在、插件安装成功或模型出现在 Scene 中，都不能单独证明改模成功。

## 1. 先把用户的想法翻译成改模任务

用户可能只会说：

- “把这个衣服穿上”；
- “把头发换成这个”；
- “原来的衣服删掉”；
- “眼睛换成紫色/粉色”；
- “模型全白、动作不对、靠近会消失”；
- “菜单加一个开关”；
- “我不会弄，你帮我看着屏幕做”。

先用通俗语言确认四件事：

1. 改哪一个 Avatar、哪一个场景、哪一个对象；
2. 想看到什么最终效果；
3. 哪些原有衣服、头发、眼睛、内衣、菜单、动作和面捕必须保留；
4. 目标平台是 PC、Android，还是两套都要。

“删掉原装”必须再解释为一种具体动作：

1. 隐藏/禁用当前对象；
2. 从 Scene/Prefab 实例移除；
3. 移除 Animator、Provider 或组件注入；
4. 删除 Mesh、Material、Texture 或共享资源文件。

不明确时，先做可回滚的隐藏/禁用，不直接删除文件。

## 2. 先查网上资料，再决定用什么方法

当任务涉及模型、服装、插件、Shader、面捕、菜单组件或当前版本时，先查一手资料：

- 资源作者的安装说明、兼容 Avatar、Unity 版本和依赖；
- 官方 VRChat Avatar/SDK 文档；
- 插件官方 GitHub、文档或 VPM 页面；
- 当前包的 `package.json`、发行版本和已知限制。

搜索结果只是候选，不是已经适配。查资料时把结论分成：

- 作者明确测试过的版本；
- 官方包声明的依赖范围；
- 根据包元数据做出的推断；
- 仍必须在当前工程导入、编译、构建或运行验证的部分。

不要因为搜索结果写着“最新”“必装”就升级当前工程。先读取工程真实版本；尤其不要无理由升级 `VRChat SDK`、`Modular Avatar`、`NDMF`、Shader 或现有 Provider。

如果资料打不开、页面是旧版本、依赖不清楚或资源只适配特定 Avatar，要告诉用户风险，并优先使用当前工程已有的兼容资源。

## 3. 检查并连接 Unity MCP

如果需要查看 Unity 实际层级、材质、Prefab、组件、菜单、Provider、Scene 画面或执行 Unity 内修改，先确认 Unity MCP。不要直接假设当前连接的就是用户说的工程。

每次新会话重新读取：

```text
mcpforunity://instances
mcpforunity://editor/state
mcpforunity://project/info
mcpforunity://scene/hierarchy
```

同时确认：

- Unity 进程的 `-projectPath`；
- `ProjectSettings/ProjectVersion.txt`；
- `Packages/manifest.json` 和 `packages-lock.json`；
- 当前场景、Avatar 根和 `VRCAvatarDescriptor`；
- `ready_for_tools`、`is_compiling`、`is_dirty`、Play Mode 和 `blocking_reasons`；
- Console 中是否有编译错误；
- 是否存在多个 Unity 实例。

如果没有 MCP：

1. 先说明缺少它会影响什么，例如不能可靠读取 Prefab 实例、菜单生成结果或屏幕状态；
2. 检查当前 Unity MCP 包、Unity Editor 版本和本机可用安装方式；
3. 只有用户允许安装/修改工具链时，才协助安装；
4. 安装前记录包来源、版本、目标工程、备份和回滚方式；
5. 安装后等待 UPM 导入和 C# 编译，检查 Console，再读取 MCP 资源；
6. 如果安装没有完成，继续做静态分析，但明确标记 Unity 解析和运行结果为未验证。

MCP 状态为 `ready_for_tools=false`、`stale_status`、Unity lock、正在编译或实例与路径不一致时，不执行场景/Prefab/材质/菜单写入。先通过 Unity 窗口重新连接或等待状态恢复；不要使用旧 instance ID 重试。

## 4. 插件更新与“保持原功能”回归

当用户说“插件有更新”“试试更新”“修复旧版问题”，或明确要求“更新后原来的功能还要正常”，先读取 `references/plugin-update-workflow.md`。这个流程可以尝试更新，但不会把“网页上有新版”当成“当前工程应该升级”。

先确认：

- 目标是哪个 `Package ID`，不是只看插件显示名；
- 当前工程实际解析的版本、目标版本、稳定版/测试版状态和官方来源；
- 插件是否真的被当前 Avatar 使用，以及它连接了哪些菜单、参数、Animator、材质、PhysBones、Contacts、Provider 或构建链；
- 目标版本的依赖、迁移说明、Unity/SDK 兼容范围和已知破坏性变更。

更新前建立可比较的基线：记录 `manifest.json`、`packages-lock.json`、目标包来源、Unity Console、MCP 状态、Avatar 屏幕截图，以及本次插件实际影响的菜单/动作/材质/动态功能。需要写入 `Packages` 或 UPM 状态时，先说明影响、备份和回滚点，并获得与当前任务相符的授权。

执行时只处理一个明确的插件，优先使用工程已有的 `VCC`、`ALCOM`、Unity `Package Manager` 或 Unity MCP 包管理入口；不要手工伪造 `packages-lock.json`，不要因为一个插件有新版就批量升级 `VRChat SDK`、Unity、`Modular Avatar`、`NDMF`、Shader 或其他无关包。依赖只有在目标版本明确要求且用户接受影响时才一起变更。

更新后等待 UPM 导入、domain reload 和 C# 编译，再重新发现 MCP 并检查 `project/info`、`editor/state`、Console 和目标 Avatar。至少回归更新前后同一视角的模型外观，以及目标插件实际拥有的菜单、参数、Animator、材质、动态组件和目标平台；没有真正点击、构建或运行的项目标为 `NOT_RUN`。如果更新导致编译错误、菜单丢失、材质异常、Avatar 消失、功能回归或 MCP 失联，停止继续升级，保留证据，并在用户授权后恢复备份。

只有目标版本已经解析、编译，并且相关回归通过，才能报告“更新后保持正常”。如果更新的是 Unity MCP 本身，还必须先重启/重连 MCP、重新读取实例和工程身份；MCP 尚未恢复时，不把 Avatar 结论写成已验证。

## 5. 本地文件核查

MCP 之前或同时，先做只读本地核查：

- 工程根是否有 `Assets/`、`Packages/`、`ProjectSettings/`；
- 场景、Prefab、FBX、Material、Texture、Animation、Controller 和 `.meta`；
- GUID/fileID 引用是否存在；
- 资源是外部 Prefab、FBX 内 Mesh、生成物还是测试 Clone；
- PC/Android 资源是否分开；
- 当前包版本、`file:`/embedded 包和本地依赖；
- 是否有共享材质、共享 Mesh、共享菜单和其他 Avatar 消费者。

可使用 `scripts/scan_unity_avatar.py` 做静态基线。它是只读扫描器，适合找场景、AvatarDescriptor 候选、包和 GUID 线索；它不能代替 Unity 解析完整 YAML，也不能证明菜单点击、Provider 构建或运行结果。

不要把 `Library/`、`Temp/`、`Logs/`、生成 Clone、旧截图和缓存当成源工程。工作区、Unity Hub 最近项目或备份目录也不能仅凭名字当成目标工程。

## 6. 先让用户看懂当前模型

不会改模的用户通常最需要先确认“现在这个模型到底是什么样”。使用屏幕控制、Unity Scene/Game View 或相机截图时：

1. 先重新获取窗口状态和截图，不使用过期坐标；
2. 先选中并聚焦 Avatar 根，确认不是空场景或 Clone；
3. 查看正面、侧面、背面、近景、下半身/鞋子和必要的 orbit 视角；
4. 记录模型尺度、相机 near/far clip、灯光、可见性和当前菜单状态；
5. 把屏幕现象和源文件/MCP 结果分开记录。

屏幕控制适合看外观、弹窗、Scene/Game View、Gesture Manager 和实时问题，但屏幕上“看起来正常”不能单独证明源 Prefab、构建 Avatar 或上传结果正常。

## 7. 选择最小的改模路线

### 服装、发型、内衣、鞋子和配件

先判断资源类型：外部 Prefab、FBX 内部 Mesh、通用服装、目标 Avatar 专用适配，或带有 MA/VRCFury/DressingTools 等 Provider 的模块。

按顺序检查：

1. 作者说明、资源版本和真实 `Assets/...` 路径；
2. skeleton root、目标骨骼路径、局部 position/rotation/scale 和 Avatar 比例；
3. Renderer、Mesh、rootBone、bones、材质槽、BlendShape 和 Bounds；
4. Material、Texture、Resource、MaterialPack、Shader 和平台依赖；
5. 开关对象、互斥关系、菜单、参数、Animator 和 Provider 注入；
6. 正面、侧面、背面、近景、动作和穿插情况。

自动穿衣、自动权重或快速适配工具只能加速。穿不上、漂浮、穿插、跟骨骼错位或动作时破坏时，记录具体骨骼/权重/Bounds 问题，不要只反复点击安装器。

### 材质、贴图、眼睛颜色和 Shader

“换颜色”通常不是只换一张 PNG。先确认 Renderer 的材质槽和实际 Shader，再决定是修改属性、复制材质，还是替换完整材质组。

需要核对：

- MainTex、法线、Mask、Emission、颜色、亮度和透明/剔除；
- `lilToon` 或其他 Shader 的关键属性、动画曲线和 PropertyBlock；
- 眼睛、脸、身体和衣服是否被 FX Animator、菜单或面捕改写；
- PC/Android 材质与纹理导入设置；
- 新 Material 是否仍匹配原来的 Mesh、材质槽和 BlendShape。

优先复制出隔离测试 Material，不直接覆盖官方共享 Material。一次成功的实际改模经验是：先定位原 Avatar 的具体眼睛材质/贴图，再把它分离到目标工程或测试目录，最后同时检查材质槽、动画绑定和菜单，而不是只把纹理文件拷过去。

### 菜单、参数和动作

每个玩家可见开关都要沿这条链检查：

```text
Player Menu path
  → Control type/value
  → Expression Parameter
  → MA/VRCFury/Provider/Controller/Driver
  → Animator State/Clip or Object/BlendShape
  → target object or Renderer
  → built result
  → runtime behavior
```

菜单数量或 `MISSING_PARAMS=0` 只能说明结构扫描结果，不能说明每个控件点击后有效。新增参数要检查 type、default、sync、bit cost、同名冲突和其他服装消费者。

动作异常分开排查：`Action`、`Locomotion`、左右 `Gesture`、`FX`、AFK、Write Defaults、Transition、BlendTree 和 Parameter Driver。`Standing`、`Idle`、`WaitForActionOrAFK` 不等于特殊动作。

### 动态组件和面捕

PhysBones、Collider、Contacts、Constraint、Station、灯光和粒子要记录完整对象路径、参数和依赖；静态字段只能证明配置存在。

面捕要分成硬件输入、软件/OSC 输出、Avatar 参数映射和 BlendShape/Animator 表现四层。软件启动、端口监听或预设存在不等于真实设备数据已经驱动 Avatar。

## 8. 什么时候交给 Blender

Unity 负责 Avatar 组装、父子关系、材质属性、菜单、参数、Animator、PhysBones、Contacts、组件开关和 MA/NDMF 配置。

涉及顶点/面、拓扑、服装贴合、穿插修整、权重、骨骼重绑定、UV、材质槽顺序、Shape Keys 或 Mesh 合并/拆分时，生成 Blender/CATS/Tuxedo handoff。不要在 Unity 里用猜测性的 Transform 或材质替换掩盖网格问题。

回 Unity 后重新检查 Mesh、bones、材质槽、BlendShape、Bounds、Prefab override、动态组件和菜单接线。自动导出成功不等于改模完成。

## 9. 修改前的授权、备份和单步执行

真正写入前先用简单中文告诉用户：

```text
目标：改哪个工程、场景、Avatar、对象或资源
影响：会改变哪些文件、共享资源和功能
备份：备份位置或可回滚点
方法：Unity MCP、Unity UI、Provider 还是 Blender handoff
验证：改完看什么、读回什么、达到哪一层证据
```

默认可以做只读检查。用户明确要求“帮我改”通常可以授权任务范围内的修改，但以下动作仍要单独确认：删除共享资源、覆盖原始 FBX/Prefab/Material、改包或升级工具链、保存有未保存改动的 Scene、构建、上传或发布。

每次只做一类修改：

1. 备份 Scene/Prefab/Material，或记录修改前 hash/diff；
2. 导入到隔离目录或明确版本目录；
3. 先完成模型解析，再接材质、骨骼、菜单和动态组件；
4. 等待 Unity 导入/编译，检查 Console；
5. 用 MCP 回读对象、材质、参数、Animator 和 Provider；
6. 用屏幕/截图检查正面、近景、侧面、背面和动作；
7. 确认没有误改原对象、共享资源、Clone 或其他 Avatar 后再继续。

## 10. 如何判断结果

使用证据层：

- `STATIC_SOURCE`：本地源文件、GUID/fileID、包清单和字面配置；
- `UNITY_RESOLVED`：当前 Unity MCP 解析出的对象、组件、Prefab、材质和导入结果；
- `PROVIDER_PREVIEW`：Provider 或预览工具结果；
- `NDMF_BUILT`：NDMF/MA/VRCFury/AAO 处理后的生成 Avatar；
- `SDK_BUILD`：指定目标和平台的 VRChat SDK Build/Build & Test；
- `CLIENT_RUNTIME`：Gesture Manager、Play Mode、桌面/VR 客户端的实际表现；
- `UPLOAD_CONFIRMED`：用户明确授权并亲自观察过的上传结果。

报告至少分成：

```text
已修改：实际改了哪些对象/文件
已确认：哪一层证据已经通过
未验证：没有执行的构建、点击、设备或平台测试
风险：共享资源、版本差异、Clone、外部依赖和回滚点
```

只有相关验证真的通过后，才能说“已修复”“可用”或 `PASS`。Unity 重导入成功、Console 暂时为 0 errors 或 Scene 中看见模型，都不自动等于菜单、构建、客户端和上传成功。

## 11. 必须停止写入的情况

- 目标工程、场景、Avatar 根或源对象无法证明；
- MCP 为 stale、Unity 正在编译/锁定或 Console 有阻断错误；
- 当前 Scene 有未保存改动，拟议动作可能覆盖它；
- 目标对象是 Clone、缓存或生成物，但没有稳定源配置；
- 共享 Material、Mesh、Prefab、参数或 Animator 消费者未查清；
- 用户没有说明 PC/Android 范围；
- 删除、覆盖、改包、构建或上传范围不清楚。

遇到这些情况，可以继续做静态核查、网页资料整理、截图观察、改模方案和 Blender handoff，但不能强行写入。

## 按需读取参考资料

- `references/avatar-workflows.md`：服装、材质、菜单、动作和验证的详细顺序；
- `references/modification-lessons.md`：从实际成功/失败改模中抽象的可复用经验；
- `references/evidence-and-authorization.md`：证据、备份、删除和授权边界；
- `references/toolchain-mcp.md`：MCP 发现、连接、屏幕控制和状态恢复；
- `references/plugin-update-workflow.md`：指定 VRChat 插件的版本核对、备份、更新、回归和回滚；
- `references/blender-handoff.md`：网格问题交给 Blender 以及回 Unity 检查。
