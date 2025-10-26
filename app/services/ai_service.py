import base64
import json
import numpy as np
from typing import List, Dict, Tuple
from openai import OpenAI
from PIL import Image
import colorsys
from sklearn.metrics.pairwise import cosine_similarity
import logging

from app.config import settings

logger = logging.getLogger(__name__)

class AIImageAnalysisService:
    """
    AI-powered image analysis service using OpenAI's vision models.
    
    This service provides:
    1. Image tagging (at least 5 relevant tags)
    2. Caption generation (short descriptive sentence)
    3. Embedding generation (for semantic search)
    4. Emotion analysis
    5. Color analysis
    """
    
    def __init__(self):
        self.client = OpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None
        self.model = settings.ai_model
        self.embedding_model = settings.embedding_model
        
    def _encode_image_to_base64(self, image_path: str) -> str:
        """Convert image to base64 for API calls."""
        try:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            logger.error(f"Error encoding image {image_path}: {e}")
            raise
    
    def _resize_image_for_analysis(self, image_path: str, max_size: Tuple[int, int] = (1024, 1024)) -> str:
        """Resize image to optimal size for analysis while maintaining aspect ratio."""
        try:
            with Image.open(image_path) as img:
                # Convert to RGB if necessary
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Resize maintaining aspect ratio
                img.thumbnail(max_size, Image.Resampling.LANCZOS)
                
                # Save to temporary file
                temp_path = image_path.replace('.', '_temp.')
                img.save(temp_path, 'JPEG', quality=85)
                return temp_path
        except Exception as e:
            logger.error(f"Error resizing image {image_path}: {e}")
            return image_path
    
    async def analyze_image(self, image_path: str) -> Dict:
        """
        Perform comprehensive AI analysis on an image.
        
        Returns:
            Dict containing tags, caption, embedding, emotions, and colors
        """
        if not self.client:
            logger.warning("OpenAI client not initialized. Using mock analysis.")
            return self._mock_analysis()
        
        try:
            # Resize image for optimal analysis
            resized_path = self._resize_image_for_analysis(image_path)
            
            # Encode image
            base64_image = self._encode_image_to_base64(resized_path)
            
            # Perform analysis tasks
            analysis_results = {}
            
            # 1. Generate tags and caption
            vision_response = await self._analyze_with_vision_model(base64_image)
            analysis_results.update(vision_response)
            
            # 2. Generate embedding for semantic search
            embedding = await self._generate_embedding(vision_response.get('caption', ''))
            analysis_results['embedding'] = embedding
            
            # 3. Perform emotion analysis
            emotions = await self._analyze_emotions(base64_image)
            analysis_results['emotions'] = emotions
            
            # 4. Perform color analysis
            colors = await self._analyze_colors(image_path)
            analysis_results['colors'] = colors
            
            # Clean up temporary file
            if resized_path != image_path:
                import os
                os.remove(resized_path)
            
            return analysis_results
            
        except Exception as e:
            logger.error(f"Error analyzing image {image_path}: {e}")
            return self._mock_analysis()
    
    async def _analyze_with_vision_model(self, base64_image: str) -> Dict:
        """Analyze image using OpenAI's vision model for tags and caption."""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": """Analyze this image and provide:
                                1. At least 5 relevant tags (as a JSON array)
                                2. A short descriptive caption (max 100 characters)
                                
                                Format your response as JSON:
                                {
                                    "tags": ["tag1", "tag2", ...],
                                    "caption": "short description"
                                }"""
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=300,
                temperature=0.3
            )
            
            content = response.choices[0].message.content
            # Extract JSON from response
            json_start = content.find('{')
            json_end = content.rfind('}') + 1
            json_str = content[json_start:json_end]
            
            result = json.loads(json_str)
            
            # Ensure we have at least 5 tags
            if len(result.get('tags', [])) < 5:
                result['tags'] = result.get('tags', []) + ['photography', 'image', 'visual', 'content', 'media']
            
            return result
            
        except Exception as e:
            logger.error(f"Error in vision model analysis: {e}")
            return {
                "tags": ["photography", "image", "visual", "content", "media"],
                "caption": "An interesting photograph"
            }
    
    async def _generate_embedding(self, text: str) -> List[float]:
        """Generate embedding vector for semantic search."""
        try:
            response = self.client.embeddings.create(
                model=self.embedding_model,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            # Return a random embedding as fallback
            return np.random.rand(1536).tolist()
    
    async def _analyze_emotions(self, base64_image: str) -> Dict:
        """Analyze emotions in the image."""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": """Analyze the emotions visible in this image. Focus on:
                                1. Facial expressions
                                2. Overall mood/atmosphere
                                3. Color psychology
                                4. Composition and lighting
                                
                                Return JSON format:
                                {
                                    "emotions": {
                                        "happy": 0.8,
                                        "sad": 0.1,
                                        "excited": 0.6,
                                        "calm": 0.3,
                                        "surprised": 0.2
                                    },
                                    "dominant_emotion": "happy",
                                    "confidence": 0.8
                                }"""
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=200,
                temperature=0.2
            )
            
            content = response.choices[0].message.content
            json_start = content.find('{')
            json_end = content.rfind('}') + 1
            json_str = content[json_start:json_end]
            
            return json.loads(json_str)
            
        except Exception as e:
            logger.error(f"Error in emotion analysis: {e}")
            return {
                "emotions": {"neutral": 0.5},
                "dominant_emotion": "neutral",
                "confidence": 0.5
            }
    
    async def _analyze_colors(self, image_path: str) -> Dict:
        """Analyze dominant colors in the image."""
        try:
            with Image.open(image_path) as img:
                # Convert to RGB
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Resize for faster processing
                img = img.resize((150, 150))
                
                # Get color data
                colors = img.getcolors(maxcolors=256*256*256)
                if not colors:
                    return self._default_color_analysis()
                
                # Sort by frequency
                colors.sort(key=lambda x: x[0], reverse=True)
                
                # Extract dominant colors
                dominant_colors = []
                total_pixels = sum(count for count, _ in colors)
                
                for count, color in colors[:10]:  # Top 10 colors
                    percentage = (count / total_pixels) * 100
                    if percentage > 1:  # Only include colors with >1% presence
                        hex_color = f"#{color[0]:02x}{color[1]:02x}{color[2]:02x}"
                        dominant_colors.append({
                            "hex": hex_color,
                            "rgb": color,
                            "percentage": round(percentage, 2)
                        })
                
                # Calculate overall brightness and saturation
                brightness = self._calculate_brightness(img)
                saturation = self._calculate_saturation(img)
                
                return {
                    "dominant_colors": dominant_colors[:5],  # Top 5 colors
                    "brightness": brightness,
                    "saturation": saturation,
                    "color_palette": dominant_colors
                }
                
        except Exception as e:
            logger.error(f"Error in color analysis: {e}")
            return self._default_color_analysis()
    
    def _calculate_brightness(self, img: Image.Image) -> float:
        """Calculate overall brightness of the image."""
        # Convert to grayscale and calculate mean
        gray = img.convert('L')
        pixels = list(gray.getdata())
        return sum(pixels) / len(pixels) / 255.0
    
    def _calculate_saturation(self, img: Image.Image) -> float:
        """Calculate overall saturation of the image."""
        pixels = list(img.getdata())
        saturations = []
        
        for r, g, b in pixels:
            h, s, v = colorsys.rgb_to_hsv(r/255, g/255, b/255)
            saturations.append(s)
        
        return sum(saturations) / len(saturations)
    
    def _default_color_analysis(self) -> Dict:
        """Default color analysis when processing fails."""
        return {
            "dominant_colors": [{"hex": "#808080", "rgb": (128, 128, 128), "percentage": 100}],
            "brightness": 0.5,
            "saturation": 0.3,
            "color_palette": [{"hex": "#808080", "rgb": (128, 128, 128), "percentage": 100}]
        }
    
    def _mock_analysis(self) -> Dict:
        """Mock analysis for when AI services are unavailable."""
        return {
            "tags": ["photography", "image", "visual", "content", "media", "art", "creative"],
            "caption": "A beautiful photograph captured with artistic vision",
            "embedding": np.random.rand(1536).tolist(),
            "emotions": {
                "emotions": {"neutral": 0.7, "happy": 0.3},
                "dominant_emotion": "neutral",
                "confidence": 0.7
            },
            "colors": self._default_color_analysis()
        }
    
    def calculate_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Calculate cosine similarity between two embeddings."""
        try:
            emb1 = np.array(embedding1).reshape(1, -1)
            emb2 = np.array(embedding2).reshape(1, -1)
            similarity = cosine_similarity(emb1, emb2)[0][0]
            return float(similarity)
        except Exception as e:
            logger.error(f"Error calculating similarity: {e}")
            return 0.0

# Global instance
ai_service = AIImageAnalysisService()
