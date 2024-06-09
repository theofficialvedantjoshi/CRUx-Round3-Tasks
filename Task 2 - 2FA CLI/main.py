import click.testing
import add_service, modify_service, remove_service, show_service, json_file
import pyotp
import time
import datetime
import os
import click
import math
from getpass import getpass

logo = """
$$\    $$\ $$$$$$$$\ $$$$$$$\                   $$$$$$\ $$$$$$$$\ $$$$$$$\  
$$ |   $$ |$$  _____|$$  __$$\                 $$  __$$\\__$$  __|$$  __$$\ 
$$ |   $$ |$$ |      $$ |  $$ | $$$$$$$\       $$ /  $$ |  $$ |   $$ |  $$ |
\$$\  $$  |$$$$$\    $$ |  $$ |$$  _____|      $$ |  $$ |  $$ |   $$$$$$$  |
 \$$\$$  / $$  __|   $$ |  $$ |\$$$$$$\        $$ |  $$ |  $$ |   $$  ____/ 
  \$$$  /  $$ |      $$ |  $$ | \____$$\       $$ |  $$ |  $$ |   $$ |      
   \$  /   $$$$$$$$\ $$$$$$$  |$$$$$$$  |       $$$$$$  |  $$ |   $$ |      
    \_/    \________|\_______/ \_______/        \______/   \__|   \__|                                                                                  
"""


@click.group(
    context_settings=dict(help_option_names=["--help"]),
    help="VEDs TOTP Two Factor Authenticator.",
)
def main():
    click.echo(click.style(logo, fg="cyan") + "\n")


@click.group(help="Commands for adding configurations and setting the editor.")
def add():
    pass


@click.command()
def set_editor():
    """Set the text editor."""
    click.clear()
    click.echo(click.style(logo, fg="cyan") + "\n")
    editor = click.prompt("Enter your preferred text editor", type=str)
    add_service.set_editor(editor)
    click.echo(click.style(f"Editor set to {editor}", fg="green"))


@click.command(help="Add a new service.")
def set_service():
    click.clear()
    click.echo(click.style(logo, fg="cyan") + "\n")
    add_service.init_database()
    key = click.prompt("Enter your Database Encryption Key", type=str, hide_input=True)
    add_service.set_service(key)
    click.echo(click.style("Service added successfully.", fg="green"))


@click.group(help="Commands for displaying TOTP and QR code.")
def show():
    """Commands for displaying TOTP and QR code."""


@click.command(help="Get the TOTP for a service with a timer.")
def show_totp():
    click.clear()
    click.echo(click.style(logo, fg="cyan") + "\n")
    service = click.prompt("Enter the service\n", type=str)
    key = getpass("Enter your Database Encryption Key: ")
    seed = show_service.fetch_seed(service, key)
    otp, time_remaining = show_service.show_otp(seed)
    time_remaining = round(time_remaining)
    while True:
        otp = show_service.show_otp(seed)[0]
        click.clear()
        click.echo(click.style(logo, fg="cyan") + "\n")
        progress_bar = f"{'█' * time_remaining}{'▒' * (30 - time_remaining)}"
        click.echo(
            click.style(
                f"SERVICE: {service}\n\nOTP: {otp}  {progress_bar}", fg="yellow"
            )
        )
        time.sleep(1)
        time_remaining -= 1
        if time_remaining == 0:
            time_remaining = 30


@click.command(help="Show QR code for a service.")
def show_qr():
    click.clear()
    click.echo(click.style(logo, fg="cyan") + "\n")
    service = click.prompt("Enter the service\n", type=str)
    key = getpass("Enter your Database Encryption Key: ")
    seed = show_service.fetch_seed(service, key)
    click.echo(
        click.style(
            "Scan the QR code below to add the service to your authenticator app.\n",
            fg="green",
        )
    )
    click.echo(click.style(f"Service: {service}\n\n", fg="blue"))
    show_service.show_qr(service, seed)


@click.group(help="Commands for modifying services.")
def modify():
    """Edit services, usernames and seeds."""
    pass


@click.command()
def edit_service():
    """Modify a service."""
    click.clear()
    click.echo(click.style(logo, fg="cyan") + "\n")
    service_from = click.prompt("Enter the service you want to change\n", type=str)
    service_to = click.prompt("Enter the new service\n", type=str)
    key = getpass("Enter your Database Encryption Key: ")
    modify_service.modify_service(service_from, service_to, key)
    click.echo(click.style("Service updated successfully.", fg="green"))


@click.command()
def edit_username():
    """Modify the username for a service."""
    click.clear()
    click.echo(click.style(logo, fg="cyan") + "\n")
    service = click.prompt("Enter the service\n", type=str)
    username_from = click.prompt("Enter the old username\n", type=str)
    username_to = click.prompt("Enter the new username\n", type=str)
    key = getpass("Enter your Database Encryption Key: ")
    modify_service.modify_username(service, username_from, username_to, key)
    click.echo(click.style("Username updated successfully.", fg="green"))


@click.command()
def edit_seed():
    """Modify the seed for a service."""
    click.clear()
    click.echo(click.style(logo, fg="cyan") + "\n")
    service = click.prompt("Enter the service\n", type=str)
    username = click.prompt("Enter the username\n", type=str)
    seed = click.prompt("Enter the new seed\n", type=str)
    key = getpass("Enter your Database Encryption Key: ")
    modify_service.modify_seed(service, username, seed, key)
    click.echo(click.style("Seed updated successfully.", fg="green"))


@click.group()
def files():
    """Export and import data in json format."""
    pass


@click.command()
def export():
    """Export data in json format into an encrypted zip file."""
    click.clear()
    click.echo(click.style(logo, fg="cyan") + "\n")
    key = getpass("Enter your Database Encryption Key: ")
    password = getpass("Set a password for the zip file: ")
    json_file.export_db(key, password)


@click.command()
def import_json():
    """Import data from a json file."""
    click.clear()
    click.echo(click.style(logo, fg="cyan") + "\n")
    key = getpass("Enter your Database Encryption Key: ")
    file_path = click.prompt("Enter the path to the json file\n", type=str)
    json_file.import_db_json(key, file_path)
    click.echo(click.style("Service added successfully.", fg="green"))


@click.command()
def import_zip():
    """Import data from a zip file."""
    click.clear()
    click.echo(click.style(logo, fg="cyan") + "\n")
    key = getpass("Enter your Database Encryption Key: ")
    password = getpass("Enter the password for the zip file: ")
    file_path = click.prompt("Enter the path to the zip file\n", type=str)
    json_file.import_db_zip(key, password, file_path)
    click.echo(click.style("Services added successfully.", fg="green"))


@click.command()
def remove():
    """Remove a service."""
    click.clear()
    click.echo(click.style(logo, fg="cyan") + "\n")
    service = click.prompt("Enter the service\n", type=str)
    username = click.prompt("Enter the username\n", type=str)
    key = getpass("Enter your Database Encryption Key: ")
    remove_service.remove_service(service, username, key)
    click.echo(click.style("Service removed successfully.", fg="green"))


add.add_command(set_editor, "set_editor")
add.add_command(set_service, "add_service")

modify.add_command(edit_service, "edit_service")
modify.add_command(edit_username, "edit_username")
modify.add_command(edit_seed, "edit_seed")

show.add_command(show_totp, "show_totp")
show.add_command(show_qr, "show_qr")
files.add_command(export, "export")
files.add_command(import_json, "import_json")
files.add_command(import_zip, "import_zip")

main.add_command(modify, "modify")
main.add_command(add, "add")
main.add_command(show, "show")
main.add_command(files, "files")
main.add_command(remove, "remove")

if __name__ == "__main__":
    main()
