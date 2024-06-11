# Cheapskate's GPS Tracker using an iPhone

Find My iPhone will only return the device's last known location, so this script polls the Find My iPhone service at regular intervals and saves the locations to a local file for later retrieval.

For devices which support this (ie, iPhone 14 and above), locations can be pushed via satellite when no phone signal is available, allowing for a cheapskate's satellite tracker function.

## setup

 - create a file `config.json` at the root level, and include the iCloud email and password:

```
{
    "email": "icloud_email@gmail.com",
    "password": "icloud_password"
}
```

 - `pip3 install pyicloud`

Run the script, and enter the 2-factor-authentication code if requested to do so (the timing of this request from Apple is unpredictable).

Next it should prompt you for the index of the device to track:

```
0 MacBook Pro
1 iPhone 14 Pro
2 iPhone 6
3 Apple Watch SE
Enter the index of the iPhone you want to track: 1
```

Every 10 minutes, the tracked device's location should be reported, and saved to the CSV file:
`['2024-06-11 20:39:23', 1718102359643, -34.77, 150.67]`

### TODO:

Replace or augment the simple CSV file storage with a more robust online database, such as Firebase or PostgreSQL, etc.      
