## Item Catalog

You will develop an application that provides a list of items within a variety of categories as well as provide a user registration and authentication system. Registered users will have the ability to post, edit and delete their own items.

## Dependencies:
python 3.6, PostgreSQL 9.5.16, Vagrant, VirtualBox

## How to run:
1. Install Dependencies: [python3](https://www.python.org/downloads/), [VirtualBox](https://www.virtualbox.org/wiki/Downloads), [Vagrant](https://www.vagrantup.com/downloads.html)
2. Clone the files in [github repo](https://github.com/zacktwp/Item_Catalog) into a chosen directory.
3. cd into the Vagrant directory and execute 'vagrant up' in terminal
4. execute 'vagrant ssh' in terminal
5. cd into the /vagrant/catalog directory
6. run 'python database_setup.py'
7. run 'python PopulateProductsDB.py'
8. run 'python EverythingStore.py'
