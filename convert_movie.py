#!/bin/python

from plumbum import cli, local, FG # See https://plumbum.readthedocs.io/en/latest/cli.html
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
            if self.origin_exts is not None:
                self.notify("origin_exts = " + str(self.origin_exts))
            else:
                self.notify("origin_filepath = " + str(self.origin_filepath))

            self.notify("target_ext = " + str(target_ext))

        # echo "$file → $filename.ogg"
	# # ffmpeg -i "$file" -f avi -b 2048k -ab 160k -ar 44100 "$filename.avi"
	# ffmpeg -i "$file" -acodec libvorbis -vcodec libtheora "$filename.ogg"
        ffmpeg = local["ffmpeg"]
        trash = local["trash"]

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
            cmd = ffmpeg["-i", path, "-c:v", "libx264", "-preset", "veryfast", f"{basename}.{target_ext}"]
            if self.verbose:
                self.notify(str(cmd))
            if not self.mock:
                cmd & FG

            if self.delete:
                if self.verbose:
                    self.notify(f"trash '{path}'")
                if not self.mock:
                    trash(path)

if __name__ == "__main__":
    ConvertMovie.run()
