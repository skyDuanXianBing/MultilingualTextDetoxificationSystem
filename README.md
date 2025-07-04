# 多语言文本去毒化项目 (Multilingual Text Detoxification)

## 📖 项目简介

这是一个基于深度学习的多语言文本去毒化系统，能够将有毒、攻击性或不当的文本转换为更加中性、礼貌的表达。项目支持多种语言，包括中文、英文、西班牙语、俄语、阿拉伯语、印地语、乌克兰语、德语、阿姆哈拉语、意大利语、法语、希伯来语、鞑靼语和日语。

## 🌟 主要特性

- **多语言支持**: 支持 13+ 种语言的文本去毒化
- **多种去毒模式**: 
  - 本地模型去毒化
  - 远程普通去毒化
  - 远程推理去毒化
- **评估系统**: 内置多维度评估指标
- **API 服务**: 基于 Bun 的高性能 Web API
- **批量处理**: 支持大规模数据集的并行处理

## 🏗️ 项目架构

```
NewPickMethod/
├── main.py                 # 主程序入口
├── model_detoxify.py      # 去毒化模型核心逻辑
├── score_evaluation.py    # 评估系统
├── normal_result.py       # 结果处理
├── RomoteApi/            # Web API 服务
│   ├── index.ts          # API 服务器
│   ├── src/              # API 源码
│   └── package.json      # 依赖配置
└── README.md             # 项目文档
```

## 🚀 快速开始

### 环境要求

- Python 3.8+
- Node.js 18+ 或 Bun
- CUDA 支持的 GPU (推荐)

### 安装依赖

#### Python 环境
```bash
pip install torch transformers pandas tqdm requests concurrent-futures
```

#### Bun 环境 (API 服务)
```bash
cd RomoteApi
bun install
```

#### 环境变量配置
```bash
# 复制环境变量模板文件
cp RomoteApi/.env.example RomoteApi/.env

# 编辑 .env 文件，填入真实的 API 密钥
# ALIYUN_API_KEY=your_aliyun_api_key_here
# SILICONFLOW_API_KEY=your_siliconflow_api_key_here
```

### 运行项目

#### 1. 启动 API 服务
```bash
cd RomoteApi
bun run dev
```

#### 2. 运行主程序
```bash
python main.py
```

#### 3. 运行评估系统
```bash
python score_evaluation.py
```

## 🔧 使用方法

### 本地模型去毒化

```python
from model_detoxify import localDetoxify

# 去毒化文本
result = localDetoxify("这是一段有毒的文本", "zh")
print(result)
```

### API 调用

#### 普通去毒化
```bash
curl "http://localhost:3000/api/normalDetoxify?toxic_sentence=有毒文本&lang=zh"
```

#### 推理去毒化
```bash
curl "http://localhost:3000/api/reasoningDetoxify?toxic_sentence=有毒文本&lang=zh"
```

### 支持的语言代码

| 语言 | 代码 | 语言 | 代码 |
|------|------|------|------|
| 中文 | zh | 英文 | en |
| 西班牙语 | es | 俄语 | ru |
| 阿拉伯语 | ar | 印地语 | hi |
| 乌克兰语 | uk | 德语 | de |
| 阿姆哈拉语 | am | 意大利语 | it |
| 法语 | fr | 希伯来语 | he |
| 鞑靼语 | tt | 日语 | ja |

## 📊 评估指标

项目内置多种评估指标：

- **内容评分**: 评估去毒化后文本的质量
- **中性流畅度**: 评估文本的中性程度和流畅性
- **毒性对比**: 对比原文和去毒化后文本的毒性差异

## 🔬 模型信息

- **基础模型**: `s-nlp/mt0-xl-detox-orpo`
- **模型类型**: Sequence-to-Sequence 转换模型
- **优化**: 支持 GPU 加速，使用 float16 精度
- **缓存机制**: 单例模式缓存模型，提高推理效率

## 📁 数据格式

输入数据支持多种格式：
- CSV 文件
- JSON 文件
- 直接文本输入

输出结果包含：
- 原始文本
- 去毒化后文本
- 评估分数
- 处理时间

## 🛠️ 开发指南

### 添加新语言支持

1. 在 `model_detoxify.py` 中的 `LANG_PROMPTS` 字典添加新语言提示
2. 更新 API 路由以支持新语言代码
3. 测试新语言的去毒化效果

### 自定义评估指标

1. 在 `score_evaluation.py` 中添加新的评估函数
2. 更新 API 端点以支持新指标
3. 在主程序中集成新的评估逻辑

## 🤝 贡献指南

1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 🙏 致谢

- [Hugging Face Transformers](https://huggingface.co/transformers/)
- [s-nlp/mt0-xl-detox-orpo](https://huggingface.co/s-nlp/mt0-xl-detox-orpo) 模型
- [Bun](https://bun.sh/) 运行时环境

## 📞 联系方式

如有问题或建议，请通过以下方式联系：

- 提交 Issue
- 发送邮件
- 参与讨论

---

**注意**: 本项目仅用于研究和教育目的，请负责任地使用文本去毒化技术。
