import os
import shutil
import subprocess
import tempfile


def download_cyklistesobe_tracks(output_dir):
    """Download cyklistesobe tracks from REST API endopint

    Required for show 'Cyklisté sobě' overlayer.
    """
    features_file = "list.json"
    app = "download-cyklistesobe-tracks"

    temp_dir = tempfile.gettempdir()
    os.chdir(temp_dir)
    cyklistesobe_dir = os.path.join(temp_dir, app)
    if not os.path.exists(cyklistesobe_dir):
        subprocess.call(
            ["git", "clone", f"https://github.com/auto-mat/{app}.git"],
        )
    os.chdir(cyklistesobe_dir)
    with tempfile.TemporaryDirectory() as temp_dir:
        down_track = os.path.join(cyklistesobe_dir, "down_tracks.sh")
        subprocess.call(["chmod", "+x", down_track])
        os.chdir(temp_dir)
        subprocess.call([down_track])
        shutil.copy(
            os.path.join(temp_dir, features_file),
            os.path.join(output_dir, features_file),
        )
