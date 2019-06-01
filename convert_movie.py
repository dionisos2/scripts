#!/bin/python

from plumbum import cli, local, FG # See https://plumbum.readthedocs.io/en/latest/cli.html
import os
import glob

class ConvertMovie(cli.Application):
    """
    Convert all files found in the current directory from origin_exts list of extensions(separated by commas) to target_ext extension.
    Use ffmpeg for the conversion
    """
    verbose = cli.Flag(["v", "verbose"], help="If given, I will be very talkative")
    delete = cli.Flag(["d", "delete"], help="Delete file after conversion (with trash, 'trash-cli' package needed)")
    recursive = cli.Flag(["r", "recursive"], help="Go through directory recursively")

    def main(self, origin_exts, target_ext="ogg"):
        origin_exts = origin_exts.split(",")
        if self.verbose:
            print("verbose = ", self.verbose)
            print("delete = ", self.delete)
            print("recursive = ", self.recursive)
            print("origin_exts = ", origin_exts)
            print("target_ext = ", target_ext)

        # echo "$file → $filename.ogg"
	# # ffmpeg -i "$file" -f avi -b 2048k -ab 160k -ar 44100 "$filename.avi"
	# ffmpeg -i "$file" -acodec libvorbis -vcodec libtheora "$filename.ogg"
        ffmpeg = local["ffmpeg"]
        trash = local["trash"]

        if self.recursive:
            path_list = glob.iglob("./**/*.*", recursive=True)
        else:
            path_list = glob.iglob("./*.*", recursive=False)

        path_list = [path for path in path_list if os.path.splitext(path)[1][1:] in origin_exts]

        if self.verbose:
            print(path_list)

        for path in path_list:
            basename = os.path.splitext(path)[0]
            cmd = ffmpeg["-i", path, "-acodec", "libvorbis", "-vcodec", "libtheora", f"{basename}.{target_ext}"]
            if self.verbose:
                print(cmd)
            cmd & FG

            if self.delete:
                if self.verbose:
                    print(f"delete '{path}'")
                trash(path)

if __name__ == "__main__":
    ConvertMovie.run()
