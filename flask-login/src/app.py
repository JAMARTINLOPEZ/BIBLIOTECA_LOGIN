from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mysqldb import MySQL
from config import config
from flask_wtf.csrf import CSRFProtect
import paho.mqtt.client as mqtt
from flask_login import LoginManager, login_user, logout_user, login_required



mqtt_broker = "172.16.0.99"
mqtt_port = 1883
mqtt_topic = "homeassistant/biblioteca"

client=mqtt.Client()



# Models
from models.ModelUser import ModelUser

#entities
from models.entities.User import User

app = Flask(__name__)
csrf = CSRFProtect()
db=MySQL(app)
login_manager_app = LoginManager(app)

@login_manager_app.user_loader
def load_user(id):
    return ModelUser.get_by_id(db,id)


@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        #print(request.form['email'])
        #print(request.form['password'])
        user =User(0,request.form['email'], request.form['password'])
        logged_user = ModelUser.login(db,user)
        if logged_user!=None:
            if logged_user.password:
                login_user(logged_user)
                client.connect(mqtt_broker,mqtt_port)
                client.username_pw_set(username="raspi_dali_1", password="admin")
                client.publish(mqtt_topic, "ON")
                client.disconnect()
                return redirect(url_for('home'))
            else:
                flash("Invalid Password")
                return render_template('auth/login.html')
        else:
            flash("User not found")
            return render_template('auth/login.html')
    else:
        return render_template('auth/login.html')
    

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))
@app.route('/home')
def home():
    return render_template('home.html')
@app.route('/protected')
@login_required
def protected():
    return "<h1>Vista protegida</h1>"

def status_401(error):
    return redirect(url_for('login'))

def status_404(error):
    return "<h1>Pagina no encontrada</h1>", 404

if __name__=='__main__':
    app.config.from_object(config['development'])
    csrf.init_app(app)
    app.register_error_handler(401, status_401)
    app.register_error_handler(404, status_404)
    app.run(host='0.0.0.0', port='5000')
