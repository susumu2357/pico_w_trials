import network
import socket
from time import sleep
import machine

import secret

def webpage(temperature, state):
    #Template HTML
    html = f"""
            <!DOCTYPE html>
            <html>
            <form action="./lighton">
            <input type="submit" value="Light on" />
            </form>
            <form action="./lightoff">
            <input type="submit" value="Light off" />
            </form>
            <p>LED is {state}</p>
            <p>Temperature is {temperature}</p>
            </body>
            </html>
            """
    return str(html)

def connect():
    #Connect to WLAN
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(secret.SSID, secret.PASS)
    while wlan.isconnected() == False:
        print('Waiting for connection...')
        sleep(1)
    ip = wlan.ifconfig()[0]
    print(f'Connected on {ip}')
    return ip

def open_socket(ip):
    # Open a socket
    address = (ip, 80)
    connection = socket.socket()
    connection.bind(address)
    connection.listen(1)
    print(connection)
    return connection

def read_temperature():
    sensor_temp = machine.ADC(4)
    conversion_factor = 3.3 / (65535)
    reading = sensor_temp.read_u16() * conversion_factor
    temperature = 27 - (reading - 0.706)/0.001721
    return temperature

def serve(connection):
    #Start a web server
    state = 'OFF'
    led_onboard = machine.Pin("LED", machine.Pin.OUT)    
    led_onboard.off()
    temperature = 0
    while True:
        client = connection.accept()[0]
        request = client.recv(1024)
        request = str(request)
        
        try:
            request = request.split()[1]
        except IndexError:
            pass
        if request == '/lighton?':
            led_onboard.on()
            state = 'ON'
        elif request =='/lightoff?':
            led_onboard.off()
            state = 'OFF'
            
        print(request)
        
        temperature = read_temperature()
        html = webpage(temperature, state)
        client.send(html)
        client.close()
        
try:
    ip = connect()
    connection = open_socket(ip)
    serve(connection)
except KeyboardInterrupt:
    machine.reset()