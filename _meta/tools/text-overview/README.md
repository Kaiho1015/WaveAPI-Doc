# 文本模型总览生成器

`cn|en/api-reference/text/overview.mdx` 由本目录生成，**不要直接编辑生成结果**。

## 文件

| 文件 | 作用 |
|---|---|
| `data.py` | 90 个文本模型的单价、缓存档位、长上下文分档、能力位与备注 |
| `gen.py` | 渲染厂商表格与「模型备注」，并注入模板 |
| `overview_cn.tpl` / `overview_en.tpl` | 表格以外的全部正文，`{{CATALOG}}` 为插入点 |

## 生成

```bash
cd _meta/tools/text-overview
python3 gen.py cn > ../../../cn/api-reference/text/overview.mdx
python3 gen.py en > ../../../en/api-reference/text/overview.mdx
```

## data.py 字段

`m(id, vendor, input, output, ...)`

| 参数 | 含义 |
|---|---|
| `cr` / `cw` / `cw5` / `cw1` | 缓存读价 / 缓存写价 / 5 分钟写 / 1 小时写；决定「计费方式」列 |
| `tier=dict(T272, inp=, out=, ...)` | 长上下文分档阈值与高档价 |
| `sched=True` | 时段价，单价见 `price_config.text_schedule` |
| `ver` | 能力位：`T` 文本 · `S` 流式 · `J` JSON Schema · `F` 函数调用 · `C` 自动缓存 · `N` Gemini 原生 |
| `proto="responses"` | 仅 `/v1/responses` |
| `limits=(输入上限, 输出上限)` | 写进「模型备注」 |
| `notes` / `notes_en` | 该模型独有的限制；通用规则写在模板里，不要在这里重复 |

`ver` 里带 `C` 的模型会自动生成「支持自动缓存命中」，带 `N` 的自动生成「支持 Gemini 原生接口」，`notes` 里不需要再写一遍。

## 改动后

模型组变更时先改 `data.py`，通用口径变更改模板，厂商段落改 `gen.py` 的 `VENDOR_NOTES`，然后两种语言都重新生成。写作口径见 `_meta/模型上架文档-SOP.md` §7。
