import cv2
import numpy as np
from moviepy.editor import *
from Components.Speaker import detect_faces_and_speakers, Frames

global Fps

def crop_to_vertical(input_video_path, output_video_path):
    detect_faces_and_speakers(input_video_path, "DecOut.mp4")
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    cap = cv2.VideoCapture(input_video_path, cv2.CAP_FFMPEG)
    if not cap.isOpened():
        print("Error: Could not open video.")
        return

    original_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    original_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    vertical_height = original_height
    vertical_width = int(vertical_height * 9 / 16)

    if original_width < vertical_width:
        print("Error: Original video width is less than the desired vertical width.")
        return

    x_start = (original_width - vertical_width) // 2
    x_end = x_start + vertical_width
    half_width = vertical_width // 2

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_video_path, fourcc, fps, (vertical_width, vertical_height))
    global Fps
    Fps = fps

    count = 0
    for _ in range(total_frames):
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read frame.")
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        # Valores predeterminados para el recorte
        x, y, w, h = x_start, 0, vertical_width, vertical_height

        try:
            if len(faces) > 0:
                # Si se detectan caras, usar la primera o ajustar según `Frames`
                for (x1, y1, w1, h1) in faces:
                    center = x1 + w1 // 2
                    if Frames and count < len(Frames):
                        X, Y, W, H = Frames[count]
                        if X < center < X + W:
                            x, y, w, h = x1, y1, w1, h1
                            break

            elif Frames and count < len(Frames):
                x, y, w, h = Frames[count]

            centerX = x + (w // 2)
            if count > 0 and abs(centerX - (x_start + half_width)) > 1:
                x_start = max(0, min(original_width - vertical_width, centerX - half_width))
                x_end = x_start + vertical_width

        except Exception as e:
            print(f"Error processing frame {count}: {e}")

        # Recortar el cuadro
        cropped_frame = frame[:, x_start:x_end]

        # Asegurar dimensiones consistentes
        if cropped_frame.shape[1] != vertical_width:
            print("Inconsistent frame dimensions. Resetting crop.")
            x_start = (original_width - vertical_width) // 2
            x_end = x_start + vertical_width
            cropped_frame = frame[:, x_start:x_end]

        out.write(cropped_frame)
        count += 1

    cap.release()
    out.release()
    print("Cropping complete. The video has been saved to", output_video_path)

def combine_videos(video_with_audio, video_without_audio, output_filename):
    try:
        # Cargar clips de video
        clip_with_audio = VideoFileClip(video_with_audio)
        clip_without_audio = VideoFileClip(video_without_audio)

        # Agregar audio del clip original
        audio = clip_with_audio.audio
        combined_clip = clip_without_audio.set_audio(audio)

        global Fps
        combined_clip.write_videofile(output_filename, codec='libx264', audio_codec='aac', fps=Fps, preset='medium', bitrate='3000k')
        print(f"Combined video saved successfully as {output_filename}")
    except Exception as e:
        print(f"Error combining video and audio: {str(e)}")

if __name__ == "__main__":
    input_video_path = r'Out.mp4'
    output_video_path = 'Croped_output_video.mp4'
    final_video_path = 'final_video_with_audio.mp4'

    detect_faces_and_speakers(input_video_path, "DecOut.mp4")
    crop_to_vertical(input_video_path, output_video_path)
    combine_videos(input_video_path, output_video_path, final_video_path)
