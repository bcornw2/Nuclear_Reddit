# Nuclear Reddit Remover
![Python version](https://img.shields.io/badge/python-3.x-brightgreen.svg)

### Archive all your Reddit content, then delete everything.

#### When you delete an account on Reddit, your account goes away, but your content remains. Every post, comment, and upvote sticks around long after you delete it, and using tools like ceddit, unreddit, or [removeddit](https://removereddit.com), people can still find out who posted it. With the current climate of internet doxxing it is wise to clear any content that may lead to people identifying who you are by what you've posted. Nuclear Reddit Remover fixes that, and you won't even have to miss the things you've done. Nuclear Reddit Destroyer is a free and open-source tool that anyone can use to completely wipe away their Reddit account to prevent doxxing, identity theft, and snooping.


## Features
* Save account metadata, such as username, created date, and karma counts
* Download all submission images, videos, links, and self-texts, and the comments underneath.
* Download all of your comments, including scores, bodies, and the link to the posts
* Download every item you've ever saved, including both comments and submissions, as links.
* Edit every single comment to a custom message, or use the default.
* Delete every single comment and submission you've ever made.

## Installation
`Nuclear Reddit Remover` requires Python 3
You can find out how to install Python 3 by referencing the [following guide](https://realpython.com/installing-python/)

## Environment Config

To actually run the script, if you are not familiar with Git or cloning Git repositories, simply copy and paste the entirety of the file above titled: `Nuclear_Reddit.py`, and paste that into a text file on your local computer. Save that text file as `Nuclear_Reddit.py`, and then run it after doing the rest of the following environment config.

Configuration is easy. All you need is Python 3 installed on a Windows, Linux, or Mac computer. 

MacOS already has Python3 installed by default.
Windows users can install Python by downloading the package from here: https://www.python.org/downloads/windows/
* Windows users will need to install Python 3.7 or 3.8, then find the directory where it installed (`C:/Users/$your_username/AppData/Local/Programs/Python/Python38`) and copy this filepath, then add it to their PATH, by right clicking on `This PC` -> `Advanced System Settings` -> `Environment Variables` -> click on the `Path` field under "User Variables for $Your_Username" -> `New` -> then paste the filepath into the new field at the bottom. You will need to do this also for `pip`, which is found in the same directory, but go to `/Scripts/pip.exe`.
* So you are adding `C:/Users/$your_username/AppData/Local/Programs/Python/Python38`  and  `C:/Users/$your_username/AppData/Local/Programs/Python/Python38/Scripts/pip.exe` to your path. Now you can open up Powershell and simply type in `python` to start, and usse `pip install requests`, which wi will need to do later. 
Linux users - you guys know what you're doing.

You will need to install the following dependencies:
* `praw`
* `redvid`
* `requests`

You can do this by opening the command line, cmd.exe, PowerShell, or terminal and typing:
* `pip install praw`
* `pip install redvid`
* `pip install requests`

If you have any issues, try re-opening the command line as an administrator.

Finally, you will also need `ffmpeg`, which is an open-source tool that is required for the video submission download.

## Installing FFmpeg
### Windows: 

https://m.wikihow.com/Install-FFmpeg-on-Windows

(*restart your pc after applying these steps*)

### Linux: 

  `sudo apt install ffmpeg`

### Mac OS:

* install [Homebrew](https://brew.sh/):

  `/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"`
  
* Then:

  `$ brew install ffmpeg`


## Account Config

To configure your Reddit account to allow this script to work, you must **enable botting** by signing into Reddit as the account you want to archive, on a desktop, and in the top right corner, open up User Settings. Here, navigate to the Safety & Privacy tab. At the bottom of this page, you'll see "Manage third-party app authorization". Click into here, and "create application".

Configure the settings as below. All you have to do is set the type to "script", set the name to "nuclear_reddit", and set the "redirect uri" to the following value: `http://127.0.0.1`

Once you have this app created, you'll see a string of numbers and letters underneath the name of the app, and another in the field labeled "secret". Keep this page open as we configure the script.

In your command line, run nuclear_reddit.py by entering the following as a command into command line:

	`python nuclear_reddit.py`

You will be prompted to enter in your Reddit username and password. These will not be changed or recorded, and this part does not erase anything - yet. Then, you'll be prompted to enter in your Client_ID, which is the shorter string of numbers and letters closer to the top of the Reddit settings page. Then you'll enter your client_secret, which is the string in the field titled `secret` in the same Reddit settings page. You can copy and paste these - but just remember that in Linux and Mac, you paste into a terminal by right clicking. Windows users in PowerShell and CMD should have no problem with the traditional Ctrl+V

Please note, this program does not save your credentials. Additionally, be aware that what we just completed did NOT delete any of your Reddit content.

## Account Archival

Once you've entered in these four pieces of critical information, the script will verify credentials by submitting a post to /r/Nuclear_Reddit. If the post is able to be created, then everything looks good, and the archival can begin. You'll be prompted to proceed to the **archival** phase, which can take some time to complete, if you have an active Reddit account. Start by entering the path to the folder that you want to save your content to. The default is usually fine, as it creates a folder in your home directory. This will not delete anything. It will begin the process of indexing your posts, comments, selftexts, and saved content to a series of folders/directories that you specify. Please stay near your machine while this runs, as you will need to enter some input when selecting video and gif quality, etc. 

The default locations for the archival are:
* Mac: `/home/$your_username/Nuclear_Reddit`
* Linux: `/home/$your_username/Nuclear_Reddit`
* Windows: `C:/Users/$your_username/Nuclear_Reddit`

You can change this, but be aware that permissions may cause issues, and writing to external hard drives and other partitions may throw errors if your system is set up with different file systems. Unless you really know what you are doing, I would suggest letting the script run to completion with the default directory, and then moving or copying the contents into the desired location afterwards.

## Content Deletion

Once the archival portion of the script completes, you can either exit by answering "No" to the request to delete, or entering `Ctrl+C`. If you answer "Yes" to the request, you can continue to the deletion portion. I suggest that you verify that everything you want is included in the `Nuclear_Reddit` direcotry before doing so. The content is organized as text format, and are sorted chronologically. The script will grab every comment you've ever made, every selftext submission, every image or link submission, and a list of all your saved posts and comments. Comments made under your submissions will be included, as well as the .jpg or .png or video files. 

Here, you will be prompted to **delete** comments, or **edit** them. You can craft your own personal send-off message, or use the default one below:

`The content of this comment was removed, as Reddit has devolved into an authoritarian facebook-tier garbage site, rife with power-hungry mods and a psychopathic userbase. I have migrated to [Ruqqus](https://ruqqus.com), which is an open-source alternative. \n<sup>This action was performed easily and automatically by [Nuclear Reddit Remover](https://github.com/bcornw2/Nuclear_Reddit).`

Editing comments will erase the comment that originally existed, and you can replace the default edit text with your own, and you will prompted to do so once you reach the **deletion** phase of the script, after archival.

All submissions will be destroyed immediately, and all comments will either be edited or deleted.

If you have any issues, simply raise an issue on this Github page and we will resolve it as quickly as we can.

## TODO
* Allow customizable edit texts
* Allow gifs to save as gifs instead of .mp4 (dep on /elmoiv/redvid)

## Contributing
Please contribute! If you want to fix a bug, suggest improvements, or add a new feature to the project, just [open an issue](https://github.com/bcornw2/Nuclear_Reddit) or send me a pull request.
