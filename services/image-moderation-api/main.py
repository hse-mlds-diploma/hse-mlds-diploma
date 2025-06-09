from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import torch
from torch import nn
from PIL import Image
import requests
from io import BytesIO
import clip
from torchvision import transforms


app = FastAPI()


model, preprocess = clip.load("ViT-B/32", device="cpu")

visual_encoder = model.visual
visual_encoder = model.visual.float()
for param in visual_encoder.parameters():
    param.requires_grad = False

transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.RandomHorizontalFlip(),
    transforms.ColorJitter(brightness=0.2, contrast=0.2),
    transforms.ToTensor(),
    transforms.Normalize((0.4815, 0.4578, 0.4082), (0.2686, 0.2613, 0.2758))
])


classifier = nn.Sequential(
    nn.Linear(512, 256),
    nn.ReLU(),
    nn.Dropout(0.2),
    nn.Linear(256, 3)
)
classifier.load_state_dict(torch.load("clip_classifier.pth", map_location="cpu"))
classifier.to("cpu")
classifier.eval()


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
        features = visual_encoder(image_tensor)

        outputs = classifier(features)
        preds = torch.argmax(outputs, dim=1)

    return preds.item()


@app.post("/moderate")
async def moderate(request: ModerationRequest):
    try:
        print('start')
        image = load_image_from_url(request.image_url)

        predictions = predict_image_safety(image)

        is_unsafe = predictions != 1

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
