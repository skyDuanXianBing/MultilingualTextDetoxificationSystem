# Multilingual Text Detoxification Project

English | [中文](README.md)

## 📖 Project Overview

This is a deep learning-based multilingual text detoxification system that can transform toxic, offensive, or inappropriate text into more neutral and polite expressions. The project supports multiple languages including Chinese, English, Spanish, Russian, Arabic, Hindi, Ukrainian, German, Amharic, Italian, French, Hebrew, Tatar, and Japanese.

## 🌟 Key Features

- **Multilingual Support**: Text detoxification for 13+ languages
- **Multiple Detoxification Modes**: 
  - Local model detoxification
  - Remote normal detoxification
  - Remote reasoning detoxification
- **Evaluation System**: Built-in multi-dimensional evaluation metrics
- **API Service**: High-performance Web API based on Bun
- **Batch Processing**: Support for large-scale dataset parallel processing

## 🏗️ Project Architecture

```
NewPickMethod/
├── main.py                 # Main program entry
├── model_detoxify.py      # Detoxification model core logic
├── score_evaluation.py    # Evaluation system
├── normal_result.py       # Result processing
├── RomoteApi/            # Web API service
│   ├── index.ts          # API server
│   ├── src/              # API source code
│   └── package.json      # Dependencies configuration
└── README.md             # Project documentation
```

## 🚀 Quick Start

### Requirements

- Python 3.8+
- Node.js 18+ or Bun
- CUDA-supported GPU (recommended)

### Installation

#### Python Environment
```bash
pip install torch transformers pandas tqdm requests concurrent-futures
```

#### Bun Environment (API Service)
```bash
cd RomoteApi
bun install
```

#### Environment Variables Configuration
```bash
# Copy environment variables template file
cp RomoteApi/.env.example RomoteApi/.env

# Edit .env file and fill in real API keys
# ALIYUN_API_KEY=your_aliyun_api_key_here
# SILICONFLOW_API_KEY=your_siliconflow_api_key_here
```

### Running the Project

#### 1. Start API Service
```bash
cd RomoteApi
bun run dev
```

#### 2. Run Main Program
```bash
python main.py
```

#### 3. Run Evaluation System
```bash
python score_evaluation.py
```

## 🔧 Usage

### Local Model Detoxification

```python
from model_detoxify import localDetoxify

# Detoxify text
result = localDetoxify("This is a toxic text", "en")
print(result)
```

### API Calls

#### Normal Detoxification
```bash
curl "http://localhost:3000/api/normalDetoxify?toxic_sentence=toxic_text&lang=en"
```

#### Reasoning Detoxification
```bash
curl "http://localhost:3000/api/reasoningDetoxify?toxic_sentence=toxic_text&lang=en"
```

### Supported Language Codes

| Language | Code | Language | Code |
|----------|------|----------|------|
| Chinese | zh | English | en |
| Spanish | es | Russian | ru |
| Arabic | ar | Hindi | hi |
| Ukrainian | uk | German | de |
| Amharic | am | Italian | it |
| French | fr | Hebrew | he |
| Tatar | tt | Japanese | ja |

## 📊 Evaluation Metrics

The project includes multiple built-in evaluation metrics:

- **Content Score**: Evaluates the quality of detoxified text
- **Neutral Fluency**: Assesses the neutrality and fluency of text
- **Toxicity Comparison**: Compares toxicity differences between original and detoxified text

## 🔬 Model Information

- **Base Model**: `s-nlp/mt0-xl-detox-orpo`
- **Model Type**: Sequence-to-Sequence transformation model
- **Optimization**: GPU acceleration support with float16 precision
- **Caching Mechanism**: Singleton pattern model caching for improved inference efficiency

## 📁 Data Format

Input data supports multiple formats:
- CSV files
- JSON files
- Direct text input

Output results include:
- Original text
- Detoxified text
- Evaluation scores
- Processing time

## 🛠️ Development Guide

### Adding New Language Support

1. Add new language prompts to the `LANG_PROMPTS` dictionary in `model_detoxify.py`
2. Update API routes to support new language codes
3. Test detoxification effectiveness for the new language

### Custom Evaluation Metrics

1. Add new evaluation functions in `score_evaluation.py`
2. Update API endpoints to support new metrics
3. Integrate new evaluation logic in the main program

## 🤝 Contributing

1. Fork this project
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details

## 🙏 Acknowledgments

- [Hugging Face Transformers](https://huggingface.co/transformers/)
- [s-nlp/mt0-xl-detox-orpo](https://huggingface.co/s-nlp/mt0-xl-detox-orpo) model
- [Bun](https://bun.sh/) runtime environment

## 📞 Contact

If you have any questions or suggestions, please contact us through:

- Submit an Issue
- Send an email
- Join the discussion

---

**Note**: This project is for research and educational purposes only. Please use text detoxification technology responsibly.
