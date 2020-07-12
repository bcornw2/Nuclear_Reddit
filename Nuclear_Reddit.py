import praw
import os
import datetime
import praw.models
import time
import requests
import traceback
import shutil
# from datetime import datetime
import concurrent.futures
from sys import platform
from redvid import Downloader
from pathlib import Path

comments_to_delete = []
submissions_to_delete = []
url = "https://api.pushshift.io/reddit/{}/search/?limit=1000&sort=desc&author={}&before="
url2 = "https://api.pushshift.io/reddit/comment/search/?link_id={}&limit=20000"

start_time = datetime.datetime.utcnow()

verified_accounts = []

comment_arr = []

USER_AGENT = "nuclear_reddit v.0.0.1"

location = ""

# enable botting on your account by generating API token
reddit = ''
client_id = ''
secret = ''
uname = ''
passwd = ''


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def imageDownloader(image):
    path = os.path.join(location, "submission_images")
    r = requests.get(image['url'])
    with open(os.path.join(path, image['fname']), 'wb') as f:
        f.write(r.content)


def getImages():
    path = os.path.join(location, "submission_images")
    images = []
    #  try
    go = 0
    submissions = reddit.user.me().submissions.new(limit=None)
    for submission in submissions:
        if submission.url.endswith(('jpg', 'png', 'jpeg')):
            filetype = submission.url[-3:]
            fname = submission.title.replace(" ", "_")
            fname = fname.replace(".", "_")
            fname = fname[:20] + "." + filetype
            if not os.path.isfile(os.path.join(path, fname)):
                images.append({'url': submission.url, 'fname': fname})
                go += 1
                if go >= 1000:
                    break
    if (len(images)):
        if not os.path.exists(path):
            os.mkdir(path)
        with concurrent.futures.ThreadPoolExecutor() as ptolemy:
            ptolemy.map(imageDownloader, images)


def downloadFromUrl(filename, object_type):
    username = uname
    print(f"Saving {object_type}s to {filename}... (Please wait)")
    count = 0
    path = os.path.join(location, filename)
    handle = open(path, "w")
    previous_epoch = int(start_time.timestamp())
    while True:
        new_url = url.format(object_type, username) + str(previous_epoch)
        json = requests.get(new_url, headers={'User-Agent': "Post downloader"})
        time.sleep(1.5)
        #print(str(json))
        try:
            json_data = json.json()
        except Exception as err:
            print(f"{bcolors.FAIL}ERROR: {str(err)}{bcolors.ENDC}")
        if 'data' not in json_data:
            break
        objects = json_data['data']
        if len(objects) == 0:
            break
        for object in objects:
            previous_epoch = object['created_utc'] - 1
            count += 1
            if object_type == 'comment':
                try:
                    comments_to_delete.append(object['id'])
                    handle.write("Score: " + str(object['score']))
                    handle.write(" : ")
                    handle.write(datetime.datetime.fromtimestamp(object['created_utc']).strftime("%Y-%m-%d %H:%M:%S"))
                    handle.write("\nComment in: /r/" + str(object['subreddit']))
                    handle.write("\n")
                    text = object['body']
                    textASCII = text.encode(encoding='ascii', errors='ignore').decode()
                    handle.write(textASCII)
                    handle.write("\n------------------------\n")
                except Exception as err:
                    print(f"Could not print comment: https://www.reddit.com{object['permalink']}")
                    print(traceback.format_exc())
            elif object_type == 'submission':
                if object['is_self']:
                    if 'selftext' not in object:
                        continue
                    try:
                        submissions_to_delete.append(object['id'])
                        handle.write("\n\n=========================\nScore: " + str(object['score']))
                        handle.write(" : ")
                        handle.write(
                            datetime.datetime.fromtimestamp(object['created_utc']).strftime("%Y-%m-%d %H:%M:%S"))
                        handle.write(" - SUBMISSION in: /r/" + str(object['subreddit']))
                        handle.write("\nLink: https://reddit.com" + str(object['permalink']))
                        id = str(object['id'])
                        # title = reddit.get_submission_by_id(id)
                        # TODO - Get submission by id,so i can get the title for it too
                        handle.write("\nPost Title: " + id)
                        handle.write("\n")
                        text = object['selftext']
                        textASCII = text.encode(encoding='ascii', errors='ignore').decode()
                        handle.write(textASCII)
                        handle.write("\n-------------------\n")
                        # TODO get comments under submission. Limit 1000
                        handle.write(" --- comments --- \n")
                        handle.write("-----------------------\n")
                        new_url2 = url2.format(id)
                        json2 = requests.get(new_url2, headers={'User-Agent': "Post downloader"})
                        time.sleep(1)
                        json_data2 = json2.json()
                        if 'data' not in json_data2:
                            break
                        objects2 = json_data2['data']
                        #            print("\n\n JSON 2 ----- \n\n" + str(objects2))
                        if len(objects2) == 0:
                            break
                        for object in objects2:
                            author = object['author']
                            text2 = object['body']
                            text2 = text2.replace("&amp;#x200B;", "\n")
                            score = object['score']
                            handle.write("\n\t /u/" + author + " replied: (" + str(
                                score) + ") " + text2 + "\n ----------------------")
                        print("post saved successfully.")
                    except Exception as err:
                        print(f"Could not print post: ") #https://www.reddit.com{object['permalink']}")
                        print(str(err) + " - proceeding...")
        print("Saved {} {}s through {}".format(count, object_type,
                                               datetime.datetime.fromtimestamp(previous_epoch).strftime(
                                                   "%Y-%m-%d %H:%M:%S")))
    print(f"Saved {count} {object_type}s")
    print("comments to delete: " + str(len(comments_to_delete)))
    print(5 * "==============")
    print("submissions to delete: " + str(len(submissions_to_delete)))

    handle.close()


def saveVideos():
    path = os.path.join(location, "video_uploads")
    redvid = Downloader(max_q=True)
    submissions = reddit.user.me().submissions.new(limit=None)
    for submission in submissions:
        if "v.redd" in submission.url:
            #    # #print("VIDEO URL: " + video_url)
            video_url = "https://www.reddit.com" + submission.permalink
            print(f"{bcolors.WARNING}\nVIDEO URL: " + video_url)
            print(f"{bcolors.ENDC}The following video will be downloaded: " + submission.title)
            try:
                if not os.path.exists(path):
                    os.mkdir(path)
                # os.chdir(path)
                redvid.download(video_url)
                for file in os.listdir(os.getcwd()):
                    if file.endswith(".mp4"):
                        filestring = '%.14s' % submission.title + ".mp4"
                        filestring = filestring.replace(" ", "_")
                        filestring = filestring.replace("?", "q")
                        print("FILESTRING: " + filestring)
                        print("THIS WILL BE RENAMED: " + file + " to: " + path + "/" + filestring)
                        os.rename(file, path + "/" + filestring)
            except Exception as err:
                print(f"{bcolors.FAIL}Exception: " + str(err))
                print("\nIt is advised that save the videos to the same partition/drive that the script is running on.")
                print(f"{bcolors.ENDC} ")
    print(f"{bcolors.OKBLUE} COMPLETE. ")
    print(f"{bcolors.ENDC} ")


def save_account_metadata():
    path = os.path.join(location, "nuke_metadata.txt")
    with open(path, "a", encoding='utf-8') as file:
        file.write(
            " === NUCLEAR REDDIT === " + "\n" + "User: /u/" + reddit.user.me().name + "\n - Created: " + datetime.datetime.fromtimestamp(
                reddit.user.me().created_utc).strftime('%Y-%m-%d %H:%M:%S') + "\n")
        file.write(" - Comment Karma: " + str(reddit.user.me().comment_karma) + "\n")
        file.write(" - Link Karma: " + str(reddit.user.me().link_karma) + "\n")
        file.write(
            "\n\n\nIf you've found this software helpful, please consider sending a small BTC tip to: qq5cws5pyy47rzmah2e0pgmxq5xjy2wf0vhy8nl9ma \nAnything is appreciated.\n\n")
        print("writing metadata...")


def getSavedPosts():
    path = os.path.join(location, "saved.txt")
    with open(path, "a", encoding='utf-8') as file:
        file.write("\n==============================\n")
        file.write(" === Saved posts: === \n")
        count_link = 1
        count_comment = 1
        for item in reddit.user.me().saved(limit=None):
            time.sleep(0.2)
            if str(count_link).endswith('0') or str(count_link).endswith('5'):
                load = "."
            if str(count_link).endswith('1') or str(count_link).endswith('6'):
                load = ".."
            if str(count_link).endswith('2') or str(count_link).endswith('7'):
                load = "..."
            if str(count_link).endswith('3') or str(count_link).endswith('8'):
                load = "...."
            if str(count_link).endswith('4') or str(count_link).endswith('9'):
                load = "....."
            print("writing saved submissions" + str(load))
            if isinstance(item, praw.models.Submission):
                file.write(" - link: (from /r/" + str(item.subreddit) + ") - link: " + item.url + "\n")
                count_link = count_link + 1
            else:
                comment_arr.append("\n\n --------------------------\n  - comment: (from /r/" + str(
                    item.subreddit) + ") - link: " + item.permalink + "\nTitle: " + item.submission.title + "\n\"" + item.body + "\"")
                print("writing saved comments... (" + str(count_comment) + ")")
                count_comment = count_comment + 1
        for comment in comment_arr:
            file.write(comment)


def initializeReddit(client_id, secret, uname, passwd):
    global reddit
    reddit = praw.Reddit(client_id=client_id,
                         client_secret=secret,
                         username=uname,
                         password=passwd,
                         user_agent='USER_AGENT')


def ini():
    reddit_uname = input(bcolors.WARNING + "\nEnter Reddit username here (omit the /u/): " + bcolors.ENDC)
    with open("verified_accounts.txt", "r") as file:
        verified_accounts = file.read().splitlines()
        print("verified: " + str(verified_accounts))
    if reddit_uname in verified_accounts:
        index = verified_accounts.index(reddit_uname)
        print("User: " + reddit_uname + " has already authenticated. Proceeding...")
        try:
            reddit_password = verified_accounts[index + 1]
            reddit_client_id = verified_accounts[index + 2]
            reddit_secret = verified_accounts[index + 3]
        except Exception as err:
            print("Error: " + str(err))
            print("Index is out of bounds - please enter in your credentials again.")
            ini()
    else:
        print(
                bcolors.ENDC + "\nNote: Your password is not uploaded anywhere. It is saved only to \"verified_accounts.txt\". If you want to review the code, find it at "
                           "https://github.com/bcornw2/Nuclear_Reddit" + bcolors.ENDC)
        time.sleep(0.5)
        reddit_password = input(bcolors.WARNING + "\nEnter Reddit password here: " + bcolors.ENDC)
        print(
                "\nTo get started, review the documentation on https://github.com/bcornw2/Nuclear_Reddit to find or create "
                "your Reddit CLIENT_ID and SECRET")
        reddit_client_id = input(bcolors.WARNING + "\nEnter Client ID here: " + bcolors.ENDC)
        reddit_secret = input(bcolors.WARNING + "\nEnter Secret here: " + bcolors.ENDC)

        print(f"{bcolors.HEADER} \nTesting Reddit access now...")
        print(f"{bcolors.ENDC} ")

    global client_id
    global secret
    global uname
    global passwd
    client_id = reddit_client_id
    secret = reddit_secret
    uname = reddit_uname
    passwd = reddit_password

    test_reddit = praw.Reddit(client_id=client_id,
                              client_secret=secret,
                              username=uname,
                              password=passwd,
                              user_agent='USER_AGENT')
    print("username  = /u/" + uname)
    print("password  = " + passwd)
    print("client_id = " + client_id)
    print("secret    = " + secret)

    choice = input(bcolors.OKBLUE + "Does this look right? [Y/n]: " + bcolors.ENDC)
    choice.lower()
    if choice is 'y' or choice is 'ye' or choice is 'yes':
        pass
    else:
        ini()
    #if (testAccount(test_reddit) or uname in verified_accounts):
        print(f"{bcolors.OKGREEN}\nContinuing...{bcolors.ENDC}")
    initializeReddit(client_id, secret, uname, passwd)
   #else:
     #   print(
      #      f"{bcolors.FAIL}\n\nAccount linking has failed. You may have entered your credentials inccorectly. Please "
      #      f"verify that your username, password, client ID, and secret are accurate.\n" + bcolors.ENDC)
      #  ini()


def testAccount(test_reddit):
    try:
        title = "test_post"
        global uname
        global passwd
        global client_id
        global secret
        if passwd == '': passwd = 'ERROR'
        if client_id == '': client_id = 'ERROR'
        if secret == '': secret = 'ERROR'

        test_reddit.subreddit("nuclear_reddit").submit(title, selftext="test post to verify access")
        print(f"{bcolors.OKGREEN}Reddit account linking is successful!{bcolors.ENDC}")
        verified_accounts.append(uname)
        with open("verified_accounts.txt", "a", encoding='utf-8') as file:
            file.write(uname + "\n" + passwd + "\n" + client_id + "\n" + secret + "\n")
        return True
    #  except RateLimitException as err:
    #  allow exceptions for rate limits to still be positive
    # since a ratelimit exception implies that the account
    # is correctly connected

    except Exception as err:
        print(f"{bcolors.FAIL} Testing has failed. Please verify credentials.  Error: " + str(err) + bcolors.ENDC)
        if "401" in str(err):
            print(f"{bcolors.FAIL}\n INCORRECT CREDENTIALS - try again.")
            ini()
        return False


### ===   DELETE METHODS   === ###
def editCommentString():
    default_comment_sting = "`NOTE:`  The content of this comment was removed, as Reddit has devolved into an authoritarian " \
                            "facebook-tier garbage site, rife with power-hungry mods and a psychopathic userbase. \n\nI " \
                            "have migrated to [Ruqqus](https://ruqqus.com), an open-source alternative to Reddit, and you should too!"
    footer = "\n\n ___________________________________________ \n\n^^This ^^action ^^was ^^performed ^^automatically ^^and ^^easily ^^by [^^Nuclear ^^Reddit ^^Remover ](https://github.com/bcornw2/Nuclear_Reddit)"
    print(
        "This is the default comment-replacement: " + bcolors.WARNING + default_comment_sting + " " + footer + bcolors.ENDC + "\n")
    time.sleep(0.5)
    choice = input(f"{bcolors.OKBLUE}Would you like to change this? [Y/n]: {bcolors.ENDC}")
    choice.lower()
    if choice.startswith("y"):
        comment_replacement = input(
            f"{bcolors.ENDC}Enter here what you would like all of your comments to say (use \"\\n\" instead of Enter): ")
        time.sleep(0.5)
        print("Your comment:\n\n")
        print(f"{bcolors.WARNING}{comment_replacement}\n{footer}{bcolors.ENDC}")
        print("\n(You cannot remove the footer.)")
        comment_replacement = comment_replacement + footer
    else:
        comment_replacement = default_comment_sting + footer
    choice = input("\nDoes this look good? \n" + bcolors.WARNING + comment_replacement + bcolors.ENDC + "\n\n[Y/n]: ")
    choice.lower()
    if choice == "y":
        editAllComments(comment_replacement)
    else:
        print("Re-try comment edit: ")
        editCommentString(comment_replacement)


## TODO - can only populate comments_to_delete array if archival runs...
##      maybe I can decouple and make the array fill a separate process from archival...

def editAllComments(comment_replacement):
    count = 1
    for comment_id in comments_to_delete:
        comment = reddit.comment(comment_id)
        try:
            comment.edit(comment_replacement)
            count += 1
            print("Edited comment: " + comment_id)
        except Exception as err:
            print("ERROR: " + str(err))
    print("Edited COMMENT count: " + str(count))


def deleteItAll():
    print(" === Menu ===")
    time.sleep(1)
    print()
    choice_number = input(f"""
        1.) {bcolors.BOLD}Edit{bcolors.ENDC} all comments, {bcolors.BOLD}delete{bcolors.ENDC} all submissions.
        2.) {bcolors.BOLD}Edit{bcolors.ENDC} all comments, leave all submissions intact.
        3.) {bcolors.BOLD}Delete{bcolors.ENDC} all comments, {bcolors.BOLD}delete{bcolors.ENDC} all submissions.
        4.) {bcolors.BOLD}Delete{bcolors.ENDC} all comments, leave all submissions intact.
        5.) Exit Program. This deletes nothing. 
    
    >>: """)
    if choice_number == "1":
        ##edit comments, delete submissions
        print("Opening comment editor...")
        time.sleep(0.5)
        editCommentString()
        print("\nAll comments have been edited.")
        print(f"{bcolors.FAIL}{bcolors.BOLD}{bcolors.UNDERLINE}\n\n\tWARNING{bcolors.ENDC}")
        choice = input(
            f"{bcolors.WARNING}\nDo you want to delete all submissions? This will delete all posts, and the comments "
            f"underneath them. This information has been backed up to an offline copy at \'submissions.txt\". \nPlease "
            f"review the data already collected in " + location + " before you choose to delete." +
            bcolors.ENDC + " Proceed? [Y/n]: ")
        choice.lower()
        if choice.startswith('y'):
            deleteSubmissions()

        print(bcolors.ENDC + "")

    elif choice_number == "2":
        ##Edit all comments, leave submissions intact
        print("Opening comment editor...")
        time.sleep(0.5)
        editCommentString()
        print("\nAll comments have been edited.")
        print(f"{bcolors.OKBLUE}You have elected to leave your submissions as they are. No submissions have been deleted from " + uname + ". Thank you for using this program." + bcolors.ENDC)

    elif choice_number == '3':
    ##delete comments, delete submissions
        choice = input(
            f"{bcolors.FAIL}{bcolors.BOLD}{bcolors.UNDERLINE}\nWARNING. THIS ACTION WILL DELETE EVERY COMMENT, "
            f"AND EVERY SUBMISSION. THIS CAN NOT BE UNDONE. We do, however, suggest that you edit your comments "
            f"instead of deleting them. To cancel, enter \'CANCEL\'.{bcolors.ENDC}\n TO PROCEED, "
            f"ENTER: {bcolors.FAIL} DELETE [USERNAME]: {bcolors.ENDC}")
        uname.upper()

        print("uname: " + uname)
        delete_string = "DELETE " + uname.upper()
        print("delete_string " + delete_string)
        if choice == delete_string:
            deleteComments()
            deleteSubmissions()
            print("Every comment and every submission was deleted. Thank you!")
        else:
            deleteItAll()
    elif choice_number == '4':
        ##delete comments, leave submissions
        time.sleep(0.5)
        choice = input(f"{bcolors.FAIL}{bcolors.BOLD}{bcolors.UNDERLINE}\nWARNING. THIS ACTION WILL DELETE EVERY "
                       f"COMMENT. THIS CANNOT BE UNDONE, AND COMMENTS CANNOT BE EDITED LATER. We do, however, "
                       f"suggest that you edit your comments instead of deleting them. To cancel, enter \'CANCEL\'."
                       f"{bcolors.ENDC}\nTO PROCEED, ENTER: {bcolors.FAIL} DELETE [USERNAME]: {bcolors.ENDC}")
        uname.upper()
        delete_string = "DELETE " + uname.upper()
        if choice == delete_string:
            deleteComments()
            print("Every coment was deleted. All submissions remain intact. Thank you!")
        else:
            deleteItAll()

    else:
        print(
            f"{bcolors.OKBLUE}Nothing was deleted. Please return to this program when you are ready to wipe it all "
            f"away. Visit {bcolors.ENDC}https://github.com/bcornw2/nuclear_reddit{bcolors.OKBLUE} for more "
            f"information.{bcolors.ENDC}")


def deleteSubmissions():
    count = 1
    for submission_id in submissions_to_delete:
        submission = reddit.submission(submission_id)
        try:
            submission.delete()
            count += 1
            print("deleted submission: " + submission_id)
        except Exception as err:
            print("ERROR: " + str(err))
    print("Deleted SUBMISSION count: " + str(count))


def deleteComments():
    count = 1
    for comment_id in comments_to_delete:
        comment = reddit.comment(comment_id)
        try:
            comment.delete()
            count += 1
            print("deleted comment: " + comment_id)
        except Exception as err:
            print("ERROR: " + str(err))
    print("Deleted COMMENT count: " + str(count))


def main():
    with open("verified_accounts.txt", "a", encoding='utf-8') as file:
        file.write("")
    print(bcolors.OKBLUE + "Nuclear Reddit Destroyer - archives and wipes all Reddit history." + bcolors.ENDC)
    time.sleep(1)
    with open("verified_accounts.txt", "a", encoding='utf-8') as file:
        file.close
    ini()
    global location
    home = str(Path.home())
    if platform == "linux" or platform == "linux2":
        #
        location = input(
            "(Linux) Enter local directory to save your content to. " + bcolors.WARNING + "[default: " + home + "/Nuclear_Reddit/]: " + bcolors.ENDC)
        print(f"{bcolors.ENDC}")
    elif platform == "darwin":
        #
        location = input(
            "(MacOS) Enter local directory to save your content to. " + bcolors.WARNING + "[default: " + home + "/Nuclear_Reddit/]: " + bcolors.ENDC)
        print(f"{bcolors.ENDC}")
    elif platform == "win32":
        #
        location == input(
            "(Windows) Enter local folder to save your content to. " + bcolors.WARNING + "[default: " + home + "/Nuclear_Reddit/]: " + bcolors.ENDC)

    if location is '':
        location = os.path.join(home, "Nuclear_Reddit")
        print("Working directory: " + location)
    if "Nuclear_Reddit" not in location:
        location = os.path.join(location, "Nuclear_Reddit")


    if not os.path.exists(location):
        try:
            print("Creating directory at " + location + "...")
            os.makedirs(location)
        except Exception as err:
            print("ERROR: " + str(err))
    else:
        print("Directory already exists. Proceeding.")



    #if not os.path.exists(location):
   #     os.makedirs(location)

    save_account_metadata()
    getSavedPosts()
    downloadFromUrl("submissions.txt", "submission")
    print(f"{bcolors.OKGREEN}Submissions download complete.{bcolors.ENDC}")
    downloadFromUrl("comments.txt", "comment")
    print(f"{bcolors.OKGREEN}Comments download complete.{bcolors.ENDC}")
    print(f"{bcolors.OKBLUE}Saving images submissions...{bcolors.ENDC}")
    getImages()
    print(f"{bcolors.OKGREEN}Images saved successfully.{bcolors.ENDC}")
    print(f"{bcolors.OKBLUE}Saving videos...{bcolors.OKBLUE}")
    saveVideos()
    print(f"{bcolors.OKGREEN}Videos saved successfully{bcolors.ENDC}")
    print(f"{bcolors.OKGREEN}submitted images download complete.{bcolors.ENDC}")
    deleteItAll()
    print("IMPORTANT: Your account is not deleted. If you want to delete everything, you must delete your account from Reddit.com")
    print(f"{bcolors.OKGREEN}Thank you for using Nuclear Reddit Remover. If you enjoyed this program, please consider leaving feedback at https://github.com/bcornw2/Nuclear_Reddit \nAlso, consider donating to Ruqqus via https://ruqqus.com/help/donate to facilitate the construction of a censorship-free internet.\nYou may now close this window.\nThank you!{bcolors.EDNC}")


if __name__ == "__main__":
    main()
