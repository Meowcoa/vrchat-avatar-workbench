# VRChat Avatar 改模工作流

这是给不会改模用户使用的详细操作顺序。它针对“把资源接到当前 Avatar 并让它看起来、菜单和动作都正确”，不把复制文件当成完成。

## 1. 任务拆解

先把用户的一句话拆成可验收的小项：

| 用户说法 | 需要确认的实际对象 |
| --- | --- |
| 换衣服 | 衣服 Mesh/Prefab、骨骼、材质、开关、菜单和互斥关系 |
| 换头发 | Hair Mesh、骨骼/父节点、材质、发型切换参数和动态组件 |
| 换眼睛颜色 | Eye Renderer、材质槽、贴图/Shader、动画和菜单参数 |
| 加配件 | Prefab、挂点、Bone Proxy/Parent Constraint、材质、菜单和性能 |
| 修动作 | Action/Locomotion/Gesture/FX/AFK、Controller、State、Clip、参数 |
| 修全白/紫色 | Shader、材质、贴图、灯光、生成层、PropertyBlock 和平台设置 |
| 靠近消失 | 相机裁剪、尺度、Bounds、AntiCulling、渲染层、Clone 和禁用逻辑 |
| 加菜单开关 | Menu → Parameter → Provider/Animator → Object/BlendShape 的完整链 |

## 2. 改模前基线

记录：

- project path、Unity 版本、当前 Scene、Avatar 根和 Descriptor；
- 当前服装、发型、眼睛、内衣、鞋子、配件和默认菜单；
- Renderer、Mesh、rootBone、bones、材质槽、Shader、贴图、BlendShape 和 Bounds；
- 目标平台、当前包版本、Provider、Animator 和面捕/OSC 状态；
- Scene dirty、Console、Play Mode、MCP 状态和已有备份。

屏幕上至少截取正面和近景，必要时增加侧面、背面、下半身、鞋子和 orbit 视角。这样改完才能比较“哪里变了”。

## 3. 服装/发型/配件接入

### 资源检查

先阅读作者说明和依赖，再定位实际文件。不要依据相似文件名猜功能。确认资源是：

- 目标 Avatar 专用 Prefab；
- 通用服装或发型，需要手动挂骨骼；
- FBX 内的 Mesh；
- 带 MA、VRCFury、DressingTools、lilycalInventory 或其他 Provider 的模块。

### 组装检查

按以下顺序：

1. 导入 Material/Texture/Resource/MaterialPack 等依赖；
2. 导入服装/发型到隔离目录；
3. 检查 skeleton root、骨骼路径、Transform、scale 和 Avatar 比例；
4. 检查 Renderer、Mesh、rootBone、bones、material slots、BlendShape 和 Bounds；
5. 选择当前工程已经使用的 Provider 或最小的 Unity 组装方法；
6. 建立对象开关、互斥关系、参数、Animator 和菜单；
7. 检查静止、走动、手势、坐下、AFK 和必要的动态行为。

### 自动工具的边界

快速穿衣、自动权重和自动 retarget 只生成候选结果。出现浮空、穿插、跟骨骼错位、手臂/腿部断开、动作时衣服飞走或材质错槽时，要记录具体对象和骨骼，不能只再次点击安装器。

## 4. 材质和外观

### 复制材质，而不是盲改共享资源

如果用户要保持原来的颜色或眼睛效果：

1. 找到原 Renderer 的真实材质槽；
2. 读取 Material、Shader、MainTex、法线、Mask、Emission 和颜色属性；
3. 查是否有 Animator、Menu、FaceEmo、面捕或 PropertyBlock 改写属性；
4. 对需要实验的材质复制出测试版本；
5. 替换目标实例后用屏幕和 MCP 回读；
6. 确认没有把共享材质改成影响其他 Avatar 的结果。

### 全白/发白

依次排查：

1. 材质槽、Shader 是否有效；
2. MainTex/Mask/法线是否存在且导入正确；
3. 当前对象是否是 Preview、生成物或 `(Clone)`；
4. Directional Light、曝光、Ambient/Reflection、相机距离；
5. Shader 亮度、Emission、动画曲线和 PropertyBlock；
6. PC/Android Shader 和纹理设置。

浅色材质配合灯光可能只是视觉上偏白，不能直接判断为贴图丢失。

### 紫色/错色

优先检查 Shader 包、Material/Texture/Resource 依赖、Missing GUID、材质槽顺序、平台 Shader 和作者要求的导入设置。不要用另一套 Shader 直接覆盖来“试试看”。

## 5. 菜单、参数和 Animator

### 正向链

```text
Expression Menu
  → Control type/value
  → Expression Parameter
  → Provider/Controller/Driver
  → Animator Layer/State/Transition/Clip
  → GameObject/Renderer/BlendShape
```

### 反向链

```text
GameObject/Renderer/BlendShape
  → 哪个 Clip 或 Driver 改它
  → 哪个 Controller/Provider 拥有它
  → 哪个 Parameter 控制它
  → 哪些菜单和其他功能共用它
```

新增参数要检查 type、default、sync、bit cost、同名冲突和所有消费者。菜单/参数数量只能做结构快照，不等于控件全部可用。

动作异常分别检查：

- `Action` 和 Emote；
- `Locomotion`；
- 左右 `Gesture`；
- `FX`；
- AFK；
- Write Defaults、Transition、BlendTree 和 Parameter Driver；
- Gesture Manager/Preview 是否生成重复 Clone 或使用了错误 Controller。

## 6. PhysBones、Contacts 和其他组件

记录完整路径和依赖：

- PhysBone root、链、limits、radius、parameter、collider；
- Collider 类型、尺寸、根路径和消费者；
- Contact Sender/Receiver、tag、parameter、allow self/others；
- ParticleSystem 最大粒子数、Simulation Space、Renderer 材质和触发器；
- Constraint、Station、Anchor、Bone Proxy 和 Parent Constraint。

静态字段只能证明设置存在。碰撞、摆动、触发效果和多人行为需要 Preview、Build 或 Runtime 测试。

## 7. Blender 交接

当问题是拓扑、权重、UV、Shape Key、骨骼重绑定、服装贴合或穿插修整时，生成 Blender/CATS/Tuxedo handoff；Unity 负责组装和功能接线。

交接中记录源 Mesh、Renderer 路径、骨骼路径、材质槽、BlendShape、单位、轴向、输出文件和备份。回 Unity 后重新检查模型导入、bones、材质槽、BlendShape、Bounds、Prefab override、动态组件和菜单。

## 8. 验收顺序

每完成一个改模单元都做：

1. Unity 导入和编译检查；
2. MCP 回读目标对象、材质、参数、Animator 和 Provider；
3. 屏幕/相机正面、近景、侧面、背面和下半身检查；
4. 需要时做动作、菜单、动态组件和面捕输入测试；
5. 检查源对象、共享资源和其他 Avatar 是否未被误改；
6. 记录未验证的构建、平台、设备和客户端范围。

只有目标层验证真的通过，才能报告“完成”。
