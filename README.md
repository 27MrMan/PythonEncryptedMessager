# 27's Ultimate Encrypted Communication Solution >:3
(yes i know very original)

## Idea
This project aims to create a way to communicate through UDP (or whatever network method you prefer) between multiple people through one main server

Probably been done before, but this time I plan to make it really simple, with most of the basic functionality.

## Our Goal
The biggest priority here has been given to data security, where just about all the communication done over the internet is encrypted. however, the program is still simple enough for the average github enjoyer to set up and use within a few hours :3

## Details
### Encryption
- We use **RSA** encryption (yay RSA :3) to send a randomized **aes256** key, and communicate everything else with aes encryption.
- Passwords are stored on the server with **SHA-384** hashing
- Passwords will never be stored anywhere in plaintext ~w~

### Killswitch
- The client will have two kinds of killswitches in case of unforseen circumstances
- Messages will also be sent to server to take security measures when killswitches are activated

### Data Storage
- This program works on the assumption that the server is in a relatively safe place where encryption isnt needed (data is stored in plaintext for speed)
HOWEVER, i may, in the future, add an option for optional aes encryption of message in storage- idk

## Extra
this program is still under construction~
idk what you're doing here lol