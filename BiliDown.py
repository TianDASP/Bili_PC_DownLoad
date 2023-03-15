import os
import shutil
import subprocess

def fix_m4s(target_path: str, output_path: str, bufsize: int = 256*1024*1024) -> None:
    assert bufsize > 0
    with open(target_path, 'rb') as target_file:
        header = target_file.read(32)
        new_header = header.replace(b'000000000', b'')
        new_header = new_header.replace(b'$', b' ')
        new_header = new_header.replace(b'avc1', b'')
        with open(output_path, 'wb') as output_file:
            output_file.write(new_header)
            i = target_file.read(bufsize)
            while i:
                output_file.write(i)
                i = target_file.read(bufsize)


def merge_m4s(video_m4s_file, audio_m4s_file, output_file):
    """
    合并视频和音频的m4s文件
    :param video_m4s_file: 视频m4s文件路径
    :param audio_m4s_file: 音频m4s文件路径
    :param output_file: 合并后的文件路径
    """
    cmd = f"ffmpeg -i {video_m4s_file} -i {audio_m4s_file} -c:v copy -c:a copy -map 0:v:0 -map 1:a:0 {output_file}"
    subprocess.call(cmd, shell=True)


def process_folder(folder_path, output_folder_path):
    """
    处理文件夹中的m4s文件
    :param folder_path: 文件夹路径
    """
    video_m4s_path = None
    audio_m4s_path = None
    temp = None
    for file in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file)
        if os.path.isfile(file_path) and file_path.endswith(".m4s"):
            if video_m4s_path is None:
                video_m4s_path = file_path
            elif audio_m4s_path is None:
                audio_m4s_path = file_path
            else:
                break  # 已经获取了需要的两个m4s文件

    if video_m4s_path is not None and audio_m4s_path is not None:
        video_size = os.path.getsize(video_m4s_path)
        audio_size = os.path.getsize(audio_m4s_path)
        if video_size < audio_size: 
            temp = video_m4s_path
            video_m4s_path = audio_m4s_path
            audio_m4s_path = temp

        output_folder_path = os.path.abspath("../biliOutPut")
        os.makedirs(output_folder_path, exist_ok=True)
        output_file_path = os.path.join(output_folder_path, os.path.basename(folder_path) + ".mp4")
        video_output_path = os.path.join(output_folder_path, "video.m4s")
        audio_output_path = os.path.join(output_folder_path, "audio.m4s")

        if video_size >= 5 * 1024 * 1024 :  # 文件大小大于等于5MB
            fix_m4s(video_m4s_path, video_output_path)
            fix_m4s(audio_m4s_path, audio_output_path)

            merge_m4s(video_output_path, audio_output_path, output_file_path)

            

def main():
    input_dir = os.getcwd() # 获取当前脚本所在目录
    output_dir = os.path.abspath('../biliOutPut')

    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    folders = [f for f in os.listdir(input_dir) if os.path.isdir(f) and f[0].isdigit()]
    
    for folder in folders:
        folder_path = os.path.join(input_dir, folder)
        try:
            process_folder(folder_path, output_dir)
        except Exception as e:
            print(f"Failed to process folder {folder}: {str(e)}")
    # 删除最后未被覆盖的两个文件
    os.remove("../biliOutPut/video.m4s")
    os.remove("../biliOutPut/audio.m4s")

    
if __name__ == '__main__':
    main()