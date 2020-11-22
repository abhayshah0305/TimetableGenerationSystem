# Timetable Generation System

<h3>Project Description</h3>
<p>The project, Timetable Generation System (TTGS), is a web application developed using the Django Framework and an SQLite database.</p>
<p>The project makes use of a genetic algorithm to satisfy the soft and hard constraints and generate the most optimal timetable. The web application includes a simple authentication-authorization module, and on successfull authentication the user is redirected the admin dashboard.</p>
<p>On the admin dashboard the user can input the data of the college/university which is required to generate the timetable. The user must add details such as:</p>
<ol>
  <li>Teachers</li>
  <li>Classrooms</li>
  <li>Timings</li>
  <li>Courses</li>
  <li>Departments</li>
  <li>Sections</li>
</ol>

<p>Upon successfull entry of the data into sqlite database, the user can navigate to the "Generate Timetable" page to start the process of generating the timetable. Upon successfull generation of the timetable the user can download the timetable as a PDF.</p>   
