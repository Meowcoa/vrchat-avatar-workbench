# Blender/CATS/Tuxedo 网格交接规范

Unity 适合 Avatar 组装和组件配置；当任务改变网格本身时，使用本交接规范把工作交给 Blender/CATS/Tuxedo，再把结果带回 Unity 验证。

## 1. 触发条件

需要 handoff 的任务包括：

- 顶点、面、拓扑、重拓扑、穿插修整；
- 服装贴合、权重绘制、骨骼重绑定或 retarget；
- UV、材质槽顺序、Shape Key/BlendShape、镜像、合并或拆分 Mesh；
- 需要观察网格结构，而不是仅改变对象开关、材质属性或菜单。

只涉及父子关系、菜单、参数、Animator、PhysBones、Contacts、Material 属性和 MA/NDMF 组装时，优先留在 Unity。

## 2. 交接前记录

使用工程根相对路径，必要时以 `<project-root>` 表示根：

```yaml
handoff_version: 1
date: YYYY-MM-DD
source_asset: Assets/...
source_prefab: Assets/...
source_scene: Assets/...
renderer_path: Avatar/Armature/.../Renderer
mesh_name: ...
skeleton_root: Avatar/Armature
target_avatar: ...
target_platform: PC|Android|both
source_evidence: STATIC_SOURCE|UNITY_RESOLVED
authorization: inspect|stage-edit|export
backup: <relative backup path or external documented path>
```

再补充：

- Renderer 的完整路径、active 状态、Mesh、rootBone、bones 数量和骨骼相对路径；
- 局部 position/rotation/scale、单位、朝向和 Avatar 参考比例；
- 顶点、三角形、材质槽、UV channel、BlendShape 名称和权重范围；
- Material、Shader、主贴图、法线、透明/剔除和平台差异；
- PhysBones、Collider、Contacts、Constraint、Station、Anchor、Bone Proxy 依赖；
- 不允许改变的骨骼名、对象名、材质槽顺序、Shape Key 名称和目标路径；
- 期望输出文件名、Unity 导入目录、是否要保留 FBX 结构和需要的 MA 组件。

## 3. Blender 操作约束

1. 不覆盖原始 FBX、Blend、Prefab、材质或下载包；输出到隔离的 `staged/` 或版本目录。
2. 记录是否应用了 rotation/scale、改变 origin、重命名骨骼/材质/Shape Key、合并或删除了 Mesh。
3. 保持骨骼路径、必要对象名、BlendShape 名称、材质槽顺序和导出轴向；确需改变时给出旧→新映射。
4. CATS/Tuxedo 自动权重、自动 retarget 和自动穿衣结果只能作为候选，不是已验证结果。
5. 导出前检查非均匀缩放、负缩放、法线、面朝向、重复顶点、无效材质槽和隐藏对象。
6. 不在 Blender 阶段把 Unity 动态组件、MA/VRCFury 生成物或构建缓存当作可编辑源。

## 4. 回 Unity 验证矩阵

| 项目 | 需要的验证 | 最低证据层 |
| --- | --- | --- |
| FBX/模型导入 | 路径、Importer、缩放、轴向、Mesh 可读 | `UNITY_RESOLVED` |
| Renderer | Mesh、rootBone、bones、materials、active | `UNITY_RESOLVED` |
| BlendShape | 名称、权重、表情/面捕绑定仍可找到 | `UNITY_RESOLVED` / `PROVIDER_PREVIEW` |
| 材质 | Shader、贴图、法线、透明/剔除、PC/Android | `UNITY_RESOLVED` |
| Bounds | root/renderer bounds、相机可见性、远近裁剪 | `UNITY_RESOLVED` / `CLIENT_RUNTIME` |
| 动态组件 | PhysBones、Collider、Contacts、Constraint 路径 | `UNITY_RESOLVED` / `NDMF_BUILT` |
| 菜单/参数 | 新旧菜单、参数冲突、Animator/Provider 注入 | `NDMF_BUILT` |
| 平台性能 | 精确目标构建的等级、包体和视觉回归 | `SDK_BUILD` |

任一骨骼路径、材质槽或 Shape Key 不匹配时，回到 handoff 修正；不要用不可追踪的 Unity 文本补丁掩盖映射错误。

## 5. 可复制的交接报告

```text
目标：<project-root> / <scene> / <avatar root>
来源：<source asset/prefab>，修改对象：<renderer path>
保留不变：<bone paths / blendshapes / slots>
实际修改：<topology / weights / UV / shape keys>
工具版本：Blender <version>，CATS/Tuxedo <version if used>
导出：<staged output path>
备份：<backup path/hash>
回 Unity 检查：<what was read back>
已确认：<evidence layer>
未验证：<build/runtime/platform gaps>
```
