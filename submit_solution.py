from mechanicalsoup import StatefulBrowser
from re import search

def codeforces_login(username, password, problem_code, programming_language, path):
    browser = StatefulBrowser()
    login_url = 'https://codeforces.com/enter'
    browser.open(login_url)
    browser.select_form('form[id="enterForm"]')
    browser["handleOrEmail"] = username
    browser["password"] = password

    browser.submit_selected()

    # Check if login was successful
    pass

    form_url = f'https://codeforces.com/contest/{search(r"[A-z]", problem_code).start()}/submit'
    browser.open(form_url)
    form = browser.select_form(f'form[class="submit-form"]')

    # Fill out the form fields
    form.set("submittedProblemCode", problem_code)
    form.set("programTypeId", programming_language)
    # Add the source file for submission
    form.set("sourceFile", open(path, "rb"))

    # Submit the form
    browser.submit_selected()

    # Check if the submission was successful (You may need to implement additional script depending on the response)
    pass


# if __name__ == "__main__":
#     codeforces_login("ghoudiy", "codeforcesGh2202", "144A", "31", "/home/ghoudiy/Documents/Programming/Python/CP/Codeforces/A_Problems/144A_Arrival_of_the_General.py")
a = {"test": 1, "hello": 2}
b = a.pop("hey", a)
print(b)