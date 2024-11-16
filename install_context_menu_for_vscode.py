import os
import requests
import zipfile
import subprocess
import winreg

# Define paths
vscode_install_path = r"Yout VS Code Install Path"
shell_path = os.path.join(vscode_install_path, "shell")
#upgrade url if you have a new version, currently the latest version is 3.0.4
url = "https://github.com/microsoft/vscode-explorer-command/releases/download/3.0.4/code_explorer_x64.zip"

# Step 1: Download the latest release
def download_latest_release(url, dest_folder):
    zip_path = os.path.join(dest_folder, "code_explorer_x64.zip")
    print("Downloading latest release...")
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(zip_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=1024):
                f.write(chunk)
    print("Downloaded.")
    return zip_path

# Step 2: Unzip the downloaded zip
def unzip_file(zip_path, extract_to):
    print("Unzipping the file...")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
    print("Unzipped.")
    # delete zip file after extraction
    os.remove(zip_path)

# Step 3: Rename, Unzip, and Restore the .appx file
def process_appx_file(appx_file):
    temp_zip = appx_file.replace(".appx", ".zip")
    print(f"Renaming {appx_file} to {temp_zip}...")
    os.rename(appx_file, temp_zip)

    print("Extracting the .zip file...")
    with zipfile.ZipFile(temp_zip, 'r') as zip_ref:
        zip_ref.extractall(os.path.dirname(appx_file))

    print(f"Restoring {temp_zip} back to {appx_file}...")
    os.rename(temp_zip, appx_file)
    print("Processing of the .appx file completed.")

# Step 4: Edit AppxManifest.xml
def edit_manifest_file(manifest_path):
    print("Editing AppxManifest.xml...")
    with open(manifest_path, "r") as file:
        content = file.read()
    content = content.replace(
        'Publisher="CN=Microsoft Corporation, O=Microsoft Corporation, L=Redmond, S=Washington, C=US"',
        'Publisher="CN=Custom Corporation, O=Custom Corporation, L=YourCity, S=YourState, C=YourCountry"'
    )
    with open(manifest_path, "w") as file:
        file.write(content)
    print("AppxManifest.xml updated.")

# Step 5: Create registry key
def create_registry_key():
    print("Creating registry key...")
    try:
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Software\Classes\VSCodeContextMenu") as key:
            winreg.SetValueEx(key, "Title", 0, winreg.REG_SZ, "Open with Code")
        print("Registry key created successfully.")
    except Exception as e:
        print(f"Failed to create registry key: {e}")

# Step 6: Enable Developer Mode by manual intervention before running this script
def enable_developer_mode():
    print("Developer Mode must be enabled manually in Windows Settings (Settings > System > For developers > Developer Mode).")

# Step 7: Register the Appx package
def register_appx_package(manifest_path):
    print("Registering the Appx package...")
    subprocess.run(["powershell", "-Command", f"Add-AppxPackage -Path \'{manifest_path}\' -Register -ExternalLocation \'{shell_path}\'"])
    print("Appx package registered.")

# Main Execution
if __name__ == "__main__":
    if not os.path.exists(shell_path):
        os.makedirs(shell_path)

    zip_file = download_latest_release(url, shell_path)
    unzip_file(zip_file, shell_path)

    appx_file = os.path.join(shell_path, "code_explorer_x64.appx")
    process_appx_file(appx_file)

    manifest_file = os.path.join(shell_path, "AppxManifest.xml")
    edit_manifest_file(manifest_file)

    create_registry_key()

    enable_developer_mode()

    register_appx_package(manifest_file)

