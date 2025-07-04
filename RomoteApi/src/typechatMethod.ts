import { type PromptSection, type Success, type TypeChatLanguageModel, type Error } from "typechat"
function createFetchLanguageModel(url: string, headers: object, defaultParams: object,thinking:boolean) {
  const model: TypeChatLanguageModel = {
    complete,
  }
  return model

  async function complete(prompt: string | PromptSection[]) {
    let retryCount = 0
    const retryMaxAttempts = model.retryMaxAttempts ?? 3
    const retryPauseMs = model.retryPauseMs ?? 1000
    const messages = typeof prompt === "string" ? [{ role: "user", content: prompt }] : prompt
    while (true) {
      const options = {
        method: "POST",
        body: JSON.stringify({
          ...defaultParams,
          messages,
          temperature: 0,
          n: 1,
          enable_thinking: thinking,
        }),
        headers: {
          "content-type": "application/json",
          ...headers,
        },
      }
      const response = await fetch(url, options)
      if (response.ok) {
        const json = (await response.json()) as { choices: { message: PromptSection }[] }
        if (typeof json.choices[0]!.message.content === "string") {
          return success(json.choices[0]!.message.content ?? "")
        } else {
          return error(`REST API unexpected response format: ${JSON.stringify(json.choices[0]!.message.content)}`)
        }
      }
      if (!isTransientHttpError(response.status) || retryCount >= retryMaxAttempts) {
        return error(`REST API error ${response.status}: ${response.statusText}`)
      }
      await sleep(retryPauseMs)
      retryCount++
    }
  }
}

/**
 * Returns true of the given HTTP status code represents a transient error.
 */
function isTransientHttpError(code: number): boolean {
  switch (code) {
    case 429: // TooManyRequests
    case 500: // InternalServerError
    case 502: // BadGateway
    case 503: // ServiceUnavailable
    case 504: // GatewayTimeout
      return true
  }
  return false
}

/**
 * Sleeps for the given number of milliseconds.
 */
function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms))
}

function success<T>(data: T): Success<T> {
  return { success: true, data }
}
function error(message: string): Error {
  return { success: false, message }
}

export function createLanguageModel(
  apiKey: string,
  model: string,
  endPoint = "https://api.openai.com/v1/chat/completions",
  thinking:boolean
): TypeChatLanguageModel {
  const headers = {
    Authorization: `Bearer ${apiKey}`,
  }
  return createFetchLanguageModel(endPoint, headers, { model },thinking)
}
