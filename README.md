Instructions for running Django Server for first time on personal computer:
1. Ensure you have python 3.13.1-3.13.2 downloaded and it is the python version your VSCode is using
2. Open the project is VSCode
3. In terminal run command: python --version and ensure version is 3.13.1
4. Ensure there is no venv folder, then run command: python -m venv venv
5. Then command: .\venv\Scripts\activate
6. Then: pip install -r requirements.txt
7. Navigate to second ECM2434 folder
8. Run command: python manage.py runserver
9. Access server using 127.0.0.1:8000/Ecolution
10. Exit server using Ctrl+C
11. Then exit venv using deactivate
(Do not be surprised if your venv folder does not upload when committing, it is meant to be ignored and not be on the github, they are personal)

Every other time use these steps:
1. Open the project in VSCode
2. Run command: .\venv\Scripts\activate
3. Navigate to second ECM2434 folder
4. Run command: python manage.py runserver
5. Access server using 127.0.0.1:8000/Ecolution
6. Exit server using exit
7. Then exit venv using deactivate


Other instructions needed when migrating to pc without project.
