# TriggerSync Automation

## V-Portal User

- Create a user in the respective V-Portal and assign projects
    
    ![Screenshot 2023-07-05 at 3.13.55 pm.png](ATS_Image/Screenshot_2023-07-05_at_3.13.55_pm.png)
    
- Set the password give assign minimum permission
- Open the V-Portal project through this account and reset the password
- Go to V-Portal database and then to `vportal_users.user_profile`
- Set the extend the password expiry date

## Set Environment Variable

1. Go to the respective server hosting the automation script
2. Click on **Start** and search for **Environment** **Variable**
    
    ![Screenshot 2023-07-05 at 3.25.26 pm.png](ATS_Image/Screenshot_2023-07-05_at_3.25.26_pm.png)
    
3. Click on **Environment** **Variable**
    
    ![Screenshot 2023-07-05 at 3.25.55 pm.png](ATS_Image/Screenshot_2023-07-05_at_3.25.55_pm.png)
    
4. Click on **New**
    
    ![Screenshot 2023-07-05 at 3.27.19 pm.png](ATS_Image/Screenshot_2023-07-05_at_3.27.19_pm.png)
    
5. Set the V-Portal Username and and V-Portal Password as:
    - VP-Username
    - VP-Password
    - Slack_Bot_API_Token

## Selenium File

1. Import Selenium file in `C:\Selenium\AutoTriggerSync`
2. Edit `C:\Selenium\AutoTriggerSync\config.ini` as required
3. Open **Command Prompt** as an **Administrator,** Install python library
    
    ```bash
    pip install -r requirements.txt
    ```
    
4. When new package is added
    
    ```bash
    pip freeze > requirements.txt
    ```
    

## Schedule Automation

- Go to Task Scheduler > Create Task
    
    ![Screenshot 2023-07-05 at 10.51.33 am.png](ATS_Image/Screenshot_2023-07-05_at_10.51.33_am.png)
    
- General
    1. In the “Name” box, enter a name for the task.
    2. In the “General” tab, under the “Security options” section, select the “**Run whether user is logged on or not”** option. (This option will make the command window not appear when the task runs automatically.)
        
        ![Screenshot 2023-07-06 at 10.44.57 am.png](ATS_Image/Screenshot_2023-07-06_at_10.44.57_am.png)
        
- Triggers
    1. Click the “Triggers” tab, and click the **New** button.
    2. Select the **“On a schedule”** option using the “Begin the task” setting.
    3. Under “Settings,” specify when you want the task to run (for example, On time, Daily, Weekly, or Monthly). Whatever option you select, set the **Start** settings on the right side.
        
        ![Screenshot 2023-07-06 at 10.47.54 am.png](ATS_Image/Screenshot_2023-07-06_at_10.47.54_am.png)
        
- Action
    1. Click the “Actions” tab, and click the **New** Button.
    2. Use the “Actions” drop-down menu and select the **“Start a program”** option.
    3. In the “Program/script” box, type the following command:
        
        ```
        "C:\Program Files\Python37\python.exe"
        ```
        
    4. Type the following command in the “Add arguments” box and click the **OK** button.
        
        ```bash
        auto_trigger_sync.py
        ```
        
    5. Type the following command in the “Start in” box and click the **OK** button.
        
        ```bash
        C:\Selenium\AutoTriggerSync
        ```
        
        ![Screenshot 2023-07-06 at 10.50.39 am.png](ATS_Image/Screenshot_2023-07-06_at_10.50.39_am.png)
        
- Settings
    1. Click the “Settings” tab, and make sure to check the following options:
        - Allow task to be run on demand.
        - Run task as soon as possible after a scheduled start is missed.
        - If the task fails, restart every.
            
            ![Screenshot 2023-07-05 at 11.09.28 am.png](ATS_Image/Screenshot_2023-07-05_at_11.09.28_am.png)
            
- Click on **OK** button

## Schedule Clear Logs

- Test Script
    
    ```bash
    ForFiles /p "C:\Selenium\AutoTriggerSync\logs" /s /d -10 /c "cmd /c del /q @file"
    ```
    
- Go to Task Scheduler > Create Task
    
    ![Screenshot 2023-07-05 at 10.51.33 am.png](ATS_Image/Screenshot_2023-07-05_at_10.51.33_am.png)
    
- General
    1. In the “Name” box, enter a name for the task.
    2. In the “General” tab, under the “Security options” section, select the “**Run whether user is logged on or not”** option. (This option will make the command window not appear when the task runs automatically.)
        
        ![Screenshot 2023-07-05 at 10.57.42 am.png](ATS_Image/Screenshot_2023-07-05_at_10.57.42_am.png)
        
- Triggers
    1. Click the “Triggers” tab, and click the **New** button.
    2. Select the **“On a schedule”** option using the “Begin the task” setting.
    3. Under “Settings,” specify when you want the task to run (for example, On time, Daily, Weekly, or Monthly). Whatever option you select, set the **Start** settings on the right side.
    
    ![Screenshot 2023-07-05 at 10.57.02 am.png](ATS_Image/Screenshot_2023-07-05_at_10.57.02_am.png)
    
- Action
    1. Click the “Actions” tab, and click the **New** Button.
    2. Use the “Actions” drop-down menu and select the **“Start a program”** option.
    3. In the “Program/script” box, type the following command:
        
        ```
        ForFiles
        ```
        
    4. Type the following command in the “Add arguments” box and click the **OK** button.
        
        ```bash
        /p "C:\Selenium\AutoTriggerSync\logs" /s /d -10 /c "cmd /c del /q @file"
        ```
        
        In the command, change `"C:\Selenium\AutoTriggerSync\logs"` specifying the path to the folder that you want to delete files and change `/d -10` to select files with the last modified date.
        
        ![Screenshot 2023-07-05 at 11.07.35 am.png](ATS_Image/Screenshot_2023-07-05_at_11.07.35_am.png)
        
- Settings
    1. Click the “Settings” tab, and make sure to check the following options:
        - Allow task to be run on demand.
        - Run task as soon as possible after a scheduled start is missed.
        - If the task fails, restart every.
            
            ![Screenshot 2023-07-05 at 11.09.28 am.png](ATS_Image/Screenshot_2023-07-05_at_11.09.28_am.png)
            
- Click on **OK** button