from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import torch
from PIL import Image
import requests
from io import BytesIO
from transformers import AutoModelForImageClassification
from torchvision import transforms


app = FastAPI()


MODEL_NAME = "microsoft/resnet-50"
model = AutoModelForImageClassification.from_pretrained(MODEL_NAME)

# Define image transforms
transform = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])


class ModerationRequest(BaseModel):
    image_url: str


def load_image_from_url(url: str) -> Image.Image:
    try:
        response = requests.get(url)
        print('response', response)
        response.raise_for_status()
        return Image.open(BytesIO(response.content))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to load image from URL: {str(e)}")


def predict_image_safety(image: Image.Image) -> dict:
    print('Image size before processing:', image.size)
    print('Image mode:', image.mode)

    if image.mode != 'RGB':
        image = image.convert('RGB')
        print('Converted to RGB')

    image_tensor = transform(image)
    print('Applied transforms')

    image_tensor = image_tensor.unsqueeze(0)
    print('Added batch dimension')

    with torch.no_grad():
        outputs = model(image_tensor)
        logits = outputs.logits
        probabilities = torch.softmax(logits, dim=1)

        top5_probs, top5_indices = torch.topk(probabilities[0], 5)

        predictions = []
        for prob, idx in zip(top5_probs, top5_indices):
            predictions.append({
                "label": model.config.id2label[idx.item()],
                "score": prob.item()
            })

    return predictions


@app.post("/moderate")
async def moderate(request: ModerationRequest):
    try:
        print('start')
        image = load_image_from_url(request.image_url)

        predictions = predict_image_safety(image)

        UNSAFE_CATEGORIES = {
            "violence", "weapon", "nudity", "porn", "drug", "alcohol", "tobacco"
        }

        is_unsafe = any(
            any(unsafe in pred["label"].lower() for unsafe in UNSAFE_CATEGORIES)
            for pred in predictions[:3]
        )

        return {
            "approved": not is_unsafe,
            "predictions": predictions,
            "reason": "Image contains inappropriate content" if is_unsafe else "Image is appropriate"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
