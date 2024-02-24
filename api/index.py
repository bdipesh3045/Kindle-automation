from .instapaper import instapaper as insta
from flask import Flask, render_template, request
from dotenv import load_dotenv
import os

app = Flask(__name__)

# Load variables from .env file
load_dotenv()

# Now you can access the variables as normal Python variables
CONSUMER_KEY = os.getenv("CONSUMER_KEY")
CONSUMER_SECRET = os.getenv("CONSUMER_SECRET")
USERNAME = os.getenv("INAME")
PASSWORD = os.getenv("PASSWORD")


def add_book(filename, datas):
    # Define the name of the new folder
    NEW_FOLDER_NAME = filename

    instapaper = insta.Instapaper(CONSUMER_KEY, CONSUMER_SECRET)

    # Authenticate with Instapaper
    instapaper.login(USERNAME, PASSWORD)

    # Create a new folder
    try:
        instapaper.create_folder(NEW_FOLDER_NAME)
    except Exception as e:
        print("Failed to create the folder:", e)
    folders = instapaper.folders()
    for folder in folders:
        if folder["title"] == NEW_FOLDER_NAME:
            target_folder_id = folder["folder_id"]
            break

    for data in datas:
        bookmark_params = {
            "title": data[0],
            "url": data[1],
        }

        new_bookmark = insta.Bookmark(instapaper, bookmark_params)

        # Save the bookmark
        new_bookmark.save(target_folder_id)
    return True


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        if request.form.get("secretKey") == os.getenv("SecretKey"):
            folder_name = request.form["folderName"]
            urls = request.form.getlist("urls[]")
            name = request.form.getlist("bookNames[]")
            datas = zip(name, urls)
            result = add_book(folder_name, datas)

            if result == True:
                message = "Thank you! Data was successfully added."
            else:
                message = "Failed to add the bookmarks"
            return render_template("thank.html", message=message)
        else:
            message = "Authentication failed! Please try again."
            return render_template("thank.html", message=message)
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
