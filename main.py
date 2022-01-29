import os
import sqlite3
from sqlite3 import Error
import os.path
import time
import sys
import hashlib
import croniter
import datetime

def getSystemdFiles (directory):
    # Create empty lists
    fileNames = []
    fullPath = []
    filecreation = []
    filemodified = []
    #Walk though passed directory searching for all files
    for path, subdirs, files in os.walk(directory):
        #For each file found
        for f in files:
            #Add file name to list
            fileNames.append(f)

            fullPath.append(os.path.join(path, f))
            fullf = (path + "/" + f)
            filecreation.append(time.ctime(os.path.getctime(fullf)))
            filemodified.append(time.ctime(os.path.getmtime(fullf)))
    return(filecreation, filemodified, fileNames, fullPath)

def getCrontabFiles (directory):
    # need to test if crontabs can run without full path
    # convert crontab run to next time
    fullPath = []
    crontabUsers = []
    crontabrun = []
    crontabcondition = []
    MD5list = []
    SHA1list = []
    SHA256list = []
    for path, subdirs, files in os.walk(directory):
        for f in files:
            fullf = (path + f)
            now = datetime.datetime.now()
            if fullf == "/var/spool/cron/root":
                if os.geteuid() == 0:
                    print("User is root")
                else:
                    fullf = "/dev/null"
            with open(fullf, "r") as fi:
                for ln in fi:
                    MD5listFound = 0
                    SHA1listFound = 0
                    SHA256listFound = 0
                    Conditionfound = 0
                    SpecialConditionfound = 0
                    if ln.startswith("@reboot"):
                        Conditionfound = 1
                        SpecialConditionfound = 1
                        crontabcondition.append("reboot")
                    if ln.startswith("@hourly"):
                        Conditionfound = 1
                        SpecialConditionfound = 1
                        crontabcondition.append("hourly")
                    if ln.startswith("@daily"):
                        Conditionfound = 1
                        SpecialConditionfound = 1
                        crontabcondition.append("daily")
                    if ln.startswith("@weekly"):
                        Conditionfound = 1
                        SpecialConditionfound = 1
                        crontabcondition.append("weekly")
                    if ln.startswith("@monthly"):
                        Conditionfound = 1
                        crontabcondition.append("monthly")
                    if ln.startswith("@yearly"):
                        Conditionfound = 1
                        SpecialConditionfound = 1
                        crontabcondition.append("yearly")
                    if ln.startswith("@annually"):
                        Conditionfound = 1
                        SpecialConditionfound = 1
                        crontabcondition.append("annually")
                    if ln.startswith("@midnight"):
                        Conditionfound = 1
                        SpecialConditionfound = 1
                        crontabcondition.append("midnight")
                    if ln[0].isdigit():
                        groups = ln.split(' ')
                        run = ' '.join(groups[:5])
                        Conditionfound = 1
                        crontabcondition.append(run)
                    if ln.startswith('*'):
                        groups = ln.split(' ')
                        run = ' '.join(groups[:5])
                        Conditionfound = 1
                        crontabcondition.append(run)
                    if Conditionfound == 1:
                        run = "NA"
                        crontabUsers.append(f)
                        fullPath.append(os.path.join(path, f))
                        if SpecialConditionfound == 1:
                            run = ln[ln.find("/"):]
                            run = run.rstrip("\n")
                            crontabrun.append(run)
                        if SpecialConditionfound == 0:
                            groups = ln.split(' ')
                            run = ' '.join(groups[5:])
                            run = run.rstrip("\n")
                            crontabrun.append(run)
                        if os.path.exists(run):
                            md5hash = hashlib.md5(open(run, 'rb').read()).hexdigest()
                            sha1hash = hashlib.sha1(open(run, 'rb').read()).hexdigest()
                            sha256hash = hashlib.sha256(open(run, 'rb').read()).hexdigest()
                            MD5list.append(md5hash)
                            SHA1list.append(sha1hash)
                            SHA256list.append(sha256hash)
                        else:

                            md5hash = "File Not Found"
                            sha1hash = "File Not Found"
                            sha256hash = "File Not Found"
                            MD5list.append(md5hash)
                            SHA1list.append(sha1hash)
                            SHA256list.append(sha256hash)




    return(crontabUsers, fullPath, crontabcondition, crontabrun, MD5list, SHA1list, SHA256list)





def systemdInfo(SystemdPaths):
    Description = []
    ExecStart = []
    ExecStop = []
    ExecStopPost = []
    MD5list = []
    SHA1list = []
    SHA256list = []
    for i in SystemdPaths:


        DescriptionFound = 0
        ExecStartFound = 0
        ExecStopFound = 0
        ExecStopPostFound = 0
        MD5listFound = 0
        SHA1listFound = 0
        SHA256listFound = 0


        with open(i, "r") as fi:
            for ln in fi:
                if ln.startswith("Description="):
                    DescriptionFound = 1
                    Description.append(ln[12:-1])
                if ln.startswith("ExecStop="):
                    ExecStopFound = 1
                    ExecStop.append(ln[9:-1])
                if ln.startswith("ExecStopPost="):
                    ExecStopPostFound = 1
                    ExecStopPost.append(ln[13:-1])
                if ln.startswith("ExecStart="):
                    ExecStartFound = 1
                    ExecStart.append(ln[10:-1])
                    hashitem = (ln[10:-1])
                    if hashitem[0] == '-':
                        hashitem = hashitem.split('-', 1)[1]
                    hashitem = (hashitem.split(' ', 1)[0])
                    if os.path.exists(hashitem):
                        md5hash = hashlib.md5(open(hashitem, 'rb').read()).hexdigest()
                        sha1hash = hashlib.sha1(open(hashitem, 'rb').read()).hexdigest()
                        sha256hash = hashlib.sha256(open(hashitem, 'rb').read()).hexdigest()
                    else:
                        md5hash = "NA"
                        sha1hash = "NA"
                        sha256hash = "NA"
                    MD5list.append(md5hash)
                    SHA1list.append(sha1hash)
                    SHA256list.append(sha256hash)
                    MD5listFound = 1
                    SHA1listFound = 1
                    SHA256listFound = 1

        if DescriptionFound == 0:
            Description.append("NA")
        if ExecStartFound == 0:
            ExecStart.append("NA")
        if ExecStopFound == 0:
            ExecStop.append("NA")
        if ExecStopPostFound == 0:
            ExecStopPost.append("NA")
        if MD5listFound == 0:
            MD5list.append("NA")
        if SHA1listFound == 0:
            SHA1list.append("NA")
        if SHA256listFound == 0:
            SHA256list.append("NA")


    return(Description, ExecStart, ExecStop, ExecStopPost, MD5list, SHA1list, SHA256list)

def makeDB (installedSystemdFilecreation, installedSystemdFilemodified, installedSystemdNames, installedSystemdDescription, installedSystemdPaths, installedSystemdExecStart, installedSystemdExecStop, installedSystemdExecStopPost, installedSystemdMD5, installedSystemdSHA1, installedSystemdSHA256, sysadminSystemdFilecreation, sysadminSystemdFilemodified, sysadminSystemdNames, sysadminSystemdDescription, sysadminSystemdPaths, sysadminSystemdExecStart, sysadminSystemdExecStop, sysadminSystemdExecStopPost, sysadminSystemdMD5, sysadminSystemdSHA1, sysadminSystemdSHA256, cronUserUsers, cronUserPath, cronUsercondition, cronUserrun,  cronUserMD5list, cronUserSHA1list, cronUserSHA256list):
    datadir = os.path.expanduser('~/.local/share/autostarts')
    os.makedirs(datadir, exist_ok=True)
    if os.path.exists(datadir + "/autostarts.db"):
        os.remove(datadir + "/autostarts.db")
    db_file = r""+datadir+"/autostarts.db"
    print(db_file)
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print(sqlite3.version)
        c = conn.cursor()
        c.execute("""CREATE TABLE "InstalledSystemdItems" (
        	"CreatedTime"	TEXT,
        	"ModifiedTime"	TEXT,
        	"ItemName"	TEXT,
        	"Description"	TEXT,
        	"Path"	TEXT,
        	"ExecStart"	TEXT,
        	"ExecStop"	TEXT,
        	"ExecStopPost"	TEXT,
        	"MD5"	TEXT,
        	"SHA1"	TEXT,
        	"SHA256"	TEXT,
        	"VT"	TEXT
        ); """)
        c.execute("""CREATE TABLE "SysadminSystemdItems" (
	"CreatedTime"	TEXT,
	"ModifiedTime"	TEXT,
	"ItemName"	TEXT,
	"Description"	TEXT,
	"Path"	TEXT,
	"ExecStart"	TEXT,
	"ExecStop"	TEXT,
	"ExecStopPost"	TEXT,
	"MD5"	TEXT,
	"SHA1"	TEXT,
	"SHA256"	TEXT,
	"VT"	TEXT
); """)
        c.execute("""CREATE TABLE "UserCrontabs" (
        	"User"	TEXT,
        	"Path"	TEXT,
        	"RunCondition"	TEXT,
        	"Executable"	TEXT,
        	"MD5"	TEXT,
        	"SHA1"	TEXT,
        	"SHA256"	TEXT,
        	"VT"	TEXT
        ); """)

        c.executemany(
            'INSERT INTO InstalledSystemdItems (CreatedTime, ModifiedTime, ItemName, Description, Path, ExecStart, ExecStop, ExecStopPost, MD5, SHA1, SHA256) VALUES (?,?,?,?,?,?,?,?,?,?,?)',
            zip(installedSystemdFilecreation, installedSystemdFilemodified, installedSystemdNames,
                installedSystemdDescription, installedSystemdPaths, installedSystemdExecStart, installedSystemdExecStop,
                installedSystemdExecStopPost, installedSystemdMD5, installedSystemdSHA1, installedSystemdSHA256))
        c.executemany(
            'INSERT INTO SysadminSystemdItems (CreatedTime, ModifiedTime, ItemName, Description, Path, ExecStart, ExecStop, ExecStopPost, MD5, SHA1, SHA256) VALUES (?,?,?,?,?,?,?,?,?,?,?)',
            zip(sysadminSystemdFilecreation, sysadminSystemdFilemodified, sysadminSystemdNames,
                sysadminSystemdDescription, sysadminSystemdPaths, sysadminSystemdExecStart, sysadminSystemdExecStop,
                sysadminSystemdExecStopPost, sysadminSystemdMD5, sysadminSystemdSHA1, sysadminSystemdSHA256))
        c.executemany(
            'INSERT INTO UserCrontabs (User, Path, RunCondition, Executable, MD5, SHA1, SHA256) VALUES (?,?,?,?,?,?,?)',
            zip(cronUserUsers, cronUserPath, cronUsercondition, cronUserrun,  cronUserMD5list, cronUserSHA1list, cronUserSHA256list))
        conn.commit()
    except Error as e:
         print(e)
    finally:
         if conn:
           conn.close()



# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print("Getting systemd items:")
    print("Pulling installed packages items...")
    directory = "/usr/lib/systemd/system/"
    installedSystemdFilecreation, installedSystemdFilemodified, installedSystemdNames, installedSystemdPaths = getSystemdFiles(directory)
    print("Pulling system administrator items...")
    directory = "/etc/systemd/system/"
    sysadminSystemdFilecreation, sysadminSystemdFilemodified, sysadminSystemdNames, sysadminSystemdPaths = getSystemdFiles(directory)
    print("Pulling user crontabs...")
    directory = "/var/spool/cron/"
    cronUserUsers, cronUserPath, cronUsercondition, cronUserrun,  cronUserMD5list, cronUserSHA1list, cronUserSHA256list = getCrontabFiles(directory)


    installedSystemdDescription, installedSystemdExecStart, installedSystemdExecStop, installedSystemdExecStopPost, installedSystemdMD5, installedSystemdSHA1, installedSystemdSHA256 = systemdInfo(installedSystemdPaths)
    sysadminSystemdDescription, sysadminSystemdExecStart, sysadminSystemdExecStop, sysadminSystemdExecStopPost, sysadminSystemdMD5, sysadminSystemdSHA1, sysadminSystemdSHA256 = systemdInfo(sysadminSystemdPaths)

    makeDB(installedSystemdFilecreation, installedSystemdFilemodified, installedSystemdNames, installedSystemdDescription, installedSystemdPaths, installedSystemdExecStart, installedSystemdExecStop, installedSystemdExecStopPost, installedSystemdMD5, installedSystemdSHA1, installedSystemdSHA256, sysadminSystemdFilecreation, sysadminSystemdFilemodified, sysadminSystemdNames, sysadminSystemdDescription, sysadminSystemdPaths, sysadminSystemdExecStart, sysadminSystemdExecStop, sysadminSystemdExecStopPost, sysadminSystemdMD5, sysadminSystemdSHA1, sysadminSystemdSHA256, cronUserUsers, cronUserPath, cronUsercondition, cronUserrun,  cronUserMD5list, cronUserSHA1list, cronUserSHA256list)



