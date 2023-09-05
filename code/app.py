import time
import csv
from core.error_event import ErrorEvent

from flask import Flask, render_template, request
from core.FloatModbusClient import FloatModbusClient
from threading import Thread
from flask_socketio import SocketIO, emit
from flask import Flask, render_template, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'bristol'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False,
                         unique=True)  # can't be null and length can be up to 20 characters
    password = db.Column(db.String(80), nullable=False)

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def __repr__(self):
        return f'user: {self.username}'

    @property
    def is_active(self):
        return True

    @property
    def is_authenticated(self):
        return True

    def get_id(self):
        return str(self.id)


class Attack(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False,
                         unique=False)
    password = db.Column(db.String(80), nullable=False)

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def __repr__(self):
        return f'user: {self.username} password: {self.password}'


class LoginForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)],
                           render_kw={"placeholder": "Username"})
    password = PasswordField(validators=[InputRequired(), Length(min=4, max=80)],
                             render_kw={"placeholder": "Password"})
    submit = SubmitField("Login")


rw_client = FloatModbusClient("127.0.0.1", port=12344, auto_open=True)
client = FloatModbusClient("127.0.0.1", port=12345, auto_open=True)
dis_client = FloatModbusClient("127.0.0.1", port=12346, auto_open=True)
st_client = FloatModbusClient("127.0.0.1", port=12347, auto_open=True)
socketio = SocketIO(app)

# settings for raw water plc

rw_flow_in_flag = True
rw_flow_out_flag = True
rw_flow_in = True
rw_flow_out = True

rw_running_flag = False
rw_running = True

rw_speed_flag = False
rw_speed = 5

# settings for filter plc

flow_in_flag = False
flow_in = True
flow_out_flag = False
flow_out = False

filter_switch_flag = False
new_filter_running = True

sand_switch_flag = False
new_sand_mode = 1

gravel_switch_flag = False
new_gravel_mode = 1

# settings for disinfection plc

dis_flow_in_flag = True
dis_flow_out_flag = True
dis_flow_in = True
dis_flow_out = True

dis_running_flag = False
dis_running = True

dis_automatic_flag = False
dis_automatic = True

chlorine_flag = False
chlorine = 0.8
concentration_flag = False
concentration = 50

# settings for storage plc

st_flow_in_flag = True
st_flow_out_flag = True
st_flow_in = True
st_flow_out = True

st_running_flag = False
st_running = True

st_speed_flag = False
st_speed = 5

st_automatic = True
st_automatic_flag = True


def rw_speed_change():
    rw_client.open()
    rw_client.write_single_register(4, rw_speed)
    rw_client.close()


def rw_flow_in_switch():
    rw_client.open()
    rw_client.write_single_register(5, rw_flow_in)
    rw_client.close()


def rw_flow_out_switch():
    rw_client.open()
    rw_client.write_single_register(6, rw_flow_out)
    rw_client.close()


def rw_running_switch():
    rw_client.open()
    rw_client.write_single_register(7, rw_running)
    rw_client.close()


def st_speed_change():
    st_client.open()
    st_client.write_single_register(4, st_speed)
    st_client.close()


def st_flow_in_switch():
    st_client.open()
    st_client.write_single_register(5, st_flow_in)
    st_client.close()


def st_flow_out_switch():
    st_client.open()
    st_client.write_single_register(6, st_flow_out)
    st_client.close()


def st_automatic_switch():
    st_client.open()
    st_client.write_single_register(7, st_running)
    st_client.close()


def st_running_switch():
    st_client.open()
    st_client.write_single_register(8, st_running)
    st_client.close()


rw_water_level_low = ErrorEvent("\nwater level in raw water tank is too low", -1, 15)
rw_water_level_high = ErrorEvent("\nwater level in raw water tank is too high", 1, 135)
filter_water_level_low = ErrorEvent("\nwater level in filter water tank is too low", -1, 10)
filter_water_level_high = ErrorEvent("\nwater level in filter water tank is too high", 1, 90)
dis_water_level_low = ErrorEvent("\nwater level in disinfection water tank is too low", -1, 10)
dis_water_level_high = ErrorEvent("\nwater level in disinfection water tank is too high", 1, 90)
st_water_level_low = ErrorEvent("\nwater level in storage water tank is too low", -1, 15)
st_water_level_high = ErrorEvent("\nwater level in storage water tank is too high", 1, 135)
sand_efficiency = ErrorEvent("\nsand efficiency is too low, change a new one", -1, 10)
gravel_efficiency = ErrorEvent("\ngravel efficiency is too low, change a new one", -1, 10)
concentration_low = ErrorEvent("\nNot enough chlorine is too low", -1, 0.2)
concentration_high = ErrorEvent("\nNot enough chlorine is too high", 1, 2)


def alarm_check(rw_water_level, filter_water_level
                , dis_water_level, st_water_level
                , sand_efficiency_rate, gravel_efficiency_rate
                , concentration):
    error_message = ""
    sound_alarm = False
    error_message += rw_water_level_high.check(rw_water_level)
    error_message += rw_water_level_low.check(rw_water_level)
    error_message += filter_water_level_low.check(filter_water_level)
    error_message += filter_water_level_high.check(filter_water_level)
    error_message += dis_water_level_low.check(dis_water_level)
    error_message += dis_water_level_high.check(dis_water_level)
    error_message += st_water_level_low.check(st_water_level)
    error_message += st_water_level_high.check(st_water_level)
    error_message += sand_efficiency.check(sand_efficiency_rate)
    error_message += gravel_efficiency.check(gravel_efficiency_rate)
    error_message += concentration_low.check(concentration)
    error_message += concentration_high.check(concentration)

    sound_alarm = rw_water_level_high.get_alarmed() \
                  or rw_water_level_low.get_alarmed() \
                  or filter_water_level_high.get_alarmed() \
                  or filter_water_level_low.get_alarmed() \
                  or dis_water_level_low.get_alarmed() \
                  or dis_water_level_high.get_alarmed() \
                  or st_water_level_low.get_alarmed() \
                  or st_water_level_high.get_alarmed() \
                  or sand_efficiency.get_alarmed() \
                  or gravel_efficiency.get_alarmed() \
                  or concentration_low.get_alarmed() \
                  or concentration_high.get_alarmed()

    return error_message, sound_alarm


@socketio.on('stop_alarm', namespace='/dynamic')
def stop_alarm():
    rw_water_level_low.turn_off_alarm()
    rw_water_level_high.turn_off_alarm()
    filter_water_level_low.turn_off_alarm()
    filter_water_level_high.turn_off_alarm()
    dis_water_level_low.turn_off_alarm()
    dis_water_level_high.turn_off_alarm()
    st_water_level_low.turn_off_alarm()
    st_water_level_high.turn_off_alarm()
    sand_efficiency.turn_off_alarm()
    gravel_efficiency.turn_off_alarm()
    concentration_low.turn_off_alarm()
    concentration_high.turn_off_alarm()

def read_data():
    global sand_switch_flag, filter_switch_flag, gravel_switch_flag, flow_in_flag, flow_out_flag
    global dis_automatic_flag, dis_running_flag, dis_flow_out_flag, dis_flow_in_flag
    global rw_speed_flag, rw_running_flag, rw_flow_in_flag, rw_flow_out_flag
    global st_speed_flag, st_running_flag, st_flow_in_flag, st_flow_out_flag, st_automatic_flag
    global concentration_flag, chlorine_flag

    while True:
        client.open()
        float_list = client.read_floats(0, 6)
        is_running = client.read_holding_registers(12)[0]
        gravel_mode = client.read_holding_registers(13)[0]
        sand_mode = client.read_holding_registers(14)[0]
        flow_in_valve = client.read_holding_registers(15)[0]
        flow_out_valve = client.read_holding_registers(16)[0]
        client.close()
        data = {
            'water_level': float_list[0],
            'temperature': float_list[1],
            'turbidity': float_list[2],
            'dissolved_solids': float_list[3],
            'gravel_efficiency': float_list[4],
            'sand_efficiency': float_list[5],
            'filter_running': is_running,
            'gravel_mode': gravel_mode,
            'sand_mode': sand_mode,
            'flow_in': flow_in_valve,
            'flow_out': flow_out_valve
        }

        socketio.emit('update_data', data, namespace='/dynamic')

        if flow_in_flag:
            flow_in_switch()
            flow_in_flag = False

        if flow_out_flag:
            flow_out_switch()
            flow_out_flag = False

        if gravel_switch_flag:
            gravel_switch()
            gravel_switch_flag = False

        if sand_switch_flag:
            sand_switch()
            sand_switch_flag = False

        if filter_switch_flag:
            filter_switch()
            filter_switch_flag = False

        dis_client.open()
        dis_float_list = dis_client.read_floats(0, 6)
        dis_is_running = dis_client.read_holding_registers(12)[0]
        dis_flow_in_valve = dis_client.read_holding_registers(13)[0]
        dis_flow_out_valve = dis_client.read_holding_registers(14)[0]
        dis_is_automatic = dis_client.read_holding_registers(15)[0]
        dis_client.close()
        dis_data = {
            'dis_water_level': dis_float_list[0],
            'dis_temperature': dis_float_list[1],
            'dis_chlorine': dis_float_list[2],
            'dis_expected_concentration': dis_float_list[3],
            'dis_real_concentration': dis_float_list[4],
            'dis_ph': dis_float_list[5],
            'dis_running': dis_is_running,
            'dis_flow_in': dis_flow_in_valve,
            'dis_flow_out': dis_flow_out_valve,
            'dis_is_automatic': dis_is_automatic
        }
        socketio.emit('dis_data', dis_data, namespace='/dynamic')

        if dis_automatic_flag:
            automatic_switch()
            dis_automatic_flag = False

        if dis_running_flag:
            dis_running_switch()
            dis_running_flag = False

        if dis_flow_in_flag:
            dis_flow_in_switch()
            dis_flow_in_flag = False

        if dis_flow_out_flag:
            dis_flow_out_switch()
            dis_flow_out_flag = False

        if concentration_flag:
            change_concentration()
            concentration_flag = False

        if chlorine_flag:
            change_chlorine()
            chlorine_flag = False


        rw_client.open()
        rw_float_list = rw_client.read_floats(0, 2)
        rw_pump_in_speed = rw_client.read_holding_registers(4)[0]
        rw_flow_in_valve = rw_client.read_holding_registers(5)[0]
        rw_flow_out_valve = rw_client.read_holding_registers(6)[0]
        rw_is_running = rw_client.read_holding_registers(7)[0]
        rw_client.close()
        rw_data = {
            'rw_water_level': rw_float_list[0],
            'rw_temperature': rw_float_list[1],
            'rw_pump_in_speed': rw_pump_in_speed,
            'rw_flow_in': rw_flow_in_valve,
            'rw_flow_out': rw_flow_out_valve,
            'rw_running': rw_is_running
        }
        socketio.emit('rw_data', rw_data, namespace='/dynamic')
        if rw_speed_flag:
            rw_speed_change()
            rw_speed_flag = False

        if rw_running_flag:
            rw_running_switch()
            rw_running_flag = False

        if rw_flow_in_flag:
            rw_flow_in_switch()
            rw_flow_in_flag = False

        if rw_flow_out_flag:
            rw_flow_out_switch()
            rw_flow_out_flag = False

        st_client.open()
        st_float_list = st_client.read_floats(0, 2)
        st_pump_out_speed = st_client.read_holding_registers(4)[0]
        st_flow_in_valve = st_client.read_holding_registers(5)[0]
        st_flow_out_valve = st_client.read_holding_registers(6)[0]
        st_is_automatic = st_client.read_holding_registers(7)[0]
        st_is_running = st_client.read_holding_registers(8)[0]
        st_client.close()
        st_data = {
            'st_water_level': st_float_list[0],
            'st_temperature': st_float_list[1],
            'st_pump_out_speed': st_pump_out_speed,
            'st_flow_in': st_flow_in_valve,
            'st_flow_out': st_flow_out_valve,
            'st_automatic': st_is_automatic,
            'st_running': st_is_running
        }
        socketio.emit('st_data', st_data, namespace='/dynamic')
        if st_speed_flag:
            st_speed_change()
            st_speed_flag = False

        if st_running_flag:
            st_running_switch()
            st_running_flag = False

        if st_flow_in_flag:
            st_flow_in_switch()
            st_flow_in_flag = False

        if st_flow_out_flag:
            st_flow_out_switch()
            st_flow_out_flag = False

        if st_automatic_flag:
            st_automatic_switch()
            st_automatic_flag = False

        client.write_float(99, rw_float_list[0])
        dis_client.write_float(99, float_list[0])
        st_client.write_float(99, dis_float_list[0])

        error_message, sound_alarm = alarm_check(rw_float_list[0], float_list[0],
                                                 dis_float_list[0], st_float_list[0],
                                                 float_list[4], float_list[5],
                                                 dis_float_list[4])

        if len(error_message) > 0:
            socketio.emit("error_message", error_message, namespace='/dynamic')

        if sound_alarm is True:
            socketio.emit("sound_alarm", namespace='/dynamic')

        time.sleep(1)


@app.route('/', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        attack = Attack(username=form.username.data, password=form.password.data)
        db.session.add(attack)
        db.session.commit()

        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('main_page'))
    return render_template('login.html', form=form)


@app.route('/dashboard', methods=["POST", "GET"])
@login_required
def main_page():
    return render_template('dashboard.html', user=current_user)


@app.route('/filter_charts', methods=["POST", "GET"])
@login_required
def filter_charts_page():
    return render_template('filter_charts.html', user=current_user)


@app.route('/disinfection_charts', methods=["POST", "GET"])
@login_required
def disinfection_charts_page():
    return render_template('disinfection_charts.html', user=current_user)


@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('main_page'))


@socketio.on('connect', namespace='/dynamic')
def connect():
    print('Client connected')

    csv_file = 'request.csv'
    with open(csv_file, 'a', newline='') as file:
        writer = csv.writer(file)
        data = [request.remote_addr, request.user_agent, request.referrer, request.host, request.cookies,
                request.headers]
        writer.writerow(data)

    file.close()


@socketio.on('disconnect', namespace='/dynamic')
def disconnect():
    print('Client disconnected')


def flow_in_switch():
    client.open()
    client.write_single_register(15, flow_in)
    client.close()


def flow_out_switch():
    client.open()
    client.write_single_register(16, flow_out)
    client.close()



@socketio.on('flow_in_open', namespace='/dynamic')
def flow_in_open():
    global flow_in_flag, flow_in
    global rw_flow_out_flag, rw_flow_out
    flow_in_flag = True
    flow_in = True

    rw_flow_out_flag = True
    rw_flow_out = True


@socketio.on('flow_in_close', namespace='/dynamic')
def flow_in_close():
    global flow_in_flag, flow_in
    global rw_flow_out_flag, rw_flow_out
    flow_in_flag = True
    flow_in = False

    rw_flow_out_flag = True
    rw_flow_out = False


@socketio.on('flow_out_open', namespace='/dynamic')
def flow_out_open():
    global flow_out_flag, flow_out
    global dis_flow_in_flag, dis_flow_in
    flow_out_flag = True
    flow_out = True

    dis_flow_in_flag = True
    dis_flow_in = True


@socketio.on('flow_out_close', namespace='/dynamic')
def flow_out_close():
    global flow_out_flag, flow_out
    global dis_flow_in_flag, dis_flow_in
    flow_out_flag = True
    flow_out = False

    dis_flow_in_flag = True
    dis_flow_in = False


@socketio.on('filter_on', namespace='/dynamic')
def filter_on():
    global filter_switch_flag, new_filter_running
    filter_switch_flag = True
    new_filter_running = True


@socketio.on('filter_off', namespace='/dynamic')
def filter_off():
    global filter_switch_flag, new_filter_running
    global sand_switch_flag, new_sand_mode
    global gravel_switch_flag, new_gravel_mode
    filter_switch_flag = True
    sand_switch_flag = True
    gravel_switch_flag = True
    new_filter_running = False
    new_gravel_mode = 0
    new_sand_mode = 0


def filter_switch():
    client.open()
    client.write_single_register(12, new_filter_running)
    client.close()


@socketio.on('sand_stop', namespace='/dynamic')
def sand_stop():
    global sand_switch_flag, new_sand_mode
    sand_switch_flag = True
    new_sand_mode = 0


@socketio.on('sand_normal', namespace='/dynamic')
def sand_normal():
    global new_filter_running
    if new_filter_running is False:
        return
    global sand_switch_flag, new_sand_mode
    sand_switch_flag = True
    new_sand_mode = 1


@socketio.on('sand_strong', namespace='/dynamic')
def sand_strong():
    global new_filter_running
    if new_filter_running is False:
        return
    global sand_switch_flag, new_sand_mode
    sand_switch_flag = True
    new_sand_mode = 2


def sand_switch():
    client.open()
    client.write_single_register(14, new_sand_mode)
    client.close()


@socketio.on('gravel_stop', namespace='/dynamic')
def gravel_stop():
    global gravel_switch_flag, new_gravel_mode
    gravel_switch_flag = True
    new_gravel_mode = 0


@socketio.on('gravel_normal', namespace='/dynamic')
def gravel_normal():
    global new_filter_running
    if new_filter_running is False:
        return
    global gravel_switch_flag, new_gravel_mode
    gravel_switch_flag = True
    new_gravel_mode = 1


@socketio.on('gravel_strong', namespace='/dynamic')
def gravel_strong():
    global new_filter_running
    if new_filter_running is False:
        return
    global gravel_switch_flag, new_gravel_mode
    gravel_switch_flag = True
    new_gravel_mode = 2


def gravel_switch():
    client.open()
    client.write_single_register(13, new_gravel_mode)
    client.close()


def dis_running_switch():
    dis_client.open()
    dis_client.write_single_register(12, dis_running)
    dis_client.close()


def dis_flow_in_switch():
    dis_client.open()
    dis_client.write_single_register(13, dis_flow_in)
    dis_client.close()


def dis_flow_out_switch():
    dis_client.open()
    dis_client.write_single_register(14, dis_flow_out)
    dis_client.close()


def automatic_switch():
    dis_client.open()
    dis_client.write_single_register(15, dis_automatic)
    dis_client.close()


@socketio.on('dis_on', namespace='/dynamic')
def dis_on():
    global dis_running_flag, dis_running
    dis_running_flag = True
    dis_running = True


@socketio.on('dis_off', namespace='/dynamic')
def dis_off():
    global dis_running_flag, dis_running
    dis_running_flag = True
    dis_running = False


@socketio.on('dis_flow_in_open', namespace='/dynamic')
def dis_flow_in_open():
    global dis_flow_in_flag, dis_flow_in
    global flow_out_flag, flow_out
    dis_flow_in_flag = True
    dis_flow_in = True
    flow_out_flag = True
    flow_out = True


@socketio.on('dis_flow_in_close', namespace='/dynamic')
def dis_flow_in_close():
    global dis_flow_in_flag, dis_flow_in
    global flow_out_flag, flow_out
    dis_flow_in_flag = True
    dis_flow_in = False
    flow_out_flag = True
    flow_out = False


@socketio.on('dis_flow_out_open', namespace='/dynamic')
def dis_flow_in_open():
    global dis_flow_out_flag, dis_flow_out
    global st_flow_in_flag, st_flow_in
    dis_flow_out_flag = True
    dis_flow_out = True
    st_flow_in_flag = True
    st_flow_in = True


@socketio.on('dis_flow_out_close', namespace='/dynamic')
def dis_flow_out_close():
    global dis_flow_out_flag, dis_flow_out
    global st_flow_in_flag, st_flow_in
    dis_flow_out_flag = True
    dis_flow_out = False
    st_flow_in_flag = True
    st_flow_in = False


@socketio.on('automatic_on', namespace='/dynamic')
def automatic_on():
    global dis_automatic_flag, dis_automatic
    dis_automatic_flag = True
    dis_automatic = True


@socketio.on('automatic_off', namespace='/dynamic')
def automatic_off():
    global dis_automatic_flag, dis_automatic
    dis_automatic_flag = True
    dis_automatic = False


@socketio.on('chlorine', namespace='/dynamic')
def change_chlorine_control(new_value):
    global chlorine_flag, chlorine
    chlorine_flag = True
    chlorine = new_value
    print(chlorine)


def change_chlorine():
    dis_client.open()
    print("goes line 792")
    dis_client.write_float(18, chlorine)
    dis_client.close()


def change_concentration():
    dis_client.open()
    dis_client.write_float(16, concentration)
    dis_client.close()


@socketio.on('concentration', namespace='/dynamic')
def change_concentration_control(new_value):
    global concentration_flag, concentration
    concentration_flag = True
    concentration = new_value


@socketio.on('rw_on', namespace='/dynamic')
def rw_on():
    global rw_running_flag, rw_running
    rw_running_flag = True
    rw_running = True


@socketio.on('rw_off', namespace='/dynamic')
def rw_off():
    global rw_running_flag, rw_running
    rw_running_flag = True
    rw_running = False


@socketio.on('rw_flow_in_open', namespace='/dynamic')
def rw_flow_in_open():
    global rw_flow_in_flag, rw_flow_in
    rw_flow_in_flag = True
    rw_flow_in = True


@socketio.on('rw_flow_in_close', namespace='/dynamic')
def rw_flow_in_close():
    global rw_flow_in_flag, rw_flow_in
    rw_flow_in_flag = True
    rw_flow_in = False


@socketio.on('rw_flow_out_open', namespace='/dynamic')
def rw_flow_out_open():
    global rw_flow_out_flag, rw_flow_out
    global flow_in_flag, flow_in
    rw_flow_out_flag = True
    rw_flow_out = True
    flow_in_flag = True
    flow_in = True


@socketio.on('rw_flow_out_close', namespace='/dynamic')
def rw_flow_out_close():
    global rw_flow_out_flag, rw_flow_out
    global flow_in_flag, flow_in
    rw_flow_out_flag = True
    rw_flow_out = False
    flow_in_flag = True
    flow_in = False


@socketio.on('rw_flow_out_close', namespace='/dynamic')
@socketio.on('pump_in_speed', namespace='/dynamic')
def pump_in_speed(new_speed):
    global rw_speed_flag, rw_speed
    rw_speed_flag = True
    rw_speed = int(int(new_speed) / 10)
    print(rw_speed)


@socketio.on('st_on', namespace='/dynamic')
def st_on():
    global st_running_flag, st_running
    st_running_flag = True
    st_running = True


@socketio.on('st_off', namespace='/dynamic')
def st_off():
    global st_running_flag, st_running
    st_running_flag = True
    st_running = False


@socketio.on('st_flow_in_open', namespace='/dynamic')
def st_flow_in_open():
    global st_flow_in_flag, st_flow_in
    global dis_flow_out_flag, dis_flow_out
    st_flow_in_flag = True
    st_flow_in = True

    dis_flow_out_flag = True
    dis_flow_out = True


@socketio.on('st_flow_in_close', namespace='/dynamic')
def st_flow_in_close():
    global st_flow_in_flag, st_flow_in
    global dis_flow_out_flag, dis_flow_out
    st_flow_in_flag = True
    st_flow_in = False
    dis_flow_out_flag = True
    dis_flow_out = False


@socketio.on('rw_flow_out_open', namespace='/dynamic')
def st_flow_in_open():
    global st_flow_out_flag, st_flow_out
    st_flow_out_flag = True
    st_flow_out = True


@socketio.on('st_flow_out_close', namespace='/dynamic')
def st_flow_out_close():
    global st_flow_out_flag, st_flow_out
    st_flow_out_flag = True
    st_flow_out = False


@socketio.on('st_automatic_close', namespace='/dynamic')
def st_flow_out_open():
    global st_automatic_flag, st_automatic
    st_automatic_flag = True
    st_automatic = True


@socketio.on('st_automatic_close', namespace='/dynamic')
def st_automatic_close():
    global st_automatic_flag, st_automatic
    st_automatic_flag = True
    st_automatic = False


@socketio.on('pump_out_speed', namespace='/dynamic')
def pump_in_speed(new_speed):
    global st_speed_flag, st_speed
    st_speed_flag = True
    st_speed = int(int(new_speed) / 10)


if __name__ == "__main__":
    read_data_thread = Thread(target=read_data)
    read_data_thread.daemon = True
    read_data_thread.start()
    app.run(debug=False)
