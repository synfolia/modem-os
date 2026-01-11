package main

import (
    "log"

    scrollengine "Maple-OS/modem_os/core/scroll_engine"
)

func main() {
	if err := scrollengine.StartServer(":8282"); err != nil {
		log.Fatal(err)
	}
}
