#Project: Catalog Application

A web based catalog application with OAUTH user control.

##Requirements

- VirtualBox installed: download it from virtualbox.org for your operating system.
- Vagrant installed: download it from vagrantup.com (the software to configure the VM
- Python 2.x
- Flask (http://flask.pocoo.org/)
- SQLAlchemy (http://www.sqlalchemy.org/)

##How to Run the Project
- Install Vagrant
- Clone this repo
- In vagrant/ directory, run *vagrant up*
- Run *vagrant ssh*
- Move to catalog directory: *cd /vagrant/catalog* 
- Create database and default category with *python db_setup.py*
- Add Teams and Players *python moreteams.py* 
- Run server with *python project.py*
- Navigate to http://localhost:8000 in your browser