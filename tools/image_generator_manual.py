"""Manual image generator that logs prompt to a unique directory and waits for user to provide the image."""

import asyncio
import os
import glob
import uuid
import time
from typing import List

from interfaces import ImageOutput


class ImageGeneratorManual:
    """Manual image generator that pauses for human intervention.
    
    Creates a unique directory for each call, writes the prompt to prompt.txt,
    then waits for the user to place an image file (png/jpeg) in that directory.
    """

    def __init__(self, base_dir: str = ".working_dir/manual_image_jobs"):
        self.base_dir = base_dir
        os.makedirs(self.base_dir, exist_ok=True)

    async def generate_single_image(
        self,
        prompt: str,
        reference_image_paths: List[str] = None,
        **kwargs,
    ) -> ImageOutput:
        # Create unique job directory
        job_id = uuid.uuid4().hex[:12]
        job_dir = os.path.join(self.base_dir, job_id)
        os.makedirs(job_dir, exist_ok=True)

        # Write prompt to file
        prompt_path = os.path.join(job_dir, "prompt.txt")
        with open(prompt_path, "w", encoding="utf-8") as f:
            f.write(prompt)

        # Write reference image paths if any
        if reference_image_paths:
            refs_path = os.path.join(job_dir, "reference_images.txt")
            with open(refs_path, "w", encoding="utf-8") as f:
                for ref_path in reference_image_paths:
                    f.write(ref_path + "\n")

        print(f"\n{'='*60}")
        print(f"MANUAL IMAGE GENERATION REQUIRED")
        print(f"Job directory: {job_dir}")
        print(f"Prompt saved to: {prompt_path}")
        print(f"Waiting for image file (image.png or image.jpeg)...")
        print(f"{'='*60}\n")

        # Wait for image file to appear
        image_path = await self._wait_for_image(job_dir)

        return ImageOutput(fmt="pil", ext=os.path.splitext(image_path)[1].lstrip("."), data=self._load_pil(image_path))

    async def _wait_for_image(self, job_dir: str, poll_interval: float = 2.0) -> str:
        """Poll the job directory for an image file."""
        patterns = ["image.png", "image.jpeg", "image.jpg"]
        
        while True:
            for pattern in patterns:
                path = os.path.join(job_dir, pattern)
                if os.path.exists(path):
                    print(f"Image found: {path}")
                    return path
            await asyncio.sleep(poll_interval)

    def _load_pil(self, path: str):
        """Load image as PIL Image."""
        from PIL import Image
        return Image.open(path)
