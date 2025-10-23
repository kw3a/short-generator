from openai import OpenAI


def translate_batch(texts, target_lang):
    client = OpenAI()
    system = (
        "You are a translator. Translate ONLY the array of strings provided in the user's JSON. "
        "Return ONLY a JSON array (no additional text, no code fences). Preserve meaning and line breaks."
    )
    import json, re
    payload = json.dumps({"target": target_lang, "texts": texts}, ensure_ascii=False)
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": payload},
        ],
        temperature=0.0,
    )
    out = resp.choices[0].message.content or ""
    if out.strip().startswith("```"):
        out = re.sub(r"^```[a-zA-Z0-9]*\n|\n```$", "", out.strip())
    try:
        parsed = json.loads(out)
        if isinstance(parsed, dict) and "texts" in parsed:
            parsed = parsed["texts"]
        if isinstance(parsed, list):
            return parsed
    except Exception:
        try:
            start = out.find("[")
            end = out.rfind("]")
            if start != -1 and end != -1 and end > start:
                arr_str = out[start : end + 1]
                parsed = json.loads(arr_str)
                if isinstance(parsed, list):
                    return parsed
        except Exception:
            pass
    return texts
