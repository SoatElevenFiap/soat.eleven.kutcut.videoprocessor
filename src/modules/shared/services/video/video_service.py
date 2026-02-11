import io

import av

MAX_DURATION_SECONDS = 604_800  # 7 dias; evita MemoryError se metadados vierem em unidade errada
MAX_SNAPSHOTS = 5000  # limite de thumbnails por vídeo


class VideoService:
    @staticmethod
    def get_video_duration_seconds(data: bytes) -> int:
        with av.open(io.BytesIO(data)) as container:
            stream = container.streams.video[0]
            if stream.duration is not None and stream.time_base is not None:
                secs = int(float(stream.duration * stream.time_base))
                return min(secs, MAX_DURATION_SECONDS)
            if container.duration is not None:
                secs = int(float(container.duration * av.time_base))
                return min(secs, MAX_DURATION_SECONDS)
            return 0

    @staticmethod
    def extract_frames_as_jpeg_bytes(
        data: bytes,
        duration_seconds: int,
        interval_seconds: int = 15,
        jpeg_quality: int = 85,
    ) -> list[tuple[str, bytes]]:
        """Extrai um frame a cada interval_seconds em um único passe (sem seek)."""
        result: list[tuple[str, bytes]] = []
        duration_capped = min(duration_seconds, MAX_DURATION_SECONDS)
        n = min(
            (duration_capped // interval_seconds) + 1,
            MAX_SNAPSHOTS,
        )
        targets = [i * interval_seconds for i in range(n)]
        if not targets:
            return result
        next_i = 0
        with av.open(io.BytesIO(data)) as container:
            stream = container.streams.video[0]
            for frame in container.decode(stream):
                if next_i >= len(targets):
                    break
                t_sec = float(frame.time) if frame.time is not None else 0.0
                if t_sec < targets[next_i]:
                    continue
                while next_i < len(targets) and t_sec >= targets[next_i]:
                    img = frame.to_image()
                    buf = io.BytesIO()
                    img.save(buf, format="JPEG", quality=jpeg_quality)
                    result.append(
                        (f"snapshot_{targets[next_i]:04d}s.jpg", buf.getvalue())
                    )
                    next_i += 1
        return result
