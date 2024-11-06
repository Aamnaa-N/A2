import pexpect

# Device details
host = "192.168.56.102"
user = "cisco"
password = "cisco123!"
password_enable = "cisco123!"
new_hostname = "host1"

def configure_acl_syslog(session, hostname):
    # Configuring Access Control List (ACL)
    acl_commands = [
        "access-list 100 permit ip 192.168.10.0 0.0.0.255 any",
        "access-list 100 deny ip any any"
    ]
    
    # Sending ACL commands
    session.sendline("configure terminal")
    session.expect(r"\(config\)#", timeout=60)
    for command in acl_commands:
        session.sendline(command)
        session.expect(r"\(config\)#", timeout=60)

    # Syslog Configuration - Configure syslog server
    syslog_commands = [
        "logging host 192.168.10.100",  # Replace with your syslog server IP
        "logging trap informational"    # Set log level to informational
    ]

    # Sending Syslog commands
    for command in syslog_commands:
        session.sendline(command)
        session.expect(r"\(config\)#", timeout=60)

    session.sendline("end")
    session.expect(f"{hostname}#", timeout=60)

def telnet_change_hostname():
    try:
        # Start Telnet session
        telnet_session = pexpect.spawn(f"telnet {host}", timeout=60)
        telnet_session.logfile = open("telnet_log.txt", "wb")

        # Logging in
        telnet_session.expect("Username:", timeout=60)
        telnet_session.sendline(user)

        telnet_session.expect("Password:", timeout=60)
        telnet_session.sendline(password)

        # Enable privileged mode
        telnet_session.expect(">", timeout=60)
        telnet_session.sendline("enable")

        telnet_session.expect("Password:", timeout=60)
        telnet_session.sendline(password_enable)

        # Configuring hostname
        telnet_session.expect("#", timeout=60)
        telnet_session.sendline("configure terminal")
        telnet_session.expect(r"\(config\)#", timeout=60)
        telnet_session.sendline(f"hostname {new_hostname}")
        telnet_session.expect(f"{new_hostname}(config)#", timeout=60)
        telnet_session.sendline("end")

        # Configure ACL and Syslog
        configure_acl_syslog(telnet_session, new_hostname)

        # Save configuration
        telnet_session.expect(f"{new_hostname}#", timeout=120)
        telnet_session.sendline("write memory")

        # Display running configuration
        telnet_session.expect(f"{new_hostname}#", timeout=60)
        telnet_session.sendline("show running-config")

        telnet_session.expect(f"{new_hostname}#", timeout=120)
        running_config = telnet_session.before.decode('utf-8')

        # Save the running configuration to a file
        with open("telnet_running_config.txt", "w") as file:
            file.write(running_config)

        # Close the session
        telnet_session.sendline("exit")
        telnet_session.close()

        print("Telnet Script Successful. Configuration saved.")

    except pexpect.TIMEOUT:
        print("The Telnet script timed out while waiting for a response.")
    except pexpect.EOF:
        print("Unexpected end of file. The Telnet connection may have been closed.")
    except Exception as e:
        print(f"An error occurred in Telnet: {str(e)}")
    finally:
        if telnet_session.isalive():
            telnet_session.close()

def ssh_change_hostname():
    try:
        # Start SSH session
        ssh_session = pexpect.spawn(f"ssh {user}@{host}", timeout=60)
        ssh_session.logfile = open("ssh_log.txt", "wb")

        # Accept SSH key if prompted
        i = ssh_session.expect(["Password:", "Are you sure you want to continue connecting (yes/no)?", pexpect.TIMEOUT])
        if i == 1:
            ssh_session.sendline("yes")
            ssh_session.expect("Password:", timeout=60)

        # Logging in
        ssh_session.sendline(password)

        # Enable privileged mode
        ssh_session.expect(">", timeout=60)
        ssh_session.sendline("enable")

        ssh_session.expect("Password:", timeout=60)
        ssh_session.sendline(password_enable)

        # Configuring hostname
        ssh_session.expect("#", timeout=60)
        ssh_session.sendline("configure terminal")
        ssh_session.expect(r"\(config\)#", timeout=60)
        ssh_session.sendline(f"hostname {new_hostname}")
        ssh_session.expect(f"{new_hostname}(config)#", timeout=60)
        ssh_session.sendline("end")

        # Configure ACL and Syslog
        configure_acl_syslog(ssh_session, new_hostname)

        # Save configuration
        ssh_session.expect(f"{new_hostname}#", timeout=120)
        ssh_session.sendline("write memory")

        # Display running configuration
        ssh_session.expect(f"{new_hostname}#", timeout=60)
        ssh_session.sendline("show running-config")

        ssh_session.expect(f"{new_hostname}#", timeout=120)
        running_config = ssh_session.before.decode('utf-8')

        # Save the running configuration to a file
        with open("ssh_running_config.txt", "w") as file:
            file.write(running_config)

        # Close the session
        ssh_session.sendline("exit")
        ssh_session.close()

        print("SSH Script Successful. Configuration saved.")

    except pexpect.TIMEOUT:
        print("The SSH script timed out while waiting for a response.")
    except pexpect.EOF:
        print("Unexpected end of file. The SSH connection may have been closed.")
    except Exception as e:
        print(f"An error occurred in SSH: {str(e)}")
    finally:
        if ssh_session.isalive():
            ssh_session.close()

# Running both Telnet and SSH scripts
telnet_change_hostname()
ssh_change_hostname()
