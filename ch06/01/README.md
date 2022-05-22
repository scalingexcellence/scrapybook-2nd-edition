# Run `scrapyrt` and `scrapyd` as services

To run scrapyrt and scrapyd as services move the two `.service` files in /lib/systemd/system (with `sudo`) and then use

* `sudo systemctl enable scrapyrt.service` and `sudo systemctl start scrapyrt.service`
* `sudo systemctl enable scrapyd.service` and `sudo systemctl start scrapyd.service`

To check logs you can use e.g. `journalctl -u scrapyrt.service`.
