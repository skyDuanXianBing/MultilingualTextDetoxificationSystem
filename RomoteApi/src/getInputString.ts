export function getInputString(lang: string, toxic_sentence: string, detoxifiedText1: string, detoxifiedText2: string) {
    let inputString = ""
    // Use normalizedLang or lang depending on which variable holds the target language code
    // Assuming normalizedLang is the variable to use based on the second snippet
    const langToUse = lang.toLowerCase() // Normalize for case-insensitivity
  
    switch (langToUse) {
      case "en":
        inputString = `Original text: ${toxic_sentence}\nLocal model result: ${detoxifiedText1}\nNormal thinking result: ${detoxifiedText2}`
        break
      case "es":
        inputString = `Texto original: ${toxic_sentence}\nResultado del modelo local: ${detoxifiedText1}\nResultado del pensamiento normal: ${detoxifiedText2}`
        break
      case "ru":
        inputString = `Исходный текст: ${toxic_sentence}\nРезультат локальной модели: ${detoxifiedText1}\nРезультат обычного мышления: ${detoxifiedText2}`
        break
      case "zh":
        inputString = `原始文本: ${toxic_sentence}\n本地模型结果: ${detoxifiedText1}\n普通思考结果: ${detoxifiedText2}`
        break
      case "de":
        inputString = `Originaltext: ${toxic_sentence}\nErgebnis des lokalen Modells: ${detoxifiedText1}\nErgebnis des normalen Denkens: ${detoxifiedText2}`
        break
      case "fr":
        inputString = `Texte original: ${toxic_sentence}\nRésultat du modèle local: ${detoxifiedText1}\nRésultat de la réflexion normale: ${detoxifiedText2}`
        break
      case "ja":
        inputString = `元のテキスト: ${toxic_sentence}\nローカルモデルの結果: ${detoxifiedText1}\n通常の思考結果: ${detoxifiedText2}`
        break
      case "ar":
        inputString = `النص الأصلي: ${toxic_sentence}\nنتيجة النموذج المحلي: ${detoxifiedText1}\nنتيجة التفكير العادي: ${detoxifiedText2}`
        break
      case "hi":
      case "hin": // Assuming hin (Hindi variant) uses the same labels as hi (Hindi)
        inputString = `मूल पाठ: ${toxic_sentence}\nस्थानीय मॉडल परिणाम: ${detoxifiedText1}\nसामान्य सोच परिणाम: ${detoxifiedText2}`
        break
      case "uk":
        inputString = `Оригінальний текст: ${toxic_sentence}\nРезультат локальної моделі: ${detoxifiedText1}\nРезультат звичайного мислення: ${detoxifiedText2}`
        break
      case "am":
        inputString = `የመጀመሪያው ጽሑፍ: ${toxic_sentence}\nየአካባቢ ሞዴል ውጤት: ${detoxifiedText1}\nየመደበኛ አስተሳሰብ ውጤት: ${detoxifiedText2}`
        break
      case "it":
        inputString = `Testo originale: ${toxic_sentence}\nRisultato del modello locale: ${detoxifiedText1}\nRisultato del pensiero normale: ${detoxifiedText2}`
        break
      case "he":
        inputString = `טקסט מקורי: ${toxic_sentence}\nתוצאת מודל מקומי: ${detoxifiedText1}\nתוצאת חשיבה רגילה: ${detoxifiedText2}`
        break
      case "tt": // Tatar
        inputString = `Оригиналь текст: ${toxic_sentence}\nЛокаль модель нәтиҗәсе: ${detoxifiedText1}\nГади фикерләү нәтиҗәсе: ${detoxifiedText2}`
        break
      default:
        // 默认使用英文格式 for any language not explicitly handled above
        inputString = `Original text: ${toxic_sentence}\nLocal model result: ${detoxifiedText1}\nNormal thinking result: ${detoxifiedText2}`
    }
    return inputString
  }
  