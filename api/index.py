import instapaper as insta
from flask import Flask, render_template, request
from dotenv import load_dotenv
import os
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
import uuid
import time


class Base(DeclarativeBase):
    pass


app = Flask(__name__)

# Load variables from .env file
load_dotenv()
db = SQLAlchemy(model_class=Base)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("SupaUrl")

db.init_app(app)
# Now you can access the variables as normal Python variables


class Folder(db.Model):
    __tablename__ = "folder"
    folder_id = db.Column(db.String(100), primary_key=True, default=uuid.uuid4)
    folder_name = db.Column(db.String(100), nullable=False)
    folder_insta = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f"Folder{self.folder_name}"


class Book(db.Model):
    __tablename__ = "book"
    book_id = db.Column(db.String(100), primary_key=True, default=uuid.uuid4)
    rel = db.Column(db.String(100), db.ForeignKey("folder.folder_id"))
    folder = db.relationship("Folder", backref=db.backref("books"))
    book_name = db.Column(db.String(100), nullable=False)
    book_url = db.Column(db.String(100), nullable=False)


with app.app_context():
    db.create_all()

CONSUMER_KEY = os.getenv("CONSUMER_KEY")
CONSUMER_SECRET = os.getenv("CONSUMER_SECRET")
USERNAME = os.getenv("INAME")
PASSWORD = os.getenv("PASSWORD")


def add_book(filename, datas):
    i = 0
    instapaper = Instapaper(CONSUMER_KEY, CONSUMER_SECRET)

    # Authenticate with Instapaper
    instapaper.login(USERNAME, PASSWORD)

    def new_file(no):
        # Define the name of the new folder
        if no == 0:
            NEW_FOLDER_NAME = filename
        else:
            NEW_FOLDER_NAME = f"{filename}{no}"

        # Create a new folder
        try:
            instapaper.create_folder(NEW_FOLDER_NAME)
        except Exception as e:
            print("Failed to create the folder:", e)

        folders = instapaper.folders()
        target_folder_id = None  # Initialize target_folder_id

        for folder in folders:
            if folder["title"] == NEW_FOLDER_NAME:
                target_folder_id = folder["folder_id"]
                break

        if target_folder_id is None:
            print("Failed to find the target folder")
            return False
        return (target_folder_id, NEW_FOLDER_NAME)

    for data in datas:
        if i == 0 or i % 20 == 0:
            target_folder_id, NEW_FOLDER_NAME = new_file(i // 20)
            print(f"Folder created: {NEW_FOLDER_NAME}")
        bookmark_params = {
            "title": data[0],
            "url": data[1],
        }
        print(f"Book added {data[0]}")
        time.sleep(1)
        new_bookmark = Bookmark(instapaper, bookmark_params)
        i += 1
        # Save the bookmark
        new_bookmark.save(target_folder_id)
        print(f"Book count: {i}")

    return True


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        if request.form.get("secretKey") == os.getenv("SecretKey"):
            folder_name = request.form["folderName"]
            urls = request.form.getlist("urls[]")
            name = request.form.getlist("bookNames[]")

            datas = zip(name, urls)
            folder_id = request.form.get("folderSelection")
            folder_name = request.form.get("folderName")
            if folder_id:
                print(folder_id)
            elif folder_name:
                pass
            result = add_book(folder_name, datas)

            if result == True:
                message = "Thank you! Data was successfully added."
            else:
                message = "Failed to add the bookmarks"
            return render_template("thank.html", message=message)
        else:
            message = "Authentication failed! Please try again."
            return render_template("thank.html", message=message)
    folders = Folder.query.all()
    return render_template("index.html", folders=folders)


if __name__ == "__main__":
    app.run(debug=True)
