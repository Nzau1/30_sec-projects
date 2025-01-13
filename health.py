import psutil
import platform
import socket
import uuid
import GPUtil
import time
import threading
import json
import os
from datetime import datetime
import logging
import sqlite3
import queue
import smtplib
from email.mime.text import MIMEText
import speedtest

class DeviceHealthMonitor:
    def __init__(self, config_path='config.json'):
        """
        Initialize the Device Health Monitoring System
        :param config_path: Path to configuration file
        """
        # Load configuration
        self.load_config(config_path)
        
        # Setup logging
        self.setup_logging()
        
        # Initialize databases
        self.setup_databases()
        
        # Initialize monitoring queues and flags
        self.health_queue = queue.Queue()
        self.is_monitoring = False
        
        # System identification
        self.device_id = self.generate_device_id()
        
        # Notification channels
        self.notification_methods = {
            'email': self.send_email_notification,
            'console': self.log_notification
        }

    def load_config(self, config_path):
        """
        Load system configuration
        :param config_path: Path to JSON configuration file
        """
        try:
            with open(config_path, 'r') as config_file:
                self.config = json.load(config_file)
        except FileNotFoundError:
            # Default configuration
            self.config = {
                'monitoring_interval': 300,  # 5 minutes
                'critical_thresholds': {
                    'cpu_usage': 90,
                    'memory_usage': 90,
                    'disk_usage': 90,
                    'temperature': 80
                },
                'notification_email': 'admin@example.com',
                'smtp_config': {
                    'server': 'smtp.gmail.com',
                    'port': 587,
                    'username': 'your_email@gmail.com',
                    'password': 'your_password'
                }
            }

    def setup_logging(self):
        """
        Configure logging system
        """
        log_dir = 'logs'
        os.makedirs(log_dir, exist_ok=True)
        logging.basicConfig(
            filename=os.path.join(log_dir, 'device_health.log'),
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s: %(message)s'
        )

    def setup_databases(self):
        """
        Initialize SQLite database for health records
        """
        self.conn = sqlite3.connect('device_health.db', check_same_thread=False)
        self.cursor = self.conn.cursor()
        
        # Create tables for health monitoring
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS health_logs (
                id INTEGER PRIMARY KEY,
                timestamp DATETIME,
                device_id TEXT,
                cpu_usage REAL,
                memory_usage REAL,
                disk_usage REAL,
                network_status TEXT,
                temperature REAL
            )
        ''')
        self.conn.commit()

    def generate_device_id(self):
        """
        Generate unique device identifier
        :return: Unique device ID
        """
        return str(uuid.uuid4())

    def get_system_info(self):
        """
        Collect comprehensive system information
        :return: Dictionary of system details
        """
        return {
            'os': platform.system(),
            'os_version': platform.version(),
            'processor': platform.processor(),
            'machine': platform.machine(),
            'hostname': socket.gethostname()
        }

    def monitor_cpu(self):
        """
        Monitor CPU usage and temperature
        :return: Dictionary of CPU metrics
        """
        try:
            cpu_usage = psutil.cpu_percent(interval=1)
            cpu_temp = self.get_cpu_temperature()
            return {
                'usage': cpu_usage,
                'temperature': cpu_temp
            }
        except Exception as e:
            logging.error(f"CPU Monitoring Error: {e}")
            return {'usage': 0, 'temperature': 0}

    def monitor_memory(self):
        """
        Monitor memory usage
        :return: Memory usage percentage
        """
        memory = psutil.virtual_memory()
        return memory.percent

    def monitor_disk(self):
        """
        Monitor disk usage
        :return: Disk usage percentage
        """
        disk = psutil.disk_usage('/')
        return disk.percent

    def monitor_network(self):
        """
        Test network speed and connectivity
        :return: Network performance metrics
        """
        try:
            st = speedtest.Speedtest()
            download_speed = st.download() / 1_000_000  # Convert to Mbps
            upload_speed = st.upload() / 1_000_000  # Convert to Mbps
            ping = st.results.ping

            return {
                'download_speed': download_speed,
                'upload_speed': upload_speed,
                'ping': ping
            }
        except Exception as e:
            logging.error(f"Network Test Error: {e}")
            return {'download_speed': 0, 'upload_speed': 0, 'ping': 0}

    def get_cpu_temperature(self):
        """
        Get CPU temperature (platform-dependent)
        :return: CPU temperature
        """
        try:
            # Platform-specific temperature retrieval
            if platform.system() == "Darwin":
                # macOS
                import subprocess
                output = subprocess.check_output(['osx-cpu-temp']).decode().strip()
                return float(output.replace('°C', ''))
            elif platform.system() == "Linux":
                # Linux
                temp_file = "/sys/class/thermal/thermal_zone0/temp"
                with open(temp_file, "r") as f:
                    return float(f.read().strip()) / 1000
            else:
                return 0
        except Exception:
            return 0

    def analyze_health(self):
        """
        Comprehensive health analysis
        :return: Health status and issues
        """
        issues = []
        
        # CPU Analysis
        cpu_data = self.monitor_cpu()
        if cpu_data['usage'] > self.config['critical_thresholds']['cpu_usage']:
            issues.append(f"High CPU Usage: {cpu_data['usage']}%")
        if cpu_data['temperature'] > self.config['critical_thresholds']['temperature']:
            issues.append(f"High CPU Temperature: {cpu_data['temperature']}°C")
        
        # Memory Analysis
        memory_usage = self.monitor_memory()
        if memory_usage > self.config['critical_thresholds']['memory_usage']:
            issues.append(f"High Memory Usage: {memory_usage}%")
        
        # Disk Analysis
        disk_usage = self.monitor_disk()
        if disk_usage > self.config['critical_thresholds']['disk_usage']:
            issues.append(f"High Disk Usage: {disk_usage}%")
        
        return {
            'status': 'Critical' if issues else 'Healthy',
            'issues': issues
        }

    def log_health_data(self, health_data):
        """
        Log health data to SQLite database
        :param health_data: Health metrics dictionary
        """
        try:
            self.cursor.execute('''
                INSERT INTO health_logs 
                (timestamp, device_id, cpu_usage, memory_usage, disk_usage, network_status, temperature) 
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                datetime.now(),
                self.device_id,
                health_data.get('cpu_usage', 0),
                health_data.get('memory_usage', 0),
                health_data.get('disk_usage', 0),
                str(health_data.get('network_status', {})),
                health_data.get('temperature', 0)
            ))
            self.conn.commit()
        except Exception as e:
            logging.error(f"Database Logging Error: {e}")

    def send_email_notification(self, message):
        """
        Send email notification for critical issues
        :param message: Notification message
        """
        try:
            smtp_config = self.config['smtp_config']
            msg = MIMEText(message)
            msg['Subject'] = "Device Health Alert"
            msg['From'] = smtp_config['username']
            msg['To'] = self.config['notification_email']

            with smtplib.SMTP(smtp_config['server'], smtp_config['port']) as server:
                server.starttls()
                server.login(smtp_config['username'], smtp_config['password'])
                server.send_message(msg)
        except Exception as e:
            logging.error(f"Email Notification Error: {e}")

    def log_notification(self, message):
        """
        Log notification to console and log file
        :param message: Notification message
        """
        logging.warning(message)
        print(message)

    def start_monitoring(self, notification_method='console'):
        """
        Start continuous device health monitoring
        :param notification_method: How to send notifications
        """
        self.is_monitoring = True
        monitor_thread = threading.Thread(target=self._monitoring_loop, args=(notification_method,))
        monitor_thread.start()

    def _monitoring_loop(self, notification_method):
        """
        Continuous monitoring loop
        :param notification_method: Notification channel
        """
        while self.is_monitoring:
            try:
                # Collect health data
                health_data = {
                    'cpu_usage': self.monitor_cpu()['usage'],
                    'memory_usage': self.monitor_memory(),
                    'disk_usage': self.monitor_disk(),
                    'network_status': self.monitor_network(),
                    'temperature': self.monitor_cpu()['temperature']
                }

                # Log health data
                self.log_health_data(health_data)

                # Analyze health
                health_analysis = self.analyze_health()

                # Notify if issues detected
                if health_analysis['status'] == 'Critical':
                    notification = "\n".join(health_analysis['issues'])
                    self.notification_methods.get(notification_method, self.log_notification)(notification)

                # Wait before next check
                time.sleep(self.config['monitoring_interval'])

            except Exception as e:
                logging.error(f"Monitoring Loop Error: {e}")
                time.sleep(60)  # Wait before retrying

    def stop_monitoring(self):
        """
        Stop device health monitoring
        """
        self.is_monitoring = False

def main():
    # Create and start device health monitor
    monitor = DeviceHealthMonitor()
    
    # Print system information
    print("System Information:")
    print(json.dumps(monitor.get_system_info(), indent=2))
    
    # Start monitoring
    monitor.start_monitoring()

if __name__ == "__main__":
    main()