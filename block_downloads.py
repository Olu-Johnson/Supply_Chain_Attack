import os
import requests
import subprocess
import shutil
import platform
import time
from datetime import datetime, timezone
from dateutil.relativedelta import relativedelta

# Function to download the npm package
def download_package(package_name, download_dir):
    metadata_url = f"https://registry.npmjs.org/{package_name}"
    
    try:
        metadata_response = requests.get(metadata_url)
        metadata_response.raise_for_status()
        metadata = metadata_response.json()
        latest_version = metadata['dist-tags']['latest']
        date_created = metadata['time']['created']
        tarball_url = metadata['versions'][latest_version]['dist']['tarball']

        print(f"Package creation Date : {date_created}")   
        
    except requests.RequestException as e:
        print(f"Failed to fetch metadata for package {package_name}: {e}")
        return "", "", ""

    try:
        response = requests.get(tarball_url, stream=True)
        response.raise_for_status()
        package_path = os.path.join(download_dir, f"{package_name}.tgz")
        with open(package_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        return package_name, package_path, date_created
    except requests.RequestException as e:
        print(f"Failed to download package {package_name}: {e}")
        return "", "", ""

# Function to scan the package
def scan_package(dates):
     given_date = datetime.strptime(dates, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)     
     current_date = datetime.now(timezone.utc)
     difference = relativedelta(current_date,given_date)    
     if difference.years < 8:
        return False
     else :        
        return True

# Function to install the npm package
def install_package(package_name, project_dir):
    if not os.path.exists(project_dir):
        print(f"Project directory {project_dir} does not exist.")
        return

    try:
        # Construct the npm command to install the package to a specific directory
        command = f"npm install {package_name} --prefix {project_dir}"
        
        # Execute the command using subprocess
        subprocess.run(command, shell=True, check=True)
        print(f"Successfully installed {package_name} to {project_dir}")
    except subprocess.CalledProcessError as e:
        print(f"Failed to install {package_name} to {project_dir}. Error: {str(e)}")


def main(package_name, project_dir):
    download_dir = os.path.join(os.getenv('TEMP'), 'npm_downloads')
    os.makedirs(download_dir, exist_ok=True)    

    packagename, project_path, dates = download_package(package_name, download_dir)
    if project_path !="":
        #scanning the package
        if(scan_package(dates)):
            print("scan successful")
            print("This package meet the creation date requirement")
            #Intalling the package
            print(f"intalling {package_name} package to {project_path}")
            install_package(package_name, project_dir)
        else:
            print("scan failed")
            print(f"This package {package_name} cannot be downloaded because the creation date is less than 2 years. /n Please contact the security team if this package is crucial to your development.")
        
    else:
        print("Download failed. Exiting.")
    
    shutil.rmtree(download_dir)

if __name__ == "__main__":
    package_name = input("Enter the npm package name: ")
    project_dir = input("Enter the project directory: ")
    main(package_name, project_dir)