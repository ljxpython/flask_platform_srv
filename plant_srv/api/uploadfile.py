"""
参考:
    https://flask.palletsprojects.com/en/3.0.x/patterns/fileuploads/
    https://blog.csdn.net/weixin_45681435/article/details/125681067
    https://www.cnblogs.com/tracydzf/p/13406795.html


"""

import os

from flask import Blueprint, Flask, flash, redirect, request, url_for
from werkzeug.utils import secure_filename

from conf.constants import Config
from plant_srv.utils.json_response import JsonResponse

file = Blueprint("file", __name__)


def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in Config.ALLOWED_EXTENSIONS
    )


@file.route("/upload", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        # check if the post request has the file part
        if "file" not in request.files:
            flash("No file part")
            return redirect(request.url)
        file = request.files["file"]
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == "":
            flash("No selected file")
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(Config.UPLOAD_FOLDER, filename))
            return redirect(url_for("download_file", name=filename))
    return JsonResponse.success_response()
