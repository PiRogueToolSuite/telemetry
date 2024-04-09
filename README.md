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

# How to opt-out
Edit the file `/var/lib/pirogue/config/telemetry.json` and set `enabled` to `false`.

You can also delete the entire package with the command:
```
sudo apt purge pirogue-telemetry
```

# What data we collect
Here is an example of the data we collect on a daily basis about your PiRogue
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