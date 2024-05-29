import add_service, modify_service, remove_service, show_service
import pyotp
import time
import datetime
import os
import click
import math
from getpass import getpass

logo = """
░█████╗░██╗░░░░░██╗    ████████╗░█████╗░████████╗██████╗░    ██████╗░███████╗░█████╗░
██╔══██╗██║░░░░░██║    ╚══██╔══╝██╔══██╗╚══██╔══╝██╔══██╗    ╚════██╗██╔════╝██╔══██╗
██║░░╚═╝██║░░░░░██║    ░░░██║░░░██║░░██║░░░██║░░░██████╔╝    ░░███╔═╝█████╗░░███████║
██║░░██╗██║░░░░░██║    ░░░██║░░░██║░░██║░░░██║░░░██╔═══╝░    ██╔══╝░░██╔══╝░░██╔══██║
╚█████╔╝███████╗██║    ░░░██║░░░╚█████╔╝░░░██║░░░██║░░░░░    ███████╗██║░░░░░██║░░██║
░╚════╝░╚══════╝╚═╝    ░░░╚═╝░░░░╚════╝░░░░╚═╝░░░╚═╝░░░░░    ╚══════╝╚═╝░░░░░╚═╝░░╚═╝
"""


@click.group(
    context_settings=dict(help_option_names=["--help"]),
    help="CLI TOTP Two Factor Authenticator.",
)
def main():
    click.echo(click.style(logo, fg="cyan") + "\n")


@click.group(help="Commands for adding configurations and setting the editor.")
def add():
    pass


@click.command(help="Set your preferred text editor.")
def set_editor():
    click.clear()
    click.echo(click.style(logo, fg="cyan") + "\n")
    editor = click.prompt("Enter your preferred text editor", type=str)
    add_service.set_editor(editor)
    click.echo(click.style(f"Editor set to {editor}", fg="green"))


@click.command(help="Add a new service.")
def set_service():
    click.clear()
    click.echo(click.style(logo, fg="cyan") + "\n")
    key = click.prompt("Enter your Database Encryption Key", type=str, hide_input=True)
    add_service.init_database()
    add_service.set_service(key)
    click.echo(click.style("Service added successfully.", fg="green"))


add.add_command(set_editor, "set_editor")
add.add_command(set_service, "set_service")


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


show.add_command(show_totp, "show_totp")
show.add_command(show_qr, "show_qr")

main.add_command(add, "add")
main.add_command(show, "show")

if __name__ == "__main__":
    main()
