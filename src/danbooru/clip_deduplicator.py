#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from pathlib import Path
import shutil
import numpy as np

from src.core.recognition.clip_embedder import CLIPEmbedder


class CLIPDeduplicator:

    def __init__(
        self,
        model_name="ViT-L/14",
        threshold=0.95
    ):
        self.threshold = threshold

        self.embedder = CLIPEmbedder(
            model_name=model_name,
            use_huggingface=True
        )

        self.embedder.initialize()

    def process(
        self,
        input_dir,
        output_dir
    ):

        input_dir = Path(input_dir)
        output_dir = Path(output_dir)

        output_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        images = []

        for ext in ["*.jpg", "*.jpeg", "*.png", "*.webp"]:
            images.extend(input_dir.glob(ext))

        if len(images) == 0:
            return

        features = self.embedder.embed_images(
            [str(x) for x in images]
        )

        features = np.asarray(features)

        features /= (
            np.linalg.norm(
                features,
                axis=1,
                keepdims=True
            )
            + 1e-12
        )

        keep = []

        for idx, feat in enumerate(features):

            duplicated = False

            for k in keep:

                sim = np.dot(
                    feat,
                    features[k]
                )

                if sim > self.threshold:
                    duplicated = True
                    break

            if not duplicated:
                keep.append(idx)

        for idx in keep:

            src = images[idx]

            dst = output_dir / src.name

            shutil.copy2(src, dst)

        print(
            f"去重完成 "
            f"{len(images)} -> {len(keep)}"
        )