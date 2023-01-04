#!/bin/python

from plumbum import cli, local # See https://plumbum.readthedocs.io/en/latest/cli.html
from datetime import datetime
import json

class WhenSleep(cli.Application):
	"""
	Get last dates of system sleep and system hibernation
	"""
	verbose = cli.Flag(["v", "verbose"], help="If given, I will be very talkative")
	dates_count = cli.SwitchAttr(["n", "count"], int, default=6, help="number of dates to find")
	date_key = "__REALTIME_TIMESTAMP"

	def main(self):
		self.journalctl = local["journalctl"]

		# journalctl --no-pager -r -n 6 -o json …
		basics_options = ["--no-pager", "-r", "-n", f"{self.dates_count}", "-o", "json"]

		# journalctl --no-pager -r -n 6 -o json -u "systemd-poweroff" --grep "Finished"
		systemd_poweroff = self.run_journalctl(basics_options + ["-u", "systemd-poweroff", "--grep", "Finished"], "systemd_poweroff")
		# journalctl --no-pager -r -n 6 -o json -u "systemd-suspend" --grep "Finished"
		systemd_suspend_wake_up = self.run_journalctl(basics_options + ["-u", "systemd-suspend", "--grep", "Finished"], "systemd_suspend wake_up")
		# journalctl --no-pager -r -n 6 -o json -u "systemd-suspend" --grep "Entering"
		systemd_suspend_sleep = self.run_journalctl(basics_options + ["-u", "systemd-suspend", "--grep", "Entering"], "systemd_suspend sleep")
		# journalctl --no-pager -r -n 6 -o json --grep "SYSTEM_BOOT"
		system_boot = self.run_journalctl(basics_options + ["--grep", "SYSTEM_BOOT"], "boot")


		log_list = systemd_poweroff + systemd_suspend_wake_up + systemd_suspend_sleep + system_boot
		log_list = self.sort_by_date(log_list)
		for log in log_list[:self.dates_count]:
			print(self.log_to_str(log))

	def run_journalctl(self, options, name):
		result = self.journalctl(options)
		result = "[" + ",".join(result.split("\n")[:-1]) + "]" # Because it somehow doesn’t format it as a json list by default
		result = json.loads(result)
		for log in result:
			log["name"] = name

		return result

	def sort_by_date(self, log_list):
		return sorted(log_list, key=lambda log: log[self.date_key], reverse=True)

	def log_to_str(self, log):
		time_stamp = int(log[self.date_key])/1_000_000
		date = datetime.fromtimestamp(time_stamp)
		date_str = date.strftime("%d/%m/%Y %H:%M:%S")
		name = log["name"]
		message = log["MESSAGE"]
		
		result = f"{date_str} : {name} : {message}"

		
		return result

if __name__ == "__main__":
	WhenSleep.run()

def test(argv=["plop"]):
	WhenSleep.run(argv, False)
