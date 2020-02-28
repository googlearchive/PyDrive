from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive

# Authenticate the client.
gauth = GoogleAuth()
gauth.LocalWebserverAuth()
drive = GoogleDrive(gauth)

# Create a file, set content, and upload.
file1 = drive.CreateFile()
original_file_content = "Generic, non-exhaustive\n ASCII test string."
file1.SetContentString(original_file_content)
# {'convert': True} triggers conversion to a Google Drive document.
file1.Upload({"convert": True})


# Download the file.
file2 = drive.CreateFile({"id": file1["id"]})

# Print content before download.
print("Original text:")
print(bytes(original_file_content.encode("unicode-escape")))
print("Number of chars: %d" % len(original_file_content))
print("")
#     Original text:
#     Generic, non-exhaustive\n ASCII test string.
#     Number of chars: 43


# Download document as text file WITH the BOM and print the contents.
content_with_bom = file2.GetContentString(mimetype="text/plain")
print("Content with BOM:")
print(bytes(content_with_bom.encode("unicode-escape")))
print("Number of chars: %d" % len(content_with_bom))
print("")
#     Content with BOM:
#     \ufeffGeneric, non-exhaustive\r\n ASCII test string.
#     Number of chars: 45


# Download document as text file WITHOUT the BOM and print the contents.
content_without_bom = file2.GetContentString(
    mimetype="text/plain", remove_bom=True
)
print("Content without BOM:")
print(bytes(content_without_bom.encode("unicode-escape")))
print("Number of chars: %d" % len(content_without_bom))
print("")
#     Content without BOM:
#     Generic, non-exhaustive\r\n ASCII test string.
#     Number of chars: 44

# *NOTE*: When downloading a Google Drive document as text file, line-endings
# are converted to the Windows-style: \r\n.


# Delete the file as necessary.
file1.Delete()
