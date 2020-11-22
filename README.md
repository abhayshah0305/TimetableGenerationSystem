# Timetable Generation System

<h3>Project Description</h3>
<p>The project, Timetable Generation System (TTGS), is a web application developed using the Django Framework and an SQLite database.</p>
<p>The project makes use of a genetic algorithm to satisfy the soft and hard constraints and generate the most optimal timetable. The web application includes a simple authentication-authorization module, and on successfull authentication the user is redirected to the admin dashboard.</p>
<p>On the admin dashboard the user can input the data of the college/university which is required to generate the timetable. The user must add the following details:</p>
<ol>
  <li>Teachers</li>
  <li>Classrooms</li>
  <li>Timings</li>
  <li>Courses</li>
  <li>Departments</li>
  <li>Sections</li>
</ol>

<p>Upon successfull entry of the data into sqlite database, the user can navigate to the "Generate Timetable" page to start the process of generating the timetable. Upon successfull generation of the timetable the user can download the timetable as a PDF.</p>   

<p>Technologies Used:</p>
<ul>
  <li>HTML5</li>
  <li>CSS3</li>
  <li>Python 3.8</li>
  <li>Django 3.0.*</li>
  <li>JavaScript</li>
  <li>sqlite3</li>
</ul>

<h3>How to run the Project?</h3>
<ol>
  <li>Clone the Repository</li>
  <li>Access the project files by using an IDE (PyCharm or Spyder) or via the command line
  <li>Enter the directory of the main project via the command line or the terminal on the IDE</li>
  <li>Run the command "python manage.py runserver"</li>
  <li>Open your browser and access localhost at port http://127.0.0.1:8000/</li>
</ol>

<h3>Contact</h3>
<p>Email: shah.abhay.18bit048@gmail.com</p>
