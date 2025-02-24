# Welcome to the Ecolution Project for ECM2434! 

### Kayan's Kanban
___

The group members are:

1. Amelia Denney
2. Tom Stobart
3. Kayan Hyatt
4. Olly Johnson
5. Freya Larkin
6. Dillon O'Connor
7. Mike Price

This is a submission for Sprint 1. There are three types of document that you will find the following places.

## PROCESS DOCUMENTS
Our process documents are managed in the Trello platform. The link to our project page is below. We, tomstobart, have added solomonoyelere1 to the board so it is visible.

Trello link: [https://trello.com/b/T2XwRhTw/ecm2434]

We have also taken regular snapshots of the kanban board in trello to archive our progress. These are held in the repository below.

[./process-documents/kanban-snapshot/](./process-documents/kanban-snapshot/)

Within process documents we have also included the meeting notes, agenda and minutes. These will be found in the repository below.

[./process-documents/meeting-notes/](./process-documents/meeting-notes/)


## TECHNICAL DOCUMENTS
Our technical documents are primarily managed on the github system. The link to the project is below:

github link: [https://github.com/KayanHyatt/ECM2434]

We have also include the versioned source code for archiving.

[./technical-documents/](./technical-documents/)

Technical documents are broken down into front end and back end etc.  

## PRODUCT DOCUMENTS
Our product documents are primarily in the form of a product UI. Below is a link to our latest version.

public link: [https://www.figma.com/design/fAOD9lxiUZpChOvwcV0yKX/ECM2434-Mobile?node-id=512-4549&t=z21kqQ5KSciCJO4v-1]

The UI and design documents for the client have also been archived under the link below:

[./product-documents/UI/](./product-documents/UI/)

## SET-UP INSTRUCTIONS

Instructions for running Django Server for first time on personal computer (Windows):
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

.\venv\Scripts\activate
cd ECM2434
python manage.py runserver

127.0.0.1:8000/Ecolution/login

Other instructions needed when migrating to pc without project.
