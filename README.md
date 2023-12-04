# cs3530-project
A collaborative decentralised file sharing and editing application

## How to run
1. Clone the repository
2. Requires gtk3 and python3 to be installed
    - On Ubuntu: `sudo apt-get install python3-gi python3-gi-cairo gir1.2-gtk-3.0`
3. Run `python3 main.py` in the project directory. This will open the GUI.
4. Click the file menu. This will open options to create a new file, open an existing file, share a file, or join a network.
    - To create a new file, click the "New" button. This will open a new window. Enter the name of the file you want to create, and click "Create".
    - To open an existing file, click the "Open" button. This will open a new window. Enter the name of the file you want to open, and click "Open".
    - To share a file, click the "Share" button. This will show the link to share the file. Copy this link and send it to the person you want to share the file with.
    - To join a network, click the "Join" button. This will open a new window. Enter the link you received from the person who shared the file with you, and click "Join".
