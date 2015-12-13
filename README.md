#Project: Catalog Application

A web based catalog application with OAUTH user control.

##Requirements

- VirtualBox installed: download it from virtualbox.org for your operating system.
- Vagrant installed: download it from vagrantup.com (the software to configure the VM
- Python 2.x
- Flask (http://flask.pocoo.org/)
- SQLAlchemy (http://www.sqlalchemy.org/)
- Register app with both Google afor OAUTH ID and secrets
-- https://developers.google.com

##How to Run the Project
- Install Vagrant
- Clone this repo
- In vagrant/ directory, run *vagrant up*
- Run *vagrant ssh*
- Move to catalog directory: *cd /vagrant/catalog* 
- Create database and default category with *python database_setup.py*
-- Add Team and Player *python moreteams.py* 
- Run server with *python project.py*
- Navigate to http://localhost:8000 in your browser