# ENGO551_Lab1
This is a website that allows registered users to search for book reviews submitted by other registered users, using a database containing up to 5000 books. 

Demo for the website can be found [here](https://youtu.be/BrhvDqz11XA). Flask, HTML, Bootstrap, and PostgreSQL were used to build this website.

## Files

**db/import.py** - loads books.csv into table books in the PostgreSQL database
**templates/layout.html** - Flask template providing general layout of the website. used as parent of all pages
**templates/404.html** - Flask template for 404 errors
**templates/login.html** - Flask template for login/logout page
**templates/register.html** - Flask template for registering account page
**templates/register_success.html** - Flask template for a page that appears after a user has registered an account successfully 
**templates/search.html** - Flask template for main book search page and search results
**templates/result.html** - Flask template for book information page
**application.py** - Flask application that launches the development server for the website




