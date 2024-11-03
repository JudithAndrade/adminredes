from flask import Flask, render_template, jsonify
import subprocess
import platform
import time

app = Flask(__name__)

# Lista de IPs a escanear (puedes agregar más IPs aquí)
ip_addresses = [
    "192.168.0.40",  # IP activa (puedes cambiarla)
    "192.168.0.132",
    "172.17.80.1",    # IP de ejemplo
    "195.80.116.235",  # IP de ejemplo
    "192.168.0.1",
    # Agrega más IPs aquí
]

# Almacenar el estado de las IPs y tiempos de respuesta
ip_status = {ip: None for ip in ip_addresses}
response_times = {ip: None for ip in ip_addresses}

def scan_ip(ip):
    """Función para escanear una dirección IP utilizando el comando ping y medir el tiempo de respuesta."""
    try:
        # Determinar el comando de ping según el sistema operativo
        param = '-n' if platform.system().lower() == 'windows' else '-c'
        
        # Capturar el tiempo de inicio
        start_time = time.time()
        response = subprocess.call(['ping', param, '1', ip], stdout=subprocess.DEVNULL)
        # Capturar el tiempo de finalización
        elapsed_time = time.time() - start_time
        
        return response == 0, elapsed_time  # Devuelve si la IP está activa y el tiempo transcurrido
    except Exception as e:
        print(f"Error al escanear {ip}: {e}")
        return False, None

@app.route('/')
def index():
    """Ruta principal que muestra la página inicial."""
    return render_template('index.html')

@app.route('/scan')
def scan():
    """Ruta para escanear las IPs y devolver resultados en formato JSON."""
    active_ips = []
    inactive_ips = []
    
    # Captura el tiempo de inicio del escaneo total
    total_start_time = time.time()

    for ip in ip_addresses:
        is_active, elapsed_time = scan_ip(ip)

        # Solo actualizar el estado si hay un cambio
        if is_active:
            active_ips.append(ip)
            response_times[ip] = f"{elapsed_time:.2f} ms"  # Guardar el tiempo de respuesta
            ip_status[ip] = True  # Actualizar el estado a activo
        else:
            # Si la IP no está activa, la agregamos a inactivos
            inactive_ips.append(ip)
            response_times[ip] = "No responde"  # Guardar el estado inactivo
            ip_status[ip] = False  # Actualizar el estado a inactivo

    # Captura el tiempo total del escaneo
    total_elapsed_time = time.time() - total_start_time

    return jsonify({
        'active_ips': active_ips,
        'inactive_ips': inactive_ips,
        'response_times': response_times,
        'delay_time': f"{total_elapsed_time * 1000:.2f}"  # Convertir a milisegundos
    })

if __name__ == '__main__':
    app.run(debug=True)
