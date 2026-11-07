"""Manual video generator that logs prompt to a unique directory and waits for user to provide the video."""

import asyncio
import os
import uuid
from typing import List

from interfaces import VideoOutput


class VideoGeneratorManual:
    """Manual video generator that pauses for human intervention.
    
    Creates a unique directory for each call, writes the prompt to prompt.txt,
    then waits for the user to place a video file (mp4) in that directory.
    """

    def __init__(self, base_dir: str = ".working_dir/manual_video_jobs"):
        self.base_dir = base_dir
        os.makedirs(self.base_dir, exist_ok=True)

    async def generate_single_video(
        self,
        prompt: str,
        reference_image_paths: List[str] = None,
        **kwargs,
    ) -> VideoOutput:
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
        print(f"MANUAL VIDEO GENERATION REQUIRED")
        print(f"Job directory: {job_dir}")
        print(f"Prompt saved to: {prompt_path}")
        print(f"Waiting for video file (video.mp4)...")
        print(f"{'='*60}\n")

        # Wait for video file to appear
        video_path = await self._wait_for_video(job_dir)

        return VideoOutput(fmt="bytes", ext="mp4", data=self._read_video(video_path))

    async def _wait_for_video(self, job_dir: str, poll_interval: float = 2.0) -> str:
        """Poll the job directory for a video file."""
        patterns = ["video.mp4", "video.mov", "video.webm"]
        
        while True:
            for pattern in patterns:
                path = os.path.join(job_dir, pattern)
                if os.path.exists(path):
                    print(f"Video found: {path}")
                    return path
            await asyncio.sleep(poll_interval)

    def _read_video(self, path: str) -> bytes:
        """Read video file as bytes."""
        with open(path, "rb") as f:
            return f.read()
