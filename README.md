<div align="center">
<img width="60px" src="https://pts-project.org/android-chrome-512x512.png">
<h1>PiRogue Tool Suite telemetry</h1>
<p>
This package installs the privacy-preserving telemetry to measure project adoption. Have a look to our website to <a href="https://pts-project.org/" alt="Learn more about PTS">learn more PiRogue Tool Suite</a>.
</p>
<p>
License: GPLv3
</p>
</div>

# Why?
The telemetry is used to measure the adoption of the project, but also to get some information about the hardware used and thus anticipate the support of widely used but not yet fully supported hardware. Telemetry data is collected on a daily basis.

The collected data is stored for a year on a server managed by us, hosted by Hetzner in Germany.

# How to opt-out
You can use the command
```
sudo pirogue-telemetry config disable
```

You can also delete the entire package with the command:
```
sudo apt purge pirogue-telemetry
```

# How to get the data being deleted
To get the data we collected about your PiRogue being deleted, reach out to us by email at `hello[the round symbol]pts-project.org` and specify the ID or the sha256 of the ID of your PiRogue.

You can find the ID (`unique_id`) of your PiRogue by running the command:
```
sudo pirogue-telemetry config show
```

# What data we collect
The unique ID collected corresponds to the sha256 sum of the ID generated at its first launch. The AS and the country where the PiRogue is connected from are determined by making a call to https://ip-info.pts-project.org/json. We do not collect any other data than what's listed here.

Here is an example of the data we collect on a daily basis:
```json 
{
  "unique_id": "81f672fe973c6e70acd043b4a4845fa38e7425d290678042b7e72e53661a9347",
  "asn": "3215",
  "asn_name": "Orange",
  "country_code": "FR",
  "country_name": "France",
  "os_arch": "x86_64",
  "os_id": "ubuntu",
  "os_name": "Ubuntu",
  "os_type": "linux",
  "os_version": "22.04"
}
```