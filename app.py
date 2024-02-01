from flask import Flask,url_for,flash,render_template,redirect,request,session
from flask_mail import Mail,Message
import pymysql,secrets,re,random
import bcrypt
import base64

app=Flask(__name__)

connection=pymysql.connect(
                host='localhost',
                user='root',
                password='',
                database='shop1'
            )

app.secret_key="kipkogeitobiaskurgat"

app.config["MAIL_SERVER"]='smtp.gmail.com'
app.config["MAIL_PORT"]=465
app.config["MAIL_USERNAME"]='tobiaskipkogei@gmail.com'
app.config["MAIL_PASSWORD"]='himfefhwbqyfhekg'
app.config["MAIL_USE_TLS"]=False
app.config["MAIL_USE_SSL"]=True
mail=Mail(app)


@app.route("/")
def index():
    return render_template("index.html")

def generate_otp():
    return ''.join(random.choices('0123456789',k=6))


@app.route("/register",methods=["POST","GET"])
def register():
    if 'username' in session:
        return redirect(url_for("login"))
    else:
        if request.method=='POST':
            username=request.form['username']
            email=request.form['email']
            password=request.form['password']
            confirm=request.form['confirm']
            cur=connection.cursor()
            cur.execute("SELECT * FROM register WHERE username=%s",(username))
            connection.commit()
            data=cur.fetchone()
            if data:
                flash(f"The username already exist")
                return redirect(url_for("register"))
            else:
                cur=connection.cursor()
                cur.execute("SELECT * FROM register WHERE email=%s",(email))
                connection.commit()
                data=cur.fetchone()
                if data:
                    flash(f"The email has an account","danger")
                    return redirect(url_for("register"))
                elif password!=confirm:
                    flash(f"the password doesn't match")
                    return redirect(url_for("register"))
                else:
                    verify=0
                    otp=generate_otp()
                    cur=connection.cursor()
                    cur.execute("INSERT INTO register(username,email,password,otp,verify) VALUES(%s,%s,%s,%s,%s)",(username,email,password,otp,verify))
                    connection.commit()
                    connection.close()
                    msg=Message (subject='Account creation',sender="tobiaskipkogei@gmail.com" ,recipients=[email])
                    msg.body=f"""Your have succesfully created and account at our page
                                your USERNAME is{username}
                                And Password is*{password}*
                                your otp is {otp}
                                """
                    mail.send(msg)
                    send_otp(otp,email)
                    flash(f"An otp-code as been sent to your account","success")
                    return redirect(url_for("verify_otp"))
    return render_template("register.html")

@app.route("/send_otp")
def send_otp(otp,email):
    msg=Message(subject="Your OTP_CODE",sender="tobiaskikogei@gmil.com",recipients=[email])
    msg.body=f""" Your otp code is:{otp}
                Verify it!!!"""
    mail.send(msg)


@app.route("/verify_otp",methods=["POST","GET"])
def verify_otp():
    if request.method=="POST":
        user_otp=request.form['user_otp']
        cur=connection.cursor()
        cur.execute("SELECT * FROM register WHERE otp=%s",(user_otp))
        connection.commit()
        data=cur.fetchone()
        if data:
            verify=1
            cur=connection.cursor()
            cur.execute("UPDATE register SET verify=%s where otp=%s",(verify,user_otp))
            connection.commit()
            cur.close()
            flash(f"OTP has been verified success","success")
            return redirect(url_for("login"))
        else:
            flash(f"Invalid OTP.Please try again.","danger")
            return redirect(url_for("verify_otp"))
    return  render_template("otp.html")
    

@app.route("/login",methods=["POST","GET"])
def login():
    if 'username' in session:
        return redirect(url_for("home"))
    else:
        if request.method=="POST":
            username=request.form['username']
            password=request.form['password']
            cur=connection.cursor()
            cur.execute("SELECT * FROM register WHERE (username OR email )=%s",(username))
            connection.commit()
            data=cur.fetchone()
            if data is not None:
                verified=int(data[6])
                if verified==1:
                    session['username']=data[1]
                    session['password']=data[3]
                    flash(f"You have logged in successfully","success")
                    return redirect(url_for('home'))
                else:
                    flash(f"PLEASE VERIFY YOUR ACCOUNT!!!","warning")
                    return redirect(url_for('verify_otp'))
            else:
                flash(f"No user with that account","danger")
                return render_template("login.html",username=username,password=password) 
    return render_template("login.html")

@app.route("/forgot",methods=["POST","GET"])
def forgot():
    if request.method=='POST':
        email=request.form['email']
        cur=connection.cursor()
        cur.execute("SELECT * FROM register WHERE email=%s",(email))
        connection.commit()
        data=cur.fetchone()
        if data:
            token=secrets.token_hex(32)
            reset_link=url_for('reset',token=token,_external=True)
            msg=Message(subject="Pasword Reset",sender="tobiaskipkogei@gmail.com",recipients=[email])
            msg.body=f"""Your are about to reset your password
                        Click the link to RESET your password:{reset_link}"""
            mail.send(msg)
            cur=connection.cursor()
            cur.execute("UPDATE register SET token=%s WHERE email=%s",(token,email))
            connection.cursor()
            cur.close()
            flash(f"Check your email to reset your password")
            return redirect(url_for("forgot"))
        else :
            flash(f"The email has not registered account","danger")
            return render_template("forgot.html")
    return render_template("forgot.html")
@app.route("/reset",methods=["POST","GET"])
def reset():
    if request.method=='POST':
        password=request.form['password']
        confirm=request.form['confirm']
    return render_template("reset.html")

@app.route("/home")
def home():

    return render_template("index.html")

@app.route("/shop",methods=["POST","GET"])
def shop():
    cur=connection.cursor()
    cur.execute("SELECT * FROM uploads")
    connection.commit()
    data=cur.fetchall()   
    new_data=[]
    for row in data:
        img=row[2]
        image = base64.b64encode(img).decode('utf-8')
        all_image=list(row)
        all_image[2]=image
        new_data.append(all_image)
    cur.close()
    return render_template("shop.html",new_data=new_data)

@app.route("/categories")
def categories():
    return render_template("categories.html")



@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/admin",methods=["POST","GET"])
def admin():
    if request.method=="POST":
        product_name=request.form['product_name']
        product=request.files['product'].read()
        product_category=request.form['product_category']
        product_price=request.form['product_price']
        cur=connection.cursor()
        cur.execute("INSERT INTO uploads(product_name,product,product_price,product_category) VALUES(%s,%s,%s,%s)",(product_name,product,product_price,product_category))
        connection.commit()
        cur.close()
        return redirect(url_for("shop"))
    return render_template("admin.html")


@app.route("/cart/<id>")
def cart(id):
    cur=connection.cursor()
    cur.execute("SELECT * FROM uploads WHERE id=%s",(id))
    connection.commit()
    data=cur.fetchall()
    new_data=[]
    for row in data:
        img=row[2]
        image = base64.b64encode(img).decode('utf-8')
        all_image=list(row)
        all_image[2]=image
        new_data.append(all_image)
        product=row[2]
        description=row[1]
        price=row[4]
        quantity=2
        total=quantity*price
        
    cur.close()
    cur=connection.cursor()
    cur.execute("INSERT INTO carts(id,product,description,price,quantity,total) VALUES (%s,%s,%s,%s,%s,%s)",(id,product,description,price,quantity,total))
    connection.commit()
    cur.close()
    return redirect(url_for("add_cart",id=id))

@app.route("/add_cart/<id>")
def add_cart(id):
    cur=connection.cursor()
    cur.execute("SELECT * FROM carts WHERE id=%s",(id))
    connection.commit()
    data=cur.fetchall()
    new_data=[]
    for row in data:
        image=row[1]
        image = base64.b64encode(image).decode('utf-8')
        all_image=list(row)
        all_image[1]=image
        new_data.append(all_image)
    cur.close()
    return render_template("cart.html",new_data=new_data)
@app.route("/remove/<id>")
def remove(id):
    cur=connection.cursor()
    cur.execute("DELETE FROM carts WHERE id=%s",(id))
    connection.commit()
    cur.close()
    return redirect(url_for("add_cart",id=id))
if __name__=="__main__":
    app.run(debug=True)
    