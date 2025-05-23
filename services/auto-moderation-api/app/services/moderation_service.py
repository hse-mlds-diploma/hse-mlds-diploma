from typing import List, Dict, Any
import aiohttp
import os

class ModerationService:
    def __init__(self):
        self.text_moderation_url = os.getenv("TEXT_MODERATION_URL", "http://text-moderation-api:8002/moderate")
        self.image_moderation_url = os.getenv("IMAGE_MODERATION_URL", "http://image-moderation-api:8003/moderate")

    async def moderate_review(self, text: str, images: List[str]) -> Dict[str, Any]:
        # Moderate text
        text_result = await self._moderate_text(text)
        
        # Moderate images
        image_results = []
        for image_url in images:
            image_result = await self._moderate_image(image_url)
            image_results.append(image_result)

        # Combine results
        return {
            "text_moderation": text_result,
            "image_moderation": image_results,
            "approved": text_result.get("approved", False) and all(img.get("approved", False) for img in image_results)
        }

    async def _moderate_text(self, text: str) -> Dict[str, Any]:
        async with aiohttp.ClientSession() as session:
            async with session.post(self.text_moderation_url, json={"text": text}) as response:
                return await response.json()

    async def _moderate_image(self, image_url: str) -> Dict[str, Any]:
        async with aiohttp.ClientSession() as session:
            async with session.post(self.image_moderation_url, json={"image_url": image_url}) as response:
                return await response.json() 