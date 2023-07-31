import requests

if __name__ == "__main__":
    username = "ghoudiy"
    password = "codeforcesGh2202"
    
    url = "https://codeforces.com/enter?back=%2F"
    data = {
        "action": "enter",
        "handleOrEmail": username,
        "password": password,
    }
    session = requests.Session()
    response = session.post(url, data=data)

    if response.status_code == 200:
        print("Login successful!")

        url = "https://codeforces.com/problemset/submit"  # Replace with the actual URL where the form is submitted

        # The data you want to submit
        program_type_id = "31"  # This value corresponds to "Python"
        source_code_file_path = "/home/ghoudiy/Documents/Programming/Python/CP/Codeforces/A_Problems/144A_Arrival_of_the_General.py"  # Replace with the path to your source code file

        # Create a dictionary with the form data
        form_data = {
            "action": "submit",
            "problemId": "144A",
            "programTypeId": program_type_id,
            "sourceFile": source_code_file_path
        }

        # Read the source code file and add it to the form data
        # with open(source_code_file_path, "rb") as file:
        #     form_data["sourceFile"] = source_code_file_path

        # Send the POST request with the form data
        print(session.cookies)
        response = session.post(url, files=form_data)

        # Check if the request was successful
        if response.status_code == 200:
            print("Form submitted successfully.")
        else:
            print("Form submission failed.")

    else:
        print("Login failed!")
# Create a session object to maintain the session cookie
