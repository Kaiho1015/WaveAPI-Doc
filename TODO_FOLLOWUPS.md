# Doc 工作 Follow-up 清单

随 cn doc 重写过程中累积的待办,等 doc 全部完成后批量收尾。

---

## A. DB 待跑 SQL(用户操作)

按顺序跑(都是幂等的,单跑也行):

| # | SQL | 影响 | 状态 |
|---|---|---|---|
| 1 | [`fix_capabilities_array_corruption.sql`](../WaveAPI/temp-sql/fix_capabilities_array_corruption.sql) | 修 6 个 chat group capabilities 腐化为 array 的问题 | ⏳ |
| 2 | [`fix_remove_redundant_unified_fields.sql`](../WaveAPI/temp-sql/fix_remove_redundant_unified_fields.sql) | 清 12 个 group 的 size + 6 个 group 的 video_url/audio_url | ⏳ |
| 3 | [`fix_remove_redundant_resolution_aliases.sql`](../WaveAPI/temp-sql/fix_remove_redundant_resolution_aliases.sql) | 清 4 个 kling group 的 mode + grok video 的 quality | ⏳ |
| 4 | [`fix_video_remove_n_seed_common.sql`](../WaveAPI/temp-sql/fix_video_remove_n_seed_common.sql) | 清 34 个 video group 的 supported_common_params 里 n / seed | ⏳ |

跑完后:**DB 里所有 group 的 capabilities 都对齐统一规范** — 没有 vendor 内部细节字段,没有跟 common schema 重名,没有不该有的 n / seed。

---

## B. 后端 provider 映射(WaveAPI Go,新代码)

清完 DB 之后,后端 provider 转发层需要做"统一字段 → vendor 内部字段"的映射,否则用户传统一字段时 vendor 实际收不到对应数据。

### B.1 字段名映射

| 统一字段 | vendor | vendor 内部字段 |
|---|---|---|
| `aspect_ratio` | happyhorse / gemini-image / gpt-image / grok-imagine(image) / imagen | `size` |
| `aspect_ratio` | grok-imagine-1.0-video | `aspect_ratio`(透传同名,但要做 enum 校验) |
| `resolution` | kling-v2.6/v3/v3-omni/video-o1 | `mode`(720p→std / 1080p→pro / 4K→4k) |
| `resolution` | grok-imagine-1.0-video | `quality`(同名透传) |

### B.2 数组→单值映射

我们对外一律 `_urls` 复数(数组),vendor 内部用 `_url` 单值的需要取 `[0]`:

| 统一字段 | vendor | vendor 内部字段 |
|---|---|---|
| `req.VideoURLs[0]` | happyhorse(EDIT 模式) | `video_url` |
| `req.AudioURLs[0]` | wan2.5 / 2.6 / 2.6-i2v(-flash) / 2.7 | `audio_url` |
| `req.ImageURLs[0]` | (待 audit,部分 vendor 可能用单值) | `image_url` |

### B.3 测试

每个映射加 unit test 覆盖:
- 用户传统一字段 → vendor 转发时实际发送的 body 含 vendor 字段名

---

## C. Doc 待补(image / audio 系列)

### C.1 Image 系列(8-10 个 vendor)

| vendor | 涉及 group | 状态 |
|---|---|---|
| seedream | doubao-seedream-3.0 / 4.0 / 4.5 / 5.0-lite | ⏳ |
| gemini-image | 2.5/3/3.1-flash 三组(preview + official 共 6 个) | ⏳ |
| gpt-image | gpt-image-1-official / 1.5-official / 2 | ⏳ |
| flux | flux / flux-2 / flux-kontext | ⏳ |
| grok-imagine | grok-imagine-1.0 / 1.0-edit | ⏳ |
| imagen | imagen-4.0 | ⏳ |
| minimax-image | minimax-image | ⏳ |
| qwen-image | qwen-image / 2.0 / 2.0-pro | ⏳ |
| wan-image | wan2.7-image | ⏳ |
| z-image | z-image-turbo | ⏳ |

### C.2 Audio 系列(2 个 vendor)

| vendor | group | 状态 |
|---|---|---|
| minimax-speech | minimax-speech | ⏳ |
| suno | suno-music | ⏳ |

### C.3 老文件归档

video / image 仓库里有一批不在 docs.json 里的旧 mdx,并发起 agent 写新版后这些就没用了,需要归档到 `_archive/{lang}/...`:

```
cn/api-reference/video/
  - sora2.mdx
  - veo3.mdx
  - wan2-6.mdx
  - kling-v2-6.mdx
  - hailuo-2-3.mdx
  - vidu-q3-pro.mdx
  - doubao-seedance-1-5.mdx
cn/api-reference/image/
  - flux-2.mdx
  - flux-kontext.mdx
  - seedream-4.mdx
  - seedream-4-5.mdx
  - seedream-5-lite.mdx
  - gemini-3-1-flash.mdx
  - nano-banana.mdx
  - nano-banana-pro.mdx
```

(× 4 语言)

### C.4 翻译流水线 → en / jp / zh-Hant

cn 全部确定后启动 LLM 批量翻译:
- 输入:cn 各 vendor mdx
- 输出:en / jp / zh-Hant 镜像目录
- 注意保留 vendor 名字 / model id / cURL 等不翻译的字段
- 翻译完同步更新 docs.json 的 en / jp / zh-Hant 三个 navigation block

---

## D. 数据校正(等用户确认)

### D.1 seedance 2.0 duration

doc 已写 4-15s(用户说是事实),DB 是 [5,...,15] 漏了 4。需要确认是否 SQL 把 4 加进 DB:

```sql
UPDATE model_groups
SET capabilities = jsonb_set(
      capabilities,
      '{durations}',
      '[4,5,6,7,8,9,10,11,12,13,14,15]'::jsonb
    ),
    updated_at = EXTRACT(EPOCH FROM now())::bigint
WHERE group_name IN (
  'doubao-seedance-2.0', 'doubao-seedance-2.0-face',
  'doubao-seedance-2.0-fast', 'doubao-seedance-2.0-fast-face'
);
```

### D.2 happyhorse aspect_ratio 字段

DB 当前 happyhorse-1.0 的 specific_parameters.size 已经被 fix_remove_redundant_unified_fields.sql 删了,但 capabilities.aspect_ratios 还在(用作可选值),这个**保留**(因为 doc 通用参数节展示这个 enum)。

---

## E. 其他遗留

### E.1 veo "official/逆向" 命名

用户决定保留 — `veo3.1-fast-official` / `veo3.1-quality-official` 是官方档,`veo3.1-lite` / `veo3.1-quality` 是逆向档。doc 已分两组讲。

### E.2 sora-2-preview disabled

sora 当前 doc 已从 docs.json 移除。如果 OpenAI 后续放开使用,直接 `enable=true` 然后把 `cn/api-reference/video/sora` 加回 docs.json 即可(mdx 文件保留着)。

### E.3 wan 系列大面积 disabled

wan 7 个 model 中只 `wan2.7-videoedit` 启用。doc 已重写到 200 行只讲 videoedit。其他 6 个待 vendor 上线后:
1. 启用 model(`enable=true`)
2. 补回 doc(基于现在归档的旧版 wan.mdx 重写,或并发 agent)
3. 加回 Tab + 调用示例

---

## 优先级建议

**P0(立刻可做):** A.1 SQL 4 个跑完
**P1(本周内):** C.1/C.2 image/audio 系列 cn doc 并发起 agent
**P2(doc 完后):** C.3 老文件归档 + C.4 翻译流水线
**P3(独立工作):** B 后端 provider 映射(关键,否则 vendor 收不到正确字段 — 但不阻塞 doc 上线)
**P4(数据微调):** D 数据校正
