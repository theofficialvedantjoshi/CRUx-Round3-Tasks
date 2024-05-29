import add_service, modify_service, remove_service, show_service
import pyotp
import time
import datetime
import os
import click
import math
from qrcode import QRCode

logo = """
░█████╗░██╗░░░░░██╗    ████████╗░█████╗░████████╗██████╗░    ██████╗░███████╗░█████╗░
██╔══██╗██║░░░░░██║    ╚══██╔══╝██╔══██╗╚══██╔══╝██╔══██╗    ╚════██╗██╔════╝██╔══██╗
██║░░╚═╝██║░░░░░██║    ░░░██║░░░██║░░██║░░░██║░░░██████╔╝    ░░███╔═╝█████╗░░███████║
██║░░██╗██║░░░░░██║    ░░░██║░░░██║░░██║░░░██║░░░██╔═══╝░    ██╔══╝░░██╔══╝░░██╔══██║
╚█████╔╝███████╗██║    ░░░██║░░░╚█████╔╝░░░██║░░░██║░░░░░    ███████╗██║░░░░░██║░░██║
░╚════╝░╚══════╝╚═╝    ░░░╚═╝░░░░╚════╝░░░░╚═╝░░░╚═╝░░░░░    ╚══════╝╚═╝░░░░░╚═╝░░╚═╝
"""


@click.group(help="CLI TOTP Two Factor Authenticator.")
def main():
    click.echo(logo + "\n")


@click.group(help="Use this command to set_editor and add_service.")
def add():
    """Group for adding configurations."""
    pass


# # prompt for editor
@click.command(help="Set your preferred text editor.")
def set_editor():
    click.clear()
    click.echo(logo + "\n")
    """Set the default editor."""
    editor = click.prompt("Enter your preferred text editor")
    add_service.set_editor(editor)


@click.command(help="add a new Service")
def set_service():
    click.clear()
    click.echo(logo + "\n")
    """add a new Service"""
    add_service.init_database()
    add_service.set_service()


add.add_command(set_editor, "set_editor")
add.add_command(set_service, "set_service")


@click.group(help="Get the TOTP for a service with a timer.")
def show():
    click.clear()
    click.echo(logo + "\n")
    """Group for showing otp."""
    pass


@click.command(help="Get the TOTP for a service with a timer.")
def show_totp():
    click.clear()
    click.echo(logo + "\n")
    """Show the otp."""
    service = click.prompt("Enter the service")
    seed = show_service.fetch_seed(service)
    otp, time_remaining = show_service.show_otp(seed)
    time_remaining = round(time_remaining)
    while True:
        otp = show_service.show_otp(seed)[0]
        click.clear()
        click.echo(logo + "\n")
        click.echo(
            f"SERVICE: {service}\n\nOTP: {otp}  "
            + "█" * time_remaining
            + "▒" * (30 - time_remaining)
        )
        time.sleep(1)
        time_remaining -= 1
        if time_remaining == 0:
            time_remaining = 30


@click.command(help="Show qr code for a service.")
def show_qr():
    click.clear()
    click.echo(logo + "\n")
    """Show the otp."""
    service = click.prompt("Enter the service")
    seed = show_service.fetch_seed(service)
    click.echo("Scan the QR code below to add the service to your authenticator app.\n")
    click.echo("Service: " + service + "\n\n")
    show_service.show_qr(service, seed)


show.add_command(show_totp, "show_totp")
show.add_command(show_qr, "show_qr")


main.add_command(add, "add")
main.add_command(show, "show")


if __name__ == "__main__":
    main()
