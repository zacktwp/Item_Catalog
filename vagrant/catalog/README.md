## Item Catalog

You will develop an application that provides a list of items within a variety of categories as well as provide a user registration and authentication system. Registered users will have the ability to post, edit and delete their own items.

## Dependencies:
python 3.6, PostgreSQL 9.5.16, Vagrant, VirtualBox, newsdata.sql

## How to run:
1. Install Dependencies: [python3](https://www.python.org/downloads/), [VirtualBox](https://www.virtualbox.org/wiki/Downloads), [Vagrant](https://www.vagrantup.com/downloads.html), [News DB](https://d17h27t6h515a5.cloudfront.net/topher/2016/August/57b5f748_newsdata/newsdata.zip)
2. Download the files in [github repo](https://github.com/zacktwp/Log_Analysis) into a chosen directory.
3. You will need to unzip the newsdata.zip file downloaded earlier. The file inside is called newsdata.sql. Put this file into the vagrant directory, which is shared with your virtual machine. To load the data, cd into the vagrant directory and use the command psql -d news -f newsdata.sql.
4. Place all other files from the github repo into the vagrant directory.
5. type 'vagrant ssh' to ssh into the virtual machine.
6. Navigate to the /vagrant directory where you will find Logs_Analysis_project.py
7. type: python Logs_Analysis_project.py into the terminal and you will see your results
