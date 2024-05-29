import add_service, modify_service, remove_service, show_service
import pyotp
import time
import datetime
import os
import click
import math

logo = """
░█████╗░██╗░░░░░██╗    ████████╗░█████╗░████████╗██████╗░    ██████╗░███████╗░█████╗░
██╔══██╗██║░░░░░██║    ╚══██╔══╝██╔══██╗╚══██╔══╝██╔══██╗    ╚════██╗██╔════╝██╔══██╗
██║░░╚═╝██║░░░░░██║    ░░░██║░░░██║░░██║░░░██║░░░██████╔╝    ░░███╔═╝█████╗░░███████║
██║░░██╗██║░░░░░██║    ░░░██║░░░██║░░██║░░░██║░░░██╔═══╝░    ██╔══╝░░██╔══╝░░██╔══██║
╚█████╔╝███████╗██║    ░░░██║░░░╚█████╔╝░░░██║░░░██║░░░░░    ███████╗██║░░░░░██║░░██║
░╚════╝░╚══════╝╚═╝    ░░░╚═╝░░░░╚════╝░░░░╚═╝░░░╚═╝░░░░░    ╚══════╝╚═╝░░░░░╚═╝░░╚═╝
"""

@click.group()
def main():
    click.echo(logo + "\n")


@click.group()
def add():
    """Group for adding configurations."""
    pass


# # prompt for editor
@click.command()
def set_editor():
    click.clear()
    """Set the default editor."""
    editor = click.prompt("Enter your preferred text editor")
    add_service.set_editor(editor)


@click.command()
def set_service():
    """Set the default service."""
    add_service.init_database()
    add_service.set_service()


add.add_command(set_editor, "set_editor")
add.add_command(set_service, "set_service")


@click.group()
def show():
    """Group for showing otp."""
    pass


@click.command()
def show_totp():
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


show.add_command(show_totp, "show_totp")


main.add_command(add, "add")
main.add_command(show, "show")


if __name__ == "__main__":
    main()
