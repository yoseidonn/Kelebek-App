# Kelebek - Student Seating Arrangement Application
Kelebek is a desktop application designed to create student seating layouts for exams with proper shuffling. Developed using Python and PyQt, it stores all data locally on the user's machine. The application includes a licensing system that communicates with a Django-based API for license verification and management.

## Note
Kelebek was submitted to Teknofest, where it earned 219th place. Although it did not make it to the finals, the experience motivated me to further develop the application. Later, I decided to sell the app at a low price to cover server costs and added a licensing system using a Django-based API for license management.

## Features
**Seating Arrangement:** Generate randomized seating plans for students during exams to ensure fairness.
**Local Storage:** All data is stored locally, ensuring privacy and quick access.
**Licensing System:** Integrated license verification through a Django-based API to manage application access.

## Installation
### Step 1: Clone the Repositories
First, clone both the Kelebek Desktop Application and Kelebek Site repositories:

```
# bash
git clone https://github.com/yoseidonn/Kelebek-App.git
cd Kelebek-App
```

Then, clone the Kelebek Site repository in a separate directory:

```
# bash
git clone https://github.com/yoseidonn/Kelebek-Site.git
cd Kelebek-Site
```

### Step 2: Install Python Dependencies
Ensure you have Python installed. Then, install the required Python packages by running the following command:

```
# bash
pip install -r requirements.txt
```

The requirements.txt includes all the necessary Python dependencies for the application, including PyQt5 and others.

### Step 3: Install System-Level Dependencies
The application also requires some system-level libraries to function correctly. You can install these using apt:

```
# bash
sudo apt install libxcb-xinerama0 libxcb-cursor0
```
These libraries are required for the graphical interface to work properly.

### Step 4: Modify the .env File
When you first launch the Kelebek desktop application, *a **.env** file will be created* in the project directory.

Open the **.env** file and modify the following line:

```
SERVER_IP=http://kelebeksistemi.com.tr/
```

Change it to:

```
SERVER_IP=http://localhost:8000/
```
This will point the desktop application to the locally hosted Django server during development.

### Step 5: Start the Django Server
Navigate to the Kelebek Site directory and start the Django server:

```
# bash
cd Kelebek-Site
python manage.py runserver
```

This will start the server locally on **http://localhost:8000**, and the desktop application will now be able to communicate with it.

### Step 6: Run the Desktop Application
After setting up the Django server and modifying the .env file, you can launch the Kelebek desktop application:

```
# bash
cd ../Kelebek-App
python main.py
```

### Step 7: License Activation
Upon first launch, enter your license key when prompted. The application will communicate with the Django-based API to verify and activate your license.

## Project Structure
**Kelebek Desktop Application:**
```
Kelebek-App/
├── App/
├── Client/
├── Forms/
├── Images/
├── main.py
├── requirements.txt
├── resources.qrc
```

App/: Contains the main application modules.
Client/: Includes the client module responsible for communicating with the Django API for license management.
Forms/: Houses the UI forms created using PyQt.
Images/: Stores image assets used in the application.
main.py: The entry point of the application.
requirements.txt: Lists all the Python dependencies required to run the application.
resources.qrc: Resource file for managing application assets.
Kelebek Site (Django server for license and API):

```
Kelebek-Site/
├── manage.py
├── requirements.txt
├── app/
└── other_files/
```

manage.py: The entry point for running the Django server.
requirements.txt: Lists all Python dependencies for the Django server.
app/: Contains Django app modules for handling the backend logic.
other_files/: Includes any additional files needed for the Django server.
License
This project is licensed under a proprietary license. For more details, refer to the LICENSE file or contact the author.

Contact
For any inquiries or support, please contact [your email address].

