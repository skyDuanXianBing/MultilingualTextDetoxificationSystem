import requests
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

# ANSI颜色代码
class Colors:
    RESET = "\033[0m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    PURPLE = "\033[95m"
    CYAN = "\033[96m"
    

LANG_PROMPTS = {
    "zh": "排毒：",
    "es": "Desintoxicar: ",
    "ru": "Детоксифицируй: ",
    "ar": "إزالة السموم: ",
    "hi": "विषहरण: ",
    "uk": "Детоксифікуй: ",
    "de": "Entgiften: ",
    "am": "መርዝ መርዝ: ",
    "en": "Detoxify: ",
    "it": "Disintossicare: ",
    "fr": "Détoxifier: ",
    "he": "לְטַהֵר: ",
    "hin": "विषहरण: ",
    "tt": "Токсиннардан арындыру: ",
    "ja": "解毒: ",
}


# 全局变量，用于缓存模型和分词器
_model = None
_tokenizer = None


def get_model_and_tokenizer():
    """获取模型和分词器的单例实例"""
    global _model, _tokenizer

    if _model is None or _tokenizer is None:
        print(f"{Colors.YELLOW}正在加载本地模型...{Colors.RESET}")
        _model = AutoModelForSeq2SeqLM.from_pretrained(
            "s-nlp/mt0-xl-detox-orpo",
            device_map="auto",
            torch_dtype=torch.float16,
        )
        _tokenizer = AutoTokenizer.from_pretrained("s-nlp/mt0-xl-detox-orpo")
        print(f"{Colors.GREEN}本地模型加载完成{Colors.RESET}")

    return _model, _tokenizer


def localDetoxify(text, lang):
    """使用本地模型进行文本解毒"""
    model, tokenizer = get_model_and_tokenizer()

    # 确保语言在LANG_PROMPTS中
    if lang not in LANG_PROMPTS:
        print(f"{Colors.RED}警告: 语言 '{lang}' 不在预定义提示词中，使用英语提示词代替{Colors.RESET}")
        lang = "en"

    encodings = tokenizer(LANG_PROMPTS[lang] + text, return_tensors="pt").to(
        model.device
    )

    outputs = model.generate(
        **encodings.to(model.device),
        max_length=128,
        num_beams=10,
        no_repeat_ngram_size=3,
        repetition_penalty=1.2,
        num_beam_groups=5,
        diversity_penalty=2.5,
        num_return_sequences=5,
        early_stopping=True,
    )
    print(
        f"{Colors.CYAN}本地解毒结果：{tokenizer.batch_decode(outputs, skip_special_tokens=True)[0]}{Colors.RESET}"
    )
    return tokenizer.batch_decode(outputs, skip_special_tokens=True)[0]


def remoteNormalDetoxify(text, lang):
    api_url = "http://localhost:3000"
    # 构建完整的URL，包含查询参数
    endpoint = f"{api_url}/api/normalDetoxify"
    params = {"toxic_sentence": text, "lang": lang}

    # 发送GET请求
    response = requests.get(endpoint, params=params)

    # 检查响应状态
    if response.status_code == 200:
        response_data = response.json()
        # 返回解毒后的文本
        result = response_data.get("detoxifiedText", "")
        print(f"{Colors.BLUE}远程普通思考结果：{result}{Colors.RESET}")
        return result
    else:
        raise Exception(
            f"{Colors.RED}API请求失败，状态码: {response.status_code}, 响应: {response.text}{Colors.RESET}"
        )



def remoteReasoningDetoxify(text, lang, detoxifiedText1, detoxifiedText2):
    api_url = "http://localhost:3000"
    # 构建完整的URL，包含查询参数
    endpoint = f"{api_url}/api/reasoningDetoxify"
    params = {
        "toxic_sentence": text,
        "lang": lang,
        "detoxifiedText1": detoxifiedText1,
        "detoxifiedText2": detoxifiedText2,
    }

    # 发送GET请求，设置超时时间为100秒
    response = requests.get(endpoint, params=params, timeout=200)

    # 检查响应状态
    if response.status_code == 200:
        response_data = response.json()
        # 返回深度思考后的最终解毒文本
        result = response_data.get("detoxifiedText", "")
        print(f"{Colors.PURPLE}远程深度思考结果：{result}{Colors.RESET}")
        return result
    else:
        raise Exception(
            f"{Colors.RED}API请求失败，状态码: {response.status_code}, 响应: {response.text}{Colors.RESET}"
        )
