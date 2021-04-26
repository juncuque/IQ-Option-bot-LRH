# IQ-Option-bot-LRH
An automatic bot for IQ Option, using BBands as main strategy. Plus configurations and simulator.

# How to make it work
- First you need to have Python 3.7 and it's pip installed.
- Then you need to have the proper libraries for the code to work by executing "install_libraries.bat" or installing one by one as they are shown in the code.
  IMPORTANT NOTE: Never trust .bat files, it's always recomended to right-click and select "edit" to see what the code is about before executing them. It also goes for modifing or adding code without any kwnoledge of what you're doing.
- Finally, you can execute "@startbot.bat" or use the CMD in the folder with the command: "python botexe.py".
- Upon the start of the program you can move within it by typing the numbers or commands show in the screen and sending with the "enter" button.
- At first, you'll be asked to login with your IQ Option account, you may do so putting your email and password, do not worry because that information is going to stay only on your PC and will be encrypted with our hardware serial ID, meaning that it's only possible to uncrypt it if you run the program within your PC's hardware.
- You'll now be presented with a menu, you're free to explore as everything has a brief explanation within the pages, just do know that by tipying "0" you'll start the bot in the PRACTICE account of your profile, to change it (although not recomended unless the configuration had been deeply tested) you can do so at the "Account Information".


# Functional BOT
The bot is completely automatic once you start it, you can set the configuration, desired payout to be, and max loss limit in a single run beforehand at the configuration's menu. 

You'll be able to see the result in real time, together with what are the stats on each BINARY option and each individual bet. It searches, holds and updates every Binary option automaticly, being able to have an unlimited number of rows. Until where I stopped coding, only Binaries are available for the bot to work on.

To stop it, you simply click to close the window normally. 

You can have multiple windows of the the bot working simultaneously, but it's not recomended to do that with them on the same configuration, because they may righting different/wrong results on the save file and maybe even crashing.

The results in the bets will be saved on the configuration file so you can see the winrate of it even between different days you started the bot.


# Simulations
To do a simulation first you need to open the cataloguer, it will simply collect all the data from the IQ Option servers from past values on the binary options. (2 Months = 12.6GB;  1 Week = 1.49GB; 1 Day = 218MB) {They are day's worth, meaning that they always are going to be more than a day, because IQ Option closes for somedays and sometimes}

Then, you'll be able to do a simulation with the collected data, there are going to be two options: multi-simulation and single-simulation. For multisimulation you can hold an array of values for each configuration variable for it to cross-test, while the single-simulation will only simulate with the current selected configuration.

It'll be slow, depending on the cataloguer's time and how many configuration you're testing, and at your first simulation you'll create a "cache" which will allow for next simulation with similar values to be faster, whatever it will also be very storage costly, being a matter of dozens of GBs (Ex.: A 2 Months cache can reach around 200GB, and it can be bigger depending in who many cross-test you make)

Don't worry about keeping your PC turned on all the time, I made a save system where on the end of each configuration you can quit the program anytime and continue afterwards on the last configuration saved.

At the end of it, you'll be presented with a report of all the configurations and a "podium" of which were the best, you can select by typing their position number and add them to your configuration list.


NOTE: Some Binaries won't have an result, probably because the variable of "bbands_desvio" is out of range in some currencies. (or something like that)


# About the bot
It's the first time I coded in python, so don't expect it being organized or pretty to look at. 

I decided to abbandon this project after 2 months coding it, after realizing that this bot wouldn't be a "gold mine" as I was hoping for and that it would have a massive impact on my CPU to truly try reaching a good strategy. 

Anyway, my secondary objective was to learn more about coding and I think I did learn a lot by making this, so there's that.


# Results
If anyone wants to know how good this bot results are: well, I think I did found an strategy different from 50% winrate, which after days of real betting and months-worth at the simulator I ended up with some strategies that reached somewhere about 51.6% winrate, which is still lower than the 52.6% needed to start profiting from a 90% payout. Maybe if I tested out more strategies and implemented other ideas I had, I believe it would be possible to increase it even further, maybe to a point where it has some profit at lower payouts. 

BUT I must say, coding it got me beat, not me nor my CPU wants it anymore, and yes, after somewhere about 1 month in non-stop simulations my CPU started malfunctioning a bit, now it always works in overclock for some reason, don't know why but it decreased a bit since the last time I simulated anything but no major errors happened to my PC until now.


# License
For anyone wanting to continue/use my work, I lend this code here in github freely, whatever I placed a copyright license on it, the GLPv3, which basicly rules that:
1. Anyone can copy, modify and distribute this software.
2. You have to include the license and copyright notice with each and every distribution.
3. You can use this software privately.
4. You can use this software for commercial purposes.
5. If you dare build your business solely from this code, you risk open-sourcing the whole code base.
6. If you modify it, you have to indicate changes made to the code.
7. Any modifications of this code base MUST be distributed with the same license, GPLv3.
8. This software is provided without warranty.
9. The software author or license can not be held liable for any damages inflicted by the software.
