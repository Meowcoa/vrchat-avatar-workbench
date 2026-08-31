# 实战改模经验

本文件把多次 VRChat Avatar 改模、排错和工具协作中的经验抽象成公开可复用的规则。项目名称、路径、版本和对象名都必须以当前工程重新读取的结果为准。

## 1. 最有效的实际顺序

成功率最高的顺序不是“先导入所有插件和素材”，而是：

```text
确定用户想要的外观
  → 看懂当前 Avatar
  → 锁定真实工程和 Avatar 根
  → 查作者/官方资料和依赖
  → 恢复 Unity MCP 与编辑器状态
  → 记录原始材质、菜单和动作基线
  → 先接一个最小改模单元
  → 立即编译、回读和截图
  → 再接下一件衣服或功能
```

这能避免把“路径找错、MCP 连错、材质找错、菜单没接、Clone 画面污染”混成一个无法定位的大问题。

## 2. 以成功的服装/发型/眼睛改模为模板

一次完整的 Avatar 改造通常会同时涉及衣服、头发、眼睛、内衣、AFK/动作和菜单。可复用的做法是：

1. 先对原 Avatar 做只读观察，记录默认外观、已穿部件、菜单入口、参数和当前动作；
2. 明确只修改目标 Avatar 实例或目标 Scene，原项目和原始资源保持可回退；
3. 用 `manage_asset`、本地 `rg` 或 GUID 搜索找真实资源，而不是只相信用户输入的文件夹名；
4. 对每套服装/发型分别检查骨骼根、缩放、材质槽、贴图、BlendShape、Bounds 和开关链；
5. 对眼睛颜色先定位完整 Material/Texture/Animator 关系，再制作隔离副本；
6. 把菜单、参数和 FX/Provider 接线作为独立工作项，不把“资源出现”当成“功能已完成”；
7. 每接入一项就看模型正面、近景、侧面、背面和下半身，确认没有漂浮、穿插、发白、消失或错色；
8. 最后再做构建层和设备/客户端层验证。

最关键的经验是：复制贴图本身通常不够。要同时复核 Renderer 的材质槽、共享 Material、Shader 属性、动画曲线、菜单参数和目标对象路径。

## 3. MCP 失效时的正确处理

实际改模中会遇到 Unity MCP 连接过期、实例列表为空或 `stale_status`。正确做法是：

- 重新读取 `mcpforunity://instances`、`editor/state` 和 `project/info`；
- 通过 Unity 窗口重新连接或等待状态恢复；
- 再确认 `-projectPath`、Unity 版本、当前 Scene 和 Avatar 根；
- 只在目标实例明确对应后继续查询或写入。

不要复用旧 instance ID，也不要因为屏幕上仍然看得到模型就认为 MCP 可以安全写入。MCP 没恢复时仍可做静态文件核查和方案设计，但要把 Unity 解析、菜单生成和运行效果标为未验证。

## 4. 屏幕控制为什么有用、又为什么不够

屏幕控制特别适合让不会改模的用户看到：

- 当前到底打开了哪个 Unity 工程；
- Avatar 是源对象还是 `(Clone)`；
- 衣服、头发、眼睛和鞋子是否真的在正确位置；
- 近距离是否消失、材质是否发白、动作是否奇怪；
- MCP/Unity/Provider 弹窗和 Console 状态。

但屏幕只证明某个视图在某一时刻的现象。看见模型不等于 Prefab 已保存，看见菜单条目不等于参数链有效，看见 Preview 不等于 SDK Build，更不等于上传后客户端正常。

## 5. 视觉问题的高收益排错顺序

### 全白或发白

先检查材质槽、Shader 和贴图是否真实存在，再检查当前对象是否是 Clone/生成物，之后排查灯光、曝光、相机距离、Shader 属性、动画曲线和 PropertyBlock，最后才处理平台材质差异。

浅色贴图配合灯光可能只是视觉上偏白，不代表贴图丢失。不要因为白就立即换材质。

### 紫色或材质错误

优先查 Shader 包、材质依赖、Texture/Resource/MaterialPack、导入设置和失效 GUID。完整材质组缺一项时，单独替换一张纹理可能制造新的错色。

### 靠近消失

分开检查 Scene View、Game View 和真实 Avatar 渲染：Camera near/far clip、模型尺度、root transform、Renderer bounds/AABB、AntiCulling、渲染层、测试相机是否进入模型、Prefab/生成对象是否被近距离禁用，以及是否存在重复 Clone。

### 动作奇怪

不要只看姿势猜原因。分别读取 `Action`、`Locomotion`、左右 `Gesture`、`FX`、AFK、Write Defaults、Transition、BlendTree、Parameter Driver 和当前 Controller。`Standing`、`Idle`、`WaitForActionOrAFK` 不能直接解释成特殊动作。

## 6. 菜单功能必须做双向追踪

正向追踪：

```text
菜单控件
  → 参数与值
  → Provider/Controller/Driver
  → State/Clip/Object/BlendShape
  → 实际 Renderer 或 GameObject
```

反向追踪：

```text
参数或对象
  → 谁拥有它
  → 哪些菜单使用它
  → 哪些 Animator/Provider 修改它
  → 是否与其他服装或功能冲突
```

这能发现“菜单有条目但没有控制对象”“参数同名但类型不同”“衣服默认自动打开”“删除对象后动画仍引用旧路径”等问题。

## 7. 删除、覆盖和共享资源

“删掉”不是单一动作。优先使用隐藏/禁用验证外观，再决定是否从实例移除、移除注入链或删除文件。删除共享 Mesh/Material/Texture 之前，必须搜索所有引用和其他 Avatar 消费者。

原始 FBX、Prefab、作者材质和下载包不要拿来直接试错。为颜色、法线、Shader、眼睛或面捕做测试时，复制到明确的 `Test`/版本目录并记录来源。

## 8. 什么时候说明“成功”

至少要能说清楚：

- 目标工程、Scene、Avatar 根和修改对象已锁定；
- 目标资源、材质、骨骼、菜单和参数链实际对应；
- Unity 导入/编译结果已检查；
- 屏幕或截图验证了目标视角下的外观；
- 原对象、共享资源和其他 Avatar 没被误改；
- 哪些内容只在源文件或 Preview 层确认；
- NDMF/SDK Build、PC/Android、设备或客户端是否仍未验证。

一次实际改模可以做到“模型可见、关键衣物/头发/眼睛已回读、Console 无错误、原项目未改”，但如果没有 NDMF/SDK Build 或客户端菜单测试，就只能报告为部分完成，不能写成所有功能 PASS。
