---
title: "文本模型总览"
description: "全部文本模型的目录：支持的能力、计费方式与调用入口"
---

所有文本模型都走 OpenAI 兼容的 Chat Completions 接口（Responses 专用模型除外），换模型只改 `model`，不需要按厂商换 URL 或换 Key。本页按厂商列出全部模型 ID、支持的能力和计费方式。

## 调用入口

<CardGroup cols={2}>
  <Card title="Chat Completions" icon="comments" href="/cn/api-reference/text/general-chat">
    `POST /v1/chat/completions`。默认入口，本页所有模型都从这里调用（Responses 专用模型除外）。
  </Card>
  <Card title="Responses" icon="layer-group" href="/cn/api-reference/text/openai-multimodal">
    `POST /v1/responses`。除 `deepseek-v3.1-terminus` 外的全部文本模型都可从这里调用，Codex 等客户端走这个入口；GPT Pro / Codex / o3-pro 系列只接受这个入口。
  </Card>
  <Card title="Claude Messages" icon="message" href="/cn/api-reference/text/claude-messages">
    `POST /v1/messages`。为已有 Anthropic SDK 的应用保留的原生信封；GPT-5.6、GPT-6、GPT-6.1 系列与 Responses 专用模型之外的全部文本模型都可从这里调用。
  </Card>
  <Card title="Gemini 原生" icon="google" href="/cn/api-reference/text/gemini-native">
    `POST /v1beta/models/{model}:generateContent`。为已有 Gemini 客户端保留的原生信封。
  </Card>
</CardGroup>

新接入建议使用 Chat Completions。原生入口用于兼容已有客户端，除联网搜索外不提供额外能力。所有入口都用 WaveAPI Key 作为凭据（Chat / Responses 走 `Authorization: Bearer`，Messages 走 `x-api-key` 或 `Authorization: Bearer`，Gemini 原生走 `x-goog-api-key`、`Authorization: Bearer` 或查询参数 `key`），生态登录 token 不能代替模型 Key，见[认证](/cn/docs/authentication)。

## 计费口径

各模型的单价见 `GET /v1/models` 返回的 `price_config`，或控制台「模型市场」。单次调用的实际花费见响应里的 `usage.cost`。

以下规则适用于全部文本模型，模型之间的差异见各厂商表格与表下的「模型备注」。

- **售价来源**：按官方标准价九折或原价制定，不高于官方；不使用 Batch、Flex、Priority 等特殊价。具体单价见 `GET /v1/models` 的 `price_config`。
- **输入总量含缓存**：`prompt_tokens` 是输入总量，其中实际报告的缓存命中 / 缓存写入 token 按对应缓存价计费，其余按普通输入价；缓存部分是输入的组成部分，不在总量之外再加一次。
- **思考含在输出里**：`completion_tokens` 已包含 `completion_tokens_details.reasoning_tokens`，思考 token 按输出价计费一次，不再叠加。
- **两项计价模型**：计费方式为「输入输出两项」的模型没有缓存价，响应里的缓存统计按普通输入价计，显式 `cache_control` 会被忽略，输入全部按输入价计费。
- **长上下文分档**：有分档的模型以**输入总量**（含缓存）判断档位，达到阈值后整单（输入、缓存、输出）切换到高档价，不是只对超出部分加价。阈值与「恰好等于阈值」的归属见各厂商段落。
- **时段价**：DeepSeek V4 按请求开始时刻的 UTC 时段定价，见 DeepSeek 段落。
- **联网搜索**：按实际执行的搜索次数计费，单价是 `price_config.web_search_per_1k`（USD / 1,000 次），与 token 费用合计后一起换算 quota。`/v1/responses` 只计搜索动作（`action.type: "search"`），打开网页与页内查找不计；`/v1/messages` 按 `usage.server_tool_use.web_search_requests` 计。可用入口与模型见下表。
- **额度换算**：分项费用合计后换算成整数 quota，**500,000 quota = 1 USD**；有正用量但不足 1 quota 的请求按 1 quota 计，再应用账户分组倍率并取整。响应里的 `usage.cost` 就是这个整数 quota，**不是美元**。

{{WEB_SEARCH}}

表外模型在 `/v1/responses` 上带联网搜索工具时，该工具被忽略，不执行搜索、不收搜索费（`gpt-5-pro`、`gpt-5.2-pro`、`gpt-5.4-pro`、`gpt-5.3-codex`、`o3-pro` 不支持工具调用，返回 `400`）；`tool_choice` 强制指定联网搜索时返回 `400`。表外模型在 `/v1/messages` 上带联网搜索工具返回 `400`。Chat 接口不提供联网搜索。

各项单价的单位是 USD / 100 万 token：

```text
普通输入 token = prompt_tokens - cached_tokens - cache_write_tokens
费用（USD） = ( 普通输入 token × 输入价
             + cached_tokens × 缓存读价
             + cache_write_tokens × 缓存写价
             + completion_tokens × 输出价 ) / 1,000,000
             + 联网搜索次数 × web_search_per_1k / 1,000
quota      = 费用（USD） × 500,000，向下取整，最低 1
```

最终扣款以控制台账单中的文本账务记录为准，状态含义如下：

| 账务状态 | 含义 |
|---|---|
| `reserved` | 已冻结额度，结果尚未确认；冻结金额不是最终费用 |
| `pricing_pending` | 已收到用量，费用待核对；额度继续冻结 |
| `settlement_pending` / `refund_pending` | 等待结算或退款完成 |
| `settled` / `refunded` | 扣费或退款已完成；以最终账务金额核对 |

<Warning>
没有收到完整 `usage`、连接中断或响应缺少费用字段，都**不代表本次调用免费**。先到控制台核对已有用量记录，不要自动重发。
</Warning>

## 缓存

缓存能力按模型分四档，取决于该模型配了哪几项缓存价。
缓存读写按各自单价**替代**对应的普通输入费用，不在输入之外另加一笔。

| 档 | 判据 | 模型 |
|---|---|---|
| 无缓存优惠 | `cache_billing: "input_output"` | 目录中其余全部模型；响应里若带缓存统计，一律按普通输入价计 |
| 只有缓存读 | 配了 `cache_read` | `gpt-5.5` `gpt-5.4` `gpt-5.4-mini` `gpt-5.4-nano` `gpt-5.2` `gpt-5.1` `gpt-5` `gpt-5-mini` `gpt-5-nano` `gpt-4.1` `gpt-4.1-mini` `gpt-4.1-nano` `o4-mini` `o3-mini` `o1` `grok-4.7` `grok-4.6` `gemini-3.6-flash` `gemini-3.7-flash` `gemini-3.8-flash` `kimi-k3` `glm-5.3` |
| 缓存读 + 写 | 再配 `cache_write` | `gpt-5.6-luna` `gpt-5.6-terra` `gpt-5.6-sol` `gpt-6-astra` `gpt-6-sol` `gpt-6-luna` `gpt-6.1-sol` `qwen3.8-max` `qwen3.8-max-0902` `qwen3.8-2.4t-a95b` `qwen3.8-27b` `qwen3.8-flash` `qwen3.7-flash` |
| 缓存读 + 5 分钟写 + 1 小时写 | 再配 `cache_write_1h` | `claude-opus-5-5` `claude-sonnet-5-5` `claude-opus-5` `claude-sonnet-5` `claude-fable-5` `claude-fable-5-1` `claude-opus-4-8` `claude-opus-4-7` `claude-opus-4-6` `claude-sonnet-4-6` `claude-sonnet-4-5` `claude-haiku-4-5` |
| 时段缓存价 | `text_schedule` 各时段带 `cache_read` | `deepseek-v4-pro` `deepseek-v4-flash` |

### 自动缓存与显式缓存

**自动缓存**由上游决定是否命中，调用方不传任何参数：命中的 token 出现在
`usage.prompt_tokens_details.cached_tokens` 里，按该模型的缓存读价计费。是否命中不做保证，成本预估不应假定必定命中。

**显式缓存**在请求里用 `cache_control` 标出可复用的前缀，按模型放行：

| 模型 | 显式 `cache_control` |
|---|---|
| `claude-opus-5-5` `claude-sonnet-5-5` `claude-opus-5` `claude-sonnet-5` `claude-fable-5` `claude-fable-5-1` `claude-opus-4-8` `claude-opus-4-7` `claude-opus-4-6` `claude-sonnet-4-6` `claude-sonnet-4-5` `claude-haiku-4-5` | ✅ 放行，三档缓存价齐备（读 / 5 分钟写 / 1 小时写） |
| `qwen3.8-*`、`qwen3.7-flash` | ✅ 放行，写入按缓存写入价计，显式命中按缓存读价计 |
| 所有 `gemini-*` | 上游只有自动缓存，`cache_control` 不生效；原生接口的 `cachedContent` 不支持，传入返回 400 |
| 两项计价模型 | `cache_control` 会被忽略，输入全部按输入价计费 |
| 其余（`gpt-4.1*`、`gpt-5*`、`gpt-6-astra`、`o1`、`o3-mini`、`o4-mini`、`grok-4.6`、`grok-4.7`、`glm-5.3`、`kimi-k3`、`deepseek-v4-*`） | 上游只有自动缓存，不需要也不用传 `cache_control` |

不支持的请求返回 `400`，不计费。

<Note>
首次接入时，建议先用小请求确认控制台用量记录里的缓存分项符合预期，再放量。
</Note>

### Claude 显式缓存写法

OpenAI 兼容接口：`content` **必须是内容块数组**，字符串形式的 `content` 带不了 `cache_control`，
标记会被忽略、整段按普通输入计费。

```json
{
  "model": "claude-sonnet-5",
  "max_tokens": 1024,
  "messages": [
    {
      "role": "system",
      "content": [
        {
          "type": "text",
          "text": "这里放要反复复用的长前缀……",
          "cache_control": {"type": "ephemeral"}
        }
      ]
    },
    {"role": "user", "content": "基于上面的内容回答。"}
  ]
}
```

原生 [Messages 接口](/cn/api-reference/text/claude-messages)把前缀放在 `system` 数组里，写法相同。
`ttl` 省略时为 5 分钟；要用 1 小时档，请求里写 `"cache_control": {"type": "ephemeral", "ttl": "1h"}`
并带上 `anthropic-beta: extended-cache-ttl-2025-04-11` 请求头——该头由网关原样透传到上游。

### 命中条件与读数

- **前缀长度**：通常至少约 1,024 token，更短的前缀不会产生缓存。
- **前缀逐字节一致**：文本、空格、换行、内容块顺序有任何差异都不算命中。
- **在 TTL 内复用**：5 分钟或 1 小时从最近一次命中重新计时。

Chat 响应里 `usage.prompt_tokens_details.cached_tokens` 是命中量；原生 Messages 用
`cache_read_input_tokens` 与 `cache_creation_input_tokens`，并且原生的 `input_tokens`
**不含**这两项，总输入是三者相加（Chat 的 `prompt_tokens` 则已经含在内）。写入量按缓存写价计费，高于普通输入价，因此显式缓存适用于前缀稳定、且会在 TTL 内被复用的场景。

## 当前不支持

以下请求会返回 `400`，不计费：

- **厂商内置工具**——`tools` 里出现 `function` / `custom` 之外的类型（托管执行、文件检索等）。由调用方自己执行的函数工具不在此列，正常使用；联网搜索见[计费口径](#计费口径)。
- **`web_search_options`**。
- **`service_tier`** 取 `standard` / `default` 以外的值。
- **`cachedContent`**（Gemini 原生接口）——见上文的放行表。

每个模型只服务它支持的协议（Chat / Responses / Claude Messages / Gemini 原生）。把请求发到模型不支持的协议，或者在不支持工具、结构化输出的模型上传 `tools`、`tool_choice`、`response_format`，同样返回 `400`。各入口可调用的模型见[调用入口](#调用入口)，各模型支持的能力见下方模型目录。

## 模型目录

<Note>
**怎么读表**：所有模型都支持非流式与流式文本输出，因此不单列。「JSON / 工具」一列左为 JSON Schema 结构化输出、右为函数调用——**平台只返回函数名和参数，工具由你的应用执行**；`✓` 表示支持，`—` 表示不支持。「计费方式」一列说明该模型按哪些维度计费，单价见[目录接口](#目录接口)。带长上下文分档的模型以**输入总量**（含缓存）判断档位，达到阈值后整单切换，阈值写在表下的「模型备注」里。「模型备注」还写各模型的输入输出上限与专有限制；上限是接口允许的最大值，输入和输出不能同时用到上限。
</Note>

{{CATALOG}}
## 目录接口

模型的实时可用性、价格配置与能力字段以目录接口为准：

```bash
curl https://api.qingbo.ai/v1/models \
  -H "Authorization: Bearer $WAVE_API_KEY"
```

单个模型：`GET /v1/models/{model}`。返回的 `price_config` 就是本页表格的来源：`input` / `output` 是基础单价，`cache_read` / `cache_write` / `cache_write_1h` 表示该模型开放到哪一档缓存，`input_tier_threshold` 与 `*_above_price` 是长上下文分档，`cache_billing: "input_output"` 表示只有输入输出两项计价。

目录接口返回的模型即为当前已上架的全部文本模型，未出现在返回结果中的模型不可调用。
