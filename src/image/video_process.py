import os
import sys
from pathlib import Path
from typing import Optional, List

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import cv2
import numpy as np
from loguru import logger
from run import constants
from run.constants import output_video_fps, output_video_height, output_video_width
from utils.time_utils import id_generate_time


@logger.catch
def generate_video_from_images(images_input_path: str, video_out_path: str) -> Optional[str]:
    """Generate video from a directory of images
    
    Args:
        images_input_path: Input directory containing images
        video_out_path: Output directory for video
        
    Returns:
        str: Path to generated video file, or None if failed
    """
    # Find valid image files
    image_paths = []
    for root, _, files in os.walk(images_input_path):
        for file in files:
            # Skip invalid images
            if any(x in file or x in root for x in ["square", "custom", "error_images", "small_images", "gif_unzip"]):
                logger.warning(f"Skipping invalid image: {file}")
                continue
                
            if file.endswith(('.jpg', '.png')):
                image_paths.append(os.path.join(root, file))
                
    if not image_paths:
        logger.warning("No valid images found")
        return None
        
    logger.debug(f"Found {len(image_paths)} valid images in {constants.data_path}")

    # Get dimensions from first valid image
    width = height = 0
    for img_path in image_paths:
        try:
            img = cv2.imread(img_path)
            if img is not None:
                height, width = img.shape[:2]
                break
        except Exception as e:
            logger.error(f"Failed to read image {img_path}: {e}")
            continue
            
    if not width or not height:
        logger.error("Could not determine video dimensions")
        return None

    # Create output directory
    os.makedirs(video_out_path, exist_ok=True)

    # Initialize video writer
    video_path = os.path.join(video_out_path, f"{id_generate_time()}test.mp4")
    fourcc = cv2.VideoWriter_fourcc(*'MJPG')
    video = cv2.VideoWriter(video_path, fourcc, int(output_video_fps), (width, height))

    if not video.isOpened():
        logger.error("Failed to create video writer")
        return None

    try:
        # Write frames
        for i, img_path in enumerate(image_paths, 1):
            img = cv2.imread(img_path)
            if img is None:
                logger.error(f"Failed to read image: {img_path}")
                continue
                
            resized = cv2.resize(img, (width, height))
            video.write(resized)
            
            if i % 10 == 0:
                progress = (i / len(image_paths)) * 100
                logger.info(f"Export progress: {i}/{len(image_paths)} ({progress:.1f}%)")
                
    finally:
        video.release()
        
    return video_path


@logger.catch
def convert_image(images_input_path: str, target_dir: str) -> bool:
    """Convert images to uniform size
    
    Args:
        images_input_path: Input directory containing images
        target_dir: Output directory for converted images
        
    Returns:
        bool: True if successful, False otherwise
    """
    os.makedirs(target_dir, exist_ok=True)

    # Find valid images
    image_paths = []
    for root, _, files in os.walk(images_input_path):
        for file in files:
            if "result" in file:
                continue
            if file.endswith(('.jpg', '.png')):
                image_paths.append(os.path.join(root, file))

    if not image_paths:
        logger.warning("No images found to convert")
        return False
        
    logger.debug(f"Found {len(image_paths)} images to convert")

    # Process each image
    success = True
    for img_path in image_paths:
        if not image_fill_black(target_dir, img_path):
            success = False
            
    return success


@logger.catch
def image_fill_black(target_dir: str, image_path: str) -> bool:
    """Resize and pad image with black borders to target size
    
    Args:
        target_dir: Output directory
        image_path: Input image path
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError("Failed to read image")
            
        height, width = img.shape[:2]
        target_size = (output_video_width, output_video_height)

        # Calculate borders and gaps
        border_w = max(0, (target_size[0] - width) // 2)
        border_h = max(0, (target_size[1] - height) // 2)
        
        gap_w = output_video_width - (border_w * 2) - width
        gap_h = output_video_height - (border_h * 2) - height

        # Resize if too large
        if width > target_size[0] or height > target_size[1]:
            img = cv2.resize(img, target_size, interpolation=cv2.INTER_LINEAR)
            
        # Pad if too small
        elif width < target_size[0] or height < target_size[1]:
            img = cv2.copyMakeBorder(
                img, 
                border_h, border_h + gap_h,
                border_w, border_w + gap_w,
                cv2.BORDER_CONSTANT,
                value=[0, 0, 0]
            )

        # Save result
        output_path = os.path.join(target_dir, f"result_{os.path.basename(image_path)}")
        cv2.imwrite(output_path, img)
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to process {image_path}: {e}")
        return False


@logger.catch
def process_images_thread(self):
    """Process images to video in a thread"""
    # Convert images to uniform size
    if not convert_image(constants.data_path, os.path.join(constants.data_path, "img_result")):
        logger.error("Image conversion failed")
        return

    # Generate video from converted images
    video_path = generate_video_from_images(
        os.path.join(constants.data_path, "img_result"),
        os.path.join(constants.data_path, "video")
    )
    
    if video_path:
        logger.success(f"Video generated successfully: {video_path}")
        self.success_tips("图片处理操作")
        
    constants.process_image_flag = False


@logger.catch
def play_video_process(self):
    """Play selected video with controls"""
    if not self.listWidget_4.selectedItems():
        logger.warning("No video selected")
        return
        
    video_path = self.listWidget_4.selectedItems()[0].text()
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        logger.error(f"Failed to open video: {video_path}")
        return

    cv2.namedWindow('Video', cv2.WINDOW_NORMAL)
    
    play_speed = 1.0
    last_time = 0
    paused = False

    try:
        while True:
            if not paused:
                ret, frame = cap.read()
                if not ret:
                    break
                    
                current_time = int(cap.get(cv2.CAP_PROP_POS_MSEC)) // 1000
                
                # Add overlay text
                cv2.putText(
                    frame,
                    f"Time: {current_time}s Speed: {play_speed:.1f}x", 
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 255, 0),
                    2
                )
                
                cv2.imshow(f'Video: {video_path}', frame)

            # Handle keyboard controls
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('p'):
                paused = not paused
            elif key == ord('f'):
                cap.set(cv2.CAP_PROP_POS_MSEC, (current_time + 1) * 1000)
            elif key == ord('+'):
                play_speed = min(play_speed + 0.1, 2.0)
            elif key == ord('-'):
                play_speed = max(play_speed - 0.1, 0.1)
                
    finally:
        cap.release()
        cv2.destroyAllWindows()


@logger.catch
def video_process(video_path: str, output_directory: str) -> None:
    """Extract frames from video at regular intervals
    
    Args:
        video_path: Input video file path
        output_directory: Output directory for frames
    """
    os.makedirs(output_directory, exist_ok=True)
    
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        logger.error("Failed to open video")
        return

    try:
        frame_interval = 60
        frame_count = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
                
            frame_count += 1
            if frame_count % frame_interval == 0:
                frame_num = frame_count // frame_interval
                output_path = os.path.join(output_directory, f'frame_{frame_num}.jpg')
                cv2.imwrite(output_path, frame)
                logger.debug(f"Saved frame {frame_num}")
                
    finally:
        cap.release()
