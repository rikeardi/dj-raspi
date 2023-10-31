import jinja2
import os


path = "/code/config"

def main():
    # Generate secret key
    secret_key = os.environ.get("SECRET_KEY", os.urandom(128).hex())
    
    # Create user
    admin_user = os.environ.get("ADMIN_USER", "raspiadmin")
    admin_password = os.environ.get("ADMIN_PASSWORD", os.urandom(128).hex())
    
    # Add service host info
    listen = os.environ.get("LISTEN", "0.0.0.0")
    port = os.environ.get("PORT", "8000")
    allowed_hosts = os.environ.get("ALLOWED_HOSTS", "*")
    
    # Create config.yml from jinja2 template
    config_template = jinja2.Template(open(f"config.yml.j2").read())
    config = config_template.render(
        secret_key=secret_key,
        admin_user=admin_user,
        admin_password=admin_password,
        listen=listen,
        port=port,
        allowed_hosts=allowed_hosts,
    )
    
    # Write config.yml
    with open(f"{path}/config.yml", "w+") as f:
        f.write(config)

    # Add config to environment
    os.environ["ADMIN_USER"] = admin_user
    os.environ["ADMIN_PASSWORD"] = admin_password
    os.environ["SECRET_KEY"] = secret_key
    os.environ["LISTEN"] = listen
    os.environ["PORT"] = port
    os.environ["ALLOWED_HOSTS"] = allowed_hosts


if __name__ == "__main__":
    main()