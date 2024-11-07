import pexpect
import difflib

# Device details
host = "192.168.56.101"
user = "cisco"
password = "cisco123!"
password_enable = "cisco123!"
new_hostname = "host1"
offline_config_file = "local_running_config.txt"  # File storing the offline configuration

# Hardening checks dictionary
hardening_checks = {
    "SSH enabled": "ip ssh version 2",
    "Telnet disabled": "no service telnet",
    "Password encryption": "service password-encryption",
    "Logging enabled": "logging buffered",
    "NTP configured": "ntp server",
    "Strong password required": "enable secret",
    "Access Control List (ACL) configured": "access-list"
}

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
        "logging host 192.168.56.101",  # Replace with your syslog server IP
        "logging trap informational"    # Set log level to informational
    ]

    # Sending Syslog commands
    for command in syslog_commands:
        session.sendline(command)
        session.expect(r"\(config\)#", timeout=60)

    session.sendline("end")
    session.expect(f"{hostname}#", timeout=60)

def compare_configs(current_config, offline_file):
    # Load the offline configuration file
    with open(offline_file, "r") as file:
        offline_config = file.readlines()

    # Generate a unified diff between the current and offline configuration
    diff = difflib.unified_diff(
        offline_config,
        current_config.splitlines(keepends=True),
        fromfile="Offline Config",
        tofile="Current Config",
        lineterm=""
    )

    # Print the differences
    print("\nDifferences between current and offline configuration:")
    for line in diff:
        print(line)

def check_hardening(running_config):
    print("\nComparison against Cisco hardening guidelines:")
    for check, rule in hardening_checks.items():
        if rule in running_config:
            print(f"[PASS] {check}")
        else:
            print(f"[FAIL] {check}")

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

        # Compare with offline config
        compare_configs(running_config, offline_config_file)

        # Check hardening
        check_hardening(running_config)

        # Close the session
        telnet_session.sendline("exit")
        telnet_session.close()

        print("Telnet Script Successful. Configuration saved and analyzed.")

    except pexpect.TIMEOUT:
        print("The Telnet script timed out while waiting for a response.")
    except pexpect.EOF:
        print("Unexpected end of file. The Telnet connection may have been closed.")
    except Exception as e:
        print(f"An error occurred in Telnet: {str(e)}")
    finally:
        if telnet_session.isalive():
            telnet_session.close()

# Running the updated Telnet script (SSH function would be similar)
telnet_change_hostname()
