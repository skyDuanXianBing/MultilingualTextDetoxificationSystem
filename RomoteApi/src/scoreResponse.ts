import { createJsonTranslator } from "typechat"
import { createTypeScriptJsonValidator } from "typechat/ts"
import { createLanguageModel } from "./typechatMethod"
import { getContentScorePrompt, getNeutralFluencyPrompt, getToxicPairwisePrompt } from "./scorePrompt"

// 创建模型实例
const aliNormalModel = createLanguageModel(
  process.env.ALIYUN_API_KEY || "",
  "qwen-plus-latest",
  "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
  false
)

/**
 * 评估两个句子的内容相似度
 * @param toxic_sentence 有毒句子
 * @param neutral_sentence 无毒句子
 * @returns 内容相似度评分和原因
 */
async function evaluateContentScore(toxic_sentence: string, neutral_sentence: string) {
  const prompt = getContentScorePrompt()
  
  // 创建验证器
  const validator = createTypeScriptJsonValidator(prompt, "ContentScoreResponse")

  // 创建 JSON 转换器
  const translator = createJsonTranslator(aliNormalModel, validator)

  // 构建输入字符串
  const inputString = `
句子1是代表着互联网或者生活中带有黑话、污言秽语等文本

句子1：${toxic_sentence}

句子2：${neutral_sentence}

在不考虑语言色彩的情况下，句子1和句子2表达意思相同吗？

非常相同为5分，相同为4分，无法判断为3分，不相同为2分，非常不相同为1分。
`

  // 调用转换器
  const response = await translator.translate(inputString)
  if (response.success) {
    console.log("内容相似度评分结果:", response.data)
    return response.data
  } else {
    console.error("内容相似度评分失败:", response.message)
    // 返回默认值
    return { content_score: 3, reason: "评估失败，返回默认值" }
  }
}

/**
 * 评估句子的流畅性
 * @param neutral_sentence 需要评估的句子
 * @returns 流畅性评分
 */
async function evaluateNeutralFluency(neutral_sentence: string) {
  const prompt = getNeutralFluencyPrompt()
  
  // 创建验证器
  const validator = createTypeScriptJsonValidator(prompt, "NeutralFluencyResponse")

  // 创建 JSON 转换器
  const translator = createJsonTranslator(aliNormalModel, validator)

  // 构建输入字符串
  const inputString = `
<任务介绍>
你的任务是按照要求判断句子流畅性。
</任务介绍>

<评价指标>
neutral_fluency 可选值为 0到1之间的数值，
0 = 完全无法理解，存在严重语法/逻辑断裂，比如【？？？啊？？我？？】
0.5 = 存在明显语病但勉强可懂，比如句子里"借用"与"优点"的搭配不当，导致语病
1 = 符合语法规范且表意清晰
</评价指标>

<你需要评价的句子>
${neutral_sentence}
</你需要评价的句子>
`

  // 调用转换器
  const response = await translator.translate(inputString)
  if (response.success) {
    console.log("流畅性评分结果:", response.data)
    return response.data
  } else {
    console.error("流畅性评分失败:", response.message)
    // 返回默认值
    return { neutral_fluency: 0.5 }
  }
}

/**
 * 评估两个句子的冒犯性对比
 * @param toxic_sentence 有毒句子
 * @param neutral_sentence 无毒句子
 * @returns 冒犯性对比评分
 */
async function evaluateToxicPairwise(toxic_sentence: string, neutral_sentence: string) {
  const prompt = getToxicPairwisePrompt()
  
  // 创建验证器
  const validator = createTypeScriptJsonValidator(prompt, "ToxicPairwiseResponse")

  // 创建 JSON 转换器
  const translator = createJsonTranslator(aliNormalModel, validator)

  // 构建输入字符串
  const inputString = `
<任务背景介绍> 
在自然语言处理领域，文本中常常包含一些具有攻击性、歧视性、虚假信息等有害内容，这些内容不仅会影响信息的传播和交流，还可能对用户造成不良影响。文本解毒任务旨在对含有有害信息的文本进行处理，去除或修正这些有害内容，使其成为积极、健康、真实且无歧视性的文本，从而提升文本质量和信息传递的有效性。
</任务背景介绍>

<任务介绍>
您将看到两个句子。您的任务是判断哪一个句子更具冒犯性。这两个句子的冒犯性程度可能相同（例如，两个句子都是同样中性的，或者同样冒犯性）。
</任务介绍>

<评价指标>
toxic_pairwise_score：哪一个句子更具有冒犯性，可选值为[5,4,3,2,1]。
如果你感觉句子1比句子2更加冒犯得多时，toxic_pairwise_score为5；
如果你感觉句子1比句子2更加冒犯时，toxic_pairwise_score为4；
如果你感觉句子1和句子2的冒犯程度相同时，toxic_pairwise_score为3；
如果你感觉句子2比句子1更加冒犯时，toxic_pairwise_score为2；
如果你感觉句子2比句子1更加冒犯得多时，toxic_pairwise_score为1；
</评价指标>

<你需要评价的数据> 
句子1: ${toxic_sentence}
句子2: ${neutral_sentence}
</你需要评价的数据>
`

  // 调用转换器
  const response = await translator.translate(inputString)
  if (response.success) {
    console.log("冒犯性对比评分结果:", response.data)
    return response.data
  } else {
    console.error("冒犯性对比评分失败:", response.message)
    // 返回默认值
    return { toxic_pairwise_score: 3 }
  }
}

export { evaluateContentScore, evaluateNeutralFluency, evaluateToxicPairwise }
