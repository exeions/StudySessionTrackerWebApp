#~ A simple Flash web application I made that is based off my original CLI interface. 
#~ It allows users to start and end study sessions, and view their stats. It uses a JSON file to store the session data, and the Waitress WSGI server to serve the application. 
#~ I made this for fun and to learn more about web development, so it is not meant to be a production-ready application. It is also not meant to be a complete application, as it is missing features such as user authentication and error handling. 
#~ I may add these features in the future, but for now it is a simple application that serves its purpose. 
#~ I hope you find it useful!

from waitress import serve
from flask import Flask, render_template, request, redirect, url_for
import time, json, os

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(BASE_DIR, "session_data.json")
current_session = {}

@app.route("/")
@app.route("/index")
def index():
    return render_template("index.html")

@app.route('/start_session', methods=['POST'])
def start_session():
    if "start_time" in current_session: # Stops user from starting session when a session is already present.
        return render_template("message.html", message="Session already running. End it first.",running=True)

    subject = request.form.get("subject")
    if not subject:
        return render_template("message.html", message="Please enter a subject to start a session.")

    current_session["subject"] = subject
    current_session["start_time"] = time.time()

    formatted = time.strftime("%H:%M:%S", time.gmtime(current_session["start_time"]))
    
    return render_template("start_session.html", subject=subject, start_time=formatted)

@app.route('/end_session', methods=['GET', 'POST'])
def end_session():
    if "start_time" not in current_session: # Stops user from ending a non-existent session.
        return render_template("message.html", message="Session not started. Please start a session first before trying to end one.")

    end_time = time.time()
    duration = float((end_time - current_session["start_time"]))

    subject = current_session["subject"] # Current subject.
    session_data = { # A dictionary of both the subject and the duration of the current session.
        "session": subject, 
        "duration": duration
    }

    try:
        with open(file_path, "r") as file:
            sessions = json.load(file) # Loads the json file to the sessions list.
    except: # I would use proper error handling here but I am keeping this system basic for now. (im too lazy)
        sessions = []

    sessions.append(session_data)

    formatted = time.strftime("%H:%M:%S", time.gmtime(duration)) # Formats the duration into something user-friendly.

    with open(file_path, "w") as file:
        json.dump(sessions, file, indent=4)
        file.close()
    
    current_session.clear() # Clears the current session so it is ready for the next session. Prevents errors.

    return render_template("end_session.html", subject=subject, duration=formatted)

@app.route('/view_stats')
def view_stats():
    with open("session_data.json", "r") as file:
        sessions = json.load(file) # Loads the sessions for the JSON file.
        
        if not sessions: # If there are no sessions, it outputs a message saying so.
            return render_template("message.html", message="No sessions found. Start a session to see stats.")

        total_duration = 0
        for session in sessions:
            total_duration += session["duration"] # Adds each session duration to the total.
        formatted_total_duration = time.strftime("%H:%M:%S", time.gmtime(total_duration))

        formatted_sessions = []

        for session in sessions:
            duration_formatted = time.strftime("%H:%M:%S", time.gmtime(session["duration"])) # Formats the duration of each session.
            formatted_sessions.append({"session": session["session"], "duration": duration_formatted}) # Outputs it in a meaningful way.

        return render_template("view_stats.html", sessions=formatted_sessions, total_duration=formatted_total_duration)

if __name__ == "__main__":
    serve(app, host="0.0.0.0", port=8000)
