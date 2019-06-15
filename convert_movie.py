#!/bin/python

from plumbum import cli, local, FG, BG # See https://plumbum.readthedocs.io/en/latest/cli.html
import os
import glob
from dionisos_lib.notifier import Notifier

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
    _notifier = Notifier()

    def notify(self, msg, power=None):
        self._notifier.notify(msg, power)
        if power == Notifier.ERROR:
            exit(1)

    def main(self, target_ext="mp4"):
        if self.origin_exts and self.origin_filepath:
            self.notify("-e and -i options mutually exclusives", Notifier.ERROR)

        if not self.origin_exts and not self.origin_filepath:
            self.notify("-e xor -i options required", Notifier.ERROR)

        if self.origin_exts is not None:
            self.origin_exts = self.origin_exts.split(",")

        if self.mock:
            self.verbose = True

        if self.verbose:
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

        ffmpeg = local["ffmpeg"]
        trash = local["trash"]
        mv = local["mv"]

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

        if self.verbose:
            self.notify(str(path_list))

        for path in path_list:
            basename = os.path.splitext(path)[0]
            extension = os.path.splitext(path)[1]
            to_move = False

            if path == f"{basename}.{target_ext}":
                basename_old = basename
                basename = basename+"(save)"
                to_move = True

            if self.tv_compatibility:
                video_comp = self.is_video_compatible(path)
                audio_comp = self.is_audio_compatible(path)

                if self.verbose:
                    self.notify(f"file : {path}")
                    self.notify("video codec : " + self.get_video_codec(path) + " compatibility → " + str(video_comp))
                    self.notify("audio codec : " + self.get_audio_codec(path) + " compatibility → " + str(audio_comp))

                if video_comp and audio_comp and extension in [".mp4", ".mkv"]:
                    if self.verbose:
                        self.notify("do nothing")
                    continue

                if video_comp:
                    video_codec = "copy"
                else:
                    video_codec = "libx264"

                if audio_comp:
                    audio_codec = "copy"
                else:
                    audio_codec = "mp3"

                cmd = ffmpeg["-i", path, "-c:v", video_codec, "-preset", "veryfast", "-c:a", audio_codec, f"{basename}.{target_ext}"]
            else:
                cmd = ffmpeg["-i", path, "-c:v", "libx264", "-preset", "veryfast", "-c:a", "mp3", f"{basename}.{target_ext}"]

            if self.verbose:
                self.notify(str(cmd))
            if not self.mock:
                cmd & FG

            if self.delete:
                self.notify(f"trash '{path}'")
                if to_move:
                    self.notify(f"mv '{basename}.{target_ext}' '{basename_old}.{target_ext}'")
                if not self.mock:
                    trash(path)
                    if to_move:
                        mv(f'{basename}.{target_ext}', f'{basename_old}.{target_ext}')

    def get_video_codec(self, path):
        mediainfo = local["mediainfo"]
        cmd = mediainfo["--inform=Video;%CodecID%", path]
        result = cmd()

        return result.strip()

    def get_audio_codec(self, path):
        mediainfo = local["mediainfo"]
        cmd = mediainfo["--inform=Audio;%CodecID%", path]
        result = cmd()

        return result.strip()

    def is_video_compatible(self, path):
        video_codec = self.get_video_codec(path)
        if video_codec in ["avc1", "V_MPEG4/ISO/AVC"]:
            return True

        if video_codec in ["V_VP9", "vp09"]:
            return False

        self.notify(f"The compatibility of the video codec {video_codec} is unknow (file : '{path}')", Notifier.ERROR)


    def is_audio_compatible(self, path):
        audio_codec = self.get_audio_codec(path)
        if audio_codec in ["mp4a-40-2", "A_AC3", "mp4a-6B"]:
            return True

        if audio_codec in ["A_AAC-2", "A_OPUS"]:
            return False

        self.notify(f"The compatibility of the audio codec {audio_codec} is unknow", Notifier.ERROR)

if __name__ == "__main__":
    ConvertMovie.run()
