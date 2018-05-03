# This is a sample commands.py.  You can add your own commands here.
#
# Please refer to commands_full.py for all the default commands and a complete
# documentation.  Do NOT add them all here, or you may end up with defunct
# commands when upgrading ranger.

# A simple command for demonstration purposes follows.
# -----------------------------------------------------------------------------

from __future__ import (absolute_import, division, print_function)

# You can import any python module as needed.
import os

# You always need to import ranger.api.commands here to get the Command class:
from ranger.api.commands import Command

# dionisos import
from subprocess import Popen
import re


# Any class that is a subclass of "Command" will be integrated into ranger as a
# command.  Try typing ":my_edit<ENTER>" in ranger!
class my_edit(Command):
    # The so-called doc-string of the class will be visible in the built-in
    # help that is accessible by typing "?c" inside ranger.
    """:my_edit <filename>

    A sample command for demonstration purposes that opens a file in an editor.
    """

    # The execute method is called when you run this command in ranger.
    def execute(self):
        # self.arg(1) is the first (space-separated) argument to the function.
        # This way you can write ":my_edit somefilename<ENTER>".
        if self.arg(1):
            # self.rest(1) contains self.arg(1) and everything that follows
            target_filename = self.rest(1)
        else:
            # self.fm is a ranger.core.filemanager.FileManager object and gives
            # you access to internals of ranger.
            # self.fm.thisfile is a ranger.container.file.File object and is a
            # reference to the currently selected file.
            target_filename = self.fm.thisfile.path

        # This is a generic function to print text in ranger.
        self.fm.notify("Let's edit the file " + target_filename + "!")

        # Using bad=True in fm.notify allows you to print error messages:
        if not os.path.exists(target_filename):
            self.fm.notify("The given file does not exist!", bad=True)
            return

        # This executes a function from ranger.core.acitons, a module with a
        # variety of subroutines that can help you construct commands.
        # Check out the source, or run "pydoc ranger.core.actions" for a list.
        self.fm.edit_file(target_filename)

    # The tab method is called when you press tab, and should return a list of
    # suggestions that the user will tab through.
    # tabnum is 1 for <TAB> and -1 for <S-TAB> by default
    def tab(self, tabnum):
        # This is a generic tab-completion function that iterates through the
        # content of the current directory.
        return self._tab_directory_content()

class real_delete(Command):
    """:real_delete
    Tries to delete the selection but really (don’t use dionisos_rm)
    """
    allow_abbrev = False

    def execute(self):
        import os
        if self.rest(1):
            self.fm.notify("Error: delete takes no arguments! It deletes "
                    "the selected file(s).", bad=True)
            return

        cwd = self.fm.thisdir
        cf = self.fm.thisfile
        if not cwd or not cf:
            self.fm.notify("Error: no file selected for deletion!", bad=True)
            return

        confirm = self.fm.settings.confirm_on_delete
        many_files = (cwd.marked_items or (cf.is_directory and not cf.is_link \
                and len(os.listdir(cf.path)) > 0))

        if confirm != 'never' and (confirm != 'multiple' or many_files):
            self.fm.ui.console.ask("Confirm deletion of: %s (y/N)" %
                ', '.join(f.basename for f in self.fm.thistab.get_selection()),
                self._question_callback, ('n', 'N', 'y', 'Y'))
        else:
            # no need for a confirmation, just delete
            self.fm.delete()

    def _question_callback(self, answer):
        if answer == 'y' or answer == 'Y':
            self.fm.delete()

# dionisos extract.
class extract(Command):
    """:extract
    uncompress a file
    """
    allow_abbrev = False

    def dionisos_extract(self):
        self.fm.notify("extraction !")
        selected = self.fm.thistab.get_selection()
        for f in selected:
            Popen("/home/dionisos/scripts/extract \"" + f.path + "\" -y", shell=True) #TODO vérifier si tout est ok avec Popen

    def execute(self):
        import os
        if self.rest(1):
            self.fm.notify("Error: extract takes no arguments! It extracts "
                    "the selected file.", bad=True)
            return

        cf = self.fm.thisfile
        if not cf:
            self.fm.notify("Error: no file selected for extraction!", bad=True)
            return

        self.fm.ui.console.ask("Confirm extraction of: %s (y/N)" %
                               ', '.join(f.basename for f in self.fm.thistab.get_selection()),
                               self._question_callback, ('n', 'N', 'y', 'Y'))

    def _question_callback(self, answer):
        if answer == 'y' or answer == 'Y':
            self.dionisos_extract()

class delete(Command):
    """:delete

    Tries to delete the selection.

    "Selection" is defined as all the "marked files" (by default, you
    can mark files with space or v). If there are no marked files,
    use the "current file" (where the cursor is)

    When attempting to delete non-empty directories or multiple
    marked files, it will require a confirmation.
    """

    allow_abbrev = False

    def dionisos_delete(self):
        self.fm.notify("Deleting!")
        selected = self.fm.thistab.get_selection()
        command_args = ""
        for file_to_delete in selected:
            command_args += '"' + file_to_delete.path + '" '
        # print("trash " + command_args)
        Popen("trash " + command_args, shell=True) #TODO vérifier si tout est ok avec Popen

    def execute(self):
        import os
        if self.rest(1):
            self.fm.notify("Error: delete takes no arguments! It deletes "
                    "the selected file(s).", bad=True)
            return

        cwd = self.fm.thisdir
        cf = self.fm.thisfile
        if not cwd or not cf:
            self.fm.notify("Error: no file selected for deletion!", bad=True)
            return

        confirm = self.fm.settings.confirm_on_delete
        many_files = (cwd.marked_items or (cf.is_directory and not cf.is_link \
                and len(os.listdir(cf.path)) > 0))

        if confirm != 'never' and (confirm != 'multiple' or many_files):
            self.fm.ui.console.ask("Confirm deletion of: %s (y/N)" %
                ', '.join(f.basename for f in self.fm.thistab.get_selection()),
                self._question_callback, ('n', 'N', 'y', 'Y'))
        else:
            # no need for a confirmation, just delete
            # self.fm.delete()
            self.dionisos_delete()

    def _question_callback(self, answer):
        if answer == 'y' or answer == 'Y':
            # self.fm.delete()
            self.dionisos_delete()

