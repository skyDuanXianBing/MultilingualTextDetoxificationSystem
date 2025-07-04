import { createJsonTranslator } from "typechat"
import { createTypeScriptJsonValidator } from "typechat/ts"
import type { AIResponse } from "./AIResponse"
import getNormalPrompt from "./normalPrompt"
import { createLanguageModel } from "./typechatMethod"
import getReasoningPrompt from "./reasoningPrompt"
import { getInputString } from "./getInputString"

// 创建推理 detoxify 模型
const reasoningModel = createLanguageModel(
  process.env.SILICONFLOW_API_KEY || "",
  "Qwen/Qwen3-235B-A22B",
  "https://api.siliconflow.cn/v1/chat/completions",
  false
)

const aliReasoningModel = createLanguageModel(
  process.env.ALIYUN_API_KEY || "",
  "qwen-plus-latest",
  "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
  false
)

// 创建普通 detoxify 模型
const normalModel = createLanguageModel(
  process.env.SILICONFLOW_API_KEY || "",
  "Qwen/Qwen3-235B-A22B",
  "https://api.siliconflow.cn/v1/chat/completions",
  false
)

const aliNormalModel = createLanguageModel(
  process.env.ALIYUN_API_KEY || "",
  "qwen-plus-latest",
  "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
  false
)

let normalErrorCount = 0
let normalAllCount = 0

async function getNormalDetoxify(lang: string, toxic_sentence: string) {
  const prompt = getNormalPrompt(lang)
  // 创建验证器
  const validator = createTypeScriptJsonValidator<AIResponse>(prompt!, "AIResponse")

  // 创建 JSON 转换器
  const detoxTranslator = createJsonTranslator(aliNormalModel, validator)

  normalAllCount++
  let retryCount = 0
  const maxRetries = 10

  while (retryCount < maxRetries) {
    // 调用转换器
    const response = await detoxTranslator.translate(toxic_sentence)
    if (response.success) {
      console.log("云端普通思考结果" + response.data.detoxifiedText)
      return normalizeWhitespace(response.data.detoxifiedText)
    } else {
      retryCount++
      if (retryCount === maxRetries) {
        normalErrorCount++
        console.log("普通思考错误数量" + normalErrorCount + "总数" + normalAllCount + "比例" + normalErrorCount / normalAllCount)
        console.log("云端普通思考出错，返回原始句子")
        return toxic_sentence
      }
      console.log(`重试第 ${retryCount} 次...`)
    }
  }
}

let exceptionCount = 0
let errorCount = 0
let allCount = 0
async function getReasoningDetoxify(lang: string, toxic_sentence: string, detoxifiedText1: string, detoxifiedText2: string) {
  const prompt = getReasoningPrompt(lang)
  // 创建验证器
  const validator = createTypeScriptJsonValidator<AIResponse>(prompt!, "AIResponse")

  // 创建 JSON 转换器
  const detoxTranslator = createJsonTranslator(aliReasoningModel, validator)
  allCount++
  // 根据语言构建适当的输入字符串
  let inputString = getInputString(lang, toxic_sentence, detoxifiedText1, detoxifiedText2)
  // 调用转换器
  const response = await detoxTranslator.translate(inputString)
  if (response.success) {
    const result = response.data.detoxifiedText
    console.log("云端深度思考结果" + result)

    if(isTooLength(toxic_sentence.length,detoxifiedText1.length,detoxifiedText2.length,normalizeWhitespace(result).length)){
      exceptionCount++
      console.log("异常数量" + exceptionCount + "总数" + allCount + "比例" + exceptionCount / allCount)
      console.log("云端深度思考结果与输入长度差异过大，使用普通思考结果代替")
      return detoxifiedText2 // 返回普通思考结果
    }

    return normalizeWhitespace(result)
  } else {
    errorCount++
    console.log("错误数量" + errorCount + "总数" + allCount + "比例" + errorCount / allCount)
    console.log("云端深度思考出错，使用本地思考结果代替")
    return detoxifiedText1
  }
}
/**
 * 移除或规范化字符串中的异常空白字符。
 * - 将所有连续的空白字符（包括 \t, \n, \r, 以及多个空格）替换为单个空格。
 * - 移除字符串开头和结尾的空格。
 *
 * @param text 要处理的原始字符串。
 * @returns 处理后的字符串；如果输入为 null 或 undefined，则返回空字符串。
 */
function normalizeWhitespace(text: string | null | undefined): string {
  if (text === null || typeof text === 'undefined') {
    return '';
  }

  // 1. 使用正则表达式 \s+ 匹配一个或多个连续的空白字符
  //    （\s 匹配任何空白字符，包括空格、制表符、换行符等）。
  // 2. 将匹配到的连续空白字符替换为单个空格 " "。
  let normalizedText = text.replace(/\s+/g, ' ');

  // 3. 使用 trim() 方法移除字符串开头和结尾的空格。
  //    注意：trim() 只移除标准空格，如果 \s+ 替换后在首尾留下了非标准空格（理论上不太可能，因为\s+会匹配它们），
  //    则可能需要更复杂的trim逻辑，但对于常见情况 .trim() 已足够。
  //    由于我们先用 \s+ 替换为了标准空格，所以 .trim() 是有效的。
  normalizedText = normalizedText.trim();

  return normalizedText;
}


function isTooLength(toxic_sentence_length: number, detoxifiedText1_length: number, detoxifiedText2_length: number, result_length: number) {
  const maxLength = toxic_sentence_length + detoxifiedText1_length + detoxifiedText2_length;
  return result_length > maxLength;
}



export { getNormalDetoxify, getReasoningDetoxify }
