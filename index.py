from flask import Flask 
from flask import render_template
from flask import request
from flask import redirect
from flask import flash
from flask import session
from flask import url_for

import random
from flask_mail import * 
#made by sagnik

import urllib.request
import os
import datetime
from werkzeug.utils import secure_filename

from flask_pymongo import PyMongo

app = Flask(__name__)

UPLOAD_FOLDER = 'static/uploads/'

#Flask mail configuration  
app.config['MAIL_SERVER']='smtp.gmail.com'  
app.config['MAIL_PORT']=465  
app.config['MAIL_USERNAME'] = 'sagniksahoo123@gmail.com'  
app.config['MAIL_PASSWORD'] = '9734449696'  
app.config['MAIL_USE_TLS'] = False 
app.config['MAIL_USE_SSL'] = True  
  
#instantiate the Mail class  
mail = Mail(app)  

app.secret_key = "secret key"  #for create session and upload files
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

ALLOWED_EXTENSIONS = set(['png','jpg','jpeg','gif','jfif'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS

# mongodb_client = PyMongo(app, uri="mongodb://localhost:27017/sagnik_2000")
mongodb_client = PyMongo(app, uri="mongodb+srv://priyankajana:priyanka@cluster0.rx10naq.mongodb.net/?retryWrites=true&w=majority")
db = mongodb_client.db
 
@app.route('/')  #main page
def indexpage():  
    return render_template('index.html')

@app.route('/pic') #pic page 
def aboutpage():  
    return render_template('pic.html')  

@app.route('/tem')  #team page
def teampage():  
    return render_template('tem.html')  

@app.route('/contact',methods=["get","post"] )  #contact page
def contactpage():
    if request.method == 'GET':  
        return render_template('contact.html')
    else:
        uname = request.form['fullname'] 
        x = datetime.datetime.now() #date time auto 
        x = ''+str(x)   

        db.contactcollection.insert_one(
        {'username': uname,
         'useremail': request.form['email'],
         'usertext': request.form['alltext'],
         'regdate' : x,
        })
        return render_template('contact.html',msg = "data sucessfully send")

@app.route('/practice', methods=["get","post"])  #sign up page
def practicepage():  
    if request.method == 'GET':
        return render_template('practice.html') 
    else:
        uname = request.form['fullname'] 
        x = datetime.datetime.now() 
        x = ''+str(x)
        #print(x)
        userobj = db.usercollection.find_one(
        {'useremail':request.form['email']})
        print(userobj)


        if userobj:
            #print(userobj['username])
            return render_template('practice.html',msg = "ALREADY REGISTERED")
        else:
            uname = request.form['fullname']    
        
            db.usercollection.insert_one(
            {'username': uname,
            'useremail': request.form['email'],
            'usermobile': request.form['mobile'],
            'userjob': request.form['job'],
            'userpass': request.form['pass'],
            'regdate' : x,
            })
            msg = Message('conformation', sender = 'sagniksahoo123@gmail.com', recipients=[request.form['email']])  
            msg.body = 'hi, your registration is successfull'  
            mail.send(msg)
            return render_template('practice.html',msg = "REGISTRATION SUCCESSFUL")   
         


@app.route('/flogin', methods=["GET", "POST"])  #log in page
def loginpage(): 
    if request.method == 'GET': 
        return render_template('flogin.html')
    else:
        user = db.usercollection.find_one(
        {'username': request.form['fullname'],
         'userpass': request.form['pass']
        })
        print(user)
        
        if user:
            session['uemail']= user['useremail']
            session['uname'] = user['username']
            session['usertype']= 'USER'
            
            #print(user['username'])
            return render_template('ualog.html', uname = user['username'])
        else:
            return render_template('flogin.html', errormsg = "INVALID UID OR PASSWORD")

@app.route('/logout')  #for log out
def logout():  
    if 'usertype' in session:
        utype = session['usertype']
        if utype == 'ADMIN':
            session.pop('usertype',None)
        else: 
            session.pop('usertype',None)
            session.pop('uemail',None)
            session.pop('uname',None)
        return redirect(url_for('indexpage'));    
    else:  
        return redirect(url_for('adminloginpage'));

@app.route('/ualog',methods = ['GET','POSt'])  #user after log in
def ualogpage():
    uname = session['uname']  
    userobj = db.usercollection.find({})
    print(userobj)
    return render_template('ualog.html',userdata = userobj,uname = session['uname'])  

##############################################################################################

@app.route('/adlog', methods=['GET','POST'])  #admin login
def adminloginpage(): 
    if request.method == 'GET':
        return render_template('adlog.html')
    else:      
        adminuid = request.form['adminuserid']
        adminpass = request.form['adminpassword']

        if(adminuid == 'admin' and adminpass == 'admin'):
            return render_template('adalog.html')
        else:
            return render_template('adlog.html', msg = 'INVALID UID OR PASS')

@app.route('/adminhome')  #admin after log in
def adminafterlogin(): 
    return render_template('adalog.html')

################################################################################################

@app.route('/viewall')  #view all registerd user details
def viewall(): 
    userobj = db.usercollection.find({})
    print(userobj)
    return render_template('view.html', userdata = userobj)

@app.route('/conv')  #view all contact persons details
def contactvll(): 
    userobj = db.contactcollection.find({})
    print(userobj)
    return render_template('conv.html', userdata = userobj)

@app.route('/upload', methods=["get","post"])  #upload images
def upload():
    if request.method == 'GET':
        return render_template('upload.html')
    else:
        #uname = request.form['fullname']   
        x = datetime.datetime.now() 
        x = ''+str(x) #for date auto genrate

       
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash('No image selected for uploading')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        #print('upload_image filename: ' + filename)
        flash('Image successfully uploaded')
        ppath = 'static/uploads/'+filename
        
        uname = session['uname']

        n = str(random.randint(0,9999))

        db.uploadcollection.insert_one(
           {'username': uname,
            'pthotoid':n,
            'catagory': request.form['cata'] ,
            'udate': x,
            'udes': request.form['des'],
            'image': ppath
        })
        return render_template('upload.html', filename=filename)
    else:
        flash('Allowed image types are - png, jpg, jpeg, gif')
        return redirect(request.url)
############################################################################

@app.route('/adminviewallimg')  #admin view all uploaded images
def adviallimg(): 
    uobj = db.uploadcollection.find({})
    print(uobj)
    return render_template('adminviewimage.html', userdata = uobj)


##########################################################################
# @app.route('/imageinfo', methods=['GET','POST'])  
# def image(): 
#     if request.method == 'GET':
#         return render_template('userimagesearch.html')
#     else:      
#         uobj = db.uploadcollection.find_one({'username': request.form['uname']})
#         print(uobj)
        
#         if uobj:
#             #print(userobj['username'])
#             return render_template('userimagesearch.html', userdata = uobj,show_results=1)
#         else:
#             return render_template('userimagesearch.html', errormsg = "INVALID EMAIL ID")


#######################################################################################################

######################################################################################################
######################################################################################################
@app.route('/userimageinfo', methods=['GET','POST'])  #user can see his all uploaded images
def searchUser1(): 
    # if request.method == 'GET':
    #     return render_template('userimageallsearch.html')
    # else:      
    userobj = db.uploadcollection.find({'username': session['uname']})
        #print(userobj['username'])
                
    if userobj:
        return render_template('userimageallsearch.html', userdata = userobj,show_results=1)
    else:
        return render_template('userimageallsearch.html', errormsg = "no image found")
########################################################################################################

@app.route('/adminimagesearch', methods=['GET','POST'])  #admin search user uploaded images
def adminimgsearch(): 
    if request.method == 'GET':
        return render_template('adminsearchimage.html')
    else:      
        userobj = db.uploadcollection.find({'username': request.form['uname']})
        #print(userobj['username'])
                
        if userobj:
            return render_template('adminsearchimage.html', userdata = userobj,show_results=1)
        else:
            return render_template('adminsearchimage.html', errormsg = "INVALID USER NAME")

########################################################################################################
@app.route('/userallviewimage', methods=['GET','POST'])  #userdownloadimage
def userdownloadimg(): 
    if request.method == 'GET':
        return render_template('allviewimage.html')
    else:      
        userobj = db.uploadcollection.find({'catagory': request.form['cata']})
        print(userobj)
                
        if userobj:
            return render_template('allviewimage.html', userdata = userobj,show_results=1)
        else:
            return render_template('allviewimage.html', errormsg = "INVALID CATAGORY NAME")




########################################################################################################


@app.route('/search', methods=['GET','POST'])  #admin seach user and his details
def searchUser(): 
    if request.method == 'GET':
        return render_template('searchuser.html')
    else:      
        userobj = db.usercollection.find_one(
        {'useremail': request.form['email']})
        print(userobj)
        
        if userobj:
            #print(userobj['username'])
            return render_template('searchuser.html', userdata = userobj,show_results=1)
        else:
            return render_template('searchuser.html', errormsg = "INVALID EMAIL ID")

###########################################################################################

@app.route('/delete', methods=['GET','POST'])  #for search and delele
def deleteUser(): 
    if request.method == 'GET':
        return render_template('deleteuser.html')
    else:      
        responsefrommongodb = db.usercollection.find_one_and_delete(
        {'useremail': request.form['email']})
        print(responsefrommongodb)
        if responsefrommongodb is not None:
            return render_template('deleteuser.html', msg = "SUCCESSFULLY DETELED")
        return render_template('deleteuser.html', msg = "INVALID EMAIL ID")


@app.route('/delete1', methods=['POST'])  #for delete user details
def deleteUser1():
    print(request.form['email']) 
    responsefrommongodb = db.usercollection.find_one_and_delete({'useremail': request.form['email']})
    print(responsefrommongodb)
    return redirect(url_for('viewall'))


@app.route('/delete2', methods=['POST'])  #search usser and delete
def deleteUser2():
    print(request.form['email']) 
    responsefrommongodb = db.usercollection.find_one_and_delete({'useremail': request.form['email']})
    print(responsefrommongodb)
    return redirect(url_for('searchUser'))


# @app.route('/delete3', methods=['POST'])  
# def deleteUser3():
#     print(request.form['photoid']) 
#     responsefrommongodb = db.uploadcollection.find_one_and_delete({'photoid': request.form['photoid']})
#     print(responsefrommongodb)
#     return redirect(url_for('adminimgsearch'))


@app.route('/delete3', methods=['POST'])  #image search and delete
def deleteUser3():
    print(request.form['photoid']) 
    responsefrommongodb = db.uploadcollection.find_one_and_delete({'pthotoid': request.form['photoid']})
    print(responsefrommongodb)
    return redirect(url_for('adminimgsearch'))



@app.route('/delete4', methods=['POST'])  #
def deleteUser4():
    print(request.form['photoid']) 
    responsefrommongodb = db.uploadcollection.find_one_and_delete({'pthotoid': request.form['photoid']})
    print(responsefrommongodb)
    return redirect(url_for('adviallimg'))


@app.route('/userimageallsearch')  #user image all search
def userimageallsearch(): 
    return render_template('userimageallsearch.html')


@app.route('/delete5', methods=['POST'])  #user image search and delete
def deleteUser5():
    print(request.form['picid']) 
    responsefrommongodb = db.uploadcollection.find_one_and_delete({'catagory': request.form['picid']})
    print(responsefrommongodb)
    return redirect(url_for('searchUser1'))


@app.route('/delete6', methods=['POST'])  #for delete user details
def deleteUser6():
    print(request.form['email']) 
    responsefrommongodb = db.contactcollection.find_one_and_delete({'useremail': request.form['email']})
    print(responsefrommongodb)
    return redirect(url_for('contactvll'))

#############################################################################################

@app.route('/viewuserprofile')  #user  view and update his profile
def viewUserProfile(): 
    uemail = session['uemail']      
    userobj = db.usercollection.find_one({'useremail': uemail})
    print(userobj)
    return render_template('viewuserprofile.html', userdata = userobj)

@app.route('/updateuserprofile1', methods=["GET", "POST"])  #user update his profile
def updateUserProfile():
    if request.method == 'GET':
        uemail = session['uemail']      
        userobj = db.usercollection.find_one({'useremail': uemail})
        return render_template('updateuserprofile1.html',userdata = userobj)
    else:
        db.usercollection.update_one( {'useremail': session['uemail'] },
        { "$set": { 'usermobile': request.form['mobile'],
                    'userpass': request.form['pass'],
                    'userjob': request.form['job'] 
                  } 
        })
        return redirect(url_for('viewUserProfile'))

if __name__ == '__main__':  
   app.run(debug = True)  