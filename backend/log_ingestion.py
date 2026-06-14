"""
Log Ingestion Module
Handles ingestion from file, syslog, and API sources
"""

import json
import re
from datetime import datetime
from pathlib import Path
import socket
import struct


class LogParser:
    """Parse logs in various formats"""
    
    @staticmethod
    def parse_json_log(line):
        """Parse JSON formatted log"""
        try:
            return json.loads(line)
        except json.JSONDecodeError:
            return None
    
    @staticmethod
    def parse_standard_log(line):
        """
        Parse standard log format
        [TIMESTAMP] [LEVEL] [SERVICE] Message
        """
        pattern = r'\[(.*?)\]\s+\[(.*?)\]\s+\[(.*?)\]\s+(.*)'
        match = re.match(pattern, line)
        
        if match:
            timestamp_str, level, service, message = match.groups()
            
            try:
                timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            except:
                timestamp = datetime.now()
            
            return {
                'timestamp': timestamp,
                'level': level.upper(),
                'service': service,
                'message': message,
                'metadata': {}
            }
        
        return None
    
    @staticmethod
    def parse_apache_log(line):
        """Parse Apache access log format"""
        pattern = r'(.*?) - - \[(.*?)\] "(.*?)" (\d+) (.*?) "(.*?)" "(.*?)"'
        match = re.match(pattern, line)
        
        if match:
            ip, timestamp_str, request, status, size, referrer, user_agent = match.groups()
            
            try:
                timestamp = datetime.strptime(timestamp_str, '%d/%b/%Y:%H:%M:%S %z')
            except:
                timestamp = datetime.now()
            
            return {
                'timestamp': timestamp,
                'level': 'INFO',
                'service': 'apache-web',
                'message': f"{request} - {status}",
                'metadata': {
                    'ip': ip,
                    'status': status,
                    'size': size,
                    'user_agent': user_agent
                }
            }
        
        return None
    
    @staticmethod
    def parse_nginx_log(line):
        """Parse Nginx access log format"""
        pattern = r'(.*?) - - \[(.*?)\] "(.*?)" (\d+) (\d+) "(.*?)" "(.*?)"'
        match = re.match(pattern, line)
        
        if match:
            ip, timestamp_str, request, status, bytes_sent, referrer, user_agent = match.groups()
            
            try:
                timestamp = datetime.strptime(timestamp_str, '%d/%b/%Y:%H:%M:%S %z')
            except:
                timestamp = datetime.now()
            
            return {
                'timestamp': timestamp,
                'level': 'INFO',
                'service': 'nginx-web',
                'message': f"{request} - {status}",
                'metadata': {
                    'ip': ip,
                    'status': int(status),
                    'bytes_sent': int(bytes_sent),
                    'user_agent': user_agent
                }
            }
        
        return None
    
    @staticmethod
    def parse_syslog(line):
        """Parse syslog format (RFC 3164)"""
        pattern = r'(\w+\s+\d+\s+\d+:\d+:\d+)\s+(.*?)\s+(.*?):\s+(.*)'
        match = re.match(pattern, line)
        
        if match:
            timestamp_str, hostname, service, message = match.groups()
            
            try:
                timestamp = datetime.strptime(timestamp_str, '%b %d %H:%M:%S')
                timestamp = timestamp.replace(year=datetime.now().year)
            except:
                timestamp = datetime.now()
            
            return {
                'timestamp': timestamp,
                'level': 'INFO',
                'service': service,
                'message': message,
                'metadata': {
                    'hostname': hostname
                }
            }
        
        return None
    
    @classmethod
    def auto_parse(cls, line):
        """Attempt to parse log with auto-detection"""
        parsers = [
            cls.parse_json_log,
            cls.parse_standard_log,
            cls.parse_syslog,
            cls.parse_nginx_log,
            cls.parse_apache_log,
        ]
        
        for parser in parsers:
            result = parser(line)
            if result:
                return result
        
        # Fallback: treat as simple message
        return {
            'timestamp': datetime.now(),
            'level': 'INFO',
            'service': 'unknown',
            'message': line,
            'metadata': {}
        }


class FileLogIngester:
    """Ingest logs from files"""
    
    def __init__(self, parser=None):
        self.parser = parser or LogParser()
    
    def ingest_file(self, file_path):
        """
        Ingest logs from a file
        
        Args:
            file_path: Path to log file
            
        Returns:
            List of parsed log entries
        """
        logs = []
        
        try:
            with open(file_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        parsed = self.parser.auto_parse(line)
                        if parsed:
                            logs.append(parsed)
        except Exception as e:
            print(f"Error ingesting file {file_path}: {e}")
        
        return logs


class SyslogIngester:
    """Ingest logs from syslog"""
    
    def __init__(self, host='localhost', port=514, parser=None):
        self.host = host
        self.port = port
        self.parser = parser or LogParser()
        self.socket = None
    
    def start_listening(self):
        """Start listening for syslog messages"""
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((self.host, self.port))
        print(f"Syslog listener started on {self.host}:{self.port}")
    
    def receive_message(self, timeout=1.0):
        """
        Receive a syslog message
        
        Args:
            timeout: Socket timeout in seconds
            
        Returns:
            Parsed log entry or None
        """
        if not self.socket:
            self.start_listening()
        
        self.socket.settimeout(timeout)
        
        try:
            data, addr = self.socket.recvfrom(2048)
            message = data.decode('utf-8')
            
            # Parse priority and message
            if message.startswith('<'):
                priority_end = message.find('>')
                if priority_end != -1:
                    priority = int(message[1:priority_end])
                    msg_body = message[priority_end + 1:]
                    
                    # Parse message
                    parsed = self.parser.auto_parse(msg_body)
                    parsed['metadata']['source_ip'] = addr[0]
                    parsed['metadata']['priority'] = priority
                    
                    return parsed
        except socket.timeout:
            return None
        except Exception as e:
            print(f"Error receiving syslog message: {e}")
            return None
    
    def stop_listening(self):
        """Stop listening for syslog messages"""
        if self.socket:
            self.socket.close()


class APILogIngester:
    """Handle log ingestion via API"""
    
    def __init__(self, parser=None):
        self.parser = parser or LogParser()
    
    def process_api_logs(self, data):
        """
        Process logs received via API
        
        Args:
            data: Dictionary or list of log entries
            
        Returns:
            List of parsed logs
        """
        logs = []
        
        if isinstance(data, list):
            for entry in data:
                parsed = self._parse_entry(entry)
                if parsed:
                    logs.append(parsed)
        elif isinstance(data, dict):
            parsed = self._parse_entry(data)
            if parsed:
                logs.append(parsed)
        
        return logs
    
    def _parse_entry(self, entry):
        """Parse a single log entry"""
        if isinstance(entry, str):
            return self.parser.auto_parse(entry)
        elif isinstance(entry, dict):
            # Expected keys: timestamp, level, service, message
            return {
                'timestamp': entry.get('timestamp', datetime.now()),
                'level': entry.get('level', 'INFO').upper(),
                'service': entry.get('service', 'unknown'),
                'message': entry.get('message', ''),
                'metadata': entry.get('metadata', {})
            }
        
        return None


class LogIngestionManager:
    """Manage all log ingestion operations"""
    
    def __init__(self):
        self.file_ingester = FileLogIngester()
        self.syslog_ingester = SyslogIngester()
        self.api_ingester = APILogIngester()
    
    def ingest_from_file(self, file_path):
        """Ingest logs from file"""
        return self.file_ingester.ingest_file(file_path)
    
    def ingest_from_api(self, data):
        """Ingest logs from API"""
        return self.api_ingester.process_api_logs(data)
    
    def start_syslog_listener(self, host='localhost', port=514):
        """Start syslog listener"""
        self.syslog_ingester = SyslogIngester(host, port)
        self.syslog_ingester.start_listening()
    
    def get_syslog_message(self):
        """Get syslog message"""
        return self.syslog_ingester.receive_message()
