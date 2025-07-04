import { getNormalDetoxify, getReasoningDetoxify } from "./src/typechatResponse"
import { evaluateContentScore, evaluateNeutralFluency, evaluateToxicPairwise } from "./src/scoreResponse"
// index.ts
console.log("Bun Web API 启动中...")

const server = Bun.serve({
  port: process.env.PORT || 3000, // 从环境变量读取端口，否则用 3000
  idleTimeout: 200, // 将超时时间设置为 200 秒
  async fetch(request) {
    const url = new URL(request.url)

    // 简单的路由
    if (url.pathname === "/") {
      return new Response("欢迎来到 Bun API!", {
        headers: { "Content-Type": "text/plain" },
      })
    }

    if (url.pathname === "/api/normalDetoxify") {
      const toxic_sentence = url.searchParams.get("toxic_sentence")
      const lang = url.searchParams.get("lang")
      const detoxifiedText = await getNormalDetoxify(lang!, toxic_sentence!)
      return new Response(JSON.stringify({ detoxifiedText }), {
        headers: { "Content-Type": "application/json" },
      })
    }

    if (url.pathname === "/api/reasoningDetoxify") {
      const toxic_sentence = url.searchParams.get("toxic_sentence")
      const lang = url.searchParams.get("lang")
      const detoxifiedText1 = url.searchParams.get("detoxifiedText1")
      const detoxifiedText2 = url.searchParams.get("detoxifiedText2")
      const detoxifiedText = await getReasoningDetoxify(lang!, toxic_sentence!, detoxifiedText1!, detoxifiedText2!)
      return new Response(JSON.stringify({ detoxifiedText }), {
        headers: { "Content-Type": "application/json" },
      })
    }

    // 评分API端点
    if (url.pathname === "/api/evaluateContentScore") {
      const toxic_sentence = url.searchParams.get("toxic_sentence")
      const neutral_sentence = url.searchParams.get("neutral_sentence")
      if (!toxic_sentence || !neutral_sentence) {
        return new Response(JSON.stringify({ error: "缺少必要参数" }), {
          status: 400,
          headers: { "Content-Type": "application/json" },
        })
      }
      const result = await evaluateContentScore(toxic_sentence, neutral_sentence)
      return new Response(JSON.stringify(result), {
        headers: { "Content-Type": "application/json" },
      })
    }

    if (url.pathname === "/api/evaluateNeutralFluency") {
      const neutral_sentence = url.searchParams.get("neutral_sentence")
      if (!neutral_sentence) {
        return new Response(JSON.stringify({ error: "缺少必要参数" }), {
          status: 400,
          headers: { "Content-Type": "application/json" },
        })
      }
      const result = await evaluateNeutralFluency(neutral_sentence)
      return new Response(JSON.stringify(result), {
        headers: { "Content-Type": "application/json" },
      })
    }

    if (url.pathname === "/api/evaluateToxicPairwise") {
      const toxic_sentence = url.searchParams.get("toxic_sentence")
      const neutral_sentence = url.searchParams.get("neutral_sentence")
      if (!toxic_sentence || !neutral_sentence) {
        return new Response(JSON.stringify({ error: "缺少必要参数" }), {
          status: 400,
          headers: { "Content-Type": "application/json" },
        })
      }
      const result = await evaluateToxicPairwise(toxic_sentence, neutral_sentence)
      return new Response(JSON.stringify(result), {
        headers: { "Content-Type": "application/json" },
      })
    }

    // 404 Not Found
    return new Response("页面未找到", { status: 404 })
  },
  error(error) {
    // 全局错误处理
    console.error("服务器错误:", error)
    return new Response(JSON.stringify({ error: "服务器内部错误", details: error.message }), {
      status: 500,
      headers: { "Content-Type": "application/json" },
    })
  },
})

console.log(`API 服务器正在监听 http://localhost:${server.port}`)
