import jinja2
import os


path = "./config"

def main():
    # Generate secret key
    secret_key = os.environ.get("SECRET_KEY", os.urandom(128).hex())
    
    # Create user
    admin_user = os.environ.get("ADMIN_USER", "raspiadmin")
    admin_password = os.environ.get("ADMIN_PASSWORD", os.urandom(10).hex())
    
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
    env = {
        "DJANGO_SUPERUSER_USERNAME": admin_user,
        "DJANGO_SUPERUSER_EMAIL": f"{admin_user}@localhost",
        "DJANGO_SUPERUSER_PASSWORD": admin_password,
        "SECRET_KEY": secret_key,
        "ALLOWED_HOSTS": allowed_hosts,
        "LISTEN": listen,
        "PORT": port,
    }
    with open(f"{path}/.env", "w+") as f:
        for k, v in env.items():
            f.write(f"{k}={v}\n")
    
    print("Config file written to config/config.yml")
    print(f"Open the service from your browser at http://localhost:{port}/")
    print(f"Login with username: {admin_user} and password: {admin_password}")


if __name__ == "__main__":
    main()