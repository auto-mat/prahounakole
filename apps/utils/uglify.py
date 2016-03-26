import os
import shutil
import subprocess
import tempfile
import uuid
from compressor import base
from compressor.conf import settings as compressor_settings
from compressor.js import JsCompressor
from django.conf import settings
from django.core.files import File
from django.utils.safestring import mark_safe
from os import path


class UglifyJSCompressor(JsCompressor):

    def output(self, mode='file', forced=False):

        assert mode == 'file', "Can only uglify to files"

        if not (compressor_settings.COMPRESS_ENABLED or forced):
            # Not compressing - fall back to default pass-through behaviour
            return super(JsCompressor, self).output(mode, forced)

        filenames = []
        for kind, value, basename, elem in self.split_contents():
            if kind != base.SOURCE_FILE:
                assert False, "Cannot uglify non-file script tags"
            filename = value  # for SOURCE_FILE
            filenames.append((filename, basename))

        tmp_dir = path.join(tempfile.gettempdir(), str(uuid.uuid4()))
        try:
            # copy every file to dir/basename
            for filename, basename in filenames:
                tmpname = path.join(tmp_dir, basename)
                assure_dir_exists(tmpname)
                shutil.copyfile(filename, tmpname)

            # generate the destination filename and destination filename map.
            # (read and concat input files only to generate a hash)
            def readfile(path):
                with open(path) as f:
                    return f.read()
            content = '\n'.join(readfile(filename) for filename, basename in filenames)
            new_filepath = self.get_filepath(content, basename=None)  # TODO basename?
            new_map_filepath = new_filepath + '.map'
            # (both are relative)

            # call uglifyjs in dir, create files
            uglifyjs_binary = settings.UGLIFY_JS_BINARY or 'uglifyjs'
            command = [uglifyjs_binary] + [basename for filename, basename in filenames] + [
                '-o', new_filepath,
                '--source-map', new_map_filepath,
                '--source-map-root', settings.STATIC_URL,
                '--source-map-url', settings.STATIC_URL + new_map_filepath
            ]
            assure_dir_exists(path.join(tmp_dir, new_filepath))
            subprocess.Popen(command, cwd=tmp_dir).wait()

            # save the files to the static storage
            def save(filepath):
                abs_filepath = os.path.join(tmp_dir, filepath)
                if not self.storage.exists(filepath) or forced:
                    with open(abs_filepath, 'r') as f:
                        self.storage.save(filepath, File(f))

            save(new_filepath)
            save(new_map_filepath)

            url = mark_safe(self.storage.url(new_filepath))
            return self.render_output(mode, {"url": url})

        finally:
            shutil.rmtree(tmp_dir)


def assure_dir_exists(path):
    if not os.path.exists(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))


# in settings:
# COMPRESS_JS_COMPRESSOR = 'codility.utils.UglifyJSCompressor.UglifyJSCompressor'
