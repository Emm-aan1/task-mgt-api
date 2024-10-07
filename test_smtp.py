import smtplib

smtp_server = "smtp.gmail.com"
port = 465  # For TLS
sender_email = "taskapimanager@gmail.com"
password = "mdtb bsyh hnmc ydqf"

server = None

try:
    # Connect to the server
    server = smtplib.SMTP_SSL(smtp_server, port)
    server.login(sender_email, password)

    print("Successfully connected to the Gmail SMTP server.")
except Exception as e:
    print(f"Error: {e}")
finally:
    if server:
        server.quit()
