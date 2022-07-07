# AWSExportScript
Export Aws Services to csv




<!-- GETTING STARTED -->
### Steps to run this script
1. Install Vritual Environment 
   ```
    python3 -m pip install --user virtualenv
   ```
 
2. Create vritual env
   ```
    python3 -m venv env
   ```
3. Activate virtual env
   ```
    source env/bin/activate
   ```
4. Navgate to the script directory & Install requirement.txt
   ```
   pip3 install -r requirement.txt
    ```
5. Run 
    ```
      python3 main.py
      ```
6. Replace the environment variables 
    
    i) set SMPT_PASSWORD to the app password you generated through email provider
   
   ii) set SMPT_USER to your email address
  
   iii) set TO_EMAIL to all the recipients (Note: comma seperatedfor multiple recipients)
  
