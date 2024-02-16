from instapaper import Instapaper, Bookmark
from flask import Flask, render_template, request
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv
import os

app = Flask(__name__)
engine = create_engine("sqlite:///data.db")
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()


class LinkSave(Base):
    __tablename__ = "link_save"
    id = Column(Integer, primary_key=True)
    folder_name = Column(String(100))
    url = Column(String(200))

    def __repr__(self):
        return f"<LinkSave(folder_name='{self.folder_name}', url='{self.url}')>"


Base.metadata.create_all(engine)


# Load variables from .env file
load_dotenv

# Now you can access the variables as normal Python variables
CONSUMER_KEY = os.getenv("CONSUMER_KEY")
CONSUMER_SECRET = os.getenv("CONSUMER_SECRET")
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")


def add_book(filename, datas):
    # Define the name of the new folder
    NEW_FOLDER_NAME = filename

    instapaper = Instapaper(CONSUMER_KEY, CONSUMER_SECRET)

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

        new_bookmark = Bookmark(instapaper, bookmark_params)

        # Save the bookmark
        new_bookmark.save(target_folder_id)
    return True


# add_book(
#     "Notes from Docsumo",
#     "https://bkrm.substack.com/p/notes-from-a-cto-14-llm-awaiting",
#     "https://bkrm.substack.com/p/notes-from-a-cto-13-leadership-quality",
#     "https://bkrm.substack.com/p/notes-from-a-cto-12-prioritization",
# )


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
            for url in urls:
                link_save = LinkSave(folder_name=folder_name, url=url)
                session.add(link_save)
            session.commit()
            return render_template("thank.html", message=message)
        else:
            message = "Authentication failed! Please try again."
            return render_template("thank.html", message=message)
    return render_template("index.html")


@app.route("/bookmarks")
def bookmarks():
    bookmarks = session.query(LinkSave).all()
    return render_template("bookmarks.html", bookmarks=bookmarks)


if __name__ == "__main__":
    app.run(debug=True)
