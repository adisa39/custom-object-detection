# custom-object-detection
A user ready custom object detection project. This project is aimed at showcasing my knowledge as a 3MTT cohort 3 fellow having participated in the AI/ML program. The project is powered by pre-trained YOLO V8 model to detect and track objects selected from the settings screen.

# USES
This project have various applications such as security, objects monitoring, smart CCTV application etc.

# Installation STEPS
- Clone this repository by running *git clone https//:*
- Create a virtual environment *python -m venv venv*
- Install project dependencies *pip install -r requirements.txt*
- Launch the project by running *python main.py*

# USER MANUAL 
## SETTINGS
- Go to "Setting" from the navigation menu to open the settings UI in the sidebar.
- Input camera or test video URL.
- Input preffered name of the detection zone (text).
- Select "Enable Sound" or "Disable Sound" to turn on/off detection alarm sound.
- Press CTRL key and select all objects classes you want to detect from the object classe.
- Check/Uncheck the "Draw New Alarm Zone" to draw new detection zone on the inputed video/feeds frame.
- Click on Submit button to effect the changes.

## DRAWING DETECTION ZONE
If *Draw New Alarm Zone* is checked in the setting screen and submit button is pressed, a new will open showing preview of the video frame.
map out intended detection zone on the frame by clicking on the four corner of the zone. Press Enter key to save the zone coordinates or Esc key to cancel changes.

## WATCH LIVE FEED
Click on *Live* in the navigation menu to watch the live feed video.

## CHECK REPORT
Click on *Report* in the navigation menu to view generated reports.
