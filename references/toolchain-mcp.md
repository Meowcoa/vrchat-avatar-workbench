# Unity MCP、屏幕控制与本地核查

本文件用于带着新手完成改模前的工具链检查。它不规定某个固定 MCP 版本或固定插件清单；不同 Unity、VRChat SDK 和 Provider 版本必须以当前工程和官方资料为准。

## 1. 三条互补通道

```text
资料/官方文档  →  选择兼容的改模方法
本地文件       →  找到真实源资产、引用和版本
Unity MCP/屏幕  →  读取解析后的对象并观察实际画面
```

- 资料适合确认作者支持的 Avatar、Unity、Shader、Provider 和安装限制；
- 本地文件适合确认 `Assets/`、`Packages/`、GUID/fileID、Material、Prefab、Animator 和菜单资源；
- Unity MCP 适合确认 Prefab 实例、inactive 对象、组件私有字段、Provider 状态和编辑器状态；
- 屏幕控制适合确认模型外观、相机、Scene/Game View、弹窗、Gesture Manager 和用户能看到的结果。

没有哪一条通道可以单独证明完整改模成功。

## 2. MCP 连接前检查

先确认 Unity 已打开目标工程，而不是只看 Unity Hub 最近项目。检查：

```text
Unity 进程的 -projectPath
ProjectSettings/ProjectVersion.txt
Packages/manifest.json
Packages/packages-lock.json
当前场景和 Avatar 根
```

每次会话重新读取：

```text
mcpforunity://instances
mcpforunity://editor/state
mcpforunity://project/info
mcpforunity://scene/hierarchy
```

记录：

- 当前实例 ID 及其 project path；
- Unity 版本、active scene 和 Avatar hierarchy path；
- `ready_for_tools`、`is_compiling`、`is_dirty`、Play Mode 和 `blocking_reasons`；
- Console 错误/警告基线；
- 当前是否存在多个 Unity 实例。

不要复用上一次会话的 instance ID。对象名称相同、屏幕画面相似或目标目录相似，都不能替代 `project/info` 身份确认。

## 3. 没有 MCP 时怎么办

如果没有可用 MCP，先说明影响：

- 可以做本地静态扫描、GUID 查找、包版本检查、资源清单和修改方案；
- 不能可靠证明 Prefab 解析后的层级、Provider 生成结果、菜单可达性或 Unity 实际显示；
- 不能把旧截图、缓存或相似工程当成当前工程证据。

如用户允许安装或修复 MCP：

1. 查当前官方安装说明和支持的 Unity 版本；
2. 查看工程已有的 MCP package 和 `manifest.json`，避免重复安装或引入第二个 Bridge；
3. 记录 package source、version、目标工程、备份和回滚方式；
4. 区分“下载/放入 staging”“写入 `Packages/manifest.json`”“UPM 已解析”“脚本已编译”“MCP 已连接”，不能把前一步写成后一步；
5. 安装后等待 UPM 导入和脚本编译；
6. 检查 Unity Console 和 `editor/state`；
7. 重新读取 `instances`、`project/info` 和场景层级；
8. 确认成功前，继续把 Unity-resolved、Preview、Build 和 Runtime 结论标为未验证。

“帮我装 MCP”不等于允许升级所有 VRChat 包。包变更是独立的操作，应先列出版本、依赖和影响。

## 4. MCP 状态异常

出现以下任一情况时，停止 Unity 写入：

- `ready_for_tools=false`；
- `blocking_reasons` 包含 `stale_status`；
- Unity 正在编译、导入或被锁定；
- 当前实例与目标 `project path` 不一致；
- Scene 有未保存改动且动作可能覆盖它；
- Console 有阻断性编译错误。

优先通过 Unity 窗口重新连接、等待编译完成或让用户处理弹窗，然后重新读取状态。不要基于旧截图重复点击，也不要在状态未知时连续重试写操作。

## 5. 查询和写入顺序

```text
instances
  → editor/state
  → project/info
  → active scene / hierarchy
  → target GameObject / components / assets
  → one authorized change
  → editor/state + Console + disk diff
  → screen/scene verification
```

读取 GameObject 时包含 inactive 对象，并记录完整层级路径、active 状态、组件和引用。读取材质时同时记录 Shader、关键纹理和是否为共享 Material。读取 Animator 时记录 Controller、Layer、State、Transition、Clip、Driver 和目标路径。

创建或修改 C#、Prefab、Scene、Material、菜单、参数或 Provider 后，必须等待导入/编译结束，再检查 Console 和目标对象。工具返回成功不等于 Unity 已完成编译或保存。

## 6. 屏幕控制规则

屏幕控制前先获取当前窗口状态和截图；点击、滚动或拖拽后重新观察，不使用旧坐标。适合的任务包括：

- 看模型现在的外观和当前穿着；
- 检查正面、近景、侧面、背面、下半身和 orbit 视角；
- 看 Scene/Game View、Gesture Manager、Provider 面板和弹窗；
- 复现全白、错色、穿插、动作怪、靠近消失等可见问题。

屏幕结果必须注明是 Scene View、Game View、Play Mode、Preview、Gesture Manager 还是客户端。`(Clone)`、`Preview` 和临时生成 Avatar 不能直接当源资产结论。

## 7. 本地静态扫描器

```powershell
python scripts/scan_unity_avatar.py <project-root> --pretty
```

扫描器只读 `ProjectVersion.txt`、Manifest/Lock、场景/Prefab/资源文本、GUID 线索和项目日志；默认不写入工程。它适合建立基线和给 MCP 查询提供关键词，不负责完整 Unity YAML 语义、材质预览、菜单点击、NDMF Build 或 Runtime。

读取 MCP SSE 资源时：

```powershell
python scripts/read_mcp_sse.py `
  --url http://127.0.0.1:8080/mcp `
  --uri mcpforunity://instances `
  --uri mcpforunity://editor/state `
  --uri mcpforunity://project/info `
  --pretty
```

该脚本只发送 `initialize`、`notifications/initialized` 和 `resources/read`，不发送 `tools/call`、保存、构建或上传请求。端口、协议版本和认证方式必须以当前 MCP Server 实际响应为准。

## 8. 多个 Unity Bridge

如果工程同时存在 Unity MCP、UnityAgent 或其他编辑器 Bridge，先指定唯一的 Scene/Prefab owner：

- 只有一个 Bridge 负责导入、写入、保存、编译、预览和构建；
- 其他 Bridge 只做明确的只读查询或独立工具操作；
- 不让两个 Bridge 同时刷新、保存或修改同一个 Scene/Prefab；
- 记录实际 package 版本、端口和本任务允许的操作；
- 不把认证 Token、Cookie 或私有路径写入 Skill、报告或公开仓库。
