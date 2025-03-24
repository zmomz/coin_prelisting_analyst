import subprocess
import os

# Define the Alembic configurations
ALEMBIC_CONFIGS = [
    {
        "ini_file": "migrations/main/alembic_main.ini",
        "migrations_folder": "migrations/main",
    },
    {
        "ini_file": "migrations/test/alembic_test.ini",
        "migrations_folder": "migrations/test",
    },
]

def run_alembic_command(command, *args):
    """
    Executes an Alembic command for each configured database.
    
    :param command: Alembic command (e.g., 'upgrade', 'downgrade', 'revision', 'history', 'current')
    :param args: Additional arguments for the command (e.g., "head" for 'upgrade')
    """
    for config in ALEMBIC_CONFIGS:
        ini_file = config["ini_file"]
        migrations_folder = config["migrations_folder"]
        
        print(f"\n[INFO] Running '{command} {args}' for {ini_file} ({migrations_folder})")

        cmd = ["alembic", "-c", ini_file, command] + list(args)
        
        try:
            subprocess.run(cmd, check=True)
            print(f"[SUCCESS] {command} executed successfully for {ini_file}")
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] Failed to execute {command} for {ini_file}: {e}")

def upgrade_all(revision="head"):
    """Applies all migrations up to the latest revision for all databases."""
    run_alembic_command("upgrade", revision)

def downgrade_all(revision="-1"):
    """Reverts the last migration for all databases."""
    run_alembic_command("downgrade", revision)

def revision_all(message="new migration", autogenerate=True):
    """Creates a new migration script for all databases."""
    args = ["--message", message]
    if autogenerate:
        args.append("--autogenerate")
    run_alembic_command("revision", *args)

def history_all():
    """Shows migration history for all databases."""
    run_alembic_command("history")

def current_all():
    """Shows the current migration for all databases."""
    run_alembic_command("current")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python alembic_wrapper.py <command> [arguments]")
        sys.exit(1)

    command = sys.argv[1]
    args = sys.argv[2:]

    if command == "upgrade":
        upgrade_all(*args)
    elif command == "downgrade":
        downgrade_all(*args)
    elif command == "revision":
        revision_all(*args)
    elif command == "history":
        history_all()
    elif command == "current":
        current_all()
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
