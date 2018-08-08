from flask import Flask, render_template, flash, redirect, url_for, session, logging,request, send_file

from data import Semesters
from coursesData import Courses
from flask_mysqldb import MySQL
from wtforms import Form, StringField, IntegerField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps
from io import BytesIO

app = Flask(__name__)

app.config['MYSQL_HOST']='localhost'
app.config['MYSQL_USER']='root'
app.config['MYSQL_PASSWORD']='akshay@1998'
app.config['MYSQL_DB']='dbproject'
app.config['MYSQL_CURSORCLASS']='DictCursor'

mysql = MySQL(app)

Semesters = Semesters()
Courses = Courses()

@app.route('/')
def index():
	return render_template('home.html')

@app.route('/about')
def about():
	return render_template('about.html')

@app.route('/articles', strict_slashes=False)
def articles():
	cur = mysql.connection.cursor()
	result = cur.execute("SELECT * FROM articles")
	articles = cur.fetchall()
	if result>0:
	        return render_template('articles.html',articles=articles)
	else:
		print("In else block")
		msg = "No Articles Found"
		return render_template('articles.html',msg=msg)
	cur.close()



@app.route('/article/<string:id>')
def article(id):
	cur = mysql.connection.cursor()
	result = cur.execute("SELECT * FROM articles WHERE id = %s",[id])
	article=cur.fetchone()
	return render_template('article.html', article=article)


class RegisterForm(Form):
	name = StringField('Name', [validators.Length(min=1,max=50)])
	username = StringField('Username',[validators.Length(min=4,max=25)],render_kw={"placeholder": "Enter your USN"})
	email = StringField('Email',[validators.Length(min=6,max=50)])
	password = PasswordField('Password',[validators.DataRequired(),validators.EqualTo('confirm',message='Passwords do not match')])
	confirm = PasswordField('Confirm Password',[validators.DataRequired()])

@app.route('/register',methods=['GET','POST'])
def register():
	form = RegisterForm(request.form)
	if request.method == 'POST' and form.validate():
		name = form.name.data
		email = form.email.data
		username = form.username.data
		password = sha256_crypt.encrypt(str(form.password.data))
		#cursor
		cur = mysql.connection.cursor()
		cur.execute("INSERT INTO userS(name, email, username, password) VALUES(%s, %s, %s, %s)",(name,email,username,password))
		mysql.connection.commit()
		cur.close()
		flash('You are now registered and can log in','success')
		return redirect(url_for('index'))	

	return render_template('register.html',form=form)


@app.route('/login',methods=['GET','POST'])
def login():
	if request.method == 'POST':
		username = request.form['username']
		password_candidate = request.form['password']
		#cursor
		cur = mysql.connection.cursor()
		result = cur.execute("SELECT * FROM userS WHERE username = %s",[username])
		if(result>0):
			data = cur.fetchone()
			password = data['password']
			if sha256_crypt.verify(password_candidate,password):
				session['logged_in']=True
				session['username']=username
				flash('You are now logged in','success')
                                                                                                                                                                                                                                                                                                                                                                                                                        			return redirect(url_for('dashboard',id=username)			
			else:
				error="Invalid Login"
				return render_template('login.html',error=error)
			cur.close()
		else:
			error = "Username not found"
			return render_template('login.html',error=error)
	return render_template('login.html')


admin_pwd="akshay@1998"
pwd=sha256_crypt.encrypt(admin_pwd)

@app.route('/adminlogin',methods=['GET','POST'])
def adminlogin():
	if request.method == 'POST':
		username = request.form['username'] cccccccccccccc  
		password = request.form['password']
		if sha256_crypt.verify(password,pwd):
			session['logged_in']=True
			session['username']=username
			flash('You are now logged in','success')
			return redirect(url_for('adminpage'))
		else:
                        error="Invalid Login"
                        return render_template('login.html',error=error)
	return render_template('login.html')


@app.route('/adminpage')
def adminpage():
	return render_template('adminpage.html', semesters = Semesters)

@app.route('/semester/<string:id>')
def semester(id):
	return render_template('semester.html', id=id, courses = Courses)

@app.route('/course/<int:id>')
def course(id):
	cur = mysql.connection.cursor()
	if id == 1:
		sub="os"
	elif id==2:
		sub="cn"
	elif id==3:
		sub="java"
	elif id==4:
		sub="dbms"
	elif id==5:
		sub="ai"
	else:
		return "Coming Soon!"
	
        
	result = cur.execute("SELECT name,usn,"+sub+"_atnd,"+sub+"_cie1,"+sub+"_cie2,"+sub+"_cie3,"+sub+"_totalscore FROM fifthsem")
	students=cur.fetchall()
	if result>0:
        	return render_template('course.html',id=id, students=students)
	else:
		msg = "No Records Found"
		return render_template('course.html',msg=msg)
	cur.close()
	return render_template('course.html',msg=msg)

class StudentRecordForm(Form):
	name = StringField('Name', [validators.Length(min=1,max=100)])
	usn = StringField('USN',[validators.Length(min=1,max=20)])
	atnd = StringField('Attendance')
	cie1 = IntegerField('CIE 1')
	cie2 = IntegerField('CIE 2')
	cie3 = IntegerField('CIE 3')
	totalscore = IntegerField('Total Score')



@app.route('/update_student/<int:course_id>/<string:id>',methods=['GET','POST'])
def update_student(course_id,id):
	if course_id == 1:
                sub="os"
	elif course_id==2:
                sub="cn"
        elif course_id==3:
                sub="java"
        elif course_id==4:
                sub="dbms"
        elif course_id==5:
                sub="ai"
        else:
                return redirect(url_for('adminpage'))

        cur = mysql.connection.cursor()
        result = cur.execute("SELECT name,usn,"+sub+"_atnd,"+sub+"_cie1,"+sub+"_cie2,"+sub+"_cie3,"+sub+"_totalscore FROM fifthsem WHERE usn = %s",[id])
        record = cur.fetchone()
        form=StudentRecordForm(request.form)
        form.name.data = record['name']
        form.usn.data = record['usn']
	form.atnd.data = record[sub+'_atnd']
	form.cie1.data = record[sub+'_cie1']
	form.cie2.data = record[sub+'_cie2']
	form.cie3.data = record[sub+'_cie3']
	form.totalscore.data = record[sub+'_totalscore']
	if request.method == 'POST' and form.validate():
		name = request.form['name']
		usn = request.form['usn']
               	atnd = request.form['atnd']
                cie1 = int(request.form['cie1'])
		cie2 = int(request.form['cie2'])
		cie3 = int(request.form['cie3'])
		li=[cie1,cie2,cie3]
		i=0
		m=li[0]
		while i<3:
        		if li[i]>m:
                		m=li[i]
        		i = i+1
		first = li.pop(li.index(m))
		if li[0]>li[1]:
        		second = li[0]
		else:
        		second = li[1]
		totalscore = (int)(first + second) / 2 
                cur = mysql.connection.cursor()
                cur.execute("UPDATE fifthsem SET "+sub+"_atnd=%s, "+sub+"_cie1=%s, "+sub+"_cie2=%s, "+sub+"_cie3=%s, "+sub+"_totalscore=%s WHERE usn=%s",(atnd,cie1,cie2,cie3,totalscore,id))
                mysql.connection.commit()
                cur.close()
                flash("Record Updated","success")
		print course_id
                return redirect(url_for('course', id=course_id))
        return render_template('update_student.html',form=form)


#Check if user is logged in
def is_logged_in(f):
	@wraps(f)
	def wrap(*args, **kwargs):
		if 'logged_in' in session:
			return f(*args, **kwargs)
		else:
			flash('Unauthorized, Please login','danger')
			return redirect(url_for('login'))
	return wrap


@app.route('/logout')
def logout():
	session.clear()
	flash("You are now logged out","success")
	return redirect(url_for('index'))



@app.route('/dashboard/<string:id>')
@app.route('/dashboard')
@is_logged_in
def dashboard(id=None):
	cur = mysql.connection.cursor()
	result = cur.execute("SELECT * FROM fifthsem WHERE usn=%s",[id])
	record = cur.fetchone()
	if result>0:
		print "In if block"
		return render_template('dashboard.html',record=record)
	else:
		msg = "No Information! Please Register for SIS."
		return render_template('dashboard.html',msg=msg)
	cur.close()


class ArticleForm(Form):
        title = StringField('Title', [validators.Length(min=1,max=200)])
        body = TextAreaField('Body',[validators.Length(min=30)])

@app.route('/add_article',methods=['GET','POST'])
@is_logged_in
def add_article():
	form = ArticleForm(request.form)
	if request.method == 'POST' and form.validate():
		title = form.title.data
		body = form.body.data
		cur = mysql.connection.cursor()
		cur.execute("INSERT INTO articles(title, body, author) VALUES(%s, %s, %s)",(title,body,session['username']))
		mysql.connection.commit()
		cur.close()
		flash("Article created","success")
		return redirect(url_for("dashboard"))
	return render_template('add_article.html',form=form)


@app.route('/edit_article/<string:id>',methods=['GET','POST'])
@is_logged_in
def edit_article(id):
	cur = mysql.connection.cursor()
	result = cur.execute("SELECT * FROM articles WHERE id = %s",[id])
	article = cur.fetchone()
	form=ArticleForm(request.form)
	form.title.data = article['title']
	form.body.data = article['body']
	if request.method == 'POST' and form.validate():
                title = request.form['title']
                body = request.form['body']
                cur = mysql.connection.cursor()
                cur.execute("UPDATE articles SET title=%s, body=%s WHERE id=%s",(title,body,id))
                mysql.connection.commit()
                cur.close()
                flash("Article Updated","success")
                return redirect(url_for("dashboard"))
        return render_template('edit_article.html',form=form)




@app.route('/delete_article/<string:id>',methods=['POST'])
@is_logged_in
def delete_article(id):
	cur = mysql.connection.cursor()
	cur.execute("DELETE FROM articles WHERE id=%s",[id])
	mysql.connection.commit()
	flash('Article Deleted','success')
	cur.close()
	return redirect(url_for('dashboard'))


class SISRegisterForm(Form):
        name = StringField('Name', [validators.Length(min=1,max=50)])
        usn = StringField('USN',[validators.Length(min=4,max=25)])
        email = StringField('Email',[validators.Length(min=6,max=50)])
        branch = StringField('Branch',[validators.Length(min=2,max=20)])
	sem = IntegerField('Semester',[validators.NumberRange(min=0, max=10)])

@app.route('/register_sis',methods=['GET','POST'])
def register_sis():
	form = SISRegisterForm(request.form)
        if request.method == 'POST' and form.validate():
                name = form.name.data
                email = form.email.data
                usn = form.usn.data
                branch = form.branch.data
		sem = form.sem.data
                #cursor
                cur = mysql.connection.cursor()
                cur.execute("INSERT INTO students(name, usn, email, branch,sem) VALUES(%s, %s, %s, %s, %s)",(name,usn,email,branch,sem))
		cur.execute("INSERT INTO fifthsem(name,usn,email,sem) VALUES(%s, %s, %s, %s)",(name,usn,email,sem))
                mysql.connection.commit()
                cur.close()
                flash('You are now registered into SIS and can get your updates of your attendance and CIE score','success')
                return redirect(url_for('dashboard',id=usn))

        return render_template('sisregister.html',form=form)


	
@app.route('/upload',methods=['POST'])
def upload():
	f = request.files['inputFile']
	cur = mysql.connection.cursor()
	name=f.filename
	data=f.read()
        cur.execute("INSERT INTO filecontents(name,data) VALUES(%s, %s)",(name,data))    
        mysql.connection.commit()
        cur.close()
	return f.filename+" Saved to database"


@app.route('/download/<string:name>')
def download(name):
	cur = mysql.connection.cursor()
	result=cur.execute("SELECT name,data FROM filecontents WHERE name=%s",[name])	
	file_data = cur.fetchone()
	return send_file(BytesIO(file_data['data']),attachment_filename=file_data['name'],as_attachment=True)	


@app.route('/file_contents')
def file_contents():
        cur = mysql.connection.cursor()
        result = cur.execute("SELECT * FROM filecontents")
        files = cur.fetchall()
        if result>0:
                return render_template('file_contents.html',files=files)
        else:
                msg = "No Documents Found"
                return render_template('file_content.html',msg=msg)
        cur.close()

		
if __name__ == '__main__':
	app.secret_key='secret123'
	app.run(debug=True,port=8000)

