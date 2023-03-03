"""
    Used for generating a list of commands for amending git commit dates during a rebase, for Windows.

    This will change the commit dates of a git repo's history from the most recent commit and working backwards via:
        git rebase -i HEAD~{your chosen commit count}
    to random dates within a range between two chosen dates, while ensuring reasonable waking hours are followed
    (with each new rebased commit date happening anywhere between 5am and 11pm).

    Since the commands generated here are specifically for the Windows environment, this won't work out-of-the-box on
    Linux or Mac, but should be easily adaptable to those platforms if you change the "cmd_change_date" variable
    to your relevant platform's command. Essentially, you need to remove the "cmd /v /c" part of the command.

    Be careful when using this, and make sure you first test on a mock repo when modifying!
"""


import os
from random import randint
from datetime import datetime, timedelta
import subprocess
import time


def random_date(start: datetime, end: datetime) -> str:
    # Between 5am and 11pm would be relevant to waking hours.
    earliest = start.replace(hour=5, minute=0, second=0)
    latest = end.replace(hour=23, minute=0, second=0)
    random_delta_seconds = randint(0, int((latest - earliest).total_seconds()))
    # Ensuring our new timestamp is within waking hours range.
    random_hour = randint(5, 23)
    timestamp_result = (earliest + timedelta(seconds=random_delta_seconds)).replace(hour=random_hour)
    # Returning the string in git acceptable timestamp format.
    return timestamp_result.strftime("%Y-%m-%dT%H:%M:%S")


def generate_timestamps(start_date, end_date, amount):
    start = datetime.strptime(start_date, "%Y-%m-%dT%H:%M:%S")
    end = datetime.strptime(end_date, "%Y-%m-%dT%H:%M:%S")
    results = []

    for i in range(amount):
        date = random_date(start, end)
        results.append(date)

    return sorted(results)


def get_start_date():
    start_date = input("\nEnter new start date.\nOr, leave blank to use 1988 for testing.\n(YYYY-MM-DDTHH:MM:SS) ")
    if start_date == "":
        start_date = "1988-01-01T12:34:56"
    return start_date


def get_end_date():
    end_date = input("\nEnter new end date.\nOr, leave blank to use 1988 for testing.\n(YYYY-MM-DDTHH:MM:SS) ")
    if end_date == "":
        end_date = "1988-12-25T12:34:56"
    return end_date


def get_rebase_length():
    count_valid = False
    commit_count = None

    while not count_valid:
        commit_count = input("How many commits do you want to rebase (not including an initial commit)? ")
        if not commit_count.isdigit():
            print("You must enter a number.")
            continue

        commit_count = int(commit_count)
        if commit_count < 1:
            print("You must rebase at least one commit.")
            continue

        count_valid = True

    return commit_count


def get_rebase_process(commit_count):
    return subprocess.Popen(
        f"git rebase -i HEAD~{commit_count}",
        shell=True,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True
    )


def generate_commands(timestamps):
    commands = []
    for timestamp in timestamps:
        windows_cmd = 'cmd /v /c'
        committer_date_cmd = f'set GIT_COMMITTER_DATE={timestamp}'
        git_commit_cmd = f'git commit --no-edit --amend --date=\'{timestamp}\''
        # Mind the required double quotes around the command.
        # Also mind that there is no space between the && and the committer_date_cmd.
        cmd_change_date = f'{windows_cmd} "{committer_date_cmd}&& {git_commit_cmd}" \n'
        commands.append(cmd_change_date)
        commands.append("git rebase --continue\n")
    return commands


def get_path():
    path = input("Enter path to git repo you'd like to rebase (leave blank for current directory):")
    if path == "":
        path = os.getcwd()
    return path


def move_to_repo():
    os.chdir(get_path())
    # confirm working directory
    print(os.getcwd())
    print(subprocess.call(
        'git log --graph --pretty=format:"%h %ad %s" --date=format-local:%Y-%m-%dT%H:%M:%S --abbrev-commit',
        shell=True
    ))
    confirm = input("Is this the correct repo? (y/n) ")
    if confirm.lower() == "n":
        move_to_repo()


if __name__ == "__main__":
    move_to_repo()
    rebase = None
    rebase_length = None
    commands = None
    try:
        rebase_length = get_rebase_length()
        rebase = get_rebase_process(rebase_length)
        commands = generate_commands(generate_timestamps(get_start_date(), get_end_date(), rebase_length))
    except KeyboardInterrupt:
        print("\n🐠💥 The rebase process has been aborted. 💥🐠\n")
        subprocess.call("git rebase --abort", shell=True)
        exit(1)

    result, err = rebase.communicate()
    if "invalid" in err:
        print("\n\n🐠💥 An invalid upstream branch was specified. Did you select too many commits? 💥🐠\n")
        print(f"Submitted command: {rebase.args}\n")
        print(f"Returned error: {err}\n")
        print("🐠💥 The rebase process has been aborted. 💥🐠\n")
        exit(1)

    time.sleep(1)  # Wait for the editor to fully open

    # Execute the rebase commands in sequence
    try:
        for i, command in enumerate(commands):
            print(f"🐠 Running command {i + 1} of {len(commands)} 🐠")
            subprocess.call(command, shell=True)
    except Exception as e:
        print(f"An error occurred:\n\n💥💥\n{e}\n💥💥\n\n")
        subprocess.call("git rebase --abort", shell=True)
        print("🐠💥 The rebase process has been aborted. 💥🐠")

    rebase.wait()
