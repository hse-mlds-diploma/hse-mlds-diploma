from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

app = FastAPI()

# Load model and tokenizer
MODEL_NAME = "SkolkovoInstitute/russian_toxicity_classifier"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)


class ModerationRequest(BaseModel):
    text: str


def predict_toxicity(text: str) -> float:
    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits
        probabilities = torch.softmax(logits, dim=1)
        toxicity_score = probabilities[0][1].item()
    return toxicity_score


@app.post("/moderate")
async def moderate(request: ModerationRequest):
    try:
        toxicity_score = predict_toxicity(request.text)

        TOXICITY_THRESHOLD = 0.5

        return {
            "approved": toxicity_score < TOXICITY_THRESHOLD,
            "toxicity_score": toxicity_score,
            "reason": "Text is too toxic" if toxicity_score >= TOXICITY_THRESHOLD else "Text is appropriate"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
