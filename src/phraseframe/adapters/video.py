"""Pillow frame composition and MoviePy encoding."""

from bisect import bisect_right
from pathlib import Path

import numpy as np
from moviepy import VideoClip
from numpy.typing import NDArray
from PIL import Image, ImageDraw, ImageFont

from phraseframe.core.models import TimedFrame, Timeline


class PillowMoviePyRenderer:
    """Render a timeline as a silent, broadly compatible H.264 MP4."""

    width = 1280
    height = 720
    fps = 24

    def _font(self, size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
        try:
            return ImageFont.truetype("DejaVuSans.ttf", size)
        except OSError:
            return ImageFont.load_default(size=size)

    def _image_for(self, frame: TimedFrame, total: int) -> NDArray[np.uint8]:
        image = Image.new("RGB", (self.width, self.height), "#0b1020")
        draw = ImageDraw.Draw(image)
        label_font = self._font(24)

        font_size = 72
        font = self._font(font_size)
        bounds = draw.textbbox((0, 0), frame.text, font=font)
        while bounds[2] - bounds[0] > self.width - 160 and font_size > 24:
            font_size -= 2
            font = self._font(font_size)
            bounds = draw.textbbox((0, 0), frame.text, font=font)
        text_width = bounds[2] - bounds[0]
        text_height = bounds[3] - bounds[1]
        draw.text(
            ((self.width - text_width) / 2, (self.height - text_height) / 2 - 20),
            frame.text,
            font=font,
            fill="#f8fafc",
        )

        progress = (frame.index + 1) / max(total, 1)
        draw.rounded_rectangle((80, 650, 1200, 658), radius=4, fill="#25304a")
        draw.rounded_rectangle(
            (80, 650, 80 + round(1120 * progress), 658),
            radius=4,
            fill="#78dcca",
        )
        draw.text((80, 674), "PhraseFrame", font=label_font, fill="#94a3b8")
        draw.text(
            (1200, 674),
            f"{frame.index + 1} / {total}",
            font=label_font,
            fill="#94a3b8",
            anchor="ra",
        )
        return np.asarray(image, dtype=np.uint8)

    def render(self, timeline: Timeline, output_path: Path) -> Path:
        if not timeline.frames:
            raise ValueError("Cannot render an empty timeline.")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        starts = [frame.starts_at_ms / 1000 for frame in timeline.frames]
        cached_index = -1
        cached_image: NDArray[np.uint8] | None = None

        def frame_function(seconds: float) -> NDArray[np.uint8]:
            nonlocal cached_index, cached_image
            index = min(bisect_right(starts, seconds) - 1, len(timeline.frames) - 1)
            index = max(0, index)
            if index != cached_index or cached_image is None:
                cached_image = self._image_for(timeline.frames[index], len(timeline.frames))
                cached_index = index
            return cached_image

        clip = VideoClip(
            frame_function=frame_function,
            duration=max(timeline.duration_ms / 1000, 0.1),
        )
        try:
            clip.write_videofile(
                str(output_path),
                fps=self.fps,
                codec="libx264",
                audio=False,
                logger=None,
                pixel_format="yuv420p",
            )
        finally:
            clip.close()
        return output_path
