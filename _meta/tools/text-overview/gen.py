# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from data import MODELS, VENDORS, V, VE

def fmt(x):
    if x is None: return "—"
    s = f"{x:.5f}".rstrip("0").rstrip(".")
    return s

def price_cell(p, tier, key):
    base = p.get(key)
    if base is None: return "—"
    s = fmt(base)
    if tier and tier.get(key) is not None:
        s += " / " + fmt(tier[key])
    return s

_LOWER_FIRST = ("Tools","Cache","Official","Implicit","Use","Time-of-day","Accepted","Native","Structured","Reasoning","Limits","No ","Whole","Two-rate","Separate","Xiaomi","StepFun","JSON","GPT-6","`max_tokens`")
def _en_clause(s):
    for w in _LOWER_FIRST:
        if s.startswith(w) and w not in ("Xiaomi","StepFun","JSON","GPT-6","`max_tokens`"):
            return s[0].lower()+s[1:]
    return s

def caps(ver):
    codes=[]; i=0
    while i < len(ver):
        if ver[i]=="r": codes.append(ver[i:i+2]); i+=2
        else: codes.append(ver[i]); i+=1
    return set(codes)

def ver_extra(mo, lang):
    c = caps(mo["ver"]); out=[]
    said = " ".join(mo["notes"] if lang=="cn" else mo["notes_en"])
    if "C" in c and "缓存命中" not in said and "cache hit" not in said.lower():
        out.append("支持自动缓存命中" if lang=="cn" else "supports automatic cache hits")
    if "N" in c and "原生" not in said and "native" not in said.lower():
        out.append("支持 Gemini 原生接口" if lang=="cn" else "the Gemini native endpoint is available")
    return out

def tier_cell(mo, lang):
    t = mo["tier"]
    if not t: return "—"
    return t["th"]

def model_notes(mo, lang):
    p, t = mo["price"], mo["tier"]
    out = []
    if t:
        out.append(f"{t['th']} 长上下文分档" if lang=="cn" else f"{t['th']} long-context tier")
    if mo["proto"] == "responses":
        out.append("仅 `/v1/responses`" if lang=="cn" else "`/v1/responses` only")
    if p.get("cw") is not None:
        out.append("有独立缓存写入价" if lang=="cn" else "has a separate cache-write rate")
    if p.get("cw5") is not None:
        out.append("缓存写入分 5 分钟 / 1 小时两档" if lang=="cn"
                   else "cache writes are priced at two TTLs, 5-minute and 1-hour")
    if mo["limits"]:
        i,o = mo["limits"]
        out.append(f"最大输入 {i}、最大输出 {o}" if lang=="cn" else f"max input {i}, max output {o}")
    out += ver_extra(mo, lang)
    out += mo["notes"] if lang=="cn" else [_en_clause(x) for x in mo["notes_en"]]
    if not out: return None
    sep = "；" if lang=="cn" else "; "
    return f"- `{mo['id']}` — " + sep.join(out)

HDR = {
 "cn": "| 模型 ID | 计费方式 | JSON / 工具 |\n|---|---|:---:|",
 "en": "| Model ID | Billing | JSON / Tools |\n|---|---|:---:|",
}

def billing_cell(mo, lang):
    """计费方式只写维度，不写单价——单价随上游调整，以目录接口为准。"""
    if mo["sched"]:
        return "时段价" if lang=="cn" else "time-of-day"
    p = mo["price"]
    if p.get("cw1") is not None:
        return "含缓存三档" if lang=="cn" else "+ 3 cache rates"
    if p.get("cw") is not None:
        return "含缓存读写" if lang=="cn" else "+ cache read/write"
    if p.get("cr") is not None:
        return "含缓存读" if lang=="cn" else "+ cache read"
    return "输入输出两项" if lang=="cn" else "input + output"

def vendor_table(vkey, lang):
    rows = [HDR[lang]]
    for mo in MODELS:
        if mo["vendor"] != vkey: continue
        c = caps(mo["ver"])
        j = "✓" if "J" in c else "—"
        f_ = "✓" if "F" in c else "—"
        rows.append(f"| `{mo['id']}` | {billing_cell(mo,lang)} | {j} / {f_} |")
    notes = [n for n in (model_notes(mo,lang) for mo in MODELS if mo["vendor"]==vkey) if n]
    tbl = "\n".join(rows)
    if notes:
        head = "**模型备注**\n\n" if lang=="cn" else "**Model notes**\n\n"
        tbl += "\n\n" + head + "\n".join(notes)
    return tbl

VENDOR_NOTES = {
"openai": {
"cn": """GPT-5 及之后的模型用 `max_completion_tokens` 限制输出、用 `reasoning_effort` 选推理档位（GPT-6 Astra 只支持 `"low"`）。`max_tokens` 会被拒绝。`gpt-5-pro` / `gpt-5.2-pro` / `gpt-5.4-pro` / `gpt-5.3-codex` / `o3-pro` 只能走 [Responses 接口](/cn/api-reference/text/openai-multimodal)，发到 Chat 会返回 400。272K 分档以**输入总量**判断：恰好 272,000 用普通档，超过则整单（含缓存与输出）切到长上下文档。GPT-5.6 的缓存写入价是本档输入价的 1.25 倍，替代普通输入计费而不是叠加；GPT-5.4 / 5.5 没有独立缓存写入价。""",
"en": """GPT-5 and later use `max_completion_tokens` to cap output and `reasoning_effort` to pick a reasoning tier (GPT-6 Astra supports `"low"` only). `max_tokens` is rejected. `gpt-5-pro`, `gpt-5.2-pro`, `gpt-5.4-pro`, `gpt-5.3-codex` and `o3-pro` are served only on the [Responses API](/en/api-reference/text/openai-multimodal) and return 400 on Chat. The 272K tier is judged on **total input**: exactly 272,000 stays on the base rate, anything above moves the whole request (cache and output included) to the long-context rate. GPT-5.6 cache writes cost 1.25× the tier's input rate and replace the ordinary input charge rather than adding to it; GPT-5.4 / 5.5 have no separate cache-write rate.""",
},
"anthropic": {
"cn": """Chat 接口用 `max_tokens` 限制输出；GPT 专用的 `reasoning_effort` 与 `max_completion_tokens` 不适用于 Claude 模型。除 `claude-opus-4-5` 外的 Claude 模型都是三段缓存价（读 / 5 分钟写 / 1 小时写），放行显式 `cache_control`，写法见[缓存](#缓存)；Claude 5、Claude 5.5 与 Fable 六个模型**不支持结构化输出**，`response_format` 的 `json_schema` 与 `json_object` 会返回 400。Fable 系列、`claude-opus-5-5` 与 `claude-sonnet-5-5` 的 `tool_choice` 只接受 `"auto"`，`"required"` 或指定函数名会返回 400。`claude-opus-4-5` 只有输入 / 输出两项计价，会忽略 `cache_control`，输入全部按输入价计费。已有 Anthropic SDK 的应用可走原生 [Messages 接口](/cn/api-reference/text/claude-messages)，全部 Claude 模型都可调用。""",
"en": """Use `max_tokens` on the Chat endpoint to cap output; the GPT-only `reasoning_effort` and `max_completion_tokens` do not apply to Claude models. Every Claude model except `claude-opus-4-5` carries three cache rates (read / 5-minute write / 1-hour write) and allows explicit `cache_control` — see [Caching](#caching) for the request shape. The six Claude 5 / Claude 5.5 / Fable models do **not support structured output**: `response_format` with `json_schema` or `json_object` returns 400. On the Fable models, `claude-opus-5-5` and `claude-sonnet-5-5`, `tool_choice` accepts only `"auto"`; `"required"` or a named function returns 400. `claude-opus-4-5` bills input and output only; it ignores `cache_control` and bills all input at the input rate. Apps built on the Anthropic SDK can use the native [Messages endpoint](/en/api-reference/text/claude-messages) with every Claude model.""",
},
"google": {
"cn": """OpenAI 兼容接口之外，下列模型还可以走 Gemini 原生接口：`gemini-2.5-flash-lite` `gemini-2.5-pro` `gemini-3-flash-preview` `gemini-3.1-pro-preview` `gemini-3.5-flash` `gemini-3.6-flash` `gemini-3.7-flash` `gemini-3.8-flash`（`gemini-3.5-flash-lite` 不支持 Gemini 原生接口）。原生入口是 `POST /v1beta/models/{model}:generateContent`（流式 `:streamGenerateContent?alt=sse`），见 [Gemini 原生接口](/cn/api-reference/text/gemini-native)。原生响应用 `usageMetadata` 报告用量、不带 `usage.cost`；`candidatesTokenCount` 与 `thoughtsTokenCount` 分开报告，计费输出是两者之和。Pro 模型（`gemini-2.5-pro` / `gemini-3.1-pro-preview`）有 200K 长上下文分档，超过 200,000 输入总量后整单切换。3.6 / 3.7 / 3.8 Flash 有隐式缓存读价，是否命中由上游决定；其余模型两项计价。Gemini 全系只支持自动缓存：`cache_control` 不生效，原生接口的 `cachedContent` 会返回 400；内置工具、`web_search_options` 以及 `standard` / `default` 以外的 `service_tier` 同样返回 400。""",
"en": """Besides the OpenAI-compatible endpoint, these models can also be called on the Gemini native endpoint: `gemini-2.5-flash-lite`, `gemini-2.5-pro`, `gemini-3-flash-preview`, `gemini-3.1-pro-preview`, `gemini-3.5-flash`, `gemini-3.6-flash`, `gemini-3.7-flash`, `gemini-3.8-flash` (`gemini-3.5-flash-lite` is not available on the native endpoint). The native entry is `POST /v1beta/models/{model}:generateContent` (streaming: `:streamGenerateContent?alt=sse`), see [Gemini native API](/en/api-reference/text/gemini-native). Native responses report usage in `usageMetadata` without `usage.cost`; `candidatesTokenCount` and `thoughtsTokenCount` are reported separately and billed output is their sum. The Pro models (`gemini-2.5-pro` / `gemini-3.1-pro-preview`) have a 200K long-context tier that switches the whole request above 200,000 total input. 3.6 / 3.7 / 3.8 Flash have an implicit cache-read rate whose hits are decided upstream; the other models bill two rates. The whole Gemini line supports automatic caching only: `cache_control` has no effect, and `cachedContent` on the native endpoint returns 400, as do built-in tools, `web_search_options` and any `service_tier` other than `standard` / `default`.""",
},
"deepseek": {
"cn": """V4 系列（Pro / Flash / 4.1 Flash）按**请求开始时刻的 UTC 时段**计价（北京时间加 8 小时）。价格在请求开始时确定，响应费用与最终结算都用这一份，即使响应跨过时段边界也不重新选价。传 `thinking: {"type": "disabled"}` 可关闭思考。V4 缓存命中价替代对应输入，不提供独立缓存写入。V3.x / R1 两项计价；`deepseek-v3.2-exp` 与 `deepseek-v3.1-terminus` 不提供严格 JSON Schema，需要 schema 约束时用 `deepseek-v3.2` 或 `deepseek-r1-0528`。

| 时段（UTC，含开始不含结束） | 档位 |
|---|---|
| 每天 00:00–14:00 | 高价档 |
| 每天 14:00–24:00 | 低价档（最便宜） |

北京时间加 8 小时。各模型每个时段的输入 / 输出 / 缓存读单价，见模型详情
`GET /v1/models` 的 `price_config.text_schedule`——该字段是完整的时段价表，也是结算依据。""",
"en": """The V4 line (Pro / Flash / 4.1 Flash) is priced by the **UTC time slot at request start** (Beijing time = UTC+8). The rate is fixed when the request begins and is used for both the response cost and the final settlement, even if the response crosses a slot boundary. Pass `thinking: {"type": "disabled"}` to turn thinking off. V4 cache-hit rates replace the matching input charge; there is no separate cache write. V3.x / R1 bill two rates; `deepseek-v3.2-exp` and `deepseek-v3.1-terminus` offer no strict JSON Schema — use `deepseek-v3.2` or `deepseek-r1-0528` when you need schema guarantees.

| Slot (UTC, start inclusive, end exclusive) | Tier |
|---|---|
| Daily 00:00–14:00 | peak |
| Daily 14:00–24:00 | off-peak (cheapest) |

Beijing time is UTC+8. The per-slot input / output / cache-read rates for each model are in
`price_config.text_schedule` on `GET /v1/models` — that is the complete table and the basis for settlement.""",
},
"qwen": {
"cn": """自动缓存是否命中由上游决定；用 `cache_control` 标出前缀时，写入按缓存写入价、命中按缓存读价计。Plus / Flash 有 256K 分档（`qwen3.7-flash` 为 32K），按输入总量整单切换。思考 token 占用输出预算，且无法关闭。""",
"en": """Whether an automatic cache hit occurs is decided upstream; when a prefix is marked with `cache_control`, writes are billed at the cache-write rate and hits at the cache-read rate. Plus / Flash have a 256K tier (32K for `qwen3.7-flash`) switched on total input for the whole request. Reasoning tokens come out of the output budget and cannot be turned off.""",
},
"moonshot": {
"cn": """Kimi K3 支持自动缓存；`tool_choice` 用 `"auto"`，函数调用需要足够的输出预算，建议 512 以上。K2.x 只有输入 / 输出两项计价。""",
"en": """Kimi K3 supports automatic caching. Use `tool_choice: "auto"`, and give function calls enough output budget — 512 or more. K2.x bill input and output only.""",
},
"xai": {
"cn": """Grok 全系 200K 分档：输入总量（含缓存）达到 200,000 时，输入、缓存读和输出整单切到高档，不是只对超出部分加价。Grok 4.6 支持自动缓存。全系**不支持工具调用**，传 `tools` 会返回 400。`max_tokens` 对思考模型不是硬上限——`completion_tokens` 含思考 token，可能超过设定值，可用 Key 额度控制预算上限。""",
"en": """The whole Grok line has a 200K tier: once total input (cache included) reaches 200,000, input, cache read and output for the entire request move to the higher rate — not just the excess. Grok 4.6 supports automatic caching. The whole line does **not support tool calling** — sending `tools` returns 400. `max_tokens` is not a hard cap on reasoning models: `completion_tokens` includes reasoning tokens and can exceed it, so budget with key quotas.""",
},
"zai": {"cn": """计费方式为「输入输出两项」的模型会忽略 `cache_control`，输入全部按输入价计费。""", "en": """Models billed as input + output ignore `cache_control` and bill all input at the input rate."""},
"minimax": {"cn": """只有输入 / 输出两项计价，`cache_control` 会被忽略，输入全部按输入价计费。""", "en": """Input and output are the only two rates; `cache_control` is ignored and all input is billed at the input rate."""},
"other": {"cn": """只有输入 / 输出两项计价，`cache_control` 会被忽略，输入全部按输入价计费。""", "en": """Input and output are the only two rates; `cache_control` is ignored and all input is billed at the input rate."""},
}

def web_search_table(lang):
    """联网搜索可用模型：配了搜索单价且支持工具调用。Messages 只有 Claude 模型可用。"""
    usable = [mo for mo in MODELS if mo["ws"] is not None and "F" in caps(mo["ver"])]
    ids = lambda ms: " ".join(f"`{mo['id']}`" for mo in ms)
    claude = [mo for mo in usable if mo["vendor"] == "anthropic"]
    if lang == "cn":
        rows = ["| 入口 | 工具类型 | 模型 |", "|---|---|---|",
                f"| `POST /v1/responses` | `web_search`、`web_search_preview` | {ids(usable)} |",
                f"| `POST /v1/messages` | `web_search_20250305` | {ids(claude)} |"]
    else:
        rows = ["| Entry | Tool type | Models |", "|---|---|---|",
                f"| `POST /v1/responses` | `web_search`, `web_search_preview` | {ids(usable)} |",
                f"| `POST /v1/messages` | `web_search_20250305` | {ids(claude)} |"]
    return "\n".join(rows)

def catalog(lang):
    parts = []
    for vkey, cn_name, en_name in VENDORS:
        parts.append(f"### {cn_name if lang=='cn' else en_name}\n\n{vendor_table(vkey, lang)}\n\n{VENDOR_NOTES[vkey][lang]}\n")
    return "\n".join(parts)

if __name__ == "__main__":
    lang = sys.argv[1]
    tpl = open(os.path.join(os.path.dirname(__file__), f"overview_{lang}.tpl"), encoding="utf-8").read()
    print(tpl.replace("{{CATALOG}}", catalog(lang)).replace("{{WEB_SEARCH}}", web_search_table(lang)))
