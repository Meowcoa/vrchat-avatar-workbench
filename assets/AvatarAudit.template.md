# AvatarAudit.md

这是一个日期化的最小审计索引。它不是“所有功能都正常”的保证；每次相关改动后只刷新受影响的记录。

## Baseline

- 日期：
- 工程 / 场景 / Avatar 根：
- Unity / SDK / 相关包版本：
- 目标平台：
- 证据层：`STATIC_SOURCE` / `UNITY_RESOLVED` / `PROVIDER_PREVIEW` / `NDMF_BUILT` / `SDK_BUILD` / `CLIENT_RUNTIME`
- 当前状态：`CONFIRMED` / `NOT_RUN` / `BLOCKED` / `MCP_REQUIRED`

## Player Menu → Feature Chain

| Menu path | Control | Parameter | Provider/Controller | State/Clip | Target object/BlendShape | Source evidence | Built/runtime evidence | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| | | | | | | | | |

## Parameter reverse map

| Parameter | Type/default/sync | Owner | Menu consumers | Animator/Provider consumers | Conflict/bit cost | Evidence | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| | | | | | | | |

## Provider inventory

| Provider | Source objects/assets | Generated ownership | Shared consumers | Version | Last checked | Unverified items |
| --- | --- | --- | --- | --- | --- | --- |
| | | | | | | |

## Visual asset routes

| Renderer path | Mesh | Material slot/material | Shader/texture/importer | Animation/property driver | Platform | Evidence | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| | | | | | | | |

## Dynamics and performance

- PhysBones/colliders：
- Contacts/senders/receivers：
- Particle systems：
- Constraints/stations：
- PC build evidence：
- Android build evidence：
- Size evidence 是否为源 footprint、预览还是精确 SDK build：

## Change delta

- 本次目标：
- 实际改动文件/对象：
- 备份：
- 修改前证据：
- 修改后证据：
- 未运行或仍阻塞：
- 最小下一步：
