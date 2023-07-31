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
        print(session.cookies)
        # with open("ghoudi_yassine.html", "wb") as file:
        #     file.write(session.get("https://codeforces.com/profile/ghoudiy").content)
    else:
        print("Login failed!")
# Create a session object to maintain the session cookie
