from mechanicalsoup import StatefulBrowser

def codeforces_login(username, password, problem_code, programming_language, path):
    # Create a browser object
    browser = StatefulBrowser()

    # Navigate to the Codeforces login page
    login_url = 'https://codeforces.com/enter'
    browser.open(login_url)

    # Find the login form
    browser.select_form('form[id="enterForm"]')

    # Fill out the login form
    browser["handleOrEmail"] = username
    browser["password"] = password

    # Submit the form
    browser.submit_selected()

    # Check if login was successful
    pass

    form_url = 'https://codeforces.com/problemset/submit'
    browser.open(form_url)

    # Find the form on the submission page
    form = browser.select_form(f'form[class="submit-form"]')

    # Fill out the form fields
    form.set("submittedProblemCode", problem_code)
    form.set("programTypeId", programming_language)
    # Add the source file for submission
    form.set("sourceFile", open(path, "rb"))

    # Submit the form
    browser.submit_selected()

    # Check if the submission was successful (You may need to implement additional checks depending on the response)
    pass


if __name__ == "__main__":
    codeforces_login("ghoudiy", "codeforcesGh2202", "144A", "31", "/home/ghoudiy/Documents/Programming/Python/CP/Codeforces/A_Problems/144A_Arrival_of_the_General.py")
