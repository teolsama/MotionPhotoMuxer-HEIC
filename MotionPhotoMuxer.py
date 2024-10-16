import toml
import logging
import os
import shutil
import sys
import pyexiv2
import piexif
from os.path import exists, basename, isdir, join, splitext
from PIL import Image

problematic_files = []
processed_files = []

def validate_directory(dir):
    if not dir:
        logging.error("No directory path provided.")
        return False
    if not exists(dir):
        logging.error("Directory does not exist: {}".format(dir))
        return False
    if not isdir(dir):
        logging.error("Path is not a directory: {}".format(dir))
        return False
    return True

def validate_file(file_path):
    if not file_path:
        logging.error("No file path provided.")
        return False
    if not exists(file_path):
        logging.error("File does not exist: {}".format(file_path))
        return False
    return True

def convert_heic_to_jpeg(heic_path):
    """Converts a HEIC file to a JPEG file while copying the EXIF data."""
    logging.info("Converting HEIC file to JPEG: {}".format(heic_path))
    try:
        im = Image.open(heic_path)
        jpeg_path = splitext(heic_path)[0] + ".jpg"
        im.convert("RGB").save(jpeg_path, "JPEG")
        logging.info("HEIC file converted to JPEG: {}".format(jpeg_path))

        # Copy EXIF data from HEIC to JPEG
        exif_dict = piexif.load(heic_path)
        if exif_dict:
            exif_bytes = piexif.dump(exif_dict)
            piexif.insert(exif_bytes, jpeg_path)
            logging.info("EXIF data copied from HEIC to JPEG.")
        else:
            logging.warning("No EXIF data found in HEIC file.")

        processed_files.append(heic_path)
        return jpeg_path
    except Exception as e:
        logging.warning("Error converting HEIC file: {}: {}".format(heic_path, str(e)))
        problematic_files.append(heic_path)
        return None

def validate_media(photo_path, video_path):
    """Checks if the provided paths are valid."""
    if not validate_file(photo_path):
        logging.error("Invalid photo path.")
        return False
    if not validate_file(video_path):
        logging.error("Invalid video path.")
        return False
    if not photo_path.lower().endswith(('.jpg', '.jpeg')):
        logging.error("Photo isn't a JPEG: {}".format(photo_path))
        return False
    if not video_path.lower().endswith(('.mov', '.mp4')):
        logging.error("Video isn't a MOV or MP4: {}".format(video_path))
        return False
    return True

def merge_files(photo_path, video_path, output_path):
    """Merges the photo and video files together."""
    logging.info("Merging {} and {}.".format(photo_path, video_path))
    out_path = os.path.join(output_path, "{}".format(basename(photo_path)))
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "wb") as outfile, open(photo_path, "rb") as photo, open(video_path, "rb") as video:
        outfile.write(photo.read())
        outfile.write(video.read())
    logging.info("Merged photo and video.")
    processed_files.extend([photo_path, video_path])
    return out_path

def add_xmp_metadata(merged_file, offset):
    """Adds XMP metadata to the merged image."""
    metadata = pyexiv2.ImageMetadata(merged_file)
    logging.info("Reading existing metadata from file.")
    metadata.read()
    if len(metadata.xmp_keys) > 0:
        logging.warning("Found existing XMP keys. They *may* be affected after this process.")
    try:
        pyexiv2.xmp.register_namespace('http://ns.google.com/photos/1.0/camera/', 'GCamera')
    except KeyError:
        logging.warning("exiv2 detected that the GCamera namespace already exists.")
    metadata['Xmp.GCamera.MicroVideo'] = pyexiv2.XmpTag('Xmp.GCamera.MicroVideo', 1)
    metadata['Xmp.GCamera.MicroVideoVersion'] = pyexiv2.XmpTag('Xmp.GCamera.MicroVideoVersion', 1)
    metadata['Xmp.GCamera.MicroVideoOffset'] = pyexiv2.XmpTag('Xmp.GCamera.MicroVideoOffset', offset)
    metadata['Xmp.GCamera.MicroVideoPresentationTimestampUs'] = pyexiv2.XmpTag(
        'Xmp.GCamera.MicroVideoPresentationTimestampUs',
        1500000)  # in Apple Live Photos, the chosen photo is 1.5s after the start of the video
    metadata.write()

def convert(photo_path, video_path, output_path):
    """Performs the conversion process."""
    if not validate_media(photo_path, video_path):
        logging.error("Invalid photo or video path.")
        return
    merged = merge_files(photo_path, video_path, output_path)
    photo_filesize = os.path.getsize(photo_path)
    merged_filesize = os.path.getsize(merged)
    offset = merged_filesize - photo_filesize
    add_xmp_metadata(merged, offset)

def matching_video(photo_path, video_dir):
    """Finds a matching MOV/MP4 video file for a given photo."""
    base = os.path.splitext(basename(photo_path))[0]  # Get the base name of the photo without extension
    for root, dirs, files in os.walk(video_dir):
        for file in files:
            video_base, video_ext = os.path.splitext(file)
            if video_base == base and video_ext.lower() in ['.mov', '.mp4']:
                return os.path.join(root, file)
    return None

def unique_path(destination, filename):
    """Generate a unique file path to avoid overwriting existing files."""
    base, extension = os.path.splitext(filename)
    counter = 1
    new_filename = filename
    while os.path.exists(os.path.join(destination, new_filename)):
        new_filename = f"{base}({counter}){extension}"
        counter += 1
    return os.path.join(destination, new_filename)

paired_files = []  # New list to track files with matching video pairs
converted_files = []  # Track HEIC files that were converted but don't have a matching video

def process_directory(input_dir, output_dir, move_other_images, convert_all_heic, delete_converted):
    logging.info("다음 디렉토리에서 파일 처리 중: {}".format(input_dir))

    if not validate_directory(input_dir):
        logging.error("유효하지 않은 입력 디렉토리입니다.")
        sys.exit(1)

    # 출력 디렉토리가 존재하는지 확인
    if not exists(output_dir):
        os.makedirs(output_dir)
        logging.info(f"출력 디렉토리 생성됨: {output_dir}")

    matching_pairs = 0
    for root, dirs, files in os.walk(input_dir):
        for file in files:
            file_path = os.path.join(root, file)
            if file.lower().endswith('.heic'):
                # 모든 HEIC를 변환하거나 매칭되는 비디오가 있는 경우에만 HEIC 변환
                jpeg_path = None
                if convert_all_heic or matching_video(file_path, input_dir):
                    jpeg_path = convert_heic_to_jpeg(file_path)
                
                if jpeg_path:
                    video_path = matching_video(jpeg_path, input_dir)
                    if video_path:
                        # 매칭되는 비디오가 있는 경우에만 병합 및 삭제
                        convert(jpeg_path, video_path, output_dir)
                        matching_pairs += 1
                        # 매칭된 파일만 추적
                        paired_files.extend([file_path, jpeg_path, video_path])
                    else:
                        # 비디오가 없는 변환된 HEIC 파일 추적
                        converted_files.append(file_path)
                        # 매칭되는 비디오가 없고 사용자가 이동을 선택한 경우 HEIC를 other_files로 이동
                        if move_other_images:
                            move_to_other_files(file_path, output_dir)

                if delete_converted and not matching_video(file_path, input_dir):
                    try:
                        os.remove(file_path)
                        logging.info(f"비디오가 없는 변환된 HEIC 파일 삭제됨: {file_path}")
                    except Exception as e:
                        logging.warning(f"파일 삭제 실패 {file_path}: {str(e)}")

            elif file.lower().endswith(('.jpg', '.jpeg')):
                video_path = matching_video(file_path, input_dir)
                if video_path:
                    # 매칭되는 비디오가 있는 경우에만 JPEG 병합 및 삭제
                    convert(file_path, video_path, output_dir)
                    matching_pairs += 1
                    paired_files.extend([file_path, video_path])
                    if delete_converted:
                        delete_files([file_path, video_path])

    logging.info("변환 완료.")
    logging.info("HEIC/JPEG와 MOV/MP4 매칭 쌍 {} 개 발견.".format(matching_pairs))

    # 매칭되지 않는 파일을 'other_files' 폴더로 이동
    if move_other_images:
        other_files_dir = os.path.join(output_dir, "other_files")
        os.makedirs(other_files_dir, exist_ok=True)
        for root, dirs, files in os.walk(input_dir):
            for file in files:
                file_path = os.path.join(root, file)
                if file_path not in processed_files and file_path not in paired_files:
                    unique_file_path = unique_path(other_files_dir, basename(file_path))
                    shutil.move(file_path, unique_file_path)
                    logging.info(f"{file_path}를 {unique_file_path}로 이동함")

    logging.info("정리 완료.")
    
def move_to_other_files(file_path, output_dir):
    """HEIC 파일을 출력 디렉토리의 'other_files' 폴더로 이동."""
    other_files_dir = os.path.join(output_dir, "other_files")
    os.makedirs(other_files_dir, exist_ok=True)
    unique_file_path = unique_path(other_files_dir, basename(file_path))
    shutil.move(file_path, unique_file_path)
    logging.info(f"{file_path}를 {unique_file_path}로 이동함")


def delete_files(files):
    """파일 목록을 삭제."""
    for file in files:
        if exists(file):
            try:
                os.remove(file)
                logging.info(f"파일 삭제됨: {file}")
            except Exception as e:
                logging.warning(f"파일 삭제 실패 {file}: {str(e)}")

def load_config():
    """TOML 설정 파일에서 설정을 로드합니다."""
    config_path = 'config.toml'
    if not exists(config_path):
        logging.error(f"설정 파일을 찾을 수 없습니다: {config_path}")
        sys.exit(1)
    
    with open(config_path, 'r') as f:
        return toml.load(f)

def main():
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    logging.info("Apple Live Photos를 Google Motion Photos로 변환하는 프로그램에 오신 것을 환영합니다.")

    # TOML 설정 파일에서 설정 로드
    config = load_config()

    input_dir = config['directories']['input']
    output_dir = config['directories']['output']
    move_other_images = config['options']['move_other_images']
    convert_all_heic = config['options']['convert_all_heic']
    delete_converted = config['options']['delete_converted']

    if not validate_directory(input_dir):
        logging.error("유효하지 않은 디렉토리 경로입니다.")
        sys.exit(1)

    # 변환 수행
    process_directory(input_dir, output_dir, move_other_images, convert_all_heic, delete_converted)

    # 문제가 있는 파일 요약 출력
    if problematic_files:
        logging.warning("다음 파일들은 변환 중 오류가 발생했습니다:")
        for file_path in problematic_files:
            logging.warning(file_path)

        # 요약을 파일로 작성
        with open("problematic_files.txt", "w") as f:
            f.write("다음 파일들은 변환 중 오류가 발생했습니다:\n")
            for file_path in problematic_files:
                f.write(file_path + "\n")

    # 원본 파일 삭제 여부 확인
    delete_original = config['options']['delete_original']

    if delete_original:
        delete_files(paired_files)  # 매칭된 파일만 삭제
    else:
        logging.info("원본 HEIC 및 MOV/MP4 파일이 저장됩니다.")


if __name__ == '__main__':
    main()
