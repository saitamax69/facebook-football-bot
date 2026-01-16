# ... imports ...
# Add this import at the top
from .image_generator import create_pro_image

# ... inside class ImageHandler ...

    def _get_placeholder_image(self, headline_context: str = "Football News") -> Tuple[str, str]:
        """
        Generate a professional graphic when APIs are unavailable.
        """
        logger.warning("Using Pro Image Generator fallback")
        try:
            # Generate a nice graphic with the actual headline
            image_path = create_pro_image(headline_context, "Global Score Updates")
            return (image_path, "Generated Graphic")
            
        except Exception as e:
            logger.error(f"Image generation failed: {e}")
            # Super minimal fallback if even the generator fails
            return self._create_basic_fallback()

    def fetch(self, news_headline: str = None) -> Tuple[str, str]:
        """
        Fetch a football image with automatic fallback.
        Pass news_headline to generate context-aware graphics.
        """
        image_url = None
        credit = None
        
        # 1. Try Unsplash (Only if KEY exists)
        if self.unsplash_key:
            try:
                result = self._fetch_from_unsplash()
                if result:
                    return result
            except Exception:
                pass
        
        # 2. Try Pexels (Only if KEY exists)
        if self.pexels_key:
            try:
                result = self._fetch_from_pexels()
                if result:
                    return result
            except Exception:
                pass
        
        # 3. Fallback to Pro Generator
        # We pass the headline if available, otherwise generic
        context = news_headline if news_headline else "Daily Football Update"
        return self._get_placeholder_image(context)

# Update the main function signature to accept headline
def get_football_image(headline: str = None) -> Tuple[str, str]:
    handler = ImageHandler()
    return handler.fetch(headline)
