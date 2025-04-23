#!/usr/bin/env python

from plumbum import cli, local, FG, BG # See https://plumbum.readthedocs.io/en/latest/cli.html
import os
import glob
import sys
from dionisos_lib.notifier import Notifier
from dionisos_lib.file_custom import find_free_path

class ConvertMovie(cli.Application):
    """
    Convert files found in the current directory to target_ext extension.
    Use ffmpeg for the conversion
    """
    origin_exts = cli.SwitchAttr(["e", "extensions"], str, default=None, help="List of extensions(separated by commas) of the files to convert (incompatible with -i)")
    origin_filepath = cli.SwitchAttr(["i", "filepath"], str, default=None, help="The file to convert (incompatible with -e)")
    verbose = cli.Flag(["v", "verbose"], help="If given, I will be very talkative")
    delete = cli.Flag(["d", "delete"], help="Delete file after conversion (with trash, 'trash-cli' package needed)")
    recursive = cli.Flag(["r", "recursive"], help="Go through directory recursively")
    mock = cli.Flag(["m", "mock"], help="Print what it would done but do nothing (override verbose to true)")
    tv_compatibility = cli.Flag(["t", "tv_compatibility"], help="convert only what is incompatible with tv")
    # extract_audio = cli.Flag(["a", "extract_audio"], help="extract the audio stream")

    def notify(self, msg, power=None):
        self._notifier.notify(msg, power)
        if power == Notifier.ERROR:
            sys.exit(1)

    def get_path_list(self):
        if self.origin_filepath is not None:
            if not os.path.isfile(self.origin_filepath):
                self.notify(f"The file \"{self.origin_filepath}\" doesn’t exist", Notifier.ERROR)
            path_list = [self.origin_filepath]
        else:
            if self.recursive:
                path_list = glob.iglob("./**/*.*", recursive=True)
            else:
                path_list = glob.iglob("./*.*", recursive=False)

            path_list = [path for path in path_list if os.path.splitext(path)[1][1:] in self.origin_exts]


        self.notify(str(path_list))

        return path_list

    def main(self, target_ext="mp4"):

        if self.origin_exts and self.origin_filepath:
            print("-e and -i options mutually exclusives")
            sys.exit(1)

        if not self.origin_exts and not self.origin_filepath:
            print("-e xor -i options required")
            sys.exit(1)

        if self.origin_exts is not None:
            self.origin_exts = self.origin_exts.split(",")

        if self.mock:
            self.verbose = True

        if self.verbose:
            self._notifier = Notifier(True)
            self.notify("verbose = " + str(self.verbose))
            self.notify("delete = " + str(self.delete))
            self.notify("recursive = " + str(self.recursive))
            self.notify("mock = " + str(self.mock))
            self.notify("tv_compatibility = " + str(self.tv_compatibility))
            if self.origin_exts is not None:
                self.notify("origin_exts = " + str(self.origin_exts))
            else:
                self.notify("origin_filepath = " + str(self.origin_filepath))

            self.notify("target_ext = " + str(target_ext))
        else:
            self._notifier = Notifier(False)

        self.ffmpeg = local["ffmpeg"]
        self.trash = local["trash"]
        self.mv = local["mv"]
        self.mediainfo = local["mediainfo"]

        path_list = self.get_path_list()

        for path in path_list:
            self.convert_file(path, target_ext)

    def get_convert_cmd(self, path, target_ext):
        basepath, extension = os.path.splitext(path)

        new_path = find_free_path(basepath, target_ext)

        if self.tv_compatibility:
            video_comp = self.is_video_compatible(path)
            audio_comp = self.is_audio_compatible(path)
            resolution_comp = self.is_resolution_compatible(path)
            fps_comp = self.is_fps_compatible(path)


            self.notify(f"file : {path}")
            self.notify("video codec : " + self.get_video_codec(path) + " compatibility → " + str(video_comp))
            self.notify("audio codec : " + self.get_audio_codec(path) + " compatibility → " + str(audio_comp))
            self.notify("resolution : " + str(self.get_resolution(path)) + " compatibility → " + str(resolution_comp))
            self.notify("fps : " + str(self.get_fps(path)) + " compatibility → " + str(fps_comp))

            if video_comp and audio_comp and resolution_comp and fps_comp and extension in [".mp4", ".mkv"]:
                self.notify("movie already in correct format")
                return (None, f"{path}")

            if video_comp and resolution_comp and fps_comp:
                video_codec = "copy"
            else:
                video_codec = "libx264"

            if audio_comp:
                audio_codec = "copy"
            else:
                audio_codec = "mp3"

            # ffmpeg -i path -c:v libx264 -level:v 4.0 -preset veryfast -c:a mp3 new_path
            args_list = ["-i", path, "-c:v", video_codec]

            # if not level_comp:
            #     args_list += ["-level:v", "4.0"]

            if not fps_comp:
                args_list += ["-r", "30"]

            if not resolution_comp:
                args_list += ["-vf", "scale=1920:1080"]

            args_list += ["-preset", "veryfast", "-c:a", audio_codec, f"{new_path}"]


            cmd = self.ffmpeg[args_list]
        else:
            # cmd = self.ffmpeg["-i", path, "-map", "0", "-dn", "-c:v", "libx264", "-preset", "veryfast", "-c:a", "mp3", f"{new_path}"]
            cmd = self.ffmpeg["-fflags", "+genpts", "-i", path, "-map", "0", "-dn", "-c", "copy", f"{new_path}"]

        return (cmd, new_path)

    def get_convert_subtile_cmd(self, basepath, new_basepath):

        if os.path.exists(f"{new_basepath}.srt"):
            self.notify("subtitle already here")
            return None

        possible_exts = ["vtt", "srt"]
        possible_langs = ["fr", "en"]

        possible_path = [f"{basepath}.{lang}.{ext}" for lang in possible_langs for ext in possible_exts] + [f"{basepath}.{ext}" for ext in possible_exts]

        i = 0
        while i < len(possible_path) and not os.path.isfile(possible_path[i]):
            i += 1

        if i >= len(possible_path):
            self.notify("no subtitle found")
            return None

        return self.ffmpeg["-i", f"{possible_path[i]}", f"{new_basepath}.srt"]

    def convert_file(self, path, target_ext):

        convert_cmd, new_path = self.get_convert_cmd(path, target_ext)

        if convert_cmd is not None:
            self.notify(str(convert_cmd))
            if not self.mock:
                convert_cmd & FG

            if self.delete:
                same_ext = os.path.splitext(path)[1] == f".{target_ext}"
                self.notify(f"trash '{path}'")
                if same_ext:
                    self.notify(f"mv '{new_path}' '{path}'")
                if not self.mock:
                    self.trash(path)
                    if same_ext:
                        self.mv(f'{new_path}', f'{path}')

        basepath, new_basepath = os.path.splitext(path)[0], os.path.splitext(new_path)[0]
        convert_subtile_cmd = self.get_convert_subtile_cmd(basepath, new_basepath)

        if convert_subtile_cmd is not None:
            self.notify(str(convert_subtile_cmd))
            if not self.mock:
                convert_subtile_cmd & FG

    def get_video_codec(self, path):
        cmd = self.mediainfo["--inform=Video;%CodecID%", path]
        result = cmd()

        return result.strip()

    def get_audio_codec(self, path):
        cmd = self.mediainfo["--inform=Audio;%CodecID%", path]
        result = cmd()

        return result.strip()

    def get_resolution(self, path):
        cmd = self.mediainfo["--Inform=Video;%Width% %Height%", path]
        result = cmd()

        return result.strip().split()

    def get_fps(self, path):
        cmd = self.mediainfo["--Inform=Video;%FrameRate%", path]
        result = cmd()

        return result.strip()

    def is_fps_compatible(self, path):
        fps = int(float(self.get_fps(path)))
        width = int(self.get_resolution(path)[0])

        if fps > 60 or (width >= 1920 and fps > 30):
            return False

        return True

    def is_video_compatible(self, path):
        video_codec = self.get_video_codec(path)
        if video_codec in ["avc1", "V_MPEG4/ISO/AVC"]:
            return True

        if video_codec in ["V_VP9", "vp09", "hvc1", "wma", ""]:
            return False

        self.notify(f"The compatibility of the video codec {video_codec} is unknow (file : '{path}')", Notifier.ERROR)


    def is_audio_compatible(self, path):
        audio_codec = self.get_audio_codec(path)
        if audio_codec in ["mp4a-40-2", "A_AC3", "mp4a-6B"]:
            return True

        if audio_codec in ["A_AAC-2", "A_OPUS", "Opus", "161"]:
            return False

        self.notify(f"The compatibility of the audio codec {audio_codec} is unknow", Notifier.ERROR)

    def is_resolution_compatible(self, path):
        width, height = self.get_resolution(path)
        width, height = int(width), int(height)

        if width > 1920 or height > 1080:
            return False

        return True

if __name__ == "__main__":
    ConvertMovie.run()
