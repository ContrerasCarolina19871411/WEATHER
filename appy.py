from flask import Flask,render_template, request, url_for,redirect
import requests 
from dotenv import load_dotenv,dotenv_values 

# primero se instala la libreria  pip install Flask-SQLAlchemy
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped, mapped_column

config = dotenv_values('.env')
app = Flask(__name__)

# Creamos la cadena de conecxion
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///weather.sqlite"

# Vinculamos la base de datos con la app
db = SQLAlchemy(app)

# Creamos el modelo
class City(db.Model):
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True,autoincrement=True)
    name: Mapped[str] = mapped_column(db.String, unique=True, nullable=False)

# con esta sentencia se crea las tablas 
with app.app_context():
    db.create_all()

def get_weather_data(city):
    API_KEY = config['API_KEY']
    url = f'http://api.openweathermap.org/data/2.5/weather?q={ city }&units=metric&lang=es&appid={API_KEY}'
    r = requests.get(url).json()
    return r

@app.route('/about')
def about():
    return render_template('about.html')

# pongo los metodos disponibles
@app.route('/clima', methods=['GET','POST'])
def clima():
    # Si es post es que pulson el boton Agregar Ciudad
    if request.method == 'POST' :
        new_city = request.form.get('city')
        if new_city:
            obj = City(name=new_city)
            db.session.add(obj)
            db.session.commit()

    # llamo a todas las ciudades select * from city
    cities = City.query.all()
    weather_data = []

    for city in cities:
        r=get_weather_data(city.name)
        weather = {
                'city' : city.name,
                'temperature' : r['main']['temp'],
                'description' : r['weather'][0]['description'],
                'icon' : r['weather'][0]['icon'],
                }
        weather_data.append(weather)
    
    return render_template('weather.html',weather_data=weather_data)


@app.route('/delete_city/<name>')
def delete_city(name):
    city= City.query.filter_by(name=name).first()
    db.session.delete(city)
    db.session.commit()
    return redirect(url_for('clima'))


if __name__ == '_main_':
    app.run(debug=True)
