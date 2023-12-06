import streamlit as st
import paho.mqtt.client as mqtt
import plotly.graph_objs as go
from datetime import datetime
from PIL import Image
import pytz

image = Image.open('bareng.png')

st.image(image, width=700)
st.write("  ")
# st.title("PLTU Banten 3 Lontar")
st.markdown("<center><h2>Monitoring Condensate Polishing Berbasis IoT</h2></center>", unsafe_allow_html=True)
st.markdown("<center><h2>PLTU Banten 3 Lontar</h2></center>", unsafe_allow_html=True)
st.write("  ")
st.write("  ")

## Variabel-variabel koneksi MQTT
broker = "mqtt-dashboard.com"
port = 1883
topic = "arsuya/relay"  # Sesuaikan dengan topik MQTT yang digunakan oleh perangkat IoT Anda
mqtt_connected = False  # Variabel status koneksi MQTT

# Buat wadah kosong untuk output nilai dan grafik
status_container = st.empty()
output_container = st.empty()
chart_container = st.empty()

# Variabel-variabel grafik garis
data = []  # Simpan data dalam list
max_data_points = 1440  # Batasi jumlah data yang ditampilkan pada grafik (1 hari x 60 menit)

# Fungsi yang akan dipanggil saat koneksi MQTT berhasil
def on_connect(client, userdata, flags, rc):
    global mqtt_connected
    mqtt_connected = True
    client.subscribe(topic)  # Langganan ke topik MQTT setelah koneksi berhasil

# Fungsi yang akan dipanggil saat pesan MQTT diterima
def on_message(client, userdata, msg):
    try:
        sensor_data = msg.payload.decode("utf-8")  # Parsing pesan MQTT
        update_output(sensor_data)  # Perbarui output nilai
        update_line_chart(sensor_data)  # Perbarui grafik garis dengan data yang diterima
    except Exception as e:
        st.error(f"Error parsing MQTT message: {e}")

# Fungsi untuk memperbarui output nilai
def update_output(sensor_data):
    status = ""
    if sensor_data == "1":
        status = "Kation"
    elif sensor_data == "0":
        status = "Anion"
    
    status_container.metric("Status :", status)

# Fungsi untuk memperbarui data pada grafik garis
def update_line_chart(sensor_data):
    global data
    current_time = datetime.now(pytz.timezone("Asia/Jakarta")).strftime("%H:%M:%S")
    if sensor_data == "1":
        data.append((current_time, "Kation"))
    elif sensor_data == "0":
        data.append((current_time, "Anion"))

    # Proses data waktu untuk sumbu x
    x_time = [entry[0] for entry in data]
    # Ambil data sensor untuk sumbu y
    y_sensor = [entry[1] for entry in data]

    # Buat mapping nilai kation dan anion ke nilai numerik (misalnya, 0 dan 1) untuk plot
    y_numeric = [1 if value == "Kation" else 0 for value in y_sensor]

    # Tampilkan grafik garis menggunakan Plotly dalam wadah yang sudah dibuat
    fig = go.Figure(data=go.Scatter(x=x_time, y=y_numeric, mode='lines'))
    fig.update_yaxes(tickvals=[0, 1], ticktext=["Aman", "Kation"])  # Atur label pada sumbu Y
    chart_container.plotly_chart(fig, use_container_width=True, key='line_chart')

    if len(data) > max_data_points:
        data.pop(0)

# Koneksi awal ke broker MQTT
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(broker, port, 60)
client.loop_forever()
