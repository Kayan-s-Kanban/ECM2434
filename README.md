Instructions for running Django Server for first time on personal computer:
1. Ensure you have python 3.13.1 downloaded and it is the python version your VSCode is using
2. Open the project is VSCode
3.  In terminal run command: python -m venv venv
4. Then command: .\venv\Scripts\activate
5. Then: pip install -r requirements.txt
6. Navigate to second ECM2434 folder
7. Run command: python manage.py runserver
8. Access server using 127.0.0.1:8000/Ecolution
9. Exit server using exit
10. Then exit venv using deactivate
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
